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
    "padded_jacket": {"name": "Padded Jacket", "armor": 2, "dodge": 8, "value": 8},
    "leather_vest": {"name": "Leather Vest",  "armor": 4,  "dodge": 10, "value": 15},
    "fisher_coat":  {"name": "Fisher Coat",  "armor": 5,  "dodge": 12, "value": 24},
    "scout_cloak":  {"name": "Scout Cloak",  "armor": 6,  "dodge": 16, "value": 35},
    "chainmail":    {"name": "Chainmail",     "armor": 8,  "dodge": 3,  "value": 45},
    "brigandine":   {"name": "Brigandine",   "armor": 11, "dodge": 5,  "value": 75},
    "ranger_hood":  {"name": "Ranger Hood",  "armor": 9,  "dodge": 18, "value": 90},
    "knight_mail":  {"name": "Knight Mail",  "armor": 13, "dodge": 4,  "value": 110},
    "plate_armor":  {"name": "Plate Armor",   "armor": 14, "dodge": 2,  "value": 100},
    "mossweave_robes": {"name": "Mossweave Robes", "armor": 12, "dodge": 14, "value": 140},
    "barkscale_mail": {"name": "Barkscale Mail", "armor": 16, "dodge": 8, "value": 190},
    "dark_plate":   {"name": "Dark Plate",    "armor": 20, "dodge": 5,  "value": 250},
    "shadow_cloak": {"name": "Shadow Cloak",  "armor": 10, "dodge": 20, "value": 80},
    "reedscale_vest": {"name": "Reedscale Vest", "armor": 18, "dodge": 11, "value": 260},
    "marshguard_plate": {"name": "Marshguard Plate", "armor": 22, "dodge": 6, "value": 360},
    "mistwalker_cloak": {"name": "Mistwalker Cloak", "armor": 17, "dodge": 24, "value": 420},
    "basalt_plate": {"name": "Basalt Plate", "armor": 26, "dodge": 3, "value": 620},
    "ashen_cloak":  {"name": "Ashen Cloak",  "armor": 21, "dodge": 22, "value": 700},
    "wyrmguard_plate": {"name": "Wyrmguard Plate", "armor": 30, "dodge": 8, "value": 950},
}
