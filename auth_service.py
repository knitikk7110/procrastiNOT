"""
auth_service.py - Authentication & Cloud Firestore Service Mixin for procrastiNOT.exe
Integrates with ProcrastiNotApp following the codebase's modular mixin architecture.

Capabilities:
- Session verification & startup auth gate.
- Per-user data isolation (scopes save file to user_{UID}.json).
- Two-way async sync with Cloud Firestore (/users/{UID}).
- Safe offline data migration prompt.
- Secure terminal logout with memory & cache clearance.
- Operator Account HUD panel in Settings.
"""

import os
import json
import threading
from datetime import datetime
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from auth_firebase import auth_client
from auth_ui import AuthModal, CyberInput

# Borrowed names from main_leaderboard.py
_NEEDED = [
    "make_label", "section", "NeonPanel", "NeonButton", "safe_int",
    "CYAN", "PINK", "PURPLE", "MINT", "YELLOW", "WHITE", "MUTED", "RED",
    "PANEL_ALT", "NAV_IDLE", "NAV_ACTIVE", "SEPARATOR", "BG_SECONDARY", "BG_ELEVATED"
]


class AuthMixin:
    """Authentication and Cloud Firestore synchronization mixin for ProcrastiNotApp."""

    def init_auth(self):
        self.auth_client = auth_client
        self.auth_modal = None
        self.authenticated_uid = None
        self.authenticated_email = None
        self.firestore_sync_busy = False
        self.firestore_sync_note = ""

    def setup_authenticated_session(self):
        """Called during application build to determine initial auth state."""
        user = self.auth_client.current_user
        if user and user.get("uid") and user.get("email_verified"):
            self.authenticated_uid = user["uid"]
            self.authenticated_email = user.get("email", "")
            self.data_file = os.path.join(self.user_data_dir, f"user_{self.authenticated_uid}.json")
            self.load_data()
            self.sync_from_firestore_async()
            Clock.schedule_once(lambda dt: self._announce_auth_ready(), 0.5)
        else:
            # Unauthenticated or unverified session: block with AuthModal
            self.authenticated_uid = None
            self.authenticated_email = None
            self.data_file = os.path.join(self.user_data_dir, "guest_data.json")
            self.load_data()
            Clock.schedule_once(lambda dt: self.open_auth_modal(is_mandatory=True), 0.3)

    def _announce_auth_ready(self):
        disp = (self.auth_client.current_user.get("display_name") if self.auth_client.current_user else "") or (self.authenticated_email.split("@")[0] if self.authenticated_email else "OPERATOR")
        if hasattr(self, "greeting_label"):
            self.greeting_label.text = f"COMMAND ACCESS GRANTED // {disp.upper()}"
        if hasattr(self, "cursor_label"):
            self.cursor_label.text = "● VERIFIED CLOUD ID"
        if hasattr(self, "set_status"):
            self.set_status(f"OPERATOR ONLINE: {self.authenticated_email} (UID: {self.authenticated_uid[:8]}...)")

    def open_auth_modal(self, is_mandatory=True):
        if self.auth_modal:
            try:
                self.auth_modal.dismiss()
            except Exception:
                pass
        self.auth_modal = AuthModal(self, on_auth_success=self.on_auth_success)
        self.auth_modal.open()

    def on_auth_success(self, uid, migrate=False):
        """Invoked when user successfully logs in or signs up and verifies email."""
        user = self.auth_client.current_user
        self.authenticated_uid = uid
        self.authenticated_email = user.get("email", "") if user else ""
        self.data_file = os.path.join(self.user_data_dir, f"user_{uid}.json")

        if migrate:
            # Migrate local data to newly authenticated cloud account
            self.save_data()
            self.sync_to_firestore_async()
            if hasattr(self, "set_status"):
                self.set_status(f"LOCAL DATA LINKED & UPLOADED FOR: {self.authenticated_email}")
        else:
            # Check if local cache for this specific user exists
            if os.path.exists(self.data_file):
                self.load_data()
                self.sync_from_firestore_async()
            else:
                # First time on this device: try fetching from Cloud Firestore
                def fetch_remote():
                    doc = self.auth_client.load_user_document(uid)
                    Clock.schedule_once(lambda dt: self._apply_initial_cloud_data(doc), 0)
                threading.Thread(target=fetch_remote, daemon=True).start()

        if hasattr(self, "refresh_screen"):
            self.refresh_screen()
        self._announce_auth_ready()
        if hasattr(self, "go_page"):
            self.go_page("home")

    def _apply_initial_cloud_data(self, doc):
        if doc and isinstance(doc, dict) and doc.get("xp") is not None:
            self._apply_dict_to_app(doc)
            self.save_data()
            if hasattr(self, "set_status"):
                self.set_status(f"RESTORED CLOUD PROFILE ({self.xp} XP) FOR: {self.authenticated_email}")
        else:
            # Clean starter account
            self.xp = 0
            self.missions = []
            self.mood_logs = []
            self.completed_dates = []
            self.habits = []
            self.save_data()
            self.sync_to_firestore_async()
            if hasattr(self, "set_status"):
                self.set_status(f"INITIALIZED FRESH OPERATOR PROFILE: {self.authenticated_email}")
        if hasattr(self, "refresh_screen"):
            self.refresh_screen()

    def logout_user(self, *args):
        """Securely log out of the operator terminal, wiping active in-memory session."""
        if hasattr(self, "sound") and hasattr(self.sound, "play"):
            self.sound.play("click")
        # Save before logging out
        if self.authenticated_uid:
            self.save_data()
            self.auth_client.clear_session()

        self.authenticated_uid = None
        self.authenticated_email = None
        self.xp = 0
        self.missions = []
        self.mood_logs = []
        self.completed_dates = []
        self.habits = []

        if hasattr(self, "greeting_label"):
            self.greeting_label.text = "TERMINAL LOCKED // AUTHENTICATION REQUIRED"
        if hasattr(self, "cursor_label"):
            self.cursor_label.text = "○ DISCONNECTED"
            self.cursor_label.color = RED

        if hasattr(self, "refresh_screen"):
            self.refresh_screen()
        if hasattr(self, "set_status"):
            self.set_status("OPERATOR LOGGED OUT. ACTIVE TERMINAL CLEARED.")
        self.open_auth_modal(is_mandatory=True)

    # ---------------------------------------------------------
    # Cloud Firestore Asynchronous Synchronization
    # ---------------------------------------------------------

    def sync_to_firestore_async(self):
        """Asynchronously push local updates to Cloud Firestore."""
        if not self.authenticated_uid or not self.auth_client.is_configured:
            return
        if self.firestore_sync_busy:
            return

        self.firestore_sync_busy = True
        payload = {
            "xp": self.xp,
            "missions": self.missions,
            "mood_logs": self.mood_logs,
            "completed_dates": self.completed_dates,
            "sound_enabled": getattr(self, "sound_enabled", True),
            "achievements": getattr(self, "achievements", []),
            "selected_companion": getattr(self, "selected_companion", "nex"),
            "arcade_scores": getattr(self, "arcade_scores", {}),
            "unlocked_themes": getattr(self, "unlocked_themes", ["cyberpunk"]),
            "current_theme": getattr(self, "current_theme", "cyberpunk"),
            "habits": getattr(self, "habits", []),
            "focus_sprints": getattr(self, "focus_sprints", 0),
            "last_synced": datetime.now().isoformat()
        }

        def worker():
            ok = self.auth_client.save_user_document(payload, uid=self.authenticated_uid)
            Clock.schedule_once(lambda dt: self._on_sync_to_done(ok), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _on_sync_to_done(self, success):
        self.firestore_sync_busy = False
        if success:
            self.firestore_sync_note = f"☁️ Synced to Cloud Firestore at {datetime.now():%H:%M:%S}"
        else:
            self.firestore_sync_note = "⚠️ Cloud Firestore sync failed. Saved locally."
        if hasattr(self, "settings_sync_label") and self.settings_sync_label:
            self.settings_sync_label.text = self.firestore_sync_note

    def sync_from_firestore_async(self):
        """Asynchronously pull cloud updates from Cloud Firestore."""
        if not self.authenticated_uid or not self.auth_client.is_configured:
            return

        def worker():
            doc = self.auth_client.load_user_document(uid=self.authenticated_uid)
            if doc:
                Clock.schedule_once(lambda dt: self._apply_dict_to_app(doc), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_dict_to_app(self, data):
        """Merge a dictionary of user data into app state."""
        self.xp = max(0, safe_int(data.get("xp", self.xp)))
        if "missions" in data and isinstance(data["missions"], list):
            self.missions = data["missions"]
        if "mood_logs" in data and isinstance(data["mood_logs"], list):
            self.mood_logs = data["mood_logs"]
        if "completed_dates" in data and isinstance(data["completed_dates"], list):
            self.completed_dates = data["completed_dates"]
        if "habits" in data and isinstance(data["habits"], list):
            self.habits = data["habits"]
        if "achievements" in data and isinstance(data["achievements"], list):
            self.achievements = data["achievements"]
        if "selected_companion" in data:
            self.selected_companion = data["selected_companion"]
        if "arcade_scores" in data and isinstance(data["arcade_scores"], dict):
            self.arcade_scores = data["arcade_scores"]
        if "focus_sprints" in data:
            self.focus_sprints = max(0, safe_int(data.get("focus_sprints", 0)))

        self.update_xp_ui()
        self.update_header()

    # ---------------------------------------------------------
    # UI Component Injection (Settings & Profile)
    # ---------------------------------------------------------

    def build_auth_settings_section(self, parent_box):
        """Renders the OPERATOR ACCOUNT & CLOUD SYNC card in Settings."""
        parent_box.add_widget(section("🔒 OPERATOR ACCOUNT & CLOUD IDENTITY", MINT))

        user = self.auth_client.current_user if hasattr(self, "auth_client") else None
        email = self.authenticated_email or (user.get("email") if user else "Not Authenticated")
        uid = self.authenticated_uid or (user.get("uid") if user else "None")

        account_panel = NeonPanel(
            orientation="vertical",
            padding=[dp(12), dp(10)],
            spacing=dp(6),
            size_hint_y=None,
            height=dp(130),
            bg_color=BG_ELEVATED,
            border_color=MINT
        )

        acc_header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        acc_header.add_widget(make_label("STATUS: VERIFIED OPERATOR", 11, MINT, True))
        acc_header.add_widget(make_label("CLOUD: FIRESTORE ONLINE", 10, CYAN, False, halign="right"))
        account_panel.add_widget(acc_header)

        account_panel.add_widget(make_label(f"EMAIL: {email}", 11, WHITE, True, size_hint_y=None, height=dp(20)))
        account_panel.add_widget(make_label(f"FIREBASE UID: {uid}", 9.5, MUTED, False, size_hint_y=None, height=dp(18)))

        self.settings_sync_label = make_label("☁️ Cloud Firestore auto-sync active.", 10, CYAN, False, size_hint_y=None, height=dp(18))
        account_panel.add_widget(self.settings_sync_label)

        action_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))
        sync_btn = NeonButton(text="🔄 SYNC CLOUD NOW", bg_color=(0.08, 0.38, 0.30, 1), font_size="10.5sp")
        sync_btn.bind(on_press=lambda *_: self.sync_to_firestore_async())

        logout_btn = NeonButton(text="🚪 LOG OUT TERMINAL", bg_color=(0.48, 0.10, 0.22, 1), font_size="10.5sp")
        logout_btn.bind(on_press=self.logout_user)

        action_row.add_widget(sync_btn)
        action_row.add_widget(logout_btn)
        account_panel.add_widget(action_row)

        parent_box.add_widget(account_panel)


def install(ns, app_cls):
    """Installs AuthMixin into ProcrastiNotApp namespace and class."""
    for name in _NEEDED:
        if name in ns:
            globals()[name] = ns[name]
    for name, fn in AuthMixin.__dict__.items():
        if callable(fn) and not name.startswith("__"):
            setattr(app_cls, name, fn)
