"""
=============================================================================
  CONSUMABLES — Potions et objets consommables
=============================================================================
  Format:
    "cle_unique": {"name": "Nom affiché", "heal": X, "value": Y},

  - heal  : HP restaurés quand utilisé
  - value : prix d'achat
=============================================================================
"""

CONSUMABLES = {
    "small_potion":  {"name": "Small Potion",  "heal": 25,  "value": 8},
    "medium_potion": {"name": "Medium Potion", "heal": 50,  "value": 20},
    "large_potion":  {"name": "Large Potion",  "heal": 100, "value": 45},
    "elixir":        {"name": "Elixir",        "heal": 200, "value": 100},
}
