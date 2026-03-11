"""
=============================================================================
  ENEMIES — Monstres par zone
=============================================================================
  Format:
    "nom_zone": [
        {"name": "Nom", "hp": X, "attack": X, "gold": (min, max), "xp": X},
        ...
    ],

  Zones existantes : "forest", "cave", "castle", "dungeon"
  Tu peux en ajouter de nouvelles — il suffit d'ajouter aussi la zone dans
  locations.py et config.py (ZONE_LEVEL_REQUIREMENTS / ZONE_TIERS).

  Les stats sont automatiquement scalées avec le level du joueur.
=============================================================================
"""

ZONE_ENEMIES = {
    "forest": [
        {"name": "Giant Rat",        "hp": 15,  "attack": 3,  "gold": (2, 6),   "xp": 6},
        {"name": "Wild Crow",        "hp": 12,  "attack": 2,  "gold": (1, 4),   "xp": 4},
        {"name": "Plague Rat Swarm", "hp": 20,  "attack": 4,  "gold": (2, 8),   "xp": 8},
        {"name": "Feral Boar",       "hp": 25,  "attack": 5,  "gold": (3, 8),   "xp": 10},
        {"name": "Giant Spider",     "hp": 22,  "attack": 4,  "gold": (2, 7),   "xp": 7},
        {"name": "Goblin Scavenger", "hp": 18,  "attack": 3,  "gold": (2, 6),   "xp": 6},
        {"name": "Venomous Snake",   "hp": 14,  "attack": 5,  "gold": (2, 5),   "xp": 5},
    ],
    "cave": [
        {"name": "Cave Wolf",      "hp": 35,  "attack": 7,  "gold": (5, 15),  "xp": 15},
        {"name": "Brown Bear",     "hp": 50,  "attack": 9,  "gold": (8, 20),  "xp": 20},
        {"name": "Cave Bat Swarm", "hp": 25,  "attack": 6,  "gold": (4, 12),  "xp": 12},
        {"name": "Rock Troll",     "hp": 60,  "attack": 10, "gold": (10, 25), "xp": 22},
        {"name": "Shadow Stalker", "hp": 40,  "attack": 8,  "gold": (6, 18),  "xp": 18},
        {"name": "Undead Miner",   "hp": 30,  "attack": 7,  "gold": (5, 15),  "xp": 14},
    ],
    "castle": [
        {"name": "Living Armor",    "hp": 60,  "attack": 12, "gold": (12, 30), "xp": 30},
        {"name": "Haunted Knight",  "hp": 70,  "attack": 14, "gold": (15, 35), "xp": 35},
        {"name": "Hollow Wraith",   "hp": 50,  "attack": 11, "gold": (10, 28), "xp": 28},
        {"name": "Cursed Sentinel", "hp": 65,  "attack": 13, "gold": (12, 32), "xp": 32},
        {"name": "Spectral Guard",  "hp": 55,  "attack": 12, "gold": (10, 28), "xp": 28},
        {"name": "Gargoyle",        "hp": 75,  "attack": 15, "gold": (15, 40), "xp": 38},
    ],
    "dungeon": [
        {"name": "Cursed Knight",  "hp": 80,  "attack": 16, "gold": (18, 45), "xp": 45},
        {"name": "Tomb Guardian",  "hp": 90,  "attack": 18, "gold": (20, 50), "xp": 50},
        {"name": "Dark Sorcerer",  "hp": 70,  "attack": 20, "gold": (25, 60), "xp": 55},
        {"name": "Bone Colossus",  "hp": 120, "attack": 22, "gold": (30, 70), "xp": 65},
        {"name": "Undead Priest",  "hp": 65,  "attack": 17, "gold": (18, 45), "xp": 45},
        {"name": "Abyssal Demon",  "hp": 100, "attack": 24, "gold": (30, 80), "xp": 70},
    ],
}

# Fallback pour les zones non listées
ENEMIES_FALLBACK = ZONE_ENEMIES["forest"]

# Le boss dragon (stats séparées dans le code combat, mais tu peux le changer ici)
DRAGON_BOSS = {
    "name": "The Ancient Dragon",
    "hp": 350,
    "attack": 40,
    "gold": (100, 250),
    "xp": 500,
    "inferno_chance": 0.3,  # % chance d'attaque spéciale (double dégâts)
}
