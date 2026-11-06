[app]
title = Brain Blitz
package.name = brainblitz
package.domain = com.abhi.games
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions =
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True
