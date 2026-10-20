"""
arcade.py - Mind Reset Arcade for procrastiNOT.exe
Cyberpunk Pixel-Arcade Mini-Games & Brain Recharge Zone.

Features:
- Dedicated Canvas Widget isolation ensuring HUDs, live scoreboards, and modals are never wiped
- Game A: NEON DODGE (Live score pointer, pause, stop button, game-over modal with REPLAY)
- Game B: PIXEL POP (30s blitz, prominent timer & combo HUD, stop button, summary modal with REPLAY)
- Game C: CYBER BREAKER (Authentic retro block smasher, paddle physics, brick explosion particles, STOP & REPLAY)
- Game D (Bonus): CALM MODE (Guided 4-4-4-4 Box Breathing chamber, mindful timer, finish button)
- Non-blocking 8-bit sound synthesizer with master sound toggle
- High score persistence integrated into projectx_data.json
- Clean Clock lifecycle management with zero leaks or thread blockage
"""

import os
import sys
import math
import random
import threading
from datetime import datetime

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (
    Color, Ellipse, Line, Mesh, PopMatrix, PushMatrix,
    Rectangle, Rotate, RoundedRectangle, Translate
)
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


# ---------------------------------------------------------------------------
# Fonts and Cyberpunk Design Tokens (Consistent with procrastiNOT OS)
# ---------------------------------------------------------------------------

def _pick_font(path, fallback="Roboto"):
    return path if os.path.exists(path) else fallback

EMOJI_FONT = _pick_font("C:/Windows/Fonts/seguiemj.ttf")
TECH_FONT = _pick_font("C:/Windows/Fonts/consola.ttf")
JAPANESE_FONT = _pick_font("C:/Windows/Fonts/msgothic.ttc", fallback="Roboto")

# Palette tokens
BG = (0.024, 0.012, 0.039, 1.0)           # #06030A - Void Black
BG_SECONDARY = (0.039, 0.027, 0.067, 1.0) # #0A0711 - Near-black surface
BG_ELEVATED = (0.063, 0.039, 0.098, 1.0)  # #100A19 - Elevated surface
PANEL = (0.039, 0.027, 0.067, 0.94)       # Panel surface
PANEL_ALT = (0.063, 0.039, 0.098, 0.96)   # Elevated card
MAGENTA = (1.0, 0.239, 0.949, 1.0)        # #FF3DF2 - Hot magenta
MAGENTA_CORE = (1.0, 0.882, 0.984, 1.0)   # #FFE1FB - Supercharged core
VIOLET = (0.165, 0.039, 0.361, 1.0)       # Deep violet haze
MINT = (0.239, 1.0, 0.690, 1.0)           # #3DFFB0 - Neon mint
CYAN = (0.0, 0.88, 1.0, 1.0)              # Pure electric cyan
ELECTRIC_BLUE = (0.12, 0.45, 1.0, 1.0)    # Deep arcade blue
YELLOW = (1.0, 0.85, 0.30, 1.0)           # Soft gold
WHITE = (0.910, 0.875, 0.937, 1.0)        # #E8DFEF
TEXT_SEC = (0.639, 0.604, 0.678, 1.0)     # Secondary text
MUTED = (0.467, 0.439, 0.502, 1.0)        # Muted telemetry
RED = (1.0, 0.20, 0.35, 1.0)              # Crimson alert
SEPARATOR = (1.0, 1.0, 1.0, 0.09)         # Hairline border

ARCADE_MESSAGES = [
    "SYSTEM OVERLOAD? TOUCH GRASS. DIGITALLY. 🎮",
    "WELCOME TO THE BRAIN CELL RECHARGE STATION. ⚡",
    "NO QUESTS. NO DEADLINES. JUST VIBES. 👾",
    "YOUR LAST TWO BRAIN CELLS DESERVE A BREAK. 🧠",
    "DEFRAGGING NEURAL CACHE... COMMENCING CASUAL GAMING. 🕹️",
    "BURNOUT PROTOCOL DETECTED // FORCED DOWNTIME INITIATED. 🛡️",
    "THE SIDE QUESTS CAN WAIT. YOUR SANITY CANNOT. ☕",
    "PROCRAS-TINATING RESPONSIBLY SINCE 2026. 🚀",
]


# ---------------------------------------------------------------------------
# Retro Arcade Sound Engine (Non-blocking, Windows native, graceful fallback)
# ---------------------------------------------------------------------------

class ArcadeAudio:
    """Non-blocking retro 8-bit sound effects using native Windows beeper or silent fallback."""

    @staticmethod
    def play(sound_type, sound_enabled=True):
        if not sound_enabled or sys.platform != "win32":
            return

        def _worker():
            try:
                import winsound
                if sound_type == "click":
                    winsound.Beep(1200, 25)
                elif sound_type == "pop":
                    winsound.Beep(1850, 35)
                elif sound_type == "bonus":
                    winsound.Beep(1500, 35)
                    winsound.Beep(2100, 45)
                elif sound_type == "dodge":
                    winsound.Beep(950, 30)
                elif sound_type == "crash":
                    for f in (520, 400, 280, 160):
                        winsound.Beep(f, 40)
                elif sound_type == "level_up":
                    for f in (660, 880, 1100, 1320):
                        winsound.Beep(f, 45)
                elif sound_type == "error":
                    winsound.Beep(280, 90)
                elif sound_type == "tone":
                    winsound.Beep(880, 60)
                elif sound_type == "calm_chime":
                    winsound.Beep(1046, 60)
                    winsound.Beep(1318, 80)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    @staticmethod
    def play_frequency(freq, duration_ms=60, sound_enabled=True):
        if not sound_enabled or sys.platform != "win32":
            return

        def _worker():
            try:
                import winsound
                winsound.Beep(int(freq), int(duration_ms))
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Reusable Cyberpunk Arcade UI Components
# ---------------------------------------------------------------------------

class ArcadePanel(BoxLayout):
    """Sleek panel with customizable neon border and glow."""

    def __init__(self, bg_color=PANEL, border_color=None, radius=6, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self._radius = dp(radius)
        self.border_color = border_color or SEPARATOR

        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            self._line_color = Color(*self.border_color)
            self._line = Line(rounded_rectangle=(self.x, self.y, max(1, self.width), max(1, self.height), self._radius), width=dp(1.0))

        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, max(1, self.width), max(1, self.height), self._radius)

    def set_bg(self, color):
        self.bg_color = color
        self._color.rgba = color

    def set_border(self, color):
        self.border_color = color
        self._line_color.rgba = color


class ArcadeButton(ButtonBehavior, BoxLayout):
    """
    Sci-fi Chamfered Retro Arcade Button with hover and press animations.
    """
    text = StringProperty("")
    active = BooleanProperty(False)

    def __init__(self, text="", variant="primary", font_size="13.5sp",
                 height_dp=40, on_click=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(height_dp))
        kwargs.setdefault("padding", [dp(12), dp(6)])
        super().__init__(**kwargs)
        self.text = text
        self.variant = variant
        self.on_click = on_click
        self._hover = False

        if variant == "primary":
            self.fill_color = (0.28, 0.05, 0.28, 0.95)
            self.stroke_color = MAGENTA
            self.text_color = MAGENTA_CORE
        elif variant == "secondary":
            self.fill_color = (0.02, 0.22, 0.25, 0.95)
            self.stroke_color = CYAN
            self.text_color = CYAN
        elif variant == "mint":
            self.fill_color = (0.02, 0.24, 0.16, 0.95)
            self.stroke_color = MINT
            self.text_color = MINT
        elif variant == "danger":
            self.fill_color = (0.35, 0.06, 0.12, 0.95)
            self.stroke_color = RED
            self.text_color = WHITE
        elif variant == "gold":
            self.fill_color = (0.30, 0.22, 0.04, 0.95)
            self.stroke_color = YELLOW
            self.text_color = YELLOW
        else:
            self.fill_color = BG_ELEVATED
            self.stroke_color = SEPARATOR
            self.text_color = WHITE

        with self.canvas.before:
            self._bg_col = Color(*self.fill_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            self._line_col = Color(*self.stroke_color)
            self._border = Line(rounded_rectangle=(self.x, self.y, max(1, self.width), max(1, self.height), dp(4)), width=dp(1.2))

        self.lbl = Label(
            text=self.text,
            font_name=TECH_FONT,
            font_size=font_size,
            bold=True,
            color=self.text_color,
            markup=True,
            halign="center",
            valign="middle"
        )
        self.lbl.bind(size=self._sync_label)
        self.add_widget(self.lbl)

        self.bind(pos=self._redraw, size=self._redraw, text=self._update_text)
        Window.bind(mouse_pos=self._on_mouse)

    def _sync_label(self, *_):
        self.lbl.text_size = self.lbl.size

    def _update_text(self, _inst, val):
        self.lbl.text = val

    def _redraw(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, max(1, self.width), max(1, self.height), dp(4))

    def _on_mouse(self, _win, pos):
        if not self.get_root_window() or self.disabled or self.opacity == 0:
            return
        inside = self.collide_point(*pos)
        if inside != self._hover:
            self._hover = inside
            if inside:
                self._bg_col.a = 1.0
                self._border.width = dp(1.8)
            else:
                self._bg_col.a = 0.85
                self._border.width = dp(1.2)

    def on_touch_down(self, touch):
        if self.disabled or self.opacity == 0:
            return False
        if self.collide_point(*touch.pos):
            self._bg_col.a = 0.5
            return super().on_touch_down(touch)
        return False

    def on_touch_up(self, touch):
        if self.disabled or self.opacity == 0:
            return False
        self._bg_col.a = 0.85 if not self._hover else 1.0
        if self.collide_point(*touch.pos):
            super().on_touch_up(touch)
            if self.on_click:
                self.on_click()
            return True
        return super().on_touch_up(touch)


class ArcadeStarfield(Widget):
    """Cosmic drifting neon pixel starfield."""

    def __init__(self, count=40, **kwargs):
        super().__init__(**kwargs)
        self.stars = []
        self._count = count
        for _ in range(count):
            self.stars.append({
                "x": random.random(),
                "y": random.random(),
                "size": random.choice([dp(1.5), dp(2.0), dp(3.0)]),
                "speed": random.uniform(0.015, 0.06),
                "alpha": random.uniform(0.3, 0.9),
                "color": random.choice([CYAN, MAGENTA, MINT, YELLOW, WHITE]),
            })
        self.bind(pos=self._draw, size=self._draw)
        self._event = None

    def start(self):
        if not self._event:
            self._event = Clock.schedule_interval(self._tick, 1.0 / 30.0)

    def stop(self):
        if self._event:
            self._event.cancel()
            self._event = None

    def _tick(self, dt):
        for s in self.stars:
            s["y"] -= s["speed"] * dt
            if s["y"] < 0:
                s["y"] = 1.0
                s["x"] = random.random()
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        w = max(self.width, 1)
        h = max(self.height, 1)
        bx, by = self.pos
        with self.canvas:
            for s in self.stars:
                c = s["color"]
                Color(c[0], c[1], c[2], s["alpha"])
                sx = bx + s["x"] * w
                sy = by + s["y"] * h
                sz = s["size"]
                Rectangle(pos=(sx, sy), size=(sz, sz))


class ArcadeTicker(BoxLayout):
    """Animated cycling humorous cyberpunk marquee."""

    def __init__(self, messages=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(36))
        super().__init__(**kwargs)
        self.messages = messages or ARCADE_MESSAGES
        self.index = 0

        self.panel = ArcadePanel(
            bg_color=BG_SECONDARY, border_color=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.35),
            orientation="horizontal", padding=[dp(12), dp(4)], spacing=dp(8)
        )
        tag = Label(
            text="[b]VIBE CHECK //[/b]",
            font_name=TECH_FONT,
            font_size="12sp",
            color=MAGENTA,
            markup=True,
            size_hint_x=None,
            width=dp(120),
            halign="left"
        )
        self.lbl = Label(
            text=self.messages[0],
            font_name=TECH_FONT,
            font_size="12.5sp",
            color=WHITE,
            markup=True,
            halign="left"
        )
        self.lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.panel.add_widget(tag)
        self.panel.add_widget(self.lbl)
        self.add_widget(self.panel)

        self._timer = None

    def start(self):
        if not self._timer:
            self._timer = Clock.schedule_interval(self._next, 5.0)

    def stop(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _next(self, _dt):
        self.index = (self.index + 1) % len(self.messages)
        anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.3)
        self.lbl.text = self.messages[self.index]
        anim.start(self.lbl)


# ---------------------------------------------------------------------------
# GAME A: NEON DODGE (High-speed cyberpunk evasion)
# ---------------------------------------------------------------------------

class NeonDodgeGame(FloatLayout):
    """
    Playable Neon Dodge mini-game:
    - Control cyber ship via Arrow Keys / A-D on Windows, or On-Screen Touch / Mouse.
    - Dedicated Canvas widget: UI elements (HUD, score pointer, buttons) are never wiped.
    - Live prominent score pointer, velocity level, best record.
    - Explicit STOP GAME button and PAUSE button.
    - Dedicated GAME OVER / RUN SUMMARY modal with REPLAY [PLAY AGAIN] and RETURN TO ARCADE buttons.
    - High score saved automatically.
    """

    def __init__(self, app, on_exit=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.on_exit = on_exit

        self.is_running = False
        self.is_paused = False
        self.score = 0
        self.score_accum = 0.0
        self.high_score = self.app.arcade_scores.get("neon_dodge", 0)

        # Ship coordinates
        self.player_x = 0.5   # 0.0 to 1.0 ratio
        self.player_target_x = 0.5
        self.player_width = dp(40)
        self.player_height = dp(48)
        self.move_speed = 0.85  # speed ratio per second

        self.obstacles = []  # list of dicts: x, y, width, height, speed, type, color, rot
        self.particles = []  # list of dicts: x, y, vx, vy, life, max_life, color, size
        self.stars = []
        for _ in range(35):
            self.stars.append([random.random(), random.random(), random.uniform(0.1, 0.4)])

        self.keys_down = set()
        self._loop_event = None

        # Dedicated background game canvas widget (drawn behind all UI)
        self.game_canvas = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.game_canvas)

        # Build UI layout on top of game canvas
        self._build_ui()
        self.bind(pos=self._redraw, size=self._redraw)

    def _build_ui(self):
        # Top HUD Bar
        hud = ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(58), pos_hint={"x": 0, "top": 1},
            bg_color=BG_SECONDARY, border_color=CYAN
        )
        back_btn = ArcadeButton(
            text="🔙 ARCADE HUB", variant="secondary", height_dp=38,
            size_hint_x=None, width=dp(135), on_click=self.exit_game
        )

        # Score pointer (prominent, high contrast)
        self.score_lbl = Label(
            text="[b]SCORE: [ 0 ][/b]", font_name=TECH_FONT, font_size="18sp",
            color=MINT, bold=True, markup=True, halign="left"
        )
        self.high_lbl = Label(
            text=f"[b]BEST: {self.high_score}[/b]", font_name=TECH_FONT, font_size="14sp",
            color=YELLOW, markup=True, halign="left"
        )
        self.speed_lbl = Label(
            text="SPEED: 1.0x", font_name=TECH_FONT, font_size="13sp",
            color=MUTED, markup=True, halign="right"
        )
        self.pause_btn = ArcadeButton(
            text="⏸️ PAUSE", variant="primary", height_dp=38,
            size_hint_x=None, width=dp(95), on_click=self.toggle_pause
        )
        self.stop_btn = ArcadeButton(
            text="🛑 STOP GAME", variant="danger", height_dp=38,
            size_hint_x=None, width=dp(115), on_click=self.stop_game_action
        )

        hud.add_widget(back_btn)
        hud.add_widget(self.score_lbl)
        hud.add_widget(self.high_lbl)
        hud.add_widget(self.speed_lbl)
        hud.add_widget(self.pause_btn)
        hud.add_widget(self.stop_btn)
        self.add_widget(hud)

        # Bottom Mobile / Touch Controls Bar
        ctrl_bar = BoxLayout(
            orientation="horizontal", padding=[dp(16), dp(8)], spacing=dp(20),
            size_hint=(1, None), height=dp(68), pos_hint={"x": 0, "y": 0}
        )
        self.left_btn = ArcadeButton(
            text="◀ ◀  STEER LEFT [A / ←]", variant="secondary", height_dp=52, font_size="14.5sp",
            size_hint_x=0.5
        )
        self.right_btn = ArcadeButton(
            text="STEER RIGHT [D / →]  ▶ ▶", variant="secondary", height_dp=52, font_size="14.5sp",
            size_hint_x=0.5
        )
        self.left_btn.bind(on_press=lambda *_: self._set_key("left", True))
        self.left_btn.bind(on_release=lambda *_: self._set_key("left", False))
        self.right_btn.bind(on_press=lambda *_: self._set_key("right", True))
        self.right_btn.bind(on_release=lambda *_: self._set_key("right", False))

        ctrl_bar.add_widget(self.left_btn)
        ctrl_bar.add_widget(self.right_btn)
        self.add_widget(ctrl_bar)

        # Game Over / Run Completed Modal
        self.game_over_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(390), dp(290)),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            bg_color=(0.04, 0.02, 0.08, 0.98), border_color=RED
        )
        self.go_title = Label(
            text="[b]💀 RUN TERMINATED[/b]\n[size=13sp]CIRCUIT OVERLOAD[/size]",
            font_name=TECH_FONT, font_size="22sp", color=RED, markup=True, halign="center"
        )
        self.go_stats = Label(
            text="FINAL SCORE: 0 PTS\nBEST: 0 PTS", font_name=TECH_FONT, font_size="16sp",
            color=WHITE, bold=True, markup=True, halign="center"
        )
        self.retry_btn = ArcadeButton(
            text="🔄 REPLAY MISSION [SPACE]", variant="mint", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        self.lobby_btn = ArcadeButton(
            text="🔙 RETURN TO ARCADE", variant="secondary", height_dp=42, font_size="14sp",
            on_click=self.exit_game
        )
        self.game_over_panel.add_widget(self.go_title)
        self.game_over_panel.add_widget(self.go_stats)
        self.game_over_panel.add_widget(self.retry_btn)
        self.game_over_panel.add_widget(self.lobby_btn)
        self.game_over_panel.opacity = 0
        self.game_over_panel.disabled = True
        self.add_widget(self.game_over_panel)

        # Ready Overlay (tap to start)
        self.ready_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(380), dp(240)),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            bg_color=(0.03, 0.02, 0.07, 0.95), border_color=CYAN
        )
        ready_lbl = Label(
            text="[b]🚀 NEON DODGE[/b]\n[size=13sp]Dodge firewall debris & glitch pulses[/size]",
            font_name=TECH_FONT, font_size="20sp", color=CYAN, markup=True, halign="center"
        )
        start_btn = ArcadeButton(
            text="⚡ LAUNCH CRAFT [PLAY]", variant="primary", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        hint_lbl = Label(
            text="Use [A/D], [Arrows], or On-Screen Steering\nPress [Space] anytime to Pause or Replay",
            font_name=TECH_FONT, font_size="13sp", color=MUTED, halign="center"
        )
        self.ready_panel.add_widget(ready_lbl)
        self.ready_panel.add_widget(start_btn)
        self.ready_panel.add_widget(hint_lbl)
        self.add_widget(self.ready_panel)

    def _set_key(self, key, state):
        if state:
            self.keys_down.add(key)
        else:
            self.keys_down.discard(key)

    def on_enter(self):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.player_x = 0.5
        self.player_target_x = 0.5
        self.obstacles.clear()
        self.particles.clear()
        self.high_score = self.app.arcade_scores.get("neon_dodge", 0)
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self._redraw()

    def on_leave(self):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.stop_loop()

    def _on_key_down(self, _win, key, scancode, codepoint, modifier):
        if not self.parent or self.opacity == 0:
            return False
        # Left arrow (276) or 'a' (97)
        if key in (276, 97):
            self.keys_down.add("left")
            return True
        # Right arrow (275) or 'd' (100)
        elif key in (275, 100):
            self.keys_down.add("right")
            return True
        # Space (32) or Enter (13)
        elif key in (32, 13):
            if not self.is_running or self.game_over_panel.opacity > 0:
                self.start_game()
                return True
            else:
                self.toggle_pause()
                return True
        return False

    def _on_key_up(self, _win, key, scancode):
        if key in (276, 97):
            self.keys_down.discard("left")
        elif key in (275, 100):
            self.keys_down.discard("right")

    def on_touch_down(self, touch):
        # Allow dragging or tapping to move ship horizontally
        if self.is_running and not self.is_paused and self.y + dp(70) < touch.y < self.top - dp(55):
            rel_x = (touch.x - self.x) / max(1, self.width)
            self.player_target_x = max(0.08, min(0.92, rel_x))
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_running and not self.is_paused and self.y + dp(70) < touch.y < self.top - dp(55):
            rel_x = (touch.x - self.x) / max(1, self.width)
            self.player_target_x = max(0.08, min(0.92, rel_x))
            return True
        return super().on_touch_move(touch)

    def start_game(self, *_):
        self.is_running = True
        self.is_paused = False
        self.score = 0
        self.score_accum = 0.0
        self.player_x = 0.5
        self.player_target_x = 0.5
        self.obstacles.clear()
        self.particles.clear()
        self.keys_down.clear()

        self.ready_panel.opacity = 0
        self.ready_panel.disabled = True
        self.game_over_panel.opacity = 0
        self.game_over_panel.disabled = True
        self.pause_btn.text = "⏸️ PAUSE"
        self.score_lbl.text = "[b]SCORE: [ 0 ][/b]"

        ArcadeAudio.play("click", self.app.sound_enabled)
        self.stop_loop()
        self._loop_event = Clock.schedule_interval(self._tick, 1.0 / 60.0)

    def stop_loop(self):
        if self._loop_event:
            self._loop_event.cancel()
            self._loop_event = None

    def toggle_pause(self, *_):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        self.pause_btn.text = "▶ RESUME" if self.is_paused else "⏸️ PAUSE"
        ArcadeAudio.play("click", self.app.sound_enabled)

    def stop_game_action(self, *_):
        """Action button to stop the running game and show the run summary & replay buttons."""
        if not self.is_running and self.ready_panel.opacity > 0:
            self.exit_game()
            return
        self._trigger_game_over(stopped=True)

    def exit_game(self, *_):
        self.stop_loop()
        self.is_running = False
        if self.on_exit:
            self.on_exit()

    def _tick(self, dt):
        if not self.is_running or self.is_paused:
            return

        # 1. Update player position
        if "left" in self.keys_down:
            self.player_x = max(0.08, self.player_x - self.move_speed * dt)
            self.player_target_x = self.player_x
        elif "right" in self.keys_down:
            self.player_x = min(0.92, self.player_x + self.move_speed * dt)
            self.player_target_x = self.player_x
        else:
            diff = self.player_target_x - self.player_x
            if abs(diff) > 0.005:
                self.player_x += diff * min(1.0, 16.0 * dt)

        # 2. Add thruster particles
        px = self.x + self.player_x * self.width
        py = self.y + dp(90)
        if random.random() < 0.65:
            self.particles.append({
                "x": px + random.uniform(-dp(6), dp(6)),
                "y": py - dp(18),
                "vx": random.uniform(-dp(15), dp(15)),
                "vy": -random.uniform(dp(80), dp(140)),
                "life": 0.0,
                "max_life": 0.35,
                "color": random.choice([CYAN, MAGENTA, MINT]),
                "size": dp(3.5),
            })

        # 3. Increase score & calculate current speed level
        self.score_accum += 30.0 * dt
        self.score = int(self.score_accum)
        speed_factor = 1.0 + min(2.5, self.score / 250.0)
        self.score_lbl.text = f"[b]SCORE: [ {self.score} ][/b]"
        self.speed_lbl.text = f"SPEED: {speed_factor:.1f}x"

        # 4. Spawn obstacles
        spawn_rate = 0.035 * speed_factor
        if random.random() < spawn_rate:
            obs_type = random.choice(["cube", "laser", "orb"])
            obs_w = dp(36) if obs_type == "cube" else (dp(64) if obs_type == "laser" else dp(32))
            obs_h = dp(36) if obs_type == "cube" else (dp(16) if obs_type == "laser" else dp(32))
            obs_col = RED if obs_type == "cube" else (MAGENTA if obs_type == "laser" else YELLOW)
            self.obstacles.append({
                "x": random.uniform(0.10, 0.90),
                "y": max(self.top, self.y + dp(450)) + dp(30),
                "w": obs_w,
                "h": obs_h,
                "type": obs_type,
                "color": obs_col,
                "rot": 0.0,
                "speed": random.uniform(dp(180), dp(260)) * speed_factor
            })

        # 5. Move obstacles & detect collisions
        pw = self.player_width * 0.70
        ph = self.player_height * 0.70

        surviving = []
        for obs in self.obstacles:
            obs["y"] -= obs["speed"] * dt
            obs["rot"] += 120 * dt
            ox = self.x + obs["x"] * self.width
            oy = obs["y"]
            ow = obs["w"]
            oh = obs["h"]

            # Collision check (AABB overlap)
            if (abs(px - ox) * 2 < (pw + ow)) and (abs(py - oy) * 2 < (ph + oh)):
                self._trigger_game_over(stopped=False)
                return

            # Keep if still on screen
            if oy + oh > self.y + dp(60):
                surviving.append(obs)
            else:
                # Successfully dodged!
                self.score_accum += 25.0
                self.score = int(self.score_accum)
                self.score_lbl.text = f"[b]SCORE: [ {self.score} ][/b]"
                ArcadeAudio.play("dodge", self.app.sound_enabled)
        self.obstacles = surviving

        # 6. Update particles
        surviving_p = []
        for p in self.particles:
            p["life"] += dt
            if p["life"] < p["max_life"]:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                surviving_p.append(p)
        self.particles = surviving_p

        # 7. Redraw canvas
        self._redraw()

    def _trigger_game_over(self, stopped=False):
        self.is_running = False
        self.stop_loop()

        if stopped:
            ArcadeAudio.play("click", self.app.sound_enabled)
        else:
            ArcadeAudio.play("crash", self.app.sound_enabled)

        # Explosion burst particles
        px = self.x + self.player_x * self.width
        py = self.y + dp(90)
        for _ in range(40):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(dp(60), dp(240))
            self.particles.append({
                "x": px, "y": py,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "life": 0.0,
                "max_life": random.uniform(0.4, 0.8),
                "color": random.choice([RED, YELLOW, MAGENTA_CORE, WHITE]),
                "size": dp(4.0),
            })
        self._redraw()

        # Update high score
        is_new_best = self.score > self.high_score
        if is_new_best:
            self.high_score = self.score
            self.app.arcade_scores["neon_dodge"] = self.score
            self.app.save_data()
            ArcadeAudio.play("level_up", self.app.sound_enabled)

        # Show modal
        if stopped:
            self.go_title.text = "[b]🛑 SPRINT TERMINATED[/b]\n[size=12sp]MISSION REPORT READY[/size]"
            self.go_title.color = CYAN
        elif is_new_best:
            self.go_title.text = "[b]🏆 NEW HIGH SCORE![/b]\n[size=12sp]LEGENDARY EVASION RUN[/size]"
            self.go_title.color = YELLOW
        else:
            self.go_title.text = "[b]💀 RUN TERMINATED[/b]\n[size=12sp]CIRCUIT OVERLOAD // CRASH[/size]"
            self.go_title.color = RED

        self.go_stats.text = f"FINAL SCORE: [ {self.score} PTS ]\nBEST RECORD: [ {self.high_score} PTS ]"
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self.game_over_panel.opacity = 1
        self.game_over_panel.disabled = False

    def _redraw(self, *_):
        self.game_canvas.canvas.clear()
        bx, by = self.pos
        w = max(self.width, 1)
        h = max(self.height, 1)

        with self.game_canvas.canvas:
            Color(*BG)
            Rectangle(pos=(bx, by), size=(w, h))

            # Perspective grid lines moving down
            Color(CYAN[0], CYAN[1], CYAN[2], 0.12)
            grid_y = by + dp(70)
            Line(points=[bx, grid_y, bx + w, grid_y], width=dp(1.2))
            for i in range(7):
                rx = bx + (i / 6.0) * w
                Line(points=[rx, grid_y, rx, by + h], width=dp(0.8))

            # Cosmic stars
            for s in self.stars:
                Color(1, 1, 1, s[2] * 0.7)
                sx = bx + s[0] * w
                sy = by + s[1] * h
                Rectangle(pos=(sx, sy), size=(dp(1.5), dp(1.5)))

            # Draw Particles
            for p in self.particles:
                alpha = max(0, 1.0 - (p["life"] / p["max_life"]))
                c = p["color"]
                Color(c[0], c[1], c[2], alpha)
                sz = p["size"] * alpha
                Rectangle(pos=(p["x"] - sz / 2, p["y"] - sz / 2), size=(sz, sz))

            # Draw Obstacles
            for obs in self.obstacles:
                ox = bx + obs["x"] * w
                oy = obs["y"]
                ow = obs["w"]
                oh = obs["h"]
                c = obs["color"]
                Color(*c)
                if obs["type"] == "cube":
                    RoundedRectangle(pos=(ox - ow / 2, oy - oh / 2), size=(ow, oh), radius=[dp(4)])
                    Color(1, 1, 1, 0.4)
                    Line(rectangle=(ox - ow / 2, oy - oh / 2, ow, oh), width=dp(1.2))
                elif obs["type"] == "laser":
                    RoundedRectangle(pos=(ox - ow / 2, oy - oh / 2), size=(ow, oh), radius=[dp(3)])
                    Color(1, 1, 1, 0.8)
                    Line(points=[ox - ow / 2, oy, ox + ow / 2, oy], width=dp(2.0))
                else:  # orb
                    Ellipse(pos=(ox - ow / 2, oy - oh / 2), size=(ow, oh))
                    Color(1, 1, 1, 0.6)
                    Line(circle=(ox, oy, ow / 2), width=dp(1.2))

            # Draw Player Ship (if alive)
            if self.is_running:
                px = bx + self.player_x * w
                py = by + dp(90)
                pw = self.player_width
                ph = self.player_height

                # Ship Aura Glow
                Color(CYAN[0], CYAN[1], CYAN[2], 0.25)
                Ellipse(pos=(px - pw, py - ph / 2), size=(pw * 2, ph * 1.5))

                # Stylized triangular neon spaceship
                Color(*CYAN)
                Line(points=[
                    px - pw / 2, py - ph / 2,
                    px, py + ph / 2,
                    px + pw / 2, py - ph / 2,
                    px, py - ph / 4,
                    px - pw / 2, py - ph / 2
                ], width=dp(2.0), close=True)

                # Cockpit Core
                Color(*MAGENTA_CORE)
                Ellipse(pos=(px - dp(4), py - dp(2)), size=(dp(8), dp(8)))


# ---------------------------------------------------------------------------
# GAME B: PIXEL POP (Reflex Target Burst)
# ---------------------------------------------------------------------------

class PixelPopGame(FloatLayout):
    """
    Playable Pixel Pop reflex mini-game:
    - 30-second rapid blitz round.
    - Dedicated Canvas widget: UI elements (HUD, timer, score, combo, buttons) are never wiped.
    - Click or tap floating neon cyber targets.
    - Particle bursts, floating score popups, and combo multipliers.
    - Golden targets add bonus time (+2s).
    - Dedicated STOP BLITZ button and ROUND RESULTS modal with REPLAY.
    """

    def __init__(self, app, on_exit=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.on_exit = on_exit

        self.time_left = 30.0
        self.score = 0
        self.combo = 1
        self.last_pop_time = 0.0
        self.popped_count = 0
        self.high_score = self.app.arcade_scores.get("pixel_pop", 0)

        self.targets = []      # list of dicts: id, x, y, size, type, color, life, max_life, scale
        self.particles = []    # explosion particles
        self.popups = []       # floating "+100" labels

        self.is_running = False
        self._loop_event = None

        # Dedicated background game canvas widget
        self.game_canvas = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.game_canvas)

        self._build_ui()
        self.bind(pos=self._redraw, size=self._redraw)

    def _build_ui(self):
        # Top HUD Bar
        hud = ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(58), pos_hint={"x": 0, "top": 1},
            bg_color=BG_SECONDARY, border_color=MAGENTA
        )
        back_btn = ArcadeButton(
            text="🔙 ARCADE HUB", variant="secondary", height_dp=38,
            size_hint_x=None, width=dp(135), on_click=self.exit_game
        )
        self.timer_lbl = Label(
            text="[b]⏱️ 30.0s[/b]", font_name=TECH_FONT, font_size="18sp",
            color=YELLOW, bold=True, markup=True, halign="left"
        )
        self.score_lbl = Label(
            text="[b]SCORE: [ 0 ][/b]", font_name=TECH_FONT, font_size="18sp",
            color=MINT, bold=True, markup=True, halign="left"
        )
        self.combo_lbl = Label(
            text="[b]COMBO: x1[/b]", font_name=TECH_FONT, font_size="14sp",
            color=MAGENTA, bold=True, markup=True, halign="left"
        )
        self.high_lbl = Label(
            text=f"[b]BEST: {self.high_score}[/b]", font_name=TECH_FONT, font_size="13sp",
            color=MUTED, markup=True, halign="right"
        )
        self.stop_btn = ArcadeButton(
            text="🛑 STOP BLITZ", variant="danger", height_dp=38,
            size_hint_x=None, width=dp(120), on_click=self.stop_round_action
        )

        hud.add_widget(back_btn)
        hud.add_widget(self.timer_lbl)
        hud.add_widget(self.score_lbl)
        hud.add_widget(self.combo_lbl)
        hud.add_widget(self.high_lbl)
        hud.add_widget(self.stop_btn)
        self.add_widget(hud)

        # Game Over / Results Modal
        self.results_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(390), dp(300)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            bg_color=(0.04, 0.02, 0.08, 0.98), border_color=MAGENTA
        )
        self.res_title = Label(
            text="[b]🎯 TIME'S UP![/b]\n[size=13sp]BLITZ ROUND COMPLETED[/size]",
            font_name=TECH_FONT, font_size="22sp", color=MAGENTA, markup=True, halign="center"
        )
        self.res_stats = Label(
            text="SCORE: [ 0 PTS ]\nTARGETS POPPED: 0\nBEST RECORD: 0 PTS",
            font_name=TECH_FONT, font_size="16sp", color=WHITE, bold=True, markup=True, halign="center"
        )
        self.play_again_btn = ArcadeButton(
            text="🔄 REPLAY [30s BLITZ]", variant="mint", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        self.lobby_btn = ArcadeButton(
            text="🔙 RETURN TO ARCADE", variant="secondary", height_dp=42, font_size="14sp",
            on_click=self.exit_game
        )
        self.results_panel.add_widget(self.res_title)
        self.results_panel.add_widget(self.res_stats)
        self.results_panel.add_widget(self.play_again_btn)
        self.results_panel.add_widget(self.lobby_btn)
        self.results_panel.opacity = 0
        self.results_panel.disabled = True
        self.add_widget(self.results_panel)

        # Welcome Card
        self.welcome_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(380), dp(250)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            bg_color=(0.03, 0.02, 0.07, 0.95), border_color=MAGENTA
        )
        w_title = Label(
            text="[b]🎯 PIXEL POP[/b]\n[size=13sp]Burst rogue data packets before they expire![/size]",
            font_name=TECH_FONT, font_size="20sp", color=MAGENTA, markup=True, halign="center"
        )
        start_btn = ArcadeButton(
            text="⚡ START BLITZ [30 SECONDS]", variant="primary", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        w_hint = Label(
            text="Tap targets rapidly to build your Combo Multiplier!\nGolden targets award +2s bonus time.",
            font_name=TECH_FONT, font_size="13sp", color=MUTED, halign="center"
        )
        self.welcome_panel.add_widget(w_title)
        self.welcome_panel.add_widget(start_btn)
        self.welcome_panel.add_widget(w_hint)
        self.add_widget(self.welcome_panel)

    def on_enter(self):
        Window.bind(on_key_down=self._on_key_down)
        self.targets.clear()
        self.particles.clear()
        self.popups.clear()
        self.high_score = self.app.arcade_scores.get("pixel_pop", 0)
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self._redraw()

    def on_leave(self):
        Window.unbind(on_key_down=self._on_key_down)
        self.stop_loop()

    def _on_key_down(self, _win, key, scancode, codepoint, modifier):
        if not self.parent or self.opacity == 0:
            return False
        if key in (32, 13):
            if not self.is_running or self.results_panel.opacity > 0:
                self.start_game()
                return True
        return False

    def start_game(self, *_):
        self.is_running = True
        self.time_left = 30.0
        self.score = 0
        self.combo = 1
        self.popped_count = 0
        self.targets.clear()
        self.particles.clear()
        self.popups.clear()

        self.welcome_panel.opacity = 0
        self.welcome_panel.disabled = True
        self.results_panel.opacity = 0
        self.results_panel.disabled = True

        self.score_lbl.text = "[b]SCORE: [ 0 ][/b]"
        self.combo_lbl.text = "[b]COMBO: x1[/b]"
        self.timer_lbl.text = "[b]⏱️ 30.0s[/b]"

        ArcadeAudio.play("click", self.app.sound_enabled)
        self.stop_loop()
        self._loop_event = Clock.schedule_interval(self._tick, 1.0 / 60.0)

    def stop_loop(self):
        if self._loop_event:
            self._loop_event.cancel()
            self._loop_event = None

    def stop_round_action(self, *_):
        """Action button to stop the running blitz round and display results & replay buttons."""
        if not self.is_running and self.welcome_panel.opacity > 0:
            self.exit_game()
            return
        self._finish_round(stopped=True)

    def exit_game(self, *_):
        self.stop_loop()
        self.is_running = False
        if self.on_exit:
            self.on_exit()

    def on_touch_down(self, touch):
        if not self.is_running:
            return super().on_touch_down(touch)

        if touch.y > self.top - dp(56):
            return super().on_touch_down(touch)

        hit_target = None
        for t in reversed(self.targets):
            tx = self.x + t["x"] * self.width
            ty = self.y + t["y"] * self.height
            rad = t["size"] / 2
            dist = math.hypot(touch.x - tx, touch.y - ty)
            if dist <= rad * 1.30:
                hit_target = t
                break

        if hit_target:
            self._pop_target(hit_target)
            return True

        return super().on_touch_down(touch)

    def _pop_target(self, t):
        self.targets.remove(t)
        self.popped_count += 1
        now = Clock.get_time()

        if now - self.last_pop_time < 1.2:
            self.combo = min(8, self.combo + 1)
        else:
            self.combo = 1
        self.last_pop_time = now

        pts = t["points"] * self.combo
        self.score += pts

        if t["type"] == "gold":
            self.time_left = min(60.0, self.time_left + 2.0)
            ArcadeAudio.play("bonus", self.app.sound_enabled)
            self._add_popup(t["x"], t["y"], f"+{pts} (+2s TIME!)", YELLOW)
        else:
            ArcadeAudio.play("pop", self.app.sound_enabled)
            combo_str = f" x{self.combo}!" if self.combo > 1 else ""
            self._add_popup(t["x"], t["y"], f"+{pts}{combo_str}", t["color"])

        tx = self.x + t["x"] * self.width
        ty = self.y + t["y"] * self.height
        for _ in range(16):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(dp(50), dp(180))
            self.particles.append({
                "x": tx, "y": ty,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "life": 0.0,
                "max_life": random.uniform(0.3, 0.6),
                "color": t["color"],
                "size": dp(3.5),
            })

        self.score_lbl.text = f"[b]SCORE: [ {self.score} ][/b]"
        self.combo_lbl.text = f"[b]COMBO: x{self.combo}[/b]"

    def _add_popup(self, x_ratio, y_ratio, text, color):
        px = self.x + x_ratio * self.width
        py = self.y + y_ratio * self.height
        self.popups.append({
            "x": px, "y": py,
            "text": text,
            "color": color,
            "life": 0.0,
            "max_life": 0.75
        })

    def _tick(self, dt):
        if not self.is_running:
            return

        self.time_left = max(0.0, self.time_left - dt)
        self.timer_lbl.text = f"[b]⏱️ {self.time_left:.1f}s[/b]"

        if self.time_left <= 0:
            self._finish_round(stopped=False)
            return

        if len(self.targets) < 5 and random.random() < 0.15:
            r = random.random()
            if r < 0.18:
                t_type = "gold"
                col = YELLOW
                pts = 300
                sz = dp(46)
            elif r < 0.55:
                t_type = "magenta"
                col = MAGENTA
                pts = 150
                sz = dp(42)
            else:
                t_type = "cyan"
                col = CYAN
                pts = 100
                sz = dp(40)

            self.targets.append({
                "x": random.uniform(0.12, 0.88),
                "y": random.uniform(0.14, 0.80),
                "size": sz,
                "type": t_type,
                "color": col,
                "points": pts,
                "life": 0.0,
                "max_life": random.uniform(2.2, 3.4),
                "pulse": 0.0
            })

        surviving_t = []
        for t in self.targets:
            t["life"] += dt
            t["pulse"] += 4.0 * dt
            if t["life"] < t["max_life"]:
                surviving_t.append(t)
        self.targets = surviving_t

        surviving_p = []
        for p in self.particles:
            p["life"] += dt
            if p["life"] < p["max_life"]:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                surviving_p.append(p)
        self.particles = surviving_p

        surviving_pop = []
        for pop in self.popups:
            pop["life"] += dt
            pop["y"] += dp(40) * dt
            if pop["life"] < pop["max_life"]:
                surviving_pop.append(pop)
        self.popups = surviving_pop

        if Clock.get_time() - self.last_pop_time > 1.3 and self.combo > 1:
            self.combo = 1
            self.combo_lbl.text = "[b]COMBO: x1[/b]"

        self._redraw()

    def _finish_round(self, stopped=False):
        self.is_running = False
        self.stop_loop()

        if stopped:
            ArcadeAudio.play("click", self.app.sound_enabled)
        else:
            ArcadeAudio.play("level_up", self.app.sound_enabled)

        is_new_best = self.score > self.high_score
        if is_new_best:
            self.high_score = self.score
            self.app.arcade_scores["pixel_pop"] = self.score
            self.app.save_data()

        if stopped:
            self.res_title.text = "[b]🛑 BLITZ STOPPED[/b]\n[size=12sp]ROUND REPORT COMPLETED[/size]"
            self.res_title.color = CYAN
        elif is_new_best:
            self.res_title.text = "[b]🏆 NEW HIGH SCORE![/b]\n[size=12sp]REFLEX MASTER RUN[/size]"
            self.res_title.color = YELLOW
        else:
            self.res_title.text = "[b]🎯 TIME'S UP![/b]\n[size=12sp]BLITZ ROUND COMPLETED[/size]"
            self.res_title.color = MAGENTA

        self.res_stats.text = f"FINAL SCORE: [ {self.score} PTS ]\nTARGETS POPPED: [ {self.popped_count} ]\nBEST RECORD: [ {self.high_score} PTS ]"
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self.results_panel.opacity = 1
        self.results_panel.disabled = False
        self._redraw()

    def _redraw(self, *_):
        self.game_canvas.canvas.clear()
        bx, by = self.pos
        w = max(self.width, 1)
        h = max(self.height, 1)

        with self.game_canvas.canvas:
            Color(*BG)
            Rectangle(pos=(bx, by), size=(w, h))

            Color(1, 1, 1, 0.03)
            for i in range(8):
                gy = by + (i / 7.0) * h
                Line(points=[bx, gy, bx + w, gy], width=dp(0.8))
                gx = bx + (i / 7.0) * w
                Line(points=[gx, by, gx, by + h], width=dp(0.8))

            for t in self.targets:
                tx = bx + t["x"] * w
                ty = by + t["y"] * h
                pulse_scale = 1.0 + 0.08 * math.sin(t["pulse"])
                sz = t["size"] * pulse_scale
                c = t["color"]

                remaining_ratio = max(0, 1.0 - (t["life"] / t["max_life"]))
                Color(c[0], c[1], c[2], 0.35)
                Line(circle=(tx, ty, (sz / 2) * (1.1 + 0.3 * (1.0 - remaining_ratio))), width=dp(1.2))

                Color(c[0], c[1], c[2], 0.22)
                Ellipse(pos=(tx - sz / 2, ty - sz / 2), size=(sz, sz))
                Color(*c)
                Line(circle=(tx, ty, sz / 2), width=dp(2.0))

                Color(1, 1, 1, 0.9)
                Ellipse(pos=(tx - dp(5), ty - dp(5)), size=(dp(10), dp(10)))

            for p in self.particles:
                alpha = max(0, 1.0 - (p["life"] / p["max_life"]))
                c = p["color"]
                Color(c[0], c[1], c[2], alpha)
                sz = p["size"] * alpha
                Rectangle(pos=(p["x"] - sz / 2, p["y"] - sz / 2), size=(sz, sz))


# ---------------------------------------------------------------------------
# GAME C: CYBER BREAKER (Firewall Block Smash Arcade)
# Replaces Memory Glitch with an exciting, 100% playable retro arcade smasher!
# ---------------------------------------------------------------------------

class CyberBreakerGame(FloatLayout):
    """
    Playable Cyber Breaker mini-game (Replaces Memory Glitch):
    - Control a high-tech quantum cyber paddle.
    - Bounce the energy plasma orb to shatter encrypted firewall blocks.
    - Dynamic angle bounce physics off paddle with edge steering.
    - Particle explosions on brick impact.
    - Live score pointer, lives counter, blocks left, pause, stop button.
    - Instant launch on start, auto-relaunch on life loss, and Spacebar replay.
    """

    def __init__(self, app, on_exit=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.on_exit = on_exit

        self.score = 0
        self.lives = 3
        self.high_score = self.app.arcade_scores.get("cyber_breaker", 0)

        self.is_running = False
        self.is_paused = False
        self.ball_attached = True

        # Paddle parameters
        self.paddle_x = 0.5  # ratio 0.0 to 1.0 (center)
        self.paddle_target_x = 0.5
        self.paddle_w = dp(92)
        self.paddle_h = dp(14)
        self.move_speed = 1.15

        # Ball parameters (widget-relative coordinates)
        self.ball_r = dp(7)
        self.ball_x = dp(200)
        self.ball_y = dp(100)
        self.ball_vx = dp(240)
        self.ball_vy = dp(340)

        self.bricks = []
        self.particles = []
        self.keys_down = set()
        self._loop_event = None
        self._relaunch_event = None

        # Dedicated background game canvas widget (drawn behind all UI)
        self.game_canvas = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.game_canvas)

        self._build_ui()
        self.bind(pos=self._redraw, size=self._on_resize)

    def _build_ui(self):
        # 1. Top HUD Bar
        hud = ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(58), pos_hint={"x": 0, "top": 1},
            bg_color=BG_SECONDARY, border_color=YELLOW
        )
        back_btn = ArcadeButton(
            text="🔙 ARCADE HUB", variant="secondary", height_dp=38,
            size_hint_x=None, width=dp(135), on_click=self.exit_game
        )
        self.score_lbl = Label(
            text="[b]SCORE: [ 0 ][/b]", font_name=TECH_FONT, font_size="18sp",
            color=MINT, bold=True, markup=True, halign="left"
        )
        self.lives_lbl = Label(
            text="[b]LIVES: [ ❤️❤️❤️ ][/b]", font_name=EMOJI_FONT, font_size="15sp",
            color=RED, bold=True, markup=True, halign="left"
        )
        self.bricks_lbl = Label(
            text="[b]BLOCKS: [ 28 ][/b]", font_name=TECH_FONT, font_size="15sp",
            color=YELLOW, bold=True, markup=True, halign="left"
        )
        self.high_lbl = Label(
            text=f"[b]BEST: {self.high_score}[/b]", font_name=TECH_FONT, font_size="13sp",
            color=MUTED, markup=True, halign="right"
        )
        self.pause_btn = ArcadeButton(
            text="⏸️ PAUSE", variant="primary", height_dp=38,
            size_hint_x=None, width=dp(95), on_click=self.toggle_pause
        )
        self.stop_btn = ArcadeButton(
            text="🛑 STOP GAME", variant="danger", height_dp=38,
            size_hint_x=None, width=dp(115), on_click=self.stop_game_action
        )

        hud.add_widget(back_btn)
        hud.add_widget(self.score_lbl)
        hud.add_widget(self.lives_lbl)
        hud.add_widget(self.bricks_lbl)
        hud.add_widget(self.high_lbl)
        hud.add_widget(self.pause_btn)
        hud.add_widget(self.stop_btn)
        self.add_widget(hud)

        # 2. Bottom Mobile / Touch Controls Bar
        ctrl_bar = BoxLayout(
            orientation="horizontal", padding=[dp(16), dp(8)], spacing=dp(20),
            size_hint=(1, None), height=dp(68), pos_hint={"x": 0, "y": 0}
        )
        self.left_btn = ArcadeButton(
            text="◀ ◀  PADDLE LEFT [A / ←]", variant="secondary", height_dp=52, font_size="14.5sp",
            size_hint_x=0.5
        )
        self.right_btn = ArcadeButton(
            text="PADDLE RIGHT [D / →]  ▶ ▶", variant="secondary", height_dp=52, font_size="14.5sp",
            size_hint_x=0.5
        )
        self.left_btn.bind(on_press=lambda *_: self._set_key("left", True))
        self.left_btn.bind(on_release=lambda *_: self._set_key("left", False))
        self.right_btn.bind(on_press=lambda *_: self._set_key("right", True))
        self.right_btn.bind(on_release=lambda *_: self._set_key("right", False))

        ctrl_bar.add_widget(self.left_btn)
        ctrl_bar.add_widget(self.right_btn)
        self.add_widget(ctrl_bar)

        # 3. Ready / Start Overlay
        self.ready_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(390), dp(260)),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            bg_color=(0.03, 0.02, 0.07, 0.96), border_color=YELLOW
        )
        self.ready_title = Label(
            text="[b]🧱 CYBER BREAKER[/b]\n[size=13sp]QUANTUM FIREWALL SMASHER[/size]",
            font_name=TECH_FONT, font_size="20sp", color=YELLOW, markup=True, halign="center"
        )
        start_btn = ArcadeButton(
            text="⚡ START BREAKER [SPACE / PLAY]", variant="gold", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        hint_lbl = Label(
            text="Controls: [A/D], [Arrows], or Touch / Drag\nBounce plasma orb to shatter all 28 firewall blocks.\nPress [Space] to pause or replay.",
            font_name=TECH_FONT, font_size="13sp", color=TEXT_SEC, halign="center"
        )
        self.ready_panel.add_widget(self.ready_title)
        self.ready_panel.add_widget(start_btn)
        self.ready_panel.add_widget(hint_lbl)
        self.add_widget(self.ready_panel)

        # 4. Game Over / Completion Modal
        self.game_over_panel = ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(18)], spacing=dp(12),
            size_hint=(None, None), size=(dp(390), dp(290)),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            bg_color=(0.04, 0.02, 0.08, 0.98), border_color=RED
        )
        self.go_title = Label(
            text="[b]💀 BREACH FAILED[/b]\n[size=13sp]ENERGY DEPLETED[/size]",
            font_name=TECH_FONT, font_size="22sp", color=RED, markup=True, halign="center"
        )
        self.go_stats = Label(
            text="FINAL SCORE: [ 0 PTS ]\nBEST RECORD: [ 0 PTS ]",
            font_name=TECH_FONT, font_size="16sp", color=WHITE, bold=True, markup=True, halign="center"
        )
        self.retry_btn = ArcadeButton(
            text="🔄 REPLAY SECTOR [SPACE]", variant="mint", height_dp=48, font_size="15sp",
            on_click=self.start_game
        )
        self.lobby_btn = ArcadeButton(
            text="🔙 RETURN TO ARCADE", variant="secondary", height_dp=42, font_size="14sp",
            on_click=self.exit_game
        )
        self.game_over_panel.add_widget(self.go_title)
        self.game_over_panel.add_widget(self.go_stats)
        self.game_over_panel.add_widget(self.retry_btn)
        self.game_over_panel.add_widget(self.lobby_btn)
        self.game_over_panel.opacity = 0
        self.game_over_panel.disabled = True
        self.add_widget(self.game_over_panel)

    def _set_key(self, key, state):
        if state:
            self.keys_down.add(key)
        else:
            self.keys_down.discard(key)

    def _on_resize(self, *_):
        if len(self.bricks) == 0:
            self._create_bricks()
        self._redraw()

    def _create_bricks(self):
        """Constructs 28 firewall blocks (4 rows of 7) with relative proportions."""
        self.bricks.clear()
        cols = 7
        rows = 4
        row_colors = [
            (MAGENTA, 150),
            (CYAN, 100),
            (MINT, 80),
            (YELLOW, 50),
        ]

        margin_ratio_x = 0.05
        avail_ratio_w = 0.90
        spacing_ratio_x = 0.012
        brick_ratio_w = (avail_ratio_w - (cols - 1) * spacing_ratio_x) / cols

        for r_idx in range(rows):
            col_theme, pts = row_colors[r_idx % len(row_colors)]
            for c_idx in range(cols):
                rel_x = margin_ratio_x + c_idx * (brick_ratio_w + spacing_ratio_x)
                self.bricks.append({
                    "c_idx": c_idx,
                    "r_idx": r_idx,
                    "rel_x": rel_x,
                    "rel_w": brick_ratio_w,
                    "color": col_theme,
                    "points": pts,
                    "alive": True
                })

    def on_enter(self):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.paddle_x = 0.5
        self.paddle_target_x = 0.5
        self.ball_attached = True
        w = max(self.width, dp(400))
        self.ball_x = w * 0.5
        self.ball_y = dp(78) + self.paddle_h + self.ball_r + dp(2)
        self.particles.clear()
        self.high_score = self.app.arcade_scores.get("cyber_breaker", 0)
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self.ready_panel.opacity = 1
        self.ready_panel.disabled = False
        self.game_over_panel.opacity = 0
        self.game_over_panel.disabled = True
        self._create_bricks()
        self._redraw()

    def on_leave(self):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.stop_loop()

    def _on_key_down(self, _win, key, scancode, codepoint, modifier):
        if not self.parent or self.opacity == 0:
            return False
        if key in (276, 97):  # Left / A
            self.keys_down.add("left")
            return True
        elif key in (275, 100):  # Right / D
            self.keys_down.add("right")
            return True
        elif key in (32, 13):  # Space or Enter
            if self.game_over_panel.opacity > 0:
                self.start_game()
                return True
            elif not self.is_running or self.ready_panel.opacity > 0:
                self.start_game()
                return True
            elif self.ball_attached:
                self._launch_ball()
                return True
            else:
                self.toggle_pause()
                return True
        return False

    def _on_key_up(self, _win, key, scancode):
        if key in (276, 97):
            self.keys_down.discard("left")
        elif key in (275, 100):
            self.keys_down.discard("right")

    def on_touch_down(self, touch):
        if self.is_running and not self.is_paused and self.y + dp(70) < touch.y < self.top - dp(56):
            rel_x = (touch.x - self.x) / max(1, self.width)
            self.paddle_target_x = max(0.08, min(0.92, rel_x))
            if self.ball_attached:
                self._launch_ball()
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_running and not self.is_paused and self.y + dp(70) < touch.y < self.top - dp(56):
            rel_x = (touch.x - self.x) / max(1, self.width)
            self.paddle_target_x = max(0.08, min(0.92, rel_x))
            return True
        return super().on_touch_move(touch)

    def start_game(self, *_):
        self.is_running = True
        self.is_paused = False
        self.score = 0
        self.lives = 3
        self.paddle_x = 0.5
        self.paddle_target_x = 0.5
        self.particles.clear()
        self.keys_down.clear()

        self._create_bricks()
        self.ready_panel.opacity = 0
        self.ready_panel.disabled = True
        self.game_over_panel.opacity = 0
        self.game_over_panel.disabled = True

        self.pause_btn.text = "⏸️ PAUSE"
        self.score_lbl.text = "[b]SCORE: [ 0 ][/b]"
        self.lives_lbl.text = "[b]LIVES: [ ❤️❤️❤️ ][/b]"
        self.bricks_lbl.text = f"[b]BLOCKS: [ {len(self.bricks)} ][/b]"

        # Launch ball immediately
        w = max(self.width, dp(400))
        self.ball_x = self.paddle_x * w
        self.ball_y = dp(78) + self.paddle_h + self.ball_r + dp(4)
        self.ball_attached = False

        ang = random.uniform(-0.35, 0.35)
        spd = dp(350)
        self.ball_vx = spd * math.sin(ang)
        self.ball_vy = spd * math.cos(ang)

        ArcadeAudio.play("pop", self.app.sound_enabled)
        self.stop_loop()
        self._loop_event = Clock.schedule_interval(self._tick, 1.0 / 60.0)

    def _launch_ball(self, *_):
        if not self.is_running or not self.ball_attached:
            return
        self.ball_attached = False
        ang = random.uniform(-0.35, 0.35)
        spd = dp(350)
        self.ball_vx = spd * math.sin(ang)
        self.ball_vy = spd * math.cos(ang)
        ArcadeAudio.play("pop", self.app.sound_enabled)

    def stop_loop(self):
        if self._loop_event:
            self._loop_event.cancel()
            self._loop_event = None
        if self._relaunch_event:
            self._relaunch_event.cancel()
            self._relaunch_event = None

    def toggle_pause(self, *_):
        if not self.is_running:
            return
        self.is_paused = not self.is_paused
        self.pause_btn.text = "▶ RESUME" if self.is_paused else "⏸️ PAUSE"
        ArcadeAudio.play("click", self.app.sound_enabled)

    def stop_game_action(self, *_):
        """Action button to stop the running game and bring up the run summary & replay buttons."""
        if not self.is_running and self.ready_panel.opacity > 0:
            self.exit_game()
            return
        self._trigger_game_over(stopped=True)

    def exit_game(self, *_):
        self.stop_loop()
        self.is_running = False
        if self.on_exit:
            self.on_exit()

    def _tick(self, dt):
        if not self.is_running or self.is_paused:
            return

        w = max(self.width, dp(400))
        h = max(self.height, dp(500))

        # 1. Update paddle position
        if "left" in self.keys_down:
            self.paddle_x = max(0.08, self.paddle_x - self.move_speed * dt)
            self.paddle_target_x = self.paddle_x
        elif "right" in self.keys_down:
            self.paddle_x = min(0.92, self.paddle_x + self.move_speed * dt)
            self.paddle_target_x = self.paddle_x
        else:
            diff = self.paddle_target_x - self.paddle_x
            if abs(diff) > 0.005:
                self.paddle_x += diff * min(1.0, 18.0 * dt)

        # 2. Update ball position & physics
        pad_cx = self.paddle_x * w
        pad_top = dp(78) + self.paddle_h

        if self.ball_attached:
            self.ball_x = pad_cx
            self.ball_y = pad_top + self.ball_r + dp(2)
        else:
            self.ball_x += self.ball_vx * dt
            self.ball_y += self.ball_vy * dt

            # Particle trail
            if random.random() < 0.45:
                self.particles.append({
                    "x": self.x + self.ball_x, "y": self.y + self.ball_y,
                    "vx": random.uniform(-dp(12), dp(12)),
                    "vy": random.uniform(-dp(12), dp(12)),
                    "life": 0.0, "max_life": 0.22,
                    "color": CYAN, "size": dp(2.8)
                })

            # Wall bounce: Left (dp(10))
            if self.ball_x - self.ball_r <= dp(10):
                self.ball_x = dp(10) + self.ball_r
                self.ball_vx = abs(self.ball_vx)
                ArcadeAudio.play("pop", self.app.sound_enabled)
            # Wall bounce: Right (w - dp(10))
            elif self.ball_x + self.ball_r >= w - dp(10):
                self.ball_x = w - dp(10) - self.ball_r
                self.ball_vx = -abs(self.ball_vx)
                ArcadeAudio.play("pop", self.app.sound_enabled)
            # Wall bounce: Top (h - dp(56))
            if self.ball_y + self.ball_r >= h - dp(56):
                self.ball_y = h - dp(56) - self.ball_r
                self.ball_vy = -abs(self.ball_vy)
                ArcadeAudio.play("pop", self.app.sound_enabled)

            # Paddle collision
            pw = self.paddle_w
            ph = self.paddle_h
            if (dp(78) <= self.ball_y - self.ball_r <= pad_top + dp(6)) and (abs(self.ball_x - pad_cx) <= pw / 2 + self.ball_r) and self.ball_vy < 0:
                self.ball_y = pad_top + self.ball_r
                offset = (self.ball_x - pad_cx) / (pw / 2)
                offset = max(-1.0, min(1.0, offset))
                spd = max(dp(340), math.hypot(self.ball_vx, self.ball_vy))
                bounce_ang = offset * 0.95
                self.ball_vx = spd * math.sin(bounce_ang)
                self.ball_vy = spd * math.cos(bounce_ang)
                ArcadeAudio.play("bonus", self.app.sound_enabled)

            # Brick collisions
            alive_count = 0
            for b in self.bricks:
                if not b["alive"]:
                    continue
                alive_count += 1
                bw = b["rel_w"] * w
                bh = dp(18)
                bx = b["rel_x"] * w
                by = h - dp(75) - b["r_idx"] * dp(24)

                # Overlap test with ball
                if (bx - self.ball_r <= self.ball_x <= bx + bw + self.ball_r and
                    by - self.ball_r <= self.ball_y <= by + bh + self.ball_r):
                    b["alive"] = False
                    alive_count -= 1
                    self.score += b["points"]
                    self.score_lbl.text = f"[b]SCORE: [ {self.score} ][/b]"
                    ArcadeAudio.play("pop", self.app.sound_enabled)

                    # Explosion particles
                    for _ in range(12):
                        ang = random.uniform(0, math.tau)
                        pspd = random.uniform(dp(40), dp(160))
                        self.particles.append({
                            "x": self.x + bx + bw / 2, "y": self.y + by + bh / 2,
                            "vx": math.cos(ang) * pspd,
                            "vy": math.sin(ang) * pspd,
                            "life": 0.0, "max_life": random.uniform(0.25, 0.45),
                            "color": b["color"], "size": dp(3.2)
                        })

                    # Reflect ball
                    prev_x = self.ball_x - self.ball_vx * dt
                    if prev_x + self.ball_r <= bx or prev_x - self.ball_r >= bx + bw:
                        self.ball_vx = -self.ball_vx
                    else:
                        self.ball_vy = -self.ball_vy

                    # Speed up ball slightly
                    spd = min(dp(520), math.hypot(self.ball_vx, self.ball_vy) * 1.015)
                    curr_ang = math.atan2(self.ball_vy, self.ball_vx)
                    self.ball_vx = spd * math.cos(curr_ang)
                    self.ball_vy = spd * math.sin(curr_ang)
                    break

            self.bricks_lbl.text = f"[b]BLOCKS: [ {alive_count} ][/b]"

            # Check Victory
            if alive_count == 0 and len(self.bricks) > 0:
                self._trigger_victory()
                return

            # Bottom boundary (lost life)
            if self.ball_y < dp(45):
                self.lives -= 1
                self.lives_lbl.text = f"[b]LIVES: [ {'❤️' * self.lives}{'🖤' * (3 - self.lives)} ][/b]"
                ArcadeAudio.play("crash", self.app.sound_enabled)

                if self.lives > 0:
                    self.ball_attached = True
                    self.ball_x = pad_cx
                    self.ball_y = pad_top + self.ball_r + dp(2)
                    if self._relaunch_event:
                        self._relaunch_event.cancel()
                    self._relaunch_event = Clock.schedule_once(lambda _dt: self._launch_ball(), 0.8)
                else:
                    self._trigger_game_over(stopped=False)
                    return

        # 3. Update particles
        surviving_p = []
        for p in self.particles:
            p["life"] += dt
            if p["life"] < p["max_life"]:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                surviving_p.append(p)
        self.particles = surviving_p

        self._redraw()

    def _trigger_victory(self):
        self.is_running = False
        self.stop_loop()
        self.score += 500
        ArcadeAudio.play("level_up", self.app.sound_enabled)

        is_new_best = self.score > self.high_score
        if is_new_best:
            self.high_score = self.score
            self.app.arcade_scores["cyber_breaker"] = self.score
            self.app.save_data()

        self.go_title.text = "[b]🎉 SECTOR CLEARED![/b]\n[size=12sp]FIREWALL BREACHED (+500 BONUS!)[/size]"
        self.go_title.color = MINT
        self.go_stats.text = f"FINAL SCORE: [ {self.score} PTS ]\nBEST RECORD: [ {self.high_score} PTS ]"
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self.retry_btn.text = "🔄 NEXT SECTOR [PLAY AGAIN]"
        self.game_over_panel.opacity = 1
        self.game_over_panel.disabled = False
        self._redraw()

    def _trigger_game_over(self, stopped=False):
        self.is_running = False
        self.stop_loop()

        if stopped:
            ArcadeAudio.play("click", self.app.sound_enabled)
        else:
            ArcadeAudio.play("crash", self.app.sound_enabled)

        is_new_best = self.score > self.high_score
        if is_new_best:
            self.high_score = self.score
            self.app.arcade_scores["cyber_breaker"] = self.score
            self.app.save_data()

        if stopped:
            self.go_title.text = "[b]🛑 SPRINT TERMINATED[/b]\n[size=12sp]MISSION REPORT READY[/size]"
            self.go_title.color = CYAN
        elif is_new_best:
            self.go_title.text = "[b]🏆 NEW HIGH SCORE![/b]\n[size=12sp]CYBER BREAKER RECORD[/size]"
            self.go_title.color = YELLOW
        else:
            self.go_title.text = "[b]💀 BREACH FAILED[/b]\n[size=12sp]ENERGY PLASMA DEPLETED[/size]"
            self.go_title.color = RED

        shattered = sum(1 for b in self.bricks if not b["alive"])
        self.go_stats.text = f"FINAL SCORE: [ {self.score} PTS ]\nBLOCKS SMASHED: [ {shattered} ]\nRECORD: [ {self.high_score} PTS ]"
        self.high_lbl.text = f"[b]BEST: {self.high_score}[/b]"
        self.retry_btn.text = "🔄 REPLAY GAME [SPACE]"
        self.game_over_panel.opacity = 1
        self.game_over_panel.disabled = False
        self._redraw()

    def _redraw(self, *_):
        self.game_canvas.canvas.clear()
        bx, by = self.pos
        w = max(self.width, dp(400))
        h = max(self.height, dp(500))

        with self.game_canvas.canvas:
            Color(*BG)
            Rectangle(pos=(bx, by), size=(w, h))

            # Wall boundaries
            Color(1, 1, 1, 0.08)
            Line(points=[bx + dp(8), by + dp(70), bx + dp(8), by + h - dp(56)], width=dp(1.2))
            Line(points=[bx + w - dp(8), by + dp(70), bx + w - dp(8), by + h - dp(56)], width=dp(1.2))
            Line(points=[bx + dp(8), by + h - dp(56), bx + w - dp(8), by + h - dp(56)], width=dp(1.2))

            # Draw Bricks
            for b in self.bricks:
                if not b["alive"]:
                    continue
                brick_w = b["rel_w"] * w
                brick_h = dp(18)
                brick_x = bx + b["rel_x"] * w
                brick_y = by + h - dp(75) - b["r_idx"] * dp(24)

                c = b["color"]
                Color(*c)
                RoundedRectangle(pos=(brick_x, brick_y), size=(brick_w, brick_h), radius=[dp(3)])
                Color(1, 1, 1, 0.40)
                Line(rounded_rectangle=(brick_x, brick_y, brick_w, brick_h, dp(3)), width=dp(1.0))

            # Draw Particles
            for p in self.particles:
                alpha = max(0, 1.0 - (p["life"] / p["max_life"]))
                c = p["color"]
                Color(c[0], c[1], c[2], alpha)
                sz = p["size"] * alpha
                Rectangle(pos=(p["x"] - sz / 2, p["y"] - sz / 2), size=(sz, sz))

            # Draw Paddle
            paddle_cx = bx + self.paddle_x * w
            paddle_y = by + dp(78)
            pw = self.paddle_w
            ph = self.paddle_h

            Color(CYAN[0], CYAN[1], CYAN[2], 0.25)
            Ellipse(pos=(paddle_cx - pw * 0.75, paddle_y - ph * 0.5), size=(pw * 1.5, ph * 2.5))

            Color(*CYAN)
            RoundedRectangle(pos=(paddle_cx - pw / 2, paddle_y), size=(pw, ph), radius=[dp(4)])
            Color(*MAGENTA_CORE)
            Line(rounded_rectangle=(paddle_cx - pw / 2, paddle_y, pw, ph, dp(4)), width=dp(1.5))

            # Draw Ball
            ball_screen_x = bx + self.ball_x
            ball_screen_y = by + self.ball_y

            Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.35)
            Ellipse(pos=(ball_screen_x - self.ball_r * 2, ball_screen_y - self.ball_r * 2), size=(self.ball_r * 4, self.ball_r * 4))

            Color(*WHITE)
            Ellipse(pos=(ball_screen_x - self.ball_r, ball_screen_y - self.ball_r), size=(self.ball_r * 2, self.ball_r * 2))
            Color(*CYAN)
            Line(circle=(ball_screen_x, ball_screen_y, self.ball_r), width=dp(1.5))


# ---------------------------------------------------------------------------
# BONUS: CALM MODE (Guided 4-4-4-4 Box Breathing Chamber)
# ---------------------------------------------------------------------------

class CalmBreathingChamber(FloatLayout):
    """
    Relaxing activity for decompression:
    - Guided 4-4-4-4 Box breathing: Inhale (4s) -> Hold (4s) -> Exhale (4s) -> Hold (4s)
    - Dedicated Canvas widget: UI elements (HUD, timer, chimes, affirmations) are never wiped.
    - Animated pulsing neon concentric rings with glowing quantum particle aura.
    - Gentle witty cyberpunk affirmations cycling peacefully.
    - Mindful timer tracking relaxation duration with FINISH SESSION button.
    """

    CALM_QUOTES = [
        "Breathe. The side quests can wait.",
        "Your value is not measured by your task count.",
        "Inhale oxygen. Exhale cortisol.",
        "Defragging neural cache... releasing tension.",
        "No deadlines live here. Just calm vibes.",
        "One breath at a time, Operator.",
        "System nominal. You are doing great.",
    ]

    def __init__(self, app, on_exit=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.on_exit = on_exit

        self.session_seconds = 0
        self.phase_time = 0.0
        self.phase_index = 0  # 0: Inhale, 1: Hold, 2: Exhale, 3: Hold
        self.phases = [
            ("INHALE", (0.0, 0.88, 1.0, 1.0), 4.0),
            ("HOLD", (1.0, 0.85, 0.30, 1.0), 4.0),
            ("EXHALE", (1.0, 0.24, 0.95, 1.0), 4.0),
            ("REST", (0.24, 1.0, 0.69, 1.0), 4.0),
        ]
        self.chimes_enabled = True

        self.particles = []
        for _ in range(25):
            self.particles.append({
                "ang": random.uniform(0, math.tau),
                "dist": random.uniform(dp(40), dp(160)),
                "speed": random.uniform(dp(15), dp(45)),
                "size": random.uniform(dp(2), dp(4)),
                "alpha": random.uniform(0.3, 0.8),
                "color": random.choice([CYAN, MAGENTA, MINT, YELLOW])
            })

        self._tick_event = None

        # Dedicated background canvas widget
        self.bg_canvas = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.bg_canvas)

        self._build_ui()
        self.bind(pos=self._redraw, size=self._redraw)

    def _build_ui(self):
        # Top HUD Bar
        hud = ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(58), pos_hint={"x": 0, "top": 1},
            bg_color=BG_SECONDARY, border_color=MINT
        )
        back_btn = ArcadeButton(
            text="🔙 ARCADE HUB", variant="secondary", height_dp=38,
            size_hint_x=None, width=dp(135), on_click=self.exit_chamber
        )
        self.timer_lbl = Label(
            text="[b]MINDFUL TIME: 00:00[/b]", font_name=TECH_FONT, font_size="16sp",
            color=MINT, bold=True, markup=True, halign="left"
        )
        self.chime_btn = ArcadeButton(
            text="🔔 CHIMES: ON", variant="mint", height_dp=38,
            size_hint_x=None, width=dp(130), on_click=self.toggle_chimes
        )
        self.finish_btn = ArcadeButton(
            text="🛑 FINISH SESSION", variant="danger", height_dp=38,
            size_hint_x=None, width=dp(145), on_click=self.exit_chamber
        )

        hud.add_widget(back_btn)
        hud.add_widget(self.timer_lbl)
        hud.add_widget(self.chime_btn)
        hud.add_widget(self.finish_btn)
        self.add_widget(hud)

        # Center Breathing Guide
        center_box = BoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint=(None, None), size=(dp(340), dp(260)),
            pos_hint={"center_x": 0.5, "center_y": 0.50}
        )
        self.phase_lbl = Label(
            text="[b]INHALE[/b]", font_name=TECH_FONT, font_size="34sp",
            color=CYAN, markup=True, halign="center"
        )
        self.sec_lbl = Label(
            text="4", font_name=TECH_FONT, font_size="46sp",
            color=WHITE, bold=True, halign="center"
        )
        center_box.add_widget(self.phase_lbl)
        center_box.add_widget(self.sec_lbl)
        self.add_widget(center_box)

        # Bottom Peaceful Affirmation Box
        self.aff_panel = ArcadePanel(
            orientation="horizontal", padding=[dp(16), dp(8)],
            size_hint=(0.88, None), height=dp(48), pos_hint={"center_x": 0.5, "y": 0.06},
            bg_color=BG_ELEVATED, border_color=SEPARATOR
        )
        self.aff_lbl = Label(
            text=self.CALM_QUOTES[0], font_name=TECH_FONT, font_size="13.5sp",
            color=TEXT_SEC, markup=True, halign="center"
        )
        self.aff_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.aff_panel.add_widget(self.aff_lbl)
        self.add_widget(self.aff_panel)

    def on_enter(self):
        self.session_seconds = 0
        self.phase_time = 0.0
        self.phase_index = 0
        self.stop_tick()
        self._tick_event = Clock.schedule_interval(self._tick, 1.0 / 30.0)
        self._redraw()

    def on_leave(self):
        self.stop_tick()

    def stop_tick(self):
        if self._tick_event:
            self._tick_event.cancel()
            self._tick_event = None

    def exit_chamber(self, *_):
        self.stop_tick()
        if self.on_exit:
            self.on_exit()

    def toggle_chimes(self, *_):
        self.chimes_enabled = not self.chimes_enabled
        self.chime_btn.text = "🔔 CHIMES: ON" if self.chimes_enabled else "🔕 CHIMES: OFF"
        ArcadeAudio.play("click", self.app.sound_enabled)

    def _tick(self, dt):
        self.session_seconds += dt
        mins = int(self.session_seconds // 60)
        secs = int(self.session_seconds % 60)
        self.timer_lbl.text = f"[b]MINDFUL TIME: {mins:02d}:{secs:02d}[/b]"

        # Affirmation cycling
        if int(self.session_seconds) % 12 == 0 and int(self.session_seconds) > 0:
            quote_idx = (int(self.session_seconds) // 12) % len(self.CALM_QUOTES)
            self.aff_lbl.text = self.CALM_QUOTES[quote_idx]

        # Phase logic
        self.phase_time += dt
        cur_phase_name, cur_col, cur_dur = self.phases[self.phase_index]
        remaining = max(1, math.ceil(cur_dur - self.phase_time))
        self.sec_lbl.text = str(remaining)

        if self.phase_time >= cur_dur:
            self.phase_time = 0.0
            self.phase_index = (self.phase_index + 1) % len(self.phases)
            new_name, new_col, _ = self.phases[self.phase_index]
            self.phase_lbl.text = f"[b]{new_name}[/b]"
            self.phase_lbl.color = new_col

            if self.chimes_enabled:
                ArcadeAudio.play("calm_chime", self.app.sound_enabled)

        # Update floating particles
        for p in self.particles:
            p["dist"] += p["speed"] * dt
            if p["dist"] > dp(180):
                p["dist"] = dp(40)
                p["ang"] = random.uniform(0, math.tau)

        self._redraw()

    def _redraw(self, *_):
        self.bg_canvas.canvas.clear()
        bx, by = self.pos
        w = max(self.width, 1)
        h = max(self.height, 1)
        cx = bx + w / 2
        cy = by + h * 0.50

        min_r = dp(55)
        max_r = dp(135)
        _, cur_col, dur = self.phases[self.phase_index]
        prog = min(1.0, self.phase_time / dur)

        if self.phase_index == 0:    # Inhale
            rad = min_r + (max_r - min_r) * math.sin(prog * (math.pi / 2))
        elif self.phase_index == 1:  # Hold
            rad = max_r + math.sin(prog * math.tau) * dp(3)
        elif self.phase_index == 2:  # Exhale
            rad = max_r - (max_r - min_r) * math.sin(prog * (math.pi / 2))
        else:                        # Rest
            rad = min_r + math.sin(prog * math.tau) * dp(2)

        with self.bg_canvas.canvas:
            Color(*BG)
            Rectangle(pos=(bx, by), size=(w, h))

            # Floating quantum dust
            for p in self.particles:
                px = cx + math.cos(p["ang"]) * p["dist"]
                py = cy + math.sin(p["ang"]) * p["dist"]
                c = p["color"]
                Color(c[0], c[1], c[2], p["alpha"])
                Rectangle(pos=(px, py), size=(p["size"], p["size"]))

            # Ambient breathing aura
            Color(cur_col[0], cur_col[1], cur_col[2], 0.12)
            Ellipse(pos=(cx - rad * 1.25, cy - rad * 1.25), size=(rad * 2.5, rad * 2.5))

            # Main breathing ring
            Color(cur_col[0], cur_col[1], cur_col[2], 0.25)
            Ellipse(pos=(cx - rad, cy - rad), size=(rad * 2, rad * 2))

            Color(*cur_col)
            Line(circle=(cx, cy, rad), width=dp(2.2))

            # Inner concentric guide ring
            Color(cur_col[0], cur_col[1], cur_col[2], 0.45)
            Line(circle=(cx, cy, rad * 0.75), width=dp(1.0))


# ---------------------------------------------------------------------------
# MAIN ARCADE HUB (Selection Lobby & Screen Router)
# ---------------------------------------------------------------------------

class MindResetArcade(Screen):
    """
    Main Mind Reset Arcade Screen:
    - Hosts the Arcade Lobby Hub, Neon Dodge, Pixel Pop, Cyber Breaker, and Calm Mode.
    - Preserves application state and cleans up resources seamlessly on exit.
    """

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_view = "lobby"

        # Background Starfield
        self.starfield = ArcadeStarfield(count=45, size_hint=(1, 1))
        self.add_widget(self.starfield)

        # Container for swappable views
        self.content_holder = FloatLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.content_holder)

        # Build Sub-Views
        self.lobby_view = self._build_lobby_view()
        self.neon_dodge = NeonDodgeGame(app=self.app, on_exit=self.show_lobby)
        self.pixel_pop = PixelPopGame(app=self.app, on_exit=self.show_lobby)
        self.cyber_breaker = CyberBreakerGame(app=self.app, on_exit=self.show_lobby)
        self.calm_chamber = CalmBreathingChamber(app=self.app, on_exit=self.show_lobby)

        # Display lobby initially
        self.content_holder.add_widget(self.lobby_view)

    def _build_lobby_view(self):
        """Constructs the arcade hub menu with game cabinets."""
        root = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12), dp(8)], size_hint=(1, 1))

        # 1. Header Bar
        header = ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(58), bg_color=BG_SECONDARY, border_color=MAGENTA
        )
        back_btn = ArcadeButton(
            text="🔙 BACK TO BASE", variant="secondary", height_dp=38,
            size_hint_x=None, width=dp(155), on_click=self.go_back_to_base
        )
        title_box = BoxLayout(orientation="vertical", spacing=dp(1))
        title_lbl = Label(
            text="[b]🕹️ MIND RESET ARCADE[/b] // NEURAL RECHARGE ZONE",
            font_name=TECH_FONT, font_size="16sp", color=MAGENTA_CORE, markup=True, halign="left"
        )
        sub_lbl = Label(
            text="TOUCH GRASS. DIGITALLY. TAKE A SHORT CASUAL BREAK TO RESET YOUR FOCUS.",
            font_name=TECH_FONT, font_size="12sp", color=TEXT_SEC, halign="left"
        )
        title_box.add_widget(title_lbl)
        title_box.add_widget(sub_lbl)

        sound_text = "🔊 SFX: ON" if self.app.sound_enabled else "🔇 SFX: OFF"
        self.sound_toggle_btn = ArcadeButton(
            text=sound_text, variant="primary", height_dp=38,
            size_hint_x=None, width=dp(125), on_click=self.toggle_app_sound
        )

        header.add_widget(back_btn)
        header.add_widget(title_box)
        header.add_widget(self.sound_toggle_btn)
        root.add_widget(header)

        # 2. Cycling Ticker Banner
        self.ticker = ArcadeTicker()
        root.add_widget(self.ticker)

        # 3. Scrollable Arcade Cabinets
        scroll = ScrollView(
            size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
            bar_width=dp(6), bar_color=CYAN
        )
        cabinet_grid = GridLayout(cols=2, spacing=dp(10), size_hint=(1, None), padding=[dp(4), dp(4)])
        cabinet_grid.bind(minimum_height=cabinet_grid.setter("height"))

        # Cabinet 1: NEON DODGE
        self.card_dodge = self._create_cabinet_card(
            title="🚀 NEON DODGE",
            badge="[REFLEX EVASION]",
            badge_col=CYAN,
            desc="Maneuver your high-velocity craft through falling firewall pulses and glitch debris. Quick casual reflex challenge.",
            controls="Controls: [A/D] or [Arrows] or Touch Screen",
            score_key="neon_dodge",
            score_suffix="PTS",
            btn_text="▶ INSERT COIN // PLAY",
            btn_variant="secondary",
            on_play=lambda: self.switch_view("neon_dodge")
        )
        cabinet_grid.add_widget(self.card_dodge)

        # Cabinet 2: PIXEL POP
        self.card_pop = self._create_cabinet_card(
            title="🎯 PIXEL POP",
            badge="[30s REFLEX BLITZ]",
            badge_col=MAGENTA,
            desc="Burst floating rogue data nodes before they dissolve. Chain rapid combos and grab golden cores for extra time.",
            controls="Controls: Click or Tap Floating Targets",
            score_key="pixel_pop",
            score_suffix="PTS",
            btn_text="▶ INSERT COIN // PLAY",
            btn_variant="primary",
            on_play=lambda: self.switch_view("pixel_pop")
        )
        cabinet_grid.add_widget(self.card_pop)

        # Cabinet 3: CYBER BREAKER (Replaces Memory Glitch)
        self.card_breaker = self._create_cabinet_card(
            title="🧱 CYBER BREAKER",
            badge="[FIREWALL SMASH]",
            badge_col=YELLOW,
            desc="Command the quantum paddle. Shatter encrypted firewall blocks and breach the security matrix with laser ball physics.",
            controls="Controls: [A/D] or [Arrows] or Touch / Drag",
            score_key="cyber_breaker",
            score_suffix="PTS",
            btn_text="▶ INSERT COIN // PLAY",
            btn_variant="gold",
            on_play=lambda: self.switch_view("cyber_breaker")
        )
        cabinet_grid.add_widget(self.card_breaker)

        # Cabinet 4: CALM MODE
        self.card_calm = self._create_cabinet_card(
            title="🧘 ZEN BREATHING",
            badge="[DECOMPRESSION]",
            badge_col=MINT,
            desc="Zero competitive pressure. Guided 4-4-4-4 box breathing with luminous quantum particles and relaxing vibes.",
            controls="Controls: Follow the expanding ring",
            score_key=None,
            score_suffix="",
            btn_text="🌿 ENTER CALM CHAMBER",
            btn_variant="mint",
            on_play=lambda: self.switch_view("calm_mode")
        )
        cabinet_grid.add_widget(self.card_calm)

        scroll.add_widget(cabinet_grid)
        root.add_widget(scroll)

        return root

    def _create_cabinet_card(self, title, badge, badge_col, desc, controls,
                             score_key, score_suffix, btn_text, btn_variant, on_play):
        card = ArcadePanel(
            orientation="vertical", padding=[dp(14), dp(12)], spacing=dp(8),
            size_hint=(1, None), height=dp(195), bg_color=BG_ELEVATED, border_color=badge_col
        )
        # Header Row
        head_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        t_lbl = Label(
            text=f"[b]{title}[/b]", font_name=TECH_FONT, font_size="16sp",
            color=WHITE, markup=True, halign="left"
        )
        b_lbl = Label(
            text=badge, font_name=TECH_FONT, font_size="12sp",
            color=badge_col, markup=True, halign="right"
        )
        head_row.add_widget(t_lbl)
        head_row.add_widget(b_lbl)
        card.add_widget(head_row)

        # Description
        d_lbl = Label(
            text=desc, font_name=TECH_FONT, font_size="12.5sp",
            color=TEXT_SEC, halign="left", valign="top"
        )
        d_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        card.add_widget(d_lbl)

        # Telemetry & Play Button Row
        bot_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(42))

        if score_key:
            score_val = self.app.arcade_scores.get(score_key, 0)
            score_txt = f"🏆 BEST: {score_val} {score_suffix}"
        else:
            score_txt = "🕊️ ZERO DEADLINES"

        s_lbl = Label(
            text=score_txt, font_name=TECH_FONT, font_size="13sp",
            color=YELLOW if score_key else MINT, markup=True, halign="left"
        )
        card.score_label = s_lbl
        card.score_key = score_key
        card.score_suffix = score_suffix

        play_btn = ArcadeButton(
            text=btn_text, variant=btn_variant, height_dp=40, font_size="13.5sp",
            size_hint_x=None, width=dp(190), on_click=on_play
        )
        bot_row.add_widget(s_lbl)
        bot_row.add_widget(play_btn)
        card.add_widget(bot_row)

        return card

    def switch_view(self, view_name):
        ArcadeAudio.play("click", self.app.sound_enabled)
        self.content_holder.clear_widgets()

        # Clean up current view
        if self.current_view == "neon_dodge":
            self.neon_dodge.on_leave()
        elif self.current_view == "pixel_pop":
            self.pixel_pop.on_leave()
        elif self.current_view == "cyber_breaker":
            self.cyber_breaker.on_leave()
        elif self.current_view == "calm_mode":
            self.calm_chamber.on_leave()

        self.current_view = view_name

        if view_name == "neon_dodge":
            self.content_holder.add_widget(self.neon_dodge)
            self.neon_dodge.on_enter()
        elif view_name == "pixel_pop":
            self.content_holder.add_widget(self.pixel_pop)
            self.pixel_pop.on_enter()
        elif view_name == "cyber_breaker":
            self.content_holder.add_widget(self.cyber_breaker)
            self.cyber_breaker.on_enter()
        elif view_name == "calm_mode":
            self.content_holder.add_widget(self.calm_chamber)
            self.calm_chamber.on_enter()
        else:
            self.show_lobby()

    def show_lobby(self):
        ArcadeAudio.play("click", self.app.sound_enabled)
        # Clean up game loops
        self.neon_dodge.on_leave()
        self.pixel_pop.on_leave()
        self.cyber_breaker.on_leave()
        self.calm_chamber.on_leave()

        self.current_view = "lobby"
        self.content_holder.clear_widgets()
        self.refresh_lobby_scores()
        self.content_holder.add_widget(self.lobby_view)

    def refresh_lobby_scores(self):
        for card in (self.card_dodge, self.card_pop, self.card_breaker):
            if hasattr(card, "score_label") and card.score_key:
                val = self.app.arcade_scores.get(card.score_key, 0)
                card.score_label.text = f"🏆 BEST: {val} {card.score_suffix}"

    def toggle_app_sound(self):
        self.app.toggle_sound()
        self.sound_toggle_btn.text = "🔊 SFX: ON" if self.app.sound_enabled else "🔇 SFX: OFF"

    def go_back_to_base(self):
        ArcadeAudio.play("click", self.app.sound_enabled)
        self.on_leave()
        self.app.go_page("home")

    def on_enter(self):
        self.starfield.start()
        self.ticker.start()
        self.refresh_lobby_scores()
        self.sound_toggle_btn.text = "🔊 SFX: ON" if self.app.sound_enabled else "🔇 SFX: OFF"

    def on_leave(self):
        self.starfield.stop()
        self.ticker.stop()
        if self.current_view == "neon_dodge":
            self.neon_dodge.on_leave()
        elif self.current_view == "pixel_pop":
            self.pixel_pop.on_leave()
        elif self.current_view == "cyber_breaker":
            self.cyber_breaker.on_leave()
        elif self.current_view == "calm_mode":
            self.calm_chamber.on_leave()


def create_arcade_screen(app):
    """Factory method to construct the Mind Reset Arcade screen."""
    return MindResetArcade(app=app, name="arcade")
