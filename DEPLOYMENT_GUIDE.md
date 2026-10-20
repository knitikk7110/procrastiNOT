# 🚀 Deploying procrastiNOT to GitHub & Vercel

Follow this quick guide to publish **procrastiNOT** live to the web so anyone can access and install it on their phone, tablet, or desktop.

---

## Phase 1: Upload Project to GitHub

### Option A: Using GitHub Desktop (Easiest GUI)
1. Download & open [GitHub Desktop](https://desktop.github.com/).
2. Click **File** -> **Add Local Repository...**.
3. Choose `C:\Users\Asus\ProjectX` and click **Add Repository** (or **Create Repository** if prompted).
4. Enter commit summary: `Initial release of procrastiNOT web app`.
5. Click **Commit to main**, then click **Publish repository** to push it to your GitHub account.

### Option B: Using GitHub Web (No Software to Install)
1. Go to [github.com/new](https://github.com/new) and name your repository (e.g. `procrastiNOT`).
2. Leave "Initialize with README" unchecked and click **Create repository**.
3. On the next screen, click the link: **"uploading an existing file"**.
4. Drag and drop the following key files & folders from `C:\Users\Asus\ProjectX`:
   - `index.html`
   - `manifest.json`
   - `sw.js`
   - `vercel.json`
   - `assets/`
   - `mood_icons/`
   - `default_user_data.json`
   - `firebase_config.json`
5. Click **Commit changes**.

### Option C: Using Git in Terminal
If you have Git installed:
```powershell
git init
git add .
git commit -m "Deploy procrastiNOT to Vercel"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/procrastiNOT.git
git push -u origin main
```

---

## Phase 2: Deploy on Vercel (Free Global Hosting)

1. Go to [vercel.com](https://vercel.com) and sign in with your GitHub account.
2. In your Vercel Dashboard, click **Add New...** -> **Project**.
3. Under **Import Git Repository**, find your `procrastiNOT` repository and click **Import**.
4. **Project Settings:**
   - **Framework Preset:** Leave as *Other* (Vercel automatically detects `index.html` static site).
   - **Root Directory:** `./`
   - **Build & Output Settings:** Leave default.
5. Click **Deploy**.
6. In ~15 seconds, Vercel gives you your live HTTPS link (e.g., `https://procrastinot-iota.vercel.app`).

---

## Phase 3: Authorize Your Vercel Domain in Firebase (MANDATORY)

For Google Sign-In and Firebase Auth to work on your live URL:

1. Open [Firebase Console](https://console.firebase.google.com/).
2. Select your project: **`procastinot-38c73`**.
3. In the left menu, navigate to: **Build** -> **Authentication** -> **Settings** tab.
4. Scroll down to **Authorized domains** and click **Add domain**.
5. Paste your Vercel domain (for example: `procrastinot-iota.vercel.app` — *without `https://`*).
6. Click **Save**.

---

## 🎉 What Works Immediately on Your Live Link:
- **Instant Google Sign-In:** 1-tap sign-in on any phone, tablet, or PC worldwide.
- **Email & Password Authentication:** Real email verification and password resets.
- **PWA Installation:** Android & iOS users will see the "Install procrastiNOT" prompt on Chrome/Safari to install it as an app on their home screen.
- **AI Multimodal Verification:** Camera proof verification and file uploads function securely over HTTPS.
- **Real-Time Cloud Isolation:** Each user's XP, habits, quests, and rank are stored safely in Cloud Firestore.
