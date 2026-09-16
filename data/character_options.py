"""Character creation options and starting bonuses."""

RACES = {
    "human": {
        "name": "Human",
        "description": "Balanced and adaptable.",
        "bonuses": {
            "max_hp": 5,
            "max_mana": 5,
            "base_attack": 1,
            "magic_power": 0,
            "base_armor": 0,
        },
    },
    "elf": {
        "name": "Elf",
        "description": "Gifted with mana and old forest senses.",
        "bonuses": {
            "max_hp": -5,
            "max_mana": 20,
            "base_attack": 0,
            "magic_power": 6,
            "base_armor": 0,
        },
    },
    "lizardfolk": {
        "name": "Lizardfolk",
        "description": "Scaled, resilient, and born for dangerous wilds.",
        "bonuses": {
            "max_hp": 15,
            "max_mana": 0,
            "base_attack": 2,
            "magic_power": 0,
            "base_armor": 2,
        },
    },
}

GENDERS = {
    "male": {"name": "Male"},
    "female": {"name": "Female"},
}

CLASSES = {
    "warrior": {
        "name": "Warrior",
        "description": "Stronger in melee, tougher at the start.",
        "bonuses": {
            "max_hp": 15,
            "max_mana": -10,
            "base_attack": 4,
            "magic_power": -2,
            "base_armor": 1,
        },
        "starting_items": {
            "weapons": ["iron_sword"],
            "consumables": ["small_potion"],
        },
    },
    "mage": {
        "name": "Mage",
        "description": "More mana and spell power, weaker in melee.",
        "bonuses": {
            "max_hp": -10,
            "max_mana": 35,
            "base_attack": -1,
            "magic_power": 8,
            "base_armor": 0,
        },
        "starting_items": {
            "spells": ["fireball"],
            "consumables": ["small_potion"],
        },
    },
}

DEFAULT_CHARACTER = {
    "race": "human",
    "gender": "male",
    "class": "warrior",
}
