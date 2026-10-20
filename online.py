"""
online.py  -  global leaderboard + player profile for procrastiNOT.exe
Backend: Supabase (free tier). Setup: run leaderboard_setup.sql once (re-running is safe).

Only these things ever leave your PC: username, avatar, country, XP, quests cleared, best streak.
Quests, moods and chats stay local.

main.py loads this with:   import online; online.install(globals(), ProcrastiNotApp)
(needs i18n.py too: it provides the flag pictures and the country picker)
"""
import re
import uuid
import secrets
import threading
from datetime import datetime

from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

# ===== YOUR SUPABASE DETAILS (Project Settings -> API) =====
SUPABASE_URL = "https://vsupqvbjcyngluhphhdp.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_C-wxF9-FNDb-HptorwEwHA_t9w2dn5x"   # PUBLIC key only. NEVER the secret/service_role key.

AVATARS = ["🤖", "🦊", "🐉", "👾", "🧠", "🔥", "🦄", "🐱", "🚀", "💀"]
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,16}$")
COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
BANNED_WORDS = []        # lowercase words you don't want inside usernames, e.g. ["admin"]
SYNC_DELAY = 4           # seconds to wait after a change before uploading (batches rapid changes)

# names borrowed from main.py (filled in by install())
_NEEDED = ["make_label", "section", "make_input", "NeonPanel", "NeonButton", "safe_int",
           "CYAN", "PINK", "PURPLE", "GREEN", "YELLOW", "WHITE", "MUTED", "RED",
           "PANEL_ALT", "NAV_IDLE", "NAV_ACTIVE"]


class OnlineMixin:
    # ---------------- state + saving ----------------
    def init_online(self):
        self.player_id = ""
        self.player_token = ""
        self.username = ""
        self.server_username = ""
        self._prev_username = ""
        self.avatar = AVATARS[0]
        self.avatar_choice = AVATARS[0]
        self.country = ""
        self.lang = "en"
        self.lb_scope = "world"
        self.lb_rows = []
        self.lb_me = None
        self.lb_busy = False
        self.lb_note = ""
        self.sync_busy = False
        self.sync_pending = False
        self.sync_ev = None
        self.sync_note = ""

    def load_online(self, data):
        self.player_id = str(data.get("player_id", "") or "")
        self.player_token = str(data.get("player_token", "") or "")
        self.username = str(data.get("username", "") or "")
        self.server_username = self.username
        self.avatar = str(data.get("avatar", "") or AVATARS[0])
        self.avatar_choice = self.avatar
        country = str(data.get("country", "") or "")
        self.country = country if COUNTRY_RE.match(country) else ""
        self.lang = str(data.get("lang", "") or "en")

    def online_save_fields(self):
        return {"player_id": self.player_id, "player_token": self.player_token,
                "username": self.username, "avatar": self.avatar,
                "country": self.country, "lang": self.lang}

    def ensure_identity(self):
        if not self.player_id:
            self.player_id = str(uuid.uuid4())
        if not self.player_token:
            self.player_token = secrets.token_urlsafe(32)

    def online_ready(self):
        return "YOURPROJECT" not in SUPABASE_URL and "YOUR_SUPABASE" not in SUPABASE_ANON_KEY

    def describe_online_error(self, err):
        return {
            "bad_username": "Username must be 3-16 letters, numbers or _",
            "name_taken": "That username is already taken",
            "bad_token": "That username belongs to another device",
            "network": "Can't reach the leaderboard right now",
            "not_set_up": "Leaderboard backend isn't set up yet (see online.py)",
        }.get(err, "Leaderboard error: " + str(err))

    def _rpc(self, fn, payload):
        headers = {"apikey": SUPABASE_ANON_KEY}
        return self._http_json(f"{SUPABASE_URL}/rest/v1/rpc/{fn}", payload, headers, timeout=20)

    # ---------------- uploading my score ----------------
    def schedule_sync(self):
        """Called after every save. Uploads a few seconds later (debounced)."""
        if not self.username or not self.online_ready():
            return
        if self.sync_ev is not None:
            self.sync_ev.cancel()
        self.sync_ev = Clock.schedule_once(lambda dt: self.sync_now(), SYNC_DELAY)

    def sync_now(self, announce=False):
        if self.sync_ev is not None:
            self.sync_ev.cancel()
            self.sync_ev = None
        if not self.username:
            return
        if not self.online_ready():
            if announce:
                self.set_status(self.describe_online_error("not_set_up"), YELLOW)
            return
        if self.sync_busy:
            self.sync_pending = True
            return
        self.sync_busy = True
        payload = {
            "p_id": self.player_id,
            "p_token": self.player_token,
            "p_username": self.username,
            "p_xp": int(self.xp),
            "p_quests": sum(1 for m in self.missions if m.get("done", False)),
            "p_streak": int(self.best_streak()),
            "p_avatar": self.avatar,
            "p_country": self.country,
        }
        threading.Thread(target=self._sync_worker, args=(payload, announce), daemon=True).start()

    def _sync_worker(self, payload, announce):
        res, err = None, ""
        try:
            res = self._rpc("submit_score", payload)
            if not (isinstance(res, dict) and res.get("ok")):
                err = res.get("error", "unknown") if isinstance(res, dict) else "unknown"
        except Exception as exc:
            self._note_err(exc)
            err = "network"
        self._sync_done(res, err, announce)

    @mainthread
    def _sync_done(self, res, err, announce):
        self.sync_busy = False
        if err:
            self.sync_note = "⚠️ " + self.describe_online_error(err)
            if err in ("bad_username", "name_taken"):
                self.username = self._prev_username
                self.save_data()
            if announce:
                self.set_status(self.sync_note, YELLOW)
                self.play_sound("error")
        else:
            self.server_username = self.username
            self.sync_note = f"☁️ Synced {datetime.now():%H:%M}"
            if announce:
                self.set_status("Profile saved. You're on the global leaderboard! 🌍", GREEN)
                self.play_sound("success")
                self.set_mascot("😎")
                self.fetch_leaderboard()
        self.refresh_profile(reset_input=bool(err and announce))
        if self.sync_pending:
            self.sync_pending = False
            self.sync_now()

    # ---------------- downloading the board ----------------
    def set_lb_scope(self, scope):
        if scope == "country" and not self.country:
            self.set_status("Pick a country first (PROFILE or SETTINGS).", YELLOW)
            self.play_sound("error")
            return
        self.lb_scope = scope
        self.update_scope_buttons()
        self.fetch_leaderboard()

    def update_scope_buttons(self):
        if hasattr(self, "scope_world"):
            is_w = (self.lb_scope == "world")
            self.scope_world.variant = "primary" if is_w else "secondary"
            self.scope_world.set_bg(NAV_ACTIVE if is_w else NAV_IDLE)
            self.scope_country.variant = "primary" if not is_w else "secondary"
            self.scope_country.set_bg(NAV_ACTIVE if not is_w else NAV_IDLE)

    def fetch_leaderboard(self, *_):
        if self.lb_busy:
            return
        if not self.online_ready():
            self.lb_note = "🛠️ Backend not set up yet. Add your Supabase URL + key in online.py."
            self.render_leaderboard()
            return
        self.lb_busy = True
        self.lb_note = "⏳ Loading the board…"
        self.render_leaderboard()
        scope_country = self.country if (self.lb_scope == "country" and self.country) else None
        threading.Thread(target=self._lb_worker, args=(scope_country,), daemon=True).start()

    def _lb_worker(self, scope_country):
        try:
            res = self._rpc("get_leaderboard", {"p_limit": 50, "p_id": self.player_id or None,
                                                "p_country": scope_country})
            rows = res.get("rows") or []
            me = res.get("me")
            self._lb_done(rows, me, "")
        except Exception as exc:
            self._note_err(exc)
            self._lb_done([], None, "network")

    @mainthread
    def _lb_done(self, rows, me, err):
        self.lb_busy = False
        if err:
            self.lb_note = "⚠️ " + self.describe_online_error(err)
        else:
            self.lb_rows, self.lb_me = rows, me
            self.lb_note = f"🌍 {len(rows)} players shown  •  updated {datetime.now():%H:%M}"
        self.render_leaderboard()
        self.refresh_profile()

    # ---------------- leaderboard page ----------------
    def build_leaderboard_page(self):
        page = self.make_page("leaderboard")
        b = page.body
        b.add_widget(section("🌍 GLOBAL LEADERBOARD", YELLOW))
        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        refresh = NeonButton(text="🔄 REFRESH", variant="primary", style="style2", size="small", bg_color=(0.02, 0.52, 0.82, 1))
        refresh.bind(on_press=self.fetch_leaderboard)
        prof = NeonButton(text="👤 MY PROFILE", variant="secondary", style="style2", size="small", bg_color=(0.20, 0.15, 0.45, 1))
        prof.bind(on_press=lambda *_: self.go_page("profile"))
        row.add_widget(refresh)
        row.add_widget(prof)
        b.add_widget(row)

        scope = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        self.scope_world = NeonButton(text="🌍 WORLD", variant="primary", style="style2", size="small", bg_color=NAV_ACTIVE)
        self.scope_world.bind(on_press=lambda *_: self.set_lb_scope("world"))
        self.scope_country = NeonButton(text="📍 MY COUNTRY", variant="secondary", style="style2", size="small", bg_color=NAV_IDLE)
        self.scope_country.bind(on_press=lambda *_: self.set_lb_scope("country"))
        scope.add_widget(self.scope_world)
        scope.add_widget(self.scope_country)
        b.add_widget(scope)

        self.lb_status = make_label("", 11, MUTED, True, auto_height=True)
        b.add_widget(self.lb_status)
        self.lb_list = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        self.lb_list.bind(minimum_height=self.lb_list.setter("height"))
        b.add_widget(self.lb_list)
        self.render_leaderboard()
        return page

    def make_lb_row(self, r):
        rank = safe_int(r.get("rnk"), 0)
        name = str(r.get("username", "???"))
        mine = bool(self.username) and name.lower() == self.username.lower()
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank)
        color = {1: YELLOW, 2: WHITE, 3: (1.0, 0.62, 0.25, 1)}.get(rank, PINK if mine else CYAN)
        row = NeonPanel(orientation="horizontal", padding=[dp(8), dp(4)], spacing=dp(6),
                        size_hint_y=None, height=dp(46), bg_color=PANEL_ALT,
                        border_color=(color[0], color[1], color[2], 0.85 if mine else 0.45))
        row.add_widget(make_label(medal or f"#{rank}", 13, color, True, halign="center",
                                  size_hint_x=None, width=dp(52), size_hint_y=1))
        row.add_widget(make_label(str(r.get("avatar") or "🤖")[:8], 18, WHITE, halign="center",
                                  size_hint_x=None, width=dp(38), size_hint_y=1))
        country = str(r.get("country") or "")
        if country:
            row.add_widget(self.make_flag(country, dp(34)))
        else:
            row.add_widget(Widget(size_hint_x=None, width=dp(34)))
        row.add_widget(make_label(name + ("  (YOU)" if mine else ""), 12, color, True, size_hint_y=1))
        lvl = safe_int(r.get("level"), 1)
        row.add_widget(make_label(f"LVL {lvl}  •  {safe_int(r.get('xp'), 0)} XP", 11, MUTED, True,
                                  halign="right", size_hint_x=None, width=dp(150), size_hint_y=1))
        return row

    def render_leaderboard(self):
        if not hasattr(self, "lb_list"):
            return
        note = self.lb_note
        if not self.username:
            note = (note + "\n" if note else "") + "👤 Pick a username in PROFILE to join the board."
        self.lb_status.text = note
        self.update_scope_buttons()
        self.lb_list.clear_widgets()
        if not self.lb_rows:
            if not self.lb_busy:
                self.lb_list.add_widget(make_label("🕳️ Nobody here yet. Be the first on the board!",
                                                   12, MUTED, size_hint_y=None, height=dp(40)))
            return
        for r in self.lb_rows:
            self.lb_list.add_widget(self.make_lb_row(r))
        me = self.lb_me
        if me and safe_int(me.get("rnk"), 0) > len(self.lb_rows):
            self.lb_list.add_widget(make_label("⋮", 14, MUTED, halign="center",
                                                size_hint_y=None, height=dp(22)))
            xp = safe_int(me.get("xp"), 0)
            self.lb_list.add_widget(self.make_lb_row({
                "rnk": me.get("rnk"), "username": me.get("username"), "avatar": self.avatar,
                "country": self.country, "xp": xp, "level": xp // 100 + 1}))

    # ---------------- profile page ----------------
    def build_profile_page(self):
        page = self.make_page("profile")
        b = page.body
        b.add_widget(section("👤 PLAYER PROFILE", PINK))

        top = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(12))
        self.profile_flag = self.make_flag(self.country, dp(78))
        self.profile_summary = make_label("", 14, WHITE, True, size_hint_y=1)
        top.add_widget(self.profile_flag)
        top.add_widget(self.profile_summary)
        b.add_widget(top)

        b.add_widget(section("✏️ EDIT PROFILE", CYAN))
        b.add_widget(make_label("Avatar", 11, MUTED, True, size_hint_y=None, height=dp(22)))
        grid = GridLayout(cols=5, spacing=dp(6), size_hint_y=None, height=dp(46 * 2 + 6))
        self.avatar_buttons = {}
        for a in AVATARS:
            btn = NeonButton(text=a, bg_color=NAV_IDLE)
            btn.font_size = "22sp"
            btn.bind(on_press=lambda _b, a=a: self.pick_avatar(a))
            grid.add_widget(btn)
            self.avatar_buttons[a] = btn
        b.add_widget(grid)

        b.add_widget(make_label("COUNTRY", 11, MUTED, True, size_hint_y=None, height=dp(22)))
        b.add_widget(self.make_country_row())

        b.add_widget(make_label("Username (3-16 letters, numbers or _)", 11, MUTED, True,
                                size_hint_y=None, height=dp(22)))
        self.profile_input = make_input("e.g. QuestGremlin42")
        self.profile_input.bind(text=self._limit_username)
        self.profile_input.bind(on_text_validate=self.save_profile)
        b.add_widget(self.profile_input)

        row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        save = NeonButton(text="💾 SAVE + JOIN BOARD", bg_color=(0.08, 0.38, 0.30, 1))
        save.bind(on_press=self.save_profile)
        leave = NeonButton(text="🚪 LEAVE BOARD", bg_color=(0.48, 0.10, 0.22, 1))
        leave.bind(on_press=self.leave_leaderboard)
        row.add_widget(save)
        row.add_widget(leave)
        b.add_widget(row)

        self.profile_sync_label = make_label("", 11, MUTED, True, auto_height=True)
        b.add_widget(self.profile_sync_label)
        b.add_widget(make_label(
            "🔒 Shared with the leaderboard: username, avatar, country, XP, level, quests cleared, best streak.\n"
            "🏠 Your quests, moods and AI chats never leave this PC.\n"
            "🚪 LEAVE BOARD deletes your row from the server.",
            10, MUTED, auto_height=True))
        self.refresh_profile(reset_input=True)
        return page

    def pick_avatar(self, a):
        self.avatar_choice = a
        for key, btn in self.avatar_buttons.items():
            btn.set_bg(NAV_ACTIVE if key == a else NAV_IDLE)

    def _limit_username(self, inst, value):
        clean = re.sub(r"[^A-Za-z0-9_]", "", value)[:16]
        if clean != value:
            inst.text = clean

    def refresh_profile(self, reset_input=False):
        if not hasattr(self, "profile_summary"):
            return
        level = self.xp // 100 + 1
        name = self.username or "(no username yet)"
        rank = f"#{self.lb_me.get('rnk')}" if self.lb_me and self.username else "unranked"
        self.profile_summary.text = (f"{self.avatar}  {name}\n"
                                     f"🏅 LEVEL {level}  •  ✨ {self.xp} XP  •  🌍 RANK {rank}")
        self.set_flag(self.profile_flag, self.country)
        if reset_input:
            self.profile_input.text = self.username
            self.pick_avatar(self.avatar)
        if self.sync_note:
            self.profile_sync_label.text = self.sync_note
        elif not self.username:
            self.profile_sync_label.text = "☁️ Not on the leaderboard yet. Pick a username!"
        else:
            self.profile_sync_label.text = ""

    def save_profile(self, *_):
        name = self.profile_input.text.strip()
        if not USERNAME_RE.match(name):
            self.set_status("Username: 3-16 letters, numbers or _ only. ✍️", YELLOW)
            self.play_sound("error")
            return
        if any(w and w in name.lower() for w in BANNED_WORDS):
            self.set_status("Pick a different username. 🙈", YELLOW)
            self.play_sound("error")
            return
        self.ensure_identity()
        self._prev_username = self.username
        self.username = name
        self.avatar = self.avatar_choice or AVATARS[0]
        self.save_data()
        if self.online_ready():
            self.sync_now(announce=True)
        else:
            self.sync_note = "🛠️ Saved on this PC. " + self.describe_online_error("not_set_up")
            self.set_status(self.sync_note, YELLOW)
            self.refresh_profile()

    def leave_leaderboard(self, *_):
        if not self.username:
            self.set_status("You're not on the leaderboard. 🤷", YELLOW)
            return
        pid, token = self.player_id, self.player_token
        self.username = ""
        self.server_username = ""
        self.sync_note = ""
        self.lb_me = None
        self.save_data()
        if self.online_ready() and pid:
            threading.Thread(target=self._leave_worker, args=(pid, token), daemon=True).start()
        self.set_status("You left the leaderboard. Your row is being deleted. 🚪", CYAN)
        self.refresh_profile(reset_input=True)
        self.render_leaderboard()

    def _leave_worker(self, pid, token):
        try:
            self._rpc("delete_me", {"p_id": pid, "p_token": token})
        except Exception as exc:
            self._note_err(exc)


def install(ns, app_cls):
    """Copy the helper names from main.py and attach the new methods to the app class."""
    for name in _NEEDED:
        globals()[name] = ns[name]
    for name, fn in OnlineMixin.__dict__.items():
        if callable(fn) and not name.startswith("__"):
            setattr(app_cls, name, fn)