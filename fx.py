# -*- coding: utf-8 -*-
"""
fx.py - animation & visual effects engine for procrastiNOT.exe

Loaded at the very end of main_leaderboard.py:
    import fx; fx.install(globals(), ProcrastiNotApp)

Design rules (in priority order):
  1. DATA SAFETY   - fx never writes your save file. Its only files are
                     fx_prefs.json (motion setting) and fx_errors.log, next to
                     projectx_data.json. XP / quest / streak logic is NOT
                     re-implemented here: the original methods run first and fx
                     only READS the result afterwards.
  2. CORRECTNESS   - every hook is wrapped: if an effect raises, the error is
                     logged and ignored, and after 6 errors all decorative
                     effects switch themselves off. The app keeps working.
  3. RESPONSIVE    - effects start AFTER the real action ran, use one pooled
                     particle set, and never create permanent Clock events
                     per refresh (each timer stops itself when it is done).
  4. LOOKS         - boot sequence, pixel rocket, glitch title, neon buttons,
                     quest-complete toast, +XP, level-up, streak, mood bounce,
                     count-up stats, ambient pulse.

Motion setting (SETTINGS page): FULL / REDUCED / OFF. OFF keeps essential
feedback (button colour, original popups) and removes decorative animation.
"""
import json
import math
import os
import random
import re
import shutil
import sys
import time
import traceback
import weakref
from datetime import datetime

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (Color, Ellipse, Line, PopMatrix, PushMatrix, Rectangle,
                           RoundedRectangle, Rotate, Scale, Translate)
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

# filled in by install() from main_leaderboard.py's globals
make_label = section = NeonPanel = NeonButton = NeonBar = TechLabel = None
MoodOption = CyberBackdrop = None
CYAN = PINK = PURPLE = GREEN = YELLOW = WHITE = MUTED = RED = None
MAGENTA = MAGENTA_CORE = VIOLET = MINT = JAPANESE_FONT = None
_NEEDED = ["make_label", "section", "NeonPanel", "NeonButton", "NeonBar", "TechLabel",
           "MoodOption", "CyberBackdrop", "CYAN", "PINK", "PURPLE", "GREEN", "YELLOW",
           "WHITE", "MUTED", "RED", "MAGENTA", "MAGENTA_CORE", "VIOLET", "MINT", "JAPANESE_FONT"]

MODES = ("full", "reduced", "off")
STREAK_MILESTONES = (3, 7, 14, 21, 30, 50, 100)
FX = {"mode": "full", "fail": 0, "prefs_path": "", "load": ("new", "")}


# ------------------------------------------------------------------
# small helpers: mode, safety net, animation wrapper
# ------------------------------------------------------------------
def mode():
    return FX["mode"]


def full():
    return FX["mode"] == "full"


def lively():
    return FX["mode"] != "off"


def _ease_out(k):
    k = max(0.0, min(1.0, k))
    return 1.0 - (1.0 - k) ** 3


def _ease_in(k):
    k = max(0.0, min(1.0, k))
    return k * k


def _fail(exc):
    """Log an effect error and never raise. Too many errors => effects off."""
    FX["fail"] += 1
    try:
        text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        try:
            print("[fx] effect error (ignored):\n" + text, file=sys.stderr)
        except Exception:
            pass
        path = FX.get("prefs_path") or ""
        if path:
            with open(os.path.join(os.path.dirname(path), "fx_errors.log"), "a",
                      encoding="utf-8") as f:
                f.write(datetime.now().isoformat(timespec="seconds") + "\n" + text + "\n")
    except Exception:
        pass
    if FX["fail"] >= 6 and FX["mode"] != "off":
        FX["mode"] = "off"


def _guarded(fn):
    """Decorator for Clock / event callbacks: an effect bug must never crash the app."""
    def wrapper(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as exc:     # noqa: BLE001
            _fail(exc)
            return False             # False also cancels a schedule_interval
    wrapper.__name__ = getattr(fn, "__name__", "fx_cb")
    return wrapper


def _go(obj, d=0.2, t="linear", on_done=None, **props):
    """Start one Animation on obj. Falls back to setting the final values."""
    try:
        anim = Animation(d=d, t=t, **props)
        if on_done is not None:
            anim.bind(on_complete=lambda *_: _guarded(on_done)())
        anim.start(obj)
        return anim
    except Exception as exc:         # noqa: BLE001
        _fail(exc)
        for key, val in props.items():
            try:
                setattr(obj, key, val)
            except Exception:
                pass
        if on_done is not None:
            _guarded(on_done)()
        return None


def _stop(obj, *props):
    try:
        Animation.cancel_all(obj, *props)
    except Exception:
        pass


def _win_center(widget):
    try:
        return widget.to_window(*widget.center)
    except Exception:
        return (Window.width / 2.0, Window.height / 2.0)


# ------------------------------------------------------------------
# prefs (own tiny file - never touches projectx_data.json)
# ------------------------------------------------------------------
def _load_prefs():
    try:
        with open(FX["prefs_path"], "r", encoding="utf-8") as f:
            m = json.load(f).get("motion")
        if m in MODES:
            FX["mode"] = m
    except Exception:
        pass


def _save_prefs():
    path = FX.get("prefs_path")
    if not path:
        return
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"motion": FX["mode"]}, f)
        os.replace(tmp, path)
    except Exception as exc:         # noqa: BLE001
        _fail(exc)


# ------------------------------------------------------------------
# PIXEL ROCKET companion (custom-drawn canvas sprite, no image files)
# ------------------------------------------------------------------
_ROCKET = [
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
_PALETTE = [
    ("W", (0.88, 0.96, 1.0, 1)),
    ("G", (0.50, 0.62, 0.86, 1)),
    ("C", (0.0, 0.95, 1.0, 1)),
    ("P", (1.0, 0.20, 0.78, 1)),
]
_ROCKETS = []       # weakrefs, so the motion setting can reach every rocket


class PixelRocket(Widget):
    """Floats, tilts, flickers its flame, can launch() and celebrate()."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self._ev = None
        self._t = random.uniform(0, 6)
        self._launch = None
        self._wiggle = None
        self._tilt_at = random.uniform(3, 6)
        self._tilt_start = None
        self._flame_len = 1
        self._flame_next = 0.0
        self._px, self._ox, self._oy = dp(4), 0.0, 0.0
        self._pix = []
        with self.canvas:
            PushMatrix()
            self._tr = Translate(0, 0)
            self._rot = Rotate(angle=0, origin=(0, 0))
            for ch, rgba in _PALETTE:
                Color(*rgba)
                for r, row in enumerate(_ROCKET):
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
        _ROCKETS.append(weakref.ref(self))
        self._layout()

    # -- lifecycle: the timer only exists while the rocket is on screen --
    def on_parent(self, *_):
        self._sync_tick()

    def _sync_tick(self):
        want = self.parent is not None and mode() != "off"
        if want and self._ev is None:
            self._ev = Clock.schedule_interval(self._tick, 1 / 24.0)
        elif not want and self._ev is not None:
            self._ev.cancel()
            self._ev = None
            self._launch = self._wiggle = None
            self._tr.y = 0
            self._rot.angle = 0
            self.opacity = 1
            self._set_flame(0)

    # -- drawing --
    def _layout(self, *_):
        px = max(1.0, min(self.width / 9.0, self.height / 15.0))
        self._px = px
        self._ox = self.x + (self.width - 9 * px) / 2.0
        self._oy = self.y + (self.height - 15 * px) / 2.0
        for rect, c, r in self._pix:
            rect.pos = (self._ox + c * px, self._oy + (14 - r) * px)
            rect.size = (px, px)
        self._rot.origin = self.center
        self._set_flame(self._flame_len)

    def _set_flame(self, f):
        self._flame_len = f
        px, ox, oy = self._px, self._ox, self._oy
        self._f_out.pos = (ox + 3 * px, oy + 2 * px)
        self._f_out.size = (3 * px, px)
        self._f_in.pos = (ox + 4 * px, oy + (2 - f) * px)
        self._f_in.size = (px, (1 + f) * px)
        self._f_tip.pos = (ox + 4 * px, oy + (1 - f) * px)
        self._f_tip.size = (px, px)

    @_guarded
    def _tick(self, dt):
        m = mode()
        if m == "off":
            return False
        self._t += dt
        now = time.monotonic()
        bob = tilt = ly = wig = 0.0
        if m == "full":
            bob = math.sin(self._t * 2.2) * self._px * 0.7
            tilt = math.sin(self._t * 1.1) * 2.5
            self._tilt_at -= dt
            if self._tilt_at <= 0 and self._tilt_start is None:
                self._tilt_start = now
            if self._tilt_start is not None:
                k = (now - self._tilt_start) / 0.8
                if k >= 1:
                    self._tilt_start = None
                    self._tilt_at = random.uniform(4, 9)
                else:
                    tilt += math.sin(k * math.pi) * 9.0
        else:
            bob = math.sin(self._t * 1.6) * self._px * 0.35
        # flame flicker (a few times per second, not every frame)
        self._flame_next -= dt
        if self._flame_next <= 0:
            self._set_flame(random.choice((0, 1)))
            self._flame_next = random.uniform(0.07, 0.16)
        # launch: shoot up, fade, reappear from below
        if self._launch is not None:
            t = now - self._launch
            if t < 0.45:
                k = t / 0.45
                ly = dp(120) * _ease_in(k)
                self.opacity = 1.0 - k * k
            elif t < 1.05:
                k = (t - 0.45) / 0.6
                ly = -dp(40) * (1.0 - _ease_out(k))
                self.opacity = min(1.0, k * 1.5)
            else:
                self._launch = None
                self.opacity = 1
            if self._launch is not None:
                self._set_flame(1)
        # celebrate: quick wiggle + hop
        if self._wiggle is not None:
            t = now - self._wiggle
            if t >= 0.9:
                self._wiggle = None
            else:
                fade = 1.0 - t / 0.9
                wig = math.sin(t * 28) * 14.0 * fade
                ly += abs(math.sin(t * 10)) * dp(8) * fade
        self._tr.y = bob + ly
        self._rot.angle = tilt + wig

    def launch(self):
        if self._ev is not None and lively():
            self._launch = time.monotonic()

    def celebrate(self):
        if self._ev is not None and lively():
            self._wiggle = time.monotonic()


# ------------------------------------------------------------------
# OVERLAY: pooled particles, rings, flash, toast, +XP, big banner
# ------------------------------------------------------------------
class FxLayer(FloatLayout):
    """One transparent layer over the whole window. Never intercepts touches."""
    MAXP = 56

    def __init__(self, **kw):
        super().__init__(size_hint=(1, 1), **kw)
        self._p = []
        self._ev = None
        self._toast = None
        self._toast_ev = None
        self._banner = None
        self._banner_ev = None
        self._floats = []
        self._rings = [None, None]
        with self.canvas:
            self._flash_c = Color(0.0, 0.95, 1.0, 0.0)
            self._flash = Rectangle(pos=(0, 0), size=(1, 1))
            self._ring_c = [Color(0, 0.95, 1, 0) for _ in range(2)]
            self._ring_l = [Line(circle=(0, 0, 1), width=dp(2.2)) for _ in range(2)]
            for _ in range(self.MAXP):
                c = Color(1, 1, 1, 0)
                r = Rectangle(pos=(-100, -100), size=(1, 1))
                self._p.append({"c": c, "r": r, "life": 0.0, "max": 1.0,
                                "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "s": dp(4)})
        self.bind(size=self._on_size)

    def _on_size(self, *_):
        self._flash.size = self.size

    # never swallow clicks: this layer is purely visual
    def on_touch_down(self, touch):
        return False

    def on_touch_move(self, touch):
        return False

    def on_touch_up(self, touch):
        return False

    # -- particles --
    def burst(self, x, y, n=22, colors=None):
        n = {"full": n, "reduced": max(4, n // 3)}.get(mode(), 0)
        if n <= 0:
            return
        colors = colors or [GREEN, CYAN, PINK, YELLOW, PURPLE]
        for p in self._p:
            if n <= 0:
                break
            if p["life"] > 0:
                continue
            ang = random.uniform(0, math.tau)
            spd = random.uniform(dp(60), dp(220))
            p["x"], p["y"] = x, y
            p["vx"], p["vy"] = math.cos(ang) * spd, math.sin(ang) * spd + dp(40)
            p["life"] = p["max"] = random.uniform(0.5, 0.95)
            p["s"] = random.choice((dp(3), dp(4), dp(5)))
            col = random.choice(colors)
            p["c"].rgba = (col[0], col[1], col[2], 1)
            n -= 1
        self._ensure_tick()

    def ring(self, x, y, color=None):
        if not full():
            return
        color = color or CYAN
        for i in range(2):
            if self._rings[i] is None:
                self._rings[i] = {"x": x, "y": y, "t": 0.0, "col": color}
                break
        self._ensure_tick()

    def flash(self, color=None):
        if not full():
            return
        color = color or CYAN
        self._flash.size = self.size
        _stop(self._flash_c)
        self._flash_c.rgba = (color[0], color[1], color[2], 0.14)
        _go(self._flash_c, d=0.45, t="out_quad", a=0.0)

    def _ensure_tick(self):
        if self._ev is None:
            self._ev = Clock.schedule_interval(self._tick, 1 / 30.0)

    @_guarded
    def _tick(self, dt):
        active = False
        for p in self._p:
            if p["life"] <= 0:
                continue
            p["life"] -= dt
            if p["life"] <= 0:
                p["c"].a = 0
                p["r"].pos = (-100, -100)
                continue
            p["vy"] -= dp(380) * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["r"].pos = (p["x"], p["y"])
            p["r"].size = (p["s"], p["s"])
            p["c"].a = min(1.0, p["life"] / p["max"] * 1.6)
            active = True
        for i, ring in enumerate(self._rings):
            if ring is None:
                continue
            ring["t"] += dt
            k = ring["t"] / 0.7
            if k >= 1:
                self._ring_c[i].a = 0
                self._rings[i] = None
                continue
            r = dp(10) + (dp(130) - dp(10)) * _ease_out(k)
            self._ring_l[i].circle = (ring["x"], ring["y"], r)
            col = ring["col"]
            self._ring_c[i].rgba = (col[0], col[1], col[2], 0.8 * (1 - k))
            active = True
        if not active:
            self._ev = None
            return False

    # -- floating "+XP" text --
    def float_text(self, text, x, y, color=None, size="16sp"):
        if not lively():
            return
        color = color or GREEN
        while len(self._floats) >= 4:
            old = self._floats.pop(0)
            _stop(old)
            self._drop(old)
        w, h = dp(120), dp(30)
        lab = TechLabel(text=text, font_size=size, bold=True, color=color, halign="center",
                        valign="middle", size_hint=(None, None), size=(w, h))
        lab.text_size = (w, h)
        lab.pos = (x - w / 2.0, y)
        self.add_widget(lab)
        self._floats.append(lab)
        rise = dp(46) if full() else dp(20)
        _go(lab, d=1.0, t="out_quad", y=y + rise)
        _go(lab, d=1.0, t="in_cubic", opacity=0.0, on_done=lambda: self._drop(lab))

    def _drop(self, widget):
        try:
            if widget in self._floats:
                self._floats.remove(widget)
            if widget.parent is self:
                self.remove_widget(widget)
        except Exception:
            pass

    # -- compact notification (one at a time, never stacks) --
    def toast(self, title, sub="", extra="", color=None):
        if mode() == "off":
            return
        color = color or GREEN
        self._kill_toast()
        w = min(dp(400), max(dp(240), self.width - dp(24)))
        h = dp(60) + (dp(18) if extra else 0)
        panel = NeonPanel(orientation="vertical", padding=[dp(10), dp(6)], spacing=dp(1),
                          size_hint=(None, None), size=(w, h),
                          bg_color=(0.03, 0.07, 0.15, 0.96),
                          border_color=(color[0], color[1], color[2], 0.95))
        panel.add_widget(make_label(title, 14, color, True, halign="center", size_hint_y=1))
        if sub:
            panel.add_widget(make_label(sub, 11, WHITE, True, halign="center", size_hint_y=1))
        if extra:
            panel.add_widget(make_label(extra, 10, YELLOW, True, halign="center", size_hint_y=1))
        ty = self.height - h - dp(16)
        panel.pos = ((self.width - w) / 2.0, ty + (dp(26) if full() else 0))
        panel.opacity = 0
        self.add_widget(panel)
        self._toast = panel
        _go(panel, d=0.22, t="out_quad", opacity=1, y=ty)
        self._toast_ev = Clock.schedule_once(self._toast_out, 2.4)

    @_guarded
    def _toast_out(self, _dt):
        panel = self._toast
        self._toast_ev = None
        if panel is not None:
            _go(panel, d=0.3, opacity=0.0, on_done=lambda: self._remove_toast(panel))

    def _remove_toast(self, panel):
        if panel.parent is self:
            self.remove_widget(panel)
        if self._toast is panel:
            self._toast = None

    def _kill_toast(self):
        if self._toast_ev is not None:
            self._toast_ev.cancel()
            self._toast_ev = None
        if self._toast is not None:
            _stop(self._toast)
            self._remove_toast(self._toast)

    # -- big temporary text (LEVEL UP) --
    def banner(self, text, color=None):
        if not lively():
            return
        color = color or GREEN
        self._kill_banner()
        w, h = min(dp(460), self.width - dp(20)), dp(110)
        lab = TechLabel(text=text, font_size="30sp", bold=True, color=color, halign="center",
                        valign="middle", size_hint=(None, None), size=(w, h))
        lab.text_size = (w, h)
        ty = self.height * 0.58
        lab.pos = ((self.width - w) / 2.0, ty - (dp(14) if full() else 0))
        lab.opacity = 0
        self.add_widget(lab)
        self._banner = lab
        _go(lab, d=0.22, t="out_quad", opacity=1, y=ty)
        self._banner_ev = Clock.schedule_once(self._banner_out, 1.5)

    @_guarded
    def _banner_out(self, _dt):
        lab = self._banner
        self._banner_ev = None
        if lab is not None:
            _go(lab, d=0.5, opacity=0.0, on_done=lambda: self._remove_banner(lab))

    def _remove_banner(self, lab):
        if lab.parent is self:
            self.remove_widget(lab)
        if self._banner is lab:
            self._banner = None

    def _kill_banner(self):
        if self._banner_ev is not None:
            self._banner_ev.cancel()
            self._banner_ev = None
        if self._banner is not None:
            _stop(self._banner)
            self._remove_banner(self._banner)


_LAYER = None


def layer():
    global _LAYER
    if _LAYER is None:
        _LAYER = FxLayer()
        Window.add_widget(_LAYER)
    elif _LAYER.parent is None:
        Window.add_widget(_LAYER)
    return _LAYER


# ------------------------------------------------------------------
# TITLE: digital reveal, restrained glitch, cyan/purple glow
# ------------------------------------------------------------------
_GLYPHS = "01<>/#%@$=+*"


class FxTitle(FloatLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._alive = False
        self._rev = None
        self._glitch_ev = None
        self._reset_ev = None
        self._t0 = 0.0
        self.glow = make_label(text, 16, PURPLE, True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.glow.opacity = 0
        self.ghost = make_label(text, 16, PINK, True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.ghost.opacity = 0
        self.main = make_label(text, 16, CYAN, True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.glow)
        self.add_widget(self.ghost)
        self.add_widget(self.main)

    def on_parent(self, _inst, parent):
        if parent is not None:
            self._start()
        else:
            self._stop()

    def _start(self):
        if self._alive:
            return
        self._alive = True
        if mode() == "off":
            return
        self._t0 = time.monotonic()
        self._rev = Clock.schedule_interval(self._reveal, 1 / 30.0)
        if full():
            self._glitch_ev = Clock.schedule_interval(self._glitch, 3.0)
            self._glow(True)

    def _stop(self):
        self._alive = False
        for name in ("_rev", "_glitch_ev", "_reset_ev"):
            ev = getattr(self, name)
            if ev is not None:
                ev.cancel()
                setattr(self, name, None)
        _stop(self.glow, "opacity")
        self.main.text = self._text

    @_guarded
    def _reveal(self, _dt):
        dur = 0.9 if full() else 0.4
        p = (time.monotonic() - self._t0) / dur
        if p >= 1.0:
            self.main.text = self._text
            self._rev = None
            return False
        n = int(p * len(self._text))
        rest = "".join(random.choice(_GLYPHS) for _ in self._text[n:])
        self.main.text = self._text[:n] + rest

    def _glow(self, up):
        if not self._alive or not full():
            self.glow.opacity = 0
            return
        _go(self.glow, d=1.4, t="in_out_sine", opacity=0.36 if up else 0.08,
            on_done=lambda: self._glow(not up))

    @_guarded
    def _glitch(self, _dt):
        if not full() or random.random() > 0.45:
            return
        self.ghost.opacity = 0.8
        self.ghost.pos_hint = {"x": random.uniform(-0.04, 0.04), "y": random.uniform(-0.05, 0.05)}
        self.main.pos_hint = {"x": random.uniform(-0.015, 0.015), "y": 0}
        self._reset_ev = Clock.schedule_once(self._unglitch, 0.12)

    @_guarded
    def _unglitch(self, _dt):
        self._reset_ev = None
        self.ghost.opacity = 0
        self.ghost.pos_hint = {"x": 0, "y": 0}
        self.main.pos_hint = {"x": 0, "y": 0}


# ------------------------------------------------------------------
# BOOT SEQUENCE (real status, skippable, short)
# ------------------------------------------------------------------
def _boot_lines(app):
    status = FX["load"][0]
    missions = getattr(app, "missions", None) or []
    done = sum(1 for m in missions if isinstance(m, dict) and m.get("done"))
    lines = [("> INITIALIZING PROCRASTINOT.EXE...", CYAN)]
    if status == "ok":
        lines.append(("> LOADING PLAYER PROFILE... OK", GREEN))
    elif status == "new" and (getattr(app, "xp", 0) or missions):
        lines.append(("> LOADING PLAYER PROFILE... IMPORTED FROM OLD SAVE", GREEN))
    elif status == "new":
        lines.append(("> LOADING PLAYER PROFILE... NEW PROFILE CREATED", YELLOW))
    else:
        lines.append(("> LOADING PLAYER PROFILE... ERROR: SAVE FILE UNREADABLE", PINK))
    if status == "corrupt":
        lines.append(("> SYNCING QUEST DATABASE... SKIPPED, 0 QUESTS LOADED", PINK))
        lines.append(("> SYSTEM ONLINE WITH WARNINGS !", YELLOW))
    else:
        lines.append(("> SYNCING QUEST DATABASE... %d QUESTS, %d CLEARED" % (len(missions), done), GREEN))
        lines.append(("> SYSTEM ONLINE \u2714", GREEN))
    return lines


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


class FxBoot(FloatLayout):
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
        self._speed = 1.0 if full() else 2.5
        app = App.get_running_app()
        self._app = app

        # Visual elements on canvas
        with self.canvas.before:
            # Stage background #06030A
            Color(0.024, 0.012, 0.039, 1.0)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            # Deep violet floor haze #2A0A5C rising from bottom edge (Ref B & C)
            Color(0.165, 0.039, 0.361, 0.40)
            self._haze1 = Ellipse(pos=(0, 0), size=(10, 10))
            Color(1.0, 0.239, 0.949, 0.05)
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
            self._grain_colors = [Color(1.0, 0.239, 0.949, 0) for _ in range(self._n_grains)]
            self._grain_rects = [Rectangle(pos=(-100, -100), size=(dp(2.2), dp(2.2))) for _ in range(self._n_grains)]

            # Scan sweep line
            self._sweep_c = Color(1.0, 0.882, 0.984, 0)
            self._sweep_line = Line(points=[0, 0, 0, 0], width=dp(1.8))

            # Opening frame slit (for transition)
            self._frame_c = Color(1.0, 0.882, 0.984, 0)
            self._frame_line = Line(rectangle=(0, 0, 0, 0), width=dp(2.0))

        # Title layers in Center
        jp_font = JAPANESE_FONT or "Roboto"
        tech_font = "C:/Windows/Fonts/consola.ttf" if os.path.exists("C:/Windows/Fonts/consola.ttf") else "Roboto"

        self.title_glow = Label(
            text="ネオン", font_size="64sp", color=(1.0, 0.239, 0.949, 0.40), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=jp_font
        )
        self.title_main = Label(
            text="ネオン", font_size="64sp", color=(1.0, 0.239, 0.949, 0.95), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=jp_font
        )
        self.title_core = Label(
            text="ネオン", font_size="64sp", color=(1.0, 0.882, 0.984, 0.85), bold=True, halign="center",
            size_hint=(None, None), size=(dp(360), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.52}, font_name=jp_font
        )
        self.add_widget(self.title_glow)
        self.add_widget(self.title_main)
        self.add_widget(self.title_core)

        # Top label (decoded mint dot-matrix)
        self.label_top = Label(
            text="neon", font_size="13sp", color=MINT or (0.239, 1.0, 0.690, 1.0), bold=True, halign="center",
            size_hint=(None, None), size=(dp(200), dp(24)),
            pos_hint={"center_x": 0.5, "center_y": 0.64}, font_name=tech_font
        )
        self.add_widget(self.label_top)

        # Bottom label (percentage / 'online')
        self.label_bottom = Label(
            text="000%", font_size="13sp", color=MINT or (0.239, 1.0, 0.690, 1.0), bold=True, halign="center",
            size_hint=(None, None), size=(dp(200), dp(24)),
            pos_hint={"center_x": 0.5, "center_y": 0.40}, font_name=tech_font
        )
        self.add_widget(self.label_bottom)

        # HUD Corners (Ref B & C)
        # Top-Left: ネオン / SECTOR 7
        self.hud_tl = Label(
            text="ネオン / SECTOR 7", font_size="10sp", color=MAGENTA or (1.0, 0.239, 0.949, 1.0), bold=False,
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"x": 0.03, "top": 0.97}, font_name=jp_font
        )
        self.add_widget(self.hud_tl)

        # Top-Right: ● DECODING / ● SIGNAL LOCKED
        self.hud_tr = Label(
            text="● DECODING", font_size="10sp", color=MINT or (0.239, 1.0, 0.690, 1.0), bold=True, halign="right",
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"right": 0.97, "top": 0.97}, font_name=tech_font
        )
        self.add_widget(self.hud_tr)

        # Bottom-Left: 000 ─────── 100
        self.hud_bl_box = BoxLayout(
            orientation="horizontal", spacing=dp(6),
            size_hint=(None, None), size=(dp(180), dp(20)),
            pos_hint={"x": 0.03, "y": 0.03}
        )
        self.hud_bl_cur = Label(text="000", font_size="10sp", color=MAGENTA or (1.0, 0.239, 0.949, 1.0), bold=False, size_hint_x=None, width=dp(30), font_name=tech_font)
        self.hud_bl_track = Widget(size_hint=(1, None), height=dp(2), pos_hint={"center_y": 0.5})
        with self.hud_bl_track.canvas:
            Color(1, 1, 1, 0.12)
            self._track_bg = Rectangle(pos=(0, 0), size=(0, dp(1.5)))
            Color(1.0, 0.239, 0.949, 1.0)
            self._track_fill = Rectangle(pos=(0, 0), size=(0, dp(1.8)))
        self.hud_bl_box.add_widget(self.hud_bl_cur)
        self.hud_bl_box.add_widget(self.hud_bl_track)
        self.hud_bl_box.add_widget(Label(text="100", font_size="10sp", color=MUTED or (0.467, 0.439, 0.502, 1.0), bold=False, size_hint_x=None, width=dp(30), font_name=tech_font))
        self.add_widget(self.hud_bl_box)

        # Bottom-Right: TAP TO SKIP / TAP TO OPEN
        self.hud_br = Label(
            text="TAP TO SKIP", font_size="10sp", color=MUTED or (0.467, 0.439, 0.502, 1.0), bold=False, halign="right",
            size_hint=(None, None), size=(dp(220), dp(20)),
            pos_hint={"right": 0.97, "y": 0.03}, font_name=tech_font
        )
        self.add_widget(self.hud_br)

        self.bind(pos=self._layout, size=self._layout)
        Window.bind(on_key_down=self._on_key)
        self._init_data()

        if mode() == "off":
            Clock.schedule_once(lambda dt: self._finish(True), 0)
        else:
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
        app = self._app
        try:
            app.play_sound("click")
            if FX["load"][0] == "corrupt":
                name = FX["load"][1]
                app.set_status("SAVE FILE UNREADABLE - a copy was kept as " + (name or "a .corrupt file"), PINK)
        except Exception as exc:
            _fail(exc)

        # Slit-of-light / frame tear opening animation into workspace
        if not fast and lively():
            cx, cy = self.center
            self._frame_c.a = 0.95
            self._frame_line.rectangle = (cx - dp(10), cy - dp(2), dp(20), dp(4))
            _go(self, d=0.45, opacity=0.0, on_done=self._remove)
        else:
            self._remove()

    def _remove(self):
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._cleanup()

    @_guarded
    def _tick(self, dt):
        if self._done:
            return False
        self._t += dt * self._speed
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

        # Decoding top label
        mint_col = MINT or (0.239, 1.0, 0.690, 1.0)
        magenta_col = MAGENTA or (1.0, 0.239, 0.949, 1.0)
        core_col = MAGENTA_CORE or (1.0, 0.882, 0.984, 1.0)
        muted_col = MUTED or (0.467, 0.439, 0.502, 1.0)

        if pct_val < 100:
            self.label_top.text = nkp_decode("neon", self._pct * 1.3, self._tick_count)
            self.label_bottom.text = f"{pct_str}%"
            self.hud_tr.text = "● DECODING" if (int(t * 4) % 2 == 0) else "○ DECODING"
            self.hud_tr.color = mint_col
            self.hud_br.text = "TAP TO SKIP" if not self._rushed else "DECODING..."
        else:
            self._locked = True
            self.label_top.text = "neon"
            self.label_bottom.text = "online"
            self.hud_tr.text = "● SIGNAL LOCKED"
            self.hud_tr.color = mint_col
            self.hud_br.text = "TAP TO OPEN // ENTER"
            self.hud_br.color = mint_col

        self.hud_bl_cur.text = pct_str
        track_w = self.hud_bl_track.width
        self._track_bg.pos = self.hud_bl_track.pos
        self._track_bg.size = (track_w, dp(1.5))
        self._track_fill.pos = self.hud_bl_track.pos
        self._track_fill.size = (track_w * self._pct, dp(1.8))

        # Title opacity & grain coalescing
        title_alpha = min(1.0, 0.2 + self._pct * 0.8)
        self.title_glow.color = (magenta_col[0], magenta_col[1], magenta_col[2], title_alpha * 0.35)
        self.title_main.color = (magenta_col[0], magenta_col[1], magenta_col[2], title_alpha * 0.95)
        self.title_core.color = (core_col[0], core_col[1], core_col[2], title_alpha * 0.85)

        # Grain particles coalescing
        for i, (gtx, gty, fall, rank) in enumerate(self._grains_data):
            if rank <= self._pct:
                k = min(1.0, (self._pct - rank) / 0.2)
                e = 1.0 - (1.0 - k) ** 3
                gx = cx + gtx
                gy = cy + gty - fall * (1.0 - e)
                self._grain_rects[i].pos = (gx, gy)
                self._grain_colors[i].rgba = (magenta_col[0], magenta_col[1], magenta_col[2], min(1.0, 0.3 + 0.7 * k))
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
                self._rain_colors[i].rgba = (mint_col[0], mint_col[1], mint_col[2], 0.20 * self._pct + 0.08)
                self._head_colors[i].rgba = (mint_col[0], mint_col[1], mint_col[2], 0.75)
            else:
                self._rain_colors[i].rgba = (magenta_col[0], magenta_col[1], magenta_col[2], 0.18 * self._pct + 0.08)
                self._head_colors[i].rgba = (core_col[0], core_col[1], core_col[2], 0.70)
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


# ------------------------------------------------------------------
# BUTTON FEEDBACK (patched into NeonButton)
# ------------------------------------------------------------------
def _patch_button(cls):
    orig_init = cls.__init__

    def _init(self, *a, **k):
        orig_init(self, *a, **k)
        try:
            _button_fx(self)
        except Exception as exc:          # noqa: BLE001
            _fail(exc)

    def _refresh(self):
        if hasattr(self, "_calc_hud_colors"):
            ret = self._calc_hud_colors()
            if len(ret) == 6:
                bg, bd, glow, dots, inner, text_color = ret
            else:
                bg, bd, glow, dots, inner = ret
                text_color = (1, 1, 1, 1)
        else:
            r, g, b = self._base[:3]
            if self.state == "down":
                kk = 1.55
            elif self._hover and not self.disabled:
                kk = 1.25
            else:
                kk = 1.0
            bg = (min(1.0, r * kk), min(1.0, g * kk), min(1.0, b * kk), 0.92)
            bd = (min(1.0, r * 1.7 + 0.12), min(1.0, g * 1.7 + 0.12), min(1.0, b * 1.7 + 0.12), 0.95)
            glow = (r, g, b, 0.2)
            dots = bd
            inner = (r * 0.7, g * 0.7, b * 0.7, 0.3)
            text_color = (1, 1, 1, 1)

        self.color = text_color
        if not getattr(self, "_fx_ready", False) or mode() == "off":
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
            return

        dur = 0.05 if self.state == "down" else 0.12
        _stop(self._bg_c)
        _stop(self._bd_c)
        _go(self._bg_c, d=dur, r=bg[0], g=bg[1], b=bg[2], a=bg[3])
        _go(self._bd_c, d=dur, r=bd[0], g=bd[1], b=bd[2], a=bd[3])
        if hasattr(self, "_glow_c"):
            _stop(self._glow_c)
            _go(self._glow_c, d=dur, r=glow[0], g=glow[1], b=glow[2], a=glow[3])
        if hasattr(self, "_glow_c2"):
            _stop(self._glow_c2)
            _go(self._glow_c2, d=dur, r=glow[0], g=glow[1], b=glow[2], a=glow[3] * 0.35)
        if hasattr(self, "_dots_c"):
            _stop(self._dots_c)
            _go(self._dots_c, d=dur, r=dots[0], g=dots[1], b=dots[2], a=dots[3])
        if hasattr(self, "_inner_c"):
            _stop(self._inner_c)
            _go(self._inner_c, d=dur, r=inner[0], g=inner[1], b=inner[2], a=inner[3])

    cls.__init__ = _init
    cls._refresh = _refresh
    cls._fx_pulse = _button_pulse


def _button_fx(btn):
    btn._fx_sc = Scale(1, 1, 1, origin=btn.center)
    btn.canvas.before.insert(0, PushMatrix())
    btn.canvas.before.insert(1, btn._fx_sc)
    with btn.canvas.after:
        btn._fx_rc = Color(1, 1, 1, 0)
        btn._fx_rl = Line(points=[0, 0], close=True, width=dp(1.6))
        PopMatrix()

    def geom(*_):
        btn._fx_sc.origin = btn.center
        if getattr(btn, "variant", "") in ("nav", "nav_active"):
            btn._fx_rl.points = []
            btn._fx_rl.close = False
            return
        if hasattr(btn, "_hud_poly"):
            pts, _ = btn._hud_poly(dp(2.5))
            btn._fx_rl.points = pts
            btn._fx_rl.close = True
        else:
            btn._fx_rl.rounded_rectangle = (btn.x - dp(2), btn.y - dp(2), max(btn.width + dp(4), 2),
                                            max(btn.height + dp(4), 2), dp(7))

    def on_state(_b, state):
        if mode() == "off":
            return
        _stop(btn._fx_sc)
        if state == "down":
            _go(btn._fx_sc, d=0.05, t="out_quad", x=0.96, y=0.96)
        elif getattr(btn, "_hover", False) and not btn.disabled:
            _go(btn._fx_sc, d=0.12, t="out_quad", x=1.02, y=1.02)
        else:
            _go(btn._fx_sc, d=0.14, t="out_back", x=1.0, y=1.0)

    def on_hover(_b, val):
        if mode() == "off" or btn.disabled or btn.state == "down":
            return
        _stop(btn._fx_sc)
        if val:
            _go(btn._fx_sc, d=0.12, t="out_quad", x=1.02, y=1.02)
        else:
            _go(btn._fx_sc, d=0.14, t="out_back", x=1.0, y=1.0)

    def on_press(_b):
        if lively() and getattr(btn, "variant", "") not in ("nav", "nav_active"):
            _button_pulse(btn, 0.55, 0.32)

    def on_disabled(_b, value):
        _stop(btn, "opacity")
        if mode() == "off":
            btn.opacity = 0.45 if value else 1.0
        else:
            _go(btn, d=0.12, opacity=0.45 if value else 1.0)

    btn.bind(pos=geom, size=geom, state=on_state, on_press=on_press, disabled=on_disabled)
    if hasattr(btn, "_hover"):
        btn.bind(_hover=on_hover)
    geom()
    btn._fx_ready = True
    if btn.disabled:
        btn.opacity = 0.45


def _button_pulse(btn, alpha=0.7, dur=0.5):
    """Brief neon outline pulse (also used to highlight the selected nav item)."""
    if getattr(btn, "variant", "") in ("nav", "nav_active"):
        return
    if not hasattr(btn, "_fx_rc") or not lively():
        return
    _stop(btn._fx_rc)
    col = getattr(btn, "_base", (0.0, 0.95, 1.0, 1.0))
    btn._fx_rc.rgba = (min(1.0, col[0] * 1.8 + 0.2), min(1.0, col[1] * 1.8 + 0.2), min(1.0, col[2] * 1.8 + 0.2), alpha)
    _go(btn._fx_rc, d=dur, t="out_quad", a=0.0)


# ------------------------------------------------------------------
# BACKDROP: respect the motion setting + occasional soft light pulse
# ------------------------------------------------------------------
def _patch_backdrop(cls):
    orig_tick = cls._tick

    def _tick(self, dt):
        try:
            m = mode()
            if m == "off":
                if not getattr(self, "_fx_placed", False):
                    self._fx_placed = True
                    orig_tick(self, 0.0)          # draw the grid once, then stay still
                return
            if m == "reduced":
                self._fx_skip = not getattr(self, "_fx_skip", False)
                if self._fx_skip:
                    return
                dt *= 2
            orig_tick(self, dt)
            _pulse(self, dt)
        except Exception as exc:                  # noqa: BLE001
            _fail(exc)

    cls._tick = _tick


def _pulse(bd, dt):
    if not hasattr(bd, "_pu_c"):
        with bd.canvas:
            bd._pu_c = Color(1.0, 0.239, 0.949, 0.0)
            bd._pu_r = Rectangle(pos=(0, 0), size=(0, 0))
        bd._pu_wait = random.uniform(3, 6)
        bd._pu_p = None
    if bd._pu_p is None:
        bd._pu_wait -= dt
        if bd._pu_wait <= 0:
            bd._pu_p = 0.0
        return
    bd._pu_p += dt / 2.2
    p = bd._pu_p
    if p >= 1.0:
        bd._pu_c.a = 0
        bd._pu_p = None
        bd._pu_wait = random.uniform(8, 14)
        return
    bd._pu_c.a = 0.06 * math.sin(math.pi * p)
    bd._pu_r.size = (bd.width, dp(2.2))
    bd._pu_r.pos = (bd.x, bd.y + p * dp(40))


# ------------------------------------------------------------------
# MOOD tiles: smooth highlight + small bounce
# ------------------------------------------------------------------
def _patch_mood(cls):
    orig = cls.update_selected

    def update_selected(self):
        try:
            prev = tuple(self.tile_color.rgba)
        except Exception:
            prev = None
        orig(self)
        try:
            sel = getattr(self.app, "selected_mood", None) == self.mood
            was = getattr(self, "_fx_sel", None)
            self._fx_sel = sel
            if was is None or was == sel or prev is None or mode() == "off":
                return
            target = tuple(self.tile_color.rgba)
            self.tile_color.rgba = prev
            _stop(self.tile_color)
            _go(self.tile_color, d=0.15, r=target[0], g=target[1], b=target[2], a=target[3])
            if sel:
                _stop(self.face, "height")
                self.face.height = dp(37)
                (Animation(height=dp(47), d=0.09, t="out_quad")
                 + Animation(height=dp(37), d=0.28, t="out_bounce")).start(self.face)
        except Exception as exc:                  # noqa: BLE001
            _fail(exc)

    cls.update_selected = update_selected


# ------------------------------------------------------------------
# insights: count-up + replayed bars (only when something is new)
# ------------------------------------------------------------------
_NUM = re.compile(r"^(\D*)(\d+)(.*)$", re.S)


def _count_up(app, label, dur=0.7):
    final = getattr(label, "_src", None)
    if not isinstance(final, str):
        return
    seen = app.__dict__.setdefault("_fx_counted", {})
    if seen.get(id(label)) == final:
        return                                      # unchanged since last animation
    seen[id(label)] = final
    m = _NUM.match(final)
    if not m or int(m.group(2)) <= 0:
        return
    pre, num, post = m.group(1), int(m.group(2)), m.group(3)
    old = getattr(label, "_fx_cev", None)
    if old is not None:
        old.cancel()
    start = time.monotonic()

    @_guarded
    def step(_dt):
        k = (time.monotonic() - start) / dur
        if k >= 1.0:
            label.text = final
            label._fx_cev = None
            return False
        label.text = "%s%d%s" % (pre, int(round(num * _ease_out(k))), post)

    label._fx_cev = Clock.schedule_interval(step, 1 / 30.0)


def _insights_enter(app):
    if not full():
        return
    for name in ("ins_xp", "ins_streak", "ins_rate", "ins_moods"):
        card = getattr(app, name, None)
        lab = getattr(card, "value_label", None)
        if lab is not None:
            _count_up(app, lab)
    bar = getattr(app, "insights_bar", None)
    if bar is not None:
        seen = app.__dict__.setdefault("_fx_barseen", {})
        v = round(bar.value, 2)
        if seen.get("insights") != v and bar.value > 0:
            seen["insights"] = v
            target = bar.value
            bar.value = 0
            bar.animate_to(target)


# ------------------------------------------------------------------
# streak flame: one gentle pulse loop, never duplicated
# ------------------------------------------------------------------
def _sync_streak(app):
    lab = getattr(app, "streak_label", None)
    if lab is None:
        return
    want = full() and app.current_streak() > 0
    on = getattr(app, "_fx_streak_on", False)
    if want and not on:
        app._fx_streak_on = True
        _pulse_streak(app, lab, True)
    elif not want and on:
        app._fx_streak_on = False
        _stop(lab, "opacity")
        lab.opacity = 1


def _pulse_streak(app, lab, down):
    if not getattr(app, "_fx_streak_on", False):
        return
    _go(lab, d=1.2, t="in_out_sine", opacity=0.72 if down else 1.0,
        on_done=lambda: _pulse_streak(app, lab, not down))


# ------------------------------------------------------------------
# wrappers around the app's own methods (originals always run first)
# ------------------------------------------------------------------
def _wrap(cls, name, pre=None, post=None):
    orig = getattr(cls, name)

    def wrapper(self, *a, **k):
        ctx = None
        if pre is not None:
            try:
                ctx = pre(self, *a, **k)
            except Exception as exc:          # noqa: BLE001
                _fail(exc)
        result = orig(self, *a, **k)          # the real behaviour - errors here are NOT hidden
        if post is not None:
            try:
                post(self, ctx, result, *a, **k)
            except Exception as exc:          # noqa: BLE001
                _fail(exc)
        return result

    wrapper.__name__ = name
    wrapper._fx_orig = orig
    setattr(cls, name, wrapper)
    return orig


def _load_pre(self, *a, **k):
    """Honest startup status: read-only check of the save file, keep a copy if unreadable."""
    FX["prefs_path"] = os.path.join(os.path.dirname(self.data_file), "fx_prefs.json")
    _load_prefs()
    status = ("new", "")
    path = self.data_file
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("save file is not a JSON object")
            status = ("ok", "")
        except Exception:                         # noqa: BLE001
            backup = path + ".corrupt-" + datetime.now().strftime("%Y%m%d-%H%M%S")
            try:
                shutil.copy2(path, backup)
                status = ("corrupt", os.path.basename(backup))
            except OSError:
                status = ("corrupt", "")
    FX["load"] = status


def _build_post(self, _ctx, _root):
    """Put the pixel rocket in the header, next to the mascot (decorative, never over inputs)."""
    mascot = getattr(self, "mascot_label", None)
    if mascot and getattr(mascot, "parent", None):
        hdr = mascot.parent
        rocket = PixelRocket(size_hint=(None, 1), width=dp(54))
        try:
            hdr.add_widget(rocket, index=hdr.children.index(mascot) + 1)
            self.fx_rocket = rocket
        except Exception:
            pass
    _apply_transition(self)


def _apply_transition(app):
    try:
        app.pages.transition.duration = 0.15 if lively() else 0.01
    except Exception:
        pass


def _cm_wrapper(cls):
    """Quest completion: original runs first; fx only reads what changed."""
    orig = cls.complete_mission

    def complete_mission(self, index, *args, **kwargs):
        ctx = {"ok": False}
        try:
            if 0 <= index < len(self.missions) and not self.missions[index].get("done", False):
                ctx.update(ok=True, xp=self.xp, level=self.xp // 100 + 1,
                           streak=self.current_streak(), ach=list(self.achievements or []))
        except Exception as exc:                  # noqa: BLE001
            _fail(exc)
        self._fx_ctx = ctx
        try:
            result = orig(self, index, *args, **kwargs)
        finally:
            self._fx_ctx = None
        try:
            _completed(self, ctx, index)
        except Exception as exc:                  # noqa: BLE001
            _fail(exc)
            if ctx.get("celebrated"):             # fall back to the original popup
                try:
                    cls._fx_orig_celebration(self, ctx.get("message", ""))
                except Exception:
                    pass
        return result

    cls.complete_mission = complete_mission


def _completed(app, ctx, index):
    if not ctx.get("ok") or not lively():
        return
    if not (0 <= index < len(app.missions)) or not app.missions[index].get("done"):
        return
    gained = app.xp - ctx["xp"]
    if gained <= 0:
        return                                    # no real reward -> no reward effects
    new_level = app.xp // 100 + 1
    leveled = new_level > ctx["level"]
    new_ach = [a for a in (app.achievements or []) if a not in ctx["ach"]]
    streak_now = app.current_streak()
    milestone = streak_now > ctx["streak"] and streak_now in STREAK_MILESTONES
    lay = layer()

    row = None
    holder = getattr(app, "mission_list", None)
    if holder is not None:
        for w in holder.children:
            if getattr(w, "_fx_index", None) == index:
                row = w
                break
    bar = getattr(app, "xp_bar", None)
    if bar is not None and getattr(bar, "parent", None) is not None:
        xp_x, xp_y = _win_center(bar)
    else:
        xp_x, xp_y = Window.center
    if row is not None and row.parent is not None:
        _row_flash(row)
        ox, oy = _win_center(row)
    else:
        ox, oy = xp_x, xp_y

    lay.burst(ox, oy, 22)
    lay.float_text("+%d XP" % gained, xp_x, xp_y + dp(8), GREEN)
    rocket = getattr(app, "fx_rocket", None)
    if rocket is not None:
        rocket.launch()

    if ctx.get("celebrated"):
        parts = ["+%d XP" % gained]
        if leveled:
            parts.append("LEVEL %d" % new_level)
        if milestone:
            parts.append("\U0001F525 %d-DAY STREAK" % streak_now)
        extra = ("\U0001F3C6 " + ", ".join(new_ach[:2])) if new_ach else ""
        lay.toast("QUEST COMPLETE", "  \u2022  ".join(parts), extra, GREEN)
    if milestone:
        lay.burst(xp_x, xp_y, 14, [YELLOW, PINK])
    if leveled:
        lay.banner("LEVEL UP!\nLEVEL %d" % new_level, GREEN)
        lay.ring(xp_x, xp_y, CYAN)
        lay.flash(CYAN)
        lay.burst(xp_x, xp_y, 28)
        if rocket is not None:
            rocket.celebrate()
        Clock.schedule_once(_guarded(lambda dt: app.play_sound("success")), 0.25)


def _row_flash(row):
    with row.canvas.after:
        c = Color(0.20, 1.0, 0.55, 0.42)
        r = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(4)])

    def sync(*_):
        r.pos = row.pos
        r.size = row.size

    row.bind(pos=sync, size=sync)

    def cleanup():
        try:
            row.unbind(pos=sync, size=sync)
            row.canvas.after.remove(c)
            row.canvas.after.remove(r)
        except Exception:
            pass

    row.opacity = 0.35
    _go(row, d=0.45, t="out_quad", opacity=1.0)
    _go(c, d=0.6, t="out_quad", on_done=cleanup, a=0.0)


def _celebration_wrapper(cls):
    orig = cls.show_celebration
    cls._fx_orig_celebration = orig

    def show_celebration(self, message):
        ctx = getattr(self, "_fx_ctx", None)
        if ctx and ctx.get("ok") and mode() != "off":
            ctx["celebrated"] = True              # compact toast replaces the blocking popup
            ctx["message"] = message
            return None
        return orig(self, message)

    cls.show_celebration = show_celebration


def _blink(self, _dt):
    """Cursor line: blinking cursor + rotating status text (PLAYER ONLINE / QUEST SYSTEM ACTIVE / FOCUS MODE)."""
    self._cursor_on = not getattr(self, "_cursor_on", False)
    lab = getattr(self, "cursor_label", None)
    if lab is None:
        return
    focusing = getattr(self, "focus_ev", None) is not None
    if focusing:
        text, col = "FOCUS MODE", YELLOW
    else:
        names = ("PLAYER ONLINE", "QUEST SYS ACTIVE")
        text = names[int(time.monotonic() // 3.5) % 2] if lively() else names[0]
        col = GREEN
    lab.text = "> " + text + (" _" if self._cursor_on else "  ")
    lab.color = col


# ------------------------------------------------------------------
# motion setting (SETTINGS page)
# ------------------------------------------------------------------
def _mode_text():
    return "\u2728 MOTION: " + FX["mode"].upper()


def _region_post(self, _ctx, _r, body):
    body.add_widget(section("\u2728 MOTION & EFFECTS", PURPLE))
    self.fx_button = NeonButton(text=_mode_text(), bg_color=(0.20, 0.15, 0.45, 1))
    self.fx_button.size_hint_y = None
    self.fx_button.height = dp(40)
    self.fx_button.bind(on_press=lambda *_: cycle_mode(self))
    body.add_widget(self.fx_button)
    body.add_widget(make_label("FULL = all effects. REDUCED = fewer, calmer effects. "
                               "OFF = no decorative animation (buttons still react).",
                               10, MUTED, auto_height=True))


def cycle_mode(app):
    FX["mode"] = MODES[(MODES.index(FX["mode"]) + 1) % len(MODES)]
    FX["fail"] = 0
    _save_prefs()
    apply_mode(app)
    try:
        app.set_status("Motion: %s" % FX["mode"].upper(), CYAN)
    except Exception:
        pass


def apply_mode(app):
    try:
        if hasattr(app, "fx_button"):
            app.fx_button.text = _mode_text()
        for ref in list(_ROCKETS):
            r = ref()
            if r is None:
                _ROCKETS.remove(ref)
            else:
                r._sync_tick()
        _apply_transition(app)
        _sync_streak(app)
        if not lively() and _LAYER is not None:
            _LAYER._kill_toast()
            _LAYER._kill_banner()
    except Exception as exc:                      # noqa: BLE001
        _fail(exc)


# ------------------------------------------------------------------
# install
# ------------------------------------------------------------------
def install(ns, app_cls):
    """Hook everything in. If anything goes wrong the app simply runs without effects."""
    if getattr(app_cls, "_fx_installed", False):
        return
    try:
        for name in _NEEDED:
            globals()[name] = ns[name]
        app_cls._fx_installed = True
        ns["BootScreen"] = FxBoot
        ns["GlitchTitle"] = FxTitle
        _patch_button(NeonButton)
        _patch_backdrop(CyberBackdrop)
        _patch_mood(MoodOption)
        _wrap(app_cls, "load_data", pre=_load_pre)
        _wrap(app_cls, "build", post=_build_post)
        _wrap(app_cls, "make_mission_row",
              post=lambda self, ctx, row, index, mission: setattr(row, "_fx_index", index))
        _celebration_wrapper(app_cls)
        _cm_wrapper(app_cls)

        def _mood_post(self, ctx, _r, *a, **k):
            if lively() and len(self.mood_logs) > ctx:
                layer().toast("MOOD SAVED", str(self.mood_logs[-1].get("mood", "")), "", CYAN)

        _wrap(app_cls, "log_mood", pre=lambda self, *a, **k: len(self.mood_logs), post=_mood_post)

        def _go_post(self, _ctx, _r, name):
            btn = getattr(self, "nav_buttons", {}).get(name)
            if btn is not None and hasattr(btn, "_fx_rc"):
                _button_pulse(btn, 0.7, 0.45)
            if name == "insights":
                _insights_enter(self)

        _wrap(app_cls, "go_page", post=_go_post)
        _wrap(app_cls, "refresh_screen", post=lambda self, ctx, r: _sync_streak(self))
        if hasattr(app_cls, "build_region_section"):
            _wrap(app_cls, "build_region_section", post=_region_post)
        app_cls._blink = _blink
    except Exception as exc:                      # noqa: BLE001
        _fail(exc)
        print("[fx] could not install effects, running without them:", exc)
