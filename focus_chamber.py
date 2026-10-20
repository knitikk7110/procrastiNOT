"""
focus_chamber.py - Cyber Focus Chamber & Pomodoro Deep Work Engine for procrastiNOT.exe

Features:
- Dedicated Pomodoro & Deep Work Engine with custom presets (25m, 45m, 15m, 5m break)
- Custom minute adjusters: [-5 MIN] and [+5 MIN] for granular duration control
- Luminous circular OpenGL progress arc with large high-contrast cyber countdown
- Visual Cyber-Flow Ambiance (peaceful flowing neon particle stream for flow state)
- Mission Target Locking with direct [MARK COMPLETE NOW] button
- Audio feedback using clean retro chimes (no annoying motherboard beeps)
- Prominent [🔙 BASE COMMAND] button for instant navigation
- Reward telemetry: +50 XP per focus sprint, streak bonuses, and Mind Reset Arcade break prompts
"""

import os
import sys
import math
import random
from datetime import datetime

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


class CyberMatrixFlow(Widget):
    """
    Peaceful falling cyber rain particle stream to induce visual flow state.
    Lightweight, smooth 30 FPS OpenGL particle simulation without audio annoyance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self._anim_ev = None
        self.active = True
        self.bind(pos=self._init_particles, size=self._init_particles)

    def _init_particles(self, *_):
        w = max(dp(100), self.width)
        h = max(dp(100), self.height)
        self.particles = []
        for _ in range(28):
            self.particles.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "speed": random.uniform(dp(40), dp(110)),
                "length": random.uniform(dp(8), dp(22)),
                "alpha": random.uniform(0.15, 0.45),
            })

    def start(self):
        if not self._anim_ev:
            self._anim_ev = Clock.schedule_interval(self._tick, 1.0 / 30.0)

    def stop(self):
        if self._anim_ev:
            self._anim_ev.cancel()
            self._anim_ev = None
        self.canvas.clear()

    def _tick(self, dt):
        if not self.active or self.width <= 0 or self.height <= 0:
            return
        bx, by = self.pos
        w, h = self.size
        self.canvas.clear()

        with self.canvas:
            for p in self.particles:
                p["y"] -= p["speed"] * dt
                if p["y"] < 0:
                    p["y"] = h + random.uniform(0, dp(30))
                    p["x"] = random.uniform(0, w)

                px = bx + p["x"]
                py = by + p["y"]
                Color(0.24, 1.0, 0.69, p["alpha"])
                Line(points=[px, py, px, py + p["length"]], width=dp(1.2))


class FocusProgressRing(Widget):
    """Futuristic neon circular progress arc and glowing track gauge."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = 1.0  # 1.0 down to 0.0
        self.phase_color = MINT
        self.bind(pos=self._redraw, size=self._redraw)

    def set_progress(self, ratio, color=MINT):
        self.progress = max(0.0, min(1.0, ratio))
        self.phase_color = color
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        radius = min(self.width, self.height) / 2 - dp(24)
        if radius <= dp(15):
            return

        with self.canvas:
            # Outer dark track
            Color(1, 1, 1, 0.07)
            Line(circle=(cx, cy, radius), width=dp(6))

            # Inner accent ring
            Color(1, 1, 1, 0.03)
            Line(circle=(cx, cy, radius - dp(12)), width=dp(1.2))

            # Ambient luminous glow behind arc
            c = self.phase_color
            Color(c[0], c[1], c[2], 0.18)
            Line(circle=(cx, cy, radius), width=dp(14))

            # Main Progress Arc
            angle = max(0.1, self.progress * 360.0)
            Color(*self.phase_color)
            Line(circle=(cx, cy, radius, 0, angle), width=dp(6.0))

            # Orbiting indicator pulse at head of arc
            rad_ang = math.radians(angle)
            head_x = cx + radius * math.sin(rad_ang)
            head_y = cy + radius * math.cos(rad_ang)
            Color(*WHITE)
            Ellipse(pos=(head_x - dp(5), head_y - dp(5)), size=(dp(10), dp(10)))
            Color(c[0], c[1], c[2], 0.6)
            Ellipse(pos=(head_x - dp(8), head_y - dp(8)), size=(dp(16), dp(16)))


class CyberFocusChamber(FloatLayout):
    """
    Ultimate Cyber Focus Chamber & Pomodoro Deep Work Engine.
    """

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        # Session state
        self.state = "IDLE"  # "FOCUS", "BREAK", "PAUSED", "IDLE"
        self.focus_duration = 25 * 60
        self.break_duration = 5 * 60
        self.current_total = self.focus_duration
        self.time_left = self.focus_duration
        self.is_break = False
        self.completed_sprints = 0
        self.total_focus_seconds = 0
        self.selected_quest_name = "GENERAL FOCUS SPRINT"
        self.flow_mode_active = True

        self._tick_event = None

        self._build_ui()
        self._sync_stats()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(16), dp(10)], size_hint=(1, 1))

        # 1. Top Header & Presets Bar
        header = arcade.ArcadePanel(
            orientation="horizontal", padding=[dp(12), dp(6)], spacing=dp(10),
            size_hint=(1, None), height=dp(56), bg_color=BG_SECONDARY, border_color=CYAN
        )
        title_box = BoxLayout(orientation="vertical", spacing=dp(1), size_hint_x=0.45)
        t_lbl = Label(
            text="[b]⏱️ CYBER FOCUS CHAMBER[/b] // DEEP WORK",
            font_name=TECH_FONT, font_size="15sp", color=CYAN, markup=True, halign="left"
        )
        t_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        sub_lbl = Label(
            text="LOCK IN. ZERO DISTRACTIONS. CONVERT TIME INTO POWER.",
            font_name=TECH_FONT, font_size="10.5sp", color=TEXT_SEC, halign="left"
        )
        sub_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        title_box.add_widget(t_lbl)
        title_box.add_widget(sub_lbl)

        # Presets and Quick Actions
        preset_box = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_x=0.55)
        btn_25 = arcade.ArcadeButton(
            text="🍅 25M", variant="primary", height_dp=36, font_size="12sp",
            size_hint_x=0.22, on_click=lambda: self.set_preset(25, 5)
        )
        btn_45 = arcade.ArcadeButton(
            text="⚡ 45M", variant="secondary", height_dp=36, font_size="12sp",
            size_hint_x=0.22, on_click=lambda: self.set_preset(45, 10)
        )
        btn_15 = arcade.ArcadeButton(
            text="🚀 15M", variant="gold", height_dp=36, font_size="12sp",
            size_hint_x=0.22, on_click=lambda: self.set_preset(15, 3)
        )
        self.flow_btn = arcade.ArcadeButton(
            text="✨ FLOW: ON", variant="mint", height_dp=36, font_size="11.5sp",
            size_hint_x=0.26, on_click=self.toggle_flow_mode
        )
        home_btn = arcade.ArcadeButton(
            text="🔙 BASE", variant="secondary", height_dp=36, font_size="11.5sp",
            size_hint_x=0.20, on_click=lambda: self.app.go_page("home")
        )

        preset_box.add_widget(btn_25)
        preset_box.add_widget(btn_45)
        preset_box.add_widget(btn_15)
        preset_box.add_widget(self.flow_btn)
        preset_box.add_widget(home_btn)

        header.add_widget(title_box)
        header.add_widget(preset_box)
        root.add_widget(header)

        # 2. Main Center Body (Timer Gauge Left, Quest & Telemetry Right)
        center_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint=(1, 1))

        # Circular Timer Card
        timer_card = arcade.ArcadePanel(
            orientation="vertical", padding=[dp(14), dp(12)], spacing=dp(6),
            size_hint=(0.58, 1), bg_color=BG_ELEVATED, border_color=MAGENTA
        )

        # Status Badge & Adjusters Header
        top_ctrl_bar = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint=(1, None), height=dp(30))
        btn_minus = arcade.ArcadeButton(
            text="-5 MIN", variant="secondary", height_dp=28, font_size="11sp",
            size_hint_x=None, width=dp(70), on_click=lambda: self.adjust_time(-5)
        )
        self.phase_badge = Label(
            text="[b]⚡ READY FOR DEEP FOCUS[/b]", font_name=TECH_FONT,
            font_size="14sp", color=MINT, markup=True, halign="center",
            size_hint_x=1
        )
        btn_plus = arcade.ArcadeButton(
            text="+5 MIN", variant="secondary", height_dp=28, font_size="11sp",
            size_hint_x=None, width=dp(70), on_click=lambda: self.adjust_time(5)
        )
        top_ctrl_bar.add_widget(btn_minus)
        top_ctrl_bar.add_widget(self.phase_badge)
        top_ctrl_bar.add_widget(btn_plus)
        timer_card.add_widget(top_ctrl_bar)

        # Progress Ring & Digital Clock Container
        ring_holder = FloatLayout(size_hint=(1, 1))
        self.matrix_flow = CyberMatrixFlow(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        ring_holder.add_widget(self.matrix_flow)

        self.progress_ring = FocusProgressRing(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        ring_holder.add_widget(self.progress_ring)

        # Centered Digital Time Display
        time_box = BoxLayout(
            orientation="vertical", spacing=dp(2), size_hint=(None, None),
            size=(dp(280), dp(110)), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.digits_lbl = Label(
            text="25:00", font_name=TECH_FONT, font_size="52sp",
            bold=True, color=WHITE, halign="center"
        )
        self.sub_state_lbl = Label(
            text="DEEP WORK SPRINT // LOCKED IN", font_name=TECH_FONT,
            font_size="11.5sp", color=TEXT_SEC, halign="center"
        )
        time_box.add_widget(self.digits_lbl)
        time_box.add_widget(self.sub_state_lbl)
        ring_holder.add_widget(time_box)

        timer_card.add_widget(ring_holder)

        # Action Buttons Row
        ctrl_bar = BoxLayout(
            orientation="horizontal", spacing=dp(8), size_hint=(1, None), height=dp(48)
        )
        self.start_btn = arcade.ArcadeButton(
            text="⚡ ENGAGE SPRINT [SPACE]", variant="primary", height_dp=44, font_size="13sp",
            size_hint_x=0.44, on_click=self.toggle_timer
        )
        self.reset_btn = arcade.ArcadeButton(
            text="🔄 RESET", variant="secondary", height_dp=44, font_size="12sp",
            size_hint_x=0.20, on_click=self.reset_timer
        )
        self.skip_btn = arcade.ArcadeButton(
            text="⏩ SKIP", variant="gold", height_dp=44, font_size="12sp",
            size_hint_x=0.18, on_click=self.skip_phase
        )
        self.abort_btn = arcade.ArcadeButton(
            text="🛑 ABORT", variant="danger", height_dp=44, font_size="12sp",
            size_hint_x=0.18, on_click=self.abort_timer
        )
        ctrl_bar.add_widget(self.start_btn)
        ctrl_bar.add_widget(self.reset_btn)
        ctrl_bar.add_widget(self.skip_btn)
        ctrl_bar.add_widget(self.abort_btn)
        timer_card.add_widget(ctrl_bar)

        center_row.add_widget(timer_card)

        # 3. Right Dashboard: Quest Locking & Focus Analytics
        side_card = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(0.42, 1))

        # Target Quest Lock-on Box
        quest_panel = arcade.ArcadePanel(
            orientation="vertical", padding=[dp(12), dp(10)], spacing=dp(6),
            size_hint=(1, None), height=dp(176), bg_color=BG_ELEVATED, border_color=CYAN
        )
        q_head = Label(
            text="[b]🎯 MISSION TARGET LOCK[/b]", font_name=TECH_FONT,
            font_size="13.5sp", color=CYAN, markup=True, halign="left",
            size_hint_y=None, height=dp(20)
        )
        self.quest_target_lbl = Label(
            text="[b]CURRENT TARGET:[/b]\n[size=12.5sp][ GENERAL FOCUS SPRINT ][/size]",
            font_name=TECH_FONT, font_size="12.5sp", color=YELLOW, markup=True,
            halign="left", valign="middle"
        )
        self.quest_target_lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        q_btn_row = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint=(1, None), height=dp(36))
        cycle_target_btn = arcade.ArcadeButton(
            text="🔄 CYCLE QUEST", variant="secondary", height_dp=36, font_size="11.5sp",
            size_hint_x=0.45, on_click=self.cycle_quest_target
        )
        self.finish_quest_btn = arcade.ArcadeButton(
            text="📸 PROVE & CLEAR", variant="mint", height_dp=36, font_size="11.5sp",
            size_hint_x=0.55, on_click=self.complete_active_quest
        )
        q_btn_row.add_widget(cycle_target_btn)
        q_btn_row.add_widget(self.finish_quest_btn)

        q_hint = Label(
            text="💡 Sprints grant +50 XP and unlock prestige themes & titles in the Cyber Vault!",
            font_name=TECH_FONT, font_size="10.5sp", color=TEXT_SEC, halign="left",
            size_hint_y=None, height=dp(26)
        )
        q_hint.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        quest_panel.add_widget(q_head)
        quest_panel.add_widget(self.quest_target_lbl)
        quest_panel.add_widget(q_btn_row)
        quest_panel.add_widget(q_hint)
        side_card.add_widget(quest_panel)

        # Productivity Telemetry Matrix
        telemetry_panel = arcade.ArcadePanel(
            orientation="vertical", padding=[dp(12), dp(10)], spacing=dp(8),
            size_hint=(1, 1), bg_color=BG_ELEVATED, border_color=SEPARATOR
        )
        m_head = Label(
            text="[b]📊 FOCUS TELEMETRY[/b]", font_name=TECH_FONT,
            font_size="13.5sp", color=MAGENTA_CORE, markup=True, halign="left",
            size_hint_y=None, height=dp(20)
        )
        telemetry_panel.add_widget(m_head)

        stat_grid = GridLayout(cols=1, spacing=dp(6), size_hint=(1, 1))
        self.sprints_lbl = Label(
            text="🍅 COMPLETED SPRINTS: [ 0 ]", font_name=TECH_FONT, font_size="13sp",
            color=MINT, bold=True, markup=True, halign="left"
        )
        self.time_stat_lbl = Label(
            text="⏳ TODAY'S MINDFUL TIME: [ 0 MINS ]", font_name=TECH_FONT, font_size="13sp",
            color=WHITE, markup=True, halign="left"
        )
        self.reward_stat_lbl = Label(
            text="⚡ FOCUS SPRINT BONUS: [ +50 XP ]", font_name=TECH_FONT, font_size="13sp",
            color=YELLOW, markup=True, halign="left"
        )
        self.streak_bonus_lbl = Label(
            text="🔥 STREAK MULTIPLIER: [ 1.5x ACTIVE ]", font_name=TECH_FONT, font_size="13sp",
            color=MAGENTA, markup=True, halign="left"
        )
        stat_grid.add_widget(self.sprints_lbl)
        stat_grid.add_widget(self.time_stat_lbl)
        stat_grid.add_widget(self.reward_stat_lbl)
        stat_grid.add_widget(self.streak_bonus_lbl)
        telemetry_panel.add_widget(stat_grid)

        # Quick Mind Reset Arcade shortcut
        arcade_shortcut_btn = arcade.ArcadeButton(
            text="🕹️ MIND RESET ARCADE BREAK", variant="mint", height_dp=38, font_size="12.5sp",
            on_click=lambda: self.app.go_page("arcade")
        )
        telemetry_panel.add_widget(arcade_shortcut_btn)

        side_card.add_widget(telemetry_panel)
        center_row.add_widget(side_card)
        root.add_widget(center_row)

        self.add_widget(root)

        # Completion Celebration Overlay Modal
        self.modal_panel = arcade.ArcadePanel(
            orientation="vertical", padding=[dp(20), dp(16)], spacing=dp(12),
            size_hint=(None, None), size=(dp(430), dp(280)),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            bg_color=(0.04, 0.02, 0.08, 0.98), border_color=MINT
        )
        self.modal_title = Label(
            text="[b]🎉 FOCUS SPRINT COMPLETE![/b]\n[size=13sp]NEURAL DISCIPLINE REWARD[/size]",
            font_name=TECH_FONT, font_size="21sp", color=MINT, markup=True, halign="center"
        )
        self.modal_stats = Label(
            text="MISSION: FOCUS SESSION EARNED!\n+50 XP BONUS CREDITED\nSTREAK MAINTAINED 🔥",
            font_name=TECH_FONT, font_size="14.5sp", color=WHITE, bold=True, markup=True, halign="center"
        )
        modal_btn_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint=(1, None), height=dp(44))
        self.next_round_btn = arcade.ArcadeButton(
            text="🌿 5M RECHARGE BREAK", variant="gold", height_dp=42, font_size="12.5sp",
            size_hint_x=0.5, on_click=self.start_break_phase
        )
        self.arcade_break_btn = arcade.ArcadeButton(
            text="🎮 PLAY ARCADE", variant="primary", height_dp=42, font_size="12.5sp",
            size_hint_x=0.5, on_click=self._go_arcade_from_modal
        )
        modal_btn_row.add_widget(self.next_round_btn)
        modal_btn_row.add_widget(self.arcade_break_btn)

        self.modal_panel.add_widget(self.modal_title)
        self.modal_panel.add_widget(self.modal_stats)
        self.modal_panel.add_widget(modal_btn_row)
        self.modal_panel.opacity = 0
        self.modal_panel.disabled = True
        self.add_widget(self.modal_panel)

    def on_enter(self):
        Window.bind(on_key_down=self._on_key_down)
        self.matrix_flow.start()
        self.cycle_quest_target(init_only=True)
        self._sync_stats()
        self._update_display()

    def on_leave(self):
        Window.unbind(on_key_down=self._on_key_down)
        self.matrix_flow.stop()

    def _on_key_down(self, _win, key, scancode, codepoint, modifier):
        if not self.parent or self.opacity == 0:
            return False
        if key in (32, 13):  # Space or Enter
            if self.modal_panel.opacity > 0:
                self.start_break_phase()
                return True
            self.toggle_timer()
            return True
        return False

    def adjust_time(self, delta_mins):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        new_mins = max(1, min(180, int(self.current_total // 60) + delta_mins))
        if not self.is_break:
            self.focus_duration = new_mins * 60
        else:
            self.break_duration = new_mins * 60
        self.current_total = new_mins * 60
        self.time_left = self.current_total
        self._update_display()

    def set_preset(self, focus_mins, break_mins):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        self.stop_loop()
        self.state = "IDLE"
        self.is_break = False
        self.focus_duration = focus_mins * 60
        self.break_duration = break_mins * 60
        self.current_total = self.focus_duration
        self.time_left = self.focus_duration
        self.phase_badge.text = f"[b]⚡ READY: {focus_mins}M FOCUS SPRINT[/b]"
        self.phase_badge.color = CYAN
        self.sub_state_lbl.text = "DEEP WORK SPRINT // LOCKED IN"
        self.start_btn.text = "⚡ ENGAGE SPRINT [SPACE]"
        self.modal_panel.opacity = 0
        self.modal_panel.disabled = True
        self._update_display()

    def toggle_timer(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        if self.state in ("FOCUS", "BREAK"):
            # Pause
            self.state = "PAUSED"
            self.stop_loop()
            self.start_btn.text = "▶ RESUME SPRINT"
            self.phase_badge.text = "[b]⏸️ SPRINT PAUSED[/b]"
            self.phase_badge.color = YELLOW
        else:
            # Start or Resume
            if not self.is_break:
                self.state = "FOCUS"
                self.phase_badge.text = "[b]⚡ DEEP FOCUS SPRINT IN PROGRESS[/b]"
                self.phase_badge.color = MINT
                self.sub_state_lbl.text = f"TARGET: {self.selected_quest_name[:28]}"
            else:
                self.state = "BREAK"
                self.phase_badge.text = "[b]🌿 SYSTEM RECHARGE BREAK ACTIVE[/b]"
                self.phase_badge.color = YELLOW
                self.sub_state_lbl.text = "TAKE A DEEP BREATH. RELAX YOUR EYES."

            self.start_btn.text = "⏸️ PAUSE"
            self.stop_loop()
            self._tick_event = Clock.schedule_interval(self._tick, 1.0)
            self._update_display()

    def reset_timer(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        self.stop_loop()
        self.state = "IDLE"
        self.time_left = self.current_total
        self.phase_badge.text = "[b]⚡ READY FOR DEEP FOCUS[/b]"
        self.phase_badge.color = MINT
        self.start_btn.text = "⚡ ENGAGE SPRINT [SPACE]"
        self.sub_state_lbl.text = "DEEP WORK SPRINT // LOCKED IN"
        self._update_display()

    def abort_timer(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        self.stop_loop()
        self.state = "IDLE"
        self.is_break = False
        self.time_left = self.focus_duration
        self.current_total = self.focus_duration
        self.phase_badge.text = "[b]⚡ READY FOR DEEP FOCUS[/b]"
        self.phase_badge.color = MINT
        self.start_btn.text = "⚡ ENGAGE SPRINT [SPACE]"
        self.sub_state_lbl.text = "DEEP WORK SPRINT // LOCKED IN"
        self.modal_panel.opacity = 0
        self.modal_panel.disabled = True
        self._update_display()

    def skip_phase(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        if not self.is_break:
            self.start_break_phase()
        else:
            self.set_preset(int(self.focus_duration / 60), int(self.break_duration / 60))

    def _tick(self, _dt):
        if self.state not in ("FOCUS", "BREAK"):
            return

        self.time_left -= 1
        if self.state == "FOCUS":
            self.total_focus_seconds += 1

        if self.time_left <= 0:
            self.time_left = 0
            self._on_phase_finished()
        self._update_display()

    def _on_phase_finished(self):
        self.stop_loop()
        if not self.is_break:
            # Focus sprint finished successfully!
            self.completed_sprints += 1
            self.app.focus_sprints = getattr(self.app, "focus_sprints", 0) + 1
            if hasattr(self.app, "add_xp"):
                self.app.add_xp(50, reason="FOCUS SPRINT")
            else:
                self.app.xp += 50
                self.app.save_data()

            arcade.ArcadeAudio.play("level_up", self.app.sound_enabled)

            # Record focus minutes to app data
            focus_mins = int(self.focus_duration / 60)
            today_str = datetime.now().strftime("%Y-%m-%d")
            if today_str not in self.app.completed_dates:
                self.app.completed_dates.append(today_str)
            self.app.save_data()

            self.modal_title.text = "[b]🎉 FOCUS SPRINT COMPLETE![/b]\n[size=13sp]NEURAL DISCIPLINE REWARD[/size]"
            self.modal_title.color = MINT
            self.modal_stats.text = (
                f"CLEARED: {focus_mins} MIN FOCUS SPRINT!\n"
                f"+50 XP CREDITED (TOTAL XP: {self.app.xp})\n"
                f"SPRINTS TODAY: [ {self.completed_sprints} ]"
            )
            self.modal_panel.opacity = 1
            self.modal_panel.disabled = False
        else:
            # Break finished
            arcade.ArcadeAudio.play("click", self.app.sound_enabled)
            self.set_preset(int(self.focus_duration / 60), int(self.break_duration / 60))

        self._sync_stats()

    def start_break_phase(self, *_):
        self.modal_panel.opacity = 0
        self.modal_panel.disabled = True
        self.is_break = True
        self.state = "BREAK"
        self.current_total = self.break_duration
        self.time_left = self.break_duration
        self.phase_badge.text = "[b]🌿 SYSTEM RECHARGE BREAK ACTIVE[/b]"
        self.phase_badge.color = YELLOW
        self.start_btn.text = "⏸️ PAUSE"
        self.sub_state_lbl.text = "SYSTEM RESTORATION // RECHARGE PROTOCOL"
        self.stop_loop()
        self._tick_event = Clock.schedule_interval(self._tick, 1.0)
        self._update_display()

    def _go_arcade_from_modal(self, *_):
        self.modal_panel.opacity = 0
        self.modal_panel.disabled = True
        self.app.go_page("arcade")

    def _update_display(self):
        m = int(self.time_left // 60)
        s = int(self.time_left % 60)
        self.digits_lbl.text = f"{m:02d}:{s:02d}"

        ratio = (self.time_left / self.current_total) if self.current_total > 0 else 0.0
        color = YELLOW if self.is_break else (MINT if self.state != "PAUSED" else YELLOW)
        self.progress_ring.set_progress(ratio, color=color)

    def _sync_stats(self):
        self.sprints_lbl.text = f"🍅 COMPLETED SPRINTS: [ {self.completed_sprints} ]"
        mins = int(self.total_focus_seconds // 60)
        self.time_stat_lbl.text = f"⏳ TODAY'S MINDFUL TIME: [ {mins} MINS ]"

    def cycle_quest_target(self, init_only=False, *_):
        if not init_only:
            arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        active_missions = [m.get("name", "Task") for m in self.app.missions if not m.get("done", False)]
        if not active_missions:
            self.selected_quest_name = "GENERAL FOCUS SPRINT"
        else:
            if init_only:
                self.selected_quest_name = active_missions[0]
            else:
                try:
                    idx = active_missions.index(self.selected_quest_name)
                    next_idx = (idx + 1) % len(active_missions)
                    self.selected_quest_name = active_missions[next_idx]
                except ValueError:
                    self.selected_quest_name = active_missions[0]

        self.quest_target_lbl.text = f"[b]CURRENT TARGET:[/b]\n[size=12.5sp][ {self.selected_quest_name} ][/size]"

    def complete_active_quest(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        target_idx = -1
        for idx, m in enumerate(self.app.missions):
            if not m.get("done", False) and m.get("name") == self.selected_quest_name:
                target_idx = idx
                break

        if target_idx >= 0:
            self.app.open_proof_verification(target_idx)
        else:
            self.app.set_status("⚠️ Select an active quest directive to submit proof.", (1.0, 0.85, 0.30, 1.0))

    def toggle_flow_mode(self, *_):
        arcade.ArcadeAudio.play("click", self.app.sound_enabled)
        self.flow_mode_active = not self.flow_mode_active
        self.matrix_flow.active = self.flow_mode_active
        if not self.flow_mode_active:
            self.matrix_flow.canvas.clear()
        self.flow_btn.text = "✨ FLOW: ON" if self.flow_mode_active else "✨ FLOW: OFF"

    def stop_loop(self):
        if self._tick_event:
            self._tick_event.cancel()
            self._tick_event = None


class FocusScreen(Screen):
    """Screen wrapper for Cyber Focus Chamber."""
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.focus_chamber = CyberFocusChamber(app=app)
        self.add_widget(self.focus_chamber)

    def on_enter(self):
        super().on_enter()
        self.focus_chamber.on_enter()

    def on_leave(self):
        super().on_leave()
        self.focus_chamber.stop_loop()
        self.focus_chamber.on_leave()


def create_focus_screen(app):
    """Factory function for creating the Cyber Focus Chamber Screen."""
    return FocusScreen(app=app, name="focus")
