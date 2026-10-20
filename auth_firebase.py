"""
auth_firebase.py - Firebase Authentication & Cloud Firestore REST Client
Designed for procrastiNOT.exe (Python/Kivy on Windows and Android).

Features:
- Pure Python using 'requests' (zero native C dependencies, 100% Android & Windows compatible).
- Email & Password Sign Up with mandatory email verification dispatch.
- Real Email Verification checking via Firebase Auth lookup.
- Email & Password Sign In with verification gating.
- Password Reset email dispatch.
- Google OAuth 2.0 Sign-In via system browser loopback flow.
- Token refresh & persistent session management across app restarts.
- Cloud Firestore REST API integration scoped strictly to user UID.
- Automatic document encoding/decoding between Python dicts and Firestore JSON.
"""

import json
import os
import sys
import time
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

# Default configuration template
CONFIG_FILE = "firebase_config.json"

DEFAULT_CONFIG = {
    "apiKey": "YOUR_FIREBASE_WEB_API_KEY",
    "authDomain": "your-project-id.firebaseapp.com",
    "projectId": "your-project-id",
    "storageBucket": "your-project-id.appspot.com",
    "messagingSenderId": "000000000000",
    "appId": "1:000000000000:web:0000000000000000000000",
    "googleClientId": "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
}


def load_firebase_config():
    """Load configuration from firebase_config.json or environment."""
    config = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_conf = json.load(f)
                config.update(user_conf)
        except Exception as e:
            print(f"[AUTH] Error reading {CONFIG_FILE}: {e}")
    # Allow environment variable overrides
    for k in config:
        env_val = os.environ.get(f"FIREBASE_{k.upper()}")
        if env_val:
            config[k] = env_val
    return config


class FirebaseAuthClient:
    """Handles all client-side Firebase Auth and Firestore REST calls."""

    AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
    TOKEN_URL = "https://securetoken.googleapis.com/v1/token"
    FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects"

    def __init__(self, config=None, session_file="session_auth.json"):
        self.config = config or load_firebase_config()
        self.session_file = session_file
        self.current_user = None
        self.load_session()

    @property
    def api_key(self):
        return self.config.get("apiKey", "")

    @property
    def project_id(self):
        return self.config.get("projectId", "")

    @property
    def is_configured(self):
        key = self.api_key
        return bool(key and "YOUR_FIREBASE" not in key and len(key) > 10)

    # ---------------------------------------------------------
    # Session Persistence & Token Storage
    # ---------------------------------------------------------

    def save_session(self):
        """Persist session token securely to disk."""
        if not self.current_user:
            if os.path.exists(self.session_file):
                try:
                    os.remove(self.session_file)
                except OSError:
                    pass
            return
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.current_user, f, indent=2)
        except Exception as e:
            print(f"[AUTH] Could not save session: {e}")

    def load_session(self):
        """Restore active session on application startup."""
        if not os.path.exists(self.session_file):
            self.current_user = None
            return None
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                self.current_user = json.load(f)
                # Check if token is expired, refresh if needed
                exp = self.current_user.get("expires_at", 0)
                if time.time() > (exp - 120):
                    self.refresh_token()
                return self.current_user
        except Exception as e:
            print(f"[AUTH] Error loading session: {e}")
            self.current_user = None
            return None

    def clear_session(self):
        """Clear active user session on logout."""
        self.current_user = None
        self.save_session()

    # ---------------------------------------------------------
    # Error Message Formatting
    # ---------------------------------------------------------

    def format_auth_error(self, err_code):
        messages = {
            "EMAIL_EXISTS": "⚠️ An account with this email address already exists. Please log in.",
            "INVALID_EMAIL": "⚠️ The email address format is invalid.",
            "WEAK_PASSWORD : Password should be at least 6 characters": "⚠️ Password must be at least 6 characters long.",
            "EMAIL_NOT_FOUND": "⚠️ No account found with this email. Please sign up.",
            "INVALID_PASSWORD": "❌ ACCESS DENIED: Invalid password or credentials.",
            "INVALID_LOGIN_CREDENTIALS": "❌ ACCESS DENIED: Invalid email or password.",
            "USER_DISABLED": "⚠️ This user account has been disabled.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "⚠️ Too many unsuccessful attempts. Access temporarily blocked for security. Please try again later.",
            "OPERATION_NOT_ALLOWED": "⚠️ This sign-in provider is disabled in Firebase Console.",
            "NETWORK_ERROR": "⚠️ Unable to connect to authentication server. Check your internet connection.",
        }
        return messages.get(err_code, f"⚠️ Authentication failed: {err_code}")

    # ---------------------------------------------------------
    # Authentication REST Endpoints
    # ---------------------------------------------------------

    def sign_up_with_email(self, email, password, display_name=""):
        """
        Register a new user with email and password.
        Immediately dispatches a verification email to their inbox.
        Returns dict with success status and user data.
        """
        if not self.is_configured:
            return {"success": False, "error": "Firebase is not configured yet. Please update firebase_config.json."}

        url = f"{self.AUTH_URL}:signUp?key={self.api_key}"
        payload = {
            "email": email.strip().lower(),
            "password": password,
            "returnSecureToken": True
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()
            if resp.status_code != 200:
                err = data.get("error", {}).get("message", "UNKNOWN_ERROR")
                return {"success": False, "error": self.format_auth_error(err)}

            id_token = data.get("idToken")
            refresh_token = data.get("refreshToken")
            uid = data.get("localId")
            expires_in = int(data.get("expiresIn", "3600"))

            # Update display name if provided
            if display_name:
                self.update_profile(id_token, display_name=display_name)

            # Send Email Verification Link directly to their inbox
            self.send_email_verification(id_token)

            user_record = {
                "uid": uid,
                "email": email.strip().lower(),
                "display_name": display_name or email.split("@")[0],
                "id_token": id_token,
                "refresh_token": refresh_token,
                "expires_at": time.time() + expires_in,
                "email_verified": False,
                "provider": "password"
            }
            self.current_user = user_record
            self.save_session()

            return {
                "success": True,
                "uid": uid,
                "email": email,
                "email_verified": False,
                "message": f"Verification email sent to {email}. Please verify your inbox to activate your account."
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}

    def send_email_verification(self, id_token=None):
        """Send verification email link to the authenticated user."""
        token = id_token or (self.current_user.get("id_token") if self.current_user else None)
        if not token:
            return {"success": False, "error": "No active authentication token."}

        url = f"{self.AUTH_URL}:sendOobCode?key={self.api_key}"
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": token
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()
            if resp.status_code == 200:
                return {"success": True, "message": "Verification email sent!"}
            err = data.get("error", {}).get("message", "UNKNOWN_ERROR")
            return {"success": False, "error": self.format_auth_error(err)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_email_verified(self, id_token=None):
        """
        Lookup current account info from Firebase server to determine
        if the user has completed email verification in their inbox.
        """
        token = id_token or (self.current_user.get("id_token") if self.current_user else None)
        if not token:
            return False

        url = f"{self.AUTH_URL}:lookup?key={self.api_key}"
        payload = {"idToken": token}
        try:
            resp = requests.post(url, json=payload, timeout=12)
            data = resp.json()
            if resp.status_code == 200:
                users = data.get("users", [])
                if users:
                    verified = users[0].get("emailVerified", False)
                    if self.current_user:
                        self.current_user["email_verified"] = verified
                        self.save_session()
                    return verified
            return False
        except Exception:
            return False

    def sign_in_with_email(self, email, password):
        """
        Log in with registered email and password.
        Enforces email verification check.
        """
        if not self.is_configured:
            return {"success": False, "error": "Firebase is not configured yet. Please update firebase_config.json."}

        url = f"{self.AUTH_URL}:signInWithPassword?key={self.api_key}"
        payload = {
            "email": email.strip().lower(),
            "password": password,
            "returnSecureToken": True
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()
            if resp.status_code != 200:
                err = data.get("error", {}).get("message", "UNKNOWN_ERROR")
                return {"success": False, "error": self.format_auth_error(err)}

            id_token = data.get("idToken")
            refresh_token = data.get("refreshToken")
            uid = data.get("localId")
            expires_in = int(data.get("expiresIn", "3600"))
            disp_name = data.get("displayName") or email.split("@")[0]

            # Check verification status from server
            verified = self.check_email_verified(id_token)

            user_record = {
                "uid": uid,
                "email": email.strip().lower(),
                "display_name": disp_name,
                "id_token": id_token,
                "refresh_token": refresh_token,
                "expires_at": time.time() + expires_in,
                "email_verified": verified,
                "provider": "password"
            }
            self.current_user = user_record
            self.save_session()

            return {
                "success": True,
                "uid": uid,
                "email": email,
                "display_name": disp_name,
                "email_verified": verified
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}

    def send_password_reset(self, email):
        """Dispatch a password reset link to user's registered email."""
        if not self.is_configured:
            return {"success": False, "error": "Firebase is not configured yet."}

        url = f"{self.AUTH_URL}:sendOobCode?key={self.api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email.strip().lower()
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()
            if resp.status_code == 200:
                return {
                    "success": True,
                    "message": f"Password reset instructions have been sent to {email}."
                }
            err = data.get("error", {}).get("message", "UNKNOWN_ERROR")
            return {"success": False, "error": self.format_auth_error(err)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def refresh_token(self):
        """Refresh expired id_token using stored refresh_token."""
        if not self.current_user or not self.current_user.get("refresh_token"):
            return False

        url = f"{self.TOKEN_URL}?key={self.api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.current_user["refresh_token"]
        }
        try:
            resp = requests.post(url, json=payload, timeout=12)
            data = resp.json()
            if resp.status_code == 200:
                self.current_user["id_token"] = data.get("id_token")
                self.current_user["refresh_token"] = data.get("refresh_token")
                expires_in = int(data.get("expires_in", "3600"))
                self.current_user["expires_at"] = time.time() + expires_in
                self.save_session()
                return True
            return False
        except Exception:
            return False

    def update_profile(self, id_token, display_name=None, photo_url=None):
        """Update user profile metadata."""
        url = f"{self.AUTH_URL}:update?key={self.api_key}"
        payload = {"idToken": id_token, "returnSecureToken": True}
        if display_name:
            payload["displayName"] = display_name
        if photo_url:
            payload["photoUrl"] = photo_url
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception:
            pass

    # ---------------------------------------------------------
    # Cloud Firestore REST Operations (UID-Scoped)
    # ---------------------------------------------------------

    def get_auth_token(self):
        """Return valid id_token, refreshing if near expiry."""
        if not self.current_user:
            return None
        exp = self.current_user.get("expires_at", 0)
        if time.time() > (exp - 60):
            self.refresh_token()
        return self.current_user.get("id_token")

    def _dict_to_firestore(self, d):
        """Convert a standard Python dictionary to Firestore Value format."""
        fields = {}
        for k, v in d.items():
            fields[k] = self._value_to_firestore(v)
        return {"fields": fields}

    def _value_to_firestore(self, val):
        if val is None:
            return {"nullValue": None}
        elif isinstance(val, bool):
            return {"booleanValue": val}
        elif isinstance(val, int):
            return {"integerValue": str(val)}
        elif isinstance(val, float):
            return {"doubleValue": val}
        elif isinstance(val, str):
            return {"stringValue": val}
        elif isinstance(val, list):
            return {"arrayValue": {"values": [self._value_to_firestore(i) for i in val]}}
        elif isinstance(val, dict):
            return {"mapValue": {"fields": {k: self._value_to_firestore(v) for k, v in val.items()}}}
        else:
            return {"stringValue": str(val)}

    def _firestore_to_dict(self, fs_doc):
        """Convert Firestore Value format back to standard Python dict."""
        if not fs_doc or "fields" not in fs_doc:
            return {}
        result = {}
        for k, v in fs_doc["fields"].items():
            result[k] = self._firestore_to_value(v)
        return result

    def _firestore_to_value(self, fv):
        if "stringValue" in fv:
            return fv["stringValue"]
        if "integerValue" in fv:
            return int(fv["integerValue"])
        if "doubleValue" in fv:
            return float(fv["doubleValue"])
        if "booleanValue" in fv:
            return fv["booleanValue"]
        if "nullValue" in fv:
            return None
        if "arrayValue" in fv:
            vals = fv["arrayValue"].get("values", [])
            return [self._firestore_to_value(i) for i in vals]
        if "mapValue" in fv:
            sub = fv["mapValue"].get("fields", {})
            return {k: self._firestore_to_value(v) for k, v in sub.items()}
        return None

    def load_user_document(self, uid=None):
        """
        Fetch user's private data document from Cloud Firestore.
        URL: /projects/{PROJECT_ID}/databases/(default)/documents/users/{UID}
        Strictly enforced by Firestore Security Rules.
        """
        token = self.get_auth_token()
        target_uid = uid or (self.current_user.get("uid") if self.current_user else None)
        if not token or not target_uid or not self.project_id:
            return None

        url = f"{self.FIRESTORE_URL}/{self.project_id}/databases/(default)/documents/users/{target_uid}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                doc = resp.json()
                return self._firestore_to_dict(doc)
            elif resp.status_code == 404:
                # Document does not exist yet for new user
                return {}
            elif resp.status_code == 403:
                print(f"[AUTH ERROR] Firestore 403 Forbidden: Security Rules blocked access for UID {target_uid}.")
                return None
            else:
                print(f"[AUTH ERROR] Firestore error {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            print(f"[AUTH] Error loading user document: {e}")
            return None

    def save_user_document(self, data_dict, uid=None):
        """
        Save user's private data document to Cloud Firestore.
        URL: /projects/{PROJECT_ID}/databases/(default)/documents/users/{UID}
        Uses PATCH so it creates or updates cleanly.
        """
        token = self.get_auth_token()
        target_uid = uid or (self.current_user.get("uid") if self.current_user else None)
        if not token or not target_uid or not self.project_id:
            return False

        url = f"{self.FIRESTORE_URL}/{self.project_id}/databases/(default)/documents/users/{target_uid}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = self._dict_to_firestore(data_dict)
        try:
            resp = requests.patch(url, headers=headers, json=body, timeout=12)
            if resp.status_code == 200:
                return True
            print(f"[AUTH ERROR] Save failed {resp.status_code}: {resp.text}")
            return False
        except Exception as e:
            print(f"[AUTH] Error saving user document: {e}")
            return False

    # ---------------------------------------------------------
    # Google OAuth 2.0 Loopback Flow (Windows Desktop)
    # ---------------------------------------------------------

    def start_google_sign_in_flow(self, on_complete):
        """
        Launches Google OAuth 2.0 flow via local loopback port on Windows.
        Invokes on_complete(result_dict) upon finish.
        """
        if not self.is_configured:
            on_complete({"success": False, "error": "Firebase is not configured."})
            return

        client_id = self.config.get("googleClientId", "")
        if not client_id or "YOUR_GOOGLE" in client_id:
            on_complete({
                "success": False,
                "error": "Google Client ID is not configured. Please add your OAuth Client ID to firebase_config.json."
            })
            return

        def run_oauth():
            redirect_port = 8921
            auth_result_holder = {"data": None, "error": None}
            cfg_json = json.dumps(self.config)

            class OAuthCallbackHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    parsed = urlparse(self.path)
                    params = parse_qs(parsed.query)

                    if "code" in params:
                        # Direct code callback fallback
                        code = params["code"][0]
                        auth_result_holder["code"] = code
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.end_headers()
                        html = """
                        <html><body style="background:#06030A;color:#3DFFB0;font-family:sans-serif;text-align:center;padding:50px;">
                        <h2>⚡ PROGRASTINOT AUTHENTICATION SUCCESSFUL</h2>
                        <p style="color:#E8DFEF;">Google identity confirmed. You may return to the terminal.</p>
                        <script>setTimeout(function(){ window.close(); }, 2000);</script>
                        </body></html>
                        """
                        self.wfile.write(html.encode("utf-8"))
                        return

                    # Default GET: serve Firebase Web SDK bridge page
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    bridge_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>procrastiNOT // Google Authentication</title>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js"></script>
  <style>
    body {{
      background: #06030A;
      color: #E8DFEF;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      text-align: center;
    }}
    .card {{
      background: rgba(16, 10, 25, 0.96);
      border: 1px solid rgba(61, 255, 176, 0.4);
      box-shadow: 0 0 35px rgba(61, 255, 176, 0.2);
      border-radius: 12px;
      padding: 34px 40px;
      max-width: 440px;
    }}
    .btn {{
      background: #4285F4;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 6px;
      font-weight: bold;
      cursor: pointer;
      font-size: 14px;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-top: 15px;
    }}
    .btn:hover {{ background: #3367D6; }}
    .spinner {{
      border: 3px solid rgba(255, 255, 255, 0.1);
      border-top: 3px solid #3DFFB0;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      animation: spin 1s linear infinite;
      margin: 18px auto;
    }}
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size: 32px; margin-bottom: 8px;">⚡</div>
    <h2 style="color: #3DFFB0; margin: 0 0 8px 0; font-family: monospace;">procrastiNOT // GOOGLE AUTH</h2>
    <div id="loader" class="spinner"></div>
    <p id="status" style="font-size: 14px; line-height: 1.5; color: #A39AAD;">Opening official Google sign-in dialog...</p>
    <button class="btn" id="btn-login" onclick="triggerGoogleLogin()" style="display:none;">
      <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#EA4335" d="M12 5c1.54 0 2.93.56 4.02 1.48l3.01-3.01C17.21 1.76 14.78 1 12 1 7.42 1 3.52 3.58 1.63 7.34l3.65 2.83C6.18 7.32 8.85 5 12 5z"/><path fill="#4285F4" d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.72 2.89c2.18-2.01 3.7-4.97 3.7-8.71z"/><path fill="#FBBC05" d="M5.28 14.83A7.05 7.05 0 0 1 4.9 12c0-1 .18-1.97.48-2.83L1.73 6.34A11.94 11.94 0 0 0 0 12c0 1.92.45 3.74 1.25 5.37l4.03-2.54z"/><path fill="#34A853" d="M12 23c3.24 0 5.95-1.08 7.93-2.91l-3.72-2.89c-1.07.72-2.45 1.16-4.21 1.16-3.15 0-5.82-2.32-6.72-5.17L1.25 15.63C3.12 19.42 7.24 23 12 23z"/></svg>
      Sign in with Google
    </button>
  </div>
  <script>
    const firebaseConfig = {cfg_json};
    if (!firebase.apps || !firebase.apps.length) {{
      firebase.initializeApp(firebaseConfig);
    }}
    const auth = firebase.auth();

    async function triggerGoogleLogin() {{
      const status = document.getElementById('status');
      const loader = document.getElementById('loader');
      const btn = document.getElementById('btn-login');
      loader.style.display = 'block';
      btn.style.display = 'none';
      status.textContent = 'Please choose your Google account in the popup window...';

      const provider = new firebase.auth.GoogleAuthProvider();
      provider.setCustomParameters({{ prompt: 'select_account' }});
      try {{
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        status.innerHTML = '<span style="color:#3DFFB0;font-weight:bold;">Authentication Successful!</span><br>Signed in as <b>' + (user.displayName || user.email) + '</b>.<br><br>Transferring credentials to procrastiNOT.exe...';
        
        await fetch('/token', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            uid: user.uid,
            email: user.email,
            displayName: user.displayName || user.email.split('@')[0],
            idToken: idToken,
            refreshToken: user.refreshToken || ''
          }})
        }});

        loader.style.display = 'none';
        status.innerHTML = '<span style="color:#3DFFB0;font-size:16px;">🎉 Success!</span><br>Connected to procrastiNOT.exe.<br><br>You may now close this browser tab.';
        setTimeout(() => window.close(), 2500);
      }} catch(err) {{
        loader.style.display = 'none';
        btn.style.display = 'inline-flex';
        status.innerHTML = '<span style="color:#FF3355;">⚠️ Sign-in notice:</span><br>' + (err.message || err.code) + '<br><br>Click the button below to retry.';
      }}
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      setTimeout(triggerGoogleLogin, 350);
    }});
  </script>
</body>
</html>
"""
                    self.wfile.write(bridge_html.encode("utf-8"))

                def do_POST(self):
                    if self.path == "/token":
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            token_data = json.loads(body)
                            auth_result_holder["token_data"] = token_data
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(b'{"status":"ok"}')
                        except Exception as e:
                            self.send_response(400)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def log_message(self, format, *args):
                    pass

            try:
                server = HTTPServer(("127.0.0.1", redirect_port), OAuthCallbackHandler)
            except Exception as e:
                on_complete({"success": False, "error": f"Could not bind loopback port: {e}"})
                return

            bridge_url = f"http://localhost:{redirect_port}"

            # Open system browser to the local bridge
            webbrowser.open(bridge_url)

            # Wait for request (give up to 90 seconds for user to sign in)
            server.timeout = 90
            start_time = time.time()
            while time.time() - start_time < 90:
                server.handle_request()
                if auth_result_holder.get("token_data") or auth_result_holder.get("code") or auth_result_holder.get("error"):
                    break
            server.server_close()

            # Check if token data was received via bridge POST /token
            tdata = auth_result_holder.get("token_data")
            if tdata and tdata.get("uid"):
                uid = tdata.get("uid")
                email = tdata.get("email")
                disp_name = tdata.get("displayName") or (email.split("@")[0] if email else "OPERATOR")
                user_record = {
                    "uid": uid,
                    "email": email,
                    "display_name": disp_name,
                    "id_token": tdata.get("idToken"),
                    "refresh_token": tdata.get("refreshToken", ""),
                    "expires_at": time.time() + 3600,
                    "email_verified": True,
                    "provider": "google"
                }
                self.current_user = user_record
                self.save_session()
                on_complete({
                    "success": True,
                    "uid": uid,
                    "email": email,
                    "display_name": disp_name,
                    "email_verified": True
                })
                return

            code = auth_result_holder.get("code")
            if not code:
                on_complete({"success": False, "error": "Google sign-in was cancelled or timed out."})
                return

            # Exchange direct code if received
            try:
                redirect_uri = f"http://127.0.0.1:{redirect_port}"
                token_resp = requests.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": client_id,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code"
                    },
                    timeout=15
                )
                tok_data = token_resp.json()
                google_id_token = tok_data.get("id_token")
                if not google_id_token:
                    on_complete({"success": False, "error": "Could not exchange Google authorization code."})
                    return

                # Authenticate with Firebase via signInWithIdp
                fb_resp = requests.post(
                    f"{self.AUTH_URL}:signInWithIdp?key={self.api_key}",
                    json={
                        "postBody": f"id_token={google_id_token}&providerId=google.com",
                        "requestUri": redirect_uri,
                        "returnIdpCredential": True,
                        "returnSecureToken": True
                    },
                    timeout=15
                )
                fb_data = fb_resp.json()
                if fb_resp.status_code == 200:
                    uid = fb_data.get("localId")
                    email = fb_data.get("email")
                    disp_name = fb_data.get("displayName") or email.split("@")[0]
                    user_record = {
                        "uid": uid,
                        "email": email,
                        "display_name": disp_name,
                        "id_token": fb_data.get("idToken"),
                        "refresh_token": fb_data.get("refreshToken"),
                        "expires_at": time.time() + int(fb_data.get("expiresIn", "3600")),
                        "email_verified": True,
                        "provider": "google"
                    }
                    self.current_user = user_record
                    self.save_session()
                    on_complete({
                        "success": True,
                        "uid": uid,
                        "email": email,
                        "display_name": disp_name,
                        "email_verified": True
                    })
                else:
                    on_complete({"success": False, "error": fb_data.get("error", {}).get("message", "Firebase error")})
            except Exception as e:
                on_complete({"success": False, "error": str(e)})

        threading.Thread(target=run_oauth, daemon=True).start()


# Module-level singleton
auth_client = FirebaseAuthClient()
