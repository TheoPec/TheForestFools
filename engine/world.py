"""World maps and map rendering."""

import random

from data.config import COLS, ROWS, CAPITAL_POS, WORLD_TILE_COUNTS, PORT_COUNT
from data.fixed_maps import FIXED_MAPS, REGIONS, TILE_CODE_TYPES, region_for_pos
from data.locations import TILE_SYMBOLS, TILE_NAMES
from data.loot_tables import merchant_stock_for_region
from engine.terminal import C, styled, TILE_COLORS, BG_COLORS


def generate_merchant_stock(region_key=None):
    """Generate a random merchant stock."""
    return merchant_stock_for_region(region_key)


def generate_terrain():
    """Generate terrain layer: water on borders, sand coastline, grass/dark_grass interior."""
    terrain = {}
    for c in COLS:
        for r in ROWS:
            terrain[(c, r)] = "grass"

    # Water on border cells
    for c in COLS:
        for r in ROWS:
            ci = COLS.index(c)
            ri = r - 1
            dist = min(ci, 9 - ci, ri, 9 - ri)
            if dist == 0 and random.random() < 0.82:
                terrain[(c, r)] = "water"

    # Extend water clusters slightly inward
    snapshot = dict(terrain)
    for c in COLS:
        for r in ROWS:
            if snapshot[(c, r)] == "water":
                ci = COLS.index(c)
                ri = r - 1
                for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nc, nr = ci + dc, ri + dr
                    if 0 <= nc < 10 and 0 <= nr < 10:
                        npos = (COLS[nc], nr + 1)
                        if terrain[npos] == "grass" and random.random() < 0.18:
                            terrain[npos] = "water"

    # Protect capital and surroundings
    cap_ci = COLS.index(CAPITAL_POS[0])
    cap_ri = CAPITAL_POS[1] - 1
    for dc in range(-1, 2):
        for dr in range(-1, 2):
            ci = cap_ci + dc
            ri = cap_ri + dr
            if 0 <= ci < 10 and 0 <= ri < 10:
                terrain[(COLS[ci], ri + 1)] = "grass"

    # Sand: non-water cells adjacent to water (including diagonal)
    for c in COLS:
        for r in ROWS:
            if terrain[(c, r)] != "water":
                ci = COLS.index(c)
                ri = r - 1
                for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1),
                               (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                    nc, nr = ci + dc, ri + dr
                    if 0 <= nc < 10 and 0 <= nr < 10:
                        if terrain[(COLS[nc], nr + 1)] == "water":
                            terrain[(c, r)] = "sand"
                            break

    # Dark grass clusters in interior
    for _ in range(6):
        ci = random.randint(2, 7)
        ri = random.randint(2, 7)
        pos = (COLS[ci], ri + 1)
        if terrain[pos] == "grass":
            terrain[pos] = "dark_grass"
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nc, nr = ci + dc, ri + dr
                if 0 <= nc < 10 and 0 <= nr < 10:
                    npos = (COLS[nc], nr + 1)
                    if terrain[npos] == "grass" and random.random() < 0.5:
                        terrain[npos] = "dark_grass"

    return terrain


def generate_world():
    """Return the starting fixed world for compatibility with older callers."""
    return generate_worlds()["mosswake"]


def generate_worlds():
    """Create every fixed world map keyed by map id."""
    return {map_key: build_fixed_world(map_key, spec) for map_key, spec in FIXED_MAPS.items()}


def world_axes(world):
    cols = sorted({pos[0] for pos in world}, key=column_sort_key)
    rows = sorted({pos[1] for pos in world})
    return cols, rows


def column_sort_key(label):
    value = 0
    for char in label:
        value = value * 26 + (ord(char) - ord("A") + 1)
    return value


def column_range_label(cols):
    if not cols:
        return "?"
    return f"{cols[0]}-{cols[-1]}"


def parse_coord(raw, cols, rows):
    cell = raw.strip().upper()
    letters = ""
    digits = ""
    for char in cell:
        if char.isalpha() and not digits:
            letters += char
        elif char.isdigit():
            digits += char
        else:
            return None
    if not letters or not digits:
        return None
    try:
        row = int(digits)
    except ValueError:
        return None
    if letters not in cols or row not in rows:
        return None
    return letters, row


def build_fixed_world(map_key, spec):
    world = {}
    named_tiles = spec.get("named_tiles", {})
    fully_revealed = spec.get("fully_revealed", False)
    start_revealed = set(spec.get("start_revealed", set()))
    cols = list(spec.get("cols", COLS))
    row_numbers = list(spec.get("row_numbers", range(1, len(spec["rows"]) + 1)))
    for row_offset, row_data in enumerate(spec["rows"]):
        row_index = row_numbers[row_offset]
        for col_index, code in enumerate(row_data):
            pos = (cols[col_index], row_index)
            tile_type = TILE_CODE_TYPES.get(code, "plains")
            terrain = terrain_for_fixed_tile(tile_type)
            tile = {
                "type": tile_type,
                "terrain": terrain,
                "visited": False,
                "merchant_stock": None,
                "loot_available": tile_type not in ("water", "plains"),
                "enemies_cleared": tile_type in ("water", "plains", "village", "port", "capital"),
                "revealed": fully_revealed or pos in start_revealed,
                "map_key": map_key,
            }
            if map_key == "continent":
                tile["region"] = region_for_pos(pos)
            if tile_type in ("village", "port", "capital"):
                tile["merchant_stock"] = generate_merchant_stock(map_key)
            if tile_type == "slime_lair":
                tile["enemies_cleared"] = False
                tile["loot_available"] = False
                tile["boss"] = "slime_king"
            tile.update(named_tiles.get(pos, {}))
            world[pos] = tile
    return world


def terrain_for_fixed_tile(tile_type):
    if tile_type == "water":
        return "water"
    if tile_type == "port":
        return "sand"
    if tile_type in ("forest", "slime_lair"):
        return "dark_grass"
    if tile_type in ("cave", "castle", "dungeon", "dragon_lair"):
        return "grass"
    return "grass"


def generate_random_world():
    """Legacy random world generator, kept for experiments."""
    world = {}
    terrain = generate_terrain()
    capital_pos = CAPITAL_POS

    sand_positions = {pos for pos, t in terrain.items() if t == "sand"}
    grass_available = [pos for pos in terrain
                       if terrain[pos] in ("grass", "dark_grass") and pos != capital_pos]

    # Place ports on sand
    sand_available = [pos for pos in sand_positions if pos != capital_pos]
    port_positions = random.sample(sand_available, min(PORT_COUNT, len(sand_available))) if sand_available else []

    # Place other specials on grass/dark_grass
    total_needed = sum(n for _, n in WORLD_TILE_COUNTS)
    chosen = random.sample(grass_available, min(total_needed, len(grass_available)))
    idx = 0
    special_map = {}
    for tile_type, count in WORLD_TILE_COUNTS:
        for _ in range(count):
            if idx < len(chosen):
                special_map[chosen[idx]] = tile_type
                idx += 1

    special_map[capital_pos] = "capital"
    for pos in port_positions:
        special_map[pos] = "port"

    for c in COLS:
        for r in ROWS:
            pos = (c, r)
            ter = terrain[pos]
            if ter == "water":
                world[pos] = {
                    "type": "water", "terrain": "water",
                    "visited": False, "merchant_stock": None,
                    "loot_available": False, "enemies_cleared": True,
                }
                continue

            tile_type = special_map.get(pos, "plains")
            tile = {
                "type": tile_type, "terrain": ter,
                "visited": False, "merchant_stock": None,
                "loot_available": True, "enemies_cleared": False,
            }
            if tile_type in ("village", "port"):
                tile["merchant_stock"] = generate_merchant_stock()
            if tile_type == "capital":
                tile["revealed"] = True
                tile["merchant_stock"] = generate_merchant_stock()
            elif tile_type not in ("plains",):
                tile["revealed"] = False
            world[pos] = tile

    return world


def draw_map(world, player_pos=None, title=None, region_filter=None, cols=None, rows=None, show_all=False):
    """Render the world map with terrain backgrounds and ASCII symbols."""
    col_w = 4
    cols, rows = cols or world_axes(world)[0], rows or world_axes(world)[1]
    print()
    if title:
        print(styled(f"  {title}", C.BOLD, C.YELLOW))
        print()

    header = "      " + " ".join(c.center(col_w) for c in cols)
    print(styled(header, C.BOLD, C.CYAN))

    sep_line = "     " + "-" * (len(cols) * (col_w + 1) - 1)
    print(styled(sep_line, C.DIM))

    for r in rows:
        row_label = styled(f" {r:>2} ", C.BOLD, C.CYAN) + styled("| ", C.DIM)
        cells_str = []
        for c in cols:
            pos = (c, r)
            tile = world[pos]
            t = tile["type"]
            if region_filter and tile.get("region") != region_filter:
                t = "unknown"
            ter = tile.get("terrain", "grass")
            bg = BG_COLORS.get(ter, "")
            symbol_visible = show_all or tile.get("revealed") or tile.get("visited") or pos == player_pos

            if pos == player_pos and t != "unknown":
                cell_str = bg + C.BOLD + C.WHITE + "@".center(col_w) + C.RESET
            elif t == "water":
                cell_str = bg + C.BOLD + C.WHITE + "~".center(col_w) + C.RESET
            elif t == "unknown":
                cell_str = bg + C.DIM + "?".center(col_w) + C.RESET
            elif t not in ("plains", "water") and not symbol_visible:
                cell_str = bg + C.DIM + ".".center(col_w) + C.RESET
            else:
                sym = TILE_SYMBOLS[t]
                color = TILE_COLORS[t]
                cell_str = bg + color + sym.center(col_w) + C.RESET
            cells_str.append(cell_str)
        print(row_label + " ".join(cells_str))

    print()
    legend_parts = []
    for t_type in ["plains", "forest", "village", "slime_lair", "cave", "castle", "dungeon",
                    "capital", "dragon_lair", "port", "water"]:
        sym = TILE_SYMBOLS[t_type]
        name = TILE_NAMES[t_type]
        color = TILE_COLORS[t_type]
        legend_parts.append(styled(sym, color) + styled(f"={name}", C.DIM))
    print("     " + "  ".join(legend_parts))
    print()


def find_poi(world, exclude_pos=None):
    """Find all points of interest (non-plains, non-water) on the map."""
    pois = []
    for pos, tile in world.items():
        if tile["type"] not in ("plains", "water"):
            if exclude_pos and pos == exclude_pos:
                continue
            pois.append((pos, tile["type"]))
    return pois


def coord_label(pos):
    """Convert (col, row) to 'A1', 'J10', etc."""
    return f"{pos[0]}{pos[1]}"
