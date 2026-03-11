"""
=============================================================================
  SPELLS — Sorts magiques
=============================================================================
  Format:
    "cle_unique": {
        "name": "Nom affiché",
        "damage": X,        # (optionnel) dégâts infligés
        "heal": X,          # (optionnel) HP restaurés
        "shield": X,        # (optionnel) bonus armure temporaire
        "weaken": 0.3,      # (optionnel) % réduction ATK ennemi
        "mana": X,          # coût en mana
        "value": X,         # prix d'achat
        "source": "mage",   # qui le vend : "mage" ou "warlock"
    },

  source:
    "mage"    → vendu par le mage dans le courtyard (castle / capital)
    "warlock" → vendu par le warlock dans la tower du castle
=============================================================================
"""

SPELLS = {
    # ---- Mage spells (courtyard) ----
    "fireball":      {"name": "Fireball",      "damage": 30, "mana": 20, "value": 50,  "source": "mage"},
    "ice_shard":     {"name": "Ice Shard",     "damage": 20, "mana": 15, "value": 35,  "source": "mage"},
    "heal_light":    {"name": "Heal Light",    "heal": 40,   "mana": 25, "value": 60,  "source": "mage"},
    "arcane_shield": {"name": "Arcane Shield", "shield": 10, "mana": 20, "value": 45,  "source": "mage"},

    # ---- Warlock spells (castle tower) ----
    "shadow_bolt":   {"name": "Shadow Bolt",   "damage": 40, "mana": 25, "value": 80,  "source": "warlock"},
    "drain_life":    {"name": "Drain Life",    "damage": 25, "heal": 25, "mana": 30, "value": 100, "source": "warlock"},
    "curse":         {"name": "Curse",         "weaken": 0.3, "mana": 20, "value": 70, "source": "warlock"},
}
