# 📱 How to Convert procrastiNOT into an Android APK

**procrastiNOT.exe** is built using Python + Kivy and is already configured for Android compilation with camera, storage, and AI vision support.

Because Android compilation toolchains (Android NDK, SDK, GCC, Clang, and autotools) require a Linux environment, **Buildozer cannot compile natively inside pure Windows PowerShell**.

Here are the 3 ways to build your APK:

---

## 🚀 Option 1: GitHub Actions (Recommended — 100% Free, Zero PC Setup)

A ready-to-run GitHub Actions workflow has already been configured in [`.github/workflows/build_apk.yml`](file:///.github/workflows/build_apk.yml).

1. Push your project code to a GitHub repository (public or private).
2. Go to your repository on GitHub and click the **Actions** tab.
3. Select **Build Android APK (procrastiNOT)** and click **Run workflow**.
4. GitHub's cloud servers (Ubuntu) will install the Android SDK/NDK, compile the Python code, and generate the `.apk`.
5. When the build finishes (approx. 10–12 minutes), click the completed run, scroll down to **Artifacts**, and download **`procrastiNOT-Android-APK`**.
6. Transfer the `.apk` to your phone (or download it directly from GitHub on your phone browser) and tap to install!

---

## ⚡ Option 2: Google Colab (Build in Browser — No Git Push Needed)

If you don't want to use GitHub, you can use Google's free Linux cloud servers:

1. Compress your project folder into a `.zip` file (`ProjectX.zip`).
2. Open [Google Colab](https://colab.research.google.com/) and create a **New Notebook**.
3. In the first code cell, paste and run:
   ```bash
   !sudo apt update
   !sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   !pip install --upgrade buildozer cython virtualenv
   ```
4. Upload your `ProjectX.zip` to the Colab files panel on the left.
5. In a second code cell, unzip and run Buildozer:
   ```bash
   !unzip -q ProjectX.zip -d app
   %cd app
   !buildozer -v android debug
   ```
6. In a third code cell, download the generated APK:
   ```python
   from google.colab import files
   import glob
   files.download(glob.glob('bin/*.apk')[0])
   ```

---

## 💻 Option 3: Local Build via WSL on Windows

If you prefer building locally on your Windows computer:

1. Open PowerShell as Administrator and install WSL (Ubuntu):
   ```powershell
   wsl --install
   ```
   *(Reboot your PC if prompted).*
2. Open Ubuntu from your Start menu and navigate to your project directory:
   ```bash
   cd /mnt/c/Users/Asus/ProjectX
   ```
3. Install the required build tools:
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   pip3 install --upgrade buildozer cython virtualenv
   ```
4. Run the build command:
   ```bash
   buildozer -v android debug
   ```
5. Your compiled `.apk` will be saved directly into `c:\Users\Asus\ProjectX\bin\`.

---

## 📲 How to Install on Your Android Phone

1. Transfer the `.apk` file to your phone via USB, Google Drive, WhatsApp, or email.
2. Tap the `.apk` file on your phone.
3. If Android prompts *"Install unknown apps"*, tap **Settings** and toggle **Allow from this source**.
4. Tap **Install** and launch **procrastiNOT**!
