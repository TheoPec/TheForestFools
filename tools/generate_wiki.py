from __future__ import annotations

from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.armors import ARMORS
from data.character_options import CLASSES, DEFAULT_CHARACTER, GENDERS, RACES
from data.consumables import CONSUMABLES
from data.enemies import DRAGON_BOSS, ZONE_ENEMIES
from data.fixed_maps import FIXED_MAPS, REGIONS
from data.locations import DESC_MAP, DESC_SUBLOCS, SUBLOCS, TILE_NAMES, TILE_SYMBOLS
from data.loot_tables import ARMOR_TIERS, REGION_LOOT_TIERS, WEAPON_TIERS
from data.misc_items import MISC_ITEMS
from data.npcs import NPC_DIALOGUES, NPC_DIALOGUES_WILD
from data.spells import SPELLS
from data.weapons import WEAPONS


INTRO_SCENES = [
    ("01_valley", "The Quiet Valley", [
        "The valley was peaceful.",
        "Green fields stretched beneath the castle.",
        "No one believed the old legends anymore.",
    ]),
    ("02_burning_road", "The First Sign", [
        "Then the roads began to burn.",
        "No army was seen.",
        "Only smoke rising beyond the hills.",
    ]),
    ("03_silent_towers", "Silent Towers", [
        "The watchtowers fell silent.",
        "No bells rang.",
        "No guards returned.",
    ]),
    ("04_council", "The King's Question", [
        "The king did not ask for war.",
        "He asked for someone brave enough to enter the forest.",
        "Or foolish enough.",
    ]),
    ("05_forest_fools", "Forest Fools", [
        "They called them Forest Fools.",
        "Scouts, wanderers, forgotten names.",
        "The ones who walked where kingdoms ended.",
    ]),
]


MAIN_STORY_DIALOGUES = [
    ("Mayor Aldren", "Mosswake", [
        ("Embargo active", "The harbor is under embargo. No boat leaves Mosswake while the marsh roads are unsafe."),
        ("Level 2 objective", "Prove you can survive beyond the village. Reach level 2 in Old Fern Forest, then come back to me."),
        ("Slime Hollow revealed", "Good. You have learned enough not to vanish at the first puddle that moves."),
        ("Slime King objective", "The trouble comes from Slime Hollow, south-east of Greenhollow. Defeat the Slime King, and I will lift the embargo."),
        ("After Slime King", "You did it. The roads will breathe again, and Mosswake owes you more than a few coins."),
        ("Pass obtained", "Southwake Port has your name on the ledger now. Show the Harbor Pass at the dock and sail when you are ready."),
    ]),
    ("King Rowen", "Crownvale", [
        ("First request", "Crownvale looks peaceful from a tower, but the road east is held by an oathbreaker in my old keep."),
        ("Hollow Baron objective", "Find Crownvale Keep at H9. Defeat the Hollow Baron, and I will grant you passage to Greenmarch."),
        ("After Hollow Baron", "The eastern road is breathing again. You did not bring me a victory parade; you brought me proof. That is better."),
        ("Greenmarch pass", "Show this at the forest border. Greenmarch will open to you. Listen there before you strike. The old trees remember more than we do."),
        ("Before final readiness", "The last road is open, but do not mistake access for readiness. Return when you have grown stronger. (Reach level 5)"),
        ("Dragon quest", "The old legends were warnings, not stories. The final sign points to Ashenreach."),
        ("Dragon quest meaning", "Go there and learn what has returned. If blade is needed, use it. If truth is needed, survive long enough to bring it back."),
        ("After dragon", "You returned with the sky still blue above us. Crownvale will remember that, even when the songs get your name wrong."),
    ]),
    ("Elder Maelis", "Greenmarch", [
        ("First request", "Greenmarch is old enough to forgive many things. Thornwell is not one of them."),
        ("Thornwell objective", "Go to Thornwell Ruins at W10. The Warden there binds roots around paths that should remain open."),
        ("After Thornwell", "The ruined root has gone quiet. You did not silence the forest; you freed the part that was choking."),
        ("Scalefen pass", "Take this to the marsh border. Scalefen respects deeds more than letters, but the seal will make them listen."),
        ("After pass", "The trees no longer pull away from your shadow. Scalefen has accepted your road; follow it carefully."),
    ]),
    ("Matriarch Sytha", "Scalefen", [
        ("First request", "Our scouts vanish near the drowned stone. Not dead at first. Just missing. Then the marsh returns their weapons."),
        ("Mirejaw objective", "Find Sunken Grotto at S17. If the Mirejaw Matriarch rules there, end her hold and the road to Ashenreach opens."),
        ("After Mirejaw", "Mirejaw's brood has scattered. The water is still foul, but now it moves where it chooses."),
        ("Ashenreach pass", "Take the Ashenreach Pass. The mountains do not welcome anyone, but they will no longer turn you away at our border."),
        ("After pass", "The marsh has judged you loud enough to be useful and quiet enough to live. The mountain road is yours."),
    ]),
    ("Highpass Scout", "Ashenreach", [
        ("First warning", "Something old moves above the ridges. We hear stone split at night, but no storm follows."),
        ("Dragon trail", "The trail bends toward the Dragon Lair. If you are one of the Forest Fools, this is where the name earns its weight."),
        ("Quest active", "Follow the ash winds. The mountain keeps pointing there, even when the compass refuses."),
        ("After dragon", "The pass is quiet. Too quiet for this place. Maybe that is what victory sounds like up here."),
    ]),
]


QUEST_CHAINS = {
    "Mosswake Isle - Harbor Pass": [
        ("Embargo de Greenhollow", "Mayor Aldren", "Reach level 2, reveal Slime Hollow, defeat the Slime King.", "Harbor Pass"),
        ("La lumiere du phare", "Nora", "Find the lighthouse lens near the old shore.", "Old lore clue"),
        ("Le filet de Tovin", "Tovin", "Recover the lost fishing net near the rocks.", "Fisher Hook Blade / gold"),
        ("Herbes pour Ameline", "Sister Ameline", "Gather herbs in Old Fern Forest.", "Potions and healing"),
    ],
    "Crownvale - Greenmarch Pass": [
        ("La route de l'Est", "King Rowen", "Investigate Crownvale Keep.", "Main regional objective"),
        ("Patrouille disparue", "Captain Valen", "Find the missing patrol in Northwatch Woods.", "Militia gear"),
        ("Archives cachees", "Archivist Odran", "Recover a page of the First Oath.", "Codex entry"),
        ("Les moutons de Fairmeadow", "Maelle", "Save the flock from Bramble Hounds.", "Gold / Fairmeadow reputation"),
        ("Serment du Baron", "King Rowen", "Defeat the Hollow Baron.", "Greenmarch Pass"),
    ],
    "Greenmarch - Scalefen Pass": [
        ("La foret qui etouffe", "Elder Maelis", "Understand why Thornwell is choking the paths.", "Main regional objective"),
        ("Chemin des rodeurs", "Eldrin", "Follow ranger marks to Deep Briar.", "Map reveal / Briar Knife"),
        ("L'enfant perdu", "Lost Child", "Rescue a child from the old clearings.", "Eldergrove reputation"),
        ("La racine qui parle", "Root Speaker", "Answer the root riddle.", "First Oath lore"),
        ("Thornwell", "Elder Maelis", "Defeat the Thornwell Warden.", "Scalefen Pass"),
    ],
    "Scalefen - Ashenreach Pass": [
        ("Les armes rendues par l'eau", "Matriarch Sytha", "Investigate the missing scouts.", "Main regional objective"),
        ("Rite des roseaux", "Sszar", "Bring clear water, black mud and white reed.", "Marsh lore"),
        ("Chasse dans Reedmire", "Kraxa", "Hunt Marsh Striders or Mudscale Brutes.", "Reedscale gear"),
        ("Le totem qui ment", "Speaking Totem", "Solve the totem riddle.", "Sunken Grotto reveal"),
        ("Mirejaw", "Matriarch Sytha", "Defeat the Mirejaw Matriarch.", "Ashenreach Pass"),
    ],
    "Ashenreach - Final": [
        ("Highpass", "Highpass Scout", "Follow the ash winds toward the dragon trail.", "Dragon quest active"),
        ("La pierre noire", "Thorek", "Explore the old mine and learn what was awakened.", "Black stone lore"),
        ("Forge des hauteurs", "Master Borun", "Bring black ore and ash fragments.", "High tier gear upgrade"),
        ("Relique du serment", "Royal Archaeologist", "Recover an oath relic at Broken Spire.", "Vaelrith truth"),
        ("Vaelrith", "Dragon", "Reach the Dragon Lair and survive the final encounter.", "Ending / Dragon Slayer Blade"),
    ],
}


COMMANDS = [
    ("help", "Show commands."),
    ("map", "Display map."),
    ("walkable / paths", "Toggle reachable-cell overlay."),
    ("zoom island|continent|region", "Change the map view."),
    ("cd {cell}", "Travel to a map cell."),
    ("cd {region}", "Travel to a region if the pass is unlocked."),
    ("cd {location}", "Enter a location."),
    ("cd {subloc}", "Enter a sub-location."),
    ("cd ..", "Go back."),
    ("sail", "Travel by boat from an authorized port."),
    ("look", "Describe the current place."),
    ("talk", "Talk to someone here."),
    ("journal / quests", "Show quest progress."),
    ("stats", "Show player stats."),
    ("inventory / inv", "Show inventory."),
    ("equip {item}", "Equip weapon or armor."),
    ("unequip weapon|armor", "Unequip gear."),
    ("use {item}", "Use consumable."),
    ("buy {item}", "Buy from shop NPCs."),
    ("sell {item}", "Sell at a merchant."),
    ("cast {spell}", "Cast a spell during combat."),
    ("fight", "Start combat in hostile places."),
    ("search", "Search special places for loot."),
    ("sleep", "Rest in a tavern."),
    ("train", "Increase spell slots at a mage."),
    ("cheat", "Testing command that unlocks content."),
    ("quit / exit", "Quit game."),
]


def clean(value) -> str:
    text = str(value)
    replacements = {
        "â€”": "--",
        "â€“": "-",
        "â†’": "->",
        "â€œ": '"',
        "â€": '"',
        "â€™": "'",
        "Ã©": "e",
        "Ã¨": "e",
        "Ãª": "e",
        "Ã ": "a",
        "Ã®": "i",
        "Ã´": "o",
        "Ã»": "u",
        "Ã§": "c",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("ascii", "ignore").decode("ascii")


def h(value) -> str:
    return escape(clean(value), quote=True)


def slug(value) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in clean(value).lower()).strip("-")


def table(headers, rows) -> str:
    head = "".join(f"<th>{h(col)}</th>" for col in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<div class=\"table-scroll\"><table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"


def list_items(items) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def stat_items(stats: dict) -> str:
    return " ".join(f"<span class=\"tag\">{h(k)} {h(v)}</span>" for k, v in stats.items())


def section(title: str, subtitle: str, body: str, ident: str | None = None) -> str:
    ident = ident or slug(title)
    return f"""
  <section class="section" id="{ident}">
    <div class="section-title"><h2>{h(title)}</h2><span>{h(subtitle)}</span></div>
    {body}
  </section>
"""


def item_rows(catalog: dict, fields: list[str]):
    rows = []
    for key, info in catalog.items():
        values = [f"<code>{h(key)}</code>", h(info.get("name", key))]
        for field in fields:
            values.append(h(info.get(field, "")))
        sell = int(info.get("value", 0) / 2) if "value" in info else ""
        values.append(h(sell))
        rows.append(values)
    return rows


def build_items_section() -> str:
    parts = []
    parts.append("<article class=\"card\"><h3>Weapons</h3>" + table(
        ["Key", "Name", "Attack", "Buy value", "Sell value"],
        item_rows(WEAPONS, ["attack", "value"]),
    ) + "</article>")
    parts.append("<article class=\"card\"><h3>Armors</h3>" + table(
        ["Key", "Name", "Armor", "Dodge", "Buy value", "Sell value"],
        item_rows(ARMORS, ["armor", "dodge", "value"]),
    ) + "</article>")
    parts.append("<article class=\"card\"><h3>Consumables</h3>" + table(
        ["Key", "Name", "Heal", "Buy value", "Sell value"],
        item_rows(CONSUMABLES, ["heal", "value"]),
    ) + "</article>")
    parts.append("<article class=\"card\"><h3>Misc items</h3>" + table(
        ["Key", "Name", "Value", "Sell value"],
        item_rows(MISC_ITEMS, ["value"]),
    ) + "</article>")
    return "<div class=\"grid one\">" + "".join(parts) + "</div>"


def build_spells_section() -> str:
    rows = []
    for key, info in SPELLS.items():
        effects = []
        for field in ("damage", "heal", "shield", "weaken"):
            if field in info:
                effects.append(f"{field}: {info[field]}")
        rows.append([
            f"<code>{h(key)}</code>",
            h(info["name"]),
            h(", ".join(effects)),
            h(info.get("mana", "")),
            h(info.get("value", "")),
            h(info.get("source", "")),
        ])
    return table(["Key", "Name", "Effect", "Mana", "Buy value", "Source"], rows)


def build_monsters_section() -> str:
    cards = []
    for pool, enemies in ZONE_ENEMIES.items():
        rows = []
        for enemy in enemies:
            rows.append([
                h(enemy["name"]),
                h(enemy["hp"]),
                h(enemy["attack"]),
                h(f"{enemy['gold'][0]}-{enemy['gold'][1]}"),
                h(enemy["xp"]),
            ])
        cards.append(f"<article class=\"card\"><h3>{h(pool)}</h3>{table(['Name','HP','ATK','Gold','XP'], rows)}</article>")
    cards.append(
        "<article class=\"card\"><h3>Dragon boss</h3>" +
        table(["Name", "HP", "ATK", "Gold", "XP", "Special"], [[
            h(DRAGON_BOSS["name"]),
            h(DRAGON_BOSS["hp"]),
            h(DRAGON_BOSS["attack"]),
            h(f"{DRAGON_BOSS['gold'][0]}-{DRAGON_BOSS['gold'][1]}"),
            h(DRAGON_BOSS["xp"]),
            h(f"inferno chance {DRAGON_BOSS.get('inferno_chance', 0)}"),
        ]]) + "</article>"
    )
    return "<div class=\"grid one\">" + "".join(cards) + "</div>"


def build_loot_section() -> str:
    weapon_rows = []
    for tier, keys in WEAPON_TIERS.items():
        for key in keys:
            info = WEAPONS.get(key, {})
            weapon_rows.append([h(tier), f"<code>{h(key)}</code>", h(info.get("name", key)), h(info.get("attack", "")), h(info.get("value", ""))])
    armor_rows = []
    for tier, keys in ARMOR_TIERS.items():
        for key in keys:
            info = ARMORS.get(key, {})
            armor_rows.append([h(tier), f"<code>{h(key)}</code>", h(info.get("name", key)), h(info.get("armor", "")), h(info.get("dodge", "")), h(info.get("value", ""))])
    region_rows = [[h(k), h(v)] for k, v in REGION_LOOT_TIERS.items()]
    return (
        "<div class=\"grid one\">"
        "<article class=\"card\"><p>Le continent n'a pas de tier de loot : c'est une vue globale du monde. Le loot depend de la region jouable ou du type de lieu ou se trouve le joueur.</p></article>"
        "<article class=\"card\"><h3>Region tiers</h3>" + table(["Region", "Tier"], region_rows) + "</article>"
        "<article class=\"card\"><h3>Weapon tiers</h3>" + table(["Tier", "Key", "Name", "ATK", "Value"], weapon_rows) + "</article>"
        "<article class=\"card\"><h3>Armor tiers</h3>" + table(["Tier", "Key", "Name", "DEF", "Dodge", "Value"], armor_rows) + "</article>"
        "</div>"
    )


def build_maps_section() -> str:
    cards = []
    for map_key, spec in FIXED_MAPS.items():
        rows = []
        for pos, info in spec.get("named_tiles", {}).items():
            tile_type = ""
            rows.append([
                h(f"{pos[0]}{pos[1]}"),
                f"<code>{h(info.get('id', ''))}</code>",
                h(info.get("name", "")),
                h(info.get("boss", "")),
                h(info.get("enemy_pool", "")),
                h(info.get("revealed", False)),
            ])
        overview_note = "<span class=\"tag\">overview only</span><span class=\"tag\">no loot tier</span>" if spec.get("overview_only") else ""
        body = [
            f"<p><span class=\"tag\">key {h(map_key)}</span><span class=\"tag\">grid {h(len(spec.get('cols', [])))}x{h(len(list(spec.get('row_numbers', []))))}</span><span class=\"tag\">start {h(spec.get('start_pos'))}</span>{overview_note}</p>",
            table(["Cell", "Id", "Name", "Boss", "Enemy pool", "Revealed"], rows) if rows else "<p>No named tiles.</p>",
        ]
        cards.append(f"<article class=\"card\"><h3>{h(spec.get('name', map_key))}</h3>{''.join(body)}</article>")
    return "<div class=\"grid one\">" + "".join(cards) + "</div>"


def build_locations_section() -> str:
    type_rows = []
    for key, name in TILE_NAMES.items():
        type_rows.append([f"<code>{h(key)}</code>", h(name), h(TILE_SYMBOLS.get(key, "")), h(", ".join(SUBLOCS.get(key, [])))])
    desc_cards = ["<article class=\"card\"><h3>Tile types and sub-locations</h3>" + table(["Type", "Name", "Symbol", "Sub-locations"], type_rows) + "</article>"]
    for key, descriptions in DESC_MAP.items():
        desc_cards.append(f"<article class=\"card\"><h3>Location text: {h(key)}</h3>" + list_items([h(text) for text in descriptions]) + "</article>")
    for key, descriptions in DESC_SUBLOCS.items():
        desc_cards.append(f"<article class=\"card\"><h3>Sub-location text: {h(key)}</h3>" + list_items([h(text) for text in descriptions]) + "</article>")
    return "<div class=\"grid one\">" + "".join(desc_cards) + "</div>"


def build_dialogues_section() -> str:
    cards = []
    for npc, region, branches in MAIN_STORY_DIALOGUES:
        rows = [[h(label), h(text)] for label, text in branches]
        cards.append(f"<article class=\"card\"><h3>{h(npc)} <span>{h(region)}</span></h3>{table(['State','Dialogue'], rows)}</article>")

    for source_name, groups in (("NPC_DIALOGUES", NPC_DIALOGUES), ("NPC_DIALOGUES_WILD", NPC_DIALOGUES_WILD)):
        for place, npcs in groups.items():
            for npc_name, lines in npcs.items():
                rows = [[h(i + 1), h(line)] for i, line in enumerate(lines)]
                cards.append(f"<article class=\"card\"><h3>{h(source_name)} / {h(place)} / {h(npc_name)}</h3>{table(['#','Dialogue template'], rows)}</article>")
    return "<div class=\"grid one\">" + "".join(cards) + "</div>"


def build_intro_section() -> str:
    rows = []
    for key, title, lines in INTRO_SCENES:
        rows.append([f"<code>{h(key)}</code>", h(title), h(" / ".join(lines)), f"<code>assets/images/intro/{h(key)}.png</code>"])
    return table(["Key", "Title", "Text", "Asset"], rows)


def build_character_section() -> str:
    race_rows = []
    for key, info in RACES.items():
        race_rows.append([f"<code>{h(key)}</code>", h(info["name"]), h(info["description"]), stat_items(info["bonuses"])])
    class_rows = []
    for key, info in CLASSES.items():
        class_rows.append([f"<code>{h(key)}</code>", h(info["name"]), h(info["description"]), stat_items(info["bonuses"]), h(info.get("starting_items", {}))])
    gender_rows = [[f"<code>{h(key)}</code>", h(info["name"])] for key, info in GENDERS.items()]
    return (
        "<div class=\"grid one\">"
        "<article class=\"card\"><h3>Races</h3>" + table(["Key", "Name", "Description", "Bonuses"], race_rows) + "</article>"
        "<article class=\"card\"><h3>Genders</h3>" + table(["Key", "Name"], gender_rows) + "</article>"
        "<article class=\"card\"><h3>Classes</h3>" + table(["Key", "Name", "Description", "Bonuses", "Starting items"], class_rows) + "</article>"
        f"<article class=\"card\"><h3>Default character</h3><p>{h(DEFAULT_CHARACTER)}</p></article>"
        "</div>"
    )


def build_quests_section() -> str:
    cards = []
    for name, quests in QUEST_CHAINS.items():
        rows = [[h(title), h(npc), h(objective), h(reward)] for title, npc, objective, reward in quests]
        cards.append(f"<article class=\"card\"><h3>{h(name)}</h3>{table(['Quest','NPC','Objective','Reward'], rows)}</article>")
    return "<div class=\"grid one\">" + "".join(cards) + "</div>"


def build_commands_section() -> str:
    return table(["Command", "Use"], [[f"<code>{h(cmd)}</code>", h(desc)] for cmd, desc in COMMANDS])


CSS = """
  @font-face { font-family: "Old London"; src: url("../fonts/OldLondon.ttf") format("truetype"); }
  :root {
    --paper: #fff0be; --paper2: #ffe2a1; --ink: #2b2013; --muted: #6b5735;
    --line: #9f6d28; --panel: rgba(255, 248, 219, .91); --shadow: rgba(65, 38, 12, .22);
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; color: var(--ink); font-family: Georgia, "Times New Roman", serif;
    background: radial-gradient(circle at 14% 10%, rgba(86,150,78,.25), transparent 30%),
      radial-gradient(circle at 82% 6%, rgba(56,143,207,.20), transparent 32%),
      linear-gradient(180deg, #f7d88a 0%, #d89f4d 100%);
  }
  a { color: #174f78; font-weight: 700; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .page { width: min(1320px, calc(100% - 28px)); margin: 0 auto; padding: 24px 0 56px; }
  .hero, .toc, .section { background: var(--panel); border: 2px solid var(--line); box-shadow: 0 18px 42px var(--shadow); }
  .hero {
    min-height: 420px; padding: clamp(24px, 4vw, 48px); display: grid; align-items: end;
    background: linear-gradient(180deg, rgba(30,50,25,.02), rgba(55,31,12,.48)), url("../assets/images/menu/menu_bg.png") center/cover;
    color: #fff9df; text-shadow: 0 3px 9px rgba(0,0,0,.75);
  }
  h1, h2, h3, p { margin: 0; }
  h1, h2 { font-family: "Old London", Georgia, serif; line-height: .95; letter-spacing: .035em; }
  h1 { font-size: clamp(3rem, 8vw, 6.4rem); }
  h2 { font-size: clamp(2rem, 5vw, 3.7rem); }
  h3 { margin-bottom: 10px; font-size: 1.02rem; text-transform: uppercase; letter-spacing: .06em; color: #432f16; }
  h3 span { font-family: "Courier New", monospace; font-size: .8rem; color: var(--muted); text-transform: none; }
  .kicker { font-family: "Courier New", monospace; text-transform: uppercase; letter-spacing: .14em; margin-bottom: 10px; }
  .hero p:last-child { max-width: 760px; margin-top: 14px; font-size: 1.18rem; line-height: 1.55; }
  .toc { margin-top: 18px; padding: 14px; display: flex; gap: 9px; flex-wrap: wrap; justify-content: center; }
  .toc a, .tag { border: 1px solid rgba(92,60,22,.45); background: rgba(255,248,219,.72); color: var(--ink); padding: 7px 10px; font-family: "Courier New", monospace; font-size: .86rem; }
  .section { margin-top: 18px; padding: clamp(18px, 3vw, 30px); }
  .section-title { border-bottom: 2px solid var(--line); padding-bottom: 10px; margin-bottom: 18px; display: flex; gap: 14px; align-items: baseline; flex-wrap: wrap; }
  .section-title span { color: var(--muted); font-family: "Courier New", monospace; }
  .lead { max-width: 940px; font-size: 1.08rem; line-height: 1.65; }
  .grid { display: grid; gap: 14px; margin-top: 16px; }
  .grid.two { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
  .grid.one { grid-template-columns: 1fr; }
  .card { background: rgba(255,253,234,.76); border: 1px solid rgba(106,70,26,.42); padding: 15px; overflow: hidden; }
  .card p, li { line-height: 1.52; }
  .card + .card { margin-top: 0; }
  ul { margin: 8px 0 0; padding-left: 20px; }
  .table-scroll { width: 100%; overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; min-width: 680px; }
  th, td { border-top: 1px solid rgba(106,70,26,.36); padding: 8px 7px; text-align: left; vertical-align: top; line-height: 1.35; }
  th { font-family: "Courier New", monospace; text-transform: uppercase; font-size: .76rem; color: #574019; }
  code { color: #134c70; font-weight: 700; }
  .footer { text-align: center; margin-top: 22px; color: #3b2b15; }
"""


def build_html() -> str:
    nav = [
        ("lore", "Lore"),
        ("intro", "Intro"),
        ("progression", "Progression"),
        ("quetes", "Quetes"),
        ("maps", "Cartes"),
        ("locations", "Lieux/Textes"),
        ("dialogues", "Dialogues"),
        ("items", "Items"),
        ("spells", "Sorts"),
        ("monsters", "Monstres"),
        ("loot", "Loot"),
        ("characters", "Persos"),
        ("commands", "Commandes"),
        ("index.html", "Accueil"),
    ]
    nav_html = "".join(
        f"<a href=\"{('#' + href) if not href.endswith('.html') else href}\">{h(label)}</a>"
        for href, label in nav
    )
    content = [
        section("Lore", "mythe principal", """
    <p class="lead">The Forest Fools raconte un royaume lumineux qui a oublie une promesse ancienne. Vaelrith, le Dragon des Vieilles Racines, n'est pas seulement un monstre : son retour signale que le Premier Serment a ete brise.</p>
    <div class="grid two">
      <article class="card"><h3>Le Premier Serment</h3><p>Les humains, les druides de Greenmarch, les clans lezards de Scalefen et les gardiens d'Ashenreach avaient promis de proteger les routes, les forets, les eaux et la pierre noire.</p></article>
      <article class="card"><h3>Les Forest Fools</h3><p>Scouts, wanderers and reckless adventurers. People call them fools because they enter cursed forests and lost roads where soldiers refuse to go.</p></article>
    </div>
""", "lore"),
        section("Intro cinematique", "textes et assets", build_intro_section(), "intro"),
        section("Progression", "structure actuelle", """
    <div class="grid two">
      <article class="card"><h3>Mosswake</h3><p>Reach level 2, reveal Slime Hollow, defeat Slime King, gain Harbor Pass, sail to Crownport.</p></article>
      <article class="card"><h3>Crownvale</h3><p>Speak to King Rowen, defeat Hollow Baron, gain Greenmarch Pass.</p></article>
      <article class="card"><h3>Greenmarch</h3><p>Speak to Elder Maelis, defeat Thornwell Warden, gain Scalefen Pass.</p></article>
      <article class="card"><h3>Scalefen / Ashenreach</h3><p>Help Matriarch Sytha, defeat Mirejaw Matriarch, reach Highpass, follow the dragon trail.</p></article>
    </div>
""", "progression"),
        section("Quetes", "quetes principales et villageoises prevues", build_quests_section(), "quetes"),
        section("Cartes", "maps fixes, coordonnees et points d'interet", build_maps_section(), "maps"),
        section("Lieux et textes", "tous les textes de lieux et sous-lieux", build_locations_section(), "locations"),
        section("Dialogues", "dialogues scenario et templates NPC", build_dialogues_section(), "dialogues"),
        section("Items", "armes, armures, consommables, misc", build_items_section(), "items"),
        section("Sorts", "magie achetable et utilisable en combat", build_spells_section(), "spells"),
        section("Monstres", "tous les pools ennemis et boss", build_monsters_section(), "monsters"),
        section("Loot", "tiers de regions, armes et armures", build_loot_section(), "loot"),
        section("Creation de personnage", "races, genres, classes, bonus", build_character_section(), "characters"),
        section("Commandes", "terminal gameplay", build_commands_section(), "commands"),
    ]
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Forest Fools - Wiki complet</title>
<link rel="icon" type="image/png" href="favicon.png">
<style>{CSS}</style>
</head>
<body id="top">
<div class="page">
  <header class="hero">
    <div>
      <p class="kicker">Wiki complet du projet</p>
      <h1>The Forest Fools</h1>
      <p>Base de donnees du jeu : lore, dialogues, quetes, cartes, lieux, items, equipements, sorts, monstres, loot et commandes.</p>
    </div>
  </header>
  <nav class="toc" aria-label="Sommaire">{nav_html}</nav>
  {''.join(content)}
  <p class="footer"><a href="#top">Retour en haut</a> | <a href="index.html">Accueil</a></p>
</div>
</body>
</html>
"""


def main() -> None:
    out = ROOT / "web" / "wiki.html"
    out.write_text(build_html(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
