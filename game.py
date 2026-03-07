#!/usr/bin/env python3
"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  _   _    _    ___
  |_   _| || | __|  | __|/ _ \\| _ \\ __/ __|_   _|  | __|| | | |  | |  / __|
    | | | __ | _|   | _|| (_) |   / _|\\__ \\ | |    | _| | |_| |_ | |__|\\__ \\
    |_| |_||_|___|  |_|  \\___/|_|_\\___|___/ |_|    |_|   \\___/\\__||____|___/

A dark medieval gothic exploration game for the terminal.
"""

import random
import sys
import os
import textwrap
import time

try:
    import ctypes
except ImportError:
    ctypes = None

# ---------------------------------------------------------------------------
# Terminal helpers
# ---------------------------------------------------------------------------

# ANSI colors
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GREY    = "\033[90m"

def styled(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET

# ---------------------------------------------------------------------------
# ASCII tile symbols -- fixed width, no emoji
# ---------------------------------------------------------------------------

TILE_SYMBOLS = {
    "plains":     ".",
    "forest":     "T",
    "village":    "V",
    "cave":       "O",
    "castle":     "#",
    "dungeon":    "X",
    "capital":    "K",
    "dragon_lair": "D",
}

TILE_COLORS = {
    "plains":     C.DIM,
    "forest":     C.GREEN,
    "village":    C.YELLOW,
    "cave":       C.GREY,
    "castle":     C.MAGENTA,
    "dungeon":    C.RED,
    "capital":    C.BOLD + C.YELLOW,
    "dragon_lair": C.RED + C.BOLD,
}

TILE_NAMES = {
    "plains":     "Plains",
    "forest":     "Forest",
    "village":    "Village",
    "cave":       "Cave",
    "castle":     "Castle",
    "dungeon":    "Dungeon",
    "capital":    "Capital",
    "dragon_lair": "Dragon Lair",
}

# ---------------------------------------------------------------------------
# Data: Items
# ---------------------------------------------------------------------------

WEAPONS = {
    "rusty_sword":    {"name": "Rusty Sword",    "attack": 3,  "value": 5},
    "iron_dagger":    {"name": "Iron Dagger",    "attack": 5,  "value": 12},
    "iron_sword":     {"name": "Iron Sword",     "attack": 8,  "value": 25},
    "steel_sword":    {"name": "Steel Sword",    "attack": 12, "value": 50},
    "war_hammer":     {"name": "War Hammer",     "attack": 14, "value": 65},
    "dark_blade":     {"name": "Dark Blade",     "attack": 18, "value": 120},
    "silver_longsword": {"name": "Silver Longsword", "attack": 22, "value": 200},
    "cursed_greatsword": {"name": "Cursed Greatsword", "attack": 28, "value": 350},
    "dragon_slayer_blade": {"name": "Dragon Slayer Blade", "attack": 35, "value": 1000},
}

ARMORS = {
    "cloth_rags":     {"name": "Cloth Rags",       "armor": 1,  "value": 3},
    "leather_vest":   {"name": "Leather Vest",     "armor": 4,  "value": 15},
    "chainmail":      {"name": "Chainmail",        "armor": 8,  "value": 45},
    "plate_armor":    {"name": "Plate Armor",      "armor": 14, "value": 100},
    "dark_plate":     {"name": "Dark Plate",       "armor": 20, "value": 250},
    "shadow_cloak":   {"name": "Shadow Cloak",     "armor": 10, "value": 80},
}

CONSUMABLES = {
    "small_potion":   {"name": "Small Potion",   "heal": 25, "value": 8},
    "medium_potion":  {"name": "Medium Potion",  "heal": 50, "value": 20},
    "large_potion":   {"name": "Large Potion",   "heal": 100, "value": 45},
    "elixir":         {"name": "Elixir",         "heal": 200, "value": 100},
}

MISC_ITEMS = {
    "old_key":        {"name": "Old Key",        "value": 2},
    "skull_amulet":   {"name": "Skull Amulet",   "value": 30},
    "raven_feather":  {"name": "Raven Feather",  "value": 1},
    "golden_chalice": {"name": "Golden Chalice", "value": 75},
    "torn_scroll":    {"name": "Torn Scroll",    "value": 5},
    "dark_gem":       {"name": "Dark Gem",       "value": 60},
    "iron_ring":      {"name": "Iron Ring",      "value": 10},
}

ALL_ITEMS = {}
ALL_ITEMS.update(WEAPONS)
ALL_ITEMS.update(ARMORS)
ALL_ITEMS.update(CONSUMABLES)
ALL_ITEMS.update(MISC_ITEMS)

# ---------------------------------------------------------------------------
# Data: Enemies
# ---------------------------------------------------------------------------

ENEMIES = [
    {"name": "Hollow Wraith",    "hp": 30,  "attack": 6,  "gold": (5, 15),  "xp": 15},
    {"name": "Skeletal Soldier",  "hp": 40,  "attack": 8,  "gold": (8, 20),  "xp": 20},
    {"name": "Plague Rat Swarm",  "hp": 20,  "attack": 4,  "gold": (2, 8),   "xp": 8},
    {"name": "Cursed Knight",     "hp": 70,  "attack": 14, "gold": (15, 40), "xp": 40},
    {"name": "Tomb Guardian",     "hp": 60,  "attack": 12, "gold": (12, 30), "xp": 30},
    {"name": "Shadow Stalker",    "hp": 50,  "attack": 10, "gold": (10, 25), "xp": 25},
    {"name": "Undead Priest",     "hp": 45,  "attack": 11, "gold": (10, 28), "xp": 28},
    {"name": "Giant Spider",      "hp": 35,  "attack": 7,  "gold": (4, 12),  "xp": 12},
    {"name": "Goblin Scavenger",  "hp": 25,  "attack": 5,  "gold": (3, 10),  "xp": 10},
    {"name": "Dark Sorcerer",     "hp": 55,  "attack": 16, "gold": (20, 50), "xp": 45},
    {"name": "Bone Colossus",     "hp": 100, "attack": 20, "gold": (30, 70), "xp": 60},
]

# ---------------------------------------------------------------------------
# Data: Gothic Descriptions
# ---------------------------------------------------------------------------

DESC_PLAINS = [
    "An open stretch of grey, wind-swept land. Dead grass sways beneath a sky heavy with iron clouds. The silence is broken only by the distant cry of a raven.",
    "A barren field stretches endlessly. The earth is cracked and dry. A lone, withered tree stands against the pale horizon like a skeletal hand reaching for the heavens.",
    "Flat, featureless moorland rolls in every direction. A thin mist clings to the ground. Somewhere far away, a bell tolls slowly.",
    "The wind howls across desolate plains. Broken wagon wheels and scattered bones suggest travellers once passed this way. None remain.",
    "A vast emptiness. The grey sky presses down like a stone lid. You feel watched, though nothing stirs.",
]

DESC_FOREST = [
    "Ancient trees crowd together, their gnarled branches intertwined like the fingers of the damned. No sunlight reaches the forest floor. The air smells of rot and damp earth.",
    "A dense, lightless wood. Twisted roots break through the soil like veins. Strange fungus glows faintly on the bark. Something moves in the canopy above.",
    "The forest is silent and suffocating. Moss-covered stones form unnatural patterns among the trees. An old path, nearly consumed by undergrowth, leads deeper into the darkness.",
    "Black pines rise like cathedral pillars into the mist. The ground is carpeted with dead needles. A cold wind carries whispers you cannot quite understand.",
]

DESC_VILLAGE = [
    "A small hamlet of crooked timber houses huddles behind a low stone wall. Smoke rises thinly from a few chimneys. The villagers eye you with suspicion and something like fear.",
    "Ramshackle buildings lean against one another as if exhausted. A chapel bell hangs cracked and silent. Mud lanes wind between shuttered windows and bolted doors.",
    "A grim settlement. The houses are dark, their thatched roofs sagging. A gallows stands in the village square, its rope swaying in the wind. A dog barks somewhere unseen.",
]

DESC_CAVE = [
    "A yawning hole in the rock face exhales cold, stale air. The darkness inside is absolute. Water drips in a slow, maddening rhythm from somewhere deep within.",
    "The cave mouth is framed by jagged stone teeth. Scratches and old bloodstains mark the entrance. The smell of damp stone and something worse drifts outward.",
    "A narrow fissure in a cliff wall opens into blackness. The wind moans as it passes over the entrance. Old torches, long extinguished, are jammed into cracks in the rock.",
]

DESC_CASTLE = [
    "A fortress of black stone rises against the sky, its towers broken and overgrown with ivy. The portcullis hangs askew. Crows circle the battlements in endless, silent orbits.",
    "The castle looms above you, vast and lightless. Arrow slits stare down like hollow eyes. The drawbridge is down but the courtyard beyond is choked with fog and rubble.",
    "Once a seat of power, this castle is now a ruin. Shattered banners hang from the walls. The great hall's roof has collapsed, and moonlight falls on a floor of dust and bones.",
]

DESC_DUNGEON = [
    "Iron-bound doors open onto steps that descend into darkness. The walls are slick with moisture and something darker. Chains rattle faintly below, though no wind stirs them.",
    "A dungeon entrance, half-hidden by fallen masonry. The air rising from below is foul and warm. Scratches on the walls form words in a language you do not recognise.",
]

DESC_CAPITAL = [
    "The great capital city rises before you, its towers of pale stone gleaming against the iron sky. Banners bearing the royal sigil snap in the wind above the massive gatehouse. The streets within teem with merchants, soldiers, and the desperate alike.",
    "Walls of ancient stone encircle the capital, worn but unbroken by centuries of war. The city within is a maze of cobbled streets and tall buildings. At its heart, the royal palace looms above everything.",
]

DESC_DRAGON_LAIR = [
    "A vast cavern carved into the mountain by claws and fire. The walls are scorched black, and the stench of sulphur is overwhelming. Bones of the unfortunate litter the ground.",
    "Heat radiates from deep within the lair. The ceiling is lost in smoke and shadow. A low, rhythmic sound echoes through the tunnels -- breathing. Something ancient breathes here.",
]

# Sub-location descriptions
DESC_SUBLOCS = {
    # Village sub-locations
    "merchant": [
        "A cramped shop crammed with dusty wares. The merchant watches you from behind a counter stacked with oddities. Candles gutter in the draught.",
        "Shelves of potions, blades, and curiosities line the walls. The merchant nods slowly, their face half-hidden in shadow.",
    ],
    "blacksmith": [
        "The forge glows red in the gloom. The blacksmith, a massive figure scarred by years of fire, hammers at a blade without looking up.",
        "Heat and the smell of molten metal fill the smithy. Weapons line the walls. The blacksmith grunts a greeting.",
    ],
    "tavern": [
        "A low-ceilinged room thick with smoke and the smell of sour ale. A handful of patrons sit in silence. The barkeep polishes a cracked tankard.",
        "The tavern is dark and crowded. A fire sputters in the hearth. Someone plays a slow, mournful tune on a lute in the corner.",
    ],
    "chapel": [
        "A small stone chapel. The altar is bare. Candles burn low before a faceless saint. The air is cold and still, as if prayer itself has frozen here.",
        "Broken pews face a crumbling altar. Stained glass, mostly shattered, casts dim coloured light on the flagstones. It smells of old incense and dust.",
    ],
    "square": [
        "The village square is empty. A well stands at its centre, its bucket missing. The cobblestones are cracked and weeds push through.",
        "A muddy open space surrounded by leaning buildings. A noticeboard displays faded warnings. A crow perches on the gallows post.",
    ],
    # Dungeon / cave sub-locations
    "entrance": [
        "The entrance is narrow and dark. Old torches, long dead, line the walls. The stone underfoot is worn smooth by countless feet -- or claws.",
    ],
    "corridor": [
        "A long, low corridor stretches into blackness. The walls are damp. Your footsteps echo strangely, as if something echoes back a moment too late.",
    ],
    "crypt": [
        "Stone sarcophagi line the walls, their lids cracked or displaced. Bones spill onto the floor. The air is thick with the sweet stench of decay.",
    ],
    "altar": [
        "A black stone altar stands at the centre of a vaulted chamber. Dark stains run down its sides. Symbols are carved into the floor around it.",
    ],
    "treasure_room": [
        "A heavy door opens onto a small chamber. Chests, some broken, some locked, line the walls. Gold coins are scattered among dust and cobwebs.",
    ],
    # Castle sub-locations
    "courtyard": [
        "A wide courtyard choked with fog. Broken statues and overturned carts litter the ground. The keep looms ahead, dark and silent.",
    ],
    "great_hall": [
        "A vast hall with a collapsed roof. Moonlight falls on a long table still set with rusted plates. A throne sits at the far end, draped in cobwebs.",
    ],
    "tower": [
        "A spiral staircase winds upward through darkness. The stone steps are narrow and uneven. Wind howls through arrow slits.",
    ],
    "dungeon_cells": [
        "Iron-barred cells line both sides of a narrow passage. Most are empty. In one, a skeleton still hangs from its manacles.",
    ],
    "throne_room": [
        "A grand chamber, cold and dark. The throne is carved from black stone. Tattered banners hang from the walls, bearing sigils no living man remembers.",
    ],
    # Forest sub-locations
    "clearing": [
        "A small clearing in the dense wood. Pale light filters through the canopy. Mushrooms grow in a perfect circle on the forest floor.",
    ],
    "ruins": [
        "Crumbling stone walls peek through the undergrowth. An old foundation, long overgrown. Something was here once. Something that was deliberately destroyed.",
    ],
    "stream": [
        "A dark stream winds through the trees. The water is cold and clear but tastes faintly of iron. Moss-covered stones line its banks.",
    ],
    "barracks": [
        "Rows of bunks line the walls of the barracks. Soldiers sharpen blades and mend armour in grim silence. The smell of iron and sweat hangs heavy in the air.",
    ],
    "tunnel": [
        "A wide tunnel carved by something enormous. Claw marks score the walls from floor to ceiling. Embers smoulder in cracks in the rock.",
    ],
    "hoard": [
        "A vast chamber piled high with gold, jewels, and the armour of fallen heroes. The wealth of a kingdom lies here, guarded by centuries of draconic greed.",
    ],
    "nest": [
        "The heart of the lair. Massive bones and scorched stone form a crude nest. The heat is almost unbearable. Then you see it -- the dragon, coiled and vast, one enormous eye sliding open to regard you.",
    ],
}

# ---------------------------------------------------------------------------
# Data: Location sub-location definitions
# ---------------------------------------------------------------------------

SUBLOCS = {
    "village": ["merchant", "blacksmith", "tavern", "chapel", "square"],
    "cave":    ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "dungeon": ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "castle":  ["courtyard", "great_hall", "tower", "dungeon_cells", "throne_room"],
    "forest":  ["clearing", "ruins", "stream"],
    "capital": ["courtyard", "great_hall", "throne_room", "barracks", "merchant"],
    "dragon_lair": ["entrance", "tunnel", "hoard", "nest"],
}

# ---------------------------------------------------------------------------
# Data: NPC dialogue templates
# ---------------------------------------------------------------------------
# {loc_type} and {coord} are replaced at runtime with actual world data.

NPC_DIALOGUES = {
    "tavern": {
        "barkeep": [
            '"Ale?" The barkeep slides a cracked tankard toward you. "A traveller, eh. You look half-dead already." He leans closer. "Word is there\'s a {loc_type} at {coord}. Folk who went there... didn\'t come back."',
            '"Keep your voice down." The barkeep glances around. "A merchant came through last week, raving about a {loc_type} near {coord}. Said he saw things crawling in the dark. I say stay away."',
            '"You want advice? Head to {coord}. There\'s a {loc_type} there. Dangerous, aye, but those who survive come back richer than kings. Or they don\'t come back at all."',
        ],
        "drunk": [
            'A man slumped over the bar grabs your arm. "I seen it... the {loc_type}... at {coord}..." He shivers. "The dead walk there. They walk and they wait."',
            '"Hic... you look strong enough..." A drunk patron waves vaguely. "Go to {coord}. The {loc_type}... there\'s treasure. Gold. I\'d go myself but... hic... my legs don\'t work so good."',
        ],
        "hooded_figure": [
            'A hooded figure in the corner beckons. "Seek the {loc_type} at {coord}. What you find there will change you. For better or worse." They vanish into shadow before you can reply.',
        ],
    },
    "blacksmith": {
        "blacksmith": [
            'The blacksmith doesn\'t look up from his anvil. "You\'ll need better steel if you\'re heading to {coord}. There\'s a {loc_type} there. The things inside... they don\'t die easy."',
            '"I forged a blade for a knight once. He was bound for the {loc_type} at {coord}." The blacksmith pauses. "The blade came back. He didn\'t."',
            '"Word of advice, stranger. The {loc_type} at {coord} -- don\'t go at night. Not that it matters. It\'s always night down there."',
        ],
    },
    "chapel": {
        "priest": [
            'The priest turns slowly. His eyes are milky and unfocused. "The darkness gathers at {coord}. A {loc_type} festers there like a wound in the earth. Pray before you go. It may be your last chance."',
            '"Child, the dead do not rest at {coord}. The {loc_type} there is cursed. I have blessed many who went to face it. I have buried more."',
            '"I hear confessions from soldiers who returned from {coord}. The {loc_type}... it changed them. They speak of altars and bones and things that should not live."',
        ],
    },
    "square": {
        "old_woman": [
            'An old woman sits by the well, muttering. She looks up as you approach. "The crows fly toward {coord}. Where crows gather, death follows. There\'s a {loc_type} there. Mark my words."',
            '"You\'re not from here." The old woman clutches a dead raven to her chest. "Go to {coord} if you want answers. The {loc_type} holds secrets. But secrets have teeth."',
        ],
        "guard": [
            'A guard leans against the gallows post. "We lost three men at {coord} last month. {loc_type}. Whatever\'s in there, it\'s getting bolder. Could use someone fool enough to go in."',
        ],
    },
    "merchant": {
        "merchant": [
            '"Ah, a customer." The merchant smiles thinly. "If you\'re heading to the {loc_type} at {coord}, you\'ll want potions. Lots of potions. The things down there don\'t bargain."',
            '"I trade with every village in these lands. The one near {coord}? They won\'t go near the {loc_type} anymore. Bad for business, but good for yours -- less competition for whatever\'s inside."',
        ],
    },
}

# Dialogue for non-village locations (forest, cave, castle, dungeon NPCs)
NPC_DIALOGUES_WILD = {
    "clearing": {
        "hermit": [
            'A gaunt figure crouches by a fire of green flame. "You seek purpose? Go to {coord}. The {loc_type} there calls to those who listen. I heard it once. I will not hear it again."',
        ],
    },
    "ruins": {
        "ghost": [
            'A pale shimmer in the air. A voice, thin as wind: "I fell at {coord}. The {loc_type}... it took everything. Avenge me, or join me."',
        ],
    },
    "courtyard": {
        "dying_knight": [
            'A knight slumps against a broken pillar, bleeding. "The {loc_type} at {coord}... we tried to clear it. Too many of them." He coughs blood. "Finish what we started."',
        ],
    },
    "entrance": {
        "survivor": [
            'A figure stumbles out of the darkness, wild-eyed. "Don\'t... don\'t go deeper." They grip your shoulder. "But if you want real treasure, the {loc_type} at {coord} is worse. And richer."',
        ],
    },
}

# ---------------------------------------------------------------------------
# Data: Merchant inventories
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# World Generation
# ---------------------------------------------------------------------------

COLS = "ABCDEFGHIJ"
ROWS = range(1, 11)

def generate_world():
    """Create a 10x10 world grid. Returns dict keyed by (col_letter, row_number)."""
    world = {}
    cells = [(c, r) for c in COLS for r in ROWS]

    # Capital is always at E5
    capital_pos = ("E", 5)
    reserved = {capital_pos}

    available = [c for c in cells if c not in reserved]

    special = []
    counts = [("forest", 3), ("village", 3), ("cave", 2), ("castle", 2), ("dungeon", 2), ("dragon_lair", 1)]
    chosen = random.sample(available, sum(n for _, n in counts))
    idx = 0
    for tile_type, count in counts:
        for _ in range(count):
            special.append((chosen[idx], tile_type))
            idx += 1

    special_map = {pos: t for pos, t in special}
    special_map[capital_pos] = "capital"

    for c in COLS:
        for r in ROWS:
            pos = (c, r)
            tile_type = special_map.get(pos, "plains")
            tile = {
                "type": tile_type,
                "visited": False,
                "merchant_stock": None,
                "loot_available": True,
                "enemies_cleared": False,
            }
            if tile_type == "village":
                tile["merchant_stock"] = generate_merchant_stock()
            if tile_type == "capital":
                tile["revealed"] = True
                tile["merchant_stock"] = generate_merchant_stock()
            elif tile_type != "plains":
                tile["revealed"] = False
            world[pos] = tile

    return world


def draw_map(world, player_pos=None):
    """Render the world map using ASCII symbols with perfect alignment."""
    # Fixed column width of 4 characters per cell
    col_w = 4
    print()

    # Header row:  "      A   B   C   D   E   F   G   H   I   J"
    header = "      " + " ".join(c.center(col_w) for c in COLS)
    print(styled(header, C.BOLD, C.CYAN))

    # Separator
    sep_line = "     " + "-" * (len(COLS) * (col_w + 1) - 1)
    print(styled(sep_line, C.DIM))

    for r in ROWS:
        # Row label: " 1 | ", " 2 | ", ..., "10 | "
        row_label = styled(f" {r:>2} ", C.BOLD, C.CYAN) + styled("| ", C.DIM)
        cells_str = []
        for c in COLS:
            pos = (c, r)
            tile = world[pos]
            t = tile["type"]
            # Hidden location logic
            if t != "plains" and t != "capital" and not tile.get("revealed", False) and pos != player_pos:
                cell_str = styled(".".center(col_w), C.DIM)
            else:
                sym = TILE_SYMBOLS[t]
                color = TILE_COLORS[t]
                cell_str = styled(sym.center(col_w), color)
            cells_str.append(cell_str)
        print(row_label + " ".join(cells_str))

    # Legend
    print()
    legend_parts = []
    for t_type in ["plains", "forest", "village", "cave", "castle", "dungeon", "capital", "dragon_lair"]:
        sym = TILE_SYMBOLS[t_type]
        name = TILE_NAMES[t_type]
        color = TILE_COLORS[t_type]
        legend_parts.append(styled(sym, color) + styled(f"={name}", C.DIM))
    print("     " + "  ".join(legend_parts))
    print()


# ---------------------------------------------------------------------------
# Helper: find interesting locations on the map
# ---------------------------------------------------------------------------

def find_poi(world, exclude_pos=None):
    """Find all points of interest (non-plains) on the map."""
    pois = []
    for pos, tile in world.items():
        if tile["type"] != "plains":
            if exclude_pos and pos == exclude_pos:
                continue
            pois.append((pos, tile["type"]))
    return pois


def coord_label(pos):
    """Convert (col, row) to 'A1', 'J10', etc."""
    return f"{pos[0]}{pos[1]}"


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.base_attack = 3
        self.base_armor = 0
        self.gold = 20
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50

        self.weapon = "rusty_sword"
        self.armor_equipped = "cloth_rags"

        # Inventory
        self.weapons = ["rusty_sword"]
        self.armors = ["cloth_rags"]
        self.consumables = ["small_potion"]
        self.misc = []

        # Location
        self.pos: tuple[str, int] = ("E", 5)
        self.inside = None       # None = on the map; "village", "cave", etc.
        self.subloc = None       # sub-location inside a location

        # Quest state
        self.dragon_quest = None  # None, "given", "completed"

    @property
    def attack(self):
        w = WEAPONS.get(self.weapon, {})
        return self.base_attack + w.get("attack", 0)

    @property
    def armor_value(self):
        a = ARMORS.get(self.armor_equipped, {})
        return self.base_armor + a.get("armor", 0)

    def weapon_name(self):
        w = WEAPONS.get(self.weapon)
        return w["name"] if w else "Bare Fists"

    def armor_name(self):
        a = ARMORS.get(self.armor_equipped)
        return a["name"] if a else "None"

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, raw_dmg):
        reduced = max(1, raw_dmg - self.armor_value // 2)
        self.hp -= reduced
        return reduced

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.base_attack += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            leveled = True
        return leveled

    def has_item(self, key):
        return (key in self.weapons or key in self.armors or
                key in self.consumables or key in self.misc)

    def add_item(self, key):
        if key in WEAPONS:
            self.weapons.append(key)
        elif key in ARMORS:
            self.armors.append(key)
        elif key in CONSUMABLES:
            self.consumables.append(key)
        elif key in MISC_ITEMS:
            self.misc.append(key)

    def remove_item(self, key):
        for lst in (self.weapons, self.armors, self.consumables, self.misc):
            if key in lst:
                lst.remove(key)
                return True
        return False


# ---------------------------------------------------------------------------
# Gothic console font setup
# ---------------------------------------------------------------------------

def set_gothic_font():
    """Try to set a gothic/medieval looking console font on Windows."""
    if not sys.stdout.isatty():
        return
    try:
        os.system('mode con cols=120 lines=40')
        if os.name == 'nt' and ctypes:
            LF_FACESIZE = 32
            STD_OUTPUT_HANDLE = -11
            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
            class CONSOLE_FONT_INFOEX(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("nFont", ctypes.c_ulong),
                    ("dwFontSize", COORD),
                    ("FontFamily", ctypes.c_uint),
                    ("FontWeight", ctypes.c_uint),
                    ("FaceName", ctypes.c_wchar * LF_FACESIZE),
                ]
            kernel32 = ctypes.windll.kernel32
            hOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            font = CONSOLE_FONT_INFOEX()
            font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
            font.dwFontSize.X = 0
            font.dwFontSize.Y = 18
            font.FontFamily = 54
            font.FontWeight = 400
            for font_name in ["Consolas", "Courier New", "Lucida Console"]:
                font.FaceName = font_name
                if kernel32.SetCurrentConsoleFontEx(hOut, False, ctypes.byref(font)):
                    break
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Intro sequence
# ---------------------------------------------------------------------------

def show_intro():
    print("\033[2J\033[H", end="", flush=True)

    skull = r"""
                      ______
                   .-"      "-.
                  /            \
                 |              |
                 |,  .-.  .-.  ,|
                 | )(__/  \__)( |
                 |/     /\     \|
                 (_     ^^     _)
                  \__|IIIIII|__/
                   | \IIIIII/ |
                   \          /
                    `--------`
"""
    for line in skull.split('\n'):
        if line.strip():
            print(styled(line, C.RED))
            time.sleep(0.08)

    time.sleep(0.5)

    lines = [
        (styled("\n  In an age of shadow and ruin...", C.DIM, C.WHITE), 1.2),
        (styled("  The realm has fallen to darkness.", C.DIM, C.WHITE), 1.0),
        (styled("  Ancient evils stir in forgotten places.", C.WHITE), 1.0),
        (styled("  A dragon of terrible power has awakened.", C.RED), 1.2),
    ]
    for line, delay in lines:
        print(line)
        time.sleep(delay)

    dragon = r"""
                           ______________
                     ,===:'.,            `-._
                          `:.`---.__         `-._
                            `:.     `--.         `.
                              \.        `.         `.
                      (,,(,    \.         `.   ____,-`.,
                   (,'     `/   \.   ,--.___`.'
               ,  ,'  ,--.  `,   \.;'         `
                `{D, {    \  :    \;
                  V,,'    /  /    //
                  j;;    /  ,' ,-//.    ,---.      ,
                  \;'   /  ,' /  _  \  /  _  \   ,'/
                         \   `'  / \  `'  / \  `.' /
                          `.___,'   `.__,'   `.__,'
"""
    print()
    for line in dragon.split('\n'):
        if line.strip():
            print(styled(line, C.RED))
            time.sleep(0.05)

    time.sleep(0.5)

    lines2 = [
        (styled("\n  Its shadow stretches across the dying land.", C.RED), 1.0),
        (styled("\n  But one soul remains...", C.YELLOW), 1.5),
        (styled("  A lone wanderer. Scarred. Determined. Unyielding.", C.YELLOW), 1.2),
        (styled("\n  You.", C.BOLD, C.WHITE), 2.0),
    ]
    for line, delay in lines2:
        print(line)
        time.sleep(delay)

    sword = r"""
                         /\
                        /  \
                       /    \
                      /  **  \
                     /________\
                         ||
                         ||
                         ||
                        _||_
                       |    |
                       |____|
"""
    for line in sword.split('\n'):
        if line.strip():
            print(styled(line, C.YELLOW))
            time.sleep(0.06)

    lines3 = [
        (styled("\n  The King awaits at the capital.", C.DIM), 0.8),
        (styled("  The quest will find you.", C.DIM), 2.0),
    ]
    for line, delay in lines3:
        print(line)
        time.sleep(delay)

    print()
    try:
        input(styled("  Press Enter to begin your journey...", C.BOLD, C.YELLOW))
    except (EOFError, KeyboardInterrupt):
        pass


# ---------------------------------------------------------------------------
# Game Engine
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        self.world = generate_world()
        self.player = Player()
        self.running = True
        self.dragon_lair_pos = next((pos for pos, t in self.world.items() if t["type"] == "dragon_lair"), None)

    # -- helpers --

    def current_tile(self):
        return self.world[self.player.pos]

    def print_sep(self):
        print(styled("=" * 60, C.DIM))

    def wrap_print(self, text, color=C.WHITE):
        for line in textwrap.wrap(text, width=70):
            print(styled("  " + line, color))

    def pos_label(self):
        return coord_label(self.player.pos)

    def location_label(self):
        parts = [self.pos_label()]
        if self.player.inside:
            parts.append(self.player.inside)
        if self.player.subloc:
            parts.append(self.player.subloc)
        return " > ".join(parts)

    def _pick_poi_for_dialogue(self):
        """Pick a random point of interest to mention in NPC dialogue."""
        pois = [(pos, t) for pos, t in find_poi(self.world, exclude_pos=self.player.pos) if t != "dragon_lair"]
        if not pois:
            return None, None, None
        pos, loc_type = random.choice(pois)
        return pos, coord_label(pos), loc_type

    # -- commands --

    def cmd_help(self, _args):
        print()
        print(styled("  COMMANDS", C.BOLD, C.YELLOW))
        print(styled("  --------", C.DIM))
        cmds = [
            ("help",             "Show this help."),
            ("map",              "Display the world map."),
            ("cd {cell}",        "Travel to a map cell.  e.g. cd B4"),
            ("cd {location}",    "Enter a location.      e.g. cd village"),
            ("cd {subloc}",      "Enter a sub-location.  e.g. cd tavern"),
            ("cd ..",            "Go back / leave current location."),
            ("look",             "Describe the current location."),
            ("talk",             "Talk to someone here."),
            ("stats",            "Show your stats."),
            ("inventory / inv",  "Show your inventory."),
            ("equip {item}",     "Equip a weapon or armor."),
            ("use {item}",       "Use a consumable item."),
            ("buy {item}",       "Buy from a merchant (when at merchant)."),
            ("sell {item}",      "Sell to a merchant (when at merchant)."),
            ("fight",            "Fight enemies (in dungeons/caves/forests)."),
            ("search",           "Search for loot (in special locations)."),
            ("quit / exit",      "Quit the game."),
        ]
        for cmd, desc in cmds:
            print(f"  {styled(cmd.ljust(20), C.CYAN)} {styled(desc, C.DIM)}")
        print()

    def cmd_map(self, _args):
        draw_map(self.world, self.player.pos)

    def cmd_look(self, _args):
        tile = self.current_tile()
        print()
        self.print_sep()

        if self.player.subloc:
            descs = DESC_SUBLOCS.get(self.player.subloc, ["You see nothing remarkable."])
            self.wrap_print(random.choice(descs), C.WHITE)
            # Hint that talk is available
            talkable = set()
            talkable.update(NPC_DIALOGUES.get(self.player.subloc, {}).keys())
            talkable.update(NPC_DIALOGUES_WILD.get(self.player.subloc, {}).keys())
            if talkable:
                print()
                print(styled("  Someone is here. Type 'talk' to speak.", C.YELLOW))
        elif self.player.inside:
            desc_map = {
                "plains": DESC_PLAINS, "forest": DESC_FOREST,
                "village": DESC_VILLAGE, "cave": DESC_CAVE,
                "castle": DESC_CASTLE, "dungeon": DESC_DUNGEON,
                "capital": DESC_CAPITAL, "dragon_lair": DESC_DRAGON_LAIR,
            }
            descs = desc_map.get(self.player.inside, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            subs = SUBLOCS.get(self.player.inside, [])
            if subs:
                print()
                print(styled("  You can visit:", C.YELLOW))
                for s in subs:
                    print(styled(f"    cd {s}", C.CYAN))
        else:
            desc_map = {
                "plains": DESC_PLAINS, "forest": DESC_FOREST,
                "village": DESC_VILLAGE, "cave": DESC_CAVE,
                "castle": DESC_CASTLE, "dungeon": DESC_DUNGEON,
                "capital": DESC_CAPITAL, "dragon_lair": DESC_DRAGON_LAIR,
            }
            descs = desc_map.get(tile["type"], DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            if tile["type"] != "plains":
                print()
                print(styled(f"  You can enter: cd {tile['type']}", C.YELLOW))

        self.print_sep()
        print()

    def cmd_talk(self, _args):
        """Talk to NPCs. They give hints about interesting locations on the map."""
        p = self.player
        subloc = p.subloc

        # King in the capital throne room
        if p.inside == "capital" and p.subloc == "throne_room":
            print()
            self.print_sep()
            print(styled("  [The King]", C.BOLD, C.YELLOW))
            print()
            if p.level < 5:
                self.wrap_print("\"You are brave to seek audience, but you are not yet ready. Return when you have proven yourself worthy. (Reach level 5)\"", C.WHITE)
            elif p.dragon_quest is None:
                dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
                self.wrap_print(f"\"The realm is dying. An ancient dragon has awakened and terrorises the land from its lair at {styled(dl_coord, C.BOLD, C.CYAN)}. You must go there and slay the beast. The fate of the kingdom rests upon your shoulders.\"", C.WHITE)
                p.dragon_quest = "given"
                if self.dragon_lair_pos:
                    self.world[self.dragon_lair_pos]["revealed"] = True
                    print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))
            elif p.dragon_quest == "given":
                dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
                self.wrap_print(f"\"The dragon still lives! Go to {styled(dl_coord, C.BOLD, C.CYAN)} and slay the beast!\"", C.WHITE)
            elif p.dragon_quest == "completed":
                self.wrap_print("\"You have saved the kingdom! You shall be remembered as a legend!\"", C.WHITE)
            self.print_sep()
            print()
            return

        if not subloc:
            if p.inside:
                print(styled("  There is no one to talk to here. Try entering a specific place.", C.DIM))
            else:
                print(styled("  There is no one to talk to in the open.", C.DIM))
            return

        # Check village NPC dialogues
        npc_group = NPC_DIALOGUES.get(subloc, {})
        # Check wild NPC dialogues
        wild_group = NPC_DIALOGUES_WILD.get(subloc, {})

        # Merge both
        all_npcs = {}
        all_npcs.update(npc_group)
        all_npcs.update(wild_group)

        if not all_npcs:
            print(styled("  There is no one here willing to speak.", C.DIM))
            return

        # Pick a random NPC from those available
        npc_name = random.choice(list(all_npcs.keys()))
        templates = all_npcs[npc_name]
        template = random.choice(templates)

        # Get a POI to mention
        poi_pos, coord, loc_type = self._pick_poi_for_dialogue()
        if coord and loc_type:
            line = template.format(
                coord=styled(coord, C.BOLD, C.CYAN),
                loc_type=styled(loc_type, C.BOLD, C.YELLOW),
            )
        else:
            # Fallback if somehow no POIs exist
            line = template.format(coord="the far reaches", loc_type="dark place")

        npc_display = npc_name.replace("_", " ").title()
        print()
        self.print_sep()
        print(styled(f"  [{npc_display}]", C.BOLD, C.YELLOW))
        print()
        self.wrap_print(line, C.WHITE)
        if poi_pos:
            self.world[poi_pos]["revealed"] = True
            print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))
        self.print_sep()
        print()

    def cmd_stats(self, _args):
        p = self.player
        print()
        print(styled("  CHARACTER", C.BOLD, C.YELLOW))
        print(styled("  ---------", C.DIM))
        hp_pct = p.hp / p.max_hp
        bar_len = 20
        filled = int(bar_len * hp_pct)
        bar = styled("#" * filled, C.RED) + styled("-" * (bar_len - filled), C.DIM)
        print(f"  HP:      {p.hp}/{p.max_hp} [{bar}]")
        print(f"  Attack:  {styled(str(p.attack), C.RED)}")
        print(f"  Armor:   {styled(str(p.armor_value), C.BLUE)}")
        print(f"  Gold:    {styled(str(p.gold), C.YELLOW)}")
        print(f"  Level:   {p.level}  (XP: {p.xp}/{p.xp_to_next})")
        print(f"  Weapon:  {styled(p.weapon_name(), C.CYAN)}")
        print(f"  Armor:   {styled(p.armor_name(), C.CYAN)}")
        print()

    def cmd_inventory(self, _args):
        p = self.player
        print()
        print(styled("  INVENTORY", C.BOLD, C.YELLOW))
        print(styled("  ---------", C.DIM))
        print(f"  Gold: {styled(str(p.gold), C.YELLOW)}")

        def _list_section(title, items, catalog):
            if items:
                print(f"\n  {styled(title, C.BOLD)}")
                for key in items:
                    info = catalog.get(key, {})
                    name = info.get("name", key)
                    extra = ""
                    if "attack" in info:
                        extra = f" (ATK +{info['attack']})"
                    elif "armor" in info:
                        extra = f" (ARM +{info['armor']})"
                    elif "heal" in info:
                        extra = f" (Heal {info['heal']})"
                    equipped = ""
                    if key == p.weapon:
                        equipped = styled(" [equipped]", C.GREEN)
                    elif key == p.armor_equipped:
                        equipped = styled(" [equipped]", C.GREEN)
                    print(f"    {name}{extra}{equipped}")

        _list_section("Weapons", p.weapons, WEAPONS)
        _list_section("Armor", p.armors, ARMORS)
        _list_section("Consumables", p.consumables, CONSUMABLES)
        _list_section("Misc", p.misc, MISC_ITEMS)
        print()

    def cmd_cd(self, args):
        if not args:
            print(styled("  Usage: cd {cell|location|subloc|..}", C.RED))
            return

        target = args[0].lower()
        p = self.player

        # cd .. -- go back
        if target == "..":
            if p.subloc:
                p.subloc = None
                print(styled(f"  You return to the {p.inside}.", C.YELLOW))
                self.cmd_look([])
            elif p.inside:
                p.inside = None
                print(styled(f"  You step outside at {self.pos_label()}.", C.YELLOW))
            else:
                print(styled("  You are already on the world map.", C.DIM))
            return

        # If inside a location, try sub-location navigation
        if p.inside:
            subs = SUBLOCS.get(p.inside, [])
            if target in subs:
                p.subloc = target
                self.cmd_look([])
                if target == "merchant" and self.current_tile()["type"] in ("village", "capital"):
                    self._show_merchant()
                return
            if target == p.inside:
                p.subloc = None
                self.cmd_look([])
                return

        # Try location entry: cd village, cd cave, etc.
        tile = self.current_tile()
        if target == tile["type"] and target != "plains" and not p.inside:
            p.inside = target
            p.subloc = None
            tile["visited"] = True
            self.cmd_look([])
            return

        # Try cell navigation: cd B4, cd J10, etc.
        cell = args[0].upper()
        if len(cell) >= 2:
            col = cell[0]
            try:
                row = int(cell[1:])
            except ValueError:
                print(styled(f"  Unknown destination: {args[0]}", C.RED))
                return

            if col in COLS and row in ROWS:
                p.inside = None
                p.subloc = None
                p.pos = (col, row)
                new_tile = self.current_tile()
                new_tile["visited"] = True
                print()
                print(styled(f"  You travel to {self.pos_label()}...", C.YELLOW))
                self._describe_arrival(new_tile)
                return
            else:
                print(styled(f"  Invalid cell: {cell}. Use A-J and 1-10.", C.RED))
                return

        print(styled(f"  Unknown destination: {args[0]}", C.RED))

    def _describe_arrival(self, tile):
        t = tile["type"]
        if t == "plains":
            self.wrap_print(random.choice(DESC_PLAINS), C.DIM)
        else:
            desc_map = {
                "forest": DESC_FOREST, "village": DESC_VILLAGE,
                "cave": DESC_CAVE, "castle": DESC_CASTLE, "dungeon": DESC_DUNGEON,
                "capital": DESC_CAPITAL, "dragon_lair": DESC_DRAGON_LAIR,
            }
            descs = desc_map.get(t, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            print(styled(f"\n  There is a {t} here. Use 'cd {t}' to enter.", C.YELLOW))
        print()

    def cmd_equip(self, args):
        if not args:
            print(styled("  Usage: equip {item_name}", C.RED))
            return

        key = "_".join(args).lower()
        p = self.player

        if key in WEAPONS and key in p.weapons:
            p.weapon = key
            print(styled(f"  Equipped {WEAPONS[key]['name']}.", C.GREEN))
        elif key in ARMORS and key in p.armors:
            p.armor_equipped = key
            print(styled(f"  Equipped {ARMORS[key]['name']}.", C.GREEN))
        else:
            print(styled(f"  You don't have '{' '.join(args)}' or it cannot be equipped.", C.RED))

    def cmd_use(self, args):
        if not args:
            print(styled("  Usage: use {item_name}", C.RED))
            return

        key = "_".join(args).lower()
        p = self.player

        if key in CONSUMABLES and key in p.consumables:
            info = CONSUMABLES[key]
            old_hp = p.hp
            p.heal(info["heal"])
            healed = p.hp - old_hp
            p.consumables.remove(key)
            print(styled(f"  Used {info['name']}. Restored {healed} HP. (HP: {p.hp}/{p.max_hp})", C.GREEN))
        else:
            print(styled(f"  You don't have '{' '.join(args)}' or it cannot be used.", C.RED))

    # -- merchant --

    def _show_merchant(self):
        tile = self.current_tile()
        stock = tile.get("merchant_stock", [])
        if not stock:
            print(styled("  The merchant has nothing left to sell.", C.DIM))
            return
        print()
        print(styled("  MERCHANT'S WARES", C.BOLD, C.YELLOW))
        print(styled("  ----------------", C.DIM))
        for key in stock:
            info = ALL_ITEMS.get(key, {})
            name = info.get("name", key)
            value = info.get("value", 0)
            extra = ""
            if "attack" in info:
                extra = f" (ATK +{info['attack']})"
            elif "armor" in info:
                extra = f" (ARM +{info['armor']})"
            elif "heal" in info:
                extra = f" (Heal {info['heal']})"
            print(f"    {name}{extra}  --  {styled(str(value) + ' gold', C.YELLOW)}")
        print()
        print(styled("  Use 'buy {item}' to purchase, 'sell {item}' to sell.", C.DIM))
        print()

    def cmd_buy(self, args):
        if not args:
            print(styled("  Usage: buy {item_name}", C.RED))
            return
        p = self.player
        if p.subloc != "merchant":
            print(styled("  You need to be at a merchant to buy items.", C.RED))
            return

        key = "_".join(args).lower()
        tile = self.current_tile()
        stock = tile.get("merchant_stock", [])

        if key not in stock:
            print(styled(f"  The merchant doesn't have '{' '.join(args)}'.", C.RED))
            return

        info = ALL_ITEMS.get(key, {})
        cost = info.get("value", 0)
        if p.gold < cost:
            print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
            return

        p.gold -= cost
        p.add_item(key)
        stock.remove(key)
        print(styled(f"  Purchased {info['name']} for {cost} gold. (Gold: {p.gold})", C.GREEN))

    def cmd_sell(self, args):
        if not args:
            print(styled("  Usage: sell {item_name}", C.RED))
            return
        p = self.player
        if p.subloc != "merchant":
            print(styled("  You need to be at a merchant to sell items.", C.RED))
            return

        key = "_".join(args).lower()
        if not p.has_item(key):
            print(styled(f"  You don't have '{' '.join(args)}'.", C.RED))
            return

        if key == p.weapon:
            print(styled("  Unequip your weapon first (equip a different one).", C.RED))
            return
        if key == p.armor_equipped:
            print(styled("  Unequip your armor first (equip a different one).", C.RED))
            return

        info = ALL_ITEMS.get(key, {})
        sell_price = max(1, info.get("value", 1) // 2)
        p.remove_item(key)
        p.gold += sell_price
        print(styled(f"  Sold {info.get('name', key)} for {sell_price} gold. (Gold: {p.gold})", C.GREEN))

    # -- combat --

    def cmd_fight(self, _args):
        p = self.player
        tile = self.current_tile()

        # Dragon boss
        if (p.inside == "dragon_lair" or tile["type"] == "dragon_lair") and p.subloc == "nest":
            self._fight_dragon()
            return

        fightable = {"dungeon", "cave", "forest", "castle"}
        loc = p.inside or tile["type"]
        if loc not in fightable:
            print(styled("  There is nothing to fight here.", C.DIM))
            return

        if tile.get("enemies_cleared"):
            print(styled("  This area has been cleared of enemies. (For now...)", C.DIM))
            return

        enemy_template = random.choice(ENEMIES)
        scale = 1 + (p.level - 1) * 0.15
        enemy = {
            "name": enemy_template["name"],
            "hp": int(enemy_template["hp"] * scale),
            "max_hp": int(enemy_template["hp"] * scale),
            "attack": int(enemy_template["attack"] * scale),
            "gold": enemy_template["gold"],
            "xp": int(enemy_template["xp"] * scale),
        }

        print()
        self.print_sep()
        print(styled(f"  A {enemy['name']} emerges from the shadows!", C.RED, C.BOLD))
        print(styled(f"  HP: {enemy['hp']}  ATK: {enemy['attack']}", C.RED))
        self.print_sep()
        print()

        while enemy["hp"] > 0 and p.hp > 0:
            print(styled(f"  Your HP: {p.hp}/{p.max_hp}  |  {enemy['name']} HP: {enemy['hp']}/{enemy['max_hp']}", C.WHITE))
            print(styled("  [a]ttack  [u]se potion  [f]lee", C.CYAN))
            try:
                action = input(styled("  > ", C.BOLD)).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return

            if action in ("a", "attack"):
                dmg = random.randint(p.attack // 2, p.attack)
                enemy["hp"] -= dmg
                print(styled(f"  You strike the {enemy['name']} for {dmg} damage!", C.YELLOW))

                if enemy["hp"] <= 0:
                    break

                raw = random.randint(enemy["attack"] // 2, enemy["attack"])
                taken = p.take_damage(raw)
                print(styled(f"  The {enemy['name']} hits you for {taken} damage!", C.RED))

            elif action in ("u", "use"):
                potions = [(k, CONSUMABLES[k]) for k in p.consumables if k in CONSUMABLES]
                if potions:
                    potions.sort(key=lambda x: x[1]["heal"])
                    key, info = potions[0]
                    old_hp = p.hp
                    p.heal(info["heal"])
                    p.consumables.remove(key)
                    print(styled(f"  Used {info['name']}. Restored {p.hp - old_hp} HP.", C.GREEN))
                else:
                    print(styled("  No potions available!", C.RED))

                raw = random.randint(enemy["attack"] // 2, enemy["attack"])
                taken = p.take_damage(raw)
                print(styled(f"  The {enemy['name']} hits you for {taken} damage!", C.RED))

            elif action in ("f", "flee"):
                if random.random() < 0.5:
                    print(styled("  You flee from battle!", C.YELLOW))
                    print()
                    return
                else:
                    print(styled("  You fail to escape!", C.RED))
                    raw = random.randint(enemy["attack"] // 2, enemy["attack"])
                    taken = p.take_damage(raw)
                    print(styled(f"  The {enemy['name']} hits you for {taken} damage!", C.RED))
            else:
                print(styled("  Invalid action.", C.DIM))

            print()

        if p.hp <= 0:
            print()
            self.print_sep()
            print(styled("  YOU HAVE FALLEN.", C.RED, C.BOLD))
            print(styled("  Darkness takes you...", C.DIM))
            self.print_sep()
            p.hp = p.max_hp // 2
            gold_lost = p.gold // 3
            p.gold -= gold_lost
            p.pos = ("E", 5)
            p.inside = None
            p.subloc = None
            print(styled(f"  You awaken at {self.pos_label()}, weakened. Lost {gold_lost} gold.", C.YELLOW))
            print()
        else:
            gold_gained = random.randint(*enemy["gold"])
            p.gold += gold_gained
            print()
            self.print_sep()
            print(styled(f"  The {enemy['name']} is defeated!", C.GREEN, C.BOLD))
            print(styled(f"  Gained {gold_gained} gold and {enemy['xp']} XP.", C.YELLOW))
            leveled = p.gain_xp(enemy["xp"])
            if leveled:
                print(styled(f"  LEVEL UP! You are now level {p.level}!", C.BOLD, C.CYAN))
                print(styled(f"  Max HP: {p.max_hp}  Base ATK: {p.base_attack}", C.CYAN))
            if random.random() < 0.3:
                loot_pool = list(CONSUMABLES.keys()) + list(MISC_ITEMS.keys())
                if random.random() < 0.15:
                    loot_pool += list(WEAPONS.keys()) + list(ARMORS.keys())
                drop = random.choice(loot_pool)
                info = ALL_ITEMS[drop]
                p.add_item(drop)
                print(styled(f"  Found: {info['name']}!", C.GREEN))
            self.print_sep()
            print()

            if random.random() < 0.4:
                tile["enemies_cleared"] = True

    # -- dragon boss --

    def _fight_dragon(self):
        p = self.player
        if p.dragon_quest == "completed":
            print(styled("  The dragon is already slain. Its bones lie cold.", C.DIM))
            return

        scale = 1 + (p.level - 1) * 0.1
        dragon = {
            "name": "The Ancient Dragon",
            "hp": int(300 * scale),
            "max_hp": int(300 * scale),
            "attack": int(30 * scale),
            "gold": (100, 250),
            "xp": int(500 * scale),
        }

        print()
        self.print_sep()
        print(styled("  THE ANCIENT DRAGON RISES!", C.RED, C.BOLD))
        print(styled("  The ground shakes. Fire erupts from the beast's maw.", C.RED))
        print(styled(f"  HP: {dragon['hp']}  ATK: {dragon['attack']}", C.RED))
        self.print_sep()
        print()

        while dragon["hp"] > 0 and p.hp > 0:
            print(styled(f"  Your HP: {p.hp}/{p.max_hp}  |  {dragon['name']} HP: {dragon['hp']}/{dragon['max_hp']}", C.WHITE))
            print(styled("  [a]ttack  [u]se potion  [f]lee", C.CYAN))
            try:
                action = input(styled("  > ", C.BOLD)).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return

            if action in ("a", "attack"):
                dmg = random.randint(p.attack // 2, p.attack)
                dragon["hp"] -= dmg
                print(styled(f"  You strike {dragon['name']} for {dmg} damage!", C.YELLOW))

                if dragon["hp"] <= 0:
                    break

                # Dragon attack -- 30% chance of inferno breath (double damage)
                if random.random() < 0.3:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"]) * 2
                    taken = p.take_damage(raw)
                    print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
                else:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    print(styled(f"  {dragon['name']} claws you for {taken} damage!", C.RED))

            elif action in ("u", "use"):
                potions = [(k, CONSUMABLES[k]) for k in p.consumables if k in CONSUMABLES]
                if potions:
                    potions.sort(key=lambda x: x[1]["heal"])
                    key, info = potions[0]
                    old_hp = p.hp
                    p.heal(info["heal"])
                    p.consumables.remove(key)
                    print(styled(f"  Used {info['name']}. Restored {p.hp - old_hp} HP.", C.GREEN))
                else:
                    print(styled("  No potions available!", C.RED))

                if random.random() < 0.3:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"]) * 2
                    taken = p.take_damage(raw)
                    print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
                else:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    print(styled(f"  {dragon['name']} claws you for {taken} damage!", C.RED))

            elif action in ("f", "flee"):
                if random.random() < 0.5:
                    print(styled("  You flee from the dragon!", C.YELLOW))
                    print()
                    return
                else:
                    print(styled("  The dragon blocks your escape!", C.RED))
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    print(styled(f"  {dragon['name']} claws you for {taken} damage!", C.RED))
            else:
                print(styled("  Invalid action.", C.DIM))

            print()

        if p.hp <= 0:
            print()
            self.print_sep()
            print(styled("  THE DRAGON HAS SLAIN YOU.", C.RED, C.BOLD))
            print(styled("  Darkness takes you...", C.DIM))
            self.print_sep()
            p.hp = p.max_hp // 2
            gold_lost = p.gold // 3
            p.gold -= gold_lost
            p.pos = ("E", 5)
            p.inside = None
            p.subloc = None
            print(styled(f"  You awaken at {self.pos_label()}, weakened. Lost {gold_lost} gold.", C.YELLOW))
            print()
        else:
            gold_gained = random.randint(*dragon["gold"])
            p.gold += gold_gained
            p.dragon_quest = "completed"
            p.weapons.append("dragon_slayer_blade")
            print()
            self.print_sep()
            print(styled("  THE ANCIENT DRAGON IS SLAIN!", C.GREEN, C.BOLD))
            print(styled(f"  Gained {gold_gained} gold and {dragon['xp']} XP.", C.YELLOW))
            print(styled("  You claim the Dragon Slayer Blade from the hoard!", C.BOLD, C.CYAN))
            leveled = p.gain_xp(dragon["xp"])
            if leveled:
                print(styled(f"  LEVEL UP! You are now level {p.level}!", C.BOLD, C.CYAN))
                print(styled(f"  Max HP: {p.max_hp}  Base ATK: {p.base_attack}", C.CYAN))
            self.print_sep()
            print()

    # -- search / loot --

    def cmd_search(self, _args):
        p = self.player
        tile = self.current_tile()

        if not p.inside:
            print(styled("  Nothing to search here in the open.", C.DIM))
            return

        if not tile.get("loot_available"):
            print(styled("  You've already searched this place thoroughly. Nothing remains.", C.DIM))
            return

        searchable = {"treasure_room", "crypt", "altar", "ruins", "clearing",
                      "throne_room", "great_hall", "tower", "dungeon_cells", "hoard"}
        if p.subloc and p.subloc in searchable:
            found_gold = random.randint(5, 30 + p.level * 5)
            p.gold += found_gold
            print(styled(f"  You search carefully... Found {found_gold} gold!", C.YELLOW))

            if random.random() < 0.5:
                loot_pool = list(CONSUMABLES.keys()) + list(MISC_ITEMS.keys())
                if random.random() < 0.2:
                    loot_pool += list(WEAPONS.keys()) + list(ARMORS.keys())
                item_key = random.choice(loot_pool)
                info = ALL_ITEMS[item_key]
                p.add_item(item_key)
                print(styled(f"  Found: {info['name']}!", C.GREEN))

            tile["loot_available"] = False
        else:
            print(styled("  You look around but find nothing of interest here.", C.DIM))

    def cmd_quit(self, _args):
        print()
        print(styled("  The darkness closes in. Your journey ends here.", C.DIM))
        print(styled("  Farewell, wanderer.", C.BOLD))
        print()
        self.running = False

    # -- command dispatch --

    def dispatch(self, raw_input):
        parts = raw_input.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        commands = {
            "help":      self.cmd_help,
            "map":       self.cmd_map,
            "look":      self.cmd_look,
            "talk":      self.cmd_talk,
            "stats":     self.cmd_stats,
            "inventory": self.cmd_inventory,
            "inv":       self.cmd_inventory,
            "cd":        self.cmd_cd,
            "equip":     self.cmd_equip,
            "use":       self.cmd_use,
            "buy":       self.cmd_buy,
            "sell":      self.cmd_sell,
            "fight":     self.cmd_fight,
            "search":    self.cmd_search,
            "quit":      self.cmd_quit,
            "exit":      self.cmd_quit,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
        else:
            print(styled(f"  Unknown command: {cmd}. Type 'help' for commands.", C.RED))

    # -- main loop --

    def run(self):
        set_gothic_font()
        show_intro()
        print("\033[2J\033[H", end="", flush=True)

        print()
        print(styled(r"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  _   _    _    ___
  |_   _| || | __|  | __|/ _ \| _ \ __/ __|_   _|  | __|| | | |  | |  / __|
    | | | __ | _|   | _|| (_) |   / _|\__ \ | |    | _| | |_| |_ | |__\__ \
    |_| |_||_|___|  |_|  \___/|_|_\___|___/ |_|    |_|   \___/\__||____|___/
        """, C.BOLD, C.RED))

        print(styled("    A Dark Medieval Gothic Exploration", C.DIM))
        print()
        print(styled("    You awaken in a grey, desolate land. Fog clings to the earth.", C.WHITE))
        print(styled("    The sky is iron. Somewhere, a bell tolls.", C.WHITE))
        print(styled("    Type 'help' for commands. Type 'map' to see the world.", C.DIM))
        print()
        self.print_sep()
        print()

        while self.running:
            loc = self.location_label()
            prompt = styled(f"  [{loc}]", C.CYAN) + styled(" > ", C.BOLD)
            try:
                raw = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                self.cmd_quit([])
                break

            self.dispatch(raw)

            if self.player.hp <= 0:
                self.player.hp = self.player.max_hp // 2
                gold_lost = self.player.gold // 3
                self.player.gold -= gold_lost
                self.player.pos = ("E", 5)
                self.player.inside = None
                self.player.subloc = None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
