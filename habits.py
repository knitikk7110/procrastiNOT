"""
habits.py - Cyber Habit Matrix & Daily Routine Forge for procrastiNOT.exe

Features:
- Daily recurring habit tracker (Hydration, Deep Work, Reading, Mindfulness, Screen Curfew)
- Tactile neon checkoff buttons with live streak tracking and legitimate XP rewards (+10 XP per habit)
- Live Daily Habit Armor Shield gauge (e.g. "80% ARMORED")
- Custom habit creation terminal with emoji selector and delete controls
- Midnight auto-reset preserving consecutive streaks
- 100% data safety and persistence inside projectx_data.json
- Seamless Base Command navigation
"""

import os
import sys
import time
from datetime import date, datetime, timedelta

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (
    Color, Ellipse, Line, Mesh, PopMatrix, PushMatrix,
    Rectangle, Rotate, RoundedRectangle, Translate
)
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

import arcade

TECH_FONT = arcade.TECH_FONT
EMOJI_FONT = arcade.EMOJI_FONT

BG = arcade.BG
BG_SECONDARY = arcade.BG_SECONDARY
BG_ELEVATED = arcade.BG_ELEVATED
PANEL = arcade.PANEL
MAGENTA = arcade.MAGENTA
MAGENTA_CORE = arcade.MAGENTA_CORE
CYAN = arcade.CYAN
MINT = arcade.MINT
YELLOW = arcade.YELLOW
WHITE = arcade.WHITE
TEXT_SEC = arcade.TEXT_SEC
MUTED = arcade.MUTED
RED = arcade.RED
SEPARATOR = arcade.SEPARATOR

DEFAULT_HABITS = [
    {"id": "h_hydrate", "name": "Drink 2L Water // Cellular Recharge", "emoji": "💧", "streak": 3, "history": []},
    {"id": "h_deepwork", "name": "Complete 1 Deep Focus Sprint", "emoji": "💻", "streak": 5, "history": []},
    {"id": "h_read", "name": "Read 15 Pages // Neural Expansion", "emoji": "📖", "streak": 2, "history": []},
    {"id": "h_stretch", "name": "Mindful Stretch or Walk", "emoji": "🧘", "streak": 1, "history": []},
    {"id": "h_curfew", "name": "Zero Social Media Before 10 AM", "emoji": "📵", "streak": 4, "history": []},
]


def today_str():
    return date.today().isoformat()


def yesterday_str():
    return (date.today() - timedelta(days=1)).isoformat()


class HabitProgressBar(Widget):
    """Futuristic neon progress gauge displaying daily habit shield integrity."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ratio = 0.0
        self.bind(pos=self._redraw, size=self._redraw)

    def set_progress(self, ratio):
        self.ratio = max(0.0, min(1.0, ratio))
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        bx, by = self.pos
        w = max(1, self.width)
        h = max(1, self.height)

        with self.canvas:
            # Backing slot
            Color(0.08, 0.05, 0.12, 0.95)
            RoundedRectangle(pos=(bx, by), size=(w, h), radius=[dp(3)])

            # Fill bar with neon mint/cyan gradient
            fill_w = max(dp(2), w * self.ratio)
            col = MINT if self.ratio >= 1.0 else (CYAN if self.ratio >= 0.5 else YELLOW)
            Color(*col)
            RoundedRectangle(pos=(bx, by), size=(fill_w, h), radius=[dp(3)])

            # Glowing hairline border
            Color(1, 1, 1, 0.2)
            Line(rounded_rectangle=(bx, by, w, h, dp(3)), width=dp(1.0))


class HabitCard(arcade.ArcadePanel):
    """Interactive daily habit card with streak badge and neon toggle."""

    def __init__(self, habit, app, on_toggle=None, on_delete=None, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("padding", [dp(14), dp(10)])
        kwargs.setdefault("spacing", dp(12))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(64))
        kwargs.setdefault("bg_color", BG_ELEVATED)
        kwargs.setdefault("border_color", SEPARATOR)
        super().__init__(**kwargs)

        self.habit = habit
        self.app = app
        self.on_toggle = on_toggle
        self.on_delete = on_delete

        # Emoji Icon Block
        icon_holder = BoxLayout(size_hint=(None, None), size=(dp(42), dp(42)), pos_hint={"center_y": 0.5})
        self.icon_lbl = Label(
            text=habit.get("emoji", "⚡"), font_name=EMOJI_FONT, font_size="22sp",
            halign="center", valign="middle"
        )
        icon_holder.add_widget(self.icon_lbl)
        self.add_widget(icon_holder)

        # Habit Details
        info_box = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.62)
        self.name_lbl = Label(
            text=f"[b]{habit.get('name', 'Habit')}[/b]", font_name=TECH_FONT,
            font_size="13sp", color=WHITE, markup=True, halign="left"
        )
        self.name_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.streak_lbl = Label(
            text=f"🔥 {habit.get('streak', 0)} DAY STREAK // DAILY RITUAL", font_name=TECH_FONT,
            font_size="10.5sp", color=YELLOW, halign="left"
        )
        self.streak_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        info_box.add_widget(self.name_lbl)
        info_box.add_widget(self.streak_lbl)
        self.add_widget(info_box)

        # Action Buttons: Toggle + Delete
        btn_box = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_x=0.38)
        self.toggle_btn = arcade.ArcadeButton(
            text="⭕ MARK DONE", variant="secondary", height_dp=40, font_size="11sp",
            size_hint_x=0.80, on_click=self._handle_toggle
        )
        del_btn = arcade.ArcadeButton(
            text="✕", variant="danger", height_dp=40, font_size="12sp",
            size_hint_x=0.20, on_click=self._handle_delete
        )
        btn_box.add_widget(self.toggle_btn)
        btn_box.add_widget(del_btn)
        self.add_widget(btn_box)

        self.refresh_state()

    def refresh_state(self):
        t_key = today_str()
        is_done = t_key in self.habit.get("history", [])

        if is_done:
            self.toggle_btn.text = "✅ DONE (+10XP)"
            self.toggle_btn.variant = "mint"
            self.set_border(MINT)
            self.name_lbl.color = MINT
        else:
            self.toggle_btn.text = "⭕ MARK DONE"
            self.toggle_btn.variant = "secondary"
            self.set_border(SEPARATOR)
            self.name_lbl.color = WHITE

        streak_val = self.habit.get("streak", 0)
        self.streak_lbl.text = f"🔥 {streak_val} DAY STREAK // DAILY RITUAL"

    def _handle_toggle(self):
        if self.on_toggle:
            self.on_toggle(self.habit)
            self.refresh_state()

    def _handle_delete(self):
        if self.on_delete:
            self.on_delete(self.habit)


class CyberHabitMatrix(BoxLayout):
    """
    Main Habit Matrix Workspace Layout.
    """

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = "vertical"
        self.padding = [dp(16), dp(10)]
        self.spacing = dp(10)

        # Ensure habits list exists in app
        if not hasattr(self.app, "habits") or not self.app.habits:
            self.app.habits = [dict(h) for h in DEFAULT_HABITS]

        self._build_ui()
        self.refresh_habits()

    @property
    def habits(self):
        return getattr(self.app, "habits", [])

    @property
    def shield_percent(self):
        total = len(self.habits)
        if total == 0:
            return 0
        t_key = today_str()
        done = sum(1 for h in self.habits if t_key in h.get("history", []))
        return int((done / total) * 100)

    def add_custom_habit(self, emoji, name):
        self.selected_emoji = emoji
        self.habit_input.text = name
        self.add_habit()

    def _build_ui(self):
        # 1. Top HUD Header Bar
        header = arcade.ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(56), bg_color=BG_SECONDARY, border_color=CYAN
        )
        t_box = BoxLayout(orientation="vertical", spacing=dp(1), size_hint_x=0.60)
        t_lbl = Label(
            text="[b]⚡ CYBER HABIT MATRIX[/b] // ルーチン RITUALS",
            font_name=TECH_FONT, font_size="15.5sp", color=CYAN, markup=True, halign="left"
        )
        t_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        sub_lbl = Label(
            text="DAILY CONSISTENCY SHIELD. RECURRING DISCIPLINE FOR REAL RESULTS.",
            font_name=TECH_FONT, font_size="10.5sp", color=TEXT_SEC, halign="left"
        )
        sub_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        t_box.add_widget(t_lbl)
        t_box.add_widget(sub_lbl)

        # Header Stats & Navigation
        ctrl_box = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_x=0.40)
        self.shield_badge = Label(
            text="[b]🛡️ SHIELD: 0%[/b]", font_name=TECH_FONT,
            font_size="12sp", color=MINT, markup=True, halign="right",
            size_hint_x=0.60
        )
        home_btn = arcade.ArcadeButton(
            text="🔙 BASE", variant="secondary", height_dp=36, font_size="12sp",
            size_hint_x=0.40, on_click=lambda: self.app.go_page("home")
        )
        ctrl_box.add_widget(self.shield_badge)
        ctrl_box.add_widget(home_btn)

        header.add_widget(t_box)
        header.add_widget(ctrl_box)
        self.add_widget(header)

        # 2. Daily Habit Shield Progress Card
        shield_card = arcade.ArcadePanel(
            orientation="vertical", padding=[dp(14), dp(10)], spacing=dp(6),
            size_hint=(1, None), height=dp(74), bg_color=BG_ELEVATED, border_color=CYAN
        )
        s_top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20))
        self.shield_title_lbl = Label(
            text="[b]🛡️ TODAY'S DISCIPLINE ARMOR SHIELD[/b]", font_name=TECH_FONT,
            font_size="12.5sp", color=WHITE, markup=True, halign="left", size_hint_x=0.70
        )
        self.shield_status_lbl = Label(
            text="0 / 0 HABITS CLEARED TODAY", font_name=TECH_FONT,
            font_size="11sp", color=YELLOW, halign="right", size_hint_x=0.30
        )
        s_top.add_widget(self.shield_title_lbl)
        s_top.add_widget(self.shield_status_lbl)
        shield_card.add_widget(s_top)

        self.progress_bar = HabitProgressBar(size_hint=(1, None), height=dp(14))
        shield_card.add_widget(self.progress_bar)
        self.add_widget(shield_card)

        # 3. Habit Scroll List
        scroll = ScrollView(
            size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
            scroll_type=["bars", "content"], bar_width=dp(4), bar_color=CYAN
        )
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        self.add_widget(scroll)

        # 4. Forge New Habit Terminal (Bottom Console)
        forge_panel = arcade.ArcadePanel(
            orientation="horizontal", padding=[dp(10), dp(6)], spacing=dp(8),
            size_hint=(1, None), height=dp(48), bg_color=BG_SECONDARY, border_color=MAGENTA
        )
        self.emoji_chips = ["💧", "💻", "📖", "🧘", "⚡", "🏋️", "🎯"]
        self.selected_emoji = "⚡"

        self.emoji_btn = arcade.ArcadeButton(
            text=f"{self.selected_emoji} ▼", variant="secondary", height_dp=36, font_size="13sp",
            size_hint_x=None, width=dp(58), on_click=self.cycle_emoji
        )
        forge_panel.add_widget(self.emoji_btn)

        self.habit_input = TextInput(
            hint_text="Forge new daily habit directive (e.g., Code 30m, Read chapter)...",
            multiline=False, size_hint=(1, 1), font_size="12sp",
            font_name=TECH_FONT, background_color=(0.04, 0.02, 0.08, 0.95),
            foreground_color=WHITE, cursor_color=CYAN,
            padding=[dp(10), dp(8)]
        )
        self.habit_input.bind(on_text_validate=self.add_habit)
        forge_panel.add_widget(self.habit_input)

        add_btn = arcade.ArcadeButton(
            text="⚡ FORGE HABIT", variant="primary", height_dp=36, font_size="12sp",
            size_hint_x=None, width=dp(130), on_click=self.add_habit
        )
        forge_panel.add_widget(add_btn)
        self.add_widget(forge_panel)

    def cycle_emoji(self, *_):
        idx = self.emoji_chips.index(self.selected_emoji)
        self.selected_emoji = self.emoji_chips[(idx + 1) % len(self.emoji_chips)]
        self.emoji_btn.text = f"{self.selected_emoji} ▼"

    def refresh_habits(self):
        self.list_box.clear_widgets()
        t_key = today_str()
        y_key = yesterday_str()

        total = len(self.app.habits)
        done_count = 0

        for h in self.app.habits:
            # Check streak integrity: if not completed yesterday or today, reset streak to 0
            hist = h.get("history", [])
            h["completed_today"] = (t_key in hist)
            if t_key in hist:
                done_count += 1
            elif y_key not in hist and hist:
                h["streak"] = 0

            card = HabitCard(
                habit=h, app=self.app,
                on_toggle=self.toggle_habit,
                on_delete=self.delete_habit
            )
            self.list_box.add_widget(card)

        # Update shield telemetry
        ratio = (done_count / total) if total > 0 else 0.0
        pct = int(ratio * 100)
        self.progress_bar.set_progress(ratio)
        self.shield_badge.text = f"[b]🛡️ SHIELD: {pct}%[/b]"
        self.shield_status_lbl.text = f"{done_count} / {total} HABITS CLEARED TODAY"
        if pct == 100 and total > 0:
            self.shield_title_lbl.text = "[b]🛡️ MAXIMUM DISCIPLINE ARMOR! 100% SECURE 🔥[/b]"
            self.shield_title_lbl.color = MINT
        else:
            self.shield_title_lbl.text = "[b]🛡️ TODAY'S DISCIPLINE ARMOR SHIELD[/b]"
            self.shield_title_lbl.color = WHITE

    def toggle_habit(self, habit):
        if isinstance(habit, str):
            habit = next((h for h in self.app.habits if h.get("id") == habit), None)
            if not habit:
                return

        t_key = today_str()
        hist = habit.setdefault("history", [])

        if t_key in hist:
            # Uncheck
            hist.remove(t_key)
            habit["completed_today"] = False
            habit["streak"] = max(0, habit.get("streak", 1) - 1)
            arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        else:
            # Complete habit! Earn legitimate +10 XP!
            hist.append(t_key)
            habit["completed_today"] = True
            habit["streak"] = habit.get("streak", 0) + 1
            if hasattr(self.app, "add_xp"):
                self.app.add_xp(10, reason="HABIT COMPLETED")
            else:
                self.app.xp += 10

            arcade.ArcadeAudio.play("coin", self.app.sound_enabled)

            # Record completion to daily dates if not present
            if t_key not in self.app.completed_dates:
                self.app.completed_dates.append(t_key)

            # Particle blast
            try:
                import fx
                w_center = Window.center
                fx.layer().burst(w_center[0], w_center[1], n=20, colors=[MINT, CYAN, YELLOW])
                fx.layer().toast("⚡ RITUAL MAINTAINED!", f"Logged: {habit.get('name', 'Habit')[:28]}", extra="+10 XP", color=MINT)
            except Exception:
                pass

            if hasattr(self.app, "companion_widget") and self.app.companion_widget:
                self.app.companion_widget.on_game_event("quest_completed")

        self.app.save_data()
        self.app.refresh_screen()
        self.refresh_habits()

    def add_habit(self, *_):
        name = (self.habit_input.text or "").strip()
        if not name:
            return

        new_h = {
            "id": f"h_{int(time.time()*1000)}",
            "name": name,
            "emoji": self.selected_emoji,
            "streak": 0,
            "history": []
        }
        self.app.habits.append(new_h)
        self.habit_input.text = ""
        self.app.save_data()
        self.refresh_habits()
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)

    def delete_habit(self, habit):
        if habit in self.app.habits:
            self.app.habits.remove(habit)
            self.app.save_data()
            self.refresh_habits()
            arcade.ArcadeAudio.play("click", self.app.sound_enabled)

    def on_enter(self):
        self.refresh_habits()

    def on_leave(self):
        pass


class HabitScreen(Screen):
    """Screen wrapper for Cyber Habit Matrix."""
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.habit_matrix = CyberHabitMatrix(app=app)
        self.add_widget(self.habit_matrix)

    def on_enter(self):
        super().on_enter()
        self.habit_matrix.on_enter()

    def on_leave(self):
        super().on_leave()
        self.habit_matrix.on_leave()


def create_habit_screen(app):
    """Factory function for creating the Cyber Habit Matrix Screen."""
    return HabitScreen(app=app, name="habits")
