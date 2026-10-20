"""
auth_ui.py - Cyberpunk Arcade Authentication Modal & Screen for procrastiNOT.exe
Provides:
- Authentic Google Sign-In button & loopback trigger
- Email/Password Sign Up with confirmation & visibility toggle
- Mandatory Email Verification Gate (real email inbox verification)
- Email/Password Log In with credential validation
- Password Reset dialog
- Data Migration prompt for existing offline JSON data
- Seamless Cyberpunk OS HUD aesthetic matching main_leaderboard.py
"""

import os
import threading
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line

from auth_firebase import auth_client

# Cyberpunk Palette matching main_leaderboard.py
BG = (0.024, 0.012, 0.039, 1.0)           # #06030A - Void Black
BG_SECONDARY = (0.039, 0.027, 0.067, 1.0) # #0A0711 - Near-black surface
BG_ELEVATED = (0.063, 0.039, 0.098, 0.98) # #100A19 - Elevated surface
MAGENTA = (1.0, 0.239, 0.949, 1.0)        # #FF3DF2
MAGENTA_CORE = (1.0, 0.882, 0.984, 1.0)   # #FFE1FB
MINT = (0.239, 1.0, 0.690, 1.0)           # #3DFFB0
CYAN = MINT
WHITE = (0.910, 0.875, 0.937, 1.0)
TEXT_SEC = (0.639, 0.604, 0.678, 1.0)
MUTED = (0.467, 0.439, 0.502, 1.0)
RED = (1.0, 0.20, 0.35, 1.0)
SEPARATOR = (1.0, 1.0, 1.0, 0.12)


class CyberInput(BoxLayout):
    """Cyberpunk themed text input with optional password visibility toggle."""

    def __init__(self, hint_text="", is_password=False, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(4), **kwargs)
        self.is_password = is_password
        self.size_hint_y = None
        self.height = dp(40)

        with self.canvas.before:
            Color(0.04, 0.03, 0.07, 1.0)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            Color(*SEPARATOR)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(4)), width=dp(1.0))
        self.bind(pos=self._update_geom, size=self._update_geom)

        self.input = TextInput(
            text="",
            hint_text=hint_text,
            multiline=False,
            password=self.is_password,
            background_color=(0, 0, 0, 0),
            foreground_color=WHITE,
            hint_text_color=MUTED,
            font_size="13sp",
            padding=[dp(10), dp(10)],
            size_hint=(1, 1)
        )
        self.add_widget(self.input)

        if self.is_password:
            self.toggle_btn = Button(
                text="👁️",
                font_size="14sp",
                background_color=(0, 0, 0, 0),
                color=TEXT_SEC,
                size_hint=(None, 1),
                width=dp(36)
            )
            self.toggle_btn.bind(on_press=self.toggle_visibility)
            self.add_widget(self.toggle_btn)

    def _update_geom(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(4))

    def toggle_visibility(self, *args):
        self.input.password = not self.input.password
        self.toggle_btn.color = MINT if not self.input.password else TEXT_SEC

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, val):
        self.input.text = val


class AuthModal(Popup):
    """
    Main Cyberpunk Authentication Gateway.
    Handles Login, Signup, Email Verification Gate, and Data Migration.
    """

    def __init__(self, app_instance, on_auth_success=None, **kwargs):
        kwargs.setdefault("title", "")
        kwargs.setdefault("separator_height", 0)
        kwargs.setdefault("auto_dismiss", False)
        kwargs.setdefault("size_hint", (0.85, 0.90))
        super().__init__(**kwargs)

        self.app = app_instance
        self.on_auth_success = on_auth_success
        self.active_tab = "login"

        self.background_color = (0, 0, 0, 0.85)

        # Root Container
        root_panel = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        with root_panel.canvas.before:
            Color(*BG_SECONDARY)
            self._bg_rect = RoundedRectangle(pos=root_panel.pos, size=root_panel.size, radius=[dp(8)])
            Color(*MAGENTA)
            self._border_line = Line(rounded_rectangle=(root_panel.x, root_panel.y, root_panel.width, root_panel.height, dp(8)), width=dp(1.2))
        root_panel.bind(pos=lambda *_: self._update_root_geom(root_panel), size=lambda *_: self._update_root_geom(root_panel))

        # Header Title
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(52), spacing=dp(2))
        title_lbl = Label(text="⚡ PROGRASTINOT // OPERATOR IDENTITY GATE", font_size="14sp", bold=True, color=MAGENTA_CORE, halign="center")
        subtitle_lbl = Label(text="Secure Verified Authentication & Isolated Terminal Data", font_size="11sp", color=MINT, halign="center")
        header.add_widget(title_lbl)
        header.add_widget(subtitle_lbl)
        root_panel.add_widget(header)

        # Tab Selector (LOGIN vs SIGN UP)
        tab_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36), spacing=dp(8))
        self.login_tab_btn = Button(text="🔑 LOG IN", bold=True, font_size="11.5sp", background_color=MINT, color=BG)
        self.login_tab_btn.bind(on_press=lambda *_: self.switch_tab("login"))

        self.signup_tab_btn = Button(text="🚀 CREATE ACCOUNT", bold=True, font_size="11.5sp", background_color=(0.1, 0.1, 0.15, 1.0), color=TEXT_SEC)
        self.signup_tab_btn.bind(on_press=lambda *_: self.switch_tab("signup"))

        tab_box.add_widget(self.login_tab_btn)
        tab_box.add_widget(self.signup_tab_btn)
        root_panel.add_widget(tab_box)

        # Form Container
        self.form_container = BoxLayout(orientation="vertical", spacing=dp(8), size_hint=(1, 1))
        root_panel.add_widget(self.form_container)

        # Status / Feedback Label
        self.status_lbl = Label(
            text="Authenticate to unlock your personal missions, XP and streaks.",
            font_size="11sp",
            color=TEXT_SEC,
            size_hint_y=None,
            height=dp(26),
            halign="center"
        )
        root_panel.add_widget(self.status_lbl)

        # Google Sign In Separator & Button
        root_panel.add_widget(Label(text="— OR CONNECT WITH GOOGLE —", font_size="9.5sp", color=MUTED, size_hint_y=None, height=dp(16)))

        self.google_btn = Button(
            text="[color=4285F4]G[/color][color=EA4335]o[/color][color=FBBC05]o[/color][color=4285F4]g[/color][color=34A853]l[/color][color=EA4335]e[/color]  CONTINUE WITH GOOGLE",
            markup=True,
            font_size="13sp",
            bold=True,
            size_hint_y=None,
            height=dp(42),
            background_color=(0.12, 0.10, 0.18, 1.0),
            color=WHITE
        )
        self.google_btn.bind(on_press=self.on_google_press)
        root_panel.add_widget(self.google_btn)

        self.content = root_panel
        self.render_form()

    def _update_root_geom(self, panel):
        self._bg_rect.pos = panel.pos
        self._bg_rect.size = panel.size
        self._border_line.rounded_rectangle = (panel.x, panel.y, panel.width, panel.height, dp(8))

    def switch_tab(self, tab):
        self.active_tab = tab
        if tab == "login":
            self.login_tab_btn.background_color = MINT
            self.login_tab_btn.color = BG
            self.signup_tab_btn.background_color = (0.1, 0.1, 0.15, 1.0)
            self.signup_tab_btn.color = TEXT_SEC
        else:
            self.signup_tab_btn.background_color = MAGENTA
            self.signup_tab_btn.color = BG
            self.login_tab_btn.background_color = (0.1, 0.1, 0.15, 1.0)
            self.login_tab_btn.color = TEXT_SEC
        self.status_lbl.text = ""
        self.render_form()

    def render_form(self):
        self.form_container.clear_widgets()

        if self.active_tab == "login":
            self.form_container.add_widget(Label(text="REGISTERED EMAIL ADDRESS:", font_size="10sp", color=MINT, size_hint_y=None, height=dp(18), halign="left"))
            self.login_email = CyberInput(hint_text="operator@domain.com")
            self.form_container.add_widget(self.login_email)

            forgot_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            forgot_box.add_widget(Label(text="PASSWORD / PASSKEY:", font_size="10sp", color=MINT, size_hint_x=0.6, halign="left"))
            forgot_btn = Button(text="Forgot Password?", font_size="10sp", color=MAGENTA, background_color=(0, 0, 0, 0), size_hint_x=0.4)
            forgot_btn.bind(on_press=self.show_forgot_password_dialog)
            forgot_box.add_widget(forgot_btn)
            self.form_container.add_widget(forgot_box)

            self.login_pass = CyberInput(hint_text="••••••••", is_password=True)
            self.form_container.add_widget(self.login_pass)

            self.submit_btn = Button(
                text="🔑 LOG IN TO TERMINAL",
                font_size="12.5sp",
                bold=True,
                size_hint_y=None,
                height=dp(42),
                background_color=MINT,
                color=BG
            )
            self.submit_btn.bind(on_press=self.handle_login_submit)
            self.form_container.add_widget(self.submit_btn)

        else:  # Sign Up Form
            self.form_container.add_widget(Label(text="CALLSIGN / DISPLAY NAME:", font_size="10sp", color=CYAN, size_hint_y=None, height=dp(18), halign="left"))
            self.signup_name = CyberInput(hint_text="e.g. Neo or Operator 7")
            self.form_container.add_widget(self.signup_name)

            self.form_container.add_widget(Label(text="ACTUAL EMAIL ADDRESS (Verification Required):", font_size="10sp", color=CYAN, size_hint_y=None, height=dp(18), halign="left"))
            self.signup_email = CyberInput(hint_text="yourname@gmail.com")
            self.form_container.add_widget(self.signup_email)

            self.form_container.add_widget(Label(text="CREATE PASSWORD (Min 6 Characters):", font_size="10sp", color=CYAN, size_hint_y=None, height=dp(18), halign="left"))
            self.signup_pass = CyberInput(hint_text="••••••••", is_password=True)
            self.form_container.add_widget(self.signup_pass)

            self.form_container.add_widget(Label(text="CONFIRM PASSWORD:", font_size="10sp", color=CYAN, size_hint_y=None, height=dp(18), halign="left"))
            self.signup_pass_confirm = CyberInput(hint_text="••••••••", is_password=True)
            self.form_container.add_widget(self.signup_pass_confirm)

            self.submit_btn = Button(
                text="🚀 CREATE ACCOUNT & SEND VERIFICATION EMAIL",
                font_size="12sp",
                bold=True,
                size_hint_y=None,
                height=dp(42),
                background_color=MAGENTA,
                color=BG
            )
            self.submit_btn.bind(on_press=self.handle_signup_submit)
            self.form_container.add_widget(self.submit_btn)

    # ---------------------------------------------------------
    # Authentication Event Handlers
    # ---------------------------------------------------------

    def handle_login_submit(self, *args):
        email = self.login_email.text.strip()
        password = self.login_pass.text.strip()

        if not email or "@" not in email or "." not in email:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Please enter a valid email address."
            return

        if not password:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Please enter your password."
            return

        self.status_lbl.color = MINT
        self.status_lbl.text = "Authenticating with server..."
        self.submit_btn.disabled = True

        def run_login():
            res = auth_client.sign_in_with_email(email, password)
            Clock.schedule_once(lambda dt: self._on_login_result(res), 0)

        threading.Thread(target=run_login, daemon=True).start()

    def _on_login_result(self, res):
        self.submit_btn.disabled = False
        if not res.get("success"):
            self.status_lbl.color = RED
            self.status_lbl.text = res.get("error", "Login failed.")
            return

        # Check if email is verified
        if not res.get("email_verified"):
            self.show_verification_gate_modal(res.get("email"))
            return

        # Login fully successful!
        self.complete_authentication(res)

    def handle_signup_submit(self, *args):
        name = self.signup_name.text.strip()
        email = self.signup_email.text.strip()
        p1 = self.signup_pass.text.strip()
        p2 = self.signup_pass_confirm.text.strip()

        if not name:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Please enter your callsign or name."
            return

        if not email or "@" not in email or "." not in email:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Please enter a genuine email address."
            return

        if len(p1) < 6:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Password must be at least 6 characters long."
            return

        if p1 != p2:
            self.status_lbl.color = RED
            self.status_lbl.text = "⚠️ Passwords do not match!"
            return

        self.status_lbl.color = MINT
        self.status_lbl.text = "Creating account & dispatching verification email..."
        self.submit_btn.disabled = True

        def run_signup():
            res = auth_client.sign_up_with_email(email, p1, display_name=name)
            Clock.schedule_once(lambda dt: self._on_signup_result(res, email), 0)

        threading.Thread(target=run_signup, daemon=True).start()

    def _on_signup_result(self, res, email):
        self.submit_btn.disabled = False
        if not res.get("success"):
            self.status_lbl.color = RED
            self.status_lbl.text = res.get("error", "Sign up failed.")
            return

        # Account created, now show verification gate modal
        self.show_verification_gate_modal(email)

    def on_google_press(self, *args):
        self.status_lbl.color = MINT
        self.status_lbl.text = "Opening system browser for Google Sign-In..."
        self.google_btn.disabled = True

        def on_complete(res):
            Clock.schedule_once(lambda dt: self._on_google_result(res), 0)

        auth_client.start_google_sign_in_flow(on_complete)

    def _on_google_result(self, res):
        self.google_btn.disabled = False
        if not res.get("success"):
            self.status_lbl.color = RED
            self.status_lbl.text = res.get("error", "Google authentication failed.")
            return
        self.complete_authentication(res)

    # ---------------------------------------------------------
    # Verification Gate Modal
    # ---------------------------------------------------------

    def show_verification_gate_modal(self, email):
        """Display dialog preventing access until email inbox link is clicked."""
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        box.add_widget(Label(text="📧 INBOX VERIFICATION REQUIRED", font_size="13sp", bold=True, color=MINT))
        msg = (
            f"A verification link has been sent to:\n[b]{email}[/b]\n\n"
            "To prevent fake accounts and secure your personal data,\n"
            "you MUST verify your email before entering the terminal.\n"
            "Open your inbox and click the verification link."
        )
        box.add_widget(Label(text=msg, markup=True, font_size="11sp", color=WHITE, halign="center"))

        check_status_lbl = Label(text="", font_size="10.5sp", color=TEXT_SEC, size_hint_y=None, height=dp(20))
        box.add_widget(check_status_lbl)

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(38))
        resend_btn = Button(text="Resend Email", font_size="11sp", background_color=MUTED, color=WHITE)
        check_btn = Button(text="✅ I HAVE VERIFIED MY EMAIL", font_size="11sp", bold=True, background_color=MINT, color=BG)

        btn_row.add_widget(resend_btn)
        btn_row.add_widget(check_btn)
        box.add_widget(btn_row)

        verify_popup = Popup(
            title="",
            content=box,
            size_hint=(0.78, 0.65),
            auto_dismiss=False,
            separator_height=0
        )

        def do_resend(*_):
            resend_btn.disabled = True
            res = auth_client.send_email_verification()
            check_status_lbl.color = MINT if res.get("success") else RED
            check_status_lbl.text = res.get("message") or res.get("error")
            Clock.schedule_once(lambda dt: setattr(resend_btn, "disabled", False), 5)

        def do_check(*_):
            check_status_lbl.color = MINT
            check_status_lbl.text = "Checking verification with Firebase..."
            verified = auth_client.check_email_verified()
            if verified:
                verify_popup.dismiss()
                self.complete_authentication({"uid": auth_client.current_user["uid"], "email": email})
            else:
                check_status_lbl.color = RED
                check_status_lbl.text = "❌ Still unverified. Please click the link in your email first!"

        resend_btn.bind(on_press=do_resend)
        check_btn.bind(on_press=do_check)
        verify_popup.open()

    # ---------------------------------------------------------
    # Password Reset Dialog
    # ---------------------------------------------------------

    def show_forgot_password_dialog(self, *args):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(Label(text="🔒 RESET OPERATOR PASSKEY", font_size="12.5sp", bold=True, color=MAGENTA))
        box.add_widget(Label(text="Enter your registered email to receive reset instructions:", font_size="11sp", color=TEXT_SEC))

        email_inp = CyberInput(hint_text="yourname@domain.com")
        if hasattr(self, "login_email") and self.login_email.text:
            email_inp.text = self.login_email.text
        box.add_widget(email_inp)

        status = Label(text="", font_size="10.5sp", color=MINT, size_hint_y=None, height=dp(20))
        box.add_widget(status)

        btns = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))
        cancel_btn = Button(text="Cancel", font_size="11sp", background_color=MUTED, color=WHITE)
        send_btn = Button(text="Send Reset Link", font_size="11sp", bold=True, background_color=MAGENTA, color=BG)
        btns.add_widget(cancel_btn)
        btns.add_widget(send_btn)
        box.add_widget(btns)

        popup = Popup(title="", content=box, size_hint=(0.75, 0.55), auto_dismiss=True, separator_height=0)
        cancel_btn.bind(on_press=popup.dismiss)

        def do_send(*_):
            em = email_inp.text.strip()
            if not em or "@" not in em:
                status.color = RED
                status.text = "⚠️ Enter a valid email."
                return
            res = auth_client.send_password_reset(em)
            status.color = MINT if res.get("success") else RED
            status.text = res.get("message") or res.get("error")
            if res.get("success"):
                Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)

        send_btn.bind(on_press=do_send)
        popup.open()

    # ---------------------------------------------------------
    # Authentication Completion & Data Migration
    # ---------------------------------------------------------

    def complete_authentication(self, user_info):
        """Called when user is authenticated & email-verified."""
        self.dismiss()
        uid = user_info.get("uid")

        # Check if local offline data exists and should be migrated
        self.check_local_data_migration(uid)

    def check_local_data_migration(self, uid):
        """Prompt user if existing local quests/XP should be migrated."""
        legacy_file = os.path.join(self.app.user_data_dir, "projectx_data.json")
        has_legacy = os.path.exists(legacy_file) and (self.app.xp > 0 or len(self.app.missions) > 0)

        if has_legacy:
            box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
            box.add_widget(Label(text="📦 MIGRATE EXISTING DATA?", font_size="13sp", bold=True, color=MINT))
            desc = (
                f"We detected existing offline quest data ({self.app.xp} XP, {len(self.app.missions)} missions).\n\n"
                "Would you like to associate this data with your new verified account?\n"
                "(Your local data will be backed up safely in all cases.)"
            )
            box.add_widget(Label(text=desc, font_size="11sp", color=WHITE, halign="center"))

            btn_box = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(38))
            skip_btn = Button(text="Start Fresh (Keep Local Backup)", font_size="10.5sp", background_color=MUTED, color=WHITE)
            migrate_btn = Button(text="⚡ Link & Upload to My Account", font_size="11sp", bold=True, background_color=MINT, color=BG)
            btn_box.add_widget(skip_btn)
            btn_box.add_widget(migrate_btn)
            box.add_widget(btn_box)

            mig_popup = Popup(title="", content=box, size_hint=(0.80, 0.58), auto_dismiss=False, separator_height=0)

            def on_skip(*_):
                mig_popup.dismiss()
                self._finish_login(uid, migrate=False)

            def on_migrate(*_):
                mig_popup.dismiss()
                self._finish_login(uid, migrate=True)

            skip_btn.bind(on_press=on_skip)
            migrate_btn.bind(on_press=on_migrate)
            mig_popup.open()
        else:
            self._finish_login(uid, migrate=False)

    def _finish_login(self, uid, migrate=False):
        if self.on_auth_success:
            self.on_auth_success(uid, migrate=migrate)
