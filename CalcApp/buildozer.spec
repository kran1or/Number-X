[app]
title = NumberX
package.name = numberx
package.domain = org.numberx

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = logo.png,dps.png
source.exclude_patterns = venv,.git,.github,__pycache__,bin,.buildozer

version = 1.0.0
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.permissions = INTERNET

# Иконка приложения
icon.filename = %(source.dir)s/logo.png

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1