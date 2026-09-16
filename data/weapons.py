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
    "mosswood_staff":      {"name": "Mosswood Staff",      "attack": 6,  "value": 18},
    "fisher_hook_blade":   {"name": "Fisher Hook Blade",   "attack": 7,  "value": 22},
    "iron_sword":          {"name": "Iron Sword",          "attack": 8,  "value": 25},
    "militia_sabre":       {"name": "Militia Sabre",       "attack": 10, "value": 38},
    "steel_sword":         {"name": "Steel Sword",         "attack": 12, "value": 50},
    "field_halberd":       {"name": "Field Halberd",       "attack": 13, "value": 58},
    "war_hammer":          {"name": "War Hammer",          "attack": 14, "value": 65},
    "knight_longsword":    {"name": "Knight Longsword",    "attack": 16, "value": 90},
    "briar_knife":         {"name": "Briar Knife",         "attack": 17, "value": 105},
    "dark_blade":          {"name": "Dark Blade",          "attack": 18, "value": 120},
    "thornwood_staff":     {"name": "Thornwood Staff",     "attack": 20, "value": 155},
    "rootbound_axe":       {"name": "Rootbound Axe",       "attack": 21, "value": 175},
    "silver_longsword":    {"name": "Silver Longsword",    "attack": 22, "value": 200},
    "reedscale_spear":     {"name": "Reedscale Spear",     "attack": 24, "value": 245},
    "swamp_cleaver":       {"name": "Swamp Cleaver",       "attack": 25, "value": 275},
    "bog_iron_mace":       {"name": "Bog-Iron Mace",       "attack": 27, "value": 320},
    "cursed_greatsword":   {"name": "Cursed Greatsword",   "attack": 28, "value": 350},
    "mirefang_blade":      {"name": "Mirefang Blade",      "attack": 30, "value": 430},
    "ashen_greatsword":    {"name": "Ashen Greatsword",    "attack": 32, "value": 560},
    "basalt_maul":         {"name": "Basalt Maul",         "attack": 34, "value": 700},
    "cinder_edge":         {"name": "Cinder Edge",         "attack": 36, "value": 850},
    "dragon_slayer_blade": {"name": "Dragon Slayer Blade", "attack": 35, "value": 1000},
    "oathkeeper":          {"name": "Oathkeeper",          "attack": 40, "value": 1500},
}
