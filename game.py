#!/usr/bin/env python3
"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  ___   ___  _     ___
  |_   _| || | __|  | __|/ _ \\| _ \\ __/ __|_   _|  | __|/ _ \\ / _ \\| |   / __|
    | | | __ | _|   | _|| (_) |   / _|\\__ \\ | |    | _|| (_) | (_) | |__ \\__ \\
    |_| |_||_|___|  |_|  \\___/|_|_\\___|___/ |_|    |_|  \\___/ \\___/|____|___/

A dark medieval gothic exploration game for the terminal.
"""

import random
import sys
import os
import textwrap
import time
from collections import Counter

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
    # Backgrounds
    BG_BLUE    = "\033[44m"
    BG_YELLOW  = "\033[43m"
    BG_GREEN   = "\033[42m"
    BG_DGREEN  = "\033[48;5;22m"

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
    "port":       "P",
    "water":      "~",
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
    "port":       C.BOLD + C.WHITE,
    "water":      C.BOLD + C.BLUE,
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
    "port":       "Port",
    "water":      "Water",
}

BG_COLORS = {
    "water":      C.BG_BLUE,
    "sand":       C.BG_YELLOW,
    "grass":      C.BG_GREEN,
    "dark_grass": C.BG_DGREEN,
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
    "cloth_rags":     {"name": "Cloth Rags",       "armor": 1,  "dodge": 5,  "value": 3},
    "leather_vest":   {"name": "Leather Vest",     "armor": 4,  "dodge": 10, "value": 15},
    "chainmail":      {"name": "Chainmail",        "armor": 8,  "dodge": 3,  "value": 45},
    "plate_armor":    {"name": "Plate Armor",      "armor": 14, "dodge": 2,  "value": 100},
    "dark_plate":     {"name": "Dark Plate",       "armor": 20, "dodge": 5,  "value": 250},
    "shadow_cloak":   {"name": "Shadow Cloak",     "armor": 10, "dodge": 20, "value": 80},
}

CONSUMABLES = {
    "small_potion":   {"name": "Small Potion",   "heal": 25, "value": 8},
    "medium_potion":  {"name": "Medium Potion",  "heal": 50, "value": 20},
    "large_potion":   {"name": "Large Potion",   "heal": 100, "value": 45},
    "elixir":         {"name": "Elixir",         "heal": 200, "value": 100},
}

MISC_ITEMS = {
    "old_key":        {"name": "Old Key",        "value": 20},
    "skull_amulet":   {"name": "Skull Amulet",   "value": 30},
    "raven_feather":  {"name": "Raven Feather",  "value": 10},
    "golden_chalice": {"name": "Golden Chalice", "value": 75},
    "torn_scroll":    {"name": "Torn Scroll",    "value": 50},
    "dark_gem":       {"name": "Dark Gem",       "value": 60},
    "iron_ring":      {"name": "Iron Ring",      "value": 10},
}

SPELLS = {
    # Mage spells (courtyard)
    "fireball":      {"name": "Fireball",      "damage": 30, "mana": 20, "value": 50,  "source": "mage"},
    "ice_shard":     {"name": "Ice Shard",     "damage": 20, "mana": 15, "value": 35,  "source": "mage"},
    "heal_light":    {"name": "Heal Light",    "heal": 40,   "mana": 25, "value": 60,  "source": "mage"},
    "arcane_shield": {"name": "Arcane Shield", "shield": 10, "mana": 20, "value": 45,  "source": "mage"},
    # Warlock spells (castle tower)
    "shadow_bolt":   {"name": "Shadow Bolt",   "damage": 40, "mana": 25, "value": 80,  "source": "warlock"},
    "drain_life":    {"name": "Drain Life",    "damage": 25, "heal": 25, "mana": 30, "value": 100, "source": "warlock"},
    "curse":         {"name": "Curse",         "weaken": 0.3, "mana": 20, "value": 70, "source": "warlock"},
}

MAP_COST = 200
TRAIN_COST = 150  # gold to increase max spell slots by 1 (near mage)
MAX_SPELLS_LIMIT = 6  # absolute ceiling

ALL_ITEMS = {}
ALL_ITEMS.update(WEAPONS)
ALL_ITEMS.update(ARMORS)
ALL_ITEMS.update(CONSUMABLES)
ALL_ITEMS.update(MISC_ITEMS)

# ---------------------------------------------------------------------------
# Data: Enemies (per zone, scaling difficulty)
# ---------------------------------------------------------------------------

# Zone tiers: forest (easy) -> cave (medium) -> castle (hard) -> dungeon (very hard)
ZONE_ENEMIES = {
    "forest": [
        {"name": "Giant Rat",         "hp": 15,  "attack": 3,  "gold": (2, 6),   "xp": 6},
        {"name": "Wild Crow",         "hp": 12,  "attack": 2,  "gold": (1, 4),   "xp": 4},
        {"name": "Plague Rat Swarm",  "hp": 20,  "attack": 4,  "gold": (2, 8),   "xp": 8},
        {"name": "Feral Boar",        "hp": 25,  "attack": 5,  "gold": (3, 8),   "xp": 10},
        {"name": "Giant Spider",      "hp": 22,  "attack": 4,  "gold": (2, 7),   "xp": 7},
        {"name": "Goblin Scavenger",  "hp": 18,  "attack": 3,  "gold": (2, 6),   "xp": 6},
        {"name": "Venomous Snake",    "hp": 14,  "attack": 5,  "gold": (2, 5),   "xp": 5},
    ],
    "cave": [
        {"name": "Cave Wolf",         "hp": 35,  "attack": 7,  "gold": (5, 15),  "xp": 15},
        {"name": "Brown Bear",        "hp": 50,  "attack": 9,  "gold": (8, 20),  "xp": 20},
        {"name": "Cave Bat Swarm",    "hp": 25,  "attack": 6,  "gold": (4, 12),  "xp": 12},
        {"name": "Rock Troll",        "hp": 60,  "attack": 10, "gold": (10, 25), "xp": 22},
        {"name": "Shadow Stalker",    "hp": 40,  "attack": 8,  "gold": (6, 18),  "xp": 18},
        {"name": "Undead Miner",      "hp": 30,  "attack": 7,  "gold": (5, 15),  "xp": 14},
    ],
    "castle": [
        {"name": "Living Armor",      "hp": 60,  "attack": 12, "gold": (12, 30), "xp": 30},
        {"name": "Haunted Knight",    "hp": 70,  "attack": 14, "gold": (15, 35), "xp": 35},
        {"name": "Hollow Wraith",     "hp": 50,  "attack": 11, "gold": (10, 28), "xp": 28},
        {"name": "Cursed Sentinel",   "hp": 65,  "attack": 13, "gold": (12, 32), "xp": 32},
        {"name": "Spectral Guard",    "hp": 55,  "attack": 12, "gold": (10, 28), "xp": 28},
        {"name": "Gargoyle",          "hp": 75,  "attack": 15, "gold": (15, 40), "xp": 38},
    ],
    "dungeon": [
        {"name": "Cursed Knight",     "hp": 80,  "attack": 16, "gold": (18, 45), "xp": 45},
        {"name": "Tomb Guardian",     "hp": 90,  "attack": 18, "gold": (20, 50), "xp": 50},
        {"name": "Dark Sorcerer",     "hp": 70,  "attack": 20, "gold": (25, 60), "xp": 55},
        {"name": "Bone Colossus",     "hp": 120, "attack": 22, "gold": (30, 70), "xp": 65},
        {"name": "Undead Priest",     "hp": 65,  "attack": 17, "gold": (18, 45), "xp": 45},
        {"name": "Abyssal Demon",     "hp": 100, "attack": 24, "gold": (30, 80), "xp": 70},
    ],
}

# Fallback for any zone not explicitly listed
ENEMIES_FALLBACK = ZONE_ENEMIES["forest"]

# Zone level requirements (player must be at least this level for NPCs to hint about the zone)
ZONE_LEVEL_REQUIREMENTS = {
    "forest": 1,
    "cave": 3,
    "castle": 6,
    "dungeon": 9,
    "dragon_lair": 5,  # king quest requires level 5
}

# Order in which zones are unlocked for NPC hints
ZONE_TIERS = ["forest", "cave", "castle", "dungeon"]

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

DESC_PORT = [
    "A weathered harbour of salt-stained stone. Fishing boats bob at their moorings. The air is thick with the smell of brine and tar. Gulls circle overhead, their cries harsh above the crash of waves.",
    "A small port clings to the coastline. Wooden piers stretch into dark waters. Nets hang drying between lampposts. The wind carries salt and the distant toll of a bell buoy.",
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
        "Behind a reinforced iron door, a vault of ancient riches awaits. One large chest, bound in black iron and carved with runes, sits at the centre — locked tight.",
    ],
    # Castle sub-locations
    "courtyard": [
        "A wide courtyard choked with fog. Broken statues and overturned carts litter the ground. The keep looms ahead, dark and silent.",
    ],
    "mage": [
        "A robed mage stands within a circle of glowing arcane runes. Ancient tomes and spell components surround them. Their eyes burn with otherworldly knowledge.",
    ],
    "warlock": [
        "A dark figure in tattered robes hunches over a grimoire bound in black leather. Shadows writhe around them. The warlock looks up with hollow, burning eyes.",
    ],
    "explorer": [
        "A weathered explorer sits at a table covered in maps and nautical charts. Their sun-darkened skin and salt-stained clothes speak of countless voyages.",
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
    "dock": [
        "A sturdy pier of weathered planks extends over grey waters. An old chalutier rocks gently at its mooring, its nets bundled on deck. An explorer studies their maps nearby.",
        "The dock creaks underfoot. A fishing trawler -- a chalutier -- is tied to the bollard, its hull scarred by countless voyages. An explorer with charts and maps sits on a barrel.",
    ],
}

# ---------------------------------------------------------------------------
# Data: Location sub-location definitions
# ---------------------------------------------------------------------------

SUBLOCS = {
    "village": ["merchant", "blacksmith", "tavern", "chapel", "square"],
    "cave":    ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "dungeon": ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "castle":  ["courtyard", "great_hall", "tower", "dungeon_cells", "throne_room", "treasure_room"],
    "forest":  ["clearing", "ruins", "stream"],
    "capital": ["courtyard", "great_hall", "throne_room", "barracks", "merchant", "tavern"],
    "dragon_lair": ["entrance", "tunnel", "hoard", "nest"],
    "port":    ["dock", "tavern", "merchant"],
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
    "dock": {
        "old_sailor": [
            '"The sea\'s been angry lately." The old sailor spits into the water. "Used to take the chalutier out beyond the reef. Can\'t now." He squints at the horizon. "Heard there\'s trouble at the {loc_type} near {coord}."',
            '"That chalutier there? She\'s mine. Seaworthy, aye. But I won\'t sail until things calm down. Heard tales of a {loc_type} at {coord}. Dark tales."',
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
    for dc in range(-1, 2):
        for dr in range(-1, 2):
            ci = COLS.index("E") + dc
            ri = 4 + dr
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
    capital_pos = ("E", 5)

    sand_positions = {pos for pos, t in terrain.items() if t == "sand"}
    grass_available = [pos for pos in terrain
                       if terrain[pos] in ("grass", "dark_grass") and pos != capital_pos]

    # Place ports on sand
    sand_available = [pos for pos in sand_positions if pos != capital_pos]
    port_positions = random.sample(sand_available, min(2, len(sand_available))) if sand_available else []

    # Place other specials on grass/dark_grass
    special = []
    counts = [("forest", 3), ("village", 3), ("cave", 2), ("castle", 2),
              ("dungeon", 2), ("dragon_lair", 1)]
    total_needed = sum(n for _, n in counts)
    chosen = random.sample(grass_available, min(total_needed, len(grass_available)))
    idx = 0
    for tile_type, count in counts:
        for _ in range(count):
            if idx < len(chosen):
                special.append((chosen[idx], tile_type))
                idx += 1

    special_map = {pos: t for pos, t in special}
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


# ---------------------------------------------------------------------------
# Helper: find interesting locations on the map
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.mana = 50
        self.max_mana = 50
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
        self.spells = []  # learned spells
        self.max_spells = 3  # can be increased via train

        # Map
        self.has_map = False

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

    @property
    def dodge_chance(self):
        a = ARMORS.get(self.armor_equipped, {})
        return a.get("dodge", 0)

    def weapon_name(self):
        w = WEAPONS.get(self.weapon)
        return w["name"] if w else "Bare Fists"

    def armor_name(self):
        a = ARMORS.get(self.armor_equipped)
        return a["name"] if a else "None"

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, raw_dmg):
        # Dodge check
        if random.randint(1, 100) <= self.dodge_chance:
            return 0  # dodged
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
            self.max_mana += 10
            self.mana = self.max_mana
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
        self.action_count = 0
        self.respawn_interval = 15  # enemies respawn every 15 actions
        self.npc_pois: dict = {}  # per-NPC assigned POIs: {subloc:npc_name -> [(pos, coord, loc_type), ...]}

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
        """Pick a random point of interest to mention in NPC dialogue, filtered by level."""
        pois = [(pos, t) for pos, t in find_poi(self.world, exclude_pos=self.player.pos) if t != "dragon_lair"]
        if not pois:
            return None, None, None
        # Filter to zones the player has access to based on level
        accessible = [(pos, t) for pos, t in pois
                      if self.player.level >= ZONE_LEVEL_REQUIREMENTS.get(t, 1)]
        if not accessible:
            return None, None, None
        pos, loc_type = random.choice(accessible)
        return pos, coord_label(pos), loc_type

    def _get_highest_unlocked_zone(self):
        """Return the highest zone tier the player has unlocked."""
        for zone in reversed(ZONE_TIERS):
            if self.player.level >= ZONE_LEVEL_REQUIREMENTS[zone]:
                return zone
        return "forest"

    def _get_next_locked_zone(self):
        """Return the next zone tier the player hasn't unlocked yet, or None."""
        for zone in ZONE_TIERS:
            if self.player.level < ZONE_LEVEL_REQUIREMENTS[zone]:
                return zone
        return None

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
            ("unequip weapon|armor", "Unequip weapon or armor."),
            ("use {item}",       "Use a consumable item."),
            ("buy {item}",       "Buy from merchant / mage / warlock / explorer."),
            ("sell {item}",      "Sell to a merchant (when at merchant)."),
            ("cast {spell}",     "Cast a spell (in combat)."),
            ("fight",            "Fight enemies (in dungeons/caves/forests)."),
            ("search",           "Search for loot (in special locations)."),
            ("sleep",            "Rest at a tavern (heals HP & mana, 10 gold)."),
            ("train",            "Train with the mage to gain a spell slot (150 gold)."),
            ("cheat",            "Beta testing: get all items, map, lvl 20."),
            ("quit / exit",      "Quit the game."),
            ("", ""),
            ("SHORTCUTS",        "h=help m=map l=look t=talk s=search"),
            ("",                 "f=fight i=inventory e=equip u=use b=buy q=quit"),
            ("", ""),
            ("TIP",              "Type partial item names (e.g. 'sell sm' for Small Potion)."),
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
            if self.player.subloc == "tavern":
                print(styled("  A room is available. Type 'sleep' to rest (10 gold).", C.YELLOW))
            # Mage in courtyard
            if self.player.subloc == "courtyard" and self.player.inside in ("castle", "capital"):
                print()
                print(styled("  A mage is here, surrounded by arcane runes.", C.MAGENTA))
                print(styled("  Type 'buy' to see available spells.", C.MAGENTA))
            # Warlock in castle tower
            if self.player.subloc == "tower" and self.player.inside == "castle":
                print()
                print(styled("  A warlock lurks in the shadows of the tower.", C.RED))
                print(styled("  Type 'buy' to see available dark spells.", C.RED))
            # Explorer at dock
            if self.player.subloc == "dock" and self.player.inside == "port":
                print()
                print(styled("  An explorer sits nearby with maps and charts.", C.CYAN))
                if not self.player.has_map:
                    print(styled(f"  Type 'buy map' to buy a full map ({MAP_COST} gold).", C.CYAN))
                else:
                    print(styled("  You already own the full map.", C.DIM))
            # Castle treasure room hint
            if self.player.subloc == "treasure_room" and self.player.inside == "castle":
                print()
                if self.world[self.player.pos].get("castle_treasure_opened"):
                    print(styled("  The chest lies open and empty.", C.DIM))
                elif "old_key" in self.player.misc:
                    print(styled("  A locked chest sits here. You have an Old Key! Type 'search' to open it.", C.YELLOW, C.BOLD))
                else:
                    print(styled("  A locked chest sits here. You need an Old Key to open it.", C.YELLOW))
        elif self.player.inside:
            desc_map = {
                "plains": DESC_PLAINS, "forest": DESC_FOREST,
                "village": DESC_VILLAGE, "cave": DESC_CAVE,
                "castle": DESC_CASTLE, "dungeon": DESC_DUNGEON,
                "capital": DESC_CAPITAL, "dragon_lair": DESC_DRAGON_LAIR,
                "port": DESC_PORT,
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
                "port": DESC_PORT,
            }
            descs = desc_map.get(tile["type"], DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            if tile["type"] not in ("plains", "water"):
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

        # Each NPC has assigned POIs filtered by player level (reassigned per level tier)
        npc_key = f"{subloc}:{npc_name}:lvl{self._get_highest_unlocked_zone()}"
        if npc_key not in self.npc_pois:
            all_pois = [(pos, t) for pos, t in find_poi(self.world, exclude_pos=p.pos)
                        if t != "dragon_lair" and p.level >= ZONE_LEVEL_REQUIREMENTS.get(t, 1)]
            chosen = random.sample(all_pois, min(2, len(all_pois)))
            self.npc_pois[npc_key] = [(pos, coord_label(pos), loc_type) for pos, loc_type in chosen]

        npc_poi_list = self.npc_pois[npc_key]
        if npc_poi_list:
            poi_pos, coord, loc_type = random.choice(npc_poi_list)
            line = template.format(
                coord=styled(coord, C.BOLD, C.CYAN),
                loc_type=styled(loc_type, C.BOLD, C.YELLOW),
            )
        else:
            poi_pos, coord, loc_type = None, None, None
            line = template.format(coord="the far reaches", loc_type="dark place")

        npc_display = npc_name.replace("_", " ").title()
        print()
        self.print_sep()
        print(styled(f"  [{npc_display}]", C.BOLD, C.YELLOW))
        print()
        self.wrap_print(line, C.WHITE)
        if poi_pos and not self.world[poi_pos].get("revealed"):
            self.world[poi_pos]["revealed"] = True
            print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))
        elif poi_pos:
            print(styled("  [This location is already on your map.]", C.DIM))

        # Check if there are higher-tier zones the player can't access yet
        next_zone = self._get_next_locked_zone()
        if next_zone:
            req_lvl = ZONE_LEVEL_REQUIREMENTS[next_zone]
            print()
            npc_display_lower = npc_display.lower()
            self.wrap_print(
                f"\"I know of darker places... but you haven't the stature for them. "
                f"Come back when you're stronger. (Reach level {req_lvl} to unlock {next_zone} hints)\"",
                C.DIM
            )
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
        mana_pct = p.mana / p.max_mana if p.max_mana > 0 else 0
        mana_filled = int(bar_len * mana_pct)
        mana_bar = styled("#" * mana_filled, C.BLUE) + styled("-" * (bar_len - mana_filled), C.DIM)
        print(f"  HP:      {p.hp}/{p.max_hp} [{bar}]")
        print(f"  Mana:    {p.mana}/{p.max_mana} [{mana_bar}]")
        print(f"  Attack:  {styled(str(p.attack), C.RED)}")
        print(f"  Defense: {styled(str(p.armor_value), C.BLUE)}")
        print(f"  Dodge:   {styled(str(p.dodge_chance) + '%', C.GREEN)}")
        print(f"  Gold:    {styled(str(p.gold), C.YELLOW)}")
        print(f"  Level:   {p.level}  (XP: {p.xp}/{p.xp_to_next})")
        print(f"  Weapon:  {styled(p.weapon_name(), C.CYAN)}")
        print(f"  Armor:   {styled(p.armor_name(), C.CYAN)}")
        if p.spells:
            spell_names = ", ".join(SPELLS[s]["name"] for s in p.spells if s in SPELLS)
            print(f"  Spells:  {styled(spell_names, C.MAGENTA)}")
        if p.has_map:
            print(f"  Map:     {styled('Full map unlocked', C.GREEN)}")
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
                # Group items by key and count duplicates
                counts = Counter(items)
                for key, count in counts.items():
                    info = catalog.get(key, {})
                    name = info.get("name", key)
                    extra = ""
                    if "attack" in info:
                        extra = f" (ATK +{info['attack']})"
                    elif "armor" in info:
                        extra = f" (DEF +{info['armor']}, Dodge {info.get('dodge', 0)}%)"
                    elif "heal" in info:
                        extra = f" (Heal {info['heal']})"
                    equipped = ""
                    if key == p.weapon:
                        equipped = styled(" [equipped]", C.GREEN)
                    elif key == p.armor_equipped:
                        equipped = styled(" [equipped]", C.GREEN)
                    qty = f" x{count}" if count > 1 else ""
                    print(f"    {name}{extra}{styled(qty, C.YELLOW)}{equipped}")

        _list_section("Weapons", p.weapons, WEAPONS)
        _list_section("Armor", p.armors, ARMORS)
        _list_section("Consumables", p.consumables, CONSUMABLES)
        _list_section("Misc", p.misc, MISC_ITEMS)

        if p.spells:
            print(f"\n  {styled('Spells', C.BOLD)}")
            for spell_key in p.spells:
                info = SPELLS.get(spell_key, {})
                name = info.get("name", spell_key)
                mana_cost = info.get("mana", 0)
                details = []
                if "damage" in info:
                    details.append(f"DMG {info['damage']}")
                if "heal" in info:
                    details.append(f"Heal {info['heal']}")
                if "shield" in info:
                    details.append(f"Shield +{info['shield']}")
                if "weaken" in info:
                    details.append(f"Weaken {int(info['weaken']*100)}%")
                detail_str = ", ".join(details)
                print(f"    {name} ({detail_str}, {mana_cost} mana)")
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

        # If inside a location, try sub-location navigation (with prefix matching)
        if p.inside:
            subs = SUBLOCS.get(p.inside, [])
            resolved = target if target in subs else None
            if resolved is None:
                matches = [s for s in subs if s.startswith(target)]
                if len(matches) == 1:
                    resolved = matches[0]
                elif len(matches) > 1:
                    print(styled(f"  Ambiguous — did you mean: {', '.join(matches)}?", C.RED))
                    return
            if resolved:
                p.subloc = resolved
                self.cmd_look([])
                if resolved == "merchant" and self.current_tile()["type"] in ("village", "capital", "port"):
                    self._show_merchant()
                return
            if target == p.inside or p.inside.startswith(target):
                p.subloc = None
                self.cmd_look([])
                return

        # Try location entry: cd village, cd cave, etc. (with prefix matching)
        tile = self.current_tile()
        if not p.inside and tile["type"] not in ("plains", "water"):
            loc_type = tile["type"]
            if loc_type.startswith(target):
                p.inside = loc_type
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
                target_tile = self.world[(col, row)]
                if target_tile["type"] == "water":
                    print(styled("  You cannot travel across water.", C.BLUE))
                    return
                p.pos = (col, row)
                new_tile = self.current_tile()
                new_tile["visited"] = True
                t = new_tile["type"]
                if t not in ("plains", "water"):
                    # Auto-enter the location
                    p.inside = t
                    p.subloc = None
                    print()
                    print(styled(f"  You travel to {self.pos_label()} — {t.replace('_', ' ').title()}.", C.YELLOW))
                    self.cmd_look([])
                else:
                    p.inside = None
                    p.subloc = None
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
                "port": DESC_PORT,
            }
            descs = desc_map.get(t, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            print(styled(f"\n  There is a {t} here. Use 'cd {t}' to enter.", C.YELLOW))
        print()

    def cmd_equip(self, args):
        if not args:
            print(styled("  Usage: equip {item_name}", C.RED))
            return

        p = self.player
        # Try resolving with prefix matching
        key = self._resolve_item_key(args, list(set(p.weapons + p.armors)))
        if key is None:
            key = "_".join(args).lower()

        if key in WEAPONS and key in p.weapons:
            p.weapon = key
            print(styled(f"  Equipped {WEAPONS[key]['name']}.", C.GREEN))
        elif key in ARMORS and key in p.armors:
            p.armor_equipped = key
            print(styled(f"  Equipped {ARMORS[key]['name']}.", C.GREEN))
        else:
            print(styled(f"  You don't have '{' '.join(args)}' or it cannot be equipped.", C.RED))

    def cmd_unequip(self, args):
        if not args:
            print(styled("  Usage: unequip weapon | unequip armor", C.RED))
            return

        target = args[0].lower()
        p = self.player

        if target in ("weapon", "w"):
            if p.weapon is None:
                print(styled("  You have no weapon equipped.", C.DIM))
            else:
                old = p.weapon_name()
                p.weapon = None
                print(styled(f"  Unequipped {old}. Fighting with bare fists.", C.YELLOW))
        elif target in ("armor", "a"):
            if p.armor_equipped is None:
                print(styled("  You have no armor equipped.", C.DIM))
            else:
                old = p.armor_name()
                p.armor_equipped = None
                print(styled(f"  Unequipped {old}. No armor.", C.YELLOW))
        else:
            print(styled("  Usage: unequip weapon | unequip armor", C.RED))

    def cmd_use(self, args):
        if not args:
            print(styled("  Usage: use {item_name}", C.RED))
            return

        p = self.player
        key = self._resolve_item_key(args, p.consumables)
        if key is None:
            key = "_".join(args).lower()

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
                extra = f" (DEF +{info['armor']}, Dodge {info.get('dodge', 0)}%)"
            elif "heal" in info:
                extra = f" (Heal {info['heal']})"
            print(f"    {name}{extra}  --  {styled(str(value) + ' gold', C.YELLOW)}")
        print()
        print(styled("  Use 'buy {item}' to purchase, 'sell {item}' to sell.", C.DIM))
        print()

    def _show_mage_spells(self):
        """Show spells available from the mage."""
        p = self.player
        available = {k: v for k, v in SPELLS.items() if v["source"] == "mage" and k not in p.spells}
        if not available:
            print(styled("  The mage has nothing more to teach you.", C.DIM))
            return
        print()
        print(styled("  MAGE'S SPELLS", C.BOLD, C.MAGENTA))
        print(styled("  -------------", C.DIM))
        for key, info in available.items():
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage']}")
            if "heal" in info:
                details.append(f"Heal {info['heal']}")
            if "shield" in info:
                details.append(f"Shield +{info['shield']}")
            detail_str = ", ".join(details)
            print(f"    {info['name']} ({detail_str}, {info['mana']} mana)  --  {styled(str(info['value']) + ' gold', C.YELLOW)}")
        print(f"\n  Spells known: {len(p.spells)}/{p.max_spells}")
        print(styled("  Use 'buy {spell}' to learn a spell.", C.DIM))
        print(styled(f"  Use 'train' to increase your spell capacity ({TRAIN_COST} gold).", C.DIM))
        print()

    def _show_warlock_spells(self):
        """Show spells available from the warlock."""
        p = self.player
        available = {k: v for k, v in SPELLS.items() if v["source"] == "warlock" and k not in p.spells}
        if not available:
            print(styled("  The warlock has nothing more to teach you.", C.DIM))
            return
        print()
        print(styled("  WARLOCK'S DARK SPELLS", C.BOLD, C.RED))
        print(styled("  --------------------", C.DIM))
        for key, info in available.items():
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage']}")
            if "heal" in info:
                details.append(f"Heal {info['heal']}")
            if "weaken" in info:
                details.append(f"Weaken {int(info['weaken']*100)}%")
            detail_str = ", ".join(details)
            print(f"    {info['name']} ({detail_str}, {info['mana']} mana)  --  {styled(str(info['value']) + ' gold', C.YELLOW)}")
        print(f"\n  Spells known: {len(p.spells)}/{p.max_spells}")
        print(styled("  Use 'buy {spell}' to learn a dark spell.", C.DIM))
        print()

    def cmd_buy(self, args):
        p = self.player

        # No args: show relevant shop if at a special location
        if not args:
            if p.subloc == "courtyard" and p.inside in ("castle", "capital"):
                self._show_mage_spells()
                return
            elif p.subloc == "tower" and p.inside == "castle":
                self._show_warlock_spells()
                return
            elif p.subloc == "dock" and p.inside == "port":
                if p.has_map:
                    print(styled("  You already own the full map.", C.DIM))
                else:
                    print(styled(f"  The explorer sells a full map for {MAP_COST} gold. Type 'buy map'.", C.CYAN))
                return
            elif p.subloc == "merchant":
                self._show_merchant()
                return
            print(styled("  Usage: buy {item_name}", C.RED))
            return

        # Buy map from explorer at dock
        if p.subloc == "dock" and p.inside == "port":
            target = "_".join(args).lower()
            if target == "map":
                if p.has_map:
                    print(styled("  You already own the full map.", C.DIM))
                    return
                if p.gold < MAP_COST:
                    print(styled(f"  Not enough gold. The map costs {MAP_COST}, you have {p.gold}.", C.RED))
                    return
                p.gold -= MAP_COST
                p.has_map = True
                for pos, tile in self.world.items():
                    if tile["type"] not in ("plains", "water"):
                        tile["revealed"] = True
                print(styled(f"  Purchased the full map for {MAP_COST} gold! All locations revealed!", C.GREEN, C.BOLD))
                return
            else:
                print(styled("  The explorer only sells maps. Type 'buy map'.", C.RED))
                return

        # Buy spells from mage in courtyard
        if p.subloc == "courtyard" and p.inside in ("castle", "capital"):
            spell_keys = [k for k, v in SPELLS.items() if v["source"] == "mage" and k not in p.spells]
            key = self._resolve_item_key(args, spell_keys)
            if key is None:
                key = "_".join(args).lower()
            if key not in SPELLS or SPELLS[key]["source"] != "mage":
                self._show_mage_spells()
                return
            if key in p.spells:
                print(styled(f"  You already know {SPELLS[key]['name']}.", C.DIM))
                return
            if len(p.spells) >= p.max_spells:
                print(styled(f"  You cannot learn more than {p.max_spells} spells. Use 'train' to expand your capacity.", C.RED))
                return
            cost = SPELLS[key]["value"]
            if p.gold < cost:
                print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
                return
            p.gold -= cost
            p.spells.append(key)
            print(styled(f"  Learned {SPELLS[key]['name']}! ({len(p.spells)}/{p.max_spells} spells) (Gold: {p.gold})", C.MAGENTA, C.BOLD))
            return

        # Buy spells from warlock in castle tower
        if p.subloc == "tower" and p.inside == "castle":
            spell_keys = [k for k, v in SPELLS.items() if v["source"] == "warlock" and k not in p.spells]
            key = self._resolve_item_key(args, spell_keys)
            if key is None:
                key = "_".join(args).lower()
            if key not in SPELLS or SPELLS[key]["source"] != "warlock":
                self._show_warlock_spells()
                return
            if key in p.spells:
                print(styled(f"  You already know {SPELLS[key]['name']}.", C.DIM))
                return
            if len(p.spells) >= p.max_spells:
                print(styled(f"  You cannot learn more than {p.max_spells} spells. Use 'train' to expand your capacity.", C.RED))
                return
            cost = SPELLS[key]["value"]
            if p.gold < cost:
                print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
                return
            p.gold -= cost
            p.spells.append(key)
            print(styled(f"  Learned {SPELLS[key]['name']}! ({len(p.spells)}/{p.max_spells} spells) (Gold: {p.gold})", C.RED, C.BOLD))
            return

        # Standard merchant buying
        if p.subloc != "merchant":
            print(styled("  You need to be at a merchant, mage, warlock, or explorer.", C.RED))
            return

        tile = self.current_tile()
        stock = tile.get("merchant_stock", [])
        key = self._resolve_item_key(args, stock)
        if key is None:
            key = "_".join(args).lower()

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

        all_player_items = p.weapons + p.armors + p.consumables + p.misc
        key = self._resolve_item_key(args, all_player_items)
        if key is None:
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

    def cmd_train(self, _args):
        """Train with the mage to increase max spell capacity."""
        p = self.player
        if not (p.subloc == "courtyard" and p.inside in ("castle", "capital")):
            print(styled("  You must be at the mage's courtyard to train.", C.RED))
            return
        if p.max_spells >= MAX_SPELLS_LIMIT:
            print(styled(f"  You have reached the maximum spell capacity ({MAX_SPELLS_LIMIT}).", C.DIM))
            return
        if p.gold < TRAIN_COST:
            print(styled(f"  Not enough gold. Training costs {TRAIN_COST} gold, you have {p.gold}.", C.RED))
            return
        p.gold -= TRAIN_COST
        p.max_spells += 1
        print(styled(f"  The mage guides you through rigorous arcane exercises...", C.MAGENTA))
        print(styled(f"  Your mind expands. You can now memorise {p.max_spells} spells. (Gold: {p.gold})", C.MAGENTA, C.BOLD))

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

        enemy_pool = ZONE_ENEMIES.get(loc, ENEMIES_FALLBACK)
        enemy_template = random.choice(enemy_pool)
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
            print(styled(f"  Your HP: {p.hp}/{p.max_hp}  Mana: {p.mana}/{p.max_mana}  |  {enemy['name']} HP: {enemy['hp']}/{enemy['max_hp']}", C.WHITE))
            spell_hint = "  [c]ast spell" if p.spells else ""
            print(styled(f"  [a]ttack  [u]se potion  [f]lee{spell_hint}", C.CYAN))
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
                if taken == 0:
                    print(styled(f"  You dodge the {enemy['name']}'s attack!", C.GREEN, C.BOLD))
                else:
                    print(styled(f"  The {enemy['name']} hits you for {taken} damage!", C.RED))

            elif action in ("c", "cast"):
                if not p.spells:
                    print(styled("  You don't know any spells!", C.RED))
                    continue
                self._cast_spell_in_combat(enemy)
                if enemy["hp"] <= 0:
                    break
                # Enemy counter-attacks after casting
                raw = random.randint(enemy["attack"] // 2, enemy["attack"])
                taken = p.take_damage(raw)
                if taken == 0:
                    print(styled(f"  You dodge the {enemy['name']}'s attack!", C.GREEN, C.BOLD))
                else:
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
                if taken == 0:
                    print(styled(f"  You dodge the {enemy['name']}'s attack!", C.GREEN, C.BOLD))
                else:
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
                    if taken == 0:
                        print(styled(f"  You dodge the {enemy['name']}'s attack!", C.GREEN, C.BOLD))
                    else:
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

        dragon = {
            "name": "The Ancient Dragon",
            "hp": 350,
            "max_hp": 350,
            "attack": 40,
            "gold": (100, 250),
            "xp": 500,
        }

        print()
        self.print_sep()
        print(styled("  THE ANCIENT DRAGON RISES!", C.RED, C.BOLD))
        print(styled("  The ground shakes. Fire erupts from the beast's maw.", C.RED))
        print(styled(f"  HP: {dragon['hp']}  ATK: {dragon['attack']}", C.RED))
        self.print_sep()
        print()

        while dragon["hp"] > 0 and p.hp > 0:
            print(styled(f"  Your HP: {p.hp}/{p.max_hp}  Mana: {p.mana}/{p.max_mana}  |  {dragon['name']} HP: {dragon['hp']}/{dragon['max_hp']}", C.WHITE))
            spell_hint = "  [c]ast spell" if p.spells else ""
            print(styled(f"  [a]ttack  [u]se potion  [f]lee{spell_hint}", C.CYAN))
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
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s INFERNO BREATH!", C.GREEN, C.BOLD))
                    else:
                        print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
                else:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s claws!", C.GREEN, C.BOLD))
                    else:
                        print(styled(f"  {dragon['name']} claws you for {taken} damage!", C.RED))

            elif action in ("c", "cast"):
                if not p.spells:
                    print(styled("  You don't know any spells!", C.RED))
                    continue
                self._cast_spell_in_combat(dragon)
                if dragon["hp"] <= 0:
                    break
                if random.random() < 0.3:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"]) * 2
                    taken = p.take_damage(raw)
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s INFERNO BREATH!", C.GREEN, C.BOLD))
                    else:
                        print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
                else:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s claws!", C.GREEN, C.BOLD))
                    else:
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
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s INFERNO BREATH!", C.GREEN, C.BOLD))
                    else:
                        print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
                else:
                    raw = random.randint(dragon["attack"] // 2, dragon["attack"])
                    taken = p.take_damage(raw)
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s claws!", C.GREEN, C.BOLD))
                    else:
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
                    if taken == 0:
                        print(styled(f"  You dodge {dragon['name']}'s claws!", C.GREEN, C.BOLD))
                    else:
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

    def _cast_spell_in_combat(self, enemy):
        """Let the player pick and cast a spell during combat."""
        p = self.player
        print(styled("  Your spells:", C.MAGENTA))
        for i, spell_key in enumerate(p.spells):
            info = SPELLS[spell_key]
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage']}")
            if "heal" in info:
                details.append(f"Heal {info['heal']}")
            if "shield" in info:
                details.append(f"Shield +{info['shield']}")
            if "weaken" in info:
                details.append(f"Weaken {int(info['weaken']*100)}%")
            detail_str = ", ".join(details)
            print(f"    [{i+1}] {info['name']} ({detail_str}, {info['mana']} mana)")
        print(styled("  [0] Cancel", C.DIM))
        try:
            choice = input(styled("  Spell> ", C.BOLD)).strip()
        except (EOFError, KeyboardInterrupt):
            return
        if choice == "0" or not choice:
            print(styled("  Cancelled.", C.DIM))
            return
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(p.spells):
                raise ValueError
        except ValueError:
            print(styled("  Invalid choice.", C.RED))
            return
        spell_key = p.spells[idx]
        info = SPELLS[spell_key]
        mana_cost = info["mana"]
        if p.mana < mana_cost:
            print(styled(f"  Not enough mana! Need {mana_cost}, have {p.mana}.", C.RED))
            return
        p.mana -= mana_cost
        # Apply spell effects
        if "damage" in info:
            dmg = info["damage"]
            enemy["hp"] -= dmg
            print(styled(f"  You cast {info['name']}! {dmg} damage to {enemy['name']}!", C.MAGENTA, C.BOLD))
        if "heal" in info:
            heal_amt = info["heal"]
            old_hp = p.hp
            p.heal(heal_amt)
            print(styled(f"  {info['name']} restores {p.hp - old_hp} HP!", C.GREEN))
        if "shield" in info:
            p.base_armor += info["shield"]
            print(styled(f"  {info['name']} grants +{info['shield']} armor for this battle!", C.BLUE))
        if "weaken" in info:
            reduction = int(enemy["attack"] * info["weaken"])
            enemy["attack"] = max(1, enemy["attack"] - reduction)
            print(styled(f"  {info['name']} weakens {enemy['name']}! ATK reduced by {reduction}!", C.RED))
        print(styled(f"  (Mana: {p.mana}/{p.max_mana})", C.BLUE))

    def cmd_search(self, _args):
        p = self.player
        tile = self.current_tile()

        if not p.inside:
            print(styled("  Nothing to search here in the open.", C.DIM))
            return

        # Castle treasure room: requires Old Key
        if p.subloc == "treasure_room" and p.inside == "castle":
            castle_key = (p.pos, "castle_treasure_opened")
            if self.world[p.pos].get("castle_treasure_opened"):
                print(styled("  The chest lies open and empty. You've already claimed the treasure.", C.DIM))
                return
            if "old_key" not in p.misc:
                print()
                self.print_sep()
                self.wrap_print(
                    "A massive iron-bound chest sits in the centre of the vault. "
                    "Its lock is ancient but sturdy — engraved with worn symbols. "
                    "You need a key to open it.", C.WHITE)
                print(styled("  [You need an Old Key to open this chest.]", C.RED))
                self.print_sep()
                print()
                return
            # Use the Old Key
            p.misc.remove("old_key")
            self.world[p.pos]["castle_treasure_opened"] = True
            print()
            self.print_sep()
            self.wrap_print(
                "You insert the Old Key into the ancient lock. It turns with a "
                "grinding screech. The chest lid creaks open, revealing a trove of riches!", C.WHITE)
            print()
            # Generous loot from the castle chest
            treasure_gold = random.randint(80, 200)
            p.gold += treasure_gold
            print(styled(f"  Found {treasure_gold} gold!", C.YELLOW))
            # Always drop a good weapon or armor
            good_loot = random.choice(["steel_sword", "war_hammer", "dark_blade", "plate_armor", "dark_plate", "silver_longsword"])
            info = ALL_ITEMS[good_loot]
            p.add_item(good_loot)
            print(styled(f"  Found: {info['name']}!", C.GREEN, C.BOLD))
            # Bonus consumables
            bonus = random.choice(list(CONSUMABLES.keys()))
            bonus_info = CONSUMABLES[bonus]
            p.add_item(bonus)
            print(styled(f"  Found: {bonus_info['name']}!", C.GREEN))
            print()
            print(styled("  [The Old Key crumbles to dust after use.]", C.DIM))
            self.print_sep()
            print()
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

    def cmd_sleep(self, _args):
        p = self.player
        if p.subloc != "tavern":
            print(styled("  You need to be in a tavern to sleep.", C.RED))
            return

        cost = 10
        if p.gold < cost:
            print(styled(f"  The barkeep shakes his head. 'Room's {cost} gold. You don't have enough.'", C.RED))
            return

        p.gold -= cost
        old_hp = p.hp
        p.hp = p.max_hp
        healed = p.hp - old_hp
        old_mana = p.mana
        p.mana = p.max_mana
        mana_restored = p.mana - old_mana
        xp_gained = random.randint(3, 8)
        leveled = p.gain_xp(xp_gained)

        # Reset all merchant stocks
        for pos, tile in self.world.items():
            if tile.get("merchant_stock") is not None:
                tile["merchant_stock"] = generate_merchant_stock()

        print()
        self.print_sep()
        print(styled("  You rent a room and collapse onto a straw mattress.", C.WHITE))
        print(styled("  Hours pass. The sounds of the tavern fade into silence.", C.DIM))
        print()
        print(styled(f"  Restored {healed} HP. HP: {p.hp}/{p.max_hp}", C.GREEN))
        print(styled(f"  Restored {mana_restored} Mana. Mana: {p.mana}/{p.max_mana}", C.BLUE))
        print(styled(f"  Gained {xp_gained} XP. (Dreams of past battles...)", C.CYAN))
        print(styled(f"  Paid {cost} gold. (Gold: {p.gold})", C.YELLOW))
        print(styled("  Merchant stocks have been refreshed across the land.", C.DIM))
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {p.level}!", C.BOLD, C.CYAN))
        self.print_sep()
        print()

    def cmd_quit(self, _args):
        print()
        print(styled("  The darkness closes in. Your journey ends here.", C.DIM))
        print(styled("  Farewell, wanderer.", C.BOLD))
        print()
        self.running = False

    def cmd_cheat(self, _args):
        """Beta testing cheat: get everything."""
        p = self.player
        # Level up to 20
        while p.level < 20:
            p.level += 1
            p.max_hp += 10
            p.base_attack += 1
            p.max_mana += 10
        p.hp = p.max_hp
        p.mana = p.max_mana
        p.xp = 0
        p.xp_to_next = int(50 * (1.5 ** 19))
        # Max gold
        p.gold = 99999
        # Full map
        p.has_map = True
        for pos, tile in self.world.items():
            if tile["type"] not in ("plains", "water"):
                tile["revealed"] = True
        # All weapons
        for key in WEAPONS:
            if key not in p.weapons:
                p.weapons.append(key)
        # All armors
        for key in ARMORS:
            if key not in p.armors:
                p.armors.append(key)
        # All consumables (5 of each)
        for key in CONSUMABLES:
            for _ in range(5):
                p.consumables.append(key)
        # All misc items
        for key in MISC_ITEMS:
            if key not in p.misc:
                p.misc.append(key)
        # All spells (up to max_spells, cheat gives all)
        all_spell_keys = list(SPELLS.keys())
        p.max_spells = MAX_SPELLS_LIMIT
        p.spells = all_spell_keys[:MAX_SPELLS_LIMIT]
        # Equip best gear
        p.weapon = "dragon_slayer_blade"
        p.armor_equipped = "dark_plate"
        print()
        self.print_sep()
        print(styled("  [CHEAT MODE ACTIVATED]", C.BOLD, C.RED))
        print(styled(f"  Level: {p.level}  |  HP: {p.hp}/{p.max_hp}  |  Mana: {p.mana}/{p.max_mana}", C.YELLOW))
        print(styled(f"  Gold: {p.gold}  |  ATK: {p.attack}  |  DEF: {p.armor_value}", C.YELLOW))
        print(styled(f"  All weapons, armors, items, and spells unlocked.", C.GREEN))
        print(styled(f"  Full map revealed.", C.GREEN))
        self.print_sep()
        print()

    # -- command dispatch --

    def _resolve_item_key(self, args, catalog_keys):
        """Resolve a partial item name to a full item key via prefix matching."""
        if not args:
            return None
        partial = "_".join(args).lower()
        # Combined lookup for names
        all_lookup = {}
        all_lookup.update(ALL_ITEMS)
        all_lookup.update(SPELLS)
        # Exact match first
        if partial in catalog_keys:
            return partial
        # Prefix match
        matches = [k for k in catalog_keys if k.startswith(partial)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = [all_lookup.get(k, {}).get("name", k) for k in matches]
            print(styled(f"  Multiple matches: {', '.join(names)}", C.YELLOW))
            return None
        # Substring match as fallback
        matches = [k for k in catalog_keys if partial in k]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = [all_lookup.get(k, {}).get("name", k) for k in matches]
            print(styled(f"  Multiple matches: {', '.join(names)}", C.YELLOW))
            return None
        return None

    def _tick_respawn(self):
        """Increment action counter and respawn enemies when threshold is reached."""
        self.action_count += 1
        if self.action_count >= self.respawn_interval:
            self.action_count = 0
            for pos, tile in self.world.items():
                if tile.get("enemies_cleared"):
                    tile["enemies_cleared"] = False
                if not tile.get("loot_available"):
                    tile["loot_available"] = True

    def dispatch(self, raw_input):
        parts = raw_input.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        # Shortcuts
        shortcuts = {
            "h": "help", "m": "map", "l": "look", "t": "talk",
            "s": "search", "f": "fight", "i": "inventory",
            "e": "equip", "u": "use", "b": "buy", "q": "quit",
        }
        cmd = shortcuts.get(cmd, cmd)

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
            "unequip":   self.cmd_unequip,
            "use":       self.cmd_use,
            "buy":       self.cmd_buy,
            "sell":      self.cmd_sell,
            "fight":     self.cmd_fight,
            "search":    self.cmd_search,
            "sleep":     self.cmd_sleep,
            "train":     self.cmd_train,
            "cheat":     self.cmd_cheat,
            "quit":      self.cmd_quit,
            "exit":      self.cmd_quit,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
            self._tick_respawn()
        else:
            print(styled(f"  Unknown command: {cmd}. Type 'help' for commands.", C.RED))

    # -- main loop --

    def run(self):
        set_gothic_font()
        show_intro()
        print("\033[2J\033[H", end="", flush=True)

        print()
        print(styled(r"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  ___   ___  _     ___
  |_   _| || | __|  | __|/ _ \| _ \ __/ __|_   _|  | __|/ _ \ / _ \| |   / __|
    | | | __ | _|   | _|| (_) |   / _|\__ \ | |    | _|| (_) | (_) | |__ \__ \
    |_| |_||_|___|  |_|  \___/|_|_\___|___/ |_|    |_|  \___/ \___/|____|___/
        """, C.BOLD, C.RED))

        print(styled("    Version 1.0.4", C.DIM))
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
