import json
import os
import re
import sys
import time
import random
import math
import threading
from collections import Counter
from datetime import date, datetime, timedelta

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.graphics import (Color, Ellipse, Line, Mesh, PopMatrix, PushMatrix,
                           Rectangle, Rotate, RoundedRectangle, Translate)
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import escape_markup
import proof_verifier
import companion


# ------------------------------------------------------------
# procrastiNOT.exe - cyberpunk arcade student productivity app
# Built with Python + Kivy. Data is saved locally as JSON.
# AI sidekick uses the Anthropic API (key goes in Settings).
# Without a key it falls back to a built-in offline helper.
# ------------------------------------------------------------

APP_TITLE = "procrastiNOT.exe"

AI_MODEL = "claude-haiku-5-5"          # change here if you want a different model
AI_URL = "https://api.anthropic.com/v1/messages"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
GROQ_BASE = "https://api.groq.com/openai/v1"
PROVIDER_CHOICES = {"Google Gemini (free)": "gemini", "Groq (free)": "groq", "Anthropic Claude": "anthropic"}
KEY_HELP = {
    "gemini": "Free key: aistudio.google.com/apikey (sign in with Google, press Create API key).",
    "groq": "Free key: console.groq.com/keys (sign up, create an API key).",
    "anthropic": "Paid key: console.anthropic.com (for Claude).",
}
# ---- BUILT-IN AI ----------------------------------------------------------
# Paste YOUR OWN free key here once and the AI helper works for everyone who
# runs your app, with nothing for them to set up.
#   Gemini (free): https://aistudio.google.com/apikey
#   Groq   (free): https://console.groq.com/keys
# Keep this file private: don't upload it to GitHub with the key inside.
import base64
BUILT_IN_GEMINI_KEY = base64.b64decode("QVEuQWI4Uk42S1dtWTh5ZlFRUzk1MDd6UG8tTUxMX0Q2T0wwZG96TS1tRl9zc0tDNzd3OVE=").decode("utf-8")
BUILT_IN_GROQ_KEY = ""


def _pick_font(path, fallback="Roboto"):
    return path if os.path.exists(path) else fallback


EMOJI_FONT = _pick_font("C:/Windows/Fonts/seguiemj.ttf")
TECH_FONT = _pick_font("C:/Windows/Fonts/consola.ttf")
JAPANESE_FONT = _pick_font("C:/Windows/Fonts/msgothic.ttc", fallback="Roboto")

# --- STRICT CYBERPUNK OS DESIGN TOKENS ---
BG = (0.024, 0.012, 0.039, 1.0)           # #06030A - Void Black
BG_SECONDARY = (0.039, 0.027, 0.067, 1.0) # #0A0711 - Near-black surface
BG_ELEVATED = (0.063, 0.039, 0.098, 1.0)  # #100A19 - Elevated surface
PANEL = (0.039, 0.027, 0.067, 0.94)       # #0A0711 with opacity
PANEL_ALT = (0.063, 0.039, 0.098, 0.96)   # #100A19
MAGENTA = (1.0, 0.239, 0.949, 1.0)        # #FF3DF2 - Hero callout & focus
MAGENTA_CORE = (1.0, 0.882, 0.984, 1.0)   # #FFE1FB - Hot neon core
VIOLET = (0.165, 0.039, 0.361, 1.0)       # #2A0A5C - Floor haze & ambient depth
MINT = (0.239, 1.0, 0.690, 1.0)           # #3DFFB0 - Status LED & telemetry
CYAN = MINT                               # Mint telemetry replaces generic cyan
PINK = MAGENTA                            # Magenta replaces old pink
PURPLE = VIOLET                           # Deep atmospheric violet
GREEN = MINT                              # Mint replaces old green
YELLOW = (1.0, 0.85, 0.30, 1.0)           # Soft gold
WHITE = (0.910, 0.875, 0.937, 1.0)        # #E8DFEF - Primary text
TEXT_SEC = (0.639, 0.604, 0.678, 1.0)     # #A39AAD - Secondary text
MUTED = (0.467, 0.439, 0.502, 1.0)        # #777080 - Muted system text
RED = (1.0, 0.20, 0.35, 1.0)              # Restrained crimson alert
SEPARATOR = (1.0, 1.0, 1.0, 0.09)         # rgba(255, 255, 255, 0.09)

NAV_IDLE = (0.039, 0.027, 0.067, 0.0)     # Understated, transparent dark
NAV_ACTIVE = (0.063, 0.039, 0.098, 0.92)  # Active elevation

MOODS = ["Focused", "Good", "Okay", "Stressed", "Tired", "Low"]
MOOD_ICONS = {"Focused": "focused", "Good": "good", "Okay": "okay", "Stressed": "stressed", "Tired": "tired", "Low": "low"}
PRIORITIES = ["Normal", "High", "Boss fight"]
PRIORITY_EMOJI = {"Normal": "🌱", "High": "⚡", "Boss fight": "🐉"}
LEVEL_TITLES = [
    "Cosmic Cadet", "Orbit Defender", "Moon Hopper",
    "Asteroid Hunter", "Starfleet Commander", "To The Moon Legend",
]
TIPS = [
    "🍅 Try 25 minutes of focus, then a 5 minute break. Repeat.",
    "🐸 Eat the frog: do the scariest quest first.",
    "📵 Phone in another room = free +50% brain.",
    "🧩 Stuck? Shrink the quest until it takes 2 minutes.",
    "💧 Water first. Productivity second.",
    "🎧 Pick one song. Work until it ends.",
    "🌙 Plan tomorrow tonight so morning-you has no excuses.",
    "🤖 Ask the AI sidekick to break any quest into tiny steps.",
]
CHIPS = [
    ("🪜 BREAK IT DOWN", "Break my focus quest into tiny steps and tell me what to do first."),
    ("⏱️ 25-MIN PLAN", "Give me a realistic 25 minute plan for my focus quest."),
    ("💡 EXPLAIN IT", "Explain what I need to know to finish my focus quest, simply."),
    ("🔥 PEP TALK", "Give me a short, funny pep talk. I'm procrastinating."),
]


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------

def today_key():
    return date.today().isoformat()


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def end_of_day(d):
    """Return the last second of the given date as a datetime."""
    return datetime.combine(d, datetime.max.time()).replace(microsecond=0)


def mission_due(m):
    """Exact due datetime of a mission (supports old saves with date only)."""
    due = m.get("due_at")
    if due:
        try:
            return datetime.fromisoformat(due)
        except (ValueError, TypeError):
            pass
    try:
        return end_of_day(date.fromisoformat(m.get("deadline", "")))
    except (ValueError, TypeError):
        return None


def is_overdue(m):
    due = mission_due(m)
    return bool(due and not m.get("done", False) and due < datetime.now())


def time_left_text(m):
    due = mission_due(m)
    if not due:
        return "♾️ No deadline"
    secs = int((due - datetime.now()).total_seconds())
    late = secs < 0
    secs = abs(secs)
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    if days:
        txt = f"{days}d {hours}h"
    elif hours:
        txt = f"{hours}h {mins}m"
    else:
        txt = f"{max(mins, 1)}m"
    return f"💀 overdue by {txt}" if late else f"⏳ {txt} left"


# Emoji/symbol characters get drawn with the emoji font, everything else with
# the monospace "terminal" font (Kivy cannot fall back between fonts by itself).
_EMOJI_RE = re.compile(
    "([\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u231A\u231B\u23E9-\u23FF\uFE0F\u200D]+)"
)


def tech_markup(text):
    try:
        safe = escape_markup(str(text))
        return _EMOJI_RE.sub(lambda m: "[font=%s]%s[/font]" % (EMOJI_FONT, m.group(1)), safe)
    except Exception:
        return str(text)


def _rewrap(widget, value):
    if widget._busy:
        return
    wrapped = tech_markup(value)
    if wrapped != value:
        widget._busy = True
        try:
            widget.text = wrapped
        finally:
            widget._busy = False


class TechLabel(Label):
    """Label that renders text in a mono font and emoji in the emoji font."""
    _busy = False

    def __init__(self, **kwargs):
        kwargs.setdefault("font_name", TECH_FONT)
        kwargs["markup"] = True
        super().__init__(**kwargs)
        self.bind(text=self._on_text)
        _rewrap(self, self.text)

    def _on_text(self, _inst, value):
        _rewrap(self, value)


# ------------------------------------------------------------
# custom widgets
# ------------------------------------------------------------

class NeonPanel(BoxLayout):
    """Refined cyberpunk OS surface with subtle separator border."""

    def __init__(self, bg_color=PANEL, border_color=None, radius=4, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self._radius = dp(radius)
        self._line = None
        self._br = []
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            # Subtle hairline separator (Rule C: eliminate repetitive bright outlines)
            if border_color:
                bc_a = min(0.35, border_color[3] if len(border_color) > 3 else 0.35)
                Color(border_color[0], border_color[1], border_color[2], bc_a)
            else:
                Color(*SEPARATOR)
            self._line = Line(rounded_rectangle=self._geom(), width=dp(1.0))
        self.bind(pos=self._update_rect, size=self._update_rect)
        self._update_rect()

    def _geom(self):
        w = max(self.width, 2)
        h = max(self.height, 2)
        r = max(1, min(self._radius, w / 2, h / 2))
        return (self.x, self.y, w, h, r)

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if self._line is not None:
            self._line.rounded_rectangle = self._geom()


class NeonBar(Widget):
    """Segmented neon progress bar. Set .value (0-1) or call animate_to()."""

    def __init__(self, fill_color=GREEN, **kwargs):
        super().__init__(**kwargs)
        self._value = 0.0
        self._target = 0.0
        self._anim_ev = None
        with self.canvas:
            Color(0.05, 0.08, 0.17, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            self._fill_color = Color(*fill_color)
            self._fill = Rectangle(pos=self.pos, size=(0, self.height))
            Color(1, 1, 1, 0.85)
            self._head = Rectangle(pos=self.pos, size=(0, 0))
            Color(0.02, 0.03, 0.07, 0.85)
            self._ticks = [Line(points=[0, 0, 0, 0], width=dp(1)) for _ in range(9)]
            self._ol_c = Color(fill_color[0], fill_color[1], fill_color[2], 0.55)
            self._outline = Line(rectangle=(self.x, self.y, max(self.width, 1), max(self.height, 1)),
                                 width=dp(0.9))
        self.bind(pos=self._redraw, size=self._redraw)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(0.0, min(1.0, float(v)))
        self._redraw()

    def animate_to(self, v):
        """Smoothly slide the bar to a new value."""
        self._target = max(0.0, min(1.0, float(v)))
        if self._anim_ev is None:
            self._anim_ev = Clock.schedule_interval(self._step, 1 / 60.0)

    def _step(self, dt):
        diff = self._target - self._value
        if abs(diff) < 0.004:
            self.value = self._target
            self._anim_ev = None
            return False
        self.value = self._value + diff * min(1.0, dt * 7)
        return True

    def set_color(self, rgba):
        self._fill_color.rgba = rgba
        self._ol_c.rgba = (rgba[0], rgba[1], rgba[2], 0.55)

    def _redraw(self, *_):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        fw = w * self._value
        self._fill.pos = (x, y)
        self._fill.size = (fw, h)
        if fw > dp(4):
            self._head.pos = (x + fw - dp(2), y)
            self._head.size = (dp(2), h)
        else:
            self._head.size = (0, 0)
        for i, tick in enumerate(self._ticks):
            tx = x + w * (i + 1) / 10.0
            tick.points = [tx, y, tx, y + h]
        self._outline.rectangle = (x, y, max(w, 1), max(h, 1))


class AccentBar(Widget):
    """Thin coloured stripe on the left side of a quest card."""

    def __init__(self, color, **kwargs):
        super().__init__(size_hint_x=None, width=dp(5), **kwargs)
        with self.canvas:
            Color(*color)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(2)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._r.pos = self.pos
        self._r.size = self.size


def compute_hud_polygon(x, y, w, h, style="style2", padding=0):
    """
    Computes responsive polygon perimeter points and vertices for HUD buttons:
    - style1: diagonal chamfer (top-left & bottom-right)
    - style2: hexagonal chamfer (all 4 corners cut)
    """
    eff_w = max(w + padding * 2, dp(8))
    eff_h = max(h + padding * 2, dp(6))
    px = x - padding
    py = y - padding

    if style == "style1":
        c = min(dp(12), eff_w * 0.16, eff_h * 0.35)
        c = max(dp(2.5), c)
        pts = [
            (px, py),
            (px + eff_w - c, py),
            (px + eff_w, py + c),
            (px + eff_w, py + eff_h),
            (px + c, py + eff_h),
            (px, py + eff_h - c),
        ]
    else:
        c = min(dp(8), eff_w * 0.12, eff_h * 0.25)
        c = max(dp(2.0), c)
        pts = [
            (px + c, py),
            (px + eff_w - c, py),
            (px + eff_w, py + c),
            (px + eff_w, py + eff_h - c),
            (px + eff_w - c, py + eff_h),
            (px + c, py + eff_h),
            (px, py + eff_h - c),
            (px, py + c),
        ]

    poly_points = []
    for pt in pts:
        poly_points.extend(pt)
    return poly_points, pts


class NeonButton(Button):
    """
    Cyberpunk Sci-Fi HUD button theme:
    - Style 1 (diagonal cut) or Style 2 (hexagonal / all-corners chamfer)
    - 4 corner dots in 2x2 grid (top right)
    - 2 indicator dots (left edge)
    - Glowing aura backdrop with smooth bloom on hover
    - Responsive chamfered geometry with OpenGL polygon mesh fill
    - Beveled inner accent line and crisp neon outline
    - Responsive sizing ("small", "default", "large")
    """
    _busy = False
    _hover = BooleanProperty(False)

    def __init__(self, bg_color=None, variant="primary", style="style2",
                 size="default", delay=0, enable_animations=True, **kwargs):
        kwargs.setdefault("font_name", TECH_FONT)
        kwargs["markup"] = True
        super().__init__(**kwargs)

        self.variant = variant
        self.hud_style = style
        self.hud_size = size
        self.delay = delay
        self.enable_animations = enable_animations

        # Responsive sizing defaults if dimensions not explicitly constrained
        if size == "small":
            self.font_size = "11sp"
            if self.size_hint_y is None and not kwargs.get("height"):
                self.height = dp(36)
            if self.size_hint_x is None and not kwargs.get("width"):
                self.width = dp(140)
        elif size == "large":
            self.font_size = "15sp"
            if self.size_hint_y is None and not kwargs.get("height"):
                self.height = dp(58)
            if self.size_hint_x is None and not kwargs.get("width"):
                self.width = dp(234)
        else:
            self.font_size = "13sp"
            if self.size_hint_y is None and not kwargs.get("height"):
                self.height = dp(46)
            if self.size_hint_x is None and not kwargs.get("width"):
                self.width = dp(182)

        # Base color resolution
        if bg_color is not None:
            self._base = tuple(bg_color)
            r, g, b = self._base[:3]
            if bg_color == NAV_ACTIVE:
                self.variant = "nav_active"
            elif bg_color == NAV_IDLE or (len(bg_color) >= 4 and bg_color[3] == 0.0):
                self.variant = "nav"
            elif max(abs(r - 0.07), abs(g - 0.12), abs(b - 0.25)) < 0.05 or (r < 0.15 and g < 0.18 and b < 0.28):
                self.variant = "secondary"
        elif variant == "secondary":
            self._base = (0.22, 0.26, 0.35, 1.0)
        elif variant in ("nav", "nav_active"):
            self._base = NAV_ACTIVE if variant == "nav_active" else NAV_IDLE
        else:
            self._base = (0.12, 0.65, 0.38, 1.0)  # Primary cyber green

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = WHITE
        self.bold = True

        # Build HUD Canvas elements
        with self.canvas.before:
            # 1. Diffuse glow aura bloom
            self._glow_c2 = Color(0, 0, 0, 0)
            self._glow_l2 = Line(points=[0, 0], close=True, width=dp(6.0))

            # 2. Focused glow aura
            self._glow_c = Color(0, 0, 0, 0)
            self._glow_l = Line(points=[0, 0], close=True, width=dp(3.5))

            # 3. Polygon mesh body fill
            self._bg_c = Color(0, 0, 0, 1)
            self._bg_mesh = Mesh(vertices=[0, 0, 0, 0], indices=[0], mode="triangles")

            # 4. Inner subtle highlight / bevel
            self._inner_c = Color(0, 0, 0, 0)
            self._inner_l = Line(points=[0, 0], close=True, width=dp(0.9))

            # 5. Primary outer border
            self._bd_c = Color(0, 0, 0, 1)
            self._bd_l = Line(points=[0, 0], close=True, width=dp(1.2))

            # 6. Top-right 4 corner dots (2x2 grid)
            self._dots_c = Color(0, 0, 0, 1)
            self._corner_dots = [Ellipse(pos=(0, 0), size=(dp(2.4), dp(2.4))) for _ in range(4)]

            # 7. Left 2 indicator dots
            self._side_dots = [Ellipse(pos=(0, 0), size=(dp(1.8), dp(1.8))) for _ in range(2)]

        self.bind(pos=self._sync, size=self._sync, state=self._on_state)
        self.bind(text=self._on_text)
        _rewrap(self, self.text)
        self._sync()
        self._refresh()
        Window.bind(mouse_pos=self._on_mouse)

    def _hud_poly(self, padding=0):
        return compute_hud_polygon(self.x, self.y, self.width, self.height, self.hud_style, padding)

    def _geom(self):
        w = max(self.width, 2)
        h = max(self.height, 2)
        return (self.x, self.y, w, h, max(1, min(dp(6), w / 2, h / 2)))

    def _sync(self, *_):
        is_nav_item = self.variant in ("nav", "nav_active")
        if is_nav_item:
            x, y, w, h = self.x, self.y, self.width, self.height
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            self._glow_l2.points = []
            self._glow_l.points = []
            if self.variant == "nav_active":
                # Clean mint left accent indicator line (Rule B & HUD layout)
                self._bd_l.points = [x + dp(1.5), y + dp(3), x + dp(1.5), y + h - dp(3)]
                self._bd_l.close = False
                self._bd_l.width = dp(2.2)
            else:
                self._bd_l.points = []
                self._bd_l.close = False
            self._inner_l.points = []
            for d in self._corner_dots:
                d.size = (0, 0)
            for d in self._side_dots:
                d.size = (0, 0)
        else:
            poly_points, pts = self._hud_poly(0)
            glow_points, _ = self._hud_poly(dp(2.5))
            glow_points2, _ = self._hud_poly(dp(4.5))
            inner_points, _ = self._hud_poly(-dp(1.2))

            self._glow_l2.points = glow_points2
            self._glow_l.points = glow_points
            self._bd_l.points = poly_points
            self._bd_l.close = True
            self._bd_l.width = dp(1.2)
            self._inner_l.points = inner_points

        # Update polygon mesh
        cx = self.x + self.width * 0.5
        cy = self.y + self.height * 0.5
        w = max(self.width, 1.0)
        h = max(self.height, 1.0)

        vertices = [cx, cy, 0.5, 0.5]
        for ptx, pty in pts:
            u = (ptx - self.x) / w
            v = (pty - self.y) / h
            vertices.extend([ptx, pty, u, v])

        indices = []
        n = len(pts)
        for i in range(1, n + 1):
            next_i = 1 if i == n else i + 1
            indices.extend([0, i, next_i])

        self._bg_mesh.vertices = vertices
        self._bg_mesh.indices = indices

        if not is_nav_item:
            # Top-right corner dots (2x2 matrix)
            if self.width < dp(45) or self.height < dp(20):
                for d in self._corner_dots:
                    d.size = (0, 0)
            else:
                dot_r = max(dp(0.9), min(dp(1.3), h * 0.035))
                d_spacing_x = max(dp(3.2), min(dp(4.8), w * 0.045))
                d_spacing_y = max(dp(3.2), min(dp(4.8), h * 0.14))
                margin_right = max(dp(6.5), min(dp(12.0), w * 0.08))
                margin_top = max(dp(4.2), min(dp(7.5), h * 0.18))

                r_x2 = self.right - margin_right
                r_x1 = r_x2 - d_spacing_x
                t_y1 = self.top - margin_top
                t_y2 = t_y1 - d_spacing_y

                c_coords = [
                    (r_x1 - dot_r, t_y1 - dot_r),
                    (r_x2 - dot_r, t_y1 - dot_r),
                    (r_x1 - dot_r, t_y2 - dot_r),
                    (r_x2 - dot_r, t_y2 - dot_r),
                ]
                dot_size = (dot_r * 2, dot_r * 2)
                for i, (cx_i, cy_i) in enumerate(c_coords):
                    self._corner_dots[i].pos = (cx_i, cy_i)
                    self._corner_dots[i].size = dot_size

            # Left indicator dots (2 vertical dots)
            if self.width < dp(40) or self.height < dp(20):
                for d in self._side_dots:
                    d.size = (0, 0)
            else:
                side_dot_r = max(dp(0.65), min(dp(1.0), h * 0.026))
                s_x = self.x + max(dp(2.5), min(dp(4.0), w * 0.025))
                s_mid_y = cy
                side_spacing = max(dp(3.8), min(dp(6.0), h * 0.14))
                s_coords = [
                    (s_x - side_dot_r, s_mid_y + side_spacing * 0.5 - side_dot_r),
                    (s_x - side_dot_r, s_mid_y - side_spacing * 0.5 - side_dot_r),
                ]
                side_size = (side_dot_r * 2, side_dot_r * 2)
                for i, (sx_i, sy_i) in enumerate(s_coords):
                    self._side_dots[i].pos = (sx_i, sy_i)
                    self._side_dots[i].size = side_size

    def _on_text(self, _inst, value):
        _rewrap(self, value)

    def _on_state(self, *_):
        self._refresh()

    def _on_mouse(self, _win, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._hover:
            self._hover = inside
            self._refresh()

    def _calc_hud_colors(self):
        r, g, b = self._base[:3]
        is_nav = (self.variant == "nav")
        is_nav_act = (self.variant == "nav_active")
        is_sec = (self.variant == "secondary")

        if is_nav:
            if self.state == "down":
                bg = (0.063, 0.039, 0.098, 0.85)
                bd = (0, 0, 0, 0)
                text_color = WHITE
            elif self._hover and not self.disabled:
                bg = (1.0, 1.0, 1.0, 0.05)
                bd = (0, 0, 0, 0)
                text_color = WHITE
            else:
                bg = (0, 0, 0, 0)
                bd = (0, 0, 0, 0)
                text_color = MUTED
            glow = (0, 0, 0, 0)
            dots = (0, 0, 0, 0)
            inner = (0, 0, 0, 0)
            return bg, bd, glow, dots, inner, text_color

        if is_nav_act:
            bg = (0.063, 0.039, 0.098, 0.95)
            bd = (MINT[0], MINT[1], MINT[2], 0.95)
            glow = (0, 0, 0, 0)
            dots = (0, 0, 0, 0)
            inner = (0, 0, 0, 0)
            text_color = WHITE
            return bg, bd, glow, dots, inner, text_color

        if self.state == "down":
            k_bright = 1.35
            glow_a = 0.35 if not is_sec else 0.15
        elif self._hover and not self.disabled:
            k_bright = 1.15
            glow_a = 0.28 if not is_sec else 0.10
        else:
            k_bright = 1.0
            glow_a = 0.08 if not is_sec else 0.04

        if is_sec:
            glow = (0.165, 0.039, 0.361, glow_a)
            bg = (0.039, 0.027, 0.067, 0.92)
            bd = (1.0, 1.0, 1.0, 0.09 if not self._hover else 0.22)
            inner = (0, 0, 0, 0)
            dots = (1.0, 1.0, 1.0, 0.40 if self._hover else 0.18)
            text_color = WHITE if self._hover else TEXT_SEC
        else:
            # Primary intentional accent (Rule B: Neon is rare and intentional)
            glow = (r, g, b, glow_a)
            bg = (0.063, 0.039, 0.098, 0.94)
            bd = (r * k_bright, g * k_bright, b * k_bright, 0.85)
            inner = (r * 0.4, g * 0.4, b * 0.4, 0.20)
            dots = (min(1.0, r * 1.2), min(1.0, g * 1.2), min(1.0, b * 1.2), 0.95)
            text_color = (1.0, 1.0, 1.0, 1.0) if self._hover else (min(1.0, r * 0.9 + 0.3), min(1.0, g * 0.9 + 0.3), min(1.0, b * 0.9 + 0.3), 1.0)
        return bg, bd, glow, dots, inner, text_color

    def _refresh(self):
        bg, bd, glow, dots, inner, text_color = self._calc_hud_colors()
        self._bg_c.rgba = bg
        self._bd_c.rgba = bd
        if hasattr(self, "_glow_c"):
            self._glow_c.rgba = glow
        if hasattr(self, "_glow_c2"):
            self._glow_c2.rgba = (glow[0], glow[1], glow[2], glow[3] * 0.35)
        if hasattr(self, "_dots_c"):
            self._dots_c.rgba = dots
        if hasattr(self, "_inner_c"):
            self._inner_c.rgba = inner
        self.color = text_color

    def set_bg(self, color):
        self._base = tuple(color)
        if color == NAV_ACTIVE or (len(color) >= 4 and abs(color[3] - NAV_ACTIVE[3]) < 0.1 and abs(color[0] - NAV_ACTIVE[0]) < 0.02 and color[3] > 0.5):
            self.variant = "nav_active"
        elif color == NAV_IDLE or (len(color) >= 4 and color[3] == 0.0):
            self.variant = "nav"
        self._sync()
        self._refresh()


class MoodOption(ButtonBehavior, BoxLayout):
    """Clickable mood tile with a PNG face icon (no emoji font dependency)."""
    def __init__(self, mood, icon_path, app, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2), padding=dp(4), **kwargs)
        self.mood = mood
        self.app = app
        self.size_hint_y = None
        self.height = dp(68)
        with self.canvas.before:
            self.tile_color = Color(*BG_ELEVATED)
            self.tile_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
            self.border_color = Color(*SEPARATOR)
            self.tile_border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(5)), width=dp(1.0))
        self.bind(pos=self._update_tile, size=self._update_tile)
        self.face = Image(source=icon_path, size_hint=(1, None), height=dp(38), fit_mode="contain")
        self.add_widget(self.face)
        self.name_label = Label(text=mood, color=TEXT_SEC, font_name=TECH_FONT, font_size="11sp",
                                bold=True, size_hint_y=None, height=dp(18))
        self.add_widget(self.name_label)
        self.update_selected()

    def _update_tile(self, *_):
        self.tile_rect.pos = self.pos
        self.tile_rect.size = self.size
        self.tile_border.rounded_rectangle = (self.x, self.y, max(self.width, 2), max(self.height, 2), dp(5))

    def on_release(self):
        self.app.selected_mood = self.mood
        self.app.update_mood_selection()
        self.app.play_sound("click")

    def update_selected(self):
        selected = getattr(self.app, "selected_mood", None) == self.mood
        self.tile_color.rgba = (0.24, 0.12, 0.38, 0.95) if selected else BG_ELEVATED
        self.border_color.rgba = CYAN if selected else SEPARATOR
        self.tile_border.width = dp(1.8) if selected else dp(1.0)
        self.name_label.color = MINT if selected else TEXT_SEC


def make_label(text="", size=14, color=WHITE, bold=False, auto_height=False, **kwargs):
    # Allow callers to override alignment without passing duplicate Label kwargs.
    halign = kwargs.pop("halign", "left")
    valign = kwargs.pop("valign", "middle")
    kwargs.setdefault("size_hint_y", None)
    kwargs.setdefault("height", dp(max(30, int(size * 2.0))))
    label = TechLabel(
        text=text,
        font_size=f"{size}sp",
        color=color,
        bold=bold,
        halign=halign,
        valign=valign,
        **kwargs,
    )
    # Constrain text to the label width so long messages wrap instead of
    # overlapping neighbouring widgets or being drawn outside the page.
    label.bind(size=lambda instance, _size: setattr(
        instance, "text_size", (max(0, instance.width - dp(8)), None)
    ))
    # Optionally grow the label to fit its wrapped text (no clipping, no gaps).
    if auto_height:
        label.bind(texture_size=lambda instance, ts: setattr(
            instance, "height", max(dp(30), ts[1] + dp(10))
        ))
    return label


def section(text, color=None):
    if color is None:
        color = MAGENTA
    lbl = make_label("▌ " + text, 12, color, True, size_hint_y=None, height=dp(26))
    with lbl.canvas.after:
        Color(1, 1, 1, 0.08)
        line = Line(points=[0, 0, 0, 0], width=dp(0.8))

    def _upd(*_):
        line.points = [lbl.x + dp(4), lbl.y + dp(2), lbl.right - dp(4), lbl.y + dp(2)]

    lbl.bind(pos=_upd, size=_upd)
    return lbl


def make_input(hint, **kwargs):
    return TextInput(
        hint_text=hint,
        multiline=False,
        size_hint_y=None,
        height=dp(42),
        padding=[dp(12), dp(11)],
        font_name=TECH_FONT,
        background_normal="",
        background_active="",
        background_color=BG_ELEVATED,
        foreground_color=WHITE,
        hint_text_color=MUTED,
        cursor_color=MINT,
        **kwargs,
    )


class GlitchTitle(FloatLayout):
    """Brand title that randomly glitches (RGB split)."""

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.ghost = make_label(text, 16, MINT, True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.ghost.opacity = 0
        self.main = make_label(text, 16, MAGENTA, True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.ghost)
        self.add_widget(self.main)
        Clock.schedule_interval(self._glitch, 2.4)

    def _glitch(self, _dt):
        if random.random() < 0.7:
            self.ghost.opacity = 0.85
            self.ghost.pos_hint = {"x": random.uniform(-0.05, 0.05), "y": random.uniform(-0.06, 0.06)}
            self.main.pos_hint = {"x": random.uniform(-0.02, 0.02), "y": 0}
            Clock.schedule_once(self._reset, 0.13)

    def _reset(self, _dt):
        self.ghost.opacity = 0
        self.ghost.pos_hint = {"x": 0, "y": 0}
        self.main.pos_hint = {"x": 0, "y": 0}


class CyberBackdrop(Widget):
    """
    Persistent Ambient Cyberpunk OS Layer:
    - Void black surface (#06030A)
    - Deep violet atmospheric floor haze (#2A0A5C) rising from bottom
    - Sparse falling Katakana code streams (ｱｲｳｴ...0123)
    - Thin vertical dotted threads
    - Dim drifting particles
    - Subtle scanline texture
    - Interactive pointer stirring
    - Completely persistent across all page transitions
    """
    N_COLS = 22
    N_DUST = 26

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._t = 0.0
        self._mouse_x = -1000.0
        self._mouse_y = -1000.0
        self._cols = []
        self._dust = []
        with self.canvas:
            Color(*BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            # Deep violet atmospheric floor haze (#2A0A5C)
            Color(VIOLET[0], VIOLET[1], VIOLET[2], 0.35)
            self._haze1 = Ellipse(pos=(0, 0), size=(10, 10))
            Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.04)
            self._haze2 = Ellipse(pos=(0, 0), size=(10, 10))

            # Thin vertical dotted threads
            Color(1.0, 1.0, 1.0, 0.035)
            self._strands = [Line(points=[0, 0, 0, 0], width=dp(0.9)) for _ in range(8)]

            # Falling Katakana character streams (heads and trails)
            self._trail_c = [Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.12) for _ in range(self.N_COLS)]
            self._trail_lines = [Line(points=[0, 0, 0, 0], width=dp(1.2)) for _ in range(self.N_COLS)]
            self._head_c = [Color(MINT[0], MINT[1], MINT[2], 0.45) for _ in range(self.N_COLS)]
            self._head_rects = [Rectangle(pos=(-100, -100), size=(dp(2.2), dp(2.2))) for _ in range(self.N_COLS)]

            # Dim drifting dust
            Color(1.0, 1.0, 1.0, 0.22)
            self._dust_rects = [Rectangle(pos=(0, 0), size=(dp(1.3), dp(1.3))) for _ in range(self.N_DUST)]

            # Subtle scanline bar
            Color(1.0, 1.0, 1.0, 0.012)
            self._scan = Rectangle(pos=(0, 0), size=(0, 0))

        self.bind(pos=self._layout, size=self._layout)
        Window.bind(mouse_pos=self._on_mouse)
        Clock.schedule_interval(self._tick, 1 / 30.0)

    def _on_mouse(self, _win, pos):
        self._mouse_x, self._mouse_y = pos

    def _layout(self, *_):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        # Violet floor haze rising from bottom edge (Rule B & Reference B/C)
        self._haze1.pos = (x - w * 0.1, y - h * 0.5)
        self._haze1.size = (w * 1.2, h * 0.85)
        self._haze2.pos = (x + w * 0.15, y - h * 0.4)
        self._haze2.size = (w * 0.7, h * 0.6)

        # Thin vertical strands
        for i, strand in enumerate(self._strands):
            sx = x + w * ((i + 1) / 9.0) + (random.uniform(-1, 1) * dp(10))
            strand.points = [sx, y, sx, y + h]

        # Rain columns (sparse distribution per Rule A & B)
        self._cols = []
        for i in range(self.N_COLS):
            cx = x + random.uniform(dp(12), w - dp(12))
            head_y = random.uniform(y, y + h * 1.3)
            spd = random.uniform(dp(45), dp(130))
            length = random.uniform(dp(40), dp(160))
            is_mint = (i % 3 == 0)
            self._cols.append([cx, head_y, spd, length, is_mint])
            if is_mint:
                self._trail_c[i].rgba = (MINT[0], MINT[1], MINT[2], 0.14)
                self._head_c[i].rgba = (MINT[0], MINT[1], MINT[2], 0.65)
            else:
                self._trail_c[i].rgba = (MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.12)
                self._head_c[i].rgba = (MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], 0.60)

        # Dim dust
        self._dust = [[random.uniform(x, x + w), random.uniform(y, y + h), random.uniform(dp(4), dp(18))]
                      for _ in range(self.N_DUST)]

    def _tick(self, dt):
        self._t += dt
        x, y, w, h = self.x, self.y, self.width, self.height
        if w < 10 or h < 10:
            return

        # Animate falling columns with subtle pointer influence
        mx, my = self._mouse_x, self._mouse_y
        for i, col in enumerate(self._cols):
            cx, head_y, spd, length, is_mint = col
            # Subtle pointer influence: near pointer accelerates slightly
            dist_x = abs(cx - mx)
            near = max(0.0, 1.0 - dist_x / dp(90)) if (0 <= my <= h) else 0.0
            eff_spd = spd * (1.0 + near * 1.5)
            head_y -= eff_spd * dt
            if head_y < y - length:
                head_y = y + h + random.uniform(dp(10), dp(120))
                cx = x + random.uniform(dp(12), w - dp(12))
            col[0] = cx
            col[1] = head_y

            top_y = min(y + h, head_y + length)
            draw_head = max(y, head_y)
            self._trail_lines[i].points = [cx, top_y, cx, draw_head]
            self._head_rects[i].pos = (cx - dp(1.1), draw_head - dp(1.1))

        # Animate dust
        for dust, rect in zip(self._dust, self._dust_rects):
            dust[1] -= dust[2] * dt
            if dust[1] < y:
                dust[1] = y + h
                dust[0] = random.uniform(x, x + w)
            rect.pos = (dust[0], dust[1])

        # Scanline
        sy = y + h - ((self._t * 0.08) % 1.0) * h
        self._scan.pos = (x, sy - dp(14))
        self._scan.size = (w, dp(28))


def nkp_hash(n):
    s = math.sin(n * 127.1 + 311.7) * 43758.5453
    return s - math.floor(s)

def nkp_decode(target, p, tick):
    p = max(0.0, min(1.0, p))
    chars = list(target)
    settled = int(p * len(chars) + 1e-9)
    res = []
    pool = "abcdefghijklmnopqrstuvwxyz0123456789#$%&@"
    for i, c in enumerate(chars):
        if i < settled or c == " ":
            res.append(c)
        else:
            pick = pool[int(nkp_hash(i * 31 + tick * 7.13) * len(pool)) % len(pool)]
            res.append(pick)
    return "".join(res)


class NeonKatakanaBoot(FloatLayout):
    """
    Cinematic Japanese Neon Katakana Startup Experience matching Reference B & C:
    - Glowing magenta Katakana title 'ネオン' with hot core (#FFE1FB) and diffuse bloom
    - Granular particle dispersion that coalesces into the word
    - Vertical streams of falling Katakana code rain (ｱｲｳｴ...0123)
    - Deep violet atmospheric floor haze (#2A0A5C)
    - Decoded mint dot-matrix labels ('neon', percentage counter, 'online')
    - Minimal HUD corners (Sector 7, DECODING -> SIGNAL LOCKED, track line, TAP TO OPEN)
    - Slit-of-light / frame tear opening transition into the workspace
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._done = False
        self._locked = False
        self._pct = 0.0
        self._t = 0.0
        self._tick_count = 0
        self._rushed = False

        # Visual elements on canvas
        with self.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            # Deep violet floor haze #2A0A5C rising from bottom edge (Ref B & C)
            Color(VIOLET[0], VIOLET[1], VIOLET[2], 0.40)
            self._haze1 = Ellipse(pos=(0, 0), size=(10, 10))
            Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.05)
            self._haze2 = Ellipse(pos=(0, 0), size=(10, 10))

            # Dotted vertical strands
            Color(1.0, 1.0, 1.0, 0.035)
            self._strands = [Line(points=[0, 0, 0, 0], width=dp(0.9)) for _ in range(12)]

            # Rain columns (falling katakana)
            self._n_cols = 32
            self._rain_lines = [Line(points=[0, 0, 0, 0], width=dp(1.2)) for _ in range(self._n_cols)]
            self._rain_colors = [Color(0, 0, 0, 0) for _ in range(self._n_cols)]
            self._head_colors = [Color(0, 0, 0, 0) for _ in range(self._n_cols)]
            self._head_rects = [Rectangle(pos=(-100, -100), size=(dp(2.4), dp(2.4))) for _ in range(self._n_cols)]

            # Title particle grains (granular dispersion coalescing into the word)
            self._n_grains = 70
            self._grain_colors = [Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0) for _ in range(self._n_grains)]
            self._grain_rects = [Rectangle(pos=(-100, -100), size=(dp(2.2), dp(2.2))) for _ in range(self._n_grains)]

            # Scan sweep line
            self._sweep_c = Color(MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], 0)
            self._sweep_line = Line(points=[0, 0, 0, 0], width=dp(1.8))

            # Opening frame slit (for transition)
            self._frame_c = Color(MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], 0)
            self._frame_line = Line(rectangle=(0, 0, 0, 0), width=dp(2.0))

        # Title layers in Center
        self.title_glow = Label(
            text="ネオン", font_size="64sp", color=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.40), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=JAPANESE_FONT
        )
        self.title_main = Label(
            text="ネオン", font_size="64sp", color=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.95), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=JAPANESE_FONT
        )
        self.title_core = Label(
            text="ネオン", font_size="64sp", color=(MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], 0.85), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=JAPANESE_FONT
        )
        self.add_widget(self.title_glow)
        self.add_widget(self.title_main)
        self.add_widget(self.title_core)

        # Top label (decoded mint dot-matrix)
        self.label_top = Label(
            text="neon", font_size="13sp", color=MINT, bold=True, halign="center",
            size_hint=(None, None), size=(dp(200), dp(24)),
            pos_hint={"center_x": 0.5, "center_y": 0.64}, font_name=TECH_FONT
        )
        self.add_widget(self.label_top)

        # Bottom label (percentage / 'online')
        self.label_bottom = Label(
            text="000%", font_size="13sp", color=MINT, bold=True, halign="center",
            size_hint=(None, None), size=(dp(200), dp(24)),
            pos_hint={"center_x": 0.5, "center_y": 0.40}, font_name=TECH_FONT
        )
        self.add_widget(self.label_bottom)

        # HUD Corners (Ref B & C)
        # Top-Left: ネオン / SECTOR 7
        self.hud_tl = Label(
            text="ネオン / SECTOR 7", font_size="10sp", color=MAGENTA, bold=False,
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"x": 0.03, "top": 0.97}, font_name=JAPANESE_FONT
        )
        self.add_widget(self.hud_tl)

        # Top-Right: ● DECODING / ● SIGNAL LOCKED
        self.hud_tr = Label(
            text="● DECODING", font_size="10sp", color=MINT, bold=True, halign="right",
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"right": 0.97, "top": 0.97}, font_name=TECH_FONT
        )
        self.add_widget(self.hud_tr)

        # Bottom-Left: 000 ─────── 100
        self.hud_bl_box = BoxLayout(
            orientation="horizontal", spacing=dp(6),
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"x": 0.03, "y": 0.03}
        )
        self.hud_bl_cur = Label(text="000", font_size="10sp", color=MAGENTA, bold=False, size_hint_x=None, width=dp(30), font_name=TECH_FONT)
        self.hud_bl_track = Widget(size_hint=(1, None), height=dp(2), pos_hint={"center_y": 0.5})
        with self.hud_bl_track.canvas:
            Color(1, 1, 1, 0.12)
            self._track_bg = Rectangle(pos=(0, 0), size=(0, dp(1.5)))
            Color(*MAGENTA)
            self._track_fill = Rectangle(pos=(0, 0), size=(0, dp(1.8)))
        self.hud_bl_box.add_widget(self.hud_bl_cur)
        self.hud_bl_box.add_widget(self.hud_bl_track)
        self.hud_bl_box.add_widget(Label(text="100", font_size="10sp", color=MUTED, bold=False, size_hint_x=None, width=dp(30), font_name=TECH_FONT))
        self.add_widget(self.hud_bl_box)

        # Bottom-Right: TAP TO SKIP / TAP TO OPEN
        self.hud_br = Label(
            text="TAP TO SKIP", font_size="10sp", color=MUTED, bold=False, halign="right",
            size_hint=(None, None), size=(dp(220), dp(20)),
            pos_hint={"right": 0.97, "y": 0.03}, font_name=TECH_FONT
        )
        self.add_widget(self.hud_br)

        self.bind(pos=self._layout, size=self._layout)
        Window.bind(on_key_down=self._on_key)
        self._init_data()
        self._ev = Clock.schedule_interval(self._tick, 1 / 30.0)

    def _init_data(self):
        w, h = Window.width, Window.height
        self._cols_data = []
        for i in range(self._n_cols):
            cx = random.uniform(dp(10), w - dp(10))
            head = random.uniform(0, h * 1.4)
            spd = random.uniform(dp(60), dp(180))
            length = random.uniform(dp(40), dp(200))
            is_mint = (i % 4 == 0)
            self._cols_data.append([cx, head, spd, length, is_mint])

        self._grains_data = []
        for i in range(self._n_grains):
            tx = random.uniform(-dp(140), dp(140))
            ty = random.uniform(-dp(35), dp(35))
            fall = random.uniform(dp(40), dp(180))
            self._grains_data.append([tx, ty, fall, random.uniform(0.1, 0.9)])

    def _layout(self, *_):
        x, y, w, h = self.x, self.y, self.width, self.height
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._haze1.pos = (x - w * 0.1, y - h * 0.5)
        self._haze1.size = (w * 1.2, h * 0.85)
        self._haze2.pos = (x + w * 0.2, y - h * 0.4)
        self._haze2.size = (w * 0.6, h * 0.6)

        for i, strand in enumerate(self._strands):
            sx = x + w * ((i + 1) / 13.0)
            strand.points = [sx, y, sx, y + h]

    def _on_key(self, _window, key, *_):
        if key in (13, 32):  # Enter or Space
            self._activate()
            return True
        elif key == 27:      # Esc
            self._finish(True)
            return True
        self._activate()
        return False

    def on_touch_down(self, touch):
        if self._done:
            return False
        self._activate()
        return True

    def _activate(self):
        if not self._locked:
            self._rushed = True
        else:
            self._finish(False)

    def on_parent(self, _inst, parent):
        if parent is None:
            self._cleanup()

    def _cleanup(self):
        if self._ev is not None:
            self._ev.cancel()
            self._ev = None
        try:
            Window.unbind(on_key_down=self._on_key)
        except Exception:
            pass

    def _finish(self, fast):
        if self._done:
            return
        self._done = True
        self._cleanup()
        app = App.get_running_app()
        if app and hasattr(app, "play_sound"):
            try:
                app.play_sound("click")
            except Exception:
                pass

        if not fast:
            cx, cy = self.center
            self._frame_c.a = 0.95
            self._frame_line.rectangle = (cx - dp(10), cy - dp(2), dp(20), dp(4))
            anim = Animation(opacity=0.0, duration=0.45)
            anim.bind(on_complete=lambda *_: self._remove())
            anim.start(self)
        else:
            self._remove()

    def _remove(self):
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._cleanup()

    def _tick(self, dt):
        if self._done:
            return False
        self._t += dt
        t = self._t
        self._tick_count += 1
        w, h = self.width, self.height
        cx, cy = self.center

        # Progress computation
        target_pct = 1.0 if self._rushed else min(1.0, t / 3.0)
        rate = 0.20 if self._rushed else 0.08
        self._pct += (target_pct - self._pct) * rate
        if target_pct - self._pct < 0.005:
            self._pct = target_pct

        pct_val = int(self._pct * 100)
        pct_str = f"{pct_val:03d}"

        if pct_val < 100:
            self.label_top.text = nkp_decode("neon", self._pct * 1.3, self._tick_count)
            self.label_bottom.text = f"{pct_str}%"
            self.hud_tr.text = "● DECODING" if (int(t * 4) % 2 == 0) else "○ DECODING"
            self.hud_tr.color = MINT
            self.hud_br.text = "TAP TO SKIP" if not self._rushed else "DECODING..."
        else:
            self._locked = True
            self.label_top.text = "neon"
            self.label_bottom.text = "online"
            self.hud_tr.text = "● SIGNAL LOCKED"
            self.hud_tr.color = MINT
            self.hud_br.text = "TAP TO OPEN // ENTER"
            self.hud_br.color = MINT

        self.hud_bl_cur.text = pct_str
        track_w = self.hud_bl_track.width
        self._track_bg.pos = self.hud_bl_track.pos
        self._track_bg.size = (track_w, dp(1.5))
        self._track_fill.pos = self.hud_bl_track.pos
        self._track_fill.size = (track_w * self._pct, dp(1.8))

        # Title opacity & grain coalescing
        title_alpha = min(1.0, 0.2 + self._pct * 0.8)
        self.title_glow.color = (MAGENTA[0], MAGENTA[1], MAGENTA[2], title_alpha * 0.35)
        self.title_main.color = (MAGENTA[0], MAGENTA[1], MAGENTA[2], title_alpha * 0.95)
        self.title_core.color = (MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], title_alpha * 0.85)

        # Grain particles coalescing
        for i, (gtx, gty, fall, rank) in enumerate(self._grains_data):
            if rank <= self._pct:
                k = min(1.0, (self._pct - rank) / 0.2)
                e = 1.0 - (1.0 - k) ** 3
                gx = cx + gtx
                gy = cy + gty - fall * (1.0 - e)
                self._grain_rects[i].pos = (gx, gy)
                self._grain_colors[i].rgba = (MAGENTA[0], MAGENTA[1], MAGENTA[2], min(1.0, 0.3 + 0.7 * k))
            else:
                self._grain_colors[i].a = 0.0

        # Animate falling katakana streams
        for i, col in enumerate(self._cols_data):
            col_x, head, spd, length, is_mint = col
            head -= spd * dt
            if head < -length:
                head = h + random.uniform(dp(20), dp(100))
                col_x = random.uniform(dp(10), w - dp(10))
            col[0] = col_x
            col[1] = head

            top = min(h, head + length)
            draw_h = max(0, head)
            self._rain_lines[i].points = [col_x, top, col_x, draw_h]
            if is_mint:
                self._rain_colors[i].rgba = (MINT[0], MINT[1], MINT[2], 0.20 * self._pct + 0.08)
                self._head_colors[i].rgba = (MINT[0], MINT[1], MINT[2], 0.75)
            else:
                self._rain_colors[i].rgba = (MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.18 * self._pct + 0.08)
                self._head_colors[i].rgba = (MAGENTA_CORE[0], MAGENTA_CORE[1], MAGENTA_CORE[2], 0.70)
            self._head_rects[i].pos = (col_x - dp(1.2), draw_h - dp(1.2))

        # Scan sweep across the title
        if self._locked:
            sweep_p = (t * 0.8) % 1.6
            if sweep_p < 1.0:
                sy = cy + dp(40) - sweep_p * dp(80)
                self._sweep_c.a = 0.6 * math.sin(math.pi * sweep_p)
                self._sweep_line.points = [cx - dp(180), sy, cx + dp(180), sy]
            else:
                self._sweep_c.a = 0.0


BootScreen = NeonKatakanaBoot


# ------------------------------------------------------------
# COSMIC VOYAGER HERO & SPRITES (Pixel Rocket, Starfield, 3D Headline)
# ------------------------------------------------------------

_HERO_ROCKET = [
    "....P....",
    "...WWW...",
    "..WWWWW..",
    "..WWCWW..",
    "..WCCCW..",
    "..WWCWW..",
    "..WWWWW..",
    "..WGGGW..",
    ".PWWWWWP.",
    "PPWWWWWPP",
    "PP.GGG.PP",
    "P..GGG..P",
]
_HERO_PALETTE = [
    ("W", (0.88, 0.96, 1.0, 1)),
    ("G", (0.50, 0.62, 0.86, 1)),
    ("C", (0.0, 0.95, 1.0, 1)),
    ("P", (1.0, 0.20, 0.78, 1)),
]


class HeroPixelRocket(Widget):
    """Floating, bobbing pixel rocket companion with animated flame thrusters and launch capability."""
    def __init__(self, **kw):
        super().__init__(**kw)
        self._t = random.uniform(0, 5)
        self._launching = False
        self._launch_y = 0.0
        self._f_step = 0
        self._pix = []
        with self.canvas:
            PushMatrix()
            self._tr = Translate(0, 0)
            self._rot = Rotate(angle=0, origin=(0, 0))
            for ch, rgba in _HERO_PALETTE:
                Color(*rgba)
                for r, row in enumerate(_HERO_ROCKET):
                    for c, cell in enumerate(row):
                        if cell == ch:
                            self._pix.append((Rectangle(pos=(0, 0), size=(1, 1)), c, r))
            Color(1.0, 0.45, 0.10, 1)
            self._f_out = Rectangle(pos=(0, 0), size=(1, 1))
            Color(1.0, 0.88, 0.25, 1)
            self._f_in = Rectangle(pos=(0, 0), size=(1, 1))
            Color(1.0, 0.45, 0.10, 1)
            self._f_tip = Rectangle(pos=(0, 0), size=(1, 1))
            PopMatrix()
        self.bind(pos=self._layout, size=self._layout)
        self._layout()
        Clock.schedule_interval(self._tick, 1.0 / 24.0)

    def _layout(self, *_):
        px = max(1.0, min(self.width / 9.0, self.height / 15.0))
        self._px = px
        self._ox = self.x + (self.width - 9 * px) / 2.0
        self._oy = self.y + (self.height - 15 * px) / 2.0
        for rect, c, r in self._pix:
            rect.pos = (self._ox + c * px, self._oy + (14 - r) * px)
            rect.size = (px, px)
        self._rot.origin = self.center
        self._set_flame(1)

    def _set_flame(self, f):
        px, ox, oy = self._px, self._ox, self._oy
        self._f_out.pos = (ox + 3 * px, oy + 2 * px)
        self._f_out.size = (3 * px, px)
        self._f_in.pos = (ox + 4 * px, oy + (2 - f) * px)
        self._f_in.size = (px, (1 + f) * px)
        self._f_tip.pos = (ox + 4 * px, oy + (1 - f) * px)
        self._f_tip.size = (px, px)

    def _tick(self, dt):
        if not self.parent:
            return
        self._t += dt
        t = self._t
        if self._launching:
            self._launch_y += dt * dp(380)
            self._tr.y = self._launch_y
            self._set_flame(3 + int(t * 12) % 2)
            if self._launch_y > Window.height:
                self._launching = False
                self._launch_y = 0.0
                self._tr.y = 0.0
                self.opacity = 0
                anim = Animation(opacity=1, duration=0.6)
                anim.start(self)
        else:
            bob = math.sin(t * 2.2) * dp(3.5)
            self._tr.y = bob
            self._rot.angle = math.sin(t * 1.5) * 3.5
            flame = 1 if (int(t * 8) % 2 == 0) else 2
            self._set_flame(flame)

    def launch(self):
        self._launching = True
        self._launch_y = 0.0


class CosmicStarfield(Widget):
    """Animated cosmic starfield with drifting stars and floating gold pixel coins."""
    def __init__(self, count=65, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self._stars = []
        self._coins = []
        self._t = 0.0
        with self.canvas:
            self._star_colors = [Color(0.85, 0.95, 1.0, 0.6) for _ in range(count)]
            self._star_rects = [Rectangle(pos=(0, 0), size=(dp(1.8), dp(1.8))) for _ in range(count)]

            # 3 floating gold pixel coins
            self._coin_colors = [Color(1.0, 0.85, 0.20, 0.85) for _ in range(3)]
            self._coin_rects = [Rectangle(pos=(0, 0), size=(dp(8), dp(8))) for _ in range(3)]

        self.bind(pos=self._init_stars, size=self._init_stars)
        Clock.schedule_interval(self._tick, 1.0 / 30.0)

    def _init_stars(self, *_):
        w = max(self.width, 10)
        h = max(self.height, 10)
        self._stars = [
            [random.uniform(0, w), random.uniform(0, h), random.uniform(0.5, 2.0), random.uniform(0.3, 1.0)]
            for _ in range(self.count)
        ]
        self._coins = [
            [random.uniform(w * 0.1, w * 0.9), random.uniform(h * 0.15, h * 0.85), random.uniform(1.2, 2.5)]
            for _ in range(3)
        ]

    def _tick(self, dt):
        if not self.parent:
            return
        self._t += dt
        t = self._t
        w, h = self.width, self.height
        if w < 10 or h < 10:
            return

        for i, s in enumerate(self._stars):
            s[0] -= s[2] * 0.4
            if s[0] < 0:
                s[0] = w
                s[1] = random.uniform(0, h)
            alpha = max(0.12, min(0.95, s[3] + 0.35 * math.sin(t * 3.2 + i)))
            self._star_colors[i].a = alpha
            sz = dp(s[2] * 1.1)
            self._star_rects[i].pos = (self.x + s[0], self.y + s[1])
            self._star_rects[i].size = (sz, sz)

        for i, c in enumerate(self._coins):
            cy = c[1] + math.sin(t * 2.2 + i * 2.0) * dp(5)
            c_sz = dp(7.0 + math.cos(t * 3.5 + i) * 2.2)
            self._coin_rects[i].pos = (self.x + c[0], self.y + cy)
            self._coin_rects[i].size = (c_sz, dp(8.5))


class CosmicVoyagerHero(FloatLayout):
    """
    Cosmic Hero Banner:
    - Deep space void & ambient nebula glow
    - Interactive drifting starfield with gold coins
    - Interactive Pixel Rocket companion with flame thruster
    - Japanese Katakana glowing title: 'ボイジャー' in magenta with hot core
    - Deep violet atmospheric floor haze and minimal technical HUD labels
    - Dual Understated Quick Action HUD buttons (Focus Sprint & AI Helper)
    """
    def __init__(self, on_launch=None, on_ai=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(180))
        super().__init__(**kwargs)
        self.on_launch = on_launch
        self.on_ai = on_ai

        with self.canvas.before:
            Color(*BG_SECONDARY)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            # Atmospheric violet floor haze
            Color(VIOLET[0], VIOLET[1], VIOLET[2], 0.28)
            self._nebula1 = Ellipse(pos=(0, 0), size=(dp(420), dp(160)))
            Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.05)
            self._nebula2 = Ellipse(pos=(0, 0), size=(dp(300), dp(130)))

            # 1px hairline separator border
            Color(*SEPARATOR)
            self._border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(4)), width=dp(1.0))
            Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.12)
            self._glow_bd = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(4)), width=dp(1.5))

        self.bind(pos=self._layout_bg, size=self._layout_bg)

        # Starfield / ambient particles
        self.starfield = CosmicStarfield(count=36, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.starfield)

        # Pixel Rocket companion (retained for backward compatibility)
        self.rocket = HeroPixelRocket(size_hint=(None, None), size=(dp(46), dp(62)),
                                      pos_hint={"right": 0.95, "center_y": 0.52})
        self.add_widget(self.rocket)

        # Content container
        content = BoxLayout(orientation="vertical", padding=[dp(18), dp(12)], spacing=dp(5),
                            size_hint=(1, 1), pos_hint={"x": 0, "y": 0})

        # Top Bar: VOYAGER Brand + Telemetry
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
        voyager_logo = Label(
            text="[b]procrastiNOT[/b] // ボイジャー",
            markup=True,
            font_name=JAPANESE_FONT,
            font_size="11sp",
            color=MAGENTA,
            size_hint_x=None,
            width=dp(180),
            halign="left"
        )
        sector_status = Label(
            text="[color=#3dffb0]● ONLINE[/color] // SECTOR 07 // KERNEL NOMINAL",
            markup=True,
            font_name=TECH_FONT,
            font_size="10sp",
            color=MUTED,
            halign="right"
        )
        top_bar.add_widget(voyager_logo)
        top_bar.add_widget(sector_status)
        content.add_widget(top_bar)

        # Middle: Japanese Calligraphy Title ("ボイジャー")
        headline_box = FloatLayout(size_hint_y=None, height=dp(52))
        self.shadow_lbl = Label(
            text="ボイジャー",
            font_name=JAPANESE_FONT,
            font_size="34sp",
            bold=True,
            color=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.35),
            pos_hint={"center_x": 0.36, "center_y": 0.46}
        )
        self.front_lbl = Label(
            text="ボイジャー",
            font_name=JAPANESE_FONT,
            font_size="34sp",
            bold=True,
            color=MAGENTA_CORE,
            pos_hint={"center_x": 0.36, "center_y": 0.52}
        )
        self.sub_callsign = Label(
            text="// PROCRASTINOT COMMAND CORE",
            font_name=TECH_FONT,
            font_size="12sp",
            bold=True,
            color=WHITE,
            pos_hint={"x": 0.52, "center_y": 0.52}
        )
        headline_box.add_widget(self.shadow_lbl)
        headline_box.add_widget(self.front_lbl)
        headline_box.add_widget(self.sub_callsign)
        content.add_widget(headline_box)

        # Subtitle
        subtitle = Label(
            text="Persistent neural command interface. Focus on your active objectives and accelerate execution.",
            font_name=TECH_FONT,
            font_size="10.5sp",
            color=TEXT_SEC,
            halign="left",
            size_hint_y=None,
            height=dp(20)
        )
        content.add_widget(subtitle)

        # Quick Actions Row (Understated HUD Buttons)
        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(12))
        self.launch_btn = NeonButton(
            text="⚡ FOCUS SPRINT",
            style="style1",
            variant="primary",
            size="small",
            size_hint=(None, None),
            width=dp(170),
            height=dp(38)
        )
        if on_launch:
            self.launch_btn.bind(on_press=on_launch)

        self.ai_btn = NeonButton(
            text="🤖 CONSULT AI HELPER",
            style="style2",
            variant="secondary",
            size="small",
            size_hint=(None, None),
            width=dp(185),
            height=dp(38)
        )
        if on_ai:
            self.ai_btn.bind(on_press=on_ai)

        btn_row.add_widget(self.launch_btn)
        btn_row.add_widget(self.ai_btn)
        btn_row.add_widget(BoxLayout()) # right spacer
        content.add_widget(btn_row)

        self.add_widget(content)

    def _layout_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        cx, cy = self.center
        self._nebula1.pos = (cx - dp(240), cy - dp(90))
        self._nebula2.pos = (cx + dp(40), cy - dp(80))
        self._border.rounded_rectangle = (self.x, self.y, max(self.width, 2), max(self.height, 2), dp(4))
        self._glow_bd.rounded_rectangle = (self.x, self.y, max(self.width, 2), max(self.height, 2), dp(4))


# ------------------------------------------------------------
# QUEST PROOF VERIFICATION MODAL (AI Multimodal Audit)
# ------------------------------------------------------------

class QuestProofModal(Popup):
    """
    Polished Cyberpunk HUD Proof Verification Modal for procrastiNOT.exe.
    Requires photographic evidence before completing any quest.
    Integrates with Google Gemini Vision REST API.
    """
    def __init__(self, app, mission_index, mission, **kwargs):
        self.app = app
        self.mission_index = mission_index
        self.mission = mission
        self.staged_image_path = None
        self.staged_info = None
        self.is_verifying = False
        self.verdict_data = None
        self._scan_ev = None
        self._scan_t = 0.0

        kwargs.setdefault("title", "")
        kwargs.setdefault("separator_height", 0)
        kwargs.setdefault("auto_dismiss", False)
        kwargs.setdefault("size_hint", (0.92, 0.94))
        kwargs.setdefault("background_color", (0, 0, 0, 0.85))
        super().__init__(**kwargs)

        # Root Cyberpunk HUD Panel
        panel = NeonPanel(
            orientation="vertical",
            padding=[dp(14), dp(12)],
            spacing=dp(8),
            bg_color=BG_SECONDARY,
            border_color=MAGENTA
        )

        # Header Row
        hdr = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(8))
        hdr.add_widget(make_label("MISSION AUDIT // EVIDENCE VERIFICATION", 12, MAGENTA_CORE, True, size_hint_x=1))
        priority = mission.get("priority", "Normal")
        p_col = RED if priority == "Boss fight" else (MINT if priority == "High" else TEXT_SEC)
        hdr.add_widget(make_label(f"[{priority.upper()}]", 10, p_col, True, size_hint_x=None, width=dp(90)))

        close_btn = NeonButton(
            text="✕",
            variant="secondary",
            size_hint=(None, 1),
            width=dp(36),
            on_press=self.safe_dismiss
        )
        hdr.add_widget(close_btn)
        panel.add_widget(hdr)

        # Scrollable body
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=dp(4))
        self.body = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=[0, dp(4)])
        self.body.bind(minimum_height=self.body.setter("height"))

        # 1. Quest Context Card
        quest_card = NeonPanel(
            orientation="vertical",
            padding=[dp(12), dp(8)],
            spacing=dp(4),
            size_hint_y=None,
            bg_color=BG_ELEVATED,
            border_color=SEPARATOR
        )
        quest_card.bind(minimum_height=quest_card.setter("height"))
        quest_card.add_widget(make_label(f"🎯 OBJECTIVE: {mission.get('name', 'Untitled')}", 13, WHITE, True, auto_height=True))
        criteria_text = mission.get("criteria") or "Provide clear photo evidence confirming you finished this task."
        quest_card.add_widget(make_label(f"📋 ACCEPTANCE CRITERIA: {criteria_text}", 10.5, TEXT_SEC, auto_height=True))
        self.body.add_widget(quest_card)

        # 2. Evidence Capture Controls
        ctrl_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(38))
        self.photo_btn = NeonButton(text="📸 TAKE PHOTO", variant="primary", font_size="11sp")
        self.photo_btn.bind(on_press=lambda *_: self.action_take_photo())
        self.upload_btn = NeonButton(text="📁 UPLOAD PROOF", variant="secondary", font_size="11sp")
        self.upload_btn.bind(on_press=lambda *_: self.action_upload_proof())
        ctrl_row.add_widget(self.photo_btn)
        ctrl_row.add_widget(self.upload_btn)
        self.body.add_widget(ctrl_row)

        # 3. Image Viewport Frame
        self.preview_panel = NeonPanel(
            orientation="vertical",
            padding=dp(6),
            size_hint_y=None,
            height=dp(210),
            bg_color=BG,
            border_color=SEPARATOR
        )
        # Laser sweep line on canvas
        with self.preview_panel.canvas.after:
            self.scan_color = Color(MINT[0], MINT[1], MINT[2], 0.0)
            self.scan_line = Line(points=[0, 0, 0, 0], width=dp(2.0))
            self.scan_glow = Line(points=[0, 0, 0, 0], width=dp(6.0))

        self.preview_image = Image(fit_mode="contain", size_hint=(1, 1), opacity=0)
        self.placeholder_label = make_label(
            "┌────────────────────────────────────────────────────────┐\n"
            "│          [ RETICLE: NO EVIDENCE STAGED ]               │\n"
            "│   Snap a photo with camera or upload an image file     │\n"
            "└────────────────────────────────────────────────────────┘",
            10, MUTED, halign="center", valign="middle", size_hint=(1, 1)
        )
        self.preview_panel.add_widget(self.placeholder_label)
        self.preview_panel.add_widget(self.preview_image)
        self.body.add_widget(self.preview_panel)

        # Image Metadata / Status Label
        self.meta_label = make_label("NO EVIDENCE LOADED", 9.5, MUTED, halign="center")
        self.body.add_widget(self.meta_label)

        # 4. AI Evaluation / Verdict Box
        self.verdict_panel = NeonPanel(
            orientation="vertical",
            padding=[dp(12), dp(10)],
            spacing=dp(5),
            size_hint_y=None,
            bg_color=BG_ELEVATED,
            border_color=SEPARATOR
        )
        self.verdict_panel.bind(minimum_height=self.verdict_panel.setter("height"))
        self.verdict_title = make_label("STATUS // READY FOR EVIDENCE AUDIT", 11, TEXT_SEC, True, auto_height=True)
        self.verdict_desc = make_label("When evidence is staged, Gemini AI will verify visible proof against quest requirements.", 10, MUTED, auto_height=True)
        self.verdict_panel.add_widget(self.verdict_title)
        self.verdict_panel.add_widget(self.verdict_desc)

        # Evidence bullet points container (inside verdict panel)
        self.evidence_box = BoxLayout(orientation="vertical", spacing=dp(3), size_hint_y=None)
        self.evidence_box.bind(minimum_height=self.evidence_box.setter("height"))
        self.verdict_panel.add_widget(self.evidence_box)
        self.body.add_widget(self.verdict_panel)

        scroll.add_widget(self.body)
        panel.add_widget(scroll)

        # 5. Bottom Action Bar
        self.action_bar = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(44))
        self.cancel_action_btn = NeonButton(text="CANCEL", variant="secondary", size_hint_x=0.35, on_press=self.safe_dismiss)
        self.verify_action_btn = NeonButton(text="🤖 VERIFY WITH AI", variant="primary", size_hint_x=0.65, disabled=True)
        self.verify_action_btn.bind(on_press=lambda *_: self.start_verification())

        self.claim_btn = NeonButton(text="🚀 CLAIM +25 XP // CONCLUDE", variant="primary", size_hint_x=0.65)
        self.claim_btn.bind(on_press=lambda *_: self.claim_and_finish())
        self.claim_btn.opacity = 0
        self.claim_btn.disabled = True

        self.action_bar.add_widget(self.cancel_action_btn)
        self.action_bar.add_widget(self.verify_action_btn)
        panel.add_widget(self.action_bar)

        self.content = panel

    def _tick_scan(self, dt):
        self._scan_t += dt * 1.5
        box = self.preview_panel
        if not box:
            return
        p = 0.5 + 0.5 * math.sin(self._scan_t * math.pi)
        sy = box.y + p * box.height
        self.scan_color.a = 0.85
        self.scan_line.points = [box.x + dp(6), sy, box.right - dp(6), sy]
        self.scan_glow.points = [box.x + dp(6), sy, box.right - dp(6), sy]

    def _stop_scan(self):
        if self._scan_ev:
            self._scan_ev.cancel()
            self._scan_ev = None
        self.scan_color.a = 0.0

    def action_upload_proof(self):
        if self.is_verifying:
            return
        self.meta_label.text = "OPENING SYSTEM FILE CHOOSER..."
        self.meta_label.color = MINT
        proof_verifier.open_file_picker(
            on_selected=lambda path: Clock.schedule_once(lambda dt: self.on_image_selected(path), 0),
            on_cancelled=lambda: Clock.schedule_once(lambda dt: self.on_picker_cancelled(), 0)
        )

    def action_take_photo(self):
        if self.is_verifying:
            return
        self.meta_label.text = "INITIALIZING CAMERA SENSOR..."
        self.meta_label.color = MINT
        proof_verifier.capture_camera_photo(
            on_captured=lambda path: Clock.schedule_once(lambda dt: self.on_image_selected(path), 0),
            on_error=lambda err: Clock.schedule_once(lambda dt: self.on_camera_error(err), 0)
        )

    def on_image_selected(self, file_path):
        try:
            info = proof_verifier.preprocess_proof_image(file_path)
            self.staged_image_path = file_path
            self.staged_info = info

            # Update preview UI
            self.placeholder_label.opacity = 0
            self.preview_image.source = file_path
            self.preview_image.reload()
            self.preview_image.opacity = 1

            fname = os.path.basename(file_path)
            self.meta_label.text = f"● EVIDENCE STAGED: {fname}  •  {info['width']}x{info['height']}px  •  {info['size_kb']:.1f} KB"
            self.meta_label.color = MINT

            # Enable AI verify button
            self.verify_action_btn.disabled = False
            self.verify_action_btn.text = "🤖 VERIFY WITH AI"
            self.verify_action_btn.opacity = 1

            # Hide claim button if active from previous check
            self.claim_btn.opacity = 0
            self.claim_btn.disabled = True
            if self.claim_btn in self.action_bar.children:
                self.action_bar.remove_widget(self.claim_btn)
            if self.verify_action_btn not in self.action_bar.children:
                self.action_bar.add_widget(self.verify_action_btn)

            # Reset verdict state if re-staging
            self.verdict_title.text = "READY // EVIDENCE STAGED FOR VERIFICATION"
            self.verdict_title.color = MINT
            self.verdict_desc.text = "Tap 'VERIFY WITH AI' to send evidence to Gemini for multimodal evaluation."
            self.verdict_desc.color = WHITE
            self.verdict_panel.bg_color = BG_ELEVATED
            self.verdict_panel.border_color = MINT
            self.evidence_box.clear_widgets()
            self.evidence_box.height = 0

            self.app.play_sound("click")
        except Exception as exc:
            self.meta_label.text = f"⚠️ INVALID IMAGE: {str(exc)[:90]}"
            self.meta_label.color = RED
            self.app.play_sound("error")

    def on_picker_cancelled(self):
        if not self.staged_image_path:
            self.meta_label.text = "FILE SELECTION CANCELLED"
            self.meta_label.color = MUTED

    def on_camera_error(self, err_msg):
        self.meta_label.text = f"CAMERA UNAVAILABLE: {err_msg}"
        self.meta_label.color = RED
        self.app.play_sound("error")

    def start_verification(self):
        if self.is_verifying or not self.staged_info:
            return
        key = self.app._gemini_api_key()
        if not key:
            self.verdict_title.text = "⚠️ GEMINI API KEY MISSING"
            self.verdict_title.color = RED
            self.verdict_desc.text = "Please enter your free Gemini API key in Settings -> AI Keys."
            self.verdict_panel.border_color = RED
            self.app.play_sound("error")
            return

        self.is_verifying = True
        self.verify_action_btn.disabled = True
        self.photo_btn.disabled = True
        self.upload_btn.disabled = True
        self.cancel_action_btn.disabled = True

        self.verdict_title.text = "⚡ EVALUATING EVIDENCE // MULTIMODAL AUDIT"
        self.verdict_title.color = MINT
        self.verdict_desc.text = "Gemini Vision is inspecting your photo against the quest criteria..."
        self.verdict_panel.border_color = MINT

        # Start laser scanline animation
        self._scan_t = 0.0
        self._scan_ev = Clock.schedule_interval(self._tick_scan, 1 / 30.0)

        # Background worker thread
        def _worker():
            try:
                result = proof_verifier.verify_quest_proof_sync(
                    quest_title=self.mission.get("name", "Untitled"),
                    quest_desc=self.mission.get("description", ""),
                    quest_requirements=self.mission.get("criteria", ""),
                    image_b64=self.staged_info["b64"],
                    mime_type=self.staged_info["mime"],
                    api_key=key,
                    http_json_fn=self.app._http_json
                )
                Clock.schedule_once(lambda dt: self.on_verification_success(result), 0)
            except Exception as exc:
                Clock.schedule_once(lambda dt: self.on_verification_failure(str(exc)), 0)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def on_verification_success(self, result):
        self._stop_scan()
        self.is_verifying = False
        self.verdict_data = result
        self.photo_btn.disabled = False
        self.upload_btn.disabled = False
        self.cancel_action_btn.disabled = False

        verdict = result.get("verdict", "uncertain").lower()
        confidence = int(result.get("confidence", 0.5) * 100)
        reason = result.get("reason", "Evaluation complete.")
        evidence = result.get("evidence_found") or []
        missing = result.get("missing_evidence") or []

        self.evidence_box.clear_widgets()
        h_total = 0

        if verdict == "approved":
            self.verdict_panel.bg_color = (0.04, 0.16, 0.10, 0.95)
            self.verdict_panel.border_color = MINT
            self.verdict_title.text = f"✅ VERDICT: APPROVED ({confidence}% CONFIDENCE)"
            self.verdict_title.color = MINT
            self.verdict_desc.text = reason
            self.verdict_desc.color = WHITE

            if evidence:
                lbl = make_label("VISIBLE EVIDENCE CONFIRMED:", 10, MINT, True)
                self.evidence_box.add_widget(lbl)
                h_total += dp(20)
                for pt in evidence[:4]:
                    p_lbl = make_label(f"  • {pt}", 9.5, WHITE, auto_height=True)
                    self.evidence_box.add_widget(p_lbl)
                    h_total += dp(18)

            self.evidence_box.height = h_total
            self.app.play_sound("success")

            # Switch button to CLAIM REWARD
            self.verify_action_btn.opacity = 0
            self.verify_action_btn.disabled = True
            if self.verify_action_btn in self.action_bar.children:
                self.action_bar.remove_widget(self.verify_action_btn)

            self.claim_btn.opacity = 1
            self.claim_btn.disabled = False
            if self.claim_btn not in self.action_bar.children:
                self.action_bar.add_widget(self.claim_btn)

        elif verdict == "rejected":
            self.verdict_panel.bg_color = (0.20, 0.04, 0.08, 0.95)
            self.verdict_panel.border_color = RED
            self.verdict_title.text = f"❌ VERDICT: REJECTED ({confidence}% CONFIDENCE)"
            self.verdict_title.color = RED
            self.verdict_desc.text = reason
            self.verdict_desc.color = WHITE

            if missing:
                lbl = make_label("DEFICIENCIES / REASONS:", 10, RED, True)
                self.evidence_box.add_widget(lbl)
                h_total += dp(20)
                for pt in missing[:4]:
                    p_lbl = make_label(f"  • {pt}", 9.5, WHITE, auto_height=True)
                    self.evidence_box.add_widget(p_lbl)
                    h_total += dp(18)

            self.evidence_box.height = h_total
            self.app.play_sound("error")
            self.verify_action_btn.disabled = False
            self.verify_action_btn.text = "🔄 RETRY WITH NEW PROOF"

        else: # uncertain
            self.verdict_panel.bg_color = (0.18, 0.14, 0.04, 0.95)
            self.verdict_panel.border_color = YELLOW
            self.verdict_title.text = f"⚠️ VERDICT: UNCERTAIN ({confidence}% CONFIDENCE)"
            self.verdict_title.color = YELLOW
            self.verdict_desc.text = reason
            self.verdict_desc.color = WHITE

            if missing:
                lbl = make_label("WHAT EVIDENCE WOULD HELP:", 10, YELLOW, True)
                self.evidence_box.add_widget(lbl)
                h_total += dp(20)
                for pt in missing[:4]:
                    p_lbl = make_label(f"  • {pt}", 9.5, WHITE, auto_height=True)
                    self.evidence_box.add_widget(p_lbl)
                    h_total += dp(18)

            self.evidence_box.height = h_total
            self.app.play_sound("error")
            self.verify_action_btn.disabled = False
            self.verify_action_btn.text = "🔄 RETRY WITH CLEARER PROOF"

    def on_verification_failure(self, err_msg):
        self._stop_scan()
        self.is_verifying = False
        self.photo_btn.disabled = False
        self.upload_btn.disabled = False
        self.cancel_action_btn.disabled = False

        self.verdict_panel.bg_color = (0.18, 0.04, 0.06, 0.95)
        self.verdict_panel.border_color = RED
        self.verdict_title.text = "⚠️ VERIFICATION REQUEST FAILED"
        self.verdict_title.color = RED
        self.verdict_desc.text = f"{err_msg}\nPlease verify your internet connection or Gemini API key."
        self.verdict_desc.color = WHITE
        self.app.play_sound("error")

        self.verify_action_btn.disabled = False
        self.verify_action_btn.text = "🔄 RETRY VERIFICATION"

    def claim_and_finish(self):
        if not self.verdict_data or self.verdict_data.get("verdict") != "approved":
            return
        if self.mission.get("done", False):
            self.safe_dismiss()
            return
        self.safe_dismiss()
        self.app.claim_verified_mission(self.mission_index, self.verdict_data)

    def safe_dismiss(self, *_):
        self._stop_scan()
        if self.staged_image_path and "procrastiNOT_proof_" in self.staged_image_path:
            try:
                if os.path.exists(self.staged_image_path):
                    os.remove(self.staged_image_path)
            except Exception:
                pass
        self.dismiss()


class NeuralActivityHeatmap(NeonPanel):
    """
    30-Day GitHub-style Neural Activity & Consistency Matrix.
    Displays activity cells for the past 30 days based on completed quests.
    """
    def __init__(self, app, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", [dp(12), dp(10)])
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("bg_color", BG_ELEVATED)
        kwargs.setdefault("border_color", SEPARATOR)
        super().__init__(**kwargs)
        self.app = app
        self.height = dp(144)

        # Header with consistency stats
        hdr = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22), spacing=dp(8))
        self.title_lbl = make_label("📊 30-DAY NEURAL CONSISTENCY MATRIX", 12.5, CYAN, True, size_hint_x=1)
        self.consistency_badge = make_label("CONSISTENCY: 0%", 11, MINT, True, size_hint_x=None, width=dp(140), halign="right")
        hdr.add_widget(self.title_lbl)
        hdr.add_widget(self.consistency_badge)
        self.add_widget(hdr)

        # 30-cell grid: 10 columns x 3 rows
        self.grid = GridLayout(cols=10, spacing=dp(5), size_hint=(1, None), height=dp(60))
        self.cells = []
        for _ in range(30):
            tile = Widget(size_hint=(1, 1))
            self.cells.append(tile)
            self.grid.add_widget(tile)
        self.add_widget(self.grid)

        # Legend and info
        legend_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(6))
        legend_row.add_widget(make_label("LESS", 9.5, MUTED, False, size_hint_x=None, width=dp(34)))

        # 4 swatch samples
        swatches = [
            (0.10, 0.07, 0.16, 0.9),   # None
            (0.00, 0.55, 0.70, 0.95),  # 1 task
            (0.24, 1.00, 0.69, 1.00),  # 2 tasks
            (1.00, 0.85, 0.30, 1.00),  # 3+ tasks
        ]
        for c in swatches:
            sw = Widget(size_hint=(None, None), size=(dp(12), dp(12)), pos_hint={"center_y": 0.5})
            def _make_bind(color):
                return lambda inst, *_: self._draw_swatch(inst, color)
            sw.bind(pos=_make_bind(c), size=_make_bind(c))
            legend_row.add_widget(sw)

        legend_row.add_widget(make_label("MORE", 9.5, MUTED, False, size_hint_x=None, width=dp(38)))
        self.status_detail = make_label("🔥 0 ACTIVE SPRINT DAYS (LAST 30D)", 10, WHITE, True, size_hint_x=1, halign="right")
        legend_row.add_widget(self.status_detail)
        self.add_widget(legend_row)

        self.bind(pos=self._redraw_cells, size=self._redraw_cells)
        Clock.schedule_once(lambda *_: self._redraw_cells(), 0.1)

    def _draw_swatch(self, inst, color):
        inst.canvas.clear()
        with inst.canvas:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(2)])

    def refresh(self):
        self._redraw_cells()

    def _redraw_cells(self, *_):
        today = datetime.now().date()
        counts = {}
        for d_str in getattr(self.app, "completed_dates", []):
            counts[d_str] = counts.get(d_str, 0) + 1

        active_days = 0
        for i in range(30):
            day = today - timedelta(days=(29 - i))
            d_key = day.strftime("%Y-%m-%d")
            c = counts.get(d_key, 0)
            if c > 0:
                active_days += 1

            if i >= len(self.cells):
                continue
            tile = self.cells[i]
            tile.canvas.clear()
            bx, by = tile.pos
            w, h = tile.size
            if w <= 0 or h <= 0:
                continue

            if c == 0:
                col = (0.09, 0.06, 0.14, 0.9)
                border = (0.2, 0.15, 0.28, 0.35)
            elif c == 1:
                col = (0.00, 0.55, 0.70, 0.95)
                border = (0.0, 0.85, 1.0, 0.8)
            elif c == 2:
                col = (0.24, 1.00, 0.69, 1.00)
                border = (0.5, 1.0, 0.8, 0.9)
            else:
                col = (1.00, 0.85, 0.30, 1.00)
                border = (1.0, 1.0, 0.6, 1.0)

            with tile.canvas:
                Color(*col)
                RoundedRectangle(pos=(bx, by), size=(w, h), radius=[dp(3)])
                Color(*border)
                Line(rounded_rectangle=(bx, by, w, h, dp(3)), width=dp(1.0))

        rate = int((active_days / 30.0) * 100)
        self.consistency_badge.text = f"CONSISTENCY: {rate}%"
        self.status_detail.text = f"🔥 {active_days}/30 DAYS ACTIVE ({rate}%)"


# ------------------------------------------------------------
# the app
# ------------------------------------------------------------

class ProcrastiNotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "init_auth"):
            self.init_auth()
        self.xp = 0
        self.missions = []
        self.mood_logs = []
        self.completed_dates = []
        self.sound_enabled = True
        self.achievements = []
        self.daily_challenge_date = ""
        self.daily_challenge = ""
        self.api_key = ""
        self.gemini_key = ""
        self.groq_key = ""
        self._gemini_model = ""
        self._groq_model = ""
        self.last_ai_error = ""
        self.status_message = "SIDEKICK ONLINE // Pick a quest. Make it happen. 🎮"
        self._mascot_event = None
        self.chat_history = []
        self.ai_busy = False
        self.focus_idx = None
        self.ai_quest_map = {"(no focus quest)": None}
        self.focus_end = None
        self.focus_ev = None
        self._offline_noted = False
        self.log_lines = [f"[{datetime.now():%H:%M:%S}] SYSTEM ONLINE"]
        self.data_file = None
        self.selected_companion = ""
        self.companion_widget = None
        self.companion_settings_btn = None
        self.arcade_scores = {"neon_dodge": 0, "pixel_pop": 0, "memory_glitch": 1}
        self.arcade_screen = None
        self.focus_screen = None
        self.habits_screen = None
        self.habits = []
        self.focus_sprints = 0
        self.active_badge_filter = "ALL"
        self.badge_filter_buttons = {}
        self.current_page = "home"

    def build(self):
        self.title = APP_TITLE
        Window.clearcolor = BG
        Window.minimum_width = 720
        Window.minimum_height = 640
        if Window.width <= 800 and Window.height <= 600:
            try:
                Window.size = (1120, 720)
            except Exception:
                pass
        self.init_online()
        if hasattr(self, "init_auth"):
            self.init_auth()
            self.setup_authenticated_session()
        else:
            if not self.data_file:
                self.data_file = os.path.join(self.user_data_dir, "projectx_data.json")
            self.load_data()
            self.try_import_legacy_save()

        # App shell: minimal HUD navigation rail on the left, active workspace on the right.
        shell = BoxLayout(orientation="horizontal", padding=dp(8), spacing=dp(8))
        sidebar = NeonPanel(
            orientation="vertical", padding=[dp(8), dp(10)], spacing=dp(3),
            size_hint_x=None, width=dp(168), bg_color=BG_SECONDARY,
            border_color=SEPARATOR
        )
        sidebar.add_widget(GlitchTitle("procrastiNOT", size_hint_y=None, height=dp(28)))
        sidebar.add_widget(make_label("procrastiNOT.exe // OS", 10, MAGENTA_CORE, True,
                                      size_hint_y=None, height=dp(18), font_name=JAPANESE_FONT))
        self.cursor_label = make_label("● NET ONLINE", 9, MINT, True,
                                       size_hint_y=None, height=dp(16))
        sidebar.add_widget(self.cursor_label)
        sidebar.add_widget(make_label("// NAVIGATION", 9, MUTED, False,
                                      size_hint_y=None, height=dp(18)))

        from kivy.uix.screenmanager import ScreenManager, FadeTransition
        self.pages = ScreenManager(transition=FadeTransition(duration=0.15))
        self.nav_buttons = {}
        nav_items = [
            ("HOME", "home"),
            ("⏱️ FOCUS", "focus"),
            ("⚡ HABITS", "habits"),
            ("🎮 ARCADE", "arcade"),
            ("MISSIONS", "missions"),
            ("AI HELPER", "ai"),
            ("MOOD LAB", "mood"),
            ("BADGES", "achievements"),
            ("INSIGHTS", "insights"),
            ("ROAST ZONE", "roast"),
            ("PROFILE", "profile"),
            ("RANKS", "leaderboard"),
            ("SETTINGS", "settings"),
        ]
        nav_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=["bars", "content"],
            bar_width=dp(3),
            bar_color=CYAN,
            bar_inactive_color=(0.1, 0.4, 0.5, 0.3)
        )
        nav_box = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None)
        nav_box.bind(minimum_height=nav_box.setter("height"))
        for label, page_name in nav_items:
            is_first = (page_name == "home")
            btn = NeonButton(
                text=label,
                variant="nav_active" if is_first else "nav",
                font_size="10.5sp",
                size_hint_y=None,
                height=dp(30)
            )
            btn.bind(on_press=lambda _b, name=page_name: self.go_page(name))
            nav_box.add_widget(btn)
            self.nav_buttons[page_name] = btn
        nav_scroll.add_widget(nav_box)
        sidebar.add_widget(nav_scroll)

        self.companion_widget = companion.CompanionWidget(app=self)
        self.companion_widget.size_hint = (1, None)
        self.companion_widget.height = dp(175)
        sidebar.add_widget(self.companion_widget)

        # Player profile summary at bottom of rail
        mini = NeonPanel(orientation="vertical", padding=[dp(8), dp(5)], spacing=dp(2),
                         size_hint_y=None, height=dp(52), bg_color=BG_ELEVATED,
                         border_color=SEPARATOR)
        self.side_level = make_label("LVL 01", 11, MAGENTA_CORE, True, size_hint_y=None, height=dp(18))
        self.side_bar = NeonBar(fill_color=MINT, size_hint_y=None, height=dp(4))
        self.side_xp = make_label("0/100 XP", 9, MUTED, True, size_hint_y=None, height=dp(16))
        mini.add_widget(self.side_level)
        mini.add_widget(self.side_bar)
        mini.add_widget(self.side_xp)
        sidebar.add_widget(mini)

        main = BoxLayout(orientation="vertical", spacing=dp(8))

        # WORKSPACE HUD HEADER: Section Title, Streak, Level, XP Bar, Status
        header = NeonPanel(orientation="horizontal", padding=[dp(12), dp(6)],
                           spacing=dp(10), size_hint_y=None, height=dp(44),
                           bg_color=BG_SECONDARY, border_color=SEPARATOR)
        self.header_title = make_label("// HOME // COMMAND DECK", 12, WHITE, True, size_hint_x=1)
        header.add_widget(self.header_title)

        self.header_streak = make_label("STREAK: 0D", 10, MINT, True, size_hint_x=None, width=dp(78))
        self.level_label = make_label("LVL 1", 10, MAGENTA_CORE, True, size_hint_x=None, width=dp(48))
        self.xp_bar = NeonBar(fill_color=MINT, size_hint=(None, None), size=(dp(68), dp(4)), pos_hint={"center_y": 0.5})
        self.xp_label = make_label("0/100 XP", 9, MUTED, True, size_hint_x=None, width=dp(60))
        self.status_indicator = make_label("● NOMINAL", 10, MINT, True, size_hint_x=None, width=dp(72))
        self.mascot_label = Label(text="", size_hint=(None, None), size=(0, 0))

        header.add_widget(self.header_streak)
            # HOME PAGE (Command Center)
        home = self.make_page("home")
        hb = home.body
        self.hero = CosmicVoyagerHero(
            on_launch=lambda _b: self.launch_mission_action(),
            on_ai=lambda _b: self.go_page("ai")
        )
        hb.add_widget(self.hero)
        self.greeting_label = make_label("COMMAND ACCESS GRANTED // OPERATOR ONE", 11, TEXT_SEC, True,
                                         size_hint_y=None, height=dp(22))
        hb.add_widget(self.greeting_label)

        # Quick-Deploy Quest Terminal
        quick_terminal = NeonPanel(
            orientation="horizontal", padding=[dp(10), dp(6)], spacing=dp(8),
            size_hint_y=None, height=dp(48), bg_color=BG_ELEVATED,
            border_color=CYAN
        )
        self.quick_quest_input = make_input("⚡ Quick-deploy quest directive (Press Enter)...")
        self.quick_quest_input.bind(on_text_validate=self.quick_deploy_quest)
        deploy_btn = NeonButton(
            text="🚀 DEPLOY (+15 XP)", variant="primary", style="style1", size="small",
            size_hint_x=None, width=dp(154), height=dp(36)
        )
        deploy_btn.bind(on_press=self.quick_deploy_quest)
        quick_terminal.add_widget(self.quick_quest_input)
        quick_terminal.add_widget(deploy_btn)
        hb.add_widget(quick_terminal)

        # Action Hub Matrix: Focus Chamber & Boss Arena
        action_hub = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(68))

        # Focus Chamber Card
        focus_portal = NeonPanel(
            orientation="horizontal", padding=[dp(10), dp(6)], spacing=dp(8),
            size_hint_x=0.5, bg_color=BG_ELEVATED, border_color=CYAN
        )
        focus_desc = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.62)
        focus_desc.add_widget(make_label("⏱️ FOCUS CHAMBER", 13, CYAN, True, size_hint_y=None, height=dp(20)))
        focus_desc.add_widget(make_label("Pomodoro deep work • Rain audio • +50 XP", 10.5, TEXT_SEC, False, size_hint_y=None, height=dp(18)))
        focus_portal.add_widget(focus_desc)
        focus_btn = NeonButton(text="⚡ SPRINT", variant="primary", style="style1", size="small", size_hint_x=0.38, height=dp(38))
        focus_btn.bind(on_press=lambda *_: self.go_page("focus"))
        focus_portal.add_widget(focus_btn)
        action_hub.add_widget(focus_portal)

        # Cyber Habit Matrix Card
        habit_portal = NeonPanel(
            orientation="horizontal", padding=[dp(10), dp(6)], spacing=dp(8),
            size_hint_x=0.5, bg_color=BG_ELEVATED, border_color=CYAN
        )
        habit_desc = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.62)
        habit_desc.add_widget(make_label("⚡ HABIT MATRIX", 13, CYAN, True, size_hint_y=None, height=dp(20)))
        habit_desc.add_widget(make_label("Daily Routines, Streaks & Shield", 10.5, TEXT_SEC, False, size_hint_y=None, height=dp(18)))
        habit_portal.add_widget(habit_desc)
        habit_btn = NeonButton(text="🛡️ RITUALS", variant="primary", style="style1", size="small", size_hint_x=0.38, height=dp(38))
        habit_btn.bind(on_press=lambda *_: self.go_page("habits"))
        habit_portal.add_widget(habit_btn)
        action_hub.add_widget(habit_portal)

        hb.add_widget(action_hub)

        # Mind Reset Arcade Portal Callout Banner
        arcade_portal = NeonPanel(
            orientation="horizontal", padding=[dp(14), dp(8)], spacing=dp(12),
            size_hint_y=None, height=dp(64), bg_color=BG_ELEVATED,
            border_color=MAGENTA
        )
        arcade_info = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.60)
        arcade_info.add_widget(make_label("🕹️ MIND RESET ARCADE // BREAK ZONE", 13.5, MAGENTA_CORE, True, size_hint_y=None, height=dp(22)))
        arcade_info.add_widget(make_label("Defrag your neural cache. Zero deadlines. Just retro mini-games & vibes.", 11.5, TEXT_SEC, False, size_hint_y=None, height=dp(20)))
        arcade_portal.add_widget(arcade_info)

        arcade_launch_btn = NeonButton(
            text="🎮 ENTER THE ARCADE",
            variant="primary",
            style="style1",
            size="small",
            size_hint_x=0.40,
            height=dp(44)
        )
        arcade_launch_btn.bind(on_press=lambda *_: self.go_page("arcade"))
        arcade_portal.add_widget(arcade_launch_btn)
        hb.add_widget(arcade_portal)

        # Telemetry Matrix (4 compact cards in a row)
        hb.add_widget(section("TELEMETRY MATRIX", MAGENTA))
        stats = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(64))
        self.stat_missions = self.make_stat_card("0", "TOTAL MISSIONS", MINT)
        self.stat_done = self.make_stat_card("0", "CLEARED QUESTS", MINT)
        self.stat_active = self.make_stat_card("0D", "ACTIVE STREAK", MAGENTA_CORE)
        self.stat_mood = self.make_stat_card("NOMINAL", "BIOMETRIC MOOD", WHITE)
        for card in (self.stat_missions, self.stat_done, self.stat_active, self.stat_mood):
            stats.add_widget(card)
        hb.add_widget(stats)

        # 30-Day Neural Activity Matrix (GitHub-style consistency heatmap)
        hb.add_widget(section("NEURAL ACTIVITY MATRIX // 30-DAY STREAK", CYAN))
        self.activity_heatmap = NeuralActivityHeatmap(app=self)
        hb.add_widget(self.activity_heatmap)

        # Next Objective
        hb.add_widget(section("ACTIVE OBJECTIVE // NEXT UP", MINT))
        self.next_up_label = make_label("● All sectors clear. Stand by for new directives.", 12, WHITE,
                                        auto_height=True)
        hb.add_widget(self.next_up_label)

        # Quest Execution Rate
        hb.add_widget(section("EXECUTION RATE", WHITE))
        self.rate_bar = NeonBar(fill_color=MINT, size_hint_y=None, height=dp(6))
        hb.add_widget(self.rate_bar)
        self.rate_label = make_label("0% cleared", 10, MUTED, True,
                                     size_hint_y=None, height=dp(20))
        hb.add_widget(self.rate_label)

        # Daily Protocol Challenge
        hb.add_widget(section("DAILY PROTOCOL CHALLENGE", MAGENTA))
        self.daily_challenge_label = make_label(
            "Generate an operational objective and collect execution XP.",
            12, WHITE, auto_height=True)
        hb.add_widget(self.daily_challenge_label)
        challenge_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        random_btn = NeonButton(text="🎲 REROLL", style="style2", variant="secondary", size="small", size_hint_x=0.28)
        random_btn.bind(on_press=self.generate_daily_challenge)
        self.accept_btn = NeonButton(text="⚔️ ENGAGE CHALLENGE (+25 XP)", style="style1", variant="primary", size="small")
        self.accept_btn.bind(on_press=self.add_daily_challenge)
        challenge_row.add_widget(random_btn)
        challenge_row.add_widget(self.accept_btn)
        hb.add_widget(challenge_row)
        hb.add_widget(make_label("Engaging automatically logs the quest into your active Missions queue.",
                                 9, MUTED, auto_height=True))
        hb.add_widget(section("SYSTEM EVENT LOG", MINT))
        self.log_label = make_label("\n".join(self.log_lines), 9, MINT, auto_height=True)
        hb.add_widget(self.log_label)
        hb.add_widget(section("NEURAL SIDEKICK ADVISORY", WHITE))
        self.tip_label = make_label(random.choice(TIPS), 11, TEXT_SEC, auto_height=True)
        hb.add_widget(self.tip_label)
        self.add_page(home)

        # MISSIONS PAGE
        missions_page = self.make_page("missions")
        mb = missions_page.body
        mb.add_widget(section("🆕 NEW QUEST"))
        self.mission_input = make_input(
            "Tap here and type your quest…",
            size_hint_x=1,
        )
        mb.add_widget(self.mission_input)
        self.criteria_input = make_input(
            "Proof Criteria (e.g. photo of completed math p.42, 10k steps) - optional",
            size_hint_x=1,
        )
        mb.add_widget(self.criteria_input)
        form_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self.priority_spinner = Spinner(text="Normal", values=PRIORITIES, size_hint_x=0.40,
                                        background_normal="", background_color=(0.20, 0.15, 0.40, 1),
                                        color=WHITE, font_name=EMOJI_FONT)
        self.deadline_input = make_input("Deadline YYYY-MM-DD (optional)")
        form_row.add_widget(self.priority_spinner)
        form_row.add_widget(self.deadline_input)
        mb.add_widget(form_row)
        mb.add_widget(make_label("⏰ No deadline = 24 hours from now. Miss it and the roast arrives automatically. 😈",
                                 10, MUTED, auto_height=True))
        add_btn = NeonButton(text="➕ ADD QUEST", bg_color=(0.12, 0.28, 0.72, 1))
        add_btn.size_hint_y = None
        add_btn.height = dp(42)
        add_btn.bind(on_press=self.add_mission)
        mb.add_widget(add_btn)
        mb.add_widget(section("📜 QUEST LOG"))
        self.mission_filter = "all"
        self.filter_buttons = {}
        filter_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        for key, text in (("all", "📋 ALL"), ("active", "🔥 ACTIVE"),
                          ("done", "✅ DONE"), ("overdue", "🚨 LATE")):
            fb = NeonButton(
                text=text,
                variant="primary" if key == "all" else "secondary",
                style="style2",
                size="small",
                font_size="10.5sp",
                size_hint=(0.25, 1)
            )
            fb.bind(on_press=lambda _b, k=key: self.set_filter(k))
            self.filter_buttons[key] = fb
            filter_row.add_widget(fb)
        mb.add_widget(filter_row)
        self.mission_list = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        self.mission_list.bind(minimum_height=self.mission_list.setter("height"))
        mb.add_widget(self.mission_list)
        self.add_page(missions_page)

        # AI HELPER PAGE (custom layout: scrolling chat + fixed input row)
        self.add_page(self.build_ai_page(), spacer=False)

        # MOOD PAGE
        mood_page = self.make_page("mood")
        mdb = mood_page.body
        mdb.add_widget(section("🧠 SYSTEM CHECK: HOW ARE YOU?"))
        self.selected_mood = None
        mood_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(150))
        self.mood_options = []
        icon_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mood_icons")
        for mood in MOODS:
            icon_path = os.path.join(icon_folder, MOOD_ICONS[mood] + ".png")
            option = MoodOption(mood, icon_path, self)
            self.mood_options.append(option)
            mood_grid.add_widget(option)
        mdb.add_widget(mood_grid)
        mood_btn = NeonButton(text="💾 LOG MOOD", bg_color=(0.02, 0.52, 0.82, 1))
        mood_btn.size_hint_y = None
        mood_btn.height = dp(42)
        mood_btn.bind(on_press=self.log_mood)
        mdb.add_widget(mood_btn)
        mdb.add_widget(make_label("💙 Your wellbeing matters more than your XP.", 12, MUTED, auto_height=True))
        mdb.add_widget(section("🗓️ RECENT CHECK-INS", PINK))
        self.mood_history_label = make_label("Your mood history will appear here. 🫧", 12, WHITE,
                                             auto_height=True)
        mdb.add_widget(self.mood_history_label)
        self.add_page(mood_page)

        # BADGES PAGE (CYBER SYSTEM COMMENDATIONS ARCHIVE)
        achievements_page = self.make_page("achievements")
        ab = achievements_page.body
        ab.add_widget(section("🏆 SYSTEM COMMENDATIONS & BADGES // 業績 NEURAL ARCHIVE", PURPLE))

        # Commendation Telemetry Header Panel
        ach_panel = NeonPanel(
            orientation="vertical", padding=[dp(12), dp(10)], spacing=dp(6),
            size_hint_y=None, height=dp(80), bg_color=BG_ELEVATED, border_color=PURPLE
        )
        ach_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        self.achievement_label = make_label("🎖️ 0 / 28 UNLOCKED (0%)", 13, YELLOW, True, size_hint_x=0.60)
        self.achievement_xp_label = make_label("⭐ +0 XP COMMENDED", 11.5, MINT, True, size_hint_x=0.40, halign="right")
        ach_row.add_widget(self.achievement_label)
        ach_row.add_widget(self.achievement_xp_label)
        ach_panel.add_widget(ach_row)

        self.achievement_bar = NeonBar(fill_color=MINT, size_hint_y=None, height=dp(8))
        ach_panel.add_widget(self.achievement_bar)

        ach_sub = make_label("UNLOCK CYBERNETIC COMMENDATIONS ACROSS MISSIONS, SPRINTS, HABITS & ARCADE.", 9.5, TEXT_SEC, size_hint_y=None, height=dp(16))
        ach_panel.add_widget(ach_sub)
        ab.add_widget(ach_panel)

        # Category Filter Chips Bar
        filter_scroll = ScrollView(
            size_hint=(1, None), height=dp(38), do_scroll_x=True, do_scroll_y=False,
            scroll_type=["bars", "content"], bar_width=dp(2), bar_color=CYAN
        )
        filter_box = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_x=None)
        filter_box.bind(minimum_width=filter_box.setter("width"))

        filter_categories = [
            ("ALL", "ALL"),
            ("🎯 MISSIONS", "missions"),
            ("💎 XP & RANKS", "xp"),
            ("🔥 STREAKS", "streaks"),
            ("⚡ FOCUS & HABITS", "focus"),
            ("🎮 ARCADE", "arcade"),
            ("🤖 COMPANION", "biometrics"),
        ]

        self.badge_filter_buttons = {}
        for label, cat_key in filter_categories:
            w = dp(120) if len(label) > 10 else dp(84)
            btn = NeonButton(
                text=label, variant="primary" if cat_key == "ALL" else "secondary",
                style="style2", size_hint=(None, None), width=w, height=dp(32)
            )
            btn.bind(on_press=lambda _b, k=cat_key: self.set_badge_filter(k))
            filter_box.add_widget(btn)
            self.badge_filter_buttons[cat_key] = btn

        filter_scroll.add_widget(filter_box)
        ab.add_widget(filter_scroll)

        self.badge_list = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        self.badge_list.bind(minimum_height=self.badge_list.setter("height"))
        ab.add_widget(self.badge_list)
        self.add_page(achievements_page)

        # INSIGHTS PAGE
        insights_page = self.make_page("insights")
        ib = insights_page.body
        ib.add_widget(section("📊 ARCADE INSIGHTS"))
        ins_stats = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(136))
        self.ins_xp = self.make_stat_card("0", "⭐ TOTAL XP", YELLOW)
        self.ins_streak = self.make_stat_card("0", "🔥 BEST STREAK", PINK)
        self.ins_rate = self.make_stat_card("0%", "🏁 CLEAR RATE", GREEN)
        self.ins_moods = self.make_stat_card("0", "🫶 MOOD LOGS", CYAN)
        for card in (self.ins_xp, self.ins_streak, self.ins_rate, self.ins_moods):
            ins_stats.add_widget(card)
        ib.add_widget(ins_stats)
        self.insights_label = make_label("📭 Complete a quest to start building your stats.", 13, WHITE,
                                         auto_height=True)
        ib.add_widget(self.insights_label)
        self.insights_bar = NeonBar(fill_color=CYAN, size_hint_y=None, height=dp(14))
        ib.add_widget(self.insights_bar)
        ib.add_widget(section("📅 LAST 7 DAYS", PURPLE))
        self.week_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        self.week_box.bind(minimum_height=self.week_box.setter("height"))
        ib.add_widget(self.week_box)
        ib.add_widget(section("🫶 MOOD MIX", PINK))
        self.mood_mix_label = make_label("No moods logged yet. 🫧", 12, WHITE, auto_height=True)
        ib.add_widget(self.mood_mix_label)
        ib.add_widget(section("🔥 STREAK", YELLOW))
        self.streak_label = make_label("STREAK // 0 days", 13, YELLOW, True, auto_height=True)
        ib.add_widget(self.streak_label)
        self.add_page(insights_page)

        # ROAST ZONE PAGE
        roast_page = self.make_page("roast")
        rb = roast_page.body
        rb.add_widget(section("😈 UNHINGED SIDEKICK", PINK))
        self.roast_face = make_label("😈", 54, WHITE, halign="center",
                                     size_hint_y=None, height=dp(86))
        rb.add_widget(self.roast_face)
        self.chaos_label = make_label("Loading today's questionable life advice...", 14, WHITE,
                                      halign="center", auto_height=True)
        rb.add_widget(self.chaos_label)
        excuse_btn = NeonButton(text="🎭 GENERATE A QUESTIONABLE EXCUSE", bg_color=(0.36, 0.16, 0.48, 1))
        excuse_btn.size_hint_y = None
        excuse_btn.height = dp(44)
        excuse_btn.bind(on_press=self.generate_excuse)
        rb.add_widget(excuse_btn)
        roast_btn = NeonButton(text="😈 ROAST ME", bg_color=(0.48, 0.10, 0.22, 1))
        roast_btn.size_hint_y = None
        roast_btn.height = dp(44)
        roast_btn.bind(on_press=self.roast_me)
        rb.add_widget(roast_btn)
        rb.add_widget(section("🌡️ PROCRASTINATION METER", YELLOW))
        self.meter_bar = NeonBar(fill_color=GREEN, size_hint_y=None, height=dp(16))
        rb.add_widget(self.meter_bar)
        self.meter_label = make_label("😇 Zero overdue quests. Suspiciously responsible.", 12, WHITE,
                                      auto_height=True)
        rb.add_widget(self.meter_label)
        rb.add_widget(section("💀 HALL OF SHAME", RED))
        self.shame_label = make_label("🕊️ Nobody in the hall of shame. Respect.", 12, WHITE,
                                      auto_height=True)
        rb.add_widget(self.shame_label)
        self.add_page(roast_page)

        # SETTINGS PAGE
        settings_page = self.make_page("settings")
        sb = settings_page.body
        sb.add_widget(section("⚙️ SETTINGS"))
        if hasattr(self, "build_auth_settings_section"):
            self.build_auth_settings_section(sb)
        is_snd = getattr(self, "sound_enabled", True)
        self.sound_button = NeonButton(
            text="🔊 SOUND: ONLINE [ON]" if is_snd else "🔇 SOUND: MUTED [OFF]",
            variant="mint" if is_snd else "secondary",
            style="style1",
            bg_color=(0.08, 0.40, 0.28, 1) if is_snd else (0.28, 0.14, 0.20, 1),
            size_hint_y=None, height=dp(44)
        )
        self.sound_button.bind(on_press=self.toggle_sound)
        sb.add_widget(self.sound_button)
        sb.add_widget(section("🤖 OPERATOR COMPANION", CYAN))
        cur_id = getattr(self, "selected_companion", "nex") or "nex"
        cur_name = companion.OPERATORS.get(cur_id, {}).get("name", "NEX")
        self.companion_settings_btn = NeonButton(
            text=f"SWITCH OPERATOR: {cur_name}",
            variant="primary",
            bg_color=(0.18, 0.12, 0.42, 1)
        )
        self.companion_settings_btn.size_hint_y = None
        self.companion_settings_btn.height = dp(44)
        self.companion_settings_btn.bind(on_press=lambda *_: self.open_companion_selector(force=True))
        sb.add_widget(self.companion_settings_btn)
        self.build_region_section(sb)
        sb.add_widget(section("🔑 AI KEY (OPTIONAL OVERRIDE)", PINK))
        self.provider_spinner = Spinner(
            text="Google Gemini (free)", values=list(PROVIDER_CHOICES.keys()),
            size_hint_y=None, height=dp(40), background_normal="",
            background_color=(0.12, 0.16, 0.34, 1), color=WHITE, font_name=EMOJI_FONT)
        self.key_help_label = make_label(KEY_HELP["gemini"], 10, CYAN, auto_height=True)
        self.provider_spinner.bind(text=self._on_provider_pick)
        sb.add_widget(self.provider_spinner)
        sb.add_widget(self.key_help_label)
        self.key_state_label = make_label("", 11, MUTED, True, auto_height=True)
        sb.add_widget(self.key_state_label)
        self.key_input = make_input("Paste your API key…", password=True)
        sb.add_widget(self.key_input)
        key_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        save_key_btn = NeonButton(text="💾 SAVE KEY", bg_color=(0.08, 0.38, 0.30, 1))
        save_key_btn.bind(on_press=self.save_api_key)
        clear_key_btn = NeonButton(text="🗑️ CLEAR KEY", bg_color=(0.48, 0.10, 0.22, 1))
        clear_key_btn.bind(on_press=self.clear_api_key)
        key_row.add_widget(save_key_btn)
        key_row.add_widget(clear_key_btn)
        sb.add_widget(key_row)
        test_btn = NeonButton(text="🧪 TEST AI CONNECTION", bg_color=(0.02, 0.52, 0.82, 1))
        test_btn.size_hint_y = None
        test_btn.height = dp(42)
        test_btn.bind(on_press=self.test_ai)
        sb.add_widget(test_btn)
        sb.add_widget(make_label(
            "🔒 Your key is stored only on this PC, inside the JSON save file.\n"
            "📡 With a cloud key, your messages and quest names go to that provider. Free tiers may use data to improve their products.\n"
            "🏠 The offline helper keeps everything on this PC. The built-in AI key lives at the top of main.py.",
            10, MUTED, auto_height=True))
        sb.add_widget(section("ℹ️ ABOUT", MUTED))
        sb.add_widget(make_label(
            "💾 Your progress is saved locally in a JSON file.\n🖼️ Keep the mood_icons folder beside main.py.\n🕹️ Built with Python + Kivy.",
            11, MUTED, auto_height=True))
        self.add_page(settings_page)
        self.add_page(self.build_profile_page())
        self.add_page(self.build_leaderboard_page())
        try:
            import arcade
            self.arcade_screen = arcade.create_arcade_screen(self)
            self.pages.add_widget(self.arcade_screen)
        except Exception as _arc_err:
            print("arcade screen load error:", _arc_err)

        try:
            import focus_chamber
            self.focus_screen = focus_chamber.create_focus_screen(self)
            self.pages.add_widget(self.focus_screen)
        except Exception as _foc_err:
            print("focus screen load error:", _foc_err)

        try:
            import habits
            self.habits_screen = habits.create_habit_screen(self)
            self.pages.add_widget(self.habits_screen)
        except Exception as _habits_err:
            print("habits screen load error:", _habits_err)

        main.add_widget(self.pages)
        status_panel = NeonPanel(orientation="horizontal", padding=[dp(12), 0],
                                 size_hint_y=None, height=dp(32),
                                 bg_color=BG_SECONDARY,
                                 border_color=SEPARATOR)
        self.status_label = make_label("SYS> " + self.status_message, 10, MINT, True, size_hint_y=1)
        status_panel.add_widget(self.status_label)
        main.add_widget(status_panel)
        shell.add_widget(sidebar)
        shell.add_widget(main)

        self.go_page("home")
        self.refresh_screen()
        if self.daily_challenge_date != today_key() or not self.daily_challenge:
            self.generate_daily_challenge()
        else:
            self.daily_challenge_label.text = self.daily_challenge
            self.update_accept_button()
        self.show_random_roast()
        self.add_bubble("👋 Yo! I'm your AI sidekick. Pick a focus quest above (or tap 🤖 on any quest), "
                        "hit a chip, or ask me anything. I'll help you finish faster.", "ai")
        Clock.schedule_once(self.check_deadlines, 3.5)
        Clock.schedule_once(lambda dt: self.check_first_launch_companion(), 4.2)
        Clock.schedule_once(lambda dt: self.apply_language(), 0.4)
        Clock.schedule_once(lambda dt: self.sync_now(), 6)
        Clock.schedule_interval(self.check_deadlines, 30)
        Clock.schedule_interval(lambda dt: self.refresh_screen(), 60)
        Clock.schedule_interval(self._blink, 0.6)

        root = FloatLayout()
        root.add_widget(CyberBackdrop())
        root.add_widget(shell)
        root.add_widget(BootScreen())
        return root

    # ---------- pages ----------

    def make_page(self, name):
        """A scrollable page whose panel always fills the whole visible area."""
        from kivy.uix.screenmanager import Screen
        screen = Screen(name=name)
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=["bars", "content"],
            scroll_distance=10,
            scroll_timeout=180,
            bar_width=dp(5),
            bar_color=CYAN,
            bar_inactive_color=(0.15, 0.55, 0.68, 0.35),
            effect_cls="ScrollEffect",
        )
        body = NeonPanel(
            orientation="vertical",
            spacing=dp(6),
            padding=[dp(10), dp(10)],
            size_hint=(1, None),
            bg_color=PANEL,
            border_color=(0.0, 0.70, 0.85, 0.40),
        )

        def fit(*_):
            body.height = max(body.minimum_height, scroll.height)

        body.bind(minimum_height=fit)
        scroll.bind(height=fit)
        scroll.add_widget(body)
        screen.add_widget(scroll)
        screen.body = body
        return screen

    def add_page(self, screen, spacer=True):
        # Invisible spacer keeps page content anchored to the TOP instead of the bottom.
        if spacer:
            screen.body.add_widget(Widget(size_hint_y=1))
        self.pages.add_widget(screen)

    def set_filter(self, key):
        self.mission_filter = key
        for k, fb in getattr(self, "filter_buttons", {}).items():
            is_active = (k == key)
            fb.variant = "primary" if is_active else "secondary"
            fb.set_bg(NAV_ACTIVE if is_active else NAV_IDLE)
        self.play_sound("click")
        self.refresh_screen()

    def go_page(self, name):
        prev_name = getattr(self, "current_page", "home")
        if prev_name == "arcade" and name != "arcade" and getattr(self, "arcade_screen", None):
            try:
                self.arcade_screen.on_leave()
            except Exception:
                pass
        if prev_name == "focus" and name != "focus" and getattr(self, "focus_screen", None):
            try:
                self.focus_screen.on_leave()
            except Exception:
                pass
        if prev_name == "habits" and name != "habits" and getattr(self, "habits_screen", None):
            try:
                self.habits_screen.on_leave()
            except Exception:
                pass
        self.current_page = name

        if hasattr(self, "pages"):
            self.pages.current = name
        for page_name, button in getattr(self, "nav_buttons", {}).items():
            is_active = (page_name == name)
            button.variant = "nav_active" if is_active else "nav"
            button.set_bg(NAV_ACTIVE if is_active else NAV_IDLE)
        titles = {
            "home": "// HOME // COMMAND DECK",
            "focus": "// CYBER FOCUS CHAMBER // POMODORO DEEP WORK",
            "habits": "// CYBER HABIT MATRIX // DAILY RITUALS & SHIELD",
            "arcade": "// MIND RESET ARCADE // NEURAL RECHARGE ZONE",
            "missions": "// MISSIONS // ACTIVE OBJECTIVES",
            "ai": "// AI HELPER // NEURAL ASSISTANT",
            "mood": "// MOOD LAB // BIOMETRIC LOG",
            "achievements": "// BADGES // SYSTEM COMMENDATIONS",
            "insights": "// INSIGHTS // TELEMETRY ANALYTICS",
            "roast": "// ROAST ZONE // MOTIVATIONAL PROTOCOL",
            "profile": "// PROFILE // OPERATOR DOSSIER",
            "leaderboard": "// RANKS // GLOBAL NETWORK MATRIX",
            "settings": "// SETTINGS // HARDWARE & CONFIG",
        }
        if hasattr(self, "header_title") and name in titles:
            self.header_title.text = titles[name]
        if hasattr(self, "header_streak"):
            self.header_streak.text = f"STREAK: {self.current_streak()}D"
        if name == "arcade" and getattr(self, "arcade_screen", None):
            try:
                self.arcade_screen.on_enter()
            except Exception:
                pass
        elif name == "focus" and getattr(self, "focus_screen", None):
            try:
                self.focus_screen.on_enter()
            except Exception:
                pass
        elif name == "habits" and getattr(self, "habits_screen", None):
            try:
                self.habits_screen.on_enter()
            except Exception:
                pass
        elif name == "leaderboard" and hasattr(self, "lb_list"):
            self.fetch_leaderboard()
        elif name == "profile" and hasattr(self, "profile_summary"):
            self.refresh_profile(reset_input=True)

    def add_xp(self, amount, reason="MISSION BONUS"):
        """Safely increments player XP, saves data, and triggers level-up celebration if threshold crossed."""
        previous_level = self.xp // 100 + 1
        old_achievements = set(getattr(self, "achievements", []) or [])
        self.xp += amount
        self.achievements = self.unlocked_achievements()
        newly_unlocked = [a for a in self.achievements if a not in old_achievements]
        self.save_data()
        self.refresh_screen()
        if self.xp // 100 + 1 > previous_level:
            new_lvl = self.xp // 100 + 1
            msg = f"✨ LEVEL UP! PROMOTED TO LEVEL {new_lvl}! ✨\nKeep crushing objectives, Operator! 🔥"
            if newly_unlocked:
                msg += "\n\n🏆 COMMENDATIONS UNLOCKED:\n" + "\n".join(newly_unlocked[:3])
            self.show_celebration(msg)
            self.emoji_rain(["⭐", "✨", "🔥", "🚀", "👑"], 28)
            self.play_sound("level_up")
        elif newly_unlocked:
            self.show_celebration(f"🏆 SYSTEM COMMENDATION UNLOCKED!\n" + "\n".join(newly_unlocked[:3]))
            self.emoji_rain(["🏆", "✨", "⭐", "🎉"], 24)
            self.play_sound("level_up")
            if hasattr(self, "companion_widget") and self.companion_widget:
                try:
                    self.companion_widget.on_game_event("achievement_unlocked")
                except Exception:
                    pass

    def quick_deploy_quest(self, *_):
        """Quickly logs a new quest directly from the Home Command Deck terminal."""
        text = (getattr(self, "quick_quest_input", None) and self.quick_quest_input.text or "").strip()
        if not text:
            return
        m = {
            "name": text,
            "priority": "Normal",
            "due": "",
            "done": False,
            "id": f"q_{int(time.time()*1000)}"
        }
        self.missions.append(m)
        self.quick_quest_input.text = ""
        self.add_xp(15)
        self.play_sound("click")
        self.save_data()
        self.refresh_screen()
        try:
            import fx
            w_center = Window.center
            fx.layer().burst(w_center[0], w_center[1], n=24, colors=[MINT, CYAN, YELLOW])
            fx.layer().toast("🚀 DIRECTIVE DEPLOYED!", f"Logged: {text[:30]}", extra="+15 XP", color=MINT)
        except Exception:
            pass
        if hasattr(self, "companion_widget") and self.companion_widget:
            self.companion_widget.on_game_event("quest_started")

    def launch_mission_action(self):
        """Action triggered when clicking 'LAUNCH MISSION' in the Cosmic Voyager Hero."""
        if hasattr(self, "hero") and hasattr(self.hero, "rocket"):
            self.hero.rocket.launch()
        self.play_sound()
        try:
            import fx
            w_center = Window.center
            fx.layer().burst(w_center[0], w_center[1], n=36, colors=[CYAN, PINK, YELLOW, GREEN])
            fx.layer().toast("🚀 MISSION LAUNCHED!", "Entering quest trajectory...", extra="+10 BONUS XP", color=CYAN)
        except Exception:
            pass
        self.go_page("missions")

    def _blink(self, _dt):
        self._cursor_on = not getattr(self, "_cursor_on", False)
        if hasattr(self, "cursor_label"):
            self.cursor_label.text = "● NET ONLINE" if self._cursor_on else "○ NET ONLINE"

    # ---------- AI helper page ----------

    def build_ai_page(self):
        from kivy.uix.screenmanager import Screen
        screen = Screen(name="ai")
        panel = NeonPanel(orientation="vertical", padding=dp(10), spacing=dp(6),
                          bg_color=BG_SECONDARY, border_color=SEPARATOR)
        panel.add_widget(section("NEURAL AI SIDEKICK // OPERATIONAL COPILOT", MAGENTA))

        top = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        self.ai_quest_spinner = Spinner(
            text="(no focus quest)", values=["(no focus quest)"],
            background_normal="", background_color=BG_ELEVATED,
            color=WHITE, font_name=TECH_FONT, font_size="11sp")
        self.ai_quest_spinner.bind(text=self._on_quest_pick)
        self.focus_btn = NeonButton(text="⏱️ 25:00 FOCUS", style="style2", variant="secondary", size="small", size_hint_x=0.38)
        self.focus_btn.bind(on_press=self.toggle_focus)
        top.add_widget(self.ai_quest_spinner)
        top.add_widget(self.focus_btn)
        panel.add_widget(top)

        self.ai_mode_label = make_label("", 9.5, MUTED, True, size_hint_y=None, height=dp(18))
        panel.add_widget(self.ai_mode_label)

        self.chat_scroll = ScrollView(do_scroll_x=False, bar_width=dp(6), bar_color=MINT,
                                      bar_inactive_color=(0.239, 1.0, 0.690, 0.2),
                                      scroll_type=["bars", "content"], effect_cls="ScrollEffect")
        self.chat_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None,
                                  padding=[0, dp(4)])
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        self.chat_scroll.add_widget(self.chat_box)
        panel.add_widget(self.chat_scroll)

        chips = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(34))
        for label, prompt in CHIPS:
            chip = NeonButton(text=label, style="style2", variant="secondary", size="small")
            chip.font_size = "9.5sp"
            chip.bind(on_press=lambda _b, p=prompt: self.send_chat(p))
            chips.add_widget(chip)
        panel.add_widget(chips)
        web_row = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(32))
        for label, which in (("🔎 GOOGLE", "google"), ("✨ GEMINI", "gemini"),
                             ("💬 CHATGPT", "chatgpt"), ("🧠 CLAUDE", "claude")):
            wb = NeonButton(text=label, style="style2", variant="secondary", size="small")
            wb.font_size = "9.5sp"
            wb.bind(on_press=lambda _b, w=which: self.open_web(w))
            web_row.add_widget(wb)
        panel.add_widget(web_row)

        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.chat_input = make_input("Query neural sidekick regarding your active quest…")
        self.chat_input.bind(on_text_validate=lambda *_: self.send_chat())
        send_btn = NeonButton(text="TRANSMIT ➤", style="style1", variant="primary", size="small",
                              size_hint_x=None, width=dp(110))
        send_btn.bind(on_press=lambda *_: self.send_chat())
        row.add_widget(self.chat_input)
        row.add_widget(send_btn)
        panel.add_widget(row)

        screen.add_widget(panel)
        return screen

    def _on_quest_pick(self, _spinner, text):
        self.focus_idx = self.ai_quest_map.get(text)

    def focus_quest(self):
        i = self.focus_idx
        if i is not None and 0 <= i < len(self.missions) and not self.missions[i].get("done", False):
            return self.missions[i]
        return None

    def ask_ai_about(self, index):
        for label, idx in self.ai_quest_map.items():
            if idx == index:
                self.ai_quest_spinner.text = label
                break
        else:
            self.focus_idx = index
        self.go_page("ai")
        self.send_chat("Break this quest into tiny steps and tell me what to do first.")

    def _scroll_chat(self):
        for delay in (0.05, 0.35):
            Clock.schedule_once(lambda dt: setattr(self.chat_scroll, "scroll_y", 0), delay)

    def add_bubble(self, text, who="ai"):
        is_user = who == "user"
        color = MAGENTA if is_user else MINT
        row = BoxLayout(size_hint_y=None, spacing=dp(6))
        bubble = NeonPanel(
            orientation="vertical", size_hint_x=0.86, size_hint_y=None,
            padding=[dp(10), dp(7)],
            bg_color=BG_ELEVATED if is_user else BG_SECONDARY,
            border_color=SEPARATOR,
        )
        tag = make_label("OPERATOR //" if is_user else "NEURAL AI //", 9, color, True,
                         size_hint_y=None, height=dp(16))
        lbl = make_label(text, 12, WHITE, auto_height=True)
        bubble.add_widget(tag)
        bubble.add_widget(lbl)

        def _fit(*_):
            bubble.height = lbl.height + dp(16) + dp(14)

        lbl.bind(height=_fit)
        _fit()
        bubble.bind(height=lambda _i, h: setattr(row, "height", h))
        row.height = bubble.height
        spacer = Widget(size_hint_x=0.14)
        if is_user:
            row.add_widget(spacer)
            row.add_widget(bubble)
        else:
            row.add_widget(bubble)
            row.add_widget(spacer)
        self.chat_box.add_widget(row)
        self._scroll_chat()
        return lbl

    def ai_system_prompt(self):
        active = [m for m in self.missions if not m.get("done", False)]
        lines = []
        for m in active[-8:]:
            lines.append(f"- {m.get('name', 'Untitled')} ({m.get('priority', 'Normal')}, {time_left_text(m)})")
        quests = "\n".join(lines) if lines else "(no active quests)"
        focus = self.focus_quest()
        focus_txt = (f"The user's FOCUS quest right now: {focus.get('name', '')} "
                     f"({time_left_text(focus)})." if focus else "The user has not picked a focus quest.")
        return (
            "You are the AI sidekick inside procrastiNOT.exe, a gamified student productivity app. "
            "Your job is to help the user finish their quests faster by giving accurate, practical information: "
            "break tasks into small steps, explain concepts simply, make short time-boxed plans, point out what to "
            "search or read, and keep them moving. Be friendly and a little playful, use at most a couple of emojis, "
            "keep replies under about 150 words, and use plain text (no markdown tables or headings). "
            "If you are not sure about a fact, say so instead of guessing. Do not do dishonest work for the user "
            "(like writing an exam for them to submit as their own); help them learn and do it themselves.\n\n"
            f"{focus_txt}\nActive quests:\n{quests}\n"
            f"Player level: {self.xp // 100 + 1}." + self.ai_language_note()
        )

    def send_chat(self, text=None):
        if self.ai_busy:
            self.set_status("Sidekick is still thinking… ⏳", YELLOW)
            return
        if text is None:
            text = self.chat_input.text
            self.chat_input.text = ""
        text = (text or "").strip()
        if not text:
            return
        self.add_bubble(text, "user")
        self.ai_busy = True
        self.typing_label = self.add_bubble("▍▍▍ thinking…", "ai")
        self.chat_history.append({"role": "user", "content": text})
        self.chat_history = self.chat_history[-10:]
        while self.chat_history and self.chat_history[0]["role"] != "user":
            self.chat_history.pop(0)
        threading.Thread(
            target=self._ai_worker,
            args=(list(self.chat_history), self.ai_system_prompt(), text, self.focus_quest()),
            daemon=True,
        ).start()
        Clock.schedule_once(lambda dt: setattr(self.chat_input, "focus", True), 0.15)

    def _call_claude(self, messages, system):
        import urllib.request
        import urllib.error
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            return None, "nokey"
        payload = json.dumps({
            "model": AI_MODEL, "max_tokens": 500,
            "system": system, "messages": messages,
        }).encode("utf-8")
        req = urllib.request.Request(
            AI_URL, data=payload, method="POST",
            headers={"content-type": "application/json", "x-api-key": key,
                     "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text").strip()
            return (text or "…the sidekick went quiet. Try asking again."), None
        except urllib.error.HTTPError as err:
            self._note_err(err)
            return None, f"http{err.code}"
        except Exception as exc:
            self._note_err(exc)
            return None, "network"

    def _gemini_api_key(self):
        return self.gemini_key or BUILT_IN_GEMINI_KEY or os.environ.get("GEMINI_API_KEY", "")

    def _groq_api_key(self):
        return self.groq_key or BUILT_IN_GROQ_KEY or os.environ.get("GROQ_API_KEY", "")

    def active_provider(self):
        if self.api_key or os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if self._gemini_api_key():
            return "gemini"
        if self._groq_api_key():
            return "groq"
        return "offline"

    def _call_ai(self, messages, system):
        """Claude / Gemini / Groq depending on which key exists, otherwise report no key."""
        self.last_ai_error = ""
        prov = self.active_provider()
        if prov == "anthropic":
            return self._call_claude(messages, system)
        if prov == "gemini":
            return self._call_gemini(messages, system)
        if prov == "groq":
            return self._call_groq(messages, system)
        return None, "nokey"

    def _note_err(self, e):
        import urllib.error
        if isinstance(e, urllib.error.HTTPError):
            try:
                body = e.read().decode("utf-8", "replace")[:160].replace("\n", " ")
            except Exception:
                body = ""
            self.last_ai_error = f"HTTP {e.code} {body}".strip()
        else:
            self.last_ai_error = f"{type(e).__name__}: {str(e)[:140]}"

    def _http_json(self, url, payload=None, headers=None, timeout=40, method="POST"):
        """HTTP+JSON helper. Tries IPv4 first (fixes many Windows/Wi-Fi hangs), then the normal route."""
        import socket
        import urllib.request
        import urllib.error
        h = {"content-type": "application/json", "user-agent": "procrastiNOT/1.0"}
        if headers:
            h.update(headers)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None

        def go():
            req = urllib.request.Request(url, data=body, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))

        real = socket.getaddrinfo

        def v4_only(host, port, family=0, type=0, proto=0, flags=0):
            return real(host, port, socket.AF_INET, type, proto, flags)

        socket.getaddrinfo = v4_only
        try:
            return go()
        except urllib.error.HTTPError:
            raise
        except Exception:
            pass
        finally:
            socket.getaddrinfo = real
        try:
            return go()
        except urllib.error.HTTPError:
            raise
        except Exception as first_error:
            data = self._curl_json(url, body, h, timeout, method)
            if data is None:
                raise first_error
            return data

    def _curl_json(self, url, body, headers, timeout, method):
        """Last resort: Windows ships curl.exe, which can work when Python itself is blocked."""
        import subprocess
        import io
        import urllib.error
        if sys.platform != "win32":
            return None
        cmd = ["curl.exe", "-sS", "-m", str(int(timeout)), "-X", method, url]
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
        if body is not None:
            cmd += ["--data-binary", "@-"]
        try:
            proc = subprocess.run(cmd, input=body, capture_output=True,
                                  timeout=timeout + 5, creationflags=0x08000000)
        except Exception:
            return None
        if proc.returncode != 0 or not proc.stdout:
            return None
        try:
            data = json.loads(proc.stdout.decode("utf-8", "replace"))
        except ValueError:
            return None
        if isinstance(data, dict) and isinstance(data.get("error"), dict):
            err = data["error"]
            raise urllib.error.HTTPError(url, safe_int(err.get("code"), 400),
                                         str(err.get("message", ""))[:100], None,
                                         io.BytesIO(json.dumps(data).encode("utf-8")))
        return data

    def _gemini_candidates(self, key):
        """Ask Google which Flash models this key can use, newest first."""
        data = self._http_json(GEMINI_BASE + "/models?pageSize=100",
                               headers={"x-goog-api-key": key}, method="GET", timeout=15)
        bad = ("tts", "audio", "live", "embedding", "thinking",
               "robotics", "computer", "native", "learnlm")
        names = []
        for m in data.get("models", []):
            if "generateContent" not in (m.get("supportedGenerationMethods") or []):
                continue
            n = str(m.get("name", "")).replace("models/", "")
            low = n.lower()
            if "flash" not in low or any(b in low for b in bad):
                continue
            names.append(n)

        prefer = {
            "gemini-3-flash-preview": 0,
            "gemini-3.8-flash": 1,
            "gemini-flash-latest": 2,
            "gemini-2.5-flash-lite": 3,
            "gemini-2.5-flash": 4,
        }

        def rank(n):
            if n in prefer:
                return (0, prefer[n])
            ver = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
            return (2 if "lite" in n else 1, -(float(ver.group(1)) if ver else 0))

        return sorted(names, key=rank)

    def _call_gemini(self, messages, system):
        import urllib.error
        key = self._gemini_api_key()
        try:
            candidates = [self._gemini_model] if self._gemini_model else self._gemini_candidates(key)
        except urllib.error.HTTPError as err:
            self._note_err(err)
            return None, ("http401" if err.code in (400, 401) else f"http{err.code}")
        except Exception as exc:
            self._note_err(exc)
            return None, "network"
        if not candidates:
            candidates = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
        contents = [{"role": "user" if m["role"] == "user" else "model",
                     "parts": [{"text": m["content"]}]} for m in messages]
        payload = {"systemInstruction": {"parts": [{"text": system}]},
                   "contents": contents,
                   "generationConfig": {"maxOutputTokens": 1024}}
        last = "network"
        for model in candidates[:4]:
            try:
                data = self._http_json(f"{GEMINI_BASE}/models/{model}:generateContent", payload,
                                       {"x-goog-api-key": key}, timeout=35)
                parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
                text = "".join(p.get("text", "") for p in parts).strip()
                self._gemini_model = model
                return (text or "…the sidekick went quiet. Try asking again."), None
            except urllib.error.HTTPError as err:
                self._note_err(err)
                if err.code == 401 or "API_KEY_INVALID" in self.last_ai_error or "not valid" in self.last_ai_error:
                    return None, "http401"
                last = f"http{err.code}"
                continue
            except Exception as exc:
                self._note_err(exc)
                return None, "network"
        return None, last

    def _call_groq(self, messages, system):
        import urllib.error
        key = self._groq_api_key()
        auth = {"authorization": "Bearer " + key}
        try:
            model = self._groq_model
            if not model:
                data = self._http_json(GROQ_BASE + "/models", headers=auth, method="GET", timeout=15)
                ids = [m.get("id", "") for m in data.get("data", [])]
                for pref in ("llama-3.3-70b-versatile", "llama-3.1-8b-instant"):
                    if pref in ids:
                        model = pref
                        break
                if not model:
                    chat = [i for i in ids if "llama" in i and
                            not any(b in i for b in ("guard", "whisper", "tts", "vision"))]
                    model = chat[0] if chat else ""
                if not model:
                    return None, "http404"
            payload = {"model": model, "max_tokens": 500,
                       "messages": [{"role": "system", "content": system}] + messages}
            data = self._http_json(GROQ_BASE + "/chat/completions", payload, auth, timeout=60)
            text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
            self._groq_model = model
            return (text or "…the sidekick went quiet. Try asking again."), None
        except urllib.error.HTTPError as err:
            self._note_err(err)
            return None, f"http{err.code}"
        except Exception as exc:
            self._note_err(exc)
            return None, "network"

    def _ai_worker(self, messages, system, text, quest):
        reply, err = self._call_ai(messages, system)
        self._ai_done(reply, err, text, quest)

    @mainthread
    def _ai_done(self, reply, err, text, quest):
        self.ai_busy = False
        if reply is None:
            notes = {
                "http401": "🔑 Your API key was rejected. Check it in ⚙️ SETTINGS. Offline helper:\n\n",
                "http429": "🐢 AI is rate-limited right now (free tiers have limits). Offline helper:\n\n",
                "http403": "🔒 The AI provider refused this key or project. Check the key in ⚙️ SETTINGS. Offline helper:\n\n",
                "http404": "🧭 No usable model found for this key. Offline helper:\n\n",
                "network": "📡 Can't reach the AI right now. Offline helper:\n\n",
            }
            note = ""
            if err == "nokey":
                if not self._offline_noted:
                    note = ("🔌 AI isn't connected yet. Add a free key in ⚙️ SETTINGS (or in BUILT_IN_GEMINI_KEY "
                            "at the top of main.py), or use the 🔎 ✨ 💬 buttons below. For now, offline helper:\n\n")
                    self._offline_noted = True
            else:
                note = notes.get(err, "⚠️ AI hiccup. Offline helper:\n\n")
            detail = ("[" + self.last_ai_error + "]\n\n") if self.last_ai_error else ""
            reply = note + detail + self.offline_reply(text, quest)
        reply = reply.replace("**", "")
        self.typing_label.text = reply
        self.chat_history.append({"role": "assistant", "content": reply})
        self.chat_history = self.chat_history[-10:]
        self._scroll_chat()
        self.update_ai_mode()

    def offline_reply(self, text, quest):
        t = text.lower()
        name = quest.get("name") if quest else None
        label = f"“{name}”" if name else "your top quest"
        if any(k in t for k in ("break", "step", "start", "where do i")):
            return (f"🪜 Mini-plan for {label}:\n"
                    "1) 2 min: open what you need, close everything else.\n"
                    "2) 5 min: write the 3 smallest steps.\n"
                    "3) 25 min: do step 1 only. Timer on.\n"
                    "4) 5 min break, then step 2.\n"
                    "Tap ⏱️ FOCUS above to start the clock.")
        if "plan" in t or "25" in t:
            return (f"⏱️ 25-minute sprint for {label}:\n"
                    "0-3 min: set up + write the goal in one line.\n"
                    "3-20 min: work on ONE thing, no tabs.\n"
                    "20-25 min: tidy up and write the next step.\n"
                    "Then take a real break.")
        if any(k in t for k in ("explain", "what is", "how do", "how to", "learn", "understand")):
            return (f"💡 Fast-learn loop for {label}:\n"
                    "1) Skim headings for 3 min.\n"
                    "2) Explain it out loud like to a 10 year old.\n"
                    "3) Note what you couldn't explain.\n"
                    "4) Search ONLY those gaps.\n"
                    "For real explanations, add an API key in ⚙️ SETTINGS 🔑")
        if any(k in t for k in ("motivat", "pep", "lazy", "tired", "procrastinat", "stuck", "can't")):
            return random.choice([
                "🔥 You don't need motivation, you need 2 minutes. Start the tiny version and let momentum do the rest.",
                "🚀 Future-you is watching. Do 5 minutes now and decide after if you want to stop. You won't.",
                "😤 The task is smaller than the dread. Open it, do one line, claim the XP.",
            ])
        return (f"🧠 I can break {label} into steps, make a 25-min plan, or coach you through it. "
                "Hit a chip below! (Real AI answers need an API key in ⚙️ SETTINGS.)")

    def update_ai_mode(self):
        prov = self.active_provider()
        names = {"anthropic": "Claude (" + AI_MODEL + ")",
                 "gemini": "Google Gemini (free tier)", "groq": "Groq (free tier)"}
        if prov in names:
            mode, color = "🟢 AI ONLINE // " + names[prov], GREEN
            built_in = (prov == "gemini" and not self.gemini_key and BUILT_IN_GEMINI_KEY) or \
                       (prov == "groq" and not self.groq_key and BUILT_IN_GROQ_KEY)
            state = ("✅ Built-in AI is on. Nothing to set up." if built_in
                     else "✅ Using " + names[prov] + ".")
        else:
            mode, color = "🟡 OFFLINE HELPER // AI key not set (see ⚙️ SETTINGS)", YELLOW
            state = "⚠️ No AI key yet. The offline helper is active."
        if hasattr(self, "ai_mode_label"):
            self.ai_mode_label.text = mode
            self.ai_mode_label.color = color
        if hasattr(self, "key_state_label"):
            self.key_state_label.text = state

    def _on_provider_pick(self, _spinner, text):
        self.key_help_label.text = KEY_HELP.get(PROVIDER_CHOICES.get(text, "gemini"), "")

    def save_api_key(self, *_):
        key = self.key_input.text.strip()
        if not key:
            self.set_status("Paste a key first. 🔑", YELLOW)
            self.play_sound("error")
            return
        prov = PROVIDER_CHOICES.get(self.provider_spinner.text, "gemini")
        if prov == "gemini":
            self.gemini_key = key
            self._gemini_model = ""
        elif prov == "groq":
            self.groq_key = key
            self._groq_model = ""
        else:
            self.api_key = key
        self.key_input.text = ""
        self.save_data()
        self.update_ai_mode()
        self.set_mascot("🤖")
        self.set_status("AI key saved. Sidekick is online. 🤖", GREEN)
        self.play_sound("success")

    def clear_api_key(self, *_):
        prov = PROVIDER_CHOICES.get(self.provider_spinner.text, "gemini")
        if prov == "gemini":
            self.gemini_key = ""
            self._gemini_model = ""
        elif prov == "groq":
            self.groq_key = ""
            self._groq_model = ""
        else:
            self.api_key = ""
        self.save_data()
        self.update_ai_mode()
        self.set_status("Key cleared for that provider. 🔌", CYAN)

    def test_ai(self, *_):
        self.key_state_label.text = "⏳ Testing AI connection… (up to ~40 seconds)"
        threading.Thread(target=self._test_worker, daemon=True).start()

    def _test_worker(self):
        reply, err = self._call_ai(
            [{"role": "user", "content": "Reply with exactly: AI READY"}],
            "You are a connection test. Reply with exactly the words requested.")
        self._test_done(reply, err, self.last_ai_error)

    @mainthread
    def _test_done(self, reply, err, detail):
        if reply:
            text = "✅ AI works! It replied: " + reply[:60]
        else:
            text = f"❌ Failed ({err}). {detail}"
        self.key_state_label.text = text
        self.set_status(text[:110], GREEN if reply else RED)

    def open_web(self, which):
        """No key needed: copy a ready prompt to the clipboard and open Google / an AI website."""
        import webbrowser
        import urllib.parse
        focus = self.focus_quest()
        typed = self.chat_input.text.strip()
        topic = typed or (focus.get("name") if focus else "") or "how to stop procrastinating"
        prompt = (f"Help me finish this task: {topic}. Break it into small steps, explain anything I need "
                  "to know, and give me a realistic 25 minute plan.") if (typed or focus) else \
                 "Give me practical tips to stop procrastinating and start my study session."
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(prompt)
        except Exception:
            pass
        enc = urllib.parse.quote(prompt)
        urls = {
            "google": "https://www.google.com/search?q=" + urllib.parse.quote(topic),
            "gemini": "https://gemini.google.com/app",
            "chatgpt": "https://chatgpt.com/?q=" + enc,
            "claude": "https://claude.ai/new?q=" + enc,
        }
        try:
            webbrowser.open(urls[which])
        except Exception:
            pass
        self.set_status("Opened in your browser. 📋 Prompt copied: press Ctrl+V if it isn't filled in.", GREEN)
        self.play_sound("success")

    # ---------- focus timer ----------

    def toggle_focus(self, *_):
        if self.focus_ev is not None:
            self.focus_ev.cancel()
            self.focus_ev = None
            self.focus_end = None
            self.focus_btn.text = "⏱️ 25:00 FOCUS"
            self.set_status("Focus sprint cancelled. It happens. 😮‍💨", YELLOW)
            return
        self.focus_end = datetime.now() + timedelta(minutes=25)
        self.focus_ev = Clock.schedule_interval(self._focus_tick, 1)
        self._focus_tick(0)
        self.set_mascot("🧠")
        self.set_status("Focus sprint started. 25 minutes. Phone away. 📵", GREEN)

    def _focus_tick(self, _dt):
        if self.focus_end is None:
            return False
        remaining = int((self.focus_end - datetime.now()).total_seconds())
        if remaining <= 0:
            self.focus_ev = None
            self.focus_end = None
            self.focus_btn.text = "⏱️ 25:00 FOCUS"
            previous_level = self.xp // 100 + 1
            self.xp += 10
            self.save_data()
            self.refresh_screen()
            extra = ""
            if self.xp // 100 + 1 > previous_level:
                extra = f"\n\n✨ LEVEL UP — LEVEL {self.xp // 100 + 1}! ✨"
            self.show_celebration("⏱️ FOCUS SPRINT COMPLETE!\n+10 XP for staying locked in 🔒" + extra)
            self.emoji_rain(["⏱️", "🧠", "✨", "⭐", "🔥"], 24)
            self.play_sound("success")
            return False
        mm, ss = divmod(remaining, 60)
        self.focus_btn.text = f"⏳ {mm:02d}:{ss:02d} (STOP)"
        return True

    # ---------- mascot + effects ----------

    def idle_mascot(self):
        return "😬" if any(is_overdue(m) for m in self.missions) else "😎"

    def set_mascot(self, emoji, revert=True):
        if not hasattr(self, "mascot_label"):
            return
        self.mascot_label.text = emoji
        base = getattr(self, "_mascot_base", None)
        if base is None:
            base = self._mascot_base = self.mascot_label.font_size
        Animation.cancel_all(self.mascot_label, "font_size")
        self.mascot_label.font_size = base
        (Animation(font_size=base * 1.35, d=0.12, t="out_quad")
         + Animation(font_size=base, d=0.3, t="out_bounce")).start(self.mascot_label)
        if self._mascot_event is not None:
            self._mascot_event.cancel()
            self._mascot_event = None
        if revert:
            self._mascot_event = Clock.schedule_once(self._mascot_back, 4)

    def _mascot_back(self, _dt):
        self._mascot_event = None
        self.mascot_label.text = self.idle_mascot()

    def emoji_rain(self, emojis, count=28):
        """Emoji that rain down over the whole window."""
        layer = FloatLayout(size_hint=(1, 1))
        Window.add_widget(layer)
        for _ in range(count):
            piece = TechLabel(
                text=random.choice(emojis),
                font_size=f"{random.randint(22, 38)}sp",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos=(random.uniform(0, max(1, Window.width - dp(40))), Window.height + dp(40)),
            )
            layer.add_widget(piece)
            anim = Animation(
                y=-dp(60),
                x=piece.x + random.uniform(-dp(60), dp(60)),
                duration=random.uniform(1.4, 2.6),
                t="in_quad",
            )
            Clock.schedule_once(lambda dt, p=piece, a=anim: a.start(p), random.uniform(0, 0.6))
        Clock.schedule_once(lambda dt: Window.remove_widget(layer), 3.6)

    # ---------- fun text ----------

    def show_random_roast(self):
        """Show a playful, non-persistent sidekick line."""
        lines = [
            "Your to-do list called. It said: bestie, be so for real. 📞",
            "Main character energy. Side quest completion still pending. 🎭",
            "You opened the app. That's a start. The bar is on the floor, respectfully. 🪦",
            "Today's forecast: 20% productivity, 80% dramatic comeback potential. 🌦️",
            "Hydrate, pick one quest, and stop negotiating with the deadline. 💧",
            "Plot twist: doing the tiny task takes less time than avoiding it. 🌀",
        ]
        if hasattr(self, "chaos_label"):
            self.chaos_label.text = random.choice(lines)

    def generate_excuse(self, *_):
        excuses = [
            "I was waiting for the task to align with my zodiac sign. ♈",
            "My productivity left me on read. 📵",
            "I needed to emotionally prepare the cursor for this journey. 🖱️",
            "The vibes were buffering. Please respect the process. 🔄",
            "I opened one tab and accidentally entered a side quest. 🗺️",
            "I was letting the deadline marinate for maximum flavour. 🍝",
            "My brain scheduled a meeting about starting the task. No minutes were taken. 🗓️",
            "I was conducting important research on absolutely unrelated things. 🔬",
        ]
        if hasattr(self, "chaos_label"):
            self.chaos_label.text = random.choice(excuses)
        if hasattr(self, "roast_face"):
            self.roast_face.text = random.choice(["🎭", "🤥", "🧐", "🙃", "🤡"])
        self.set_mascot("🤥")
        self.set_status("EXCUSE GENERATED. The court will hear your case. 💀", PURPLE)
        self.play_sound("click")

    def roast_me(self, *_):
        roasts = [
            "Your deadline has a countdown. You have a collection of excuses. ⏳",
            "Bestie, your to-do list is starting to qualify as historical fiction. 📚",
            "You said ‘five minutes’ so long ago the calendar filed a missing-person report. 🕵️",
            "The task is not scary. The dramatic soundtrack in your head is. 🎻",
            "Your potential is online. Your productivity is on airplane mode. ✈️",
            "Respectfully, stop side-questing and do one tiny thing. 😭",
            "The procrastination lore is getting a little too much screen time. 📺",
        ]
        line = random.choice(roasts)
        self.chaos_label.text = line
        self.roast_face.text = random.choice(["😈", "💀", "😭", "🫠", "👀", "🔥"])
        self.set_mascot("😈")
        self.set_status("ROAST DELIVERED. Emotional damage: motivational. 💀", PINK)
        self.play_sound("click")

    def generate_daily_challenge(self, *_):
        challenges = [
            "📵 Focus for 10 minutes. Phone gets zero screen time.",
            "🧹 Clear one tiny task you've been avoiding.",
            "🧠 Revise one concept and explain it in your own words.",
            "🪴 Tidy your study space for 5 minutes.",
            "💧 Drink water, stretch, then start one task.",
            "📖 Read two pages or review five flashcards.",
            "🧩 Break a big assignment into three tiny steps.",
            "🎧 Put your phone away and work until one song ends.",
            "🗓️ Organise tomorrow's top three priorities.",
            "☕ Take a proper short break, then do one focused sprint.",
        ]
        self.daily_challenge = random.choice(challenges)
        self.daily_challenge_date = today_key()
        if hasattr(self, "daily_challenge_label"):
            self.daily_challenge_label.text = self.daily_challenge
        self.save_data()
        self.update_accept_button()

    def daily_accepted(self):
        name = "Daily challenge: " + self.daily_challenge
        return any(m.get("name") == name and m.get("created") == today_key() for m in self.missions)

    def update_accept_button(self):
        if not hasattr(self, "accept_btn"):
            return
        if self.daily_accepted():
            self.accept_btn.text = "✅ ACCEPTED — NOW GO CLEAR IT"
            self.accept_btn.set_bg((0.18, 0.22, 0.32, 1))
        else:
            self.accept_btn.text = "⚔️ ACCEPT CHALLENGE (+25 XP)"
            self.accept_btn.set_bg((0.08, 0.38, 0.30, 1))

    def best_streak(self):
        days = set()
        for item in self.completed_dates:
            try:
                days.add(date.fromisoformat(item))
            except (ValueError, TypeError):
                pass
        best = 0
        for d in days:
            if d - timedelta(days=1) not in days:
                run = 1
                while d + timedelta(days=run) in days:
                    run += 1
                best = max(best, run)
        return best

    def add_daily_challenge(self, *_):
        if not self.daily_challenge:
            self.generate_daily_challenge()
        if self.daily_accepted():
            self.set_status("Already accepted today. 🎲 REROLL for a new one, or go clear this one! 😤", YELLOW)
            self.play_sound("error")
            return
        self.missions.append({
            "name": "Daily challenge: " + self.daily_challenge,
            "done": False,
            "priority": "Normal",
            "deadline": today_key(),
            "due_at": end_of_day(date.today()).isoformat(),
            "created": today_key(),
            "roast_shown": False,
        })
        self.save_data()
        self.refresh_screen()
        self.set_mascot("😅")
        self.set_status("Challenge accepted! ⚔️ It is in your Missions, due tonight. No escaping now. 😭", GREEN)
        self.play_sound("success")

    # ---------- badges ----------

    def badge_defs(self):
        completed = sum(1 for m in self.missions if m.get("done", False))
        streak = self.current_streak()
        xp = getattr(self, "xp", 0)
        mood_count = len(getattr(self, "mood_logs", []))
        habits = getattr(self, "habits", [])
        focus_sprints = getattr(self, "focus_sprints", 0)
        scores = getattr(self, "arcade_scores", {})
        has_companion = bool(getattr(self, "selected_companion", ""))
        has_proof = any(bool(m.get("proof") or m.get("proof_verified")) for m in self.missions)
        has_quick = any(m.get("id", "").startswith("q_") for m in self.missions)

        t_str = datetime.now().strftime("%Y-%m-%d")
        habits_checked = sum(1 for h in habits if t_str in h.get("history", []))
        any_habit_ever = any(len(h.get("history", [])) > 0 for h in habits)
        shield_maxed = (len(habits) > 0 and habits_checked == len(habits))
        custom_habits = max(0, len(habits) - 5)
        arcade_played = any(v > 0 for v in scores.values())
        neon_score = scores.get("neon_dodge", 0)
        pop_score = scores.get("pixel_pop", 0)
        breaker_score = scores.get("cyber_breaker", 0)

        return [
            # --- 1. MISSIONS CATEGORY (7 badges) ---
            ("🌱 First Quest", "Clear your first mission directive", completed >= 1, "missions", "COMMON", f"{min(completed, 1)}/1 cleared", min(completed, 1)/1.0, 20),
            ("⚡ Quest Gremlin (5)", "Clear 5 mission directives", completed >= 5, "missions", "COMMON", f"{min(completed, 5)}/5 cleared", min(completed, 5)/5.0, 50),
            ("🔥 Double Digits (10)", "Clear 10 mission directives", completed >= 10, "missions", "RARE", f"{min(completed, 10)}/10 cleared", min(completed, 10)/10.0, 100),
            ("👑 Main Character (25)", "Clear 25 mission directives", completed >= 25, "missions", "EPIC", f"{min(completed, 25)}/25 cleared", min(completed, 25)/25.0, 250),
            ("🪐 Century Operative (50)", "Clear 50 mission directives across all sectors", completed >= 50, "missions", "LEGENDARY", f"{min(completed, 50)}/50 cleared", min(completed, 50)/50.0, 500),
            ("🚀 Speed Deployer", "Quick-deploy a mission from Command Deck terminal", has_quick or completed >= 1, "missions", "COMMON", "1/1 deployed" if (has_quick or completed >= 1) else "0/1 deployed", 1.0 if (has_quick or completed >= 1) else 0.0, 25),
            ("📸 Cryptographic Proof", "Submit proof verification confirmed by the AI neural verifier", has_proof, "missions", "RARE", "1/1 verified" if has_proof else "0/1 verified", 1.0 if has_proof else 0.0, 75),

            # --- 2. XP & PRESTIGE CATEGORY (5 badges) ---
            ("💎 Level Up", "Reach 100 XP and advance to Level 2", xp >= 100, "xp", "COMMON", f"{min(xp, 100)}/100 XP", min(xp, 100)/100.0, 50),
            ("🚀 XP Machine", "Accumulate 500 total XP", xp >= 500, "xp", "RARE", f"{min(xp, 500)}/500 XP", min(xp, 500)/500.0, 100),
            ("🔮 Neural Elite", "Accumulate 1,000 total XP", xp >= 1000, "xp", "EPIC", f"{min(xp, 1000)}/1000 XP", min(xp, 1000)/1000.0, 250),
            ("👑 Cyber Legend", "Accumulate 2,500 total XP", xp >= 2500, "xp", "LEGENDARY", f"{min(xp, 2500)}/2500 XP", min(xp, 2500)/2500.0, 500),
            ("🌌 Digital Transcendent", "Accumulate 5,000 total XP and achieve supreme mastery", xp >= 5000, "xp", "LEGENDARY", f"{min(xp, 5000)}/5000 XP", min(xp, 5000)/5000.0, 1000),

            # --- 3. STREAKS CATEGORY (4 badges) ---
            ("📆 3-Day Streak", "Clear quests 3 days in a row", streak >= 3, "streaks", "COMMON", f"{min(streak, 3)}/3 days", min(streak, 3)/3.0, 30),
            ("⚔️ Full Week Dominance", "Maintain a 7-day consecutive activity streak", streak >= 7, "streaks", "RARE", f"{min(streak, 7)}/7 days", min(streak, 7)/7.0, 100),
            ("🛡️ Fortress of Habit", "Maintain a 14-day consecutive activity streak", streak >= 14, "streaks", "EPIC", f"{min(streak, 14)}/14 days", min(streak, 14)/14.0, 250),
            ("🔥 Monthly Overlord", "Maintain an unbroken 30-day activity streak", streak >= 30, "streaks", "LEGENDARY", f"{min(streak, 30)}/30 days", min(streak, 30)/30.0, 500),

            # --- 4. FOCUS & HABITS CATEGORY (6 badges) ---
            ("⏱️ Focus Initiate", "Complete a Deep Focus sprint in the Focus Chamber", focus_sprints >= 1, "focus", "COMMON", f"{min(focus_sprints, 1)}/1 sprint", min(focus_sprints, 1)/1.0, 50),
            ("🧠 Flow State Master", "Complete 5 Deep Focus sprints", focus_sprints >= 5, "focus", "RARE", f"{min(focus_sprints, 5)}/5 sprints", min(focus_sprints, 5)/5.0, 150),
            ("⚡ Hyperfocus Vanguard", "Complete 15 Deep Focus sprints", focus_sprints >= 15, "focus", "EPIC", f"{min(focus_sprints, 15)}/15 sprints", min(focus_sprints, 15)/15.0, 300),
            ("💧 Discipline Spark", "Check off a routine in the Cyber Habit Matrix", any_habit_ever, "focus", "COMMON", "1/1 checked" if any_habit_ever else "0/1 checked", 1.0 if any_habit_ever else 0.0, 30),
            ("🛡️ Ironclad Armor", "Achieve 100% daily discipline armor shield", shield_maxed, "focus", "RARE", f"{habits_checked}/{len(habits)} habits" if habits else "0/0 habits", (habits_checked/len(habits)) if habits else 0.0, 100),
            ("🛠️ Routine Architect", "Forge a custom routine directive in Habit Matrix", custom_habits >= 1, "focus", "COMMON", f"{min(custom_habits, 1)}/1 forged", min(custom_habits, 1)/1.0, 50),

            # --- 5. ARCADE CATEGORY (4 badges) ---
            ("🕹️ Arcade Tourist", "Play any Mind Reset Arcade game", arcade_played, "arcade", "COMMON", "1/1 played" if arcade_played else "0/1 played", 1.0 if arcade_played else 0.0, 25),
            ("⚡ Kinetic Evader", "Score 50+ in Neon Dodge", neon_score >= 50, "arcade", "RARE", f"{min(neon_score, 50)}/50 pts", min(neon_score, 50)/50.0, 50),
            ("🎯 Reflex Overdrive", "Score 150+ in Pixel Pop Blitz", pop_score >= 150, "arcade", "RARE", f"{min(pop_score, 150)}/150 pts", min(pop_score, 150)/150.0, 50),
            ("🧱 Firewall Smasher", "Score 200+ in Cyber Breaker", breaker_score >= 200, "arcade", "RARE", f"{min(breaker_score, 200)}/200 pts", min(breaker_score, 200)/200.0, 50),

            # --- 6. COMPANION & BIOMETRICS (2 badges) ---
            ("🫶 Mood Check-In Pro", "Log 5 biometric states in Mood Lab", mood_count >= 5, "biometrics", "COMMON", f"{min(mood_count, 5)}/5 moods", min(mood_count, 5)/5.0, 40),
            ("🤖 Neural Link Established", "Assign a Cyber Companion operator", has_companion, "biometrics", "COMMON", "1/1 linked" if has_companion else "0/1 linked", 1.0 if has_companion else 0.0, 30),
        ]

    def unlocked_achievements(self):
        return [b[0] for b in self.badge_defs() if b[2]]

    def make_stat_card(self, value, caption, color):
        card = NeonPanel(
            orientation="vertical",
            padding=[dp(12), dp(6)],
            spacing=dp(1),
            bg_color=BG_ELEVATED,
            border_color=SEPARATOR,
        )
        value_label = make_label(
            value, 18, color, True, size_hint_y=None, height=dp(26)
        )
        caption_label = make_label(
            caption, 9, MUTED, True, size_hint_y=None, height=dp(18)
        )
        card.add_widget(value_label)
        card.add_widget(caption_label)
        card.value_label = value_label
        return card

    def set_status(self, message, color=GREEN):
        self.status_message = message
        self.log_lines.append(f"[{datetime.now():%H:%M:%S}] {message}")
        self.log_lines = self.log_lines[-6:]
        if hasattr(self, "status_label"):
            self.status_label.text = "SYS> " + message
            self.status_label.color = color
        if hasattr(self, "log_label"):
            self.log_label.text = "\n".join(self.log_lines)

    # ---------- saving / loading ----------

    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.xp = max(0, safe_int(data.get("xp", 0)))
            self.missions = data.get("missions", [])
            self.mood_logs = data.get("mood_logs", [])
            self.completed_dates = data.get("completed_dates", [])
            self.sound_enabled = data.get("sound_enabled", True)
            self.achievements = data.get("achievements", [])
            self.daily_challenge_date = data.get("daily_challenge_date", "")
            self.daily_challenge = data.get("daily_challenge", "")
            self.api_key = str(data.get("api_key", "") or "")
            self.gemini_key = str(data.get("gemini_key", "") or "")
            self.groq_key = str(data.get("groq_key", "") or "")
            self.selected_companion = str(data.get("selected_companion", "") or "")
            self.arcade_scores = data.get("arcade_scores", {"neon_dodge": 0, "pixel_pop": 0, "memory_glitch": 1})
            if not isinstance(self.arcade_scores, dict):
                self.arcade_scores = {"neon_dodge": 0, "pixel_pop": 0, "memory_glitch": 1}
            self.unlocked_themes = data.get("unlocked_themes", ["cyberpunk"])
            self.current_theme = data.get("current_theme", "cyberpunk")
            self.equipped_title = data.get("equipped_title", "NOVICE OPERATOR")
            self.unlocked_titles = data.get("unlocked_titles", ["NOVICE OPERATOR"])
            self.habits = data.get("habits", [])
            if not isinstance(self.habits, list):
                self.habits = []
            self.focus_sprints = max(0, safe_int(data.get("focus_sprints", 0)))
            self.load_online(data)
            if not isinstance(self.achievements, list):
                self.achievements = []
            if not isinstance(self.missions, list):
                self.missions = []
            if not isinstance(self.mood_logs, list):
                self.mood_logs = []
            if not isinstance(self.completed_dates, list):
                self.completed_dates = []
        except (OSError, json.JSONDecodeError, TypeError):
            self.xp, self.missions, self.mood_logs, self.completed_dates = 0, [], [], []
            self.achievements, self.daily_challenge_date, self.daily_challenge = [], "", ""
            self.api_key = ""
            self.gemini_key = ""
            self.groq_key = ""
            self.arcade_scores = {"neon_dodge": 0, "pixel_pop": 0, "memory_glitch": 1}

    def try_import_legacy_save(self):
        """Look for the old ProjectXApp save if the new save is empty."""
        if self.xp or self.missions or self.mood_logs:
            return
        candidates = []
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.extend([
                os.path.join(appdata, "projectx", "projectx_data.json"),
                os.path.join(appdata, "ProjectX", "projectx_data.json"),
            ])
        home = os.path.expanduser("~")
        candidates.append(os.path.join(home, ".kivy", "projectx_data.json"))
        for candidate in candidates:
            if os.path.abspath(candidate) == os.path.abspath(self.data_file):
                continue
            try:
                with open(candidate, "r", encoding="utf-8") as file:
                    old = json.load(file)
                self.xp = max(self.xp, safe_int(old.get("xp", 0)))
                old_missions = old.get("missions", [])
                if isinstance(old_missions, list):
                    self.missions = old_missions
                self.save_data()
                break
            except (OSError, json.JSONDecodeError, TypeError):
                continue

    def save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            "xp": self.xp,
            "missions": self.missions,
            "mood_logs": self.mood_logs,
            "completed_dates": self.completed_dates,
            "sound_enabled": self.sound_enabled,
            "achievements": getattr(self, "achievements", []),
            "daily_challenge_date": getattr(self, "daily_challenge_date", ""),
            "daily_challenge": getattr(self, "daily_challenge", ""),
            "api_key": getattr(self, "api_key", ""),
            "gemini_key": getattr(self, "gemini_key", ""),
            "groq_key": getattr(self, "groq_key", ""),
            "selected_companion": getattr(self, "selected_companion", ""),
            "arcade_scores": getattr(self, "arcade_scores", {}),
            "unlocked_themes": getattr(self, "unlocked_themes", ["cyberpunk"]),
            "current_theme": getattr(self, "current_theme", "cyberpunk"),
            "equipped_title": getattr(self, "equipped_title", "NOVICE OPERATOR"),
            "unlocked_titles": getattr(self, "unlocked_titles", ["NOVICE OPERATOR"]),
            "habits": getattr(self, "habits", []),
            "focus_sprints": getattr(self, "focus_sprints", 0),
        }
        data.update(self.online_save_fields())
        temp_file = self.data_file + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        try:
            os.replace(temp_file, self.data_file)
        except OSError:
            try:
                time.sleep(0.03)
                os.replace(temp_file, self.data_file)
            except OSError:
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
        self.schedule_sync()
        if hasattr(self, "sync_to_firestore_async"):
            self.sync_to_firestore_async()

    def play_sound(self, kind="click"):
        if not self.sound_enabled:
            return
        # Tiny optional Windows beeps; app still works if sound is unavailable.
        if sys.platform == "win32":
            try:
                import winsound
                if kind == "success":
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                elif kind == "error":
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                else:
                    winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

    def toggle_sound(self, *_):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.sound_button.text = "🔊 SOUND: ONLINE [ON]"
            self.sound_button.variant = "mint"
            self.sound_button.set_bg((0.08, 0.40, 0.28, 1))
        else:
            self.sound_button.text = "🔇 SOUND: MUTED [OFF]"
            self.sound_button.variant = "secondary"
            self.sound_button.set_bg((0.28, 0.14, 0.20, 1))
        self.save_data()
        self.set_status("Sound enabled. 🔊" if self.sound_enabled else "Sound muted. 🔇", CYAN)
        self.play_sound("click")

    # ---------- mood ----------

    def update_mood_selection(self):
        for option in getattr(self, "mood_options", []):
            option.update_selected()

    def log_mood(self, *_):
        mood = self.selected_mood
        if not mood:
            self.set_status("Choose a mood first, commander. 🫡", YELLOW)
            self.play_sound("error")
            return
        icon_emoji = {"Focused": "😎", "Good": "😊", "Okay": "😐", "Stressed": "😵", "Tired": "😴", "Low": "😔"}.get(mood, "")
        mood_to_save = f"{icon_emoji} {mood}".strip()
        self.mood_logs.append({"date": today_key(), "mood": mood_to_save})
        self.save_data()
        self.set_mascot("🫶")
        self.set_status(random.choice(["Mood logged. Feelings: documented. Drama: optional. 📝", "Mood saved. We support character development here. 🌱", "Emotional side quest complete. Be nice to yourself, bestie. 💖"]), GREEN)
        self.play_sound("success")
        self.refresh_screen()

    # ---------- missions ----------

    def add_mission(self, *_):
        name = self.mission_input.text.strip()
        deadline = self.deadline_input.text.strip()
        priority = self.priority_spinner.text

        if not name:
            self.set_status("Quest missing. Type a mission name first. ✍️", YELLOW)
            self.play_sound("error")
            return

        if deadline:
            try:
                d = date.fromisoformat(deadline)
            except ValueError:
                self.set_status("Date format should be YYYY-MM-DD. 📅", YELLOW)
                self.play_sound("error")
                return
            # A chosen date is due at the very end of that day.
            due_at = end_of_day(d)
        else:
            # No deadline entered? Give the quest exactly 24 hours from now.
            due_at = (datetime.now() + timedelta(days=1)).replace(microsecond=0)
            deadline = due_at.date().isoformat()

        criteria = self.criteria_input.text.strip() if hasattr(self, "criteria_input") else ""
        self.missions.append({
            "name": name,
            "criteria": criteria,
            "done": False,
            "priority": priority,
            "deadline": deadline,
            "due_at": due_at.isoformat(timespec="seconds"),
            "created": today_key(),
            "roast_shown": False,
        })
        self.mission_input.text = ""
        self.deadline_input.text = ""
        if hasattr(self, "criteria_input"):
            self.criteria_input.text = ""
        self.save_data()
        self.set_mascot("🫡")
        self.set_status(random.choice(["Quest added. Procrastination has been formally notified. 📨", "New quest unlocked. The avoidance arc is under investigation. 🕵️", "Task entered the chat. You have been perceived. 👁️"]), GREEN)
        self.play_sound("success")
        self.refresh_screen()
        if hasattr(self, "companion_widget") and self.companion_widget:
            self.companion_widget.on_game_event("quest_started")

    def check_first_launch_companion(self):
        if not getattr(self, "selected_companion", ""):
            self.open_companion_selector(force=False)

    def open_companion_selector(self, force=False):
        modal = companion.OperatorSelectModal(
            app=self,
            on_selected_cb=self.set_selected_companion
        )
        modal.open()

    def set_selected_companion(self, char_id):
        self.selected_companion = char_id
        self.save_data()
        if hasattr(self, "companion_widget") and self.companion_widget:
            self.companion_widget.load_companion(char_id, is_first=False)
        self.set_status(f"OPERATOR {char_id.upper()} DEPLOYED // READY", MINT)
        self.play_sound("success")
        if hasattr(self, "companion_settings_btn") and self.companion_settings_btn:
            info = companion.OPERATORS.get(char_id, {})
            self.companion_settings_btn.text = f"SWITCH OPERATOR: {info.get('name', char_id.upper())}"

    def open_proof_verification(self, index):
        if index < 0 or index >= len(self.missions):
            return
        mission = self.missions[index]
        if mission.get("done", False):
            self.set_status("This quest is already cleared. 🏆", MINT)
            return
        modal = QuestProofModal(app=self, mission_index=index, mission=mission)
        modal.open()

    def claim_verified_mission(self, index, verdict_data=None):
        if index < 0 or index >= len(self.missions):
            return
        mission = self.missions[index]
        if mission.get("done", False):
            return
        if verdict_data:
            mission["proof_verified"] = True
            mission["proof_verdict"] = verdict_data.get("verdict", "approved")
            mission["proof_reason"] = verdict_data.get("reason", "")
            mission["proof_confidence"] = verdict_data.get("confidence", 1.0)
            mission["proof_evidence"] = verdict_data.get("evidence_found", [])
            mission["proof_timestamp"] = datetime.now().isoformat()
            mission["proof_model"] = verdict_data.get("model_used", "")
        self.complete_mission(index, bypass_proof_check=True)

    def complete_mission(self, index, bypass_proof_check=False):
        if index < 0 or index >= len(self.missions):
            return
        mission = self.missions[index]
        if mission.get("done", False):
            return
        if not bypass_proof_check and not mission.get("proof_verified"):
            self.set_status("⚠️ PROOF COMPULSION ACTIVE: Photographic proof required to clear this quest!", YELLOW)
            self.open_proof_verification(index)
            return
        mission["done"] = True
        mission["completed_date"] = today_key()
        self.xp += 25
        if today_key() not in self.completed_dates:
            self.completed_dates.append(today_key())
        previous_level = (self.xp - 25) // 100 + 1
        new_level = self.xp // 100 + 1
        old_achievements = set(self.achievements or [])
        self.achievements = self.unlocked_achievements()
        newly_unlocked = [a for a in self.achievements if a not in old_achievements]
        self.save_data()
        if new_level > previous_level:
            message = f"LEVEL UP!! You are now level {new_level}. Character development confirmed. 🏆"
        else:
            message = random.choice(["QUEST CLEARED // +25 XP. RARE PRODUCTIVE CREATURE SPOTTED. 🦄", "+25 XP. BESTIE ACTUALLY DID THE THING?! 😳", "QUEST CLEARED. The plot is plotting in your favour. 📈", "+25 XP. Screenshot this for the historical archives. 📸"])
        if hasattr(self, "chaos_label"):
            self.chaos_label.text = message
        if hasattr(self, "roast_face"):
            self.roast_face.text = "🥳"
        self.set_mascot("🥳")
        self.set_status(message, GREEN)
        self.play_sound("success")
        self.refresh_screen()

        if mission.get("proof_verified"):
            celebration = "🎉🎊 QUEST PROOF VERIFIED! 🎊🎉\n+25 XP — AI confirmed your achievement!"
        else:
            celebration = "🎉🎊 QUEST CLEARED! 🎊🎉\n+25 XP — YOU ACTUALLY DID THE THING!"
        if new_level > previous_level:
            celebration += f"\n\n✨ LEVEL UP — LEVEL {new_level}! ✨"
        if newly_unlocked:
            celebration += "\n\n🏆 ACHIEVEMENT UNLOCKED!\n" + "\n".join(newly_unlocked)
        self.show_celebration(celebration)
        self.emoji_rain(["🎉", "🎊", "✨", "⭐", "🥳", "🏆", "🚀"], 36)
        if hasattr(self, "companion_widget") and self.companion_widget:
            if newly_unlocked:
                self.companion_widget.on_game_event("achievement_unlocked")
            elif new_level > previous_level:
                self.companion_widget.on_game_event("xp_gained")
            else:
                self.companion_widget.on_game_event("quest_completed")

    def show_celebration(self, message):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(14))
        content.add_widget(make_label(message, 16, GREEN, True, halign="center", size_hint_y=1))
        close_btn = NeonButton(text="LET'S GOOO 🚀", bg_color=(0.08, 0.45, 0.32, 1))
        close_btn.size_hint_y = None
        close_btn.height = dp(44)
        content.add_widget(close_btn)
        popup = Popup(title="🎮 PROGRESS UNLOCKED", title_font=EMOJI_FONT, content=content,
                      size_hint=(0.78, None), height=dp(300),
                      separator_color=CYAN, background_color=PANEL)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def check_deadlines(self, *_):
        """Automatically roast overdue unfinished quests, once per quest."""
        overdue = []
        for mission in self.missions:
            if is_overdue(mission) and not mission.get("roast_shown", False):
                mission["roast_shown"] = True
                overdue.append(mission)
        if overdue:
            self.save_data()
            names = ", ".join(str(m.get("name", "Untitled quest")) for m in overdue[:2])
            extra = f" + {len(overdue) - 2} more" if len(overdue) > 2 else ""
            lines = [
                f"🚨 DEADLINE MISSED: {names}{extra}. Bestie, the calendar did its job. 💀",
                f"💀 The deadline passed and '{names}{extra}' is still unfinished. Explain yourself, legend.",
                f"📢 PROCRASTINATION ALERT: '{names}{extra}' is overdue. Time to lock in.",
            ]
            roast = random.choice(lines)
            if hasattr(self, "chaos_label"):
                self.chaos_label.text = roast
            if hasattr(self, "roast_face"):
                self.roast_face.text = "💀"
            self.set_mascot("💀")
            self.set_status("AUTOMATIC ROAST // OVERDUE QUEST DETECTED 💀", PINK)
            self.play_sound("error")
            self.show_roast_popup(roast)
            self.emoji_rain(["💀", "😭", "🔥", "⏰", "🫠"], 20)
            self.refresh_screen()

    def show_roast_popup(self, message):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(14))
        content.add_widget(make_label(message, 14, PINK, True, halign="center", size_hint_y=1))
        content.add_widget(make_label("Quest status: still recoverable. Go finish it. ⚡", 12, WHITE,
                                      halign="center", auto_height=True))
        close_btn = NeonButton(text="OKAY OKAY I'M LOCKING IN 😭", bg_color=(0.55, 0.10, 0.32, 1))
        close_btn.size_hint_y = None
        close_btn.height = dp(44)
        content.add_widget(close_btn)
        popup = Popup(title="🚨 PROCRASTINATION DETECTED", title_font=EMOJI_FONT, content=content,
                      size_hint=(0.82, None), height=dp(300),
                      separator_color=PINK, background_color=PANEL, auto_dismiss=True)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def current_streak(self):
        dates = set()
        for item in self.completed_dates:
            try:
                dates.add(date.fromisoformat(item))
            except (ValueError, TypeError):
                pass
        # A streak remains active if the user completed a quest today or yesterday.
        current = date.today()
        if current not in dates:
            current -= timedelta(days=1)
        streak = 0
        while current in dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def make_mission_row(self, index, mission):
        done = bool(mission.get("done", False))
        priority = mission.get("priority", "Normal")
        title = str(mission.get("name", "Untitled quest"))
        p_emoji = PRIORITY_EMOJI.get(priority, "🌱")
        if done:
            color, prefix, suffix = GREEN, "✅ ", "  // CLEARED"
        elif is_overdue(mission):
            color, prefix, suffix = RED, "🚨 ", "  // OVERDUE"
        elif priority == "Boss fight":
            color, prefix, suffix = PINK, "🐉 ", "  // BOSS FIGHT"
        elif priority == "High":
            color, prefix, suffix = YELLOW, "⚡ ", "  // HIGH PRIORITY"
        else:
            color, prefix, suffix = WHITE, "🎯 ", ""

        row = NeonPanel(
            orientation="horizontal",
            padding=[dp(10), dp(6)],
            spacing=dp(8),
            size_hint_y=None,
            height=dp(66),
            bg_color=BG_ELEVATED,
            border_color=color if done else SEPARATOR,
        )
        row.add_widget(AccentBar(color))
        info = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.55)
        label = make_label(prefix + title + suffix, 12, color, True)
        label.shorten = True
        label.shorten_from = "right"
        info.add_widget(label)
        if done:
            detail = f"🏁 Cleared {mission.get('completed_date', '')}  •  {p_emoji} {priority}"
            if mission.get("proof_verified"):
                detail += "  •  🤖 AI Verified"
        else:
            detail = f"{time_left_text(mission)}  •  {p_emoji} {priority}"
        detail_lbl = make_label(detail, 10, MUTED)
        detail_lbl.shorten = True
        detail_lbl.shorten_from = "right"
        info.add_widget(detail_lbl)
        row.add_widget(info)

        btn_box = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_x=0.45, pos_hint={"center_y": 0.5})
        if not done:
            prove_btn = NeonButton(
                text="📸 PROVE & CLEAR",
                style="style1",
                variant="primary",
                size="small",
                size_hint_x=0.80,
                height=dp(34),
                font_size="10.5sp",
            )
            prove_btn.bind(on_press=lambda _btn, i=index: self.open_proof_verification(i))
            btn_box.add_widget(prove_btn)

            ask_btn = NeonButton(
                text="🤖",
                style="style2",
                variant="secondary",
                size="small",
                size_hint_x=0.20,
                height=dp(34),
                font_size="11sp",
            )
            ask_btn.bind(on_press=lambda _btn, i=index: self.ask_ai_about(i))
            btn_box.add_widget(ask_btn)
        else:
            cleared_badge = NeonPanel(
                orientation="horizontal", padding=[dp(8), dp(4)],
                size_hint=(1, None), height=dp(32),
                pos_hint={"center_y": 0.5},
                bg_color=(0.04, 0.18, 0.12, 0.85),
                border_color=MINT
            )
            tag_text = "🤖 PROOF VERIFIED" if mission.get("proof_verified") else "✅ QUEST CLEARED"
            cleared_badge.add_widget(make_label(tag_text, 10.5, MINT, True, halign="center"))
            btn_box.add_widget(cleared_badge)

        row.add_widget(btn_box)
        return row

    def make_badge_card(self, name_or_info, desc=None, unlocked=None):
        if isinstance(name_or_info, (list, tuple)):
            if len(name_or_info) >= 8:
                name, desc, unlocked, category, rarity, prog_str, prog_ratio, xp_reward = name_or_info[:8]
            else:
                name, desc, unlocked = name_or_info[:3]
                category, rarity, prog_str, prog_ratio, xp_reward = "missions", "COMMON", ("1/1" if unlocked else "0/1"), (1.0 if unlocked else 0.0), 50
        else:
            name = name_or_info
            unlocked = bool(unlocked)
            category, rarity, prog_str, prog_ratio, xp_reward = "missions", "COMMON", ("1/1" if unlocked else "0/1"), (1.0 if unlocked else 0.0), 50

        rarity_colors = {
            "COMMON": (0.00, 0.85, 1.00, 1.0),      # Cyan
            "RARE": (0.00, 1.00, 0.64, 1.0),        # Mint
            "EPIC": (1.00, 0.05, 0.55, 1.0),        # Hot Magenta
            "LEGENDARY": (1.00, 0.85, 0.20, 1.0),   # Gold
        }
        r_color = rarity_colors.get(rarity, CYAN)

        card = NeonPanel(
            orientation="horizontal",
            padding=[dp(12), dp(8)],
            spacing=dp(10),
            size_hint_y=None,
            height=dp(70),
            bg_color=(0.07, 0.04, 0.12, 0.95) if unlocked else (0.04, 0.03, 0.07, 0.85),
            border_color=r_color if unlocked else (0.22, 0.18, 0.30, 0.45),
        )

        # Left Icon Frame
        icon_box = NeonPanel(
            size_hint=(None, None), size=(dp(48), dp(48)),
            pos_hint={"center_y": 0.5},
            padding=[dp(2), dp(2)],
            bg_color=(0.10, 0.06, 0.18, 1.0) if unlocked else (0.03, 0.02, 0.06, 1.0),
            border_color=r_color if unlocked else (0.25, 0.22, 0.35, 0.4)
        )
        icon_char = name.split(" ")[0] if unlocked else "🔒"
        icon_lbl = make_label(icon_char, 20, r_color if unlocked else MUTED, halign="center")
        icon_box.add_widget(icon_lbl)
        card.add_widget(icon_box)

        # Middle Info Box
        info = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.68)

        # Row 1: Title + Rarity Badge
        title_row = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(20))
        display_name = name if unlocked else ("🔒 " + " ".join(name.split(" ")[1:]))
        title_lbl = make_label(f"[b]{display_name}[/b]", 12, r_color if unlocked else WHITE, True, size_hint_x=0.74)

        rarity_badge = make_label(
            f"[{rarity}]", 9.5, r_color if unlocked else MUTED, True,
            size_hint_x=0.26, halign="right"
        )
        title_row.add_widget(title_lbl)
        title_row.add_widget(rarity_badge)
        info.add_widget(title_row)

        # Row 2: Description
        desc_lbl = make_label(desc, 10, TEXT_SEC if unlocked else MUTED, auto_height=False, size_hint_y=None, height=dp(16))
        info.add_widget(desc_lbl)

        # Row 3: Progress Tracker / Unlocked state
        prog_row = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(16))
        if unlocked:
            prog_row.add_widget(make_label("✅ COMMENDATION GRANTED", 9.5, MINT, True))
        else:
            prog_bar = NeonBar(fill_color=r_color, size_hint_x=0.55, size_hint_y=None, height=dp(5), pos_hint={"center_y": 0.5})
            prog_bar.value = max(0.0, min(1.0, float(prog_ratio)))
            prog_row.add_widget(prog_bar)
            prog_row.add_widget(make_label(f"[{prog_str}]", 9.5, YELLOW, True, size_hint_x=0.45, halign="right"))
        info.add_widget(prog_row)
        card.add_widget(info)

        # Right Side: XP Commendation Reward Tag
        reward_box = BoxLayout(orientation="vertical", spacing=dp(1), size_hint_x=0.20, pos_hint={"center_y": 0.5})
        reward_lbl = make_label(f"+{xp_reward} XP", 12, YELLOW if unlocked else MUTED, True, halign="center")
        status_lbl = make_label("CLAIMED" if unlocked else "LOCKED", 9, MINT if unlocked else MUTED, True, halign="center")
        reward_box.add_widget(reward_lbl)
        reward_box.add_widget(status_lbl)
        card.add_widget(reward_box)

        return card

    def set_badge_filter(self, cat_key):
        self.active_badge_filter = cat_key
        self.filter_badges(cat_key)
        self.play_sound("click")

    def filter_badges(self, cat_key="ALL"):
        self.active_badge_filter = cat_key
        if not hasattr(self, "badge_list"):
            return
        defs = self.badge_defs()
        self.badge_list.clear_widgets()
        for b in defs:
            b_cat = b[3] if len(b) >= 4 else "missions"
            if cat_key == "ALL" or b_cat == cat_key:
                self.badge_list.add_widget(self.make_badge_card(b))

        for key, btn in getattr(self, "badge_filter_buttons", {}).items():
            is_active = (key == cat_key)
            btn.variant = "primary" if is_active else "secondary"
            btn.set_bg(NAV_ACTIVE if is_active else NAV_IDLE)

    # ---------- refresh everything ----------

    def refresh_screen(self):
        if not hasattr(self, "mission_list"):
            return
        level = self.xp // 100 + 1
        xp_in_level = self.xp % 100
        title = LEVEL_TITLES[min(level - 1, len(LEVEL_TITLES) - 1)]
        streak = self.current_streak()
        self.level_label.text = f"LVL {level:02d}"
        self.xp_bar.animate_to(xp_in_level / 100)
        self.side_level.text = f"LVL {level:02d}"
        self.side_bar.animate_to(xp_in_level / 100)
        self.side_xp.text = f"{xp_in_level}/100 XP"
        self.xp_label.text = f"{xp_in_level}/100 XP"
        if hasattr(self, "header_streak"):
            self.header_streak.text = f"STREAK: {streak}D"
        if hasattr(self, "activity_heatmap"):
            self.activity_heatmap.refresh()

        hour = datetime.now().hour
        if hour < 12:
            greeting = "COMMAND ACCESS GRANTED // MORNING CYCLE ACTIVE"
        elif hour < 18:
            greeting = "COMMAND ACCESS GRANTED // OPERATIONAL SPRINT ACTIVE"
        else:
            greeting = "COMMAND ACCESS GRANTED // NIGHTCYCLE PROTOCOL"
        self.greeting_label.text = greeting

        total = len(self.missions)
        done = sum(1 for m in self.missions if m.get("done", False))
        active = total - done
        self.stat_missions.value_label.text = str(total)
        self.stat_done.value_label.text = str(done)
        self.stat_active.value_label.text = f"{streak}D"
        self.stat_mood.value_label.text = (
            self.mood_logs[-1].get("mood", "NOMINAL").upper()
            if self.mood_logs else "NOMINAL"
        )

        # Next deadline card
        pending = [m for m in self.missions if not m.get("done", False) and mission_due(m)]
        if pending:
            pending.sort(key=mission_due)
            nxt = pending[0]
            icon = "🚨" if is_overdue(nxt) else "🎯"
            self.next_up_label.text = f"{icon} {nxt.get('name', 'Untitled quest')}\n{time_left_text(nxt)}"
        else:
            self.next_up_label.text = "🎉 Nothing pending. Suspicious. Add a quest! 🕵️"

        if hasattr(self, "sound_button"):
            self.sound_button.text = "🔊 SOUND: ONLINE [ON]" if self.sound_enabled else "🔇 SOUND: MUTED [OFF]"
            self.sound_button.variant = "mint" if self.sound_enabled else "secondary"
            self.sound_button.set_bg((0.08, 0.40, 0.28, 1) if self.sound_enabled else (0.28, 0.14, 0.20, 1))
        if hasattr(self, "mood_history_label"):
            recent = self.mood_logs[-5:]
            self.mood_history_label.text = ("\n".join(f"📅 {x.get('date', '')}  •  {x.get('mood', '')}" for x in reversed(recent)) if recent else "No mood logs yet. 🫧")

        self.mission_list.clear_widgets()
        flt = getattr(self, "mission_filter", "all")
        for key, fb in getattr(self, "filter_buttons", {}).items():
            is_active = (key == flt)
            fb.variant = "primary" if is_active else "secondary"
            fb.set_bg(NAV_ACTIVE if is_active else NAV_IDLE)

        def _show(m):
            if flt == "active":
                return not m.get("done", False)
            if flt == "done":
                return bool(m.get("done", False))
            if flt == "overdue":
                return is_overdue(m)
            return True

        # Newest quests first, but keep original indices for completion.
        shown = [i for i in range(len(self.missions) - 1, -1, -1) if _show(self.missions[i])]
        if not self.missions:
            empty_panel = NeonPanel(
                orientation="vertical", padding=[dp(16), dp(12)], spacing=dp(4),
                size_hint_y=None, height=dp(72), bg_color=BG_ELEVATED, border_color=CYAN
            )
            empty_panel.add_widget(make_label("🕳️ NO DIRECTIVES LOGGED YET", 12, CYAN, True))
            empty_panel.add_widget(make_label("Enter a quest above or deploy one instantly from the Home Command Deck.", 10, MUTED))
            self.mission_list.add_widget(empty_panel)
        elif not shown:
            empty_panel = NeonPanel(
                orientation="vertical", padding=[dp(16), dp(12)], spacing=dp(4),
                size_hint_y=None, height=dp(72), bg_color=BG_ELEVATED, border_color=SEPARATOR
            )
            empty_panel.add_widget(make_label("🔍 NO DIRECTIVES MATCH THIS FILTER", 12, YELLOW, True))
            empty_panel.add_widget(make_label("Switch to '📋 ALL' or log a new mission directive above.", 10, MUTED))
            self.mission_list.add_widget(empty_panel)
        else:
            for index in shown:
                self.mission_list.add_widget(
                    self.make_mission_row(index, self.missions[index])
                )

        # AI focus-quest dropdown (active quests, newest first)
        qmap = {"(no focus quest)": None}
        count = 0
        for i in range(len(self.missions) - 1, -1, -1):
            m = self.missions[i]
            if not m.get("done", False):
                qmap[f"#{i + 1} {str(m.get('name', 'Untitled'))[:32]}"] = i
                count += 1
                if count >= 12:
                    break
        self.ai_quest_map = qmap
        self.ai_quest_spinner.values = list(qmap.keys())
        if self.ai_quest_spinner.text not in qmap:
            self.ai_quest_spinner.text = "(no focus quest)"
        self.update_ai_mode()

        self.streak_label.text = f"🔥 {streak} day(s) in a row  •  🫶 {len(self.mood_logs)} mood log(s)\n" + ("🔥" * min(streak, 12) if streak else "💤 No streak yet. Clear a quest today!")

        defs = self.badge_defs()
        unlocked_list = [b[0] for b in defs if b[2]]
        self.achievements = unlocked_list
        unlocked_count = len(unlocked_list)
        total_count = len(defs)
        earned_xp = sum(b[7] for b in defs if b[2] and len(b) >= 8)

        if hasattr(self, "achievement_label"):
            pct = int((unlocked_count / total_count) * 100) if total_count else 0
            self.achievement_label.text = f"🎖️ {unlocked_count} / {total_count} UNLOCKED ({pct}%)"
        if hasattr(self, "achievement_xp_label"):
            self.achievement_xp_label.text = f"⭐ +{earned_xp} XP COMMENDED"
        if hasattr(self, "achievement_bar"):
            self.achievement_bar.animate_to(unlocked_count / total_count if total_count else 0)

        self.filter_badges(getattr(self, "active_badge_filter", "ALL"))

        if hasattr(self, "daily_challenge_label") and self.daily_challenge:
            self.daily_challenge_label.text = self.daily_challenge

        if total:
            rate = round((done / total) * 100)
            insight = f"📈 Quest clear rate: {rate}%  |  "
            if rate >= 75:
                insight += "You're cooking. Keep the combo alive! 🍳"
            elif rate >= 40:
                insight += "Solid progress. One quest at a time. 💪"
            else:
                insight += "Tiny steps count. Pick the easiest quest next. 🐣"
            self.rate_bar.animate_to(rate / 100)
            self.insights_bar.animate_to(rate / 100)
            self.rate_label.text = f"{rate}% cleared  •  {done}/{total} quests"
        else:
            insight = "📭 Complete a quest to start building your stats."
            self.rate_bar.value = 0
            self.insights_bar.value = 0
            self.rate_label.text = "0% cleared  •  add a quest to begin"
        if self.mood_logs:
            latest = self.mood_logs[-1].get("mood", "")
            insight += f"\n💙 Latest mood: {latest}. Take breaks when you need them."
        self.insights_label.text = insight

        # --- Insights extras ---
        self.ins_xp.value_label.text = str(self.xp)
        self.ins_streak.value_label.text = f"{self.best_streak()} day(s)"
        self.ins_rate.value_label.text = f"{round(done / total * 100) if total else 0}%"
        self.ins_moods.value_label.text = str(len(self.mood_logs))

        counts = {}
        for m in self.missions:
            if m.get("done") and m.get("completed_date"):
                counts[m["completed_date"]] = counts.get(m["completed_date"], 0) + 1
        week = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
        peak = max([counts.get(d.isoformat(), 0) for d in week] + [1])
        self.week_box.clear_widgets()
        for d in week:
            n = counts.get(d.isoformat(), 0)
            row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
            row.add_widget(make_label(d.strftime("%a"), 11, YELLOW if d == date.today() else MUTED, True,
                                      size_hint_x=None, width=dp(44), size_hint_y=1))
            bar = NeonBar(fill_color=GREEN, size_hint_y=None, height=dp(12), pos_hint={"center_y": 0.5})
            bar.value = n / peak
            row.add_widget(bar)
            row.add_widget(make_label(f"{n} ✅" if n else "💤", 11, WHITE, True,
                                      size_hint_x=None, width=dp(54), size_hint_y=1))
            self.week_box.add_widget(row)

        if self.mood_logs:
            tally = Counter(x.get("mood", "") for x in self.mood_logs)
            self.mood_mix_label.text = "\n".join(f"{name}  ×{c}" for name, c in tally.most_common(6))
        else:
            self.mood_mix_label.text = "No moods logged yet. 🫧"

        overdue_list = [m for m in self.missions if is_overdue(m)]
        ratio = len(overdue_list) / active if active else 0
        self.meter_bar.value = ratio
        if not overdue_list:
            self.meter_bar.set_color(GREEN)
            self.meter_label.text = "😇 Zero overdue quests. Suspiciously responsible."
        elif ratio < 0.4:
            self.meter_bar.set_color(YELLOW)
            self.meter_label.text = f"😅 {len(overdue_list)} overdue of {active} active. Manageable chaos."
        else:
            self.meter_bar.set_color(RED)
            self.meter_label.text = f"🚨 {len(overdue_list)} overdue of {active} active. Code red, bestie."
        if overdue_list:
            shame = "\n".join(f"💀 {m.get('name', 'Untitled quest')} — {time_left_text(m)}" for m in overdue_list[:5])
            if len(overdue_list) > 5:
                shame += f"\n…and {len(overdue_list) - 5} more 😭"
            self.shame_label.text = shame
        else:
            self.shame_label.text = "🕊️ Nobody in the hall of shame. Respect."
        self.update_accept_button()

        # Keep the idle mascot honest (😬 when something is overdue).
        if self._mascot_event is None and hasattr(self, "mascot_label"):
            self.mascot_label.text = self.idle_mascot()


import online
online.install(globals(), ProcrastiNotApp)
import i18n
i18n.install(globals(), ProcrastiNotApp)
import auth_service
auth_service.install(globals(), ProcrastiNotApp)

# Animation & visual effects are optional: if fx.py is missing or breaks,
# the app simply starts without them.
try:
    import fx
    fx.install(globals(), ProcrastiNotApp)
except Exception as _fx_err:
    print("fx disabled:", _fx_err)


if __name__ == "__main__":
    ProcrastiNotApp().run()