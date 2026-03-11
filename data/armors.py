"""
=============================================================================
  ARMORS — Ajouter / modifier des armures ici
=============================================================================
  Format:
    "cle_unique": {"name": "Nom affiché", "armor": X, "dodge": Y, "value": Z},

  - armor : réduction de dégâts
  - dodge : % de chance d'esquiver une attaque
  - value : prix d'achat
=============================================================================
"""

ARMORS = {
    "cloth_rags":   {"name": "Cloth Rags",   "armor": 1,  "dodge": 5,  "value": 3},
    "leather_vest": {"name": "Leather Vest",  "armor": 4,  "dodge": 10, "value": 15},
    "chainmail":    {"name": "Chainmail",     "armor": 8,  "dodge": 3,  "value": 45},
    "plate_armor":  {"name": "Plate Armor",   "armor": 14, "dodge": 2,  "value": 100},
    "dark_plate":   {"name": "Dark Plate",    "armor": 20, "dodge": 5,  "value": 250},
    "shadow_cloak": {"name": "Shadow Cloak",  "armor": 10, "dodge": 20, "value": 80},
}
