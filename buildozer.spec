[app]

# (str) Title of your application
title = procrastiNOT

# (str) Package name
package.name = procrastinot

# (str) Package domain (needed for android/ios packaging)
package.domain = org.procrastinot

# (str) Source code where the main.py lives
source.dir = .

# (str) Application versioning
version = 0.1

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,otf,wav,mp3

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,plyer,pillow

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,INTERNET

# (list) Android features required by the application
android.features = android.hardware.camera,android.hardware.camera.autofocus

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android SDK
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
