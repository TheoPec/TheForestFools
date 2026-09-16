"""Fixed world maps for the story progression."""

from data.config import COLS_10, COLS_26, COLS_52

TILE_CODE_TYPES = {
    "~": "water",
    ".": "plains",
    "T": "forest",
    "V": "village",
    "P": "port",
    "S": "slime_lair",
    "O": "cave",
    "#": "castle",
    "X": "dungeon",
    "K": "capital",
    "D": "dragon_lair",
}

REGIONS = {
    "crownvale": "Crownvale",
    "greenmarch": "Greenmarch",
    "scalefen": "Scalefen",
    "ashenreach": "Ashenreach",
}

REGION_ALIASES = {
    "scalefen": "scalefen",
}

REGION_BOUNDS = {
    "crownvale": {"cols": COLS_52[:26], "rows": range(1, 27)},
    "greenmarch": {"cols": COLS_52[26:], "rows": range(1, 27)},
    "scalefen": {"cols": COLS_52[:26], "rows": range(27, 53)},
    "ashenreach": {"cols": COLS_52[26:], "rows": range(27, 53)},
}

REGION_PASSES = {
    "crownvale": None,
    "greenmarch": "greenmarch_pass",
    "scalefen": "scalefen_pass",
    "ashenreach": "ashenreach_pass",
}

REGION_ENTRANCES = {
    "crownvale": ("D", 23),
    "greenmarch": ("B", 13),
    "scalefen": ("B", 13),
    "ashenreach": ("M", 4),
}


def _blank(cols, row_count, fill="~"):
    return [[fill for _ in cols] for _ in range(row_count)]


def _set(grid, cols, pos, code):
    col, row = pos
    grid[row - 1][cols.index(col)] = code


def _paint_ellipse(grid, cols, cx, cy, rx, ry, code):
    for row_index, row in enumerate(grid, start=1):
        for col_index, _ in enumerate(cols, start=1):
            x = (col_index - cx) / rx
            y = (row_index - cy) / ry
            if x * x + y * y <= 1:
                row[col_index - 1] = code


def _paint_rect(grid, cols, left_col, top_row, right_col, bottom_row, code):
    left = cols.index(left_col) + 1
    right = cols.index(right_col) + 1
    for row in range(top_row, bottom_row + 1):
        for col_index in range(left, right + 1):
            grid[row - 1][col_index - 1] = code


def _rows(grid):
    return ["".join(row) for row in grid]


def _build_mosswake_rows():
    return [
        "~~~~~~~~~~",
        "~~~..~~~~~",
        "~~~..~~~~~",
        "~~~...~~~~",
        "~~~.V.P~~~",
        "~~~T...~~~",
        "~~~~T..~~~",
        "~~~..S.~~~",
        "~~~....~~~",
        "~~~~~~~~~~",
    ]


def _build_continent_rows():
    grid = _blank(COLS_52, 52, ".")

    for row in range(1, 53):
        for col_index in range(1, 53):
            if row in (1, 52) or col_index in (1, 52):
                grid[row - 1][col_index - 1] = "~"

    _paint_rect(grid, COLS_52, "F", 4, "Q", 12, "T")
    _paint_rect(grid, COLS_52, "R", 9, "Z", 20, "T")
    _paint_rect(grid, COLS_52, "AA", 3, "AL", 12, "T")
    _paint_rect(grid, COLS_52, "AN", 16, "AW", 25, "T")
    _paint_rect(grid, COLS_52, "G", 33, "Q", 45, "T")
    _paint_rect(grid, COLS_52, "AB", 34, "AP", 49, "T")

    for pos, code in {
        ("D", 23): "P",
        ("M", 10): "K",
        ("H", 14): "#",
        ("R", 18): "O",
        ("X", 22): "V",
        ("AA", 16): "V",
        ("AJ", 9): "V",
        ("AR", 20): "O",
        ("M", 32): "#",
        ("F", 43): "V",
        ("S", 39): "O",
        ("AA", 32): "X",
        ("AM", 42): "D",
        ("AS", 36): "X",
    }.items():
        _set(grid, COLS_52, pos, code)
    return _rows(grid)


def _build_crownvale_rows():
    grid = _blank(COLS_26, 26, ".")
    _paint_rect(grid, COLS_26, "A", 1, "C", 26, "~")
    _paint_rect(grid, COLS_26, "A", 1, "Z", 2, "~")
    _paint_rect(grid, COLS_26, "A", 24, "Z", 26, "~")
    for pos, code in {
        ("D", 23): "P",
        ("M", 12): "K",
        ("H", 9): "#",
        ("Q", 17): "V",
        ("V", 4): "T",
        ("S", 20): "T",
    }.items():
        _set(grid, COLS_26, pos, code)
    return _rows(grid)


def _build_greenmarch_rows():
    grid = _blank(COLS_26, 26, ".")
    _paint_rect(grid, COLS_26, "A", 1, "Z", 2, "~")
    _paint_rect(grid, COLS_26, "K", 24, "T", 26, "~")
    _paint_rect(grid, COLS_26, "A", 10, "C", 17, ".")
    _paint_ellipse(grid, COLS_26, 13, 7, 4, 3, ".")
    _paint_ellipse(grid, COLS_26, 10, 15, 4, 3, ".")
    _paint_ellipse(grid, COLS_26, 18, 19, 4, 3, ".")
    _paint_rect(grid, COLS_26, "Y", 3, "Z", 24, ".")
    for pos, code in {
        ("B", 13): "T",
        ("M", 7): "V",
        ("J", 15): "O",
        ("R", 19): "T",
        ("W", 10): "X",
    }.items():
        _set(grid, COLS_26, pos, code)
    return _rows(grid)


def _build_scalefen_rows():
    grid = _blank(COLS_26, 26, ".")
    _paint_rect(grid, COLS_26, "Y", 1, "Z", 26, "~")
    _paint_rect(grid, COLS_26, "A", 1, "B", 4, "T")
    _paint_rect(grid, COLS_26, "A", 1, "A", 26, "~")
    _paint_ellipse(grid, COLS_26, 9, 6, 4, 3, "~")
    _paint_ellipse(grid, COLS_26, 15, 12, 5, 3, "~")
    _paint_ellipse(grid, COLS_26, 8, 20, 3, 3, "~")
    _paint_ellipse(grid, COLS_26, 20, 18, 3, 4, "~")
    for pos, code in {
        ("B", 13): "V",
        ("H", 18): "T",
        ("M", 12): "#",
        ("S", 17): "O",
        ("X", 8): "P",
    }.items():
        _set(grid, COLS_26, pos, code)
    return _rows(grid)


def _build_ashenreach_rows():
    grid = _blank(COLS_26, 26, ".")
    _paint_rect(grid, COLS_26, "A", 1, "F", 4, ".")
    _paint_rect(grid, COLS_26, "Y", 1, "Z", 26, "~")
    _paint_rect(grid, COLS_26, "A", 24, "Z", 26, "~")
    _paint_rect(grid, COLS_26, "A", 10, "B", 20, "~")
    for pos, code in {
        ("M", 4): "O",
        ("F", 18): "X",
        ("N", 13): "O",
        ("T", 10): "X",
        ("U", 20): "D",
    }.items():
        _set(grid, COLS_26, pos, code)
    return _rows(grid)


FIXED_MAPS = {
    "mosswake": {
        "name": "Mosswake Isle",
        "short_name": "Mosswake",
        "cols": COLS_10,
        "row_numbers": range(1, 11),
        "start_pos": ("E", 5),
        "arrival_pos": ("G", 5),
        "fully_revealed": False,
        "start_revealed": {("E", 5), ("D", 6), ("E", 7)},
        "rows": _build_mosswake_rows(),
        "named_tiles": {
            ("E", 5): {"id": "greenhollow", "name": "Greenhollow Village", "revealed": True},
            ("D", 6): {"id": "old_fern_forest", "name": "Old Fern Forest", "revealed": True},
            ("E", 7): {"id": "mossroot_forest", "name": "Mossroot Forest", "revealed": True},
            ("F", 8): {"id": "slime_hollow", "name": "Slime Hollow", "boss": "slime_king"},
            ("G", 5): {"id": "southwake_port", "name": "Southwake Port"},
        },
    },
    "continent": {
        "name": "Mainland of Elarion",
        "short_name": "Elarion",
        "cols": COLS_52,
        "row_numbers": range(1, 53),
        "start_pos": ("D", 23),
        "arrival_pos": ("D", 23),
        "overview_only": True,
        "fully_revealed": False,
        "start_revealed": {("D", 23)},
        "rows": _build_continent_rows(),
        "named_tiles": {
            ("D", 23): {"id": "crownport", "name": "Crownport", "revealed": True},
            ("M", 10): {"id": "crown_capital", "name": "Crownvale Capital"},
            ("H", 14): {"id": "crownvale_keep", "name": "Crownvale Keep"},
            ("X", 22): {"id": "westmere_village", "name": "Westmere Village"},
            ("AJ", 9): {"id": "greenmarch_village", "name": "Greenmarch Village"},
            ("M", 32): {"id": "scalefen_marshhold", "name": "Scalefen Marshhold"},
            ("F", 43): {"id": "lowbridge_village", "name": "Lowbridge Village"},
            ("AM", 42): {"id": "ashen_dragon_lair", "name": "Ashenreach Dragon Lair"},
        },
    },
    "crownvale": {
        "name": "Crownvale",
        "short_name": "Crownvale",
        "cols": COLS_26,
        "row_numbers": range(1, 27),
        "start_pos": ("D", 23),
        "arrival_pos": ("D", 23),
        "fully_revealed": False,
        "start_revealed": {("D", 23), ("M", 12)},
        "rows": _build_crownvale_rows(),
        "named_tiles": {
            ("D", 23): {"id": "crownport", "name": "Crownport", "revealed": True},
            ("M", 12): {"id": "crown_capital", "name": "Crownvale Capital", "revealed": True},
            ("H", 9): {"id": "crownvale_keep", "name": "Crownvale Keep", "boss": "hollow_baron"},
            ("Q", 17): {"id": "fairmeadow", "name": "Fairmeadow Village"},
            ("V", 4): {"id": "northwatch_woods", "name": "Northwatch Woods", "enemy_pool": "crownvale_woods"},
            ("S", 20): {"id": "sunmere_woods", "name": "Sunmere Woods", "enemy_pool": "crownvale_woods"},
        },
    },
    "greenmarch": {
        "name": "Greenmarch",
        "short_name": "Greenmarch",
        "cols": COLS_26,
        "row_numbers": range(1, 27),
        "start_pos": ("B", 13),
        "arrival_pos": ("B", 13),
        "fully_revealed": False,
        "start_revealed": {("B", 13)},
        "rows": _build_greenmarch_rows(),
        "named_tiles": {
            ("B", 13): {"id": "greenmarch_westwood", "name": "Westwood Gate", "revealed": True},
            ("M", 7): {"id": "eldergrove", "name": "Eldergrove"},
            ("J", 15): {"id": "rootglass_cave", "name": "Rootglass Cave"},
            ("R", 19): {"id": "deep_briar", "name": "Deep Briar", "enemy_pool": "greenmarch_forest"},
            ("W", 10): {"id": "thornwell_ruins", "name": "Thornwell Ruins", "boss": "thornwell_warden"},
        },
    },
    "scalefen": {
        "name": "Scalefen",
        "short_name": "Scalefen",
        "cols": COLS_26,
        "row_numbers": range(1, 27),
        "start_pos": ("B", 13),
        "arrival_pos": ("B", 13),
        "fully_revealed": False,
        "start_revealed": {("B", 13)},
        "rows": _build_scalefen_rows(),
        "named_tiles": {
            ("B", 13): {"id": "fenwatch", "name": "Fenwatch Village", "revealed": True},
            ("H", 18): {"id": "reedmire", "name": "Reedmire", "enemy_pool": "scalefen_marsh"},
            ("M", 12): {"id": "scalefen_marshhold", "name": "Scalefen Marshhold"},
            ("S", 17): {"id": "sunken_grotto", "name": "Sunken Grotto", "boss": "mirejaw_matriarch"},
            ("X", 8): {"id": "eastwake_port", "name": "Eastwake Port"},
        },
    },
    "ashenreach": {
        "name": "Ashenreach",
        "short_name": "Ashenreach",
        "cols": COLS_26,
        "row_numbers": range(1, 27),
        "start_pos": ("M", 4),
        "arrival_pos": ("M", 4),
        "fully_revealed": False,
        "start_revealed": {("M", 4)},
        "rows": _build_ashenreach_rows(),
        "named_tiles": {
            ("M", 4): {"id": "highpass", "name": "Highpass", "enemy_pool": "ashenreach_wastes"},
            ("F", 18): {"id": "blackmouth_dungeon", "name": "Blackmouth Dungeon", "enemy_pool": "ashenreach_wastes"},
            ("N", 13): {"id": "ash_cavern", "name": "Ash Cavern", "enemy_pool": "ashenreach_wastes"},
            ("T", 10): {"id": "broken_spire", "name": "Broken Spire", "enemy_pool": "ashenreach_wastes"},
            ("U", 20): {"id": "ashen_dragon_lair", "name": "Ashenreach Dragon Lair"},
        },
    },
}


def region_for_pos(pos):
    """Return the continent region key for a map coordinate."""
    col, row = pos
    col_index = COLS_52.index(col) + 1
    west = col_index <= 26
    north = row <= 26
    if west and north:
        return "crownvale"
    if not west and north:
        return "greenmarch"
    if west and not north:
        return "scalefen"
    return "ashenreach"
