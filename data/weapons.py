"""
=============================================================================
  WEAPONS — Ajouter / modifier des armes ici
=============================================================================
  Format:
    "cle_unique": {"name": "Nom affiché", "attack": X, "value": Y},

  - attack : bonus d'attaque quand l'arme est équipée
  - value  : prix d'achat chez le marchand (vente = moitié)
=============================================================================
"""

WEAPONS = {
    "rusty_sword":         {"name": "Rusty Sword",         "attack": 3,  "value": 5},
    "iron_dagger":         {"name": "Iron Dagger",         "attack": 5,  "value": 12},
    "iron_sword":          {"name": "Iron Sword",          "attack": 8,  "value": 25},
    "steel_sword":         {"name": "Steel Sword",         "attack": 12, "value": 50},
    "war_hammer":          {"name": "War Hammer",          "attack": 14, "value": 65},
    "dark_blade":          {"name": "Dark Blade",          "attack": 18, "value": 120},
    "silver_longsword":    {"name": "Silver Longsword",    "attack": 22, "value": 200},
    "cursed_greatsword":   {"name": "Cursed Greatsword",   "attack": 28, "value": 350},
    "dragon_slayer_blade": {"name": "Dragon Slayer Blade", "attack": 35, "value": 1000},
}
