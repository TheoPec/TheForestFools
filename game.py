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
import io
import textwrap
from collections import Counter
from contextlib import redirect_stdout

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
    MAP_COST, TRAIN_COST, SLEEP_COST,
    MAX_SPELLS_LIMIT, RESPAWN_INTERVAL,
    ZONE_LEVEL_REQUIREMENTS, ZONE_TIERS, CAPITAL_POS,
)
from data.character_options import RACES, GENDERS, CLASSES, DEFAULT_CHARACTER
from data.fixed_maps import FIXED_MAPS, REGIONS, REGION_ALIASES, REGION_BOUNDS, REGION_ENTRANCES, REGION_PASSES
from data.loot_tables import random_treasure_equipment, roll_search_drop

# --- Engine imports ---
from engine.terminal import C, styled, set_gothic_font, strip_ansi
from engine.player import Player
from engine.world import (
    generate_worlds, generate_merchant_stock, draw_map,
    find_poi, coord_label, column_range_label, parse_coord, world_axes,
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
        self.worlds = generate_worlds()
        self.current_world_key = "mosswake"
        self.map_view_key = self.current_world_key
        self.map_region_filter = None
        self.unlocked_regions = {"crownvale"}
        self.world = self.worlds[self.current_world_key]
        self.player = Player()
        self.player.pos = FIXED_MAPS[self.current_world_key]["start_pos"]
        self.current_tile()["visited"] = True
        self.current_tile()["revealed"] = True
        self.running = True
        self.dragon_world_key = "ashenreach"
        dragon_world = self.worlds.get(self.dragon_world_key, {})
        self.dragon_lair_pos = next((pos for pos, t in dragon_world.items() if t["type"] == "dragon_lair"), None)
        self.action_count = 0
        self.respawn_interval = RESPAWN_INTERVAL
        self.npc_pois: dict = {}
        self.active_combat = None
        self.message_log: list[dict] = []
        self.max_message_log = 300
        self.show_walkable_overlay = False
        self.graphical_mode = False

    # -- helpers --

    def current_tile(self):
        return self.world[self.player.pos]

    def current_world_name(self):
        return FIXED_MAPS.get(self.current_world_key, {}).get("name", self.current_world_key.title())

    def tile_display_name(self, tile):
        fallback = TILE_NAMES.get(tile["type"], tile["type"].replace("_", " ").title())
        return tile.get("name") or fallback

    def world_cols_rows(self, map_key=None):
        map_key = map_key or self.current_world_key
        spec = FIXED_MAPS.get(map_key, {})
        cols = list(spec.get("cols") or world_axes(self.worlds[map_key])[0])
        rows = list(spec.get("row_numbers") or world_axes(self.worlds[map_key])[1])
        return cols, rows

    def map_view_axes(self):
        if self.map_region_filter and self.map_view_key == "continent":
            bounds = REGION_BOUNDS[self.map_region_filter]
            return list(bounds["cols"]), list(bounds["rows"])
        return self.world_cols_rows(self.map_view_key)

    def is_region_unlocked(self, region_key):
        pass_key = REGION_PASSES.get(region_key)
        return region_key in self.unlocked_regions or pass_key is None or self._has_misc(pass_key)

    def is_tile_walkable(self, tile):
        if tile["type"] == "water":
            return False
        region = tile.get("region")
        if region and not self.is_region_unlocked(region):
            return False
        return True

    def map_view_world(self):
        return self.worlds.get(self.map_view_key, self.world)

    def map_view_name(self):
        map_name = FIXED_MAPS.get(self.map_view_key, {}).get("name", self.map_view_key.title())
        if self.map_region_filter:
            return f"{map_name} / {REGIONS.get(self.map_region_filter, self.map_region_filter.title())}"
        return map_name

    def switch_world(self, map_key, pos=None):
        if map_key not in self.worlds:
            return False
        self.current_world_key = map_key
        self.world = self.worlds[map_key]
        self.map_view_key = map_key
        self.map_region_filter = None
        self.player.pos = pos or FIXED_MAPS[map_key].get("arrival_pos") or FIXED_MAPS[map_key]["start_pos"]
        self.player.inside = None
        self.player.subloc = None
        self.current_tile()["visited"] = True
        return True

    def switch_region(self, region_key):
        if region_key not in REGIONS:
            return False
        if not self.is_region_unlocked(region_key):
            pass_key = REGION_PASSES.get(region_key)
            pass_name = MISC_ITEMS.get(pass_key, {}).get("name", "regional pass")
            print(styled(f"  You need the {pass_name} to enter {REGIONS[region_key]}.", C.RED))
            return False
        if self.current_world_key == "mosswake":
            print(styled("  You need to reach the mainland before crossing regional borders.", C.RED))
            return False
        self.switch_world(region_key, REGION_ENTRANCES[region_key])
        print(styled(f"  You travel into {REGIONS[region_key]}.", C.YELLOW))
        self.cmd_look([])
        return True

    def slime_king_defeated(self):
        for tile in self.worlds["mosswake"].values():
            if tile.get("boss") == "slime_king":
                return bool(tile.get("boss_defeated"))
        return False

    def _find_boss_tile(self, world_key, boss_key):
        for pos, tile in self.worlds.get(world_key, {}).items():
            if tile.get("boss") == boss_key:
                return pos, tile
        return None, None

    def _boss_defeated(self, world_key, boss_key):
        _, tile = self._find_boss_tile(world_key, boss_key)
        return bool(tile and tile.get("boss_defeated"))

    def _reveal_location(self, world_key, pos):
        tile = self.worlds.get(world_key, {}).get(pos)
        if tile and not tile.get("revealed"):
            tile["revealed"] = True
            print(styled("  [A new location has been revealed on your map!]", C.BOLD, C.CYAN))

    def _grant_misc_once(self, item_key):
        if self._has_misc(item_key):
            return False
        self.player.misc.append(item_key)
        item_name = MISC_ITEMS.get(item_key, {}).get("name", item_key.replace("_", " ").title())
        print()
        print(styled(f"  Received: {item_name}.", C.GREEN, C.BOLD))
        return True

    def _has_misc(self, item_key):
        if item_key in self.player.misc:
            return True
        return False

    def configure_character(self, race=None, gender=None, character_class=None):
        """Apply character creation choices to the player."""
        race = race or DEFAULT_CHARACTER["race"]
        gender = gender or DEFAULT_CHARACTER["gender"]
        character_class = character_class or DEFAULT_CHARACTER["class"]
        if race not in RACES:
            race = DEFAULT_CHARACTER["race"]
        if gender not in GENDERS:
            gender = DEFAULT_CHARACTER["gender"]
        if character_class not in CLASSES:
            character_class = DEFAULT_CHARACTER["class"]

        p = self.player
        p.race = race
        p.gender = gender
        p.character_class = character_class

        def apply_bonuses(bonuses):
            p.max_hp = max(20, p.max_hp + bonuses.get("max_hp", 0))
            p.max_mana = max(0, p.max_mana + bonuses.get("max_mana", 0))
            p.base_attack = max(1, p.base_attack + bonuses.get("base_attack", 0))
            p.base_armor = max(0, p.base_armor + bonuses.get("base_armor", 0))
            p.magic_power = max(0, p.magic_power + bonuses.get("magic_power", 0))

        apply_bonuses(RACES[race].get("bonuses", {}))
        apply_bonuses(CLASSES[character_class].get("bonuses", {}))

        starting_items = CLASSES[character_class].get("starting_items", {})
        for key in starting_items.get("weapons", []):
            if key in WEAPONS and key not in p.weapons:
                p.weapons.append(key)
                p.weapon = key
        for key in starting_items.get("armors", []):
            if key in ARMORS and key not in p.armors:
                p.armors.append(key)
                p.armor_equipped = key
        for key in starting_items.get("consumables", []):
            if key in CONSUMABLES:
                p.consumables.append(key)
        for key in starting_items.get("spells", []):
            if key in SPELLS and key not in p.spells and len(p.spells) < p.max_spells:
                p.spells.append(key)

        p.hp = p.max_hp
        p.mana = p.max_mana
        return self.get_ui_state()

    def print_sep(self):
        print(styled("=" * 60, C.DIM))

    def wrap_print(self, text, color=C.WHITE):
        for line in textwrap.wrap(text, width=70):
            print(styled("  " + line, color))

    def pos_label(self):
        return coord_label(self.player.pos)

    def location_label(self):
        parts = [self.current_world_name(), self.pos_label()]
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
            ("walkable / paths", "Toggle color overlay for reachable cells."),
            ("zoom {map|region}", "Change map view. e.g. zoom island, zoom crownvale."),
            ("cd {cell}",        "Travel to a map cell.  e.g. cd B4"),
            ("cd {region}",      "Travel to a region if you have its pass."),
            ("cd {location}",    "Enter a location.      e.g. cd village"),
            ("cd {subloc}",      "Enter a sub-location.  e.g. cd tavern"),
            ("cd ..",            "Go back / leave current location."),
            ("sail",             "Travel by boat from an authorized port."),
            ("look",             "Describe the current location."),
            ("talk",             "Talk to someone here."),
            ("journal",          "Show main quest progress."),
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
            ("SHORTCUTS",        "h=help m=map l=look t=talk j=journal s=search"),
            ("",                 "f=fight i=inventory e=equip u=use b=buy q=quit"),
            ("", ""),
            ("TIP",              "Type partial item names (e.g. 'sell sm' for Small Potion)."),
        ]
        for cmd, desc in cmds:
            print(f"  {styled(cmd.ljust(20), C.CYAN)} {styled(desc, C.DIM)}")
        print()

    def cmd_map(self, _args):
        if self.graphical_mode:
            print(styled(f"  Map panel updated: {self.map_view_name()}.", C.CYAN))
            if FIXED_MAPS.get(self.map_view_key, {}).get("overview_only"):
                print(styled("  This is a world overview. Use region zooms for playable grids.", C.DIM))
            return
        if FIXED_MAPS.get(self.map_view_key, {}).get("overview_only"):
            print(styled(f"  {self.map_view_name()} is shown as a world overview in the map panel.", C.CYAN))
            print(styled("  Use 'zoom crownvale', 'zoom greenmarch', 'zoom scalefen' or 'zoom ashenreach' for playable grids.", C.DIM))
            return
        player_pos = self.player.pos if self.map_view_key == self.current_world_key else None
        cols, rows = self.map_view_axes()
        draw_map(
            self.map_view_world(),
            player_pos,
            title=self.map_view_name(),
            region_filter=self.map_region_filter,
            cols=cols,
            rows=rows,
            show_all=self.player.has_map,
        )

    def cmd_walkable(self, args):
        if args:
            choice = args[0].lower()
            if choice in ("on", "true", "1"):
                self.show_walkable_overlay = True
            elif choice in ("off", "false", "0"):
                self.show_walkable_overlay = False
            else:
                print(styled("  Usage: walkable [on|off]", C.RED))
                return
        else:
            self.show_walkable_overlay = not self.show_walkable_overlay

        state = "ON" if self.show_walkable_overlay else "OFF"
        print(styled(f"  Walkable overlay: {state}.", C.CYAN))

    def cmd_zoom(self, args):
        if not args:
            print(styled("  Usage: zoom island|continent|current|crownvale|greenmarch|scalefen|ashenreach", C.RED))
            return

        target = "_".join(args).lower()
        target = REGION_ALIASES.get(target, target)
        aliases = {
            "island": ("mosswake", None),
            "mosswake": ("mosswake", None),
            "mosswake_isle": ("mosswake", None),
            "continent": ("continent", None),
            "mainland": ("continent", None),
            "elarion": ("continent", None),
            "current": (self.current_world_key, None),
        }
        if target in REGIONS:
            aliases[target] = (target, None)

        if target not in aliases:
            print(styled(f"  Unknown zoom target: {target}.", C.RED))
            return

        self.map_view_key, self.map_region_filter = aliases[target]
        print(styled(f"  Map view: {self.map_view_name()}.", C.CYAN))
        self.cmd_map([])

    def cmd_look(self, _args):
        tile = self.current_tile()
        print()
        self.print_sep()

        if self.player.subloc:
            descs = DESC_SUBLOCS.get(self.player.subloc, ["You see nothing remarkable."])
            self.wrap_print(random.choice(descs), C.WHITE)
            if (
                self.current_world_key == "mosswake"
                and self.player.inside == "village"
                and self.player.subloc == "town_hall"
            ):
                print()
                print(styled("  Mayor Aldren is here. Type 'talk' to speak.", C.YELLOW))
            if self.current_world_key == "crownvale" and self.player.inside == "capital" and self.player.subloc == "throne_room":
                print()
                print(styled("  King Rowen studies a war map. Type 'talk' to speak.", C.YELLOW))
            if self.current_world_key == "greenmarch" and self.player.inside == "village" and self.player.subloc == "town_hall":
                print()
                print(styled("  Elder Maelis waits beside leaf-marked maps. Type 'talk' to speak.", C.YELLOW))
            if self.current_world_key == "scalefen" and self.player.inside == "village" and self.player.subloc == "town_hall":
                print()
                print(styled("  Matriarch Sytha watches the marsh paths. Type 'talk' to speak.", C.YELLOW))
            if (
                self.current_world_key == "ashenreach"
                and self.player.inside == "cave"
                and self.player.subloc == "entrance"
                and self.current_tile().get("id") == "highpass"
            ):
                print()
                print(styled("  A wounded scout guards a broken waystone. Type 'talk' to speak.", C.YELLOW))
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
                print(styled(f"  {self.tile_display_name(tile)} is here. You can enter: cd {tile['type']}", C.YELLOW))

        self.print_sep()
        print()

    def cmd_talk(self, _args):
        p = self.player
        subloc = p.subloc

        if self.current_world_key == "mosswake" and p.inside == "village" and p.subloc == "town_hall":
            self.talk_mosswake_mayor()
            return

        if self.current_world_key == "crownvale" and p.inside == "capital" and p.subloc == "throne_room":
            self.talk_crownvale_king()
            return

        if self.current_world_key == "greenmarch" and p.inside == "village" and p.subloc == "town_hall":
            self.talk_greenmarch_elder()
            return

        if self.current_world_key == "scalefen" and p.inside == "village" and p.subloc == "town_hall":
            self.talk_scalefen_matriarch()
            return

        if (
            self.current_world_key == "ashenreach"
            and p.inside == "cave"
            and p.subloc == "entrance"
            and self.current_tile().get("id") == "highpass"
        ):
            self.talk_ashenreach_scout()
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

    def talk_mosswake_mayor(self):
        p = self.player
        print()
        self.print_sep()
        print(styled("  [Mayor Aldren]", C.BOLD, C.YELLOW))
        print()
        if "harbor_pass" in p.misc:
            self.wrap_print(
                "\"Southwake Port has your name on the ledger now. Show the Harbor Pass at the dock and sail when you are ready.\"",
                C.WHITE,
            )
        elif self.slime_king_defeated():
            self.wrap_print(
                "\"You did it. The roads will breathe again, and Mosswake owes you more than a few coins.\"",
                C.WHITE,
            )
            p.misc.append("harbor_pass")
            self.worlds["mosswake"][("G", 5)]["revealed"] = True
            print()
            print(styled("  Received: Harbor Pass.", C.GREEN, C.BOLD))
            print(styled("  You may now use 'sail' at Southwake Port.", C.CYAN))
        elif p.level < 2:
            self.wrap_print(
                "\"The harbor is under embargo. No boat leaves Mosswake while the marsh roads are unsafe.\"",
                C.WHITE,
            )
            self.wrap_print(
                "\"Prove you can survive beyond the village. Reach level 2 in Old Fern Forest, then come back to me.\"",
                C.WHITE,
            )
            self.worlds["mosswake"][("D", 6)]["revealed"] = True
            print()
            print(styled("  Quest: Reach level 2, then return to Mayor Aldren.", C.CYAN))
        else:
            self.wrap_print(
                "\"Good. You have learned enough not to vanish at the first puddle that moves.\"",
                C.WHITE,
            )
            self.wrap_print(
                "\"The trouble comes from Slime Hollow, south-east of Greenhollow. Defeat the Slime King, and I will lift the embargo.\"",
                C.WHITE,
            )
            self.worlds["mosswake"][("F", 8)]["revealed"] = True
            print()
            print(styled("  Quest: Defeat the Slime King in Slime Hollow.", C.CYAN))
        self.print_sep()
        print()

    def talk_crownvale_king(self):
        p = self.player
        print()
        self.print_sep()
        print(styled("  [King Rowen]", C.BOLD, C.YELLOW))
        print()
        if "greenmarch_pass" not in p.misc:
            if self._boss_defeated("crownvale", "hollow_baron"):
                self.wrap_print(
                    "\"The eastern road is breathing again. You did not bring me a victory parade; you brought me proof. That is better.\"",
                    C.WHITE,
                )
                self._grant_misc_once("greenmarch_pass")
                self.wrap_print("\"Show this at the forest border. Greenmarch will open to you. Listen there before you strike. The old trees remember more than we do.\"", C.WHITE)
            else:
                self.wrap_print(
                    "\"Crownvale looks peaceful from a tower, but the road east is held by an oathbreaker in my old keep.\"",
                    C.WHITE,
                )
                self.wrap_print(
                    "\"Find Crownvale Keep at H9. Defeat the Hollow Baron, and I will grant you passage to Greenmarch.\"",
                    C.WHITE,
                )
                self._reveal_location("crownvale", ("H", 9))
                print()
                print(styled("  Quest: Defeat the Hollow Baron in Crownvale Keep.", C.CYAN))
        elif "ashenreach_pass" not in p.misc:
            self.wrap_print(
                "\"You have my trust, but the old threat is not a single wound. Follow the passes. Hear what Greenmarch and Scalefen know before you seek the mountains.\"",
                C.WHITE,
            )
        elif p.dragon_quest is None:
            if p.level < 5:
                self.wrap_print(
                    "\"The last road is open, but do not mistake access for readiness. Return when you have grown stronger. (Reach level 5)\"",
                    C.WHITE,
                )
            else:
                dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
                self.wrap_print(
                    f"\"The old legends were warnings, not stories. The final sign points to Ashenreach, at {styled(dl_coord, C.BOLD, C.CYAN)}.\"",
                    C.WHITE,
                )
                self.wrap_print(
                    "\"Go there and learn what has returned. If blade is needed, use it. If truth is needed, survive long enough to bring it back.\"",
                    C.WHITE,
                )
                p.dragon_quest = "given"
                if self.dragon_lair_pos:
                    self._reveal_location(self.dragon_world_key, self.dragon_lair_pos)
                print()
                print(styled("  Quest: Reach the Ashenreach Dragon Lair.", C.CYAN))
        elif p.dragon_quest == "given":
            dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
            self.wrap_print(f"\"Ashenreach still waits. The answer lies at {styled(dl_coord, C.BOLD, C.CYAN)}.\"", C.WHITE)
        elif p.dragon_quest == "completed":
            self.wrap_print(
                "\"You returned with the sky still blue above us. Crownvale will remember that, even when the songs get your name wrong.\"",
                C.WHITE,
            )
        self.print_sep()
        print()

    def talk_greenmarch_elder(self):
        p = self.player
        print()
        self.print_sep()
        print(styled("  [Elder Maelis]", C.BOLD, C.GREEN))
        print()
        if self._has_misc("scalefen_pass"):
            self.wrap_print(
                "\"The trees no longer pull away from your shadow. Scalefen has accepted your road; follow it carefully.\"",
                C.WHITE,
            )
        elif self._boss_defeated("greenmarch", "thornwell_warden"):
            self.wrap_print(
                "\"The ruined root has gone quiet. You did not silence the forest; you freed the part that was choking.\"",
                C.WHITE,
            )
            self._grant_misc_once("scalefen_pass")
            self.wrap_print("\"Take this to the marsh border. Scalefen respects deeds more than letters, but the seal will make them listen.\"", C.WHITE)
        else:
            self.wrap_print(
                "\"Greenmarch is old enough to forgive many things. Thornwell is not one of them.\"",
                C.WHITE,
            )
            self.wrap_print(
                "\"Go to Thornwell Ruins at W10. The Warden there binds roots around paths that should remain open.\"",
                C.WHITE,
            )
            self._reveal_location("greenmarch", ("W", 10))
            print()
            print(styled("  Quest: Defeat the Thornwell Warden in Thornwell Ruins.", C.CYAN))
        self.print_sep()
        print()

    def talk_scalefen_matriarch(self):
        p = self.player
        print()
        self.print_sep()
        print(styled("  [Matriarch Sytha]", C.BOLD, C.CYAN))
        print()
        if "ashenreach_pass" in p.misc:
            self.wrap_print(
                "\"The marsh has judged you loud enough to be useful and quiet enough to live. The mountain road is yours.\"",
                C.WHITE,
            )
        elif self._boss_defeated("scalefen", "mirejaw_matriarch"):
            self.wrap_print(
                "\"Mirejaw's brood has scattered. The water is still foul, but now it moves where it chooses.\"",
                C.WHITE,
            )
            self._grant_misc_once("ashenreach_pass")
            self.wrap_print("\"Take the Ashenreach Pass. The mountains do not welcome anyone, but they will no longer turn you away at our border.\"", C.WHITE)
        else:
            self.wrap_print(
                "\"Our scouts vanish near the drowned stone. Not dead at first. Just missing. Then the marsh returns their weapons.\"",
                C.WHITE,
            )
            self.wrap_print(
                "\"Find Sunken Grotto at S17. If the Mirejaw Matriarch rules there, end her hold and the road to Ashenreach opens.\"",
                C.WHITE,
            )
            self._reveal_location("scalefen", ("S", 17))
            print()
            print(styled("  Quest: Defeat the Mirejaw Matriarch in Sunken Grotto.", C.CYAN))
        self.print_sep()
        print()

    def talk_ashenreach_scout(self):
        p = self.player
        print()
        self.print_sep()
        print(styled("  [Highpass Scout]", C.BOLD, C.YELLOW))
        print()
        if p.dragon_quest == "completed":
            self.wrap_print(
                "\"The pass is quiet. Too quiet for this place. Maybe that is what victory sounds like up here.\"",
                C.WHITE,
            )
        elif p.dragon_quest == "given":
            dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
            self.wrap_print(f"\"Follow the ash winds to {styled(dl_coord, C.BOLD, C.CYAN)}. The mountain keeps pointing there, even when the compass refuses.\"", C.WHITE)
        else:
            dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
            self.wrap_print(
                "\"Something old moves above the ridges. We hear stone split at night, but no storm follows.\"",
                C.WHITE,
            )
            self.wrap_print(
                f"\"The trail bends toward {styled(dl_coord, C.BOLD, C.CYAN)}. If you are one of the Forest Fools, this is where the name earns its weight.\"",
                C.WHITE,
            )
            p.dragon_quest = "given"
            if self.dragon_lair_pos:
                self._reveal_location(self.dragon_world_key, self.dragon_lair_pos)
            print()
            print(styled("  Quest: Reach the Ashenreach Dragon Lair.", C.CYAN))
        self.print_sep()
        print()

    def cmd_journal(self, _args):
        p = self.player

        def status_line(done, active, title, detail):
            if done:
                label, color = "[DONE]", C.GREEN
            elif active:
                label, color = "[ACTIVE]", C.CYAN
            else:
                label, color = "[LOCKED]", C.DIM
            print(styled(f"  {label.ljust(9)} {title}", color, C.BOLD if active else ""))
            self.wrap_print(f"    {detail}", C.DIM if not active and not done else C.WHITE)

        harbor_done = "harbor_pass" in p.misc
        crown_done = "greenmarch_pass" in p.misc
        green_done = self._has_misc("scalefen_pass")
        scale_done = "ashenreach_pass" in p.misc
        dragon_done = p.dragon_quest == "completed"

        print()
        self.print_sep()
        print(styled("  JOURNAL", C.BOLD, C.YELLOW))
        print()

        if harbor_done:
            mosswake_detail = "Mosswake's embargo is lifted. Southwake Port can sail to Crownport."
        elif self.slime_king_defeated():
            mosswake_detail = "Return to Mayor Aldren in Greenhollow Town Hall to claim the Harbor Pass."
        elif p.level < 2:
            mosswake_detail = "Reach level 2 in Old Fern Forest, then return to Mayor Aldren."
        else:
            mosswake_detail = "Mayor Aldren revealed Slime Hollow. Defeat the Slime King."
        status_line(harbor_done, not harbor_done, "Mosswake Embargo", mosswake_detail)

        if crown_done:
            crown_detail = "King Rowen granted the Greenmarch Pass."
        elif harbor_done:
            crown_detail = "Reach Crownvale Capital, speak to King Rowen, then defeat the Hollow Baron at Crownvale Keep."
        else:
            crown_detail = "Leave Mosswake before the Crownvale road matters."
        status_line(crown_done, harbor_done and not crown_done, "Crownvale Road", crown_detail)

        if green_done:
            green_detail = "Elder Maelis granted the Scalefen Pass."
        elif crown_done:
            green_detail = "Find Eldergrove, speak to Elder Maelis, then defeat the Thornwell Warden at Thornwell Ruins."
        else:
            green_detail = "Earn the Greenmarch Pass from King Rowen."
        status_line(green_done, crown_done and not green_done, "Greenmarch Roots", green_detail)

        if scale_done:
            scale_detail = "Matriarch Sytha granted the Ashenreach Pass."
        elif green_done:
            scale_detail = "Speak to Matriarch Sytha in Scalefen, then defeat the Mirejaw Matriarch at Sunken Grotto."
        else:
            scale_detail = "Earn the Scalefen Pass from Greenmarch."
        status_line(scale_done, green_done and not scale_done, "Scalefen Waters", scale_detail)

        if dragon_done:
            ash_detail = "Vaelrith has fallen. Return to the kingdom when you are ready."
        elif scale_done or p.dragon_quest == "given":
            dl_coord = coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else "unknown"
            ash_detail = f"Reach Highpass and follow the ash winds toward the Dragon Lair at {dl_coord}."
        else:
            ash_detail = "Earn the Ashenreach Pass and learn what waits in the mountains."
        status_line(dragon_done, (scale_done or p.dragon_quest == "given") and not dragon_done, "Ashenreach Dragon", ash_detail)

        print()
        print(styled("  Local quest chains planned for villages are listed in web/wiki.html.", C.DIM))
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
        race_name = RACES.get(p.race, {}).get("name", p.race.title())
        gender_name = GENDERS.get(p.gender, {}).get("name", p.gender.title())
        class_name = CLASSES.get(p.character_class, {}).get("name", p.character_class.title())
        print(f"  Origin:  {styled(race_name + ' / ' + gender_name + ' / ' + class_name, C.CYAN)}")
        print(f"  HP:      {p.hp}/{p.max_hp} [{bar}]")
        print(f"  Mana:    {p.mana}/{p.max_mana} [{mana_bar}]")
        print(f"  Attack:  {styled(str(p.attack), C.RED)}")
        print(f"  Magic:   {styled(str(p.magic_power), C.MAGENTA)}")
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
        target = REGION_ALIASES.get(target, target)
        p = self.player

        if target in REGIONS:
            self.switch_region(target)
            return

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

        cols, rows = self.world_cols_rows()
        parsed = parse_coord(args[0], cols, rows)
        if parsed:
            col, row = parsed
            if (col, row) in self.world:
                target_tile = self.world[(col, row)]
                if target_tile["type"] == "water":
                    print(styled("  You cannot travel across water.", C.BLUE))
                    return
                if self.current_world_key == "continent":
                    region = target_tile.get("region")
                    if region and not self.is_region_unlocked(region):
                        region_name = REGIONS.get(region, region.title())
                        print(styled(f"  The road to {region_name} is barred by regional decree.", C.RED))
                        print(styled("  Earn that region's pass before crossing the border.", C.DIM))
                        return
                p.pos = (col, row)
                new_tile = self.current_tile()
                new_tile["visited"] = True
                t = new_tile["type"]
                if t not in ("plains", "water"):
                    p.inside = t
                    p.subloc = None
                    print()
                    print(styled(f"  You travel to {self.pos_label()} - {self.tile_display_name(new_tile)}.", C.YELLOW))
                    self.cmd_look([])
                else:
                    p.inside = None
                    p.subloc = None
                    print()
                    print(styled(f"  You travel to {self.pos_label()}...", C.YELLOW))
                    self._describe_arrival(new_tile)
                return

        if any(ch.isdigit() for ch in args[0]):
            print(styled(
                f"  Invalid cell: {args[0].upper()}. Use {column_range_label(cols)} and {rows[0]}-{rows[-1]}.",
                C.RED,
            ))
            return

        print(styled(f"  Unknown destination: {args[0]}", C.RED))

    def cmd_sail(self, _args):
        p = self.player
        tile = self.current_tile()
        if tile["type"] != "port" and p.inside != "port":
            print(styled("  You need to be at a port to sail.", C.RED))
            return

        if self.current_world_key == "mosswake":
            if "harbor_pass" not in p.misc:
                print(styled("  The dockmaster blocks the pier.", C.YELLOW))
                print(styled("  \"No one leaves Mosswake without the mayor's Harbor Pass.\"", C.WHITE))
                return
            self.switch_world("crownvale", FIXED_MAPS["crownvale"]["arrival_pos"])
            print()
            self.print_sep()
            self.wrap_print(
                "The boat cuts through the morning tide. Mosswake shrinks behind you until the mainland rises ahead.",
                C.WHITE,
            )
            print(styled(f"  Arrived at {self.current_world_name()} / {self.pos_label()}.", C.CYAN))
            self.print_sep()
            print()
            self.cmd_look([])
            return

        if self.current_world_key == "continent" or self.current_world_key in REGIONS:
            self.switch_world("mosswake", FIXED_MAPS["mosswake"]["arrival_pos"])
            print()
            self.print_sep()
            self.wrap_print("You sail back across the channel toward Mosswake Isle.", C.WHITE)
            print(styled(f"  Arrived at {self.current_world_name()} / {self.pos_label()}.", C.CYAN))
            self.print_sep()
            print()
            self.cmd_look([])
            return

        print(styled("  No sailing route is available here.", C.DIM))

    def _describe_arrival(self, tile):
        t = tile["type"]
        if t == "plains":
            self.wrap_print(random.choice(DESC_PLAINS), C.DIM)
        else:
            descs = DESC_MAP.get(t, DESC_PLAINS)
            self.wrap_print(random.choice(descs), C.WHITE)
            print(styled(f"\n  {self.tile_display_name(tile)} is here. Use 'cd {t}' to enter.", C.YELLOW))
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
        if self.active_combat and self.active_combat.active:
            print(styled("  You are already in combat. Use: attack, use [potion], cast {spell}, flee.", C.RED))
            return

        p = self.player
        tile = self.current_tile()

        if (p.inside == "dragon_lair" or tile["type"] == "dragon_lair") and p.subloc == "nest":
            self.active_combat = fight_dragon(p, self.world, self.print_sep, self.pos_label)
            return

        self.active_combat = fight_enemy(p, tile, self.print_sep, self.pos_label)

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
            good_loot = random_treasure_equipment(tile, p.level)
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
            item_key = roll_search_drop(tile, p.level)
            if item_key:
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
                tile["merchant_stock"] = generate_merchant_stock(tile.get("map_key", self.current_world_key))
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
        catalog_keys = list(dict.fromkeys(catalog_keys))
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
                if tile.get("boss_defeated"):
                    continue
                if tile["type"] in ("forest", "cave", "castle", "dungeon") and tile.get("enemies_cleared"):
                    tile["enemies_cleared"] = False
                if tile["type"] in ("forest", "cave", "castle", "dungeon") and not tile.get("loot_available"):
                    tile["loot_available"] = True

    def dispatch(self, raw_input):
        parts = raw_input.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        if self.active_combat and self.active_combat.active:
            if cmd in ("q", "quit", "exit"):
                self.cmd_quit(args)
                self._tick_respawn()
                return
            combat_shortcuts = {
                "a": "attack", "c": "cast", "u": "use", "f": "flee",
                "p": "use", "?": "help",
            }
            combat_cmd = combat_shortcuts.get(cmd, cmd)
            self.active_combat.handle_command(combat_cmd, args)
            if not self.active_combat.active:
                self.active_combat = None
            self._tick_respawn()
            return

        if self.active_combat and not self.active_combat.active:
            self.active_combat = None

        shortcuts = {
            "h": "help", "m": "map", "l": "look", "t": "talk",
            "j": "journal", "s": "search", "f": "fight", "i": "inventory",
            "e": "equip", "u": "use", "b": "buy", "q": "quit",
        }
        cmd = shortcuts.get(cmd, cmd)

        commands = {
            "help":      self.cmd_help,
            "map":       self.cmd_map,
            "walkable":  self.cmd_walkable,
            "paths":     self.cmd_walkable,
            "zoom":      self.cmd_zoom,
            "look":      self.cmd_look,
            "talk":      self.cmd_talk,
            "journal":   self.cmd_journal,
            "quests":    self.cmd_journal,
            "stats":     self.cmd_stats,
            "inventory": self.cmd_inventory,
            "inv":       self.cmd_inventory,
            "cd":        self.cmd_cd,
            "sail":      self.cmd_sail,
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
        elif cmd in ("attack", "cast", "flee"):
            print(styled("  You are not in combat.", C.DIM))
        else:
            print(styled(f"  Unknown command: {cmd}. Type 'help' for commands.", C.RED))

    # -- interface bridge --

    def _append_message(self, text, kind="output", raw=None):
        entry = {
            "kind": kind,
            "text": strip_ansi(text),
            "raw": raw if raw is not None else text,
        }
        self.message_log.append(entry)
        if len(self.message_log) > self.max_message_log:
            self.message_log = self.message_log[-self.max_message_log:]
        return entry

    def _append_output(self, output):
        entries = []
        for line in output.splitlines():
            entries.append(self._append_message(line, "output", raw=line))
        return entries

    def process_command(self, raw_input):
        """Run one terminal command and return messages plus UI-readable state."""
        new_messages = []
        command = raw_input.strip()
        if command:
            new_messages.append(self._append_message(f"> {command}", "command"))

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.dispatch(raw_input)

        new_messages.extend(self._append_output(buffer.getvalue()))
        return {
            "messages": new_messages,
            "state": self.get_ui_state(),
        }

    def get_ui_state(self):
        """Return all passive UI panels as structured data."""
        return {
            "running": self.running,
            "location": self._get_location_state(),
            "player": self._get_player_state(),
            "map": self._get_map_state(),
            "context": self._get_context_state(),
            "combat": self.active_combat.get_state() if self.active_combat and self.active_combat.active else None,
            "terminal": {
                "interactive": True,
                "messages": list(self.message_log),
            },
        }

    def _get_location_state(self):
        tile = self.current_tile()
        return {
            "label": self.location_label(),
            "world_key": self.current_world_key,
            "coord": self.pos_label(),
            "pos": {"col": self.player.pos[0], "row": self.player.pos[1]},
            "inside": self.player.inside,
            "subloc": self.player.subloc,
            "tile_type": tile["type"],
            "terrain": tile.get("terrain", "grass"),
            "available_sublocations": list(SUBLOCS.get(self.player.inside, [])) if self.player.inside else [],
        }

    def _get_player_state(self):
        p = self.player

        def item_counts(items, catalog):
            counts = Counter(items)
            result = []
            for key, count in counts.items():
                info = catalog.get(key, {})
                result.append({
                    "key": key,
                    "name": info.get("name", key),
                    "count": count,
                    "equipped": key == p.weapon or key == p.armor_equipped,
                    "attack": info.get("attack"),
                    "armor": info.get("armor"),
                    "dodge": info.get("dodge"),
                    "heal": info.get("heal"),
                    "value": info.get("value"),
                })
            return result

        return {
            "race": {
                "key": p.race,
                "name": RACES.get(p.race, {}).get("name", p.race.title()),
            },
            "gender": {
                "key": p.gender,
                "name": GENDERS.get(p.gender, {}).get("name", p.gender.title()),
            },
            "class": {
                "key": p.character_class,
                "name": CLASSES.get(p.character_class, {}).get("name", p.character_class.title()),
            },
            "hp": p.hp,
            "max_hp": p.max_hp,
            "mana": p.mana,
            "max_mana": p.max_mana,
            "level": p.level,
            "xp": p.xp,
            "xp_to_next": p.xp_to_next,
            "gold": p.gold,
            "attack": p.attack,
            "magic_power": p.magic_power,
            "defense": p.armor_value,
            "dodge_chance": p.dodge_chance,
            "weapon": {
                "key": p.weapon,
                "name": p.weapon_name(),
            },
            "armor": {
                "key": p.armor_equipped,
                "name": p.armor_name(),
            },
            "spells": [
                {"key": key, "name": SPELLS.get(key, {}).get("name", key)}
                for key in p.spells
            ],
            "spell_slots": {
                "used": len(p.spells),
                "max": p.max_spells,
            },
            "has_map": p.has_map,
            "inventory": {
                "weapons": item_counts(p.weapons, WEAPONS),
                "armors": item_counts(p.armors, ARMORS),
                "consumables": item_counts(p.consumables, CONSUMABLES),
                "misc": item_counts(p.misc, MISC_ITEMS),
            },
        }

    def _is_tile_visible(self, pos, tile, player_on_view=True):
        if player_on_view and pos == self.player.pos:
            return True
        if self.player.has_map:
            return True
        return tile.get("revealed", False) or tile.get("visited", False)

    def _get_map_state(self):
        cells = []
        view_world = self.map_view_world()
        cols, rows = self.map_view_axes()
        player_on_view = self.map_view_key == self.current_world_key and self.player.pos[0] in cols and self.player.pos[1] in rows
        for r in rows:
            for c in cols:
                pos = (c, r)
                tile = view_world[pos]
                is_filtered = bool(self.map_region_filter and tile.get("region") != self.map_region_filter)
                symbol_visible = False if is_filtered else self._is_tile_visible(pos, tile, player_on_view)
                is_player = player_on_view and pos == self.player.pos
                tile_type = "unknown" if is_filtered else tile["type"]
                walkable = False if is_filtered else self.is_tile_walkable(tile)
                cells.append({
                    "coord": coord_label(pos),
                    "col": c,
                    "row": r,
                    "terrain": "unknown" if is_filtered else tile.get("terrain", "grass"),
                    "type": tile_type,
                    "actual_type": None if is_filtered else tile["type"],
                    "visible": symbol_visible,
                    "symbol_visible": symbol_visible,
                    "terrain_visible": not is_filtered,
                    "visited": tile.get("visited", False),
                    "revealed": tile.get("revealed", False),
                    "is_player": is_player,
                    "walkable": walkable,
                    "enemies_cleared": tile.get("enemies_cleared", False),
                    "loot_available": tile.get("loot_available", False),
                    "region": tile.get("region"),
                })
        return {
            "name": self.map_view_name(),
            "key": self.map_view_key,
            "region": self.map_region_filter,
            "cols": list(cols),
            "rows": list(rows),
            "player_coord": self.pos_label() if player_on_view else None,
            "player_pos": {"col": self.player.pos[0], "row": self.player.pos[1]},
            "show_walkable": self.show_walkable_overlay,
            "overview_only": FIXED_MAPS.get(self.map_view_key, {}).get("overview_only", False),
            "cells": cells,
        }

    def _get_context_state(self):
        tile = self.current_tile()
        mode = "combat" if self.active_combat and self.active_combat.active else "exploration"
        context = {
            "mode": mode,
            "tile_name": self.tile_display_name(tile),
            "tile_type": tile["type"],
            "terrain": tile.get("terrain", "grass"),
            "quest": {
                "dragon": self.player.dragon_quest,
                "dragon_lair_coord": coord_label(self.dragon_lair_pos) if self.dragon_lair_pos else None,
            },
            "merchant_stock": list(tile.get("merchant_stock") or []),
            "zone_unlocks": dict(ZONE_LEVEL_REQUIREMENTS),
        }
        if self.active_combat and self.active_combat.active:
            context["enemy"] = self.active_combat.get_state()["enemy"]
        return context

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
