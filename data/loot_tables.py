"""Loot tiers for shops, search rewards, and rare monster equipment drops."""

import random

from data.armors import ARMORS
from data.consumables import CONSUMABLES
from data.misc_items import MISC_ITEMS
from data.weapons import WEAPONS


REGION_LOOT_TIERS = {
    "mosswake": 1,
    "crownvale": 2,
    "greenmarch": 3,
    "scalefen": 4,
    "ashenreach": 5,
}

POOL_LOOT_TIERS = {
    "slime_king": 1,
    "crownvale_woods": 2,
    "hollow_baron": 2,
    "greenmarch_forest": 3,
    "thornwell_warden": 3,
    "scalefen_marsh": 4,
    "mirejaw_matriarch": 4,
    "ashenreach_wastes": 5,
}

TILE_TYPE_MIN_TIERS = {
    "forest": 1,
    "slime_lair": 1,
    "village": 1,
    "port": 1,
    "capital": 2,
    "cave": 2,
    "castle": 2,
    "dungeon": 4,
    "dragon_lair": 5,
}

WEAPON_TIERS = {
    1: ["rusty_sword", "iron_dagger", "mosswood_staff", "fisher_hook_blade"],
    2: ["iron_sword", "militia_sabre", "steel_sword", "field_halberd", "war_hammer", "knight_longsword"],
    3: ["briar_knife", "dark_blade", "thornwood_staff", "rootbound_axe", "silver_longsword"],
    4: ["reedscale_spear", "swamp_cleaver", "bog_iron_mace", "mirefang_blade", "cursed_greatsword"],
    5: ["ashen_greatsword", "basalt_maul", "cinder_edge"],
    6: ["dragon_slayer_blade", "oathkeeper"],
}

ARMOR_TIERS = {
    1: ["cloth_rags", "padded_jacket", "leather_vest", "fisher_coat", "scout_cloak"],
    2: ["chainmail", "brigandine", "ranger_hood", "knight_mail", "plate_armor"],
    3: ["shadow_cloak", "mossweave_robes", "barkscale_mail"],
    4: ["reedscale_vest", "marshguard_plate", "mistwalker_cloak", "dark_plate"],
    5: ["basalt_plate", "ashen_cloak", "wyrmguard_plate"],
}

COMMON_MISC_LOOT = [
    "old_key",
    "skull_amulet",
    "raven_feather",
    "golden_chalice",
    "torn_scroll",
    "dark_gem",
    "iron_ring",
]


def loot_tier_for_tile(tile, player_level=1):
    """Return the loot tier implied by a tile's world, type, boss, or enemy pool."""
    if not tile:
        return max(1, min(5, 1 + player_level // 4))

    map_key = tile.get("map_key") or tile.get("region")
    tier = REGION_LOOT_TIERS.get(map_key, 1)
    tier = max(tier, TILE_TYPE_MIN_TIERS.get(tile.get("type"), 1))

    pool_key = tile.get("boss") or tile.get("enemy_pool")
    if pool_key:
        tier = max(tier, POOL_LOOT_TIERS.get(pool_key, tier))

    return max(1, min(5, tier))


def _items_up_to(tier_table, tier):
    items = []
    for item_tier in sorted(tier_table):
        if item_tier <= tier:
            items.extend(key for key in tier_table[item_tier] if key in WEAPONS or key in ARMORS)
    return items


def _items_at(tier_table, tier):
    return [key for key in tier_table.get(tier, []) if key in WEAPONS or key in ARMORS]


def equipment_keys_for_tier(tier):
    return _items_up_to(WEAPON_TIERS, tier) + _items_up_to(ARMOR_TIERS, tier)


def rare_next_tier_equipment(tier):
    candidates = _items_at(WEAPON_TIERS, tier + 1) + _items_at(ARMOR_TIERS, tier + 1)
    if tier >= 5:
        candidates += _items_at(WEAPON_TIERS, 6)
    return candidates


def random_equipment_for_tile(tile, player_level=1, rare_chance=0.08):
    tier = loot_tier_for_tile(tile, player_level)
    if random.random() < rare_chance:
        candidates = rare_next_tier_equipment(tier)
        if candidates:
            return random.choice(candidates)
    candidates = _items_at(WEAPON_TIERS, tier) + _items_at(ARMOR_TIERS, tier)
    if tier > 1 and random.random() < 0.25:
        candidates += _items_at(WEAPON_TIERS, tier - 1) + _items_at(ARMOR_TIERS, tier - 1)
    return random.choice(candidates) if candidates else None


def random_common_loot():
    return random.choice(list(CONSUMABLES.keys()) + [key for key in COMMON_MISC_LOOT if key in MISC_ITEMS])


def roll_enemy_drop(tile, player_level=1):
    """Drop table for normal monsters: common loot often, equipment rarely."""
    if random.random() >= 0.32:
        return None
    if random.random() < 0.12:
        return random_equipment_for_tile(tile, player_level, rare_chance=0.12)
    return random_common_loot()


def roll_search_drop(tile, player_level=1):
    """Drop table for searchable places: better chance than monsters."""
    if random.random() >= 0.55:
        return None
    if random.random() < 0.28:
        return random_equipment_for_tile(tile, player_level, rare_chance=0.18)
    return random_common_loot()


def random_treasure_equipment(tile, player_level=1):
    return random_equipment_for_tile(tile, player_level, rare_chance=0.25)


def merchant_stock_for_region(region_key=None):
    """Generate shop stock using the region tier instead of the full item list."""
    tier = REGION_LOOT_TIERS.get(region_key, 1)
    stock = []

    consumables = list(CONSUMABLES.keys())
    stock.extend(random.sample(consumables, k=min(3, len(consumables))))

    current_weapons = [key for key in _items_at(WEAPON_TIERS, tier) if key in WEAPONS]
    previous_weapons = [key for key in _items_at(WEAPON_TIERS, tier - 1) if key in WEAPONS]
    current_armors = [key for key in _items_at(ARMOR_TIERS, tier) if key in ARMORS]
    previous_armors = [key for key in _items_at(ARMOR_TIERS, tier - 1) if key in ARMORS]

    if current_weapons:
        stock.extend(random.sample(current_weapons, k=min(random.randint(1, 2), len(current_weapons))))
    if previous_weapons and random.random() < 0.45:
        stock.append(random.choice(previous_weapons))
    if current_armors and random.random() < 0.8:
        stock.append(random.choice(current_armors))
    elif previous_armors and random.random() < 0.45:
        stock.append(random.choice(previous_armors))
    if random.random() < 0.08:
        rare = rare_next_tier_equipment(tier)
        if rare:
            stock.append(random.choice(rare))

    return stock
