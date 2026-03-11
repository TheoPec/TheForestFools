"""World generation and map rendering."""

import random

from data.config import COLS, ROWS, CAPITAL_POS, WORLD_TILE_COUNTS, PORT_COUNT
from data.locations import TILE_SYMBOLS, TILE_NAMES
from data.consumables import CONSUMABLES
from data.weapons import WEAPONS
from data.armors import ARMORS
from engine.terminal import C, styled, TILE_COLORS, BG_COLORS


def generate_merchant_stock():
    """Generate a random merchant stock."""
    stock = []
    for key in random.sample(list(CONSUMABLES.keys()), k=min(3, len(CONSUMABLES))):
        stock.append(key)
    for key in random.sample(list(WEAPONS.keys()), k=random.randint(1, 3)):
        stock.append(key)
    if random.random() < 0.6:
        stock.append(random.choice(list(ARMORS.keys())))
    return stock


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
    """Create a 10x10 world grid with terrain. Returns dict keyed by (col_letter, row_number)."""
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


def draw_map(world, player_pos=None):
    """Render the world map with terrain backgrounds and ASCII symbols."""
    col_w = 4
    print()

    header = "      " + " ".join(c.center(col_w) for c in COLS)
    print(styled(header, C.BOLD, C.CYAN))

    sep_line = "     " + "-" * (len(COLS) * (col_w + 1) - 1)
    print(styled(sep_line, C.DIM))

    for r in ROWS:
        row_label = styled(f" {r:>2} ", C.BOLD, C.CYAN) + styled("| ", C.DIM)
        cells_str = []
        for c in COLS:
            pos = (c, r)
            tile = world[pos]
            t = tile["type"]
            ter = tile.get("terrain", "grass")
            bg = BG_COLORS.get(ter, "")

            if t == "water":
                cell_str = bg + C.BOLD + C.WHITE + "~".center(col_w) + C.RESET
            elif t not in ("plains", "capital") and not tile.get("revealed", False) and pos != player_pos:
                cell_str = bg + C.DIM + ".".center(col_w) + C.RESET
            else:
                sym = TILE_SYMBOLS[t]
                color = TILE_COLORS[t]
                cell_str = bg + color + sym.center(col_w) + C.RESET
            cells_str.append(cell_str)
        print(row_label + " ".join(cells_str))

    print()
    legend_parts = []
    for t_type in ["plains", "forest", "village", "cave", "castle", "dungeon",
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
