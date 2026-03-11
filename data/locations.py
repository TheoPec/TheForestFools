"""
=============================================================================
  LOCATIONS — Tiles, sous-locations, et descriptions
=============================================================================
  Modifie ici les types de tuiles sur la carte, les sous-locations
  disponibles dans chaque lieu, et toutes les descriptions gothiques.
=============================================================================
"""

# ---------------------------------------------------------------------------
# Symboles et couleurs des tuiles sur la carte
# ---------------------------------------------------------------------------

TILE_SYMBOLS = {
    "plains":      ".",
    "forest":      "T",
    "village":     "V",
    "cave":        "O",
    "castle":      "#",
    "dungeon":     "X",
    "capital":     "K",
    "dragon_lair": "D",
    "port":        "P",
    "water":       "~",
}

TILE_NAMES = {
    "plains":      "Plains",
    "forest":      "Forest",
    "village":     "Village",
    "cave":        "Cave",
    "castle":      "Castle",
    "dungeon":     "Dungeon",
    "capital":     "Capital",
    "dragon_lair": "Dragon Lair",
    "port":        "Port",
    "water":       "Water",
}

# ---------------------------------------------------------------------------
# Sous-locations accessibles dans chaque type de lieu
# ---------------------------------------------------------------------------

SUBLOCS = {
    "village":     ["merchant", "blacksmith", "tavern", "chapel", "square"],
    "cave":        ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "dungeon":     ["entrance", "corridor", "crypt", "altar", "treasure_room"],
    "castle":      ["courtyard", "great_hall", "tower", "dungeon_cells", "throne_room", "treasure_room"],
    "forest":      ["clearing", "ruins", "stream"],
    "capital":     ["courtyard", "great_hall", "throne_room", "barracks", "merchant", "tavern"],
    "dragon_lair": ["entrance", "tunnel", "hoard", "nest"],
    "port":        ["dock", "tavern", "merchant"],
}

# ---------------------------------------------------------------------------
# Descriptions gothiques — zones principales
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

# Table de lookup — ne pas modifier sauf si tu ajoutes un nouveau type de lieu
DESC_MAP = {
    "plains":      DESC_PLAINS,
    "forest":      DESC_FOREST,
    "village":     DESC_VILLAGE,
    "cave":        DESC_CAVE,
    "castle":      DESC_CASTLE,
    "dungeon":     DESC_DUNGEON,
    "capital":     DESC_CAPITAL,
    "dragon_lair": DESC_DRAGON_LAIR,
    "port":        DESC_PORT,
}

# ---------------------------------------------------------------------------
# Descriptions des sous-locations
# ---------------------------------------------------------------------------

DESC_SUBLOCS = {
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
