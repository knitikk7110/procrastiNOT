"""
companion.py - Living Cyberpunk RPG Companion System for procrastiNOT.exe
Provides:
- 3 Distinct Pixel-Art Companions (NEX, GLITCH, ZERO)
- Multi-state sprite animation engine (idle, react, celebrate)
- Offline prerecorded character-specific dialogue pools
- Windows mouse hover & Android touch reactivity
- First-launch "CHOOSE YOUR OPERATOR" selection modal & settings integration
- Event hooks for quests, XP, streaks, and achievements
"""

import os
import random
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "characters")

# Color Tokens
MAGENTA = (1.0, 0.08, 0.58, 1.0)
MAGENTA_CORE = (1.0, 0.40, 0.78, 1.0)
CYAN = (0.0, 0.90, 1.0, 1.0)
MINT = (0.0, 1.0, 0.65, 1.0)
YELLOW = (1.0, 0.88, 0.20, 1.0)
WHITE = (0.95, 0.97, 1.0, 1.0)
MUTED = (0.55, 0.58, 0.68, 1.0)
BG_PANEL = (0.07, 0.05, 0.12, 0.96)
BG_CARD = (0.11, 0.08, 0.18, 0.95)
def _pick_font(*paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return Label().font_name

TECH_FONT = _pick_font("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/lucon.ttf")

# --------------------------------------------------------------------------
# 1. OPERATOR DEFINITIONS & PRERECORDED DIALOGUE
# --------------------------------------------------------------------------

OPERATORS = {
    "nex": {
        "id": "nex",
        "name": "NEX",
        "title": "THE HACKER",
        "role": "NEURAL INFILTRATOR",
        "tagline": "Sarcastic, clever, and always three moves ahead.",
        "bio": "Wears an oversized jacket and neon cyberdeck. Treats your task list like a high-stakes mainframe to breach.",
        "color": MAGENTA,
        "accent_hex": "#FF1493",
        "dialogues": {
            "first_launch": [
                "Neural link established. Try not to embarrass me out there.",
                "Operator Nex online. Let's breach this task list before lunch.",
            ],
            "welcome": [
                "Oh, look. The human has returned to the main quest.",
                "Back in the chair? Good. The mission log is waiting.",
                "Connection restored. Let's see if productivity follows.",
            ],
            "idle": [
                "Your potential is online. Your productivity? Questionable.",
                "Scanning memory... detected zero active focus sprints.",
                "Procrastination is just malware running in your brain.",
                "I'm compiling your excuse database. It's getting large.",
                "Are we grinding today, or just staring at the terminal?",
            ],
            "hover": [
                "Stop hovering over me and start clicking quests.",
                "Scanning cursor... yep, that's procrastination behavior.",
                "Need a hint or just admiring my cyberdeck?",
            ],
            "tap": [
                "Hey! Careful with the jacket, that's custom fiber optics.",
                "Poking me won't write your code for you.",
                "Input received. Now redirect that energy into a task.",
                "Touch detected. I'm an operator, not a stress ball.",
            ],
            "quest_started": [
                "New mission accepted. Try not to ghost this one.",
                "Target acquired. Commencing operational sprint.",
                "Quest logged. The clock is officially running.",
            ],
            "quest_completed": [
                "Quest cleared. Okay, main character energy.",
                "Target neutralized. Even I'm slightly impressed.",
                "Mission complete. Your XP has been securely routed.",
            ],
            "quest_failed": [
                "The quest is still waiting. No pressure. Mostly.",
                "Deadline breached? Time to execute a counter-attack.",
            ],
            "xp_gained": [
                "XP acquired. The build is getting stronger.",
                "+25 XP logged into the neural core.",
            ],
            "streak_milestone": [
                "Streak updated. The consistency arc is real.",
                "Combo maintained. Don't drop the packet now.",
            ],
            "achievement_unlocked": [
                "Achievement unlocked. Finally, some actual lore.",
                "Badge decrypted. Wear it with pride, human.",
            ],
            "return_after_inactivity": [
                "Welcome back. The procrastination counter was ticking.",
                "You survived the outside world? Back to the grind.",
            ],
            "settings_interaction": [
                "Tinkering with the config? Don't break my cyberdeck.",
            ],
        },
    },
    "glitch": {
        "id": "glitch",
        "name": "GLITCH",
        "title": "THE REBEL",
        "role": "ARCADE STRIKER",
        "tagline": "Chaotic, energetic, competitive, and loud.",
        "bio": "Street rebel with electric-blue hair and a cybernetic arm. Believes life is an arcade game you're meant to beat.",
        "color": CYAN,
        "accent_hex": "#00E5FF",
        "dialogues": {
            "first_launch": [
                "PLAYER DETECTED. LET'S MAKE SOME NOISE!",
                "Glitch in the system! Let's conquer this quest log!",
            ],
            "welcome": [
                "PLAYER DETECTED. LET'S MAKE SOME PROGRESS!",
                "ROUND TWO! Ready to smash through the to-do list?!",
                "You're back! The streak combo is waiting for you!",
            ],
            "idle": [
                "Standing still loses the combo! Pick a quest!",
                "My cyber arm is itching for action. Let's grind!",
                "Are we setting high scores or just spectating?",
                "Idle timer running! High-score players never rest!",
                "Energy levels full. Waiting on user execution!",
            ],
            "hover": [
                "Hands off the cyber arm! Unless you're ready to fight!",
                "Quick reflexes! Now use that speed on your missions!",
                "Target locked! What are we smashing next?",
            ],
            "tap": [
                "Boom! Ready for action! Pick a mission already!",
                "That's a direct hit! Now hit your deadlines like that!",
                "Arcade mode: ENGAGED! Let's get moving!",
                "Cyber arm calibrated! Let's stack that XP!",
            ],
            "quest_started": [
                "NEW MISSION LOCKED IN! GO SMASH IT!",
                "CHALLENGE ACCEPTED! No retreating, player!",
                "OBJECTIVE MARKED! Speedrun this quest!",
            ],
            "quest_completed": [
                "You actually did the quest? Character development!",
                "STAGE CLEAR! THAT'S HOW IT'S DONE!",
                "XP ACQUIRED. THE GRIND CONTINUES!",
            ],
            "quest_failed": [
                "Don't let the boss win! Reroll and clear it!",
                "Drop the excuse, pick up the pace! Next round!",
            ],
            "xp_gained": [
                "XP ACQUIRED. THE GRIND CONTINUES!",
                "+25 XP! We're stacking those numbers!",
            ],
            "streak_milestone": [
                "STREAK MULTIPLIER ACTIVE! DON'T DROP THE COMBO!",
                "UNSTOPPABLE! The streak counter is on fire!",
            ],
            "achievement_unlocked": [
                "ACHIEVEMENT SECURED! WE LEVELING UP FOR REAL!",
                "TROPHY UNLOCKED! Put that in the historical record!",
            ],
            "return_after_inactivity": [
                "AFK status lifted! Let's reclaim lost ground!",
                "Break over! Let's build that momentum right back!",
            ],
            "settings_interaction": [
                "Adjusting audio? Turn the sound effects UP!",
            ],
        },
    },
    "zero": {
        "id": "zero",
        "name": "ZERO",
        "title": "THE ANDROID",
        "role": "SYSTEM LOGIC CORE",
        "tagline": "Deadpan, analytical, robotic, and unintentionally funny.",
        "bio": "Titanium chassis with floating orbital units and a mint visor. Evaluates all human endeavors with mathematical coldness.",
        "color": MINT,
        "accent_hex": "#00FFA3",
        "dialogues": {
            "first_launch": [
                "Unit Zero initialized. Human collaboration protocol active.",
                "Diagnostic complete. Productivity optimization sequence begun.",
            ],
            "welcome": [
                "Operator recognized. Biometric status: functional.",
                "System online. Commencing daily operational review.",
                "Human presence confirmed. Efficiency metrics loaded.",
            ],
            "idle": [
                "Productivity levels: unexpectedly nonzero.",
                "Reminder: procrastination is not a recognized achievement.",
                "Current human velocity: 0.00 units per second.",
                "Calculating odds of finishing tasks... result: depends on you.",
                "Energy reserves optimal. Awaiting task delegation.",
            ],
            "hover": [
                "Cursor proximity registered. Awaiting operational input.",
                "Optical tracking active. Your mouse cursor is being monitored.",
                "Proximity alert: hover detected. Operational task required.",
            ],
            "tap": [
                "Haptic impact detected. Chassis integrity unaffected.",
                "Tactile input acknowledged. No physical damage logged.",
                "Query: does poking the android accelerate homework?",
                "Orbital satellite units re-centered after vibration.",
            ],
            "quest_started": [
                "Mission parameters logged. Execution recommended.",
                "Task registered in neural queue. Timer started.",
                "Protocol initiated. Avoidance routines suppressed.",
            ],
            "quest_completed": [
                "Task completed. Human efficiency temporarily acceptable.",
                "Verification confirmed: quest status set to cleared.",
                "Objective resolved with satisfactory parameters.",
            ],
            "quest_failed": [
                "Deadline variance exceeded. Recalibrating workflow.",
                "Unfinished task logged. Corrective action advised.",
            ],
            "xp_gained": [
                "XP quantified: increment applied to neural profile.",
                "Experience points aggregated successfully.",
            ],
            "streak_milestone": [
                "Temporal streak consistency validated. Proceed.",
                "Consecutive daily performance index upgraded.",
            ],
            "achievement_unlocked": [
                "New achievement index unlocked. Analytical approval granted.",
                "Milestone classified as exceptional performance.",
            ],
            "return_after_inactivity": [
                "Inactivity interval terminated. Resuming operational state.",
                "Human return confirmed. Idle logs archived.",
            ],
            "settings_interaction": [
                "System preferences accessed. Ensure optimal parameters.",
            ],
        },
    },
}


# --------------------------------------------------------------------------
# 2. SPRITE TEXTURE CACHE & LOADER
# --------------------------------------------------------------------------

class CompanionAssetManager:
    """Loads and caches transparent pixel-art sprite textures in memory."""
    _cache = {}

    @classmethod
    def get_texture(cls, char_id, state, frame_idx):
        key = f"{char_id}_{state}_{frame_idx}"
        if key in cls._cache:
            return cls._cache[key]

        file_name = f"{state}_{frame_idx}.png"
        path = os.path.join(ASSETS_DIR, char_id, file_name)
        if not os.path.exists(path):
            # Fallback to preview or idle 0
            path = os.path.join(ASSETS_DIR, char_id, "idle_0.png")
            if not os.path.exists(path):
                path = os.path.join(ASSETS_DIR, char_id, "preview.png")

        if os.path.exists(path):
            try:
                tex = CoreImage(path).texture
                cls._cache[key] = tex
                return tex
            except Exception as exc:
                print(f"[Companion] Texture load error {path}: {exc}")

        return None

    @classmethod
    def get_preview(cls, char_id):
        key = f"{char_id}_preview"
        if key in cls._cache:
            return cls._cache[key]
        path = os.path.join(ASSETS_DIR, char_id, "preview.png")
        if os.path.exists(path):
            try:
                tex = CoreImage(path).texture
                cls._cache[key] = tex
                return tex
            except Exception:
                pass
        return None


# --------------------------------------------------------------------------
# 3. COMPACT CYBERPUNK DIALOGUE SPEECH BUBBLE
# --------------------------------------------------------------------------

class SpeechBubble(BoxLayout):
    """
    Compact Cyberpunk dialogue box situated above or beside the companion.
    Features:
    - Auto-wrapping readable text
    - Dynamic glowing border keyed to companion's color
    - Holographic speech-stem pointing down to character
    """
    def __init__(self, char_color=MINT, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.height = dp(42)
        self.padding = [dp(6), dp(4)]
        self.spacing = dp(2)
        self.char_color = char_color

        with self.canvas.before:
            Color(*BG_PANEL)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            self._border_col = Color(*self.char_color)
            self._border = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, dp(4)], width=dp(1.1))

        self.label = Label(
            text="...",
            font_size="9sp",
            color=WHITE,
            halign="center",
            valign="middle",
            size_hint=(1, 1),
            font_name=TECH_FONT
        )
        self.label.bind(size=self._on_label_resize)
        self.add_widget(self.label)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.rounded_rectangle = [self.x, self.y, self.width, self.height, dp(4)]

    def _on_label_resize(self, *_):
        self.label.text_size = (self.width - dp(10), None)

    def set_color(self, color):
        self.char_color = color
        self._border_col.rgba = color

    def show_message(self, text):
        clean = str(text).strip()
        self.label.text = clean
        lines = max(1, (len(clean) // 22) + 1)
        target_h = max(dp(38), min(dp(54), dp(16) + lines * dp(13)))
        anim = Animation(height=target_h, duration=0.15)
        anim.start(self)


# --------------------------------------------------------------------------
# 4. LIVING COMPANION WIDGET (Sidebar Placement)
# --------------------------------------------------------------------------

class CompanionWidget(BoxLayout):
    """
    The Living RPG Companion Widget.
    Placed inside the sidebar underneath RANKS and SETTINGS.
    Features:
    - Multi-frame sprite animation (idle, react, celebrate)
    - Holographic floor projection pedestal & shadow
    - Mouse hover (desktop) & Touch reaction (mobile)
    - Speech bubble with context-driven offline dialogue
    - Safe timer cleanup on removal
    """
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = "vertical"
        self.size_hint = (1, 1)
        self.padding = [dp(4), dp(4)]
        self.spacing = dp(4)

        self.char_id = "nex"
        self.current_state = "idle"
        self.current_frame = 0
        self.max_frames = 4
        self.last_msg = ""
        self._anim_ev = None
        self._state_restore_ev = None
        self._idle_talk_ev = None
        self._is_hovered = False
        self._last_hover_time = 0.0

        # 1. Dialogue Bubble
        self.bubble = SpeechBubble(char_color=MAGENTA)
        self.add_widget(self.bubble)

        # 2. Stage (Sprite + Hologram Pedestal)
        self.stage = FloatLayout(size_hint=(1, 1))
        with self.stage.canvas.before:
            # Subtle glowing platform ring
            self._pedestal_col = Color(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.35)
            self._pedestal = Ellipse(pos=(0, 0), size=(dp(64), dp(14)))
            self._pedestal_ring = Line(ellipse=(0, 0, dp(64), dp(14)), width=dp(1.2))

        self.sprite = Image(
            fit_mode="contain",
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.52}
        )
        self.stage.add_widget(self.sprite)
        self.stage.bind(pos=self._sync_stage, size=self._sync_stage)
        self.add_widget(self.stage)

        # 3. Status Tag / Operator Name Tag
        self.footer = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(4))
        self.status_dot = Label(
            text="●",
            font_size="10sp",
            color=MINT,
            size_hint_x=None,
            width=dp(14),
            halign="center"
        )
        self.name_tag = Label(
            text="[NEX // NET ONLINE]",
            font_size="9sp",
            bold=True,
            color=WHITE,
            size_hint_x=1,
            halign="left",
            font_name=TECH_FONT
        )
        self.footer.add_widget(self.status_dot)
        self.footer.add_widget(self.name_tag)
        self.add_widget(self.footer)

        # Mouse hover binding (Windows)
        Window.bind(mouse_pos=self._on_mouse_pos)

        # Load initial companion from saved data
        initial_id = getattr(app, "selected_companion", "nex") or "nex"
        self.load_companion(initial_id, is_first=True)

        # Start animation loops
        self._anim_ev = Clock.schedule_interval(self._tick_anim, 0.28)  # ~3.5 FPS for crisp retro feel
        self._idle_talk_ev = Clock.schedule_interval(self._tick_idle_talk, 45.0)  # Periodic witty line

    def _sync_stage(self, *_):
        w = max(dp(40), min(dp(80), self.stage.width * 0.65))
        h = dp(14)
        px = self.stage.x + (self.stage.width - w) * 0.5
        py = self.stage.y + dp(6)
        self._pedestal.pos = (px, py)
        self._pedestal.size = (w, h)
        self._pedestal_ring.ellipse = (px, py, w, h)

    def load_companion(self, char_id, is_first=False):
        if char_id not in OPERATORS:
            char_id = "nex"
        self.char_id = char_id
        info = OPERATORS[char_id]

        # Update theme colors
        col = info["color"]
        self.bubble.set_color(col)
        self._pedestal_col.rgba = (col[0], col[1], col[2], 0.40)
        self.name_tag.text = f"[{info['name']} // ONLINE]"
        self.name_tag.color = col

        # Set initial frame
        self.current_state = "idle"
        self.current_frame = 0
        self.max_frames = 4
        self._update_sprite()

        # Welcome message
        category = "first_launch" if is_first else "welcome"
        self.speak(category)

    def _update_sprite(self):
        tex = CompanionAssetManager.get_texture(self.char_id, self.current_state, self.current_frame)
        if tex:
            self.sprite.texture = tex

    def _tick_anim(self, dt):
        self.current_frame = (self.current_frame + 1) % self.max_frames
        self._update_sprite()

    def _tick_idle_talk(self, dt):
        if self.current_state == "idle" and not self._is_hovered:
            self.speak("idle")

    def play_state(self, state, duration=2.5, frames=4):
        """Temporarily plays an action state (react, celebrate) then reverts to idle."""
        if self._state_restore_ev:
            self._state_restore_ev.cancel()
            self._state_restore_ev = None

        self.current_state = state
        self.current_frame = 0
        self.max_frames = frames
        self._update_sprite()

        def _revert(dt):
            self.current_state = "idle"
            self.current_frame = 0
            self.max_frames = 4
            self._update_sprite()
            self._state_restore_ev = None

        self._state_restore_ev = Clock.schedule_once(_revert, duration)

    def speak(self, category):
        """Selects a randomized prerecorded line without immediate repetition."""
        info = OPERATORS.get(self.char_id, OPERATORS["nex"])
        pool = info["dialogues"].get(category) or info["dialogues"].get("idle", ["Online."])

        # Avoid exact repetition if pool > 1
        available = [msg for msg in pool if msg != self.last_msg] or pool
        msg = random.choice(available)
        self.last_msg = msg
        self.bubble.show_message(msg)

    # ----------------------------------------------------------------------
    # User Interactions: Hover (Windows) & Tap (Android / Click)
    # ----------------------------------------------------------------------

    def _on_mouse_pos(self, _win, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and not self._is_hovered:
            self._is_hovered = True
            self.on_hover_enter()
        elif not inside and self._is_hovered:
            self._is_hovered = False

    def on_hover_enter(self):
        """Windows mouse enter reaction."""
        if self.current_state != "celebrate":
            self.play_state("react", duration=2.2, frames=3)
            self.speak("hover")

    def on_touch_down(self, touch):
        """Click / Mobile touch event."""
        if self.collide_point(*touch.pos):
            self.on_companion_tapped()
            return True
        return super().on_touch_down(touch)

    def on_companion_tapped(self):
        """Companion poked by user."""
        self.play_state("react", duration=2.5, frames=3)
        self.speak("tap")
        self.app.play_sound("click")
        # Visual pulse animation
        anim = Animation(size_hint=(0.98, 0.98), duration=0.08) + Animation(size_hint=(0.92, 0.92), duration=0.12)
        anim.start(self.sprite)

    # ----------------------------------------------------------------------
    # Event Integration Hooks
    # ----------------------------------------------------------------------

    def on_game_event(self, event_name, **kwargs):
        """Triggered when quests, XP, streaks, or achievements occur."""
        if event_name in ("quest_completed", "achievement_unlocked"):
            self.play_state("celebrate", duration=3.5, frames=4)
        elif event_name in ("quest_started", "xp_gained", "streak_milestone"):
            self.play_state("react", duration=2.0, frames=3)

        self.speak(event_name)

    def on_parent(self, _inst, parent):
        if parent is None:
            self.cleanup()

    def cleanup(self):
        """Safely release timers and listeners to prevent memory/clock leaks."""
        if self._anim_ev:
            self._anim_ev.cancel()
            self._anim_ev = None
        if self._idle_talk_ev:
            self._idle_talk_ev.cancel()
            self._idle_talk_ev = None
        if self._state_restore_ev:
            self._state_restore_ev.cancel()
            self._state_restore_ev = None
        try:
            Window.unbind(mouse_pos=self._on_mouse_pos)
        except Exception:
            pass


# --------------------------------------------------------------------------
# 5. FIRST-LAUNCH "CHOOSE YOUR OPERATOR" SELECTION MODAL
# --------------------------------------------------------------------------

class OperatorSelectModal(Popup):
    """
    Polished Cyberpunk HUD Operator Selection Modal.
    Presented on first launch or via Settings -> Switch Operator.
    Displays individual cards for NEX, GLITCH, and ZERO with live previews.
    """
    def __init__(self, app, on_selected_cb=None, **kwargs):
        self.app = app
        self.on_selected_cb = on_selected_cb

        kwargs.setdefault("title", "")
        kwargs.setdefault("separator_height", 0)
        kwargs.setdefault("auto_dismiss", False)
        kwargs.setdefault("size_hint", (0.94, 0.92))
        kwargs.setdefault("background_color", (0, 0, 0, 0.88))
        super().__init__(**kwargs)

        # Root Panel
        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        with root.canvas.before:
            Color(*BG_PANEL)
            self._bg = RoundedRectangle(pos=root.pos, size=root.size, radius=[dp(8)])
            Color(*MAGENTA)
            self._bd = Line(rounded_rectangle=[root.x, root.y, root.width, root.height, dp(8)], width=dp(1.4))
        root.bind(pos=lambda *_: setattr(self._bg, "pos", root.pos) or setattr(self._bd, "rounded_rectangle", [root.x, root.y, root.width, root.height, dp(8)]),
                  size=lambda *_: setattr(self._bg, "size", root.size) or setattr(self._bd, "rounded_rectangle", [root.x, root.y, root.width, root.height, dp(8)]))

        # Header
        hdr = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(52), spacing=dp(2))
        t1 = Label(
            text="CHOOSE YOUR OPERATOR // SELECT COMPANION",
            font_size="15sp",
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(24),
            font_name=TECH_FONT
        )
        t2 = Label(
            text="Your grind. Your rules. Your companion.",
            font_size="11sp",
            color=MINT,
            size_hint_y=None,
            height=dp(18)
        )
        hdr.add_widget(t1)
        hdr.add_widget(t2)
        root.add_widget(hdr)

        # Cards Layout (Horizontal for desktop/wide, wraps naturally)
        cards_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, 1))

        for char_id in ("nex", "glitch", "zero"):
            card = self._build_card(char_id)
            cards_row.add_widget(card)

        root.add_widget(cards_row)

        # Close / Skip button (if not first launch)
        if getattr(app, "selected_companion", ""):
            close_btn = Label(
                text="[ CANCEL / KEEP CURRENT OPERATOR ]",
                font_size="11sp",
                color=MUTED,
                size_hint=(1, None),
                height=dp(30)
            )
            close_btn.bind(on_touch_down=lambda _inst, touch: self.dismiss() if close_btn.collide_point(*touch.pos) else False)
            root.add_widget(close_btn)

        self.content = root

    def _build_card(self, char_id):
        info = OPERATORS[char_id]
        col = info["color"]

        card = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6), size_hint=(1, 1))
        with card.canvas.before:
            Color(*BG_CARD)
            bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
            Color(*col)
            border = Line(rounded_rectangle=[card.x, card.y, card.width, card.height, dp(6)], width=dp(1.2))
        card.bind(pos=lambda *_: setattr(bg, "pos", card.pos) or setattr(border, "rounded_rectangle", [card.x, card.y, card.width, card.height, dp(6)]),
                  size=lambda *_: setattr(bg, "size", card.size) or setattr(border, "rounded_rectangle", [card.x, card.y, card.width, card.height, dp(6)]))

        # Title & Role
        name_lbl = Label(text=info["name"], font_size="14sp", bold=True, color=col, size_hint_y=None, height=dp(20), font_name=TECH_FONT)
        title_lbl = Label(text=f"// {info['title']}", font_size="10sp", color=WHITE, size_hint_y=None, height=dp(16))
        card.add_widget(name_lbl)
        card.add_widget(title_lbl)

        # Preview Sprite
        preview_box = FloatLayout(size_hint=(1, 1))
        tex = CompanionAssetManager.get_preview(char_id)
        img = Image(texture=tex, fit_mode="contain", size_hint=(0.85, 0.85), pos_hint={"center_x": 0.5, "center_y": 0.5})
        preview_box.add_widget(img)
        card.add_widget(preview_box)

        # Tagline & Bio
        tagline_lbl = Label(
            text=f"\"{info['tagline']}\"",
            font_size="9.5sp",
            color=WHITE,
            size_hint_y=None,
            height=dp(28),
            halign="center"
        )
        tagline_lbl.bind(size=lambda *_: setattr(tagline_lbl, "text_size", (card.width - dp(16), None)))
        card.add_widget(tagline_lbl)

        # Select Button
        btn = BoxLayout(size_hint_y=None, height=dp(38))
        with btn.canvas.before:
            Color(col[0] * 0.35, col[1] * 0.35, col[2] * 0.35, 1.0)
            btn_bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(4)])
            Color(*col)
            btn_bd = Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(4)], width=dp(1.2))
        btn.bind(pos=lambda *_: setattr(btn_bg, "pos", btn.pos) or setattr(btn_bd, "rounded_rectangle", [btn.x, btn.y, btn.width, btn.height, dp(4)]),
                 size=lambda *_: setattr(btn_bg, "size", btn.size) or setattr(btn_bd, "rounded_rectangle", [btn.x, btn.y, btn.width, btn.height, dp(4)]))

        btn_lbl = Label(text="SELECT OPERATOR >>", font_size="11sp", bold=True, color=WHITE, font_name=TECH_FONT)
        btn.add_widget(btn_lbl)

        def _on_press(_inst, touch):
            if btn.collide_point(*touch.pos):
                self.choose_operator(char_id)
                return True
            return False

        btn.bind(on_touch_down=_on_press)
        card.add_widget(btn)

        return card

    def choose_operator(self, char_id):
        self.dismiss()
        if self.on_selected_cb:
            self.on_selected_cb(char_id)
