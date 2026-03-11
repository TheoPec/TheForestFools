"""Combat system: regular fights, dragon boss, spell casting."""

import random
from data.weapons import WEAPONS
from data.armors import ARMORS
from data.consumables import CONSUMABLES
from data.misc_items import MISC_ITEMS
from data.spells import SPELLS
from data.enemies import ZONE_ENEMIES, ENEMIES_FALLBACK, DRAGON_BOSS
from data.config import ENEMY_SCALE_PER_LEVEL
from engine.terminal import C, styled

# Combined item catalog for loot drops
ALL_ITEMS = {}
ALL_ITEMS.update(WEAPONS)
ALL_ITEMS.update(ARMORS)
ALL_ITEMS.update(CONSUMABLES)
ALL_ITEMS.update(MISC_ITEMS)


def cast_spell_in_combat(player, enemy, print_sep=None):
    """Let the player pick and cast a spell during combat."""
    print(styled("  Your spells:", C.MAGENTA))
    for i, spell_key in enumerate(player.spells):
        info = SPELLS[spell_key]
        details = []
        if "damage" in info:
            details.append(f"DMG {info['damage']}")
        if "heal" in info:
            details.append(f"Heal {info['heal']}")
        if "shield" in info:
            details.append(f"Shield +{info['shield']}")
        if "weaken" in info:
            details.append(f"Weaken {int(info['weaken']*100)}%")
        detail_str = ", ".join(details)
        print(f"    [{i+1}] {info['name']} ({detail_str}, {info['mana']} mana)")
    print(styled("  [0] Cancel", C.DIM))
    try:
        choice = input(styled("  Spell> ", C.BOLD)).strip()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "0" or not choice:
        print(styled("  Cancelled.", C.DIM))
        return
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(player.spells):
            raise ValueError
    except ValueError:
        print(styled("  Invalid choice.", C.RED))
        return
    spell_key = player.spells[idx]
    info = SPELLS[spell_key]
    mana_cost = info["mana"]
    if player.mana < mana_cost:
        print(styled(f"  Not enough mana! Need {mana_cost}, have {player.mana}.", C.RED))
        return
    player.mana -= mana_cost
    if "damage" in info:
        dmg = info["damage"]
        enemy["hp"] -= dmg
        print(styled(f"  You cast {info['name']}! {dmg} damage to {enemy['name']}!", C.MAGENTA, C.BOLD))
    if "heal" in info:
        heal_amt = info["heal"]
        old_hp = player.hp
        player.heal(heal_amt)
        print(styled(f"  {info['name']} restores {player.hp - old_hp} HP!", C.GREEN))
    if "shield" in info:
        player.base_armor += info["shield"]
        print(styled(f"  {info['name']} grants +{info['shield']} armor for this battle!", C.BLUE))
    if "weaken" in info:
        reduction = int(enemy["attack"] * info["weaken"])
        enemy["attack"] = max(1, enemy["attack"] - reduction)
        print(styled(f"  {info['name']} weakens {enemy['name']}! ATK reduced by {reduction}!", C.RED))
    print(styled(f"  (Mana: {player.mana}/{player.max_mana})", C.BLUE))


def _enemy_attack(player, enemy):
    """Standard enemy counter-attack."""
    raw = random.randint(enemy["attack"] // 2, enemy["attack"])
    taken = player.take_damage(raw)
    if taken == 0:
        print(styled(f"  You dodge the {enemy['name']}'s attack!", C.GREEN, C.BOLD))
    else:
        print(styled(f"  The {enemy['name']} hits you for {taken} damage!", C.RED))


def _dragon_attack(player, dragon):
    """Dragon counter-attack with inferno breath chance."""
    if random.random() < DRAGON_BOSS.get("inferno_chance", 0.3):
        raw = random.randint(dragon["attack"] // 2, dragon["attack"]) * 2
        taken = player.take_damage(raw)
        if taken == 0:
            print(styled(f"  You dodge {dragon['name']}'s INFERNO BREATH!", C.GREEN, C.BOLD))
        else:
            print(styled(f"  {dragon['name']} unleashes INFERNO BREATH for {taken} damage!", C.RED, C.BOLD))
    else:
        raw = random.randint(dragon["attack"] // 2, dragon["attack"])
        taken = player.take_damage(raw)
        if taken == 0:
            print(styled(f"  You dodge {dragon['name']}'s claws!", C.GREEN, C.BOLD))
        else:
            print(styled(f"  {dragon['name']} claws you for {taken} damage!", C.RED))


def _combat_use_potion(player):
    """Use the smallest potion available."""
    potions = [(k, CONSUMABLES[k]) for k in player.consumables if k in CONSUMABLES]
    if potions:
        potions.sort(key=lambda x: x[1]["heal"])
        key, info = potions[0]
        old_hp = player.hp
        player.heal(info["heal"])
        player.consumables.remove(key)
        print(styled(f"  Used {info['name']}. Restored {player.hp - old_hp} HP.", C.GREEN))
        return True
    else:
        print(styled("  No potions available!", C.RED))
        return False


def _combat_loop(player, enemy, attack_func, print_sep_fn):
    """Shared combat loop for regular enemies and the dragon."""
    while enemy["hp"] > 0 and player.hp > 0:
        print(styled(f"  Your HP: {player.hp}/{player.max_hp}  Mana: {player.mana}/{player.max_mana}  |  {enemy['name']} HP: {enemy['hp']}/{enemy['max_hp']}", C.WHITE))
        spell_hint = "  [c]ast spell" if player.spells else ""
        print(styled(f"  [a]ttack  [u]se potion  [f]lee{spell_hint}", C.CYAN))
        try:
            action = input(styled("  > ", C.BOLD)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "abort"

        if action in ("a", "attack"):
            dmg = random.randint(player.attack // 2, player.attack)
            enemy["hp"] -= dmg
            print(styled(f"  You strike {enemy['name']} for {dmg} damage!", C.YELLOW))
            if enemy["hp"] <= 0:
                break
            attack_func(player, enemy)

        elif action in ("c", "cast"):
            if not player.spells:
                print(styled("  You don't know any spells!", C.RED))
                continue
            cast_spell_in_combat(player, enemy)
            if enemy["hp"] <= 0:
                break
            attack_func(player, enemy)

        elif action in ("u", "use"):
            _combat_use_potion(player)
            attack_func(player, enemy)

        elif action in ("f", "flee"):
            if random.random() < 0.5:
                print(styled("  You flee from battle!", C.YELLOW))
                print()
                return "fled"
            else:
                print(styled("  You fail to escape!", C.RED))
                attack_func(player, enemy)
        else:
            print(styled("  Invalid action.", C.DIM))

        print()

    if player.hp <= 0:
        return "died"
    return "won"


def fight_enemy(player, tile, print_sep_fn, pos_label_fn):
    """Run a regular enemy fight. Returns True if fight happened."""
    loc = player.inside or tile["type"]
    fightable = {"dungeon", "cave", "forest", "castle"}
    if loc not in fightable:
        print(styled("  There is nothing to fight here.", C.DIM))
        return

    if tile.get("enemies_cleared"):
        print(styled("  This area has been cleared of enemies. (For now...)", C.DIM))
        return

    enemy_pool = ZONE_ENEMIES.get(loc, ENEMIES_FALLBACK)
    enemy_template = random.choice(enemy_pool)
    scale = 1 + (player.level - 1) * ENEMY_SCALE_PER_LEVEL
    enemy = {
        "name": enemy_template["name"],
        "hp": int(enemy_template["hp"] * scale),
        "max_hp": int(enemy_template["hp"] * scale),
        "attack": int(enemy_template["attack"] * scale),
        "gold": enemy_template["gold"],
        "xp": int(enemy_template["xp"] * scale),
    }

    print()
    print_sep_fn()
    print(styled(f"  A {enemy['name']} emerges from the shadows!", C.RED, C.BOLD))
    print(styled(f"  HP: {enemy['hp']}  ATK: {enemy['attack']}", C.RED))
    print_sep_fn()
    print()

    result = _combat_loop(player, enemy, _enemy_attack, print_sep_fn)

    if result == "died":
        print()
        print_sep_fn()
        print(styled("  YOU HAVE FALLEN.", C.RED, C.BOLD))
        print(styled("  Darkness takes you...", C.DIM))
        print_sep_fn()
        _death_penalty(player, pos_label_fn)
    elif result == "won":
        gold_gained = random.randint(*enemy["gold"])
        player.gold += gold_gained
        print()
        print_sep_fn()
        print(styled(f"  The {enemy['name']} is defeated!", C.GREEN, C.BOLD))
        print(styled(f"  Gained {gold_gained} gold and {enemy['xp']} XP.", C.YELLOW))
        leveled = player.gain_xp(enemy["xp"])
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {player.level}!", C.BOLD, C.CYAN))
            print(styled(f"  Max HP: {player.max_hp}  Base ATK: {player.base_attack}", C.CYAN))
        if random.random() < 0.3:
            loot_pool = list(CONSUMABLES.keys()) + list(MISC_ITEMS.keys())
            if random.random() < 0.15:
                loot_pool += list(WEAPONS.keys()) + list(ARMORS.keys())
            drop = random.choice(loot_pool)
            info = ALL_ITEMS[drop]
            player.add_item(drop)
            print(styled(f"  Found: {info['name']}!", C.GREEN))
        print_sep_fn()
        print()
        if random.random() < 0.4:
            tile["enemies_cleared"] = True


def fight_dragon(player, world, print_sep_fn, pos_label_fn):
    """Run the dragon boss fight."""
    if player.dragon_quest == "completed":
        print(styled("  The dragon is already slain. Its bones lie cold.", C.DIM))
        return

    dragon = {
        "name": DRAGON_BOSS["name"],
        "hp": DRAGON_BOSS["hp"],
        "max_hp": DRAGON_BOSS["hp"],
        "attack": DRAGON_BOSS["attack"],
        "gold": DRAGON_BOSS["gold"],
        "xp": DRAGON_BOSS["xp"],
    }

    print()
    print_sep_fn()
    print(styled("  THE ANCIENT DRAGON RISES!", C.RED, C.BOLD))
    print(styled("  The ground shakes. Fire erupts from the beast's maw.", C.RED))
    print(styled(f"  HP: {dragon['hp']}  ATK: {dragon['attack']}", C.RED))
    print_sep_fn()
    print()

    result = _combat_loop(player, dragon, _dragon_attack, print_sep_fn)

    if result == "died":
        print()
        print_sep_fn()
        print(styled("  THE DRAGON HAS SLAIN YOU.", C.RED, C.BOLD))
        print(styled("  Darkness takes you...", C.DIM))
        print_sep_fn()
        _death_penalty(player, pos_label_fn)
    elif result == "won":
        gold_gained = random.randint(*dragon["gold"])
        player.gold += gold_gained
        player.dragon_quest = "completed"
        player.weapons.append("dragon_slayer_blade")
        print()
        print_sep_fn()
        print(styled("  THE ANCIENT DRAGON IS SLAIN!", C.GREEN, C.BOLD))
        print(styled(f"  Gained {gold_gained} gold and {dragon['xp']} XP.", C.YELLOW))
        print(styled("  You claim the Dragon Slayer Blade from the hoard!", C.BOLD, C.CYAN))
        leveled = player.gain_xp(dragon["xp"])
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {player.level}!", C.BOLD, C.CYAN))
            print(styled(f"  Max HP: {player.max_hp}  Base ATK: {player.base_attack}", C.CYAN))
        print_sep_fn()
        print()


def _death_penalty(player, pos_label_fn):
    from data.config import CAPITAL_POS
    player.hp = player.max_hp // 2
    gold_lost = player.gold // 3
    player.gold -= gold_lost
    player.pos = CAPITAL_POS
    player.inside = None
    player.subloc = None
    print(styled(f"  You awaken at {pos_label_fn()}, weakened. Lost {gold_lost} gold.", C.YELLOW))
    print()
