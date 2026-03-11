"""Player class."""

import random
from data.weapons import WEAPONS
from data.armors import ARMORS
from data.consumables import CONSUMABLES
from data.misc_items import MISC_ITEMS
from data.config import (
    PLAYER_START_HP, PLAYER_START_MANA, PLAYER_START_ATTACK,
    PLAYER_START_GOLD, PLAYER_START_WEAPON, PLAYER_START_ARMOR,
    STARTING_MAX_SPELLS, LEVELUP_HP, LEVELUP_ATTACK, LEVELUP_MANA,
    XP_BASE, XP_MULTIPLIER, CAPITAL_POS,
)


class Player:
    def __init__(self):
        self.hp = PLAYER_START_HP
        self.max_hp = PLAYER_START_HP
        self.mana = PLAYER_START_MANA
        self.max_mana = PLAYER_START_MANA
        self.base_attack = PLAYER_START_ATTACK
        self.base_armor = 0
        self.gold = PLAYER_START_GOLD
        self.level = 1
        self.xp = 0
        self.xp_to_next = XP_BASE

        self.weapon = PLAYER_START_WEAPON
        self.armor_equipped = PLAYER_START_ARMOR

        # Inventory
        self.weapons = [PLAYER_START_WEAPON]
        self.armors = [PLAYER_START_ARMOR]
        self.consumables = ["small_potion"]
        self.misc = []
        self.spells = []
        self.max_spells = STARTING_MAX_SPELLS

        # Map
        self.has_map = False

        # Location
        self.pos: tuple[str, int] = CAPITAL_POS
        self.inside = None
        self.subloc = None

        # Quest state
        self.dragon_quest = None  # None, "given", "completed"

    @property
    def attack(self):
        w = WEAPONS.get(self.weapon, {})
        return self.base_attack + w.get("attack", 0)

    @property
    def armor_value(self):
        a = ARMORS.get(self.armor_equipped, {})
        return self.base_armor + a.get("armor", 0)

    @property
    def dodge_chance(self):
        a = ARMORS.get(self.armor_equipped, {})
        return a.get("dodge", 0)

    def weapon_name(self):
        w = WEAPONS.get(self.weapon)
        return w["name"] if w else "Bare Fists"

    def armor_name(self):
        a = ARMORS.get(self.armor_equipped)
        return a["name"] if a else "None"

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, raw_dmg):
        if random.randint(1, 100) <= self.dodge_chance:
            return 0  # dodged
        reduced = max(1, raw_dmg - self.armor_value // 2)
        self.hp -= reduced
        return reduced

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_hp += LEVELUP_HP
            self.hp = self.max_hp
            self.base_attack += LEVELUP_ATTACK
            self.max_mana += LEVELUP_MANA
            self.mana = self.max_mana
            self.xp_to_next = int(self.xp_to_next * XP_MULTIPLIER)
            leveled = True
        return leveled

    def has_item(self, key):
        return (key in self.weapons or key in self.armors or
                key in self.consumables or key in self.misc)

    def add_item(self, key):
        if key in WEAPONS:
            self.weapons.append(key)
        elif key in ARMORS:
            self.armors.append(key)
        elif key in CONSUMABLES:
            self.consumables.append(key)
        elif key in MISC_ITEMS:
            self.misc.append(key)

    def remove_item(self, key):
        for lst in (self.weapons, self.armors, self.consumables, self.misc):
            if key in lst:
                lst.remove(key)
                return True
        return False
