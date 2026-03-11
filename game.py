#!/usr/bin/env python3
"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  ___   ___  _     ___
  |_   _| || | __|  | __|/ _ \\| _ \\ __/ __|_   _|  | __|/ _ \\ / _ \\| |   / __|
    | | | __ | _|   | _|| (_) |   / _|\\__ \\ | |    | _|| (_) | (_) | |__ \\__ \\
    |_| |_||_|___|  |_|  \\___/|_|_\\___|___/ |_|    |_|  \\___/ \\___/|____|___/

A dark medieval gothic exploration game for the terminal.

Structure:
  data/         → Fichiers de contenu (armes, monstres, sorts, etc.)
  engine/       → Logique du jeu (combat, world, player, etc.)
  game.py       → Ce fichier — le coeur du jeu
"""

import random
import textwrap
from collections import Counter

# --- Data imports ---
from data.weapons import WEAPONS
from data.armors import ARMORS
from data.consumables import CONSUMABLES
from data.misc_items import MISC_ITEMS
from data.spells import SPELLS
from data.enemies import ZONE_ENEMIES, ENEMIES_FALLBACK
from data.locations import (
    TILE_SYMBOLS, TILE_NAMES, SUBLOCS,
    DESC_PLAINS, DESC_MAP, DESC_SUBLOCS,
)
from data.npcs import NPC_DIALOGUES, NPC_DIALOGUES_WILD
from data.config import (
    COLS, ROWS, MAP_COST, TRAIN_COST, SLEEP_COST,
    MAX_SPELLS_LIMIT, RESPAWN_INTERVAL,
    ZONE_LEVEL_REQUIREMENTS, ZONE_TIERS, CAPITAL_POS,
)

# --- Engine imports ---
from engine.terminal import C, styled, set_gothic_font
from engine.player import Player
from engine.world import (
    generate_world, generate_merchant_stock, draw_map,
    find_poi, coord_label,
)
from engine.combat import fight_enemy, fight_dragon
from engine.intro import show_intro

# Combined item catalog (for buy/sell/loot)
ALL_ITEMS = {}
ALL_ITEMS.update(WEAPONS)
ALL_ITEMS.update(ARMORS)
ALL_ITEMS.update(CONSUMABLES)
ALL_ITEMS.update(MISC_ITEMS)


# ---------------------------------------------------------------------------
# Game Engine
# ---------------------------------------------------------------------------

class Game:
    def __init__(self):
        self.world = generate_world()
        self.player = Player()
        self.running = True
        self.dragon_lair_pos = next((pos for pos, t in self.world.items() if t["type"] == "dragon_lair"), None)
        self.action_count = 0
        self.respawn_interval = RESPAWN_INTERVAL
        self.npc_pois: dict = {}

    # -- helpers --

    def current_tile(self):
        return self.world[self.player.pos]

    def print_sep(self):
        print(styled("=" * 60, C.DIM))

    def wrap_print(self, text, color=C.WHITE):
        for line in textwrap.wrap(text, width=70):
            print(styled("  " + line, color))

    def pos_label(self):
        return coord_label(self.player.pos)

    def location_label(self):
        parts = [self.pos_label()]
        if self.player.inside:
            parts.append(self.player.inside)
        if self.player.subloc:
            parts.append(self.player.subloc)
        return " > ".join(parts)

    def _pick_poi_for_dialogue(self):
        pois = [(pos, t) for pos, t in find_poi(self.world, exclude_pos=self.player.pos) if t != "dragon_lair"]
        if not pois:
            return None, None, None
        accessible = [(pos, t) for pos, t in pois
                      if self.player.level >= ZONE_LEVEL_REQUIREMENTS.get(t, 1)]
        if not accessible:
            return None, None, None
        pos, loc_type = random.choice(accessible)
        return pos, coord_label(pos), loc_type

    def _get_highest_unlocked_zone(self):
        for zone in reversed(ZONE_TIERS):
            if self.player.level >= ZONE_LEVEL_REQUIREMENTS[zone]:
                return zone
        return "forest"

    def _get_next_locked_zone(self):
        for zone in ZONE_TIERS:
            if self.player.level < ZONE_LEVEL_REQUIREMENTS[zone]:
                return zone
        return None

    # -- commands --

    def cmd_help(self, _args):
        print()
        print(styled("  COMMANDS", C.BOLD, C.YELLOW))
        print(styled("  --------", C.DIM))
        cmds = [
            ("help",             "Show this help."),
            ("map",              "Display the world map."),
            ("cd {cell}",        "Travel to a map cell.  e.g. cd B4"),
            ("cd {location}",    "Enter a location.      e.g. cd village"),
            ("cd {subloc}",      "Enter a sub-location.  e.g. cd tavern"),
            ("cd ..",            "Go back / leave current location."),
            ("look",             "Describe the current location."),
            ("talk",             "Talk to someone here."),
            ("stats",            "Show your stats."),
            ("inventory / inv",  "Show your inventory."),
            ("equip {item}",     "Equip a weapon or armor."),
            ("unequip weapon|armor", "Unequip weapon or armor."),
            ("use {item}",       "Use a consumable item."),
            ("buy {item}",       "Buy from merchant / mage / warlock / explorer."),
            ("sell {item}",      "Sell to a merchant (when at merchant)."),
            ("cast {spell}",     "Cast a spell (in combat)."),
            ("fight",            "Fight enemies (in dungeons/caves/forests)."),
            ("search",           "Search for loot (in special locations)."),
            ("sleep",            "Rest at a tavern (heals HP & mana, 10 gold)."),
            ("train",            "Train with the mage to gain a spell slot (150 gold)."),
            ("cheat",            "Beta testing: get all items, map, lvl 20."),
            ("quit / exit",      "Quit the game."),
            ("", ""),
            ("SHORTCUTS",        "h=help m=map l=look t=talk s=search"),
            ("",                 "f=fight i=inventory e=equip u=use b=buy q=quit"),
            ("", ""),
            ("TIP",              "Type partial item names (e.g. 'sell sm' for Small Potion)."),
        ]
        for cmd, desc in cmds:
            print(f"  {styled(cmd.ljust(20), C.CYAN)} {styled(desc, C.DIM)}")
        print()

    def cmd_map(self, _args):
        draw_map(self.world, self.player.pos)

    def cmd_look(self, _args):
        tile = self.current_tile()
        print()
        self.print_sep()

        if self.player.subloc:
            descs = DESC_SUBLOCS.get(self.player.subloc, ["You see nothing remarkable."])
            self.wrap_print(random.choice(descs), C.WHITE)
            talkable = set()
            talkable.update(NPC_DIALOGUES.get(self.player.subloc, {}).keys())
            talkable.update(NPC_DIALOGUES_WILD.get(self.player.subloc, {}).keys())
            if talkable:
                print()
                print(styled("  Someone is here. Type 'talk' to speak.", C.YELLOW))
            if self.player.subloc == "tavern":
                print(styled("  A room is available. Type 'sleep' to rest (10 gold).", C.YELLOW))
            if self.player.subloc == "courtyard" and self.player.inside in ("castle", "capital"):
                print()
                print(styled("  A mage is here, surrounded by arcane runes.", C.MAGENTA))
                print(styled("  Type 'buy' to see available spells.", C.MAGENTA))
            if self.player.subloc == "tower" and self.player.inside == "castle":
                print()
                print(styled("  A warlock lurks in the shadows of the tower.", C.RED))
                print(styled("  Type 'buy' to see available dark spells.", C.RED))
            if self.player.subloc == "dock" and self.player.inside == "port":
                print()
                print(styled("  An explorer sits nearby with maps and charts.", C.CYAN))
                if not self.player.has_map:
                    print(styled(f"  Type 'buy map' to buy a full map ({MAP_COST} gold).", C.CYAN))
                else:
                    print(styled("  You already own the full map.", C.DIM))
            if self.player.subloc == "treasure_room" and self.player.inside == "castle":
                print()
                if self.world[self.player.pos].get("castle_treasure_opened"):
                    print(styled("  The chest lies open and empty.", C.DIM))
                elif "old_key" in self.player.misc:
                    print(styled("  A locked chest sits here. You have an Old Key! Type 'search' to open it.", C.YELLOW, C.BOLD))
                else:
                    print(styled("  A locked chest sits here. You need an Old Key to open it.", C.YELLOW))
        elif self.player.inside:
            descs = DESC_MAP.get(self.player.inside, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            subs = SUBLOCS.get(self.player.inside, [])
            if subs:
                print()
                print(styled("  You can visit:", C.YELLOW))
                for s in subs:
                    print(styled(f"    cd {s}", C.CYAN))
        else:
            descs = DESC_MAP.get(tile["type"], DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            if tile["type"] not in ("plains", "water"):
                print()
                print(styled(f"  You can enter: cd {tile['type']}", C.YELLOW))

        self.print_sep()
        print()

    def cmd_talk(self, _args):
        p = self.player
        subloc = p.subloc

        # King in the capital throne room
        if p.inside == "capital" and p.subloc == "throne_room":
            print()
            self.print_sep()
            print(styled("  [The King]", C.BOLD, C.YELLOW))
            print()
            if p.level < 5:
                self.wrap_print("\"You are brave to seek audience, but you are not yet ready. Return when you have proven yourself worthy. (Reach level 5)\"", C.WHITE)
            elif p.dragon_quest is None:
                dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
                self.wrap_print(f"\"The realm is dying. An ancient dragon has awakened and terrorises the land from its lair at {styled(dl_coord, C.BOLD, C.CYAN)}. You must go there and slay the beast. The fate of the kingdom rests upon your shoulders.\"", C.WHITE)
                p.dragon_quest = "given"
                if self.dragon_lair_pos:
                    self.world[self.dragon_lair_pos]["revealed"] = True
                    print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))
            elif p.dragon_quest == "given":
                dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
                self.wrap_print(f"\"The dragon still lives! Go to {styled(dl_coord, C.BOLD, C.CYAN)} and slay the beast!\"", C.WHITE)
            elif p.dragon_quest == "completed":
                self.wrap_print("\"You have saved the kingdom! You shall be remembered as a legend!\"", C.WHITE)
            self.print_sep()
            print()
            return

        if not subloc:
            if p.inside:
                print(styled("  There is no one to talk to here. Try entering a specific place.", C.DIM))
            else:
                print(styled("  There is no one to talk to in the open.", C.DIM))
            return

        npc_group = NPC_DIALOGUES.get(subloc, {})
        wild_group = NPC_DIALOGUES_WILD.get(subloc, {})
        all_npcs = {}
        all_npcs.update(npc_group)
        all_npcs.update(wild_group)

        if not all_npcs:
            print(styled("  There is no one here willing to speak.", C.DIM))
            return

        npc_name = random.choice(list(all_npcs.keys()))
        templates = all_npcs[npc_name]
        template = random.choice(templates)

        npc_key = f"{subloc}:{npc_name}:lvl{self._get_highest_unlocked_zone()}"
        if npc_key not in self.npc_pois:
            all_pois = [(pos, t) for pos, t in find_poi(self.world, exclude_pos=p.pos)
                        if t != "dragon_lair" and p.level >= ZONE_LEVEL_REQUIREMENTS.get(t, 1)]
            chosen = random.sample(all_pois, min(2, len(all_pois)))
            self.npc_pois[npc_key] = [(pos, coord_label(pos), loc_type) for pos, loc_type in chosen]

        npc_poi_list = self.npc_pois[npc_key]
        if npc_poi_list:
            poi_pos, coord, loc_type = random.choice(npc_poi_list)
            line = template.format(
                coord=styled(coord, C.BOLD, C.CYAN),
                loc_type=styled(loc_type, C.BOLD, C.YELLOW),
            )
        else:
            poi_pos, coord, loc_type = None, None, None
            line = template.format(coord="the far reaches", loc_type="dark place")

        npc_display = npc_name.replace("_", " ").title()
        print()
        self.print_sep()
        print(styled(f"  [{npc_display}]", C.BOLD, C.YELLOW))
        print()
        self.wrap_print(line, C.WHITE)
        if poi_pos and not self.world[poi_pos].get("revealed"):
            self.world[poi_pos]["revealed"] = True
            print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))
        elif poi_pos:
            print(styled("  [This location is already on your map.]", C.DIM))

        next_zone = self._get_next_locked_zone()
        if next_zone:
            req_lvl = ZONE_LEVEL_REQUIREMENTS[next_zone]
            print()
            self.wrap_print(
                f"\"I know of darker places... but you haven't the stature for them. "
                f"Come back when you're stronger. (Reach level {req_lvl} to unlock {next_zone} hints)\"",
                C.DIM
            )
        self.print_sep()
        print()

    def cmd_stats(self, _args):
        p = self.player
        print()
        print(styled("  CHARACTER", C.BOLD, C.YELLOW))
        print(styled("  ---------", C.DIM))
        bar_len = 20
        hp_pct = p.hp / p.max_hp
        filled = int(bar_len * hp_pct)
        bar = styled("#" * filled, C.RED) + styled("-" * (bar_len - filled), C.DIM)
        mana_pct = p.mana / p.max_mana if p.max_mana > 0 else 0
        mana_filled = int(bar_len * mana_pct)
        mana_bar = styled("#" * mana_filled, C.BLUE) + styled("-" * (bar_len - mana_filled), C.DIM)
        print(f"  HP:      {p.hp}/{p.max_hp} [{bar}]")
        print(f"  Mana:    {p.mana}/{p.max_mana} [{mana_bar}]")
        print(f"  Attack:  {styled(str(p.attack), C.RED)}")
        print(f"  Defense: {styled(str(p.armor_value), C.BLUE)}")
        print(f"  Dodge:   {styled(str(p.dodge_chance) + '%', C.GREEN)}")
        print(f"  Gold:    {styled(str(p.gold), C.YELLOW)}")
        print(f"  Level:   {p.level}  (XP: {p.xp}/{p.xp_to_next})")
        print(f"  Weapon:  {styled(p.weapon_name(), C.CYAN)}")
        print(f"  Armor:   {styled(p.armor_name(), C.CYAN)}")
        if p.spells:
            spell_names = ", ".join(SPELLS[s]["name"] for s in p.spells if s in SPELLS)
            print(f"  Spells:  {styled(spell_names, C.MAGENTA)}")
        if p.has_map:
            print(f"  Map:     {styled('Full map unlocked', C.GREEN)}")
        print()

    def cmd_inventory(self, _args):
        p = self.player
        print()
        print(styled("  INVENTORY", C.BOLD, C.YELLOW))
        print(styled("  ---------", C.DIM))
        print(f"  Gold: {styled(str(p.gold), C.YELLOW)}")

        def _list_section(title, items, catalog):
            if items:
                print(f"\n  {styled(title, C.BOLD)}")
                counts = Counter(items)
                for key, count in counts.items():
                    info = catalog.get(key, {})
                    name = info.get("name", key)
                    extra = ""
                    if "attack" in info:
                        extra = f" (ATK +{info['attack']})"
                    elif "armor" in info:
                        extra = f" (DEF +{info['armor']}, Dodge {info.get('dodge', 0)}%)"
                    elif "heal" in info:
                        extra = f" (Heal {info['heal']})"
                    equipped = ""
                    if key == p.weapon:
                        equipped = styled(" [equipped]", C.GREEN)
                    elif key == p.armor_equipped:
                        equipped = styled(" [equipped]", C.GREEN)
                    qty = f" x{count}" if count > 1 else ""
                    print(f"    {name}{extra}{styled(qty, C.YELLOW)}{equipped}")

        _list_section("Weapons", p.weapons, WEAPONS)
        _list_section("Armor", p.armors, ARMORS)
        _list_section("Consumables", p.consumables, CONSUMABLES)
        _list_section("Misc", p.misc, MISC_ITEMS)

        if p.spells:
            print(f"\n  {styled('Spells', C.BOLD)}")
            for spell_key in p.spells:
                info = SPELLS.get(spell_key, {})
                name = info.get("name", spell_key)
                mana_cost = info.get("mana", 0)
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
                print(f"    {name} ({detail_str}, {mana_cost} mana)")
        print()

    def cmd_cd(self, args):
        if not args:
            print(styled("  Usage: cd {cell|location|subloc|..}", C.RED))
            return

        target = args[0].lower()
        p = self.player

        if target == "..":
            if p.subloc:
                p.subloc = None
                print(styled(f"  You return to the {p.inside}.", C.YELLOW))
                self.cmd_look([])
            elif p.inside:
                p.inside = None
                print(styled(f"  You step outside at {self.pos_label()}.", C.YELLOW))
            else:
                print(styled("  You are already on the world map.", C.DIM))
            return

        if p.inside:
            subs = SUBLOCS.get(p.inside, [])
            resolved = target if target in subs else None
            if resolved is None:
                matches = [s for s in subs if s.startswith(target)]
                if len(matches) == 1:
                    resolved = matches[0]
                elif len(matches) > 1:
                    print(styled(f"  Ambiguous — did you mean: {', '.join(matches)}?", C.RED))
                    return
            if resolved:
                p.subloc = resolved
                self.cmd_look([])
                if resolved == "merchant" and self.current_tile()["type"] in ("village", "capital", "port"):
                    self._show_merchant()
                return
            if target == p.inside or p.inside.startswith(target):
                p.subloc = None
                self.cmd_look([])
                return

        tile = self.current_tile()
        if not p.inside and tile["type"] not in ("plains", "water"):
            loc_type = tile["type"]
            if loc_type.startswith(target):
                p.inside = loc_type
                p.subloc = None
                tile["visited"] = True
                self.cmd_look([])
                return

        cell = args[0].upper()
        if len(cell) >= 2:
            col = cell[0]
            try:
                row = int(cell[1:])
            except ValueError:
                print(styled(f"  Unknown destination: {args[0]}", C.RED))
                return

            if col in COLS and row in ROWS:
                target_tile = self.world[(col, row)]
                if target_tile["type"] == "water":
                    print(styled("  You cannot travel across water.", C.BLUE))
                    return
                p.pos = (col, row)
                new_tile = self.current_tile()
                new_tile["visited"] = True
                t = new_tile["type"]
                if t not in ("plains", "water"):
                    p.inside = t
                    p.subloc = None
                    print()
                    print(styled(f"  You travel to {self.pos_label()} — {t.replace('_', ' ').title()}.", C.YELLOW))
                    self.cmd_look([])
                else:
                    p.inside = None
                    p.subloc = None
                    print()
                    print(styled(f"  You travel to {self.pos_label()}...", C.YELLOW))
                    self._describe_arrival(new_tile)
                return
            else:
                print(styled(f"  Invalid cell: {cell}. Use A-J and 1-10.", C.RED))
                return

        print(styled(f"  Unknown destination: {args[0]}", C.RED))

    def _describe_arrival(self, tile):
        t = tile["type"]
        if t == "plains":
            self.wrap_print(random.choice(DESC_PLAINS), C.DIM)
        else:
            descs = DESC_MAP.get(t, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            print(styled(f"\n  There is a {t} here. Use 'cd {t}' to enter.", C.YELLOW))
        print()

    def cmd_equip(self, args):
        if not args:
            print(styled("  Usage: equip {item_name}", C.RED))
            return
        p = self.player
        key = self._resolve_item_key(args, list(set(p.weapons + p.armors)))
        if key is None:
            key = "_".join(args).lower()
        if key in WEAPONS and key in p.weapons:
            p.weapon = key
            print(styled(f"  Equipped {WEAPONS[key]['name']}.", C.GREEN))
        elif key in ARMORS and key in p.armors:
            p.armor_equipped = key
            print(styled(f"  Equipped {ARMORS[key]['name']}.", C.GREEN))
        else:
            print(styled(f"  You don't have '{' '.join(args)}' or it cannot be equipped.", C.RED))

    def cmd_unequip(self, args):
        if not args:
            print(styled("  Usage: unequip weapon | unequip armor", C.RED))
            return
        target = args[0].lower()
        p = self.player
        if target in ("weapon", "w"):
            if p.weapon is None:
                print(styled("  You have no weapon equipped.", C.DIM))
            else:
                old = p.weapon_name()
                p.weapon = None
                print(styled(f"  Unequipped {old}. Fighting with bare fists.", C.YELLOW))
        elif target in ("armor", "a"):
            if p.armor_equipped is None:
                print(styled("  You have no armor equipped.", C.DIM))
            else:
                old = p.armor_name()
                p.armor_equipped = None
                print(styled(f"  Unequipped {old}. No armor.", C.YELLOW))
        else:
            print(styled("  Usage: unequip weapon | unequip armor", C.RED))

    def cmd_use(self, args):
        if not args:
            print(styled("  Usage: use {item_name}", C.RED))
            return
        p = self.player
        key = self._resolve_item_key(args, p.consumables)
        if key is None:
            key = "_".join(args).lower()
        if key in CONSUMABLES and key in p.consumables:
            info = CONSUMABLES[key]
            old_hp = p.hp
            p.heal(info["heal"])
            healed = p.hp - old_hp
            p.consumables.remove(key)
            print(styled(f"  Used {info['name']}. Restored {healed} HP. (HP: {p.hp}/{p.max_hp})", C.GREEN))
        else:
            print(styled(f"  You don't have '{' '.join(args)}' or it cannot be used.", C.RED))

    # -- merchant --

    def _show_merchant(self):
        tile = self.current_tile()
        stock = tile.get("merchant_stock", [])
        if not stock:
            print(styled("  The merchant has nothing left to sell.", C.DIM))
            return
        print()
        print(styled("  MERCHANT'S WARES", C.BOLD, C.YELLOW))
        print(styled("  ----------------", C.DIM))
        for key in stock:
            info = ALL_ITEMS.get(key, {})
            name = info.get("name", key)
            value = info.get("value", 0)
            extra = ""
            if "attack" in info:
                extra = f" (ATK +{info['attack']})"
            elif "armor" in info:
                extra = f" (DEF +{info['armor']}, Dodge {info.get('dodge', 0)}%)"
            elif "heal" in info:
                extra = f" (Heal {info['heal']})"
            print(f"    {name}{extra}  --  {styled(str(value) + ' gold', C.YELLOW)}")
        print()
        print(styled("  Use 'buy {item}' to purchase, 'sell {item}' to sell.", C.DIM))
        print()

    def _show_mage_spells(self):
        p = self.player
        available = {k: v for k, v in SPELLS.items() if v["source"] == "mage" and k not in p.spells}
        if not available:
            print(styled("  The mage has nothing more to teach you.", C.DIM))
            return
        print()
        print(styled("  MAGE'S SPELLS", C.BOLD, C.MAGENTA))
        print(styled("  -------------", C.DIM))
        for key, info in available.items():
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage']}")
            if "heal" in info:
                details.append(f"Heal {info['heal']}")
            if "shield" in info:
                details.append(f"Shield +{info['shield']}")
            detail_str = ", ".join(details)
            print(f"    {info['name']} ({detail_str}, {info['mana']} mana)  --  {styled(str(info['value']) + ' gold', C.YELLOW)}")
        print(f"\n  Spells known: {len(p.spells)}/{p.max_spells}")
        print(styled("  Use 'buy {spell}' to learn a spell.", C.DIM))
        print(styled(f"  Use 'train' to increase your spell capacity ({TRAIN_COST} gold).", C.DIM))
        print()

    def _show_warlock_spells(self):
        p = self.player
        available = {k: v for k, v in SPELLS.items() if v["source"] == "warlock" and k not in p.spells}
        if not available:
            print(styled("  The warlock has nothing more to teach you.", C.DIM))
            return
        print()
        print(styled("  WARLOCK'S DARK SPELLS", C.BOLD, C.RED))
        print(styled("  --------------------", C.DIM))
        for key, info in available.items():
            details = []
            if "damage" in info:
                details.append(f"DMG {info['damage']}")
            if "heal" in info:
                details.append(f"Heal {info['heal']}")
            if "weaken" in info:
                details.append(f"Weaken {int(info['weaken']*100)}%")
            detail_str = ", ".join(details)
            print(f"    {info['name']} ({detail_str}, {info['mana']} mana)  --  {styled(str(info['value']) + ' gold', C.YELLOW)}")
        print(f"\n  Spells known: {len(p.spells)}/{p.max_spells}")
        print(styled("  Use 'buy {spell}' to learn a dark spell.", C.DIM))
        print()

    def cmd_buy(self, args):
        p = self.player

        if not args:
            if p.subloc == "courtyard" and p.inside in ("castle", "capital"):
                self._show_mage_spells()
                return
            elif p.subloc == "tower" and p.inside == "castle":
                self._show_warlock_spells()
                return
            elif p.subloc == "dock" and p.inside == "port":
                if p.has_map:
                    print(styled("  You already own the full map.", C.DIM))
                else:
                    print(styled(f"  The explorer sells a full map for {MAP_COST} gold. Type 'buy map'.", C.CYAN))
                return
            elif p.subloc == "merchant":
                self._show_merchant()
                return
            print(styled("  Usage: buy {item_name}", C.RED))
            return

        # Buy map from explorer at dock
        if p.subloc == "dock" and p.inside == "port":
            target = "_".join(args).lower()
            if target == "map":
                if p.has_map:
                    print(styled("  You already own the full map.", C.DIM))
                    return
                if p.gold < MAP_COST:
                    print(styled(f"  Not enough gold. The map costs {MAP_COST}, you have {p.gold}.", C.RED))
                    return
                p.gold -= MAP_COST
                p.has_map = True
                for pos, tile in self.world.items():
                    if tile["type"] not in ("plains", "water"):
                        tile["revealed"] = True
                print(styled(f"  Purchased the full map for {MAP_COST} gold! All locations revealed!", C.GREEN, C.BOLD))
                return
            else:
                print(styled("  The explorer only sells maps. Type 'buy map'.", C.RED))
                return

        # Buy spells from mage in courtyard
        if p.subloc == "courtyard" and p.inside in ("castle", "capital"):
            spell_keys = [k for k, v in SPELLS.items() if v["source"] == "mage" and k not in p.spells]
            key = self._resolve_item_key(args, spell_keys)
            if key is None:
                key = "_".join(args).lower()
            if key not in SPELLS or SPELLS[key]["source"] != "mage":
                self._show_mage_spells()
                return
            if key in p.spells:
                print(styled(f"  You already know {SPELLS[key]['name']}.", C.DIM))
                return
            if len(p.spells) >= p.max_spells:
                print(styled(f"  You cannot learn more than {p.max_spells} spells. Use 'train' to expand your capacity.", C.RED))
                return
            cost = SPELLS[key]["value"]
            if p.gold < cost:
                print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
                return
            p.gold -= cost
            p.spells.append(key)
            print(styled(f"  Learned {SPELLS[key]['name']}! ({len(p.spells)}/{p.max_spells} spells) (Gold: {p.gold})", C.MAGENTA, C.BOLD))
            return

        # Buy spells from warlock in castle tower
        if p.subloc == "tower" and p.inside == "castle":
            spell_keys = [k for k, v in SPELLS.items() if v["source"] == "warlock" and k not in p.spells]
            key = self._resolve_item_key(args, spell_keys)
            if key is None:
                key = "_".join(args).lower()
            if key not in SPELLS or SPELLS[key]["source"] != "warlock":
                self._show_warlock_spells()
                return
            if key in p.spells:
                print(styled(f"  You already know {SPELLS[key]['name']}.", C.DIM))
                return
            if len(p.spells) >= p.max_spells:
                print(styled(f"  You cannot learn more than {p.max_spells} spells. Use 'train' to expand your capacity.", C.RED))
                return
            cost = SPELLS[key]["value"]
            if p.gold < cost:
                print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
                return
            p.gold -= cost
            p.spells.append(key)
            print(styled(f"  Learned {SPELLS[key]['name']}! ({len(p.spells)}/{p.max_spells} spells) (Gold: {p.gold})", C.RED, C.BOLD))
            return

        # Standard merchant buying
        if p.subloc != "merchant":
            print(styled("  You need to be at a merchant, mage, warlock, or explorer.", C.RED))
            return

        tile = self.current_tile()
        stock = tile.get("merchant_stock", [])
        key = self._resolve_item_key(args, stock)
        if key is None:
            key = "_".join(args).lower()
        if key not in stock:
            print(styled(f"  The merchant doesn't have '{' '.join(args)}'.", C.RED))
            return
        info = ALL_ITEMS.get(key, {})
        cost = info.get("value", 0)
        if p.gold < cost:
            print(styled(f"  Not enough gold. You need {cost}, you have {p.gold}.", C.RED))
            return
        p.gold -= cost
        p.add_item(key)
        stock.remove(key)
        print(styled(f"  Purchased {info['name']} for {cost} gold. (Gold: {p.gold})", C.GREEN))

    def cmd_sell(self, args):
        if not args:
            print(styled("  Usage: sell {item_name}", C.RED))
            return
        p = self.player
        if p.subloc != "merchant":
            print(styled("  You need to be at a merchant to sell items.", C.RED))
            return
        all_player_items = p.weapons + p.armors + p.consumables + p.misc
        key = self._resolve_item_key(args, all_player_items)
        if key is None:
            key = "_".join(args).lower()
        if not p.has_item(key):
            print(styled(f"  You don't have '{' '.join(args)}'.", C.RED))
            return
        if key == p.weapon:
            print(styled("  Unequip your weapon first (equip a different one).", C.RED))
            return
        if key == p.armor_equipped:
            print(styled("  Unequip your armor first (equip a different one).", C.RED))
            return
        info = ALL_ITEMS.get(key, {})
        sell_price = max(1, info.get("value", 1) // 2)
        p.remove_item(key)
        p.gold += sell_price
        print(styled(f"  Sold {info.get('name', key)} for {sell_price} gold. (Gold: {p.gold})", C.GREEN))

    def cmd_train(self, _args):
        p = self.player
        if not (p.subloc == "courtyard" and p.inside in ("castle", "capital")):
            print(styled("  You must be at the mage's courtyard to train.", C.RED))
            return
        if p.max_spells >= MAX_SPELLS_LIMIT:
            print(styled(f"  You have reached the maximum spell capacity ({MAX_SPELLS_LIMIT}).", C.DIM))
            return
        if p.gold < TRAIN_COST:
            print(styled(f"  Not enough gold. Training costs {TRAIN_COST} gold, you have {p.gold}.", C.RED))
            return
        p.gold -= TRAIN_COST
        p.max_spells += 1
        print(styled("  The mage guides you through rigorous arcane exercises...", C.MAGENTA))
        print(styled(f"  Your mind expands. You can now memorise {p.max_spells} spells. (Gold: {p.gold})", C.MAGENTA, C.BOLD))

    # -- combat --

    def cmd_fight(self, _args):
        p = self.player
        tile = self.current_tile()

        if (p.inside == "dragon_lair" or tile["type"] == "dragon_lair") and p.subloc == "nest":
            fight_dragon(p, self.world, self.print_sep, self.pos_label)
            return

        fight_enemy(p, tile, self.print_sep, self.pos_label)

    # -- search / loot --

    def cmd_search(self, _args):
        p = self.player
        tile = self.current_tile()

        if not p.inside:
            print(styled("  Nothing to search here in the open.", C.DIM))
            return

        # Castle treasure room: requires Old Key
        if p.subloc == "treasure_room" and p.inside == "castle":
            if self.world[p.pos].get("castle_treasure_opened"):
                print(styled("  The chest lies open and empty. You've already claimed the treasure.", C.DIM))
                return
            if "old_key" not in p.misc:
                print()
                self.print_sep()
                self.wrap_print(
                    "A massive iron-bound chest sits in the centre of the vault. "
                    "Its lock is ancient but sturdy — engraved with worn symbols. "
                    "You need a key to open it.", C.WHITE)
                print(styled("  [You need an Old Key to open this chest.]", C.RED))
                self.print_sep()
                print()
                return
            p.misc.remove("old_key")
            self.world[p.pos]["castle_treasure_opened"] = True
            print()
            self.print_sep()
            self.wrap_print(
                "You insert the Old Key into the ancient lock. It turns with a "
                "grinding screech. The chest lid creaks open, revealing a trove of riches!", C.WHITE)
            print()
            treasure_gold = random.randint(80, 200)
            p.gold += treasure_gold
            print(styled(f"  Found {treasure_gold} gold!", C.YELLOW))
            good_loot = random.choice(["steel_sword", "war_hammer", "dark_blade", "plate_armor", "dark_plate", "silver_longsword"])
            info = ALL_ITEMS[good_loot]
            p.add_item(good_loot)
            print(styled(f"  Found: {info['name']}!", C.GREEN, C.BOLD))
            bonus = random.choice(list(CONSUMABLES.keys()))
            bonus_info = CONSUMABLES[bonus]
            p.add_item(bonus)
            print(styled(f"  Found: {bonus_info['name']}!", C.GREEN))
            print()
            print(styled("  [The Old Key crumbles to dust after use.]", C.DIM))
            self.print_sep()
            print()
            return

        if not tile.get("loot_available"):
            print(styled("  You've already searched this place thoroughly. Nothing remains.", C.DIM))
            return

        searchable = {"treasure_room", "crypt", "altar", "ruins", "clearing",
                      "throne_room", "great_hall", "tower", "dungeon_cells", "hoard"}
        if p.subloc and p.subloc in searchable:
            found_gold = random.randint(5, 30 + p.level * 5)
            p.gold += found_gold
            print(styled(f"  You search carefully... Found {found_gold} gold!", C.YELLOW))
            if random.random() < 0.5:
                loot_pool = list(CONSUMABLES.keys()) + list(MISC_ITEMS.keys())
                if random.random() < 0.2:
                    loot_pool += list(WEAPONS.keys()) + list(ARMORS.keys())
                item_key = random.choice(loot_pool)
                info = ALL_ITEMS[item_key]
                p.add_item(item_key)
                print(styled(f"  Found: {info['name']}!", C.GREEN))
            tile["loot_available"] = False
        else:
            print(styled("  You look around but find nothing of interest here.", C.DIM))

    def cmd_sleep(self, _args):
        p = self.player
        if p.subloc != "tavern":
            print(styled("  You need to be in a tavern to sleep.", C.RED))
            return
        if p.gold < SLEEP_COST:
            print(styled(f"  The barkeep shakes his head. 'Room's {SLEEP_COST} gold. You don't have enough.'", C.RED))
            return
        p.gold -= SLEEP_COST
        old_hp = p.hp
        p.hp = p.max_hp
        healed = p.hp - old_hp
        old_mana = p.mana
        p.mana = p.max_mana
        mana_restored = p.mana - old_mana
        xp_gained = random.randint(3, 8)
        leveled = p.gain_xp(xp_gained)
        for pos, tile in self.world.items():
            if tile.get("merchant_stock") is not None:
                tile["merchant_stock"] = generate_merchant_stock()
        print()
        self.print_sep()
        print(styled("  You rent a room and collapse onto a straw mattress.", C.WHITE))
        print(styled("  Hours pass. The sounds of the tavern fade into silence.", C.DIM))
        print()
        print(styled(f"  Restored {healed} HP. HP: {p.hp}/{p.max_hp}", C.GREEN))
        print(styled(f"  Restored {mana_restored} Mana. Mana: {p.mana}/{p.max_mana}", C.BLUE))
        print(styled(f"  Gained {xp_gained} XP. (Dreams of past battles...)", C.CYAN))
        print(styled(f"  Paid {SLEEP_COST} gold. (Gold: {p.gold})", C.YELLOW))
        print(styled("  Merchant stocks have been refreshed across the land.", C.DIM))
        if leveled:
            print(styled(f"  LEVEL UP! You are now level {p.level}!", C.BOLD, C.CYAN))
        self.print_sep()
        print()

    def cmd_quit(self, _args):
        print()
        print(styled("  The darkness closes in. Your journey ends here.", C.DIM))
        print(styled("  Farewell, wanderer.", C.BOLD))
        print()
        self.running = False

    def cmd_cheat(self, _args):
        p = self.player
        while p.level < 20:
            p.level += 1
            p.max_hp += 10
            p.base_attack += 1
            p.max_mana += 10
        p.hp = p.max_hp
        p.mana = p.max_mana
        p.xp = 0
        p.xp_to_next = int(50 * (1.5 ** 19))
        p.gold = 99999
        p.has_map = True
        for pos, tile in self.world.items():
            if tile["type"] not in ("plains", "water"):
                tile["revealed"] = True
        for key in WEAPONS:
            if key not in p.weapons:
                p.weapons.append(key)
        for key in ARMORS:
            if key not in p.armors:
                p.armors.append(key)
        for key in CONSUMABLES:
            for _ in range(5):
                p.consumables.append(key)
        for key in MISC_ITEMS:
            if key not in p.misc:
                p.misc.append(key)
        all_spell_keys = list(SPELLS.keys())
        p.max_spells = MAX_SPELLS_LIMIT
        p.spells = all_spell_keys[:MAX_SPELLS_LIMIT]
        p.weapon = "dragon_slayer_blade"
        p.armor_equipped = "dark_plate"
        print()
        self.print_sep()
        print(styled("  [CHEAT MODE ACTIVATED]", C.BOLD, C.RED))
        print(styled(f"  Level: {p.level}  |  HP: {p.hp}/{p.max_hp}  |  Mana: {p.mana}/{p.max_mana}", C.YELLOW))
        print(styled(f"  Gold: {p.gold}  |  ATK: {p.attack}  |  DEF: {p.armor_value}", C.YELLOW))
        print(styled("  All weapons, armors, items, and spells unlocked.", C.GREEN))
        print(styled("  Full map revealed.", C.GREEN))
        self.print_sep()
        print()

    # -- command dispatch --

    def _resolve_item_key(self, args, catalog_keys):
        if not args:
            return None
        partial = "_".join(args).lower()
        all_lookup = {}
        all_lookup.update(ALL_ITEMS)
        all_lookup.update(SPELLS)
        if partial in catalog_keys:
            return partial
        matches = [k for k in catalog_keys if k.startswith(partial)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = [all_lookup.get(k, {}).get("name", k) for k in matches]
            print(styled(f"  Multiple matches: {', '.join(names)}", C.YELLOW))
            return None
        matches = [k for k in catalog_keys if partial in k]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = [all_lookup.get(k, {}).get("name", k) for k in matches]
            print(styled(f"  Multiple matches: {', '.join(names)}", C.YELLOW))
            return None
        return None

    def _tick_respawn(self):
        self.action_count += 1
        if self.action_count >= self.respawn_interval:
            self.action_count = 0
            for pos, tile in self.world.items():
                if tile.get("enemies_cleared"):
                    tile["enemies_cleared"] = False
                if not tile.get("loot_available"):
                    tile["loot_available"] = True

    def dispatch(self, raw_input):
        parts = raw_input.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        shortcuts = {
            "h": "help", "m": "map", "l": "look", "t": "talk",
            "s": "search", "f": "fight", "i": "inventory",
            "e": "equip", "u": "use", "b": "buy", "q": "quit",
        }
        cmd = shortcuts.get(cmd, cmd)

        commands = {
            "help":      self.cmd_help,
            "map":       self.cmd_map,
            "look":      self.cmd_look,
            "talk":      self.cmd_talk,
            "stats":     self.cmd_stats,
            "inventory": self.cmd_inventory,
            "inv":       self.cmd_inventory,
            "cd":        self.cmd_cd,
            "equip":     self.cmd_equip,
            "unequip":   self.cmd_unequip,
            "use":       self.cmd_use,
            "buy":       self.cmd_buy,
            "sell":      self.cmd_sell,
            "fight":     self.cmd_fight,
            "search":    self.cmd_search,
            "sleep":     self.cmd_sleep,
            "train":     self.cmd_train,
            "cheat":     self.cmd_cheat,
            "quit":      self.cmd_quit,
            "exit":      self.cmd_quit,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
            self._tick_respawn()
        else:
            print(styled(f"  Unknown command: {cmd}. Type 'help' for commands.", C.RED))

    # -- main loop --

    def run(self):
        set_gothic_font()
        show_intro()
        print("\033[2J\033[H", end="", flush=True)

        print()
        print(styled(r"""
   _____ _  _ ___    ___  ___  ___ ___ ___ _____    ___  ___   ___  _     ___
  |_   _| || | __|  | __|/ _ \| _ \ __/ __|_   _|  | __|/ _ \ / _ \| |   / __|
    | | | __ | _|   | _|| (_) |   / _|\__ \ | |    | _|| (_) | (_) | |__ \__ \
    |_| |_||_|___|  |_|  \___/|_|_\___|___/ |_|    |_|  \___/ \___/|____|___/
        """, C.BOLD, C.RED))

        print(styled("    Version 1.0.5", C.DIM))
        print(styled("    A Dark Medieval Gothic Exploration", C.DIM))
        print()
        print(styled("    You awaken in a grey, desolate land. Fog clings to the earth.", C.WHITE))
        print(styled("    The sky is iron. Somewhere, a bell tolls.", C.WHITE))
        print(styled("    Type 'help' for commands. Type 'map' to see the world.", C.DIM))
        print()
        self.print_sep()
        print()

        while self.running:
            loc = self.location_label()
            prompt = styled(f"  [{loc}]", C.CYAN) + styled(" > ", C.BOLD)
            try:
                raw = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                self.cmd_quit([])
                break

            self.dispatch(raw)

            if self.player.hp <= 0:
                self.player.hp = self.player.max_hp // 2
                gold_lost = self.player.gold // 3
                self.player.gold -= gold_lost
                self.player.pos = CAPITAL_POS
                self.player.inside = None
                self.player.subloc = None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
