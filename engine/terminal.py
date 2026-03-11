"""Terminal helpers: ANSI colors, styled text, console font setup."""

import os
import sys

try:
    import ctypes
except ImportError:
    ctypes = None


# ANSI color codes
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GREY    = "\033[90m"
    # Backgrounds
    BG_BLUE   = "\033[44m"
    BG_YELLOW = "\033[43m"
    BG_GREEN  = "\033[42m"
    BG_DGREEN = "\033[48;5;22m"


TILE_COLORS = {
    "plains":      C.DIM,
    "forest":      C.GREEN,
    "village":     C.YELLOW,
    "cave":        C.GREY,
    "castle":      C.MAGENTA,
    "dungeon":     C.RED,
    "capital":     C.BOLD + C.YELLOW,
    "dragon_lair": C.RED + C.BOLD,
    "port":        C.BOLD + C.WHITE,
    "water":       C.BOLD + C.BLUE,
}

BG_COLORS = {
    "water":      C.BG_BLUE,
    "sand":       C.BG_YELLOW,
    "grass":      C.BG_GREEN,
    "dark_grass": C.BG_DGREEN,
}


def styled(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET


def set_gothic_font():
    """Try to set a gothic/medieval looking console font on Windows."""
    if not sys.stdout.isatty():
        return
    try:
        os.system('mode con cols=120 lines=40')
        if os.name == 'nt' and ctypes:
            LF_FACESIZE = 32
            STD_OUTPUT_HANDLE = -11

            class COORD(ctypes.Structure):
                _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

            class CONSOLE_FONT_INFOEX(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("nFont", ctypes.c_ulong),
                    ("dwFontSize", COORD),
                    ("FontFamily", ctypes.c_uint),
                    ("FontWeight", ctypes.c_uint),
                    ("FaceName", ctypes.c_wchar * LF_FACESIZE),
                ]

            kernel32 = ctypes.windll.kernel32
            hOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            font = CONSOLE_FONT_INFOEX()
            font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
            font.dwFontSize.X = 0
            font.dwFontSize.Y = 18
            font.FontFamily = 54
            font.FontWeight = 400
            for font_name in ["Consolas", "Courier New", "Lucida Console"]:
                font.FaceName = font_name
                if kernel32.SetCurrentConsoleFontEx(hOut, False, ctypes.byref(font)):
                    break
    except Exception:
        pass
