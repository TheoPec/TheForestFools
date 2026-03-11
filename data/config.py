"""
=============================================================================
  CONFIG — Constantes du jeu
=============================================================================
  Modifie ici les prix, les niveaux requis, la taille de la carte, etc.
=============================================================================
"""

# Grille de la carte
COLS = "ABCDEFGHIJ"
ROWS = range(1, 11)

# Prix
MAP_COST = 200          # prix de la carte complète chez l'explorateur
TRAIN_COST = 150        # prix pour augmenter le nombre de sorts
SLEEP_COST = 10         # prix pour dormir à la taverne

# Sorts
MAX_SPELLS_LIMIT = 6    # max absolu de sorts appris
STARTING_MAX_SPELLS = 3 # slots de sorts au départ

# Respawn
RESPAWN_INTERVAL = 15   # les ennemis réapparaissent toutes les N actions

# Level scaling (multiplicateur par level au-dessus de 1)
ENEMY_SCALE_PER_LEVEL = 0.15

# Niveaux requis pour débloquer les hints NPC par zone
ZONE_LEVEL_REQUIREMENTS = {
    "forest":     1,
    "cave":       3,
    "castle":     6,
    "dungeon":    9,
    "dragon_lair": 5,
}

# Ordre de déblocage des zones
ZONE_TIERS = ["forest", "cave", "castle", "dungeon"]

# Nombre de chaque type de lieu sur la carte
WORLD_TILE_COUNTS = [
    ("forest", 3),
    ("village", 3),
    ("cave", 2),
    ("castle", 2),
    ("dungeon", 2),
    ("dragon_lair", 1),
]

# Nombre de ports
PORT_COUNT = 2

# Position de départ / capitale
CAPITAL_POS = ("E", 5)

# Joueur — stats de départ
PLAYER_START_HP = 100
PLAYER_START_MANA = 50
PLAYER_START_ATTACK = 3
PLAYER_START_GOLD = 20
PLAYER_START_WEAPON = "rusty_sword"
PLAYER_START_ARMOR = "cloth_rags"

# Level up bonuses
LEVELUP_HP = 10
LEVELUP_ATTACK = 1
LEVELUP_MANA = 10
XP_BASE = 50
XP_MULTIPLIER = 1.5
