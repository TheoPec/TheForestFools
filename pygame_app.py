"""Pygame interface for The Forest Fools.

The interface is passive except for the central terminal: every gameplay action
still goes through the existing command system.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from data.character_options import RACES, GENDERS, CLASSES, DEFAULT_CHARACTER
from data.armors import ARMORS
from data.config import (
    PLAYER_START_ARMOR,
    PLAYER_START_ATTACK,
    PLAYER_START_HP,
    PLAYER_START_MANA,
    PLAYER_START_WEAPON,
)
from data.locations import TILE_NAMES, TILE_SYMBOLS
from data.spells import SPELLS
from data.weapons import WEAPONS
from game import Game


TITLE = "The Forest Fools"
VERSION = "1.0.5"
WINDOW_SIZE = (1440, 810)
MIN_SIZE = (960, 540)
FPS = 60


BG = (8, 10, 9)
PANEL_BG = (17, 21, 19)
PANEL_INNER = (12, 15, 14)
TEXT = (221, 232, 219)
MUTED = (137, 154, 140)
DIM = (83, 96, 88)
RED = (232, 48, 54)
GREEN = (51, 190, 89)
BLUE = (75, 94, 230)
PURPLE = (176, 79, 181)
YELLOW = (224, 184, 75)
CYAN = (91, 206, 220)
WHITE = (245, 246, 236)
BLACK = (0, 0, 0)
TITLE_GREEN = (38, 89, 54)
TITLE_SHADOW = (248, 237, 184)
MENU_TEXT = (34, 54, 43)
MENU_SELECTED = (183, 122, 38)


TERRAIN_COLORS = {
    "unknown": (41, 45, 43),
    "water": (28, 61, 117),
    "sand": (151, 127, 72),
    "grass": (40, 94, 45),
    "dark_grass": (23, 61, 35),
}

TYPE_COLORS = {
    "unknown": (41, 45, 43),
    "plains": (76, 91, 76),
    "forest": (53, 153, 73),
    "slime_lair": (88, 196, 88),
    "village": (189, 160, 76),
    "cave": (123, 127, 130),
    "castle": (153, 90, 178),
    "dungeon": (170, 48, 56),
    "capital": (229, 195, 76),
    "dragon_lair": (221, 46, 42),
    "port": (200, 213, 215),
    "water": (47, 93, 168),
}

MENU_IMAGE_DIR = ("assets", "images", "menu")
INTRO_IMAGE_DIR = ("assets", "images", "intro")
CHARACTER_SELECT_DIR = ("assets", "images", "character_select")
CHARACTER_IMAGE_DIR = ("assets", "images", "characters")
MAP_IMAGE_DIR = ("assets", "images", "maps")
INFO_BACKGROUND_DIR = ("assets", "images", "info_backgrounds")
MUSIC_DIR = ("assets", "music")

INTRO_SCENE_DATA = [
    {
        "key": "01_valley",
        "title": "The Quiet Valley",
        "lines": [
            "The valley was peaceful.",
            "Green fields stretched beneath the castle.",
            "No one believed the old legends anymore.",
        ],
        "accent": GREEN,
    },
    {
        "key": "02_burning_road",
        "title": "The First Sign",
        "lines": [
            "Then the roads began to burn.",
            "No army was seen.",
            "Only smoke rising beyond the hills.",
        ],
        "accent": RED,
    },
    {
        "key": "03_silent_towers",
        "title": "Silent Towers",
        "lines": [
            "The watchtowers fell silent.",
            "No bells rang.",
            "No guards returned.",
        ],
        "accent": YELLOW,
    },
    {
        "key": "04_council",
        "title": "The King's Question",
        "lines": [
            "The king did not ask for war.",
            "He asked for someone brave enough to enter the forest.",
            "Or foolish enough.",
        ],
        "accent": PURPLE,
    },
    {
        "key": "05_forest_fools",
        "title": "Forest Fools",
        "lines": [
            "They called them Forest Fools.",
            "Scouts, wanderers, forgotten names.",
            "The ones who walked where kingdoms ended.",
        ],
        "accent": CYAN,
    },
]


def resource_path(*parts: str) -> Path:
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base).joinpath(*parts)


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


@dataclass
class Fonts:
    title: pygame.font.Font
    menu_title: pygame.font.Font
    scene_title: pygame.font.Font
    heading: pygame.font.Font
    body: pygame.font.Font
    small: pygame.font.Font
    menu: pygame.font.Font
    intro: pygame.font.Font
    terminal: pygame.font.Font
    terminal_small: pygame.font.Font
    map: pygame.font.Font


@dataclass
class Animation:
    frames: list[pygame.Surface] = field(default_factory=list)
    fps: float = 6.0

    def get_frame(self, elapsed_ms: int) -> pygame.Surface | None:
        if not self.frames:
            return None
        index = int((elapsed_ms / 1000) * self.fps) % len(self.frames)
        return self.frames[index]


@dataclass
class IntroScene:
    key: str
    title: str
    lines: list[str]
    accent: tuple[int, int, int]
    image: pygame.Surface | None = None
    animation: Animation | None = None


def load_font(path: Path, size: int, fallback_name: str | None = None) -> pygame.font.Font:
    try:
        if path.exists():
            return pygame.font.Font(str(path), size)
    except pygame.error:
        pass
    return pygame.font.SysFont(fallback_name or "consolas", size)


def load_image(path: Path) -> pygame.Surface | None:
    try:
        if path.exists():
            return pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None
    return None


def load_animation(directory_parts: tuple[str, ...], stem: str, fps: float = 6.0) -> Animation:
    directory = resource_path(*directory_parts)
    frames = []
    for index in range(100):
        frame = load_image(directory / f"{stem}_{index:03}.png")
        if frame is None:
            if index == 0:
                continue
            break
        frames.append(frame)

    if not frames:
        still = load_image(directory / f"{stem}.png")
        if still is not None:
            frames.append(still)

    return Animation(frames=frames, fps=fps)


def scale_nearest(surface: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    return pygame.transform.scale(surface, (max(1, size[0]), max(1, size[1])))


def draw_image_fit(target, image: pygame.Surface, rect: pygame.Rect, cover=False):
    src_w, src_h = image.get_size()
    if src_w <= 0 or src_h <= 0:
        return
    scale = max(rect.w / src_w, rect.h / src_h) if cover else min(rect.w / src_w, rect.h / src_h)
    size = (int(src_w * scale), int(src_h * scale))
    scaled = scale_nearest(image, size)
    target.blit(scaled, (rect.centerx - scaled.get_width() // 2, rect.centery - scaled.get_height() // 2))


def find_music_file(stem: str) -> Path | None:
    music_dir = resource_path(*MUSIC_DIR)
    for ext in (".ogg", ".wav", ".mp3"):
        candidate = music_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def make_fonts() -> Fonts:
    old_london = resource_path("fonts", "OldLondon.ttf")
    enchanted = resource_path("fonts", "Enchanted Land.otf")
    return Fonts(
        title=load_font(old_london, 56, "georgia"),
        menu_title=pygame.font.SysFont("georgia", 72, bold=True),
        scene_title=load_font(old_london, 36, "georgia"),
        heading=load_font(enchanted, 34, "consolas"),
        body=load_font(enchanted, 25, "consolas"),
        small=load_font(enchanted, 20, "consolas"),
        menu=pygame.font.SysFont("consolas", 30, bold=True),
        intro=pygame.font.SysFont("consolas", 22),
        terminal=pygame.font.SysFont("consolas", 17),
        terminal_small=pygame.font.SysFont("consolas", 14),
        map=pygame.font.SysFont("consolas", 16, bold=True),
    )


def draw_text(surface, font, text, pos, color=TEXT):
    rendered = font.render(str(text), True, color)
    surface.blit(rendered, pos)
    return rendered.get_rect(topleft=pos)


def draw_shadowed_text(surface, font, text, center_pos, color, shadow_color=BLACK, offset=3):
    rendered_shadow = font.render(str(text), True, shadow_color)
    rendered = font.render(str(text), True, color)
    x = center_pos[0] - rendered.get_width() // 2
    y = center_pos[1] - rendered.get_height() // 2
    surface.blit(rendered_shadow, (x + offset, y + offset))
    surface.blit(rendered, (x, y))
    return rendered.get_rect(topleft=(x, y))


def draw_outlined_text(surface, font, text, center_pos, color, outline_color, outline=3):
    text = str(text)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center_pos)
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx == 0 and dy == 0:
                continue
            if dx * dx + dy * dy <= outline * outline + 1:
                shadow = font.render(text, True, outline_color)
                surface.blit(shadow, shadow.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy)))
    surface.blit(rendered, rect)
    return rect


def draw_text_right(surface, font, text, rect, y, color=TEXT):
    rendered = font.render(str(text), True, color)
    surface.blit(rendered, (rect.right - rendered.get_width(), y))
    return rendered.get_rect(topright=(rect.right, y))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    if text == "":
        return [""]
    words = str(text).split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
            continue

        if current:
            lines.append(current)
            current = word
        else:
            piece = ""
            for char in word:
                candidate_piece = piece + char
                if font.size(candidate_piece)[0] <= max_width:
                    piece = candidate_piece
                else:
                    if piece:
                        lines.append(piece)
                    piece = char
            current = piece
    if current:
        lines.append(current)
    return lines or [""]


def draw_panel(surface, rect: pygame.Rect, border_color, title: str, font: pygame.font.Font):
    pygame.draw.rect(surface, border_color, rect, border_radius=6)
    inner = rect.inflate(-12, -12)
    pygame.draw.rect(surface, PANEL_BG, inner, border_radius=4)
    title_rect = pygame.Rect(inner.x + 12, inner.y + 8, inner.w - 24, 30)
    draw_text(surface, font, title.upper(), title_rect.topleft, border_color)
    pygame.draw.line(surface, border_color, (inner.x + 12, inner.y + 44), (inner.right - 12, inner.y + 44), 1)
    return pygame.Rect(inner.x + 14, inner.y + 56, inner.w - 28, inner.h - 70)


def draw_bar(surface, rect: pygame.Rect, value: int, max_value: int, color, label: str, font):
    pygame.draw.rect(surface, PANEL_INNER, rect, border_radius=4)
    pygame.draw.rect(surface, (43, 49, 45), rect, width=1, border_radius=4)
    pct = 0 if max_value <= 0 else max(0, min(1, value / max_value))
    fill = pygame.Rect(rect.x + 2, rect.y + 2, int((rect.w - 4) * pct), rect.h - 4)
    if fill.w > 0:
        pygame.draw.rect(surface, color, fill, border_radius=3)
    text = f"{label}: {value}/{max_value}"
    rendered = font.render(text, True, WHITE)
    surface.blit(rendered, (rect.centerx - rendered.get_width() // 2, rect.centery - rendered.get_height() // 2))


class ForestFoolsApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.audio_enabled = False
        self.init_audio()
        self.menu_animation = load_animation(MENU_IMAGE_DIR, "menu_bg", fps=6.0)
        self.intro_scenes = self.load_intro_scenes()
        self.character_background = load_image(resource_path(*CHARACTER_SELECT_DIR) / "background.png")
        self.character_portraits = self.load_character_portraits()
        self.map_images = self.load_map_images()
        self.map_frame_images = self.load_map_frame_images()
        self.info_backgrounds = self.load_info_backgrounds()
        self.running = True
        self.mode = "menu"
        self.menu_items = ["New Game", "Continue", "Options", "Quit"]
        self.menu_index = 0
        self.menu_notice = ""
        self.menu_fade_elapsed = 0
        self.menu_fade_duration = 900
        self.game: Game | None = None
        self.input_buffer = ""
        self.command_history: list[str] = []
        self.history_index: int | None = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.elapsed_ms = 0
        self.intro_index = 0
        self.intro_scene_elapsed = 0
        self.intro_visible_chars = 0
        self.intro_chars_per_second = 42
        self.intro_full_revealed_at: int | None = None
        self.race_keys = list(RACES.keys())
        self.gender_keys = ["female", "male"]
        self.class_keys = list(CLASSES.keys())
        self.character_choice = dict(DEFAULT_CHARACTER)
        self.character_focus = 0
        self.character_rows = ["race", "gender", "class", "start"]

    def run(self):
        pygame.key.start_text_input()
        while self.running:
            dt = self.clock.tick(FPS)
            self.elapsed_ms += dt
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            if self.mode == "menu_fade":
                self.update_menu_fade(dt)
            if self.mode == "intro":
                self.update_intro(dt)

            for event in pygame.event.get():
                self.handle_event(event)

            self.draw()
            pygame.display.flip()

        pygame.key.stop_text_input()
        pygame.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(WINDOW_SIZE)
            return

        if self.mode == "menu":
            self.handle_menu_event(event)
        elif self.mode == "menu_fade":
            self.handle_menu_fade_event(event)
        elif self.mode == "intro":
            self.handle_intro_event(event)
        elif self.mode == "character_select":
            self.handle_character_select_event(event)
        elif self.mode == "game":
            self.handle_game_event(event)

    def init_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error:
            self.audio_enabled = False

    def play_music(self, stem: str, loops=-1, fade_ms=900):
        if not self.audio_enabled:
            return
        path = find_music_file(stem)
        if path is None:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        except pygame.error:
            pass

    def stop_music(self, fade_ms=700):
        if not self.audio_enabled:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            pass

    def load_intro_scenes(self) -> list[IntroScene]:
        scenes = []
        for scene_data in INTRO_SCENE_DATA:
            animation = load_animation(INTRO_IMAGE_DIR, scene_data["key"], fps=6.0)
            if scene_data["key"] == "01_valley" and not animation.frames and self.menu_animation.frames:
                animation = self.menu_animation
            scenes.append(IntroScene(
                key=scene_data["key"],
                title=scene_data["title"],
                lines=list(scene_data["lines"]),
                accent=scene_data["accent"],
                animation=animation if animation.frames else None,
                image=animation.frames[0] if animation.frames else None,
            ))
        return scenes

    def load_character_portraits(self) -> dict[tuple[str, ...], Animation]:
        portraits = {}
        for race_key in RACES:
            for gender_key in GENDERS:
                for class_key in CLASSES:
                    animation = load_animation(CHARACTER_IMAGE_DIR, f"{race_key}_{gender_key}_{class_key}", fps=6.0)
                    if animation.frames:
                        portraits[(race_key, gender_key, class_key)] = animation
                animation = load_animation(CHARACTER_IMAGE_DIR, f"{race_key}_{gender_key}", fps=6.0)
                if animation.frames:
                    portraits[(race_key, gender_key)] = animation
        return portraits

    def load_map_images(self) -> dict[str, pygame.Surface]:
        images = {}
        map_dir = resource_path(*MAP_IMAGE_DIR)
        for key in ("mosswake", "continent", "crownvale", "greenmarch", "scalefen", "ashenreach"):
            image = load_image(map_dir / f"{key}.png")
            if image:
                images[key] = image
        return images

    def load_map_frame_images(self) -> dict[str, pygame.Surface]:
        images = {}
        map_dir = resource_path(*MAP_IMAGE_DIR)
        for key in ("map_paper", "mosswake_paper", "continent_paper", "crownvale_paper", "greenmarch_paper", "scalefen_paper", "ashenreach_paper"):
            image = load_image(map_dir / f"{key}.png")
            if image:
                images[key] = image
        return images

    def load_info_backgrounds(self) -> dict[str, pygame.Surface]:
        images = {}
        image_dir = resource_path(*INFO_BACKGROUND_DIR)
        for key in (
            "mosswake",
            "crownvale",
            "greenmarch",
            "scalefen",
            "ashenreach",
            "continent",
            "village",
            "capital",
            "cave",
            "port",
            "castle",
            "forest",
            "dragon_lair",
            "slime_lair",
        ):
            image = load_image(image_dir / f"{key}.png")
            if image:
                images[key] = image
        return images

    def get_character_animation(self, race_key: str, gender_key: str, class_key: str) -> Animation | None:
        return (
            self.character_portraits.get((race_key, gender_key, class_key))
            or self.character_portraits.get((race_key, gender_key))
        )

    def handle_menu_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            self.menu_notice = ""
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            self.menu_notice = ""
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.activate_menu_item()
        elif event.key in (pygame.K_1, pygame.K_KP1):
            self.menu_index = 0
            self.activate_menu_item()
        elif event.key in (pygame.K_2, pygame.K_KP2):
            self.menu_index = 1
            self.activate_menu_item()
        elif event.key in (pygame.K_3, pygame.K_KP3):
            self.menu_index = 2
            self.activate_menu_item()
        elif event.key in (pygame.K_4, pygame.K_KP4, pygame.K_ESCAPE):
            self.menu_index = 3
            self.activate_menu_item()

    def activate_menu_item(self):
        item = self.menu_items[self.menu_index]
        if item == "New Game":
            self.start_menu_fade()
        elif item == "Continue":
            self.menu_notice = "Continue sera ajoute avec la sauvegarde."
        elif item == "Options":
            self.menu_notice = "Options audio et affichage arriveront apres le prototype."
        elif item == "Quit":
            self.running = False

    def start_menu_fade(self):
        self.mode = "menu_fade"
        self.menu_notice = ""
        self.menu_fade_elapsed = 0

    def update_menu_fade(self, dt):
        self.menu_fade_elapsed += dt
        if self.menu_fade_elapsed >= self.menu_fade_duration:
            self.start_intro()

    def handle_menu_fade_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.start_intro()

    def start_intro(self):
        self.mode = "intro"
        self.menu_notice = ""
        self.intro_index = 0
        self.intro_scene_elapsed = 0
        self.intro_visible_chars = 0
        self.intro_full_revealed_at = None
        self.play_music("intro", loops=-1)

    def start_character_select(self):
        self.mode = "character_select"
        self.character_choice = dict(DEFAULT_CHARACTER)
        self.character_focus = 0
        self.input_buffer = ""
        self.history_index = None
        self.play_music("character_select", loops=-1)

    def start_new_game(self):
        self.stop_music()
        self.game = Game()
        self.game.graphical_mode = True
        self.game.configure_character(
            self.character_choice.get("race"),
            self.character_choice.get("gender"),
            self.character_choice.get("class"),
        )
        race_name = RACES[self.character_choice["race"]]["name"]
        gender_name = GENDERS[self.character_choice["gender"]]["name"]
        class_name = CLASSES[self.character_choice["class"]]["name"]
        self.game._append_message("The Forest Fools")
        self.game._append_message("New game started.")
        self.game._append_message(f"Character: {race_name} / {gender_name} / {class_name}.")
        self.game._append_message("Type help for commands.")
        self.input_buffer = ""
        self.command_history = []
        self.history_index = None
        self.mode = "game"
        self.game.process_command("look")

    def update_intro(self, dt):
        scene = self.current_intro_scene()
        if scene is None:
            return
        self.intro_scene_elapsed += dt
        total_chars = self.intro_text_length(scene)
        if self.intro_visible_chars < total_chars:
            self.intro_visible_chars = min(
                total_chars,
                self.intro_visible_chars + max(1, int(self.intro_chars_per_second * dt / 1000)),
            )
            if self.intro_visible_chars >= total_chars:
                self.intro_full_revealed_at = self.intro_scene_elapsed
        elif self.intro_full_revealed_at is None:
            self.intro_full_revealed_at = self.intro_scene_elapsed

    def current_intro_scene(self) -> IntroScene | None:
        if not self.intro_scenes:
            return None
        return self.intro_scenes[self.intro_index]

    def intro_text_length(self, scene: IntroScene) -> int:
        return sum(len(line) for line in scene.lines)

    def reveal_or_advance_intro(self):
        scene = self.current_intro_scene()
        if scene is None:
            self.start_character_select()
            return
        total_chars = self.intro_text_length(scene)
        if self.intro_visible_chars < total_chars:
            self.intro_visible_chars = total_chars
            self.intro_full_revealed_at = self.intro_scene_elapsed
            return
        self.next_intro_scene()

    def next_intro_scene(self):
        if self.intro_index >= len(self.intro_scenes) - 1:
            self.start_character_select()
            return
        self.intro_index += 1
        self.intro_scene_elapsed = 0
        self.intro_visible_chars = 0
        self.intro_full_revealed_at = None

    def handle_intro_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.start_character_select()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            self.reveal_or_advance_intro()

    def handle_character_select_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.character_focus = (self.character_focus - 1) % len(self.character_rows)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.character_focus = (self.character_focus + 1) % len(self.character_rows)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.cycle_character_option(-1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.cycle_character_option(1)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            if self.character_rows[self.character_focus] == "start":
                self.start_new_game()
            else:
                self.cycle_character_option(1)
        elif event.key == pygame.K_ESCAPE:
            self.mode = "menu"
            self.menu_notice = "New game cancelled."

    def cycle_character_option(self, direction: int):
        row = self.character_rows[self.character_focus]
        key_lists = {
            "race": self.race_keys,
            "gender": self.gender_keys,
            "class": self.class_keys,
        }
        keys = key_lists.get(row)
        if not keys:
            return
        current = self.character_choice[row]
        index = keys.index(current) if current in keys else 0
        self.character_choice[row] = keys[(index + direction) % len(keys)]

    def handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.submit_command()
                return
            if event.key == pygame.K_BACKSPACE:
                if event.mod & pygame.KMOD_CTRL:
                    self.input_buffer = self.input_buffer.rstrip()
                    self.input_buffer = self.input_buffer[: self.input_buffer.rfind(" ") + 1].rstrip()
                else:
                    self.input_buffer = self.input_buffer[:-1]
                self.history_index = None
                return
            if event.key == pygame.K_ESCAPE:
                self.mode = "menu"
                self.menu_notice = "Game paused."
                return
            if event.key == pygame.K_UP:
                self.recall_history(-1)
                return
            if event.key == pygame.K_DOWN:
                self.recall_history(1)
                return

        if event.type == pygame.TEXTINPUT:
            if event.text and event.text.isprintable():
                self.input_buffer += event.text
                self.history_index = None

    def recall_history(self, direction: int):
        if not self.command_history:
            return
        if self.history_index is None:
            self.history_index = len(self.command_history) if direction < 0 else len(self.command_history) - 1
        self.history_index = clamp(self.history_index + direction, 0, len(self.command_history) - 1)
        self.input_buffer = self.command_history[self.history_index]

    def submit_command(self):
        if not self.game:
            return
        command = self.input_buffer.strip()
        self.input_buffer = ""
        self.history_index = None
        if not command:
            return
        self.command_history.append(command)
        self.game.process_command(command)
        if not self.game.running:
            self.mode = "menu"
            self.menu_notice = "Journey ended."

    def draw(self):
        self.screen.fill(BG)
        self.draw_scanlines()
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "menu_fade":
            progress = min(1.0, self.menu_fade_elapsed / max(1, self.menu_fade_duration))
            self.draw_menu(overlay_alpha=int(255 * (1.0 - progress)))
        elif self.mode == "intro":
            self.draw_intro()
        elif self.mode == "character_select":
            self.draw_character_select()
        elif self.mode == "game":
            self.draw_game()

    def draw_scanlines(self):
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 4):
            pygame.draw.line(overlay, (255, 255, 255, 10), (0, y), (width, y))
        self.screen.blit(overlay, (0, 0))

    def draw_menu(self, overlay_alpha=255):
        self.draw_menu_background()
        if overlay_alpha <= 0:
            return

        width, height = self.screen.get_size()
        center_x = width // 2
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        draw_outlined_text(
            overlay,
            self.fonts.menu_title,
            TITLE.upper(),
            (center_x, 112),
            (255, 244, 184),
            (24, 62, 43),
            outline=4,
        )
        subtitle = self.fonts.terminal_small.render(f"Version {VERSION}", True, (248, 238, 190))
        subtitle_rect = subtitle.get_rect(center=(center_x, 170))
        subtitle_shadow = self.fonts.terminal_small.render(f"Version {VERSION}", True, (25, 45, 34))
        overlay.blit(subtitle_shadow, subtitle_shadow.get_rect(center=(center_x + 2, 172)))
        overlay.blit(subtitle, subtitle_rect)

        menu_y = int(height * 0.62)
        for i, item in enumerate(self.menu_items):
            selected = i == self.menu_index
            color = (255, 216, 90) if selected else (250, 248, 222)
            label = f"{i + 1}. {item}"
            if selected:
                label = f"> {label} <"
            draw_outlined_text(
                overlay,
                self.fonts.menu,
                label,
                (center_x, menu_y + i * 48),
                color,
                (18, 43, 30),
                outline=3,
            )

        if self.menu_notice:
            for i, line in enumerate(wrap_text(self.menu_notice, self.fonts.body, 620)):
                rendered = self.fonts.terminal.render(line, True, (255, 244, 184))
                shadow = self.fonts.terminal.render(line, True, (18, 43, 30))
                pos = (center_x - rendered.get_width() // 2, height - 115 + i * 26)
                overlay.blit(shadow, (pos[0] + 2, pos[1] + 2))
                overlay.blit(rendered, pos)

        overlay.set_alpha(overlay_alpha)
        self.screen.blit(overlay, (0, 0))

    def draw_menu_background(self):
        width, height = self.screen.get_size()
        bg_frame = self.menu_animation.get_frame(self.elapsed_ms)
        if bg_frame:
            draw_image_fit(self.screen, bg_frame, self.screen.get_rect(), cover=True)
            veil = pygame.Surface((width, height), pygame.SRCALPHA)
            veil.fill((255, 246, 205, 22))
            self.screen.blit(veil, (0, 0))
        else:
            self.draw_menu_placeholder_background()

    def draw_menu_placeholder_background(self):
        width, height = self.screen.get_size()
        self.screen.fill((123, 194, 232))
        sky = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            ratio = y / max(1, height)
            r = int(112 + ratio * 76)
            g = int(184 + ratio * 43)
            b = int(235 - ratio * 70)
            pygame.draw.line(sky, (r, g, b), (0, y), (width, y))
        self.screen.blit(sky, (0, 0))

        sun_pos = (int(width * 0.78), int(height * 0.16))
        pygame.draw.circle(self.screen, (255, 233, 145), sun_pos, max(28, width // 38))

        def poly(points, color):
            pygame.draw.polygon(self.screen, color, points)

        mountain_y = int(height * 0.42)
        poly([(0, mountain_y + 90), (int(width * 0.20), mountain_y - 80), (int(width * 0.40), mountain_y + 90)], (111, 132, 126))
        poly([(int(width * 0.22), mountain_y + 80), (int(width * 0.50), mountain_y - 125), (int(width * 0.78), mountain_y + 85)], (94, 118, 121))
        poly([(int(width * 0.55), mountain_y + 90), (int(width * 0.78), mountain_y - 72), (width, mountain_y + 95)], (128, 145, 132))

        ground = int(height * 0.62)
        pygame.draw.rect(self.screen, (94, 174, 77), (0, ground, width, height - ground))
        poly([(0, height), (0, ground + 56), (width, ground + 126), (width, height)], (64, 148, 68))
        poly([(0, height), (int(width * 0.42), ground + 35), (width, height)], (119, 188, 82))

        field_colors = [(222, 195, 96), (99, 174, 74), (236, 214, 127), (82, 157, 69)]
        field_top = ground + 95
        stripe_w = max(42, width // 18)
        for i, x in enumerate(range(-stripe_w, width + stripe_w, stripe_w)):
            poly([(x, height), (x + stripe_w, height), (int(width * 0.52) + (i - 9) * 14, field_top)], field_colors[i % len(field_colors)])

        # Mountain castle placeholder.
        block = max(5, width // 220)
        cx = int(width * 0.50)
        cy = mountain_y - 94
        castle = (238, 232, 202)
        roof = (126, 74, 74)
        for rx, ry, rw, rh in [(-18, 0, 36, 18), (-24, -14, 10, 32), (14, -14, 10, 32), (-6, -27, 12, 45)]:
            pygame.draw.rect(self.screen, castle, (cx + rx * block, cy + ry * block, rw * block, rh * block))
        for rx, ry, rw, rh in [(-27, -19, 16, 7), (11, -19, 16, 7), (-9, -34, 18, 8)]:
            pygame.draw.polygon(self.screen, roof, [
                (cx + rx * block, cy + (ry + rh) * block),
                (cx + (rx + rw // 2) * block, cy + ry * block),
                (cx + (rx + rw) * block, cy + (ry + rh) * block),
            ])

    def draw_intro(self):
        scene = self.current_intro_scene()
        if scene is None:
            self.start_character_select()
            return

        width, height = self.screen.get_size()
        self.screen.fill((107, 174, 221))
        full_rect = self.screen.get_rect()

        frame = scene.animation.get_frame(self.elapsed_ms) if scene.animation else scene.image
        if frame:
            draw_image_fit(self.screen, frame, full_rect, cover=True)
        else:
            self.draw_intro_placeholder(full_rect, scene)

        margin = max(28, width // 34)
        overlay_h = int(height * 0.25)
        text_rect = pygame.Rect(0, height - overlay_h, width, overlay_h)
        overlay = pygame.Surface((width, overlay_h), pygame.SRCALPHA)
        for y in range(overlay_h):
            alpha = int(20 + (y / max(1, overlay_h - 1)) * 175)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (width, y))
        self.screen.blit(overlay, text_rect.topleft)

        visible_lines = self.visible_intro_lines(scene)
        y = text_rect.y + 34
        text_x = margin
        text_w = width - margin * 2
        for line in visible_lines:
            for wrapped in wrap_text(line, self.fonts.intro, text_w):
                shadow = self.fonts.intro.render(wrapped, True, (0, 0, 0))
                rendered = self.fonts.intro.render(wrapped, True, WHITE)
                self.screen.blit(shadow, (text_x + 2, y + 2))
                self.screen.blit(rendered, (text_x, y))
                y += self.fonts.intro.get_linesize()
            y += 8

        hint = "Enter/Space: avancer     Esc: passer l'intro"
        if self.intro_visible_chars < self.intro_text_length(scene):
            hint = "Enter/Space: afficher la suite     Esc: passer l'intro"
        rendered = self.fonts.terminal_small.render(hint, True, (218, 226, 211))
        self.screen.blit(rendered, (width - rendered.get_width() - margin, height - 28))

    def visible_intro_lines(self, scene: IntroScene) -> list[str]:
        remaining = self.intro_visible_chars
        visible = []
        for line in scene.lines:
            if remaining <= 0:
                break
            take = min(len(line), remaining)
            visible.append(line[:take])
            remaining -= take
        return visible

    def draw_intro_placeholder(self, rect: pygame.Rect, scene: IntroScene):
        pygame.draw.rect(self.screen, (124, 190, 232), rect)
        grid = max(4, rect.w // 128)
        origin_x = rect.centerx
        origin_y = rect.centery
        pulse = (self.elapsed_ms // 240) % 2
        accent = scene.accent
        dark = (42, 74, 53)
        stone = (225, 220, 190)
        roof = (128, 76, 72)

        def block(px, py, pw, ph, color):
            pygame.draw.rect(self.screen, color, (
                origin_x + px * grid,
                origin_y + py * grid,
                pw * grid,
                ph * grid,
            ))

        def pixel_sky():
            for y in range(rect.y, rect.bottom, grid * 3):
                ratio = (y - rect.y) / max(1, rect.h)
                color = (int(112 + 70 * ratio), int(186 + 35 * ratio), int(236 - 62 * ratio))
                pygame.draw.rect(self.screen, color, (rect.x, y, rect.w, grid * 3))

        def mountain_range(color=(112, 133, 126), y_offset=-20):
            pygame.draw.polygon(self.screen, color, [
                (rect.x, origin_y + 8 * grid + y_offset),
                (origin_x - 44 * grid, origin_y - 34 * grid + y_offset),
                (origin_x - 8 * grid, origin_y + 8 * grid + y_offset),
                (origin_x + 22 * grid, origin_y - 42 * grid + y_offset),
                (rect.right, origin_y + 10 * grid + y_offset),
                (rect.right, rect.bottom),
                (rect.x, rect.bottom),
            ])

        def fields():
            ground_y = origin_y + 18 * grid
            pygame.draw.rect(self.screen, (98, 176, 75), (rect.x, ground_y, rect.w, rect.bottom - ground_y))
            colors = [(221, 193, 93), (102, 179, 73), (232, 212, 126), (78, 155, 68)]
            for i, x in enumerate(range(rect.x - 80, rect.right + 80, 90)):
                pygame.draw.polygon(self.screen, colors[i % len(colors)], [
                    (x, rect.bottom),
                    (x + 92, rect.bottom),
                    (origin_x + (i - 8) * 10, ground_y + 20),
                ])

        def castle(cx, cy, scale=1):
            s = grid * scale
            for rx, ry, rw, rh in [(-16, 0, 32, 17), (-22, -12, 9, 29), (13, -12, 9, 29), (-5, -25, 10, 42)]:
                pygame.draw.rect(self.screen, stone, (cx + rx * s, cy + ry * s, rw * s, rh * s))
            for rx, ry, rw, rh in [(-24, -17, 13, 6), (11, -17, 13, 6), (-8, -31, 16, 7)]:
                pygame.draw.polygon(self.screen, roof, [
                    (cx + rx * s, cy + (ry + rh) * s),
                    (cx + (rx + rw // 2) * s, cy + ry * s),
                    (cx + (rx + rw) * s, cy + (ry + rh) * s),
                ])

        pixel_sky()

        if scene.key == "01_valley":
            self.draw_menu_placeholder_background()
        elif scene.key == "02_burning_road":
            pixel_sky()
            mountain_range((111, 132, 126), y_offset=-16)
            fields()
            road = [
                (origin_x - 8 * grid, origin_y + 14 * grid),
                (origin_x + 12 * grid, origin_y + 14 * grid),
                (rect.right, rect.bottom),
                (rect.x + 10 * grid, rect.bottom),
            ]
            pygame.draw.polygon(self.screen, (143, 112, 75), road)
            block(-8, 16, 18, 5, (102, 67, 45))
            block(-5, 12, 10, 5, (89, 57, 38))
            block(8 + pulse, 8, 5, 10, (88, 87, 84))
            block(15 - pulse, 1, 4, 13, (65, 70, 75))
            block(2, 10, 4, 6, RED)
            block(5, 8, 2, 5, YELLOW)
        elif scene.key == "03_silent_towers":
            pixel_sky()
            mountain_range((117, 141, 130), y_offset=6)
            pygame.draw.rect(self.screen, (66, 132, 79), (rect.x, origin_y + 12 * grid, rect.w, rect.bottom))
            for offset in (-38, 0, 36):
                block(offset, -8, 5, 33, (95, 72, 50))
                block(offset - 5, -13, 15, 5, (82, 61, 43))
                block(offset - 4, -18, 13, 5, (82, 61, 43))
            for i in range(-60, 65, 12):
                block(i, 20, 4, 30, dark)
                block(i - 4, 11, 12, 10, (47, 101, 57))
            block(30 + pulse, -24, 5, 10, (104, 105, 103))
        elif scene.key == "04_council":
            pygame.draw.rect(self.screen, (91, 67, 50), rect)
            pygame.draw.rect(self.screen, (129, 93, 62), (rect.x, rect.y + rect.h // 2, rect.w, rect.h // 2))
            table = pygame.Rect(origin_x - 42 * grid, origin_y - 2 * grid, 84 * grid, 22 * grid)
            pygame.draw.rect(self.screen, (97, 57, 35), table)
            pygame.draw.rect(self.screen, (188, 160, 106), table.inflate(-10 * grid, -6 * grid))
            pygame.draw.line(self.screen, (88, 112, 77), table.midleft, table.midright, 2 * grid)
            pygame.draw.line(self.screen, (79, 92, 114), table.center, (table.centerx + 22 * grid, table.centery + 6 * grid), grid)
            block(-5, -34, 10, 9, (190, 173, 127))
            block(-7, -25, 14, 20, (77, 63, 88))
            block(-55, -12, 2, 18, YELLOW)
            block(53, -12, 2, 18, YELLOW)
            block(-57, -18 + pulse, 6, 6, (255, 217, 108))
            block(50, -18 + pulse, 6, 6, (255, 217, 108))
        else:
            # Forest Fools: ancient forest gate and a narrow path.
            pygame.draw.rect(self.screen, (87, 151, 105), rect)
            pygame.draw.rect(self.screen, (39, 89, 55), (rect.x, origin_y + 4 * grid, rect.w, rect.bottom))
            pygame.draw.polygon(self.screen, (136, 104, 70), [
                (origin_x - 7 * grid, origin_y + 18 * grid),
                (origin_x + 7 * grid, origin_y + 18 * grid),
                (origin_x + 24 * grid, rect.bottom),
                (origin_x - 24 * grid, rect.bottom),
            ])
            for i in range(-62, 64, 18):
                block(i, -20, 6, 72, (62, 47, 34))
                block(i - 8, -34, 22, 20, (32, 92, 49))
                block(i - 12, -48, 30, 18, (35, 105, 56))
            block(-2, -32, 4, 48, YELLOW)
            block(-10, -8, 20, 4, dark)
            block(-6, 16, 12, 8, dark)
            block(-34 + pulse, -4, 2, 2, (224, 214, 92))
            block(31 - pulse, -13, 2, 2, (224, 214, 92))
            block(10 + pulse, 5, 2, 2, (224, 214, 92))
            return

        if scene.key not in ("01_valley", "02_burning_road", "03_silent_towers", "04_council"):
            mountain_range()
            fields()
            castle(origin_x + 34 * grid, origin_y - 32 * grid, scale=1)
            block(-38, 18, 4, 6, (224, 176, 104))
            block(-40, 24, 8, 16, dark)
            block(-42, 40, 4, 14, dark)
            block(-34, 40, 4, 14, dark)
            block(-28, 16, 2, 38, (112, 96, 74))
            pygame.draw.line(self.screen, (126, 95, 54), (rect.x, rect.bottom), (origin_x - 35 * grid, origin_y + 40 * grid), 10)


    def draw_character_select(self):
        width, height = self.screen.get_size()
        self.draw_character_select_background()
        race_key = self.character_choice["race"]
        gender_key = self.character_choice["gender"]
        class_key = self.character_choice["class"]
        preview = self.get_character_preview(race_key, class_key)

        center_x = width // 2
        margin = max(28, width // 34)
        top_panel = pygame.Rect(margin, 28, width - margin * 2, 255)

        draw_outlined_text(
            self.screen,
            self.fonts.scene_title,
            "Choose Your Forest Fool",
            (center_x, top_panel.y + 35),
            (255, 241, 180),
            (19, 46, 33),
            outline=3,
        )

        row_w = min(900, top_panel.w - 52)
        row_x = center_x - row_w // 2
        self.draw_choice_strip(
            pygame.Rect(row_x, top_panel.y + 70, row_w, 42),
            "Race",
            self.race_keys,
            race_key,
            RACES,
            self.character_focus == 0,
        )
        self.draw_choice_strip(
            pygame.Rect(row_x, top_panel.y + 121, row_w, 42),
            "Gender",
            self.gender_keys,
            gender_key,
            GENDERS,
            self.character_focus == 1,
        )
        self.draw_choice_strip(
            pygame.Rect(row_x, top_panel.y + 172, row_w, 42),
            "Class",
            self.class_keys,
            class_key,
            CLASSES,
            self.character_focus == 2,
        )
        self.draw_start_choice(pygame.Rect(row_x, top_panel.y + 221, row_w, 29), self.character_focus == 3)

        stage_top = top_panel.bottom + max(16, height // 55)
        stage_bottom = height - 126
        stage_h = max(260, stage_bottom - stage_top)
        portrait_w = min(360, max(230, int(width * 0.24)))
        female_rect = pygame.Rect(
            int(width * 0.15),
            int(stage_top + stage_h * 0.44),
            int(portrait_w * 0.90),
            int(stage_h * 0.66),
        )
        male_rect = pygame.Rect(
            int(width * 0.62),
            int(stage_top + stage_h * 0.23),
            portrait_w,
            int(stage_h * 0.86),
        )
        self.draw_character_portrait(female_rect, race_key, "female", gender_key == "female", class_key)
        self.draw_character_portrait(male_rect, race_key, "male", gender_key == "male", class_key)

        stats_rect = pygame.Rect(margin, height - 92, width - margin * 2, 66)
        self.draw_character_preview_stats(stats_rect, preview, race_key, class_key)

    def draw_character_select_background(self):
        width, height = self.screen.get_size()
        if self.character_background:
            draw_image_fit(self.screen, self.character_background, self.screen.get_rect(), cover=True)
        else:
            self.draw_character_select_placeholder_background(width, height)

    def draw_character_select_placeholder_background(self, width, height):
        self.screen.fill((131, 202, 236))
        horizon = int(height * 0.52)
        pygame.draw.rect(self.screen, (105, 184, 90), (0, horizon, width, height - horizon))
        pygame.draw.polygon(self.screen, (82, 158, 78), [
            (0, height),
            (0, horizon + 80),
            (width, horizon + 30),
            (width, height),
        ])
        pygame.draw.polygon(self.screen, (232, 210, 116), [
            (int(width * 0.45), height),
            (int(width * 0.58), height),
            (int(width * 0.53), horizon + 18),
            (int(width * 0.50), horizon + 18),
        ])
        rock = pygame.Rect(int(width * 0.18), int(height * 0.62), int(width * 0.17), int(height * 0.11))
        pygame.draw.rect(self.screen, (112, 112, 98), rock, border_radius=8)
        pygame.draw.rect(self.screen, (89, 91, 82), rock.inflate(-16, -14), border_radius=5)

    def draw_choice_strip(self, rect, label, keys, selected_key, source, focused):
        fill = (255, 245, 196, 175) if focused else (255, 245, 196, 118)
        border = (255, 214, 76) if focused else (52, 94, 54, 112)
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=6)
        pygame.draw.rect(surface, border, surface.get_rect(), width=2 if focused else 1, border_radius=6)
        self.screen.blit(surface, rect.topleft)

        label_color = (91, 69, 28) if focused else (32, 66, 42)
        draw_text(self.screen, self.fonts.terminal, label.upper(), (rect.x + 15, rect.y + 10), label_color)

        option_area = pygame.Rect(rect.x + 120, rect.y, rect.w - 135, rect.h)
        option_w = option_area.w // max(1, len(keys))
        for index, key in enumerate(keys):
            name = source.get(key, {}).get("name", key.title())
            selected = key == selected_key
            color = (255, 248, 206) if selected else (36, 61, 43)
            if selected:
                selected_rect = pygame.Rect(option_area.x + index * option_w + 5, rect.y + 5, option_w - 10, rect.h - 10)
                pygame.draw.rect(self.screen, (78, 139, 74, 210), selected_rect, border_radius=5)
                pygame.draw.rect(self.screen, (255, 226, 103), selected_rect, width=2 if focused else 1, border_radius=5)
            rendered = self.fonts.terminal.render(name, True, color)
            x = option_area.x + index * option_w + option_w // 2 - rendered.get_width() // 2
            y = rect.centery - rendered.get_height() // 2
            self.screen.blit(rendered, (x, y))

    def draw_start_choice(self, rect, focused):
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        fill = (78, 139, 74, 210) if focused else (255, 245, 196, 118)
        border = (255, 218, 92) if focused else (52, 94, 54, 112)
        pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=6)
        pygame.draw.rect(surface, border, surface.get_rect(), width=2 if focused else 1, border_radius=6)
        self.screen.blit(surface, rect.topleft)
        label = "Begin Journey"
        if focused:
            label = "> Begin Journey <"
        rendered = self.fonts.terminal.render(label, True, (255, 248, 206) if focused else (36, 61, 43))
        self.screen.blit(rendered, (rect.centerx - rendered.get_width() // 2, rect.centery - rendered.get_height() // 2))

    def draw_character_portrait(self, rect, race_key, gender_key, selected, class_key):
        art_rect = pygame.Rect(rect.x, rect.y, rect.w, rect.h - 42)
        animation = self.get_character_animation(race_key, gender_key, class_key)
        frame = animation.get_frame(self.elapsed_ms) if animation else None
        if frame:
            self.draw_character_sprite(frame, art_rect, selected)
        else:
            self.draw_character_placeholder(
                art_rect,
                race_key,
                gender_key,
                class_key,
                seated=gender_key == "female",
                glow=selected,
            )

    def draw_character_sprite(self, image: pygame.Surface, rect: pygame.Rect, selected: bool):
        image = self.trim_transparent_sprite(image)
        src_w, src_h = image.get_size()
        if src_w <= 0 or src_h <= 0:
            return
        scale = min(rect.w / src_w, rect.h / src_h)
        size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        scaled = scale_nearest(image, size)
        target_rect = scaled.get_rect(center=rect.center)
        target_rect.bottom = min(target_rect.bottom, rect.bottom)

        if selected:
            mask = pygame.mask.from_surface(scaled)
            glow = mask.to_surface(
                setcolor=(255, 226, 92, 118),
                unsetcolor=(0, 0, 0, 0),
            ).convert_alpha()
            for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, -4), (-4, 4), (4, 4)):
                self.screen.blit(glow, (target_rect.x + dx, target_rect.y + dy))

        self.screen.blit(scaled, target_rect)

    def trim_transparent_sprite(self, image: pygame.Surface, padding=12) -> pygame.Surface:
        mask = pygame.mask.from_surface(image)
        rects = mask.get_bounding_rects()
        if not rects:
            return image
        bounds = rects[0].copy()
        for rect in rects[1:]:
            bounds.union_ip(rect)
        bounds.inflate_ip(padding * 2, padding * 2)
        bounds = bounds.clip(image.get_rect())
        return image.subsurface(bounds).copy()

    def draw_character_placeholder(self, rect, race_key, gender_key, class_key, seated=False, glow=False):
        scale = max(2, min(rect.w // 32, rect.h // 42))
        cx = rect.centerx
        cy = rect.centery + 15 * scale
        race_colors = {
            "human": ((232, 180, 124), (75, 52, 36)),
            "elf": ((229, 190, 135), (224, 225, 140)),
            "lizardfolk": ((99, 170, 82), (44, 104, 55)),
        }
        skin, hair = race_colors.get(race_key, ((226, 174, 124), (70, 48, 36)))
        cloth = (80, 139, 84) if class_key == "warrior" else (83, 92, 178)
        trim = (214, 181, 74) if class_key == "warrior" else (130, 220, 232)
        shadow = (22, 31, 24)
        rock = (105, 102, 87)

        def block(px, py, pw, ph, color):
            rect_px = pygame.Rect(cx + px * scale, cy + py * scale, pw * scale, ph * scale)
            if glow:
                for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, -3), (-3, 3), (3, 3)):
                    pygame.draw.rect(self.screen, (255, 226, 92), rect_px.move(dx, dy))
            pygame.draw.rect(self.screen, shadow, rect_px.move(2, 2))
            pygame.draw.rect(self.screen, color, rect_px)

        body_w = 13 if gender_key == "male" else 11
        if seated:
            block(-11, -8, 23, 9, rock)
            block(-9, -3, 19, 5, rock)
            block(-body_w // 2, -24, body_w, 14, cloth)
            block(-body_w // 2 - 2, -20, 2, 10, cloth)
            block(body_w // 2, -20, 2, 10, cloth)
            block(-7, -11, 7, 4, cloth)
            block(1, -11, 8, 4, cloth)
            block(-5, -33, 10, 9, skin)
        else:
            block(-body_w // 2, -24, body_w, 16, cloth)
            block(-body_w // 2 - 2, -20, 2, 12, cloth)
            block(body_w // 2, -20, 2, 12, cloth)
            block(-4, -8, 3, 10, cloth)
            block(2, -8, 3, 10, cloth)
            block(-5, -33, 10, 9, skin)
        if race_key == "lizardfolk":
            block(-2, -38, 4, 4, hair)
            block(-8, -30, 3, 5, skin)
            block(5, -30, 3, 5, skin)
            block(4, -34, 5, 3, skin)
        else:
            block(-6, -36, 12, 5, hair)
        if race_key == "elf":
            block(-9, -31, 3, 3, skin)
            block(6, -31, 3, 3, skin)
        if class_key == "mage":
            block(8, -27, 2, 25, trim)
            block(7, -31, 4, 4, trim)
        else:
            block(8, -26, 3, 24, trim)
            block(7, -27, 5, 5, trim)

    def get_character_preview(self, race_key, class_key):
        stats = {
            "max_hp": PLAYER_START_HP,
            "max_mana": PLAYER_START_MANA,
            "base_attack": PLAYER_START_ATTACK,
            "base_armor": 0,
            "magic_power": 0,
        }

        def apply_bonuses(bonuses):
            stats["max_hp"] = max(20, stats["max_hp"] + bonuses.get("max_hp", 0))
            stats["max_mana"] = max(0, stats["max_mana"] + bonuses.get("max_mana", 0))
            stats["base_attack"] = max(1, stats["base_attack"] + bonuses.get("base_attack", 0))
            stats["base_armor"] = max(0, stats["base_armor"] + bonuses.get("base_armor", 0))
            stats["magic_power"] = max(0, stats["magic_power"] + bonuses.get("magic_power", 0))

        apply_bonuses(RACES.get(race_key, {}).get("bonuses", {}))
        class_data = CLASSES.get(class_key, {})
        apply_bonuses(class_data.get("bonuses", {}))

        starting_items = class_data.get("starting_items", {})
        weapon_key = starting_items.get("weapons", [PLAYER_START_WEAPON])[0] if starting_items.get("weapons") else PLAYER_START_WEAPON
        armor_key = starting_items.get("armors", [PLAYER_START_ARMOR])[0] if starting_items.get("armors") else PLAYER_START_ARMOR
        spells = [
            SPELLS[key]["name"]
            for key in starting_items.get("spells", [])
            if key in SPELLS
        ]
        return {
            "hp": stats["max_hp"],
            "mana": stats["max_mana"],
            "attack": stats["base_attack"] + WEAPONS.get(weapon_key, {}).get("attack", 0),
            "magic": stats["magic_power"],
            "defense": stats["base_armor"] + ARMORS.get(armor_key, {}).get("armor", 0),
            "weapon": WEAPONS.get(weapon_key, {}).get("name", weapon_key),
            "armor": ARMORS.get(armor_key, {}).get("name", armor_key),
            "spells": spells,
        }

    def draw_character_preview_stats(self, rect, preview, race_key, class_key):
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (18, 44, 29, 132), surface.get_rect(), border_radius=8)
        pygame.draw.rect(surface, (183, 218, 147, 120), surface.get_rect(), width=1, border_radius=8)
        self.screen.blit(surface, rect.topleft)

        race_desc = RACES.get(race_key, {}).get("description", "")
        class_desc = CLASSES.get(class_key, {}).get("description", "")
        title = f"{race_desc} {class_desc}".strip()
        desc_w = int(rect.w * 0.38)
        self.draw_wrapped_lines(title, self.fonts.terminal_small, rect.x + 16, rect.y + 11, desc_w, (238, 244, 221), max_lines=2)

        stats = [
            ("HP", preview["hp"], RED),
            ("Mana", preview["mana"], BLUE),
            ("Attack", preview["attack"], YELLOW),
            ("Magic", preview["magic"], PURPLE),
            ("Defense", preview["defense"], CYAN),
        ]
        stats_x = rect.x + desc_w + 34
        loadout_w = 210
        slot_w = max(82, (rect.right - stats_x - loadout_w - 24) // len(stats))
        y = rect.y + 13
        for index, (label, value, color) in enumerate(stats):
            x = stats_x + index * slot_w
            draw_text(self.screen, self.fonts.terminal_small, label, (x, y), (190, 214, 176))
            draw_text(self.screen, self.fonts.terminal, value, (x, y + 22), color)

        loadout = f"{preview['weapon']} / {preview['armor']}"
        if preview["spells"]:
            loadout += " / " + ", ".join(preview["spells"])
        wrapped = wrap_text(loadout, self.fonts.terminal_small, loadout_w)
        loadout_y = rect.y + 14
        for line in wrapped[:2]:
            rendered = self.fonts.terminal_small.render(line, True, (238, 244, 221))
            self.screen.blit(rendered, (rect.right - rendered.get_width() - 16, loadout_y))
            loadout_y += self.fonts.terminal_small.get_linesize()


    def layout(self):
        width, height = self.screen.get_size()
        margin = 10
        gap = 10
        total_w = width - margin * 2 - gap * 2
        left_w = clamp(int(total_w * 0.22), 240, 320)
        right_w = clamp(int(total_w * 0.40), 360, 560)
        center_w = total_w - left_w - right_w
        if center_w < 430:
            missing = 430 - center_w
            right_w = max(330, right_w - missing)
            center_w = total_w - left_w - right_w

        full_h = height - margin * 2
        min_context_h = 190
        right_top_h = min(right_w, full_h - gap - min_context_h)
        right_top_h = max(300, right_top_h)
        return {
            "left": pygame.Rect(margin, margin, left_w, full_h),
            "terminal": pygame.Rect(margin + left_w + gap, margin, center_w, full_h),
            "map": pygame.Rect(margin + left_w + gap + center_w + gap, margin, right_w, right_top_h),
            "context": pygame.Rect(
                margin + left_w + gap + center_w + gap,
                margin + right_top_h + gap,
                right_w,
                full_h - right_top_h - gap,
            ),
        }

    def draw_game(self):
        if not self.game:
            return
        state = self.game.get_ui_state()
        panels = self.layout()
        self.draw_player_panel(panels["left"], state["player"], state["location"])
        self.draw_terminal_panel(panels["terminal"], state)
        self.draw_map_panel(panels["map"], state["map"])
        self.draw_context_panel(panels["context"], state)

    def draw_player_panel(self, rect, player, location):
        content = draw_panel(self.screen, rect, GREEN, "Player", self.fonts.small)
        x, y = content.x, content.y

        portrait = pygame.Rect(x + 18, y, content.w - 36, 145)
        pygame.draw.rect(self.screen, PANEL_INNER, portrait, border_radius=4)
        pygame.draw.rect(self.screen, (42, 62, 47), portrait, width=1, border_radius=4)
        race_key = player["race"]["key"]
        gender_key = player["gender"]["key"]
        class_key = player["class"]["key"]
        portrait_animation = self.get_character_animation(race_key, gender_key, class_key)
        portrait_frame = portrait_animation.get_frame(self.elapsed_ms) if portrait_animation else None
        if portrait_frame:
            self.draw_character_sprite(portrait_frame, portrait.inflate(-14, -12), False)
        else:
            self.draw_character_placeholder(portrait.inflate(-18, -8), race_key, gender_key, class_key)
        y = portrait.bottom + 18

        draw_text(self.screen, self.fonts.body, f"Lv {player['level']} {player['class']['name']}", (x, y), WHITE)
        y += 30
        origin = f"{player['race']['name']} / {player['gender']['name']}"
        draw_text(self.screen, self.fonts.small, origin, (x, y), YELLOW)
        y += 26
        draw_text(self.screen, self.fonts.small, location["label"], (x, y), CYAN)
        y += 32

        draw_bar(self.screen, pygame.Rect(x, y, content.w, 24), player["hp"], player["max_hp"], RED, "HP", self.fonts.terminal_small)
        y += 32
        draw_bar(self.screen, pygame.Rect(x, y, content.w, 24), player["mana"], player["max_mana"], BLUE, "Mana", self.fonts.terminal_small)
        y += 32
        draw_bar(self.screen, pygame.Rect(x, y, content.w, 20), player["xp"], player["xp_to_next"], YELLOW, "XP", self.fonts.terminal_small)
        y += 36

        stat_lines = [
            ("Gold", player["gold"], YELLOW),
            ("Attack", player["attack"], RED),
            ("Magic", player["magic_power"], PURPLE),
            ("Defense", player["defense"], BLUE),
            ("Dodge", f"{player['dodge_chance']}%", GREEN),
        ]
        for label, value, color in stat_lines:
            draw_text(self.screen, self.fonts.small, label, (x, y), MUTED)
            draw_text_right(self.screen, self.fonts.small, value, pygame.Rect(x, y, content.w, 24), y, color)
            y += 26

        y += 10
        draw_text(self.screen, self.fonts.small, "Weapon", (x, y), MUTED)
        y += 23
        y = self.draw_wrapped_lines(player["weapon"]["name"], self.fonts.small, x, y, content.w, CYAN, max_lines=2)
        y += 7
        draw_text(self.screen, self.fonts.small, "Armor", (x, y), MUTED)
        y += 23
        y = self.draw_wrapped_lines(player["armor"]["name"], self.fonts.small, x, y, content.w, CYAN, max_lines=2)
        y += 12

        slots = player["spell_slots"]
        draw_text(self.screen, self.fonts.small, f"Spells {slots['used']}/{slots['max']}", (x, y), PURPLE)
        y += 25
        for spell in player["spells"][:5]:
            y = self.draw_wrapped_lines(f"- {spell['name']}", self.fonts.small, x + 8, y, content.w - 8, TEXT, max_lines=1)

    def draw_pixel_placeholder(self, rect):
        scale = max(5, min(rect.w // 24, rect.h // 24))
        cx = rect.centerx
        top = rect.y + 20
        color = (65, 180, 91)
        shadow = (24, 76, 39)
        pixels = [
            (-2, 0, 5, 3), (-3, 3, 7, 6), (-2, 9, 5, 3),
            (-4, 12, 9, 8), (-5, 20, 4, 6), (2, 20, 4, 6),
            (-3, 28, 3, 9), (1, 28, 3, 9),
        ]
        for px, py, pw, ph in pixels:
            pygame.draw.rect(self.screen, shadow, (cx + px * scale + 3, top + py * scale + 3, pw * scale, ph * scale))
            pygame.draw.rect(self.screen, color, (cx + px * scale, top + py * scale, pw * scale, ph * scale))
        draw_text(self.screen, self.fonts.terminal_small, "PIXEL ART", (rect.centerx - 34, rect.bottom - 24), DIM)

    def draw_terminal_panel(self, rect, state):
        content = draw_panel(self.screen, rect, RED, "Terminal", self.fonts.small)
        input_h = 34
        history_rect = pygame.Rect(content.x, content.y, content.w, content.h - input_h - 10)
        input_rect = pygame.Rect(content.x, content.bottom - input_h, content.w, input_h)

        pygame.draw.rect(self.screen, PANEL_INNER, history_rect, border_radius=4)
        pygame.draw.rect(self.screen, (67, 35, 36), history_rect, width=1, border_radius=4)

        terminal_lines = self.collect_terminal_lines(state["terminal"]["messages"], history_rect.w - 18)
        line_h = self.fonts.terminal.get_linesize()
        max_lines = max(1, history_rect.h // line_h)
        visible = terminal_lines[-max_lines:]
        y = history_rect.y + 6
        for text, color in visible:
            draw_text(self.screen, self.fonts.terminal, text, (history_rect.x + 8, y), color)
            y += line_h

        pygame.draw.rect(self.screen, BLACK, input_rect, border_radius=4)
        pygame.draw.rect(self.screen, RED, input_rect, width=1, border_radius=4)
        prompt = "> " + self.input_buffer
        if self.cursor_visible:
            prompt += "_"
        draw_text(self.screen, self.fonts.terminal, prompt, (input_rect.x + 9, input_rect.y + 8), CYAN)

    def collect_terminal_lines(self, messages, max_width):
        lines = []
        for msg in messages[-120:]:
            text = msg.get("text", "")
            kind = msg.get("kind", "output")
            color = CYAN if kind == "command" else TEXT
            if not text:
                lines.append(("", color))
                continue
            if "ERROR" in text.upper() or "INVALID" in text.upper() or "UNKNOWN" in text.upper():
                color = RED
            elif "FOUND" in text.upper() or "GAINED" in text.upper() or "EQUIPPED" in text.upper():
                color = GREEN
            elif "GOLD" in text.upper():
                color = YELLOW
            for wrapped in wrap_text(text, self.fonts.terminal, max_width):
                lines.append((wrapped, color))
        return lines

    def draw_map_paper_frame(self, rect: pygame.Rect, map_state, map_key: str):
        frame_key = f"{map_key}_paper"
        frame_image = self.map_frame_images.get(frame_key) or self.map_frame_images.get("map_paper")
        if frame_image:
            self.screen.fill((218, 181, 104), rect)
            crop = max(10, int(min(frame_image.get_size()) * 0.038))
            crop_rect = pygame.Rect(
                crop,
                crop,
                max(1, frame_image.get_width() - crop * 2),
                max(1, frame_image.get_height() - crop * 2),
            )
            draw_image_fit(self.screen, frame_image.subsurface(crop_rect), rect, cover=True)
        else:
            paper = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(paper, (206, 174, 108, 242), paper.get_rect(), border_radius=5)
            inner = paper.get_rect().inflate(-10, -10)
            pygame.draw.rect(paper, (230, 207, 145, 238), inner, border_radius=3)
            pygame.draw.rect(paper, (92, 61, 31, 255), paper.get_rect(), width=4, border_radius=5)
            pygame.draw.rect(paper, (151, 103, 50, 220), inner, width=2, border_radius=3)
            self.screen.blit(paper, rect.topleft)

        title = map_state.get("name", "Map").split(" / ")[0]
        title_font = self.fonts.scene_title if rect.w >= 360 else self.fonts.body
        rendered = title_font.render(title, True, (64, 43, 24))
        shadow = title_font.render(title, True, (240, 221, 157))
        x = rect.centerx - rendered.get_width() // 2
        y = rect.y + 6
        self.screen.blit(shadow, (x + 2, y + 2))
        self.screen.blit(rendered, (x, y))

    def draw_map_image(self, image: pygame.Surface, rect: pygame.Rect, map_state, image_key: str):
        pygame.draw.rect(self.screen, PANEL_INNER, rect, border_radius=4)
        src_w, src_h = image.get_size()
        if src_w <= 0 or src_h <= 0:
            return
        scale = min(rect.w / src_w, rect.h / src_h)
        size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        scaled = scale_nearest(image, size)
        image_rect = scaled.get_rect(center=rect.center)
        self.screen.blit(scaled, image_rect)

        cols = map_state["cols"]
        rows = map_state["rows"]
        col_count = max(1, len(cols))
        row_count = max(1, len(rows))
        cell_w = image_rect.w / col_count
        cell_h = image_rect.h / row_count

        grid_surface = pygame.Surface(image_rect.size, pygame.SRCALPHA)
        line_color = (255, 255, 255, 34)
        for index in range(col_count + 1):
            x = int(index * cell_w)
            pygame.draw.line(grid_surface, line_color, (x, 0), (x, image_rect.h))
        for index in range(row_count + 1):
            y = int(index * cell_h)
            pygame.draw.line(grid_surface, line_color, (0, y), (image_rect.w, y))
        self.screen.blit(grid_surface, image_rect.topleft)

        cells = {cell_data["coord"]: cell_data for cell_data in map_state["cells"]}
        if map_state.get("show_walkable"):
            overlay = pygame.Surface(image_rect.size, pygame.SRCALPHA)
            for row_idx, row in enumerate(rows):
                for col_idx, col in enumerate(cols):
                    data = cells[f"{col}{row}"]
                    if not data.get("walkable"):
                        continue
                    cell_rect = pygame.Rect(
                        int(col_idx * cell_w),
                        int(row_idx * cell_h),
                        max(1, int(cell_w + 1)),
                        max(1, int(cell_h + 1)),
                    )
                    pygame.draw.rect(overlay, (92, 255, 124, 58), cell_rect)
            self.screen.blit(overlay, image_rect.topleft)

        label_font = self.fonts.terminal_small
        if min(cell_w, cell_h) >= 22:
            label_step = 1
        elif min(cell_w, cell_h) >= 12:
            label_step = 2
        else:
            label_step = 5

        for index, col in enumerate(cols):
            if index % label_step != 0:
                continue
            rendered = label_font.render(str(col), True, WHITE)
            shadow = label_font.render(str(col), True, BLACK)
            x = image_rect.x + int((index + 0.5) * cell_w) - rendered.get_width() // 2
            y = image_rect.y - rendered.get_height() - 4
            self.screen.blit(shadow, (x + 1, y + 1))
            self.screen.blit(rendered, (x, y))

        for index, row in enumerate(rows):
            if index % label_step != 0:
                continue
            text = str(row)
            rendered = label_font.render(text, True, WHITE)
            shadow = label_font.render(text, True, BLACK)
            x = image_rect.x - rendered.get_width() - 6
            y = image_rect.y + int((index + 0.5) * cell_h) - rendered.get_height() // 2
            self.screen.blit(shadow, (x + 1, y + 1))
            self.screen.blit(rendered, (x, y))

        if min(cell_w, cell_h) >= 28:
            symbol_font = self.fonts.body
        elif min(cell_w, cell_h) >= 12:
            symbol_font = self.fonts.map
        else:
            symbol_font = self.fonts.terminal_small
        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate((self.elapsed_ms / 8) % 360).x
        pulse_alpha = int(62 + pulse * 92)

        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(cols):
                data = cells[f"{col}{row}"]
                cell_rect = pygame.Rect(
                    image_rect.x + int(col_idx * cell_w),
                    image_rect.y + int(row_idx * cell_h),
                    max(1, int(cell_w + 1)),
                    max(1, int(cell_h + 1)),
                )
                if data["is_player"]:
                    glow = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(glow, (255, 244, 160, pulse_alpha), glow.get_rect())
                    self.screen.blit(glow, cell_rect.topleft)
                    pygame.draw.rect(self.screen, WHITE, cell_rect, width=2)

                if not data.get("symbol_visible"):
                    continue

                tile_type = data["type"]
                if tile_type in ("plains", "water", "unknown"):
                    continue
                symbol = TILE_SYMBOLS.get(tile_type, "?")
                rendered = symbol_font.render(symbol, True, WHITE)
                center = (cell_rect.centerx, cell_rect.centery)
                for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                    shadow = symbol_font.render(symbol, True, BLACK)
                    self.screen.blit(shadow, shadow.get_rect(center=(center[0] + dx, center[1] + dy)))
                self.screen.blit(rendered, rendered.get_rect(center=center))

    def draw_map_overview_image(self, image: pygame.Surface, rect: pygame.Rect):
        src_w, src_h = image.get_size()
        if src_w <= 0 or src_h <= 0:
            return
        scale = min(rect.w / src_w, rect.h / src_h)
        size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        scaled = scale_nearest(image, size)
        image_rect = scaled.get_rect(center=rect.center)
        self.screen.blit(scaled, image_rect)

    def draw_map_panel(self, rect, map_state):
        content = rect.inflate(-2, -2)
        grid_margin = 12
        label_h = 22
        legend_h = 36
        col_count = max(1, len(map_state["cols"]))
        row_count = max(1, len(map_state["rows"]))
        cell = min(
            (content.w - grid_margin * 2 - 24) // col_count,
            (content.h - label_h - legend_h - grid_margin * 2) // row_count,
        )
        cell = max(5, cell)
        grid_w = cell * col_count
        grid_h = cell * row_count
        start_x = content.centerx - grid_w // 2
        start_y = content.y + label_h + 8

        map_image_key = map_state.get("region") or map_state.get("key")
        map_image = self.map_images.get(map_image_key)
        if map_image:
            side = min(content.w, content.h)
            paper_rect = pygame.Rect(
                content.centerx - side // 2,
                content.centery - side // 2,
                side,
                side,
            )
            self.draw_map_paper_frame(paper_rect, map_state, map_image_key)

            if map_state.get("overview_only"):
                paper_pad = max(10, int(side * 0.03))
                title_space = max(34, int(side * 0.09))
                overview_side = min(
                    paper_rect.w - paper_pad * 2,
                    paper_rect.h - paper_pad - title_space,
                )
                image_rect = pygame.Rect(
                    paper_rect.centerx - overview_side // 2,
                    paper_rect.y + title_space,
                    overview_side,
                    overview_side,
                )
                self.draw_map_overview_image(map_image, image_rect)
                return

            label_gutter = max(16, int(side * 0.04))
            paper_pad = max(10, int(side * 0.028))
            title_space = max(24, int(side * 0.075))
            available_w = paper_rect.w - paper_pad * 2 - label_gutter
            available_h = paper_rect.h - paper_pad * 2 - title_space - label_gutter
            map_side = min(available_w, available_h)
            image_rect = pygame.Rect(
                paper_rect.x + paper_pad + label_gutter + (available_w - map_side) // 2,
                paper_rect.y + paper_pad + title_space + label_gutter - max(8, int(side * 0.022)),
                map_side,
                map_side,
            )
            self.draw_map_image(map_image, image_rect, map_state, map_image_key)
            return

        if cell >= 10:
            for i, col in enumerate(map_state["cols"]):
                rendered = self.fonts.terminal_small.render(col, True, MUTED)
                shadow = self.fonts.terminal_small.render(col, True, BLACK)
                x = start_x + i * cell + cell // 2 - rendered.get_width() // 2
                y = start_y - rendered.get_height() - 4
                self.screen.blit(shadow, (x + 1, y + 1))
                self.screen.blit(rendered, (x, y))
            for i, row in enumerate(map_state["rows"]):
                rendered = self.fonts.terminal_small.render(str(row), True, MUTED)
                shadow = self.fonts.terminal_small.render(str(row), True, BLACK)
                x = start_x - rendered.get_width() - 6
                y = start_y + i * cell + cell // 2 - rendered.get_height() // 2
                self.screen.blit(shadow, (x + 1, y + 1))
                self.screen.blit(rendered, (x, y))

        cells = {cell_data["coord"]: cell_data for cell_data in map_state["cells"]}
        for row_idx, row in enumerate(map_state["rows"]):
            for col_idx, col in enumerate(map_state["cols"]):
                data = cells[f"{col}{row}"]
                tile_type = data["type"]
                terrain = data["terrain"]
                cell_rect = pygame.Rect(start_x + col_idx * cell, start_y + row_idx * cell, cell - 2, cell - 2)
                fill = TERRAIN_COLORS.get(terrain, TYPE_COLORS.get(tile_type, DIM))
                if tile_type == "unknown":
                    fill = TYPE_COLORS["unknown"]
                pygame.draw.rect(self.screen, fill, cell_rect)
                pygame.draw.rect(self.screen, (9, 13, 10), cell_rect, width=1)
                if map_state.get("show_walkable") and data.get("walkable"):
                    overlay = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
                    overlay.fill((92, 255, 124, 58))
                    self.screen.blit(overlay, cell_rect.topleft)

                if data["is_player"]:
                    pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate((self.elapsed_ms / 8) % 360).x
                    overlay = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
                    overlay.fill((255, 244, 160, int(62 + pulse * 92)))
                    self.screen.blit(overlay, cell_rect.topleft)
                    pygame.draw.rect(self.screen, WHITE, cell_rect, width=2)
                    continue

                if not data.get("symbol_visible"):
                    continue

                if tile_type in ("plains", "water", "unknown"):
                    continue

                symbol = TILE_SYMBOLS.get(tile_type, "?")
                if cell >= 28:
                    font = self.fonts.body
                elif cell >= 12:
                    font = self.fonts.map
                else:
                    font = self.fonts.terminal_small
                rendered = font.render(symbol, True, WHITE)
                center = cell_rect.center
                for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                    shadow = font.render(symbol, True, BLACK)
                    self.screen.blit(shadow, shadow.get_rect(center=(center[0] + dx, center[1] + dy)))
                self.screen.blit(rendered, rendered.get_rect(center=center))

        y = start_y + grid_h + 14
        legend = "K Capital   T Forest   V Village   S Slime   D Dragon   ? Unknown"
        self.draw_wrapped_lines(legend, self.fonts.terminal_small, content.x, y, content.w, MUTED, max_lines=2)

    def draw_context_panel(self, rect, state):
        location = state["location"]
        image_key = self.context_background_key(location)
        image = self.info_backgrounds.get(image_key) if image_key else None
        if image:
            self.draw_info_background(image, rect)
        else:
            pygame.draw.rect(self.screen, PANEL_INNER, rect)

    def context_background_key(self, location) -> str | None:
        for key in (
            location.get("subloc"),
            location.get("inside"),
            location.get("tile_type"),
            location.get("world_key"),
        ):
            if key in self.info_backgrounds:
                return key
        return "mosswake" if "mosswake" in self.info_backgrounds else None

    def draw_info_background(self, image: pygame.Surface, rect: pygame.Rect):
        src_w, src_h = image.get_size()
        if src_w <= 0 or src_h <= 0:
            return
        scale = rect.h / src_h
        if src_w * scale < rect.w:
            scale = rect.w / src_w
        size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        scaled = scale_nearest(image, size)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(rect)
        self.screen.blit(scaled, (rect.x, rect.centery - scaled.get_height() // 2))
        self.screen.set_clip(previous_clip)

    def draw_wrapped_lines(self, text, font, x, y, max_width, color, max_lines=None):
        lines = wrap_text(text, font, max_width)
        if max_lines is not None:
            lines = lines[:max_lines]
        line_h = font.get_linesize()
        for line in lines:
            draw_text(self.screen, font, line, (x, y), color)
            y += line_h
        return y


if __name__ == "__main__":
    ForestFoolsApp().run()
