"""Combat system: step-based encounters for the interface terminal."""

import random

from data.armors import ARMORS
from data.consumables import CONSUMABLES
from data.enemies import DRAGON_BOSS, ENEMIES_FALLBACK, ZONE_ENEMIES
from data.misc_items import MISC_ITEMS
from data.spells import SPELLS
from data.weapons import WEAPONS
from data.config import ENEMY_SCALE_PER_LEVEL
from data.loot_tables import roll_enemy_drop
from engine.terminal import C, styled


ALL_ITEMS = {}
ALL_ITEMS.update(WEAPONS)
ALL_ITEMS.update(ARMORS)
ALL_ITEMS.update(CONSUMABLES)
ALL_ITEMS.update(MISC_ITEMS)


def _normalise(value):
    return value.lower().replace(" ", "_")


def _resolve_spell_key(player, args):
    if not args:
        return None

    candidate = "_".join(args).lower()
    if candidate.isdigit():
        idx = int(candidate) - 1
        if 0 <= idx < len(player.spells):
            return player.spells[idx]
        return None

    if candidate in player.spells:
        return candidate

    matches = []
    for spell_key in player.spells:
        info = SPELLS.get(spell_key, {})
        spell_name = _normalise(info.get("name", spell_key))
        if spell_key.startswith(candidate) or spell_name.startswith(candidate):
            matches.append(spell_key)
    if len(matches) == 1:
        return matches[0]

    matches = []
    for spell_key in player.spells:
        info = SPELLS.get(spell_key, {})
        spell_name = _normalise(info.get("name", spell_key))
        if candidate in spell_key or candidate in spell_name:
            matches.append(spell_key)
    if len(matches) == 1:
        return matches[0]

    return None


def _resolve_consumable_key(player, args):
    consumable_keys = list(dict.fromkeys(player.consumables))
    if not args:
        potions = [(k, CONSUMABLES[k]) for k in consumable_keys if k in CONSUMABLES]
        if not potions:
            return None
        potions.sort(key=lambda item: item[1]["heal"])
        return potions[0][0]

    candidate = "_".join(args).lower()
    if candidate in consumable_keys and candidate in CONSUMABLES:
        return candidate

    matches = []
    for item_key in consumable_keys:
        if item_key not in CONSUMABLES:
            continue
        info = CONSUMABLES[item_key]
        item_name = _normalise(info.get("name", item_key))
        if item_key.startswith(candidate) or item_name.startswith(candidate):
            matches.append(item_key)
    if len(matches) == 1:
        return matches[0]

    matches = []
    for item_key in consumable_keys:
        if item_key not in CONSUMABLES:
            continue
        info = CONSUMABLES[item_key]
        item_name = _normalise(info.get("name", item_key))
        if candidate in item_key or candidate in item_name:
            matches.append(item_key)
    if len(matches) == 1:
        return matches[0]

    return None


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


class CombatEncounter:
    """A combat that advances one player command at a time."""

    def __init__(self, player, enemy, kind, tile=None, world=None, print_sep_fn=None, pos_label_fn=None):
        self.player = player
        self.enemy = enemy
        self.kind = kind
        self.tile = tile
        self.world = world
        self.print_sep_fn = print_sep_fn or (lambda: None)
        self.pos_label_fn = pos_label_fn or (lambda: "")
        self.active = True
        self.result = None
        self.attack_func = _dragon_attack if kind == "dragon" else _enemy_attack

    def get_state(self):
        return {
            "active": self.active,
            "kind": self.kind,
            "result": self.result,
            "enemy": {
                "name": self.enemy["name"],
                "hp": max(0, self.enemy["hp"]),
                "max_hp": self.enemy["max_hp"],
                "attack": self.enemy["attack"],
            },
            "commands": ["attack", "use", "cast {spell}", "flee"],
        }

    def print_status(self):
        if not self.active:
            return
        print(styled(
            f"  Your HP: {self.player.hp}/{self.player.max_hp}  Mana: {self.player.mana}/{self.player.max_mana}  |  "
            f"{self.enemy['name']} HP: {max(0, self.enemy['hp'])}/{self.enemy['max_hp']}",
            C.WHITE,
        ))
        spell_hint = "  cast {spell}" if self.player.spells else ""
        print(styled(f"  Commands: attack  use [potion]  flee{spell_hint}", C.CYAN))

    def print_spell_list(self):
        if not self.player.spells:
            print(styled("  You don't know any spells.", C.RED))
            return
        print(styled("  Your spells:", C.MAGENTA))
        for i, spell_key in enumerate(self.player.spells):
            info = SPELLS[spell_key]
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage'] + self.player.magic_power}")
            if "heal" in info:
                details.append(f"Heal {info['heal'] + self.player.magic_power}")
            if "shield" in info:
                details.append(f"Shield +{info['shield']}")
            if "weaken" in info:
                details.append(f"Weaken {int(info['weaken'] * 100)}%")
            detail_str = ", ".join(details)
            print(f"    [{i + 1}] {info['name']} ({detail_str}, {info['mana']} mana)")
        print(styled("  Use: cast {spell name}  or  cast {number}", C.DIM))

    def handle_command(self, cmd, args=None):
        if not self.active:
            print(styled("  The battle is already over.", C.DIM))
            return

        args = args or []
        cmd = cmd.lower()

        if cmd.isdigit():
            if cmd == "0":
                print(styled("  Cancelled.", C.DIM))
                return
            if self._cast_spell([cmd]):
                self._enemy_turn_if_needed()
            return

        if cmd in ("a", "attack"):
            self._player_attack()
            self._enemy_turn_if_needed()
            return

        if cmd in ("c", "cast"):
            if not args:
                self.print_spell_list()
                return
            if self._cast_spell(args):
                self._enemy_turn_if_needed()
            return

        if cmd in ("u", "use", "potion"):
            self._use_potion(args)
            self._enemy_turn_if_needed()
            return

        if cmd in ("f", "flee"):
            self._flee()
            return

        if cmd in ("help", "?"):
            self.print_status()
            if self.player.spells:
                self.print_spell_list()
            return

        print(styled("  You are in combat. Use: attack, use [potion], cast {spell}, flee.", C.RED))

    def _player_attack(self):
        dmg = random.randint(self.player.attack // 2, self.player.attack)
        self.enemy["hp"] -= dmg
        print(styled(f"  You strike {self.enemy['name']} for {dmg} damage!", C.YELLOW))

    def _cast_spell(self, args):
        if not self.player.spells:
            print(styled("  You don't know any spells!", C.RED))
            return False

        spell_key = _resolve_spell_key(self.player, args)
        if spell_key is None or spell_key not in SPELLS:
            print(styled(f"  Unknown spell: {' '.join(args)}.", C.RED))
            self.print_spell_list()
            return False

        info = SPELLS[spell_key]
        mana_cost = info["mana"]
        if self.player.mana < mana_cost:
            print(styled(f"  Not enough mana! Need {mana_cost}, have {self.player.mana}.", C.RED))
            return False

        self.player.mana -= mana_cost
        if "damage" in info:
            dmg = max(1, info["damage"] + self.player.magic_power)
            self.enemy["hp"] -= dmg
            print(styled(f"  You cast {info['name']}! {dmg} damage to {self.enemy['name']}!", C.MAGENTA, C.BOLD))
        if "heal" in info:
            heal_amt = max(1, info["heal"] + self.player.magic_power)
            old_hp = self.player.hp
            self.player.heal(heal_amt)
            print(styled(f"  {info['name']} restores {self.player.hp - old_hp} HP!", C.GREEN))
        if "shield" in info:
            self.player.base_armor += info["shield"]
            print(styled(f"  {info['name']} grants +{info['shield']} armor for this battle!", C.BLUE))
        if "weaken" in info:
            reduction = int(self.enemy["attack"] * info["weaken"])
            self.enemy["attack"] = max(1, self.enemy["attack"] - reduction)
            print(styled(f"  {info['name']} weakens {self.enemy['name']}! ATK reduced by {reduction}!", C.RED))
        print(styled(f"  (Mana: {self.player.mana}/{self.player.max_mana})", C.BLUE))
        return True

    def _use_potion(self, args):
        key = _resolve_consumable_key(self.player, args)
        if key is None:
            print(styled("  No matching potion available!", C.RED))
            return
        info = CONSUMABLES[key]
        old_hp = self.player.hp
        self.player.heal(info["heal"])
        self.player.consumables.remove(key)
        print(styled(f"  Used {info['name']}. Restored {self.player.hp - old_hp} HP.", C.GREEN))

    def _flee(self):
        if self.kind == "dragon":
            print(styled("  There is no fleeing the dragon now.", C.RED, C.BOLD))
            self.attack_func(self.player, self.enemy)
            if self.player.hp <= 0:
                self._finish_died()
            else:
                self.print_status()
            return

        if random.random() < 0.5:
            print(styled("  You flee from battle!", C.YELLOW))
            print()
            self.active = False
            self.result = "fled"
        else:
            print(styled("  You fail to escape!", C.RED))
            self.attack_func(self.player, self.enemy)
            if self.player.hp <= 0:
                self._finish_died()
            else:
                self.print_status()

    def _enemy_turn_if_needed(self):
        if self.enemy["hp"] <= 0:
            self._finish_won()
            return

        self.attack_func(self.player, self.enemy)
        if self.player.hp <= 0:
            self._finish_died()
            return

        print()
        self.print_status()

    def _finish_died(self):
        print()
        self.print_sep_fn()
        if self.kind == "dragon":
            print(styled("  THE DRAGON HAS SLAIN YOU.", C.RED, C.BOLD))
        else:
            print(styled("  YOU HAVE FALLEN.", C.RED, C.BOLD))
        print(styled("  Darkness takes you...", C.DIM))
        self.print_sep_fn()
        _death_penalty(self.player, self.pos_label_fn)
        self.active = False
        self.result = "died"

    def _finish_won(self):
        if self.kind == "dragon":
            self._finish_dragon_won()
        else:
            self._finish_enemy_won()
        self.active = False
        self.result = "won"

    def _finish_enemy_won(self):
        gold_gained = random.randint(*self.enemy["gold"])
        self.player.gold += gold_gained
        print()
        self.print_sep_fn()
        print(styled(f"  The {self.enemy['name']} is defeated!", C.GREEN, C.BOLD))
        print(styled(f"  Gained {gold_gained} gold and {self.enemy['xp']} XP.", C.YELLOW))
        leveled = self.player.gain_xp(self.enemy["xp"])
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {self.player.level}!", C.BOLD, C.CYAN))
            print(styled(f"  Max HP: {self.player.max_hp}  Base ATK: {self.player.base_attack}", C.CYAN))
        drop = roll_enemy_drop(self.tile, self.player.level)
        if drop:
            info = ALL_ITEMS[drop]
            self.player.add_item(drop)
            print(styled(f"  Found: {info['name']}!", C.GREEN))
        self.print_sep_fn()
        print()
        if self.tile is not None and self.tile.get("boss"):
            self.tile["boss_defeated"] = True
            self.tile["enemies_cleared"] = True
        elif self.tile is not None and random.random() < 0.4:
            self.tile["enemies_cleared"] = True

    def _finish_dragon_won(self):
        gold_gained = random.randint(*self.enemy["gold"])
        self.player.gold += gold_gained
        self.player.dragon_quest = "completed"
        self.player.weapons.append("dragon_slayer_blade")
        print()
        self.print_sep_fn()
        print(styled("  THE ANCIENT DRAGON IS SLAIN!", C.GREEN, C.BOLD))
        print(styled(f"  Gained {gold_gained} gold and {self.enemy['xp']} XP.", C.YELLOW))
        print(styled("  You claim the Dragon Slayer Blade from the hoard!", C.BOLD, C.CYAN))
        leveled = self.player.gain_xp(self.enemy["xp"])
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {self.player.level}!", C.BOLD, C.CYAN))
            print(styled(f"  Max HP: {self.player.max_hp}  Base ATK: {self.player.base_attack}", C.CYAN))
        self.print_sep_fn()
        print()


def fight_enemy(player, tile, print_sep_fn, pos_label_fn):
    """Start a regular enemy fight and return a CombatEncounter."""
    loc = player.inside or tile["type"]
    fightable = {"dungeon", "cave", "forest", "castle", "slime_lair"}
    if loc not in fightable:
        print(styled("  There is nothing to fight here.", C.DIM))
        return None

    if tile.get("boss_defeated"):
        print(styled("  This boss has already been defeated.", C.DIM))
        return None

    if tile.get("enemies_cleared"):
        print(styled("  This area has been cleared of enemies. (For now...)", C.DIM))
        return None

    pool_key = tile.get("boss") or tile.get("enemy_pool") or loc
    enemy_pool = ZONE_ENEMIES.get(pool_key, ZONE_ENEMIES.get(loc, ENEMIES_FALLBACK))
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

    encounter = CombatEncounter(player, enemy, "enemy", tile=tile, print_sep_fn=print_sep_fn, pos_label_fn=pos_label_fn)
    encounter.print_status()
    return encounter


def fight_dragon(player, world, print_sep_fn, pos_label_fn):
    """Start the dragon boss fight and return a CombatEncounter."""
    if player.dragon_quest == "completed":
        print(styled("  The dragon is already slain. Its bones lie cold.", C.DIM))
        return None

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

    encounter = CombatEncounter(player, dragon, "dragon", world=world, print_sep_fn=print_sep_fn, pos_label_fn=pos_label_fn)
    encounter.print_status()
    return encounter


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
