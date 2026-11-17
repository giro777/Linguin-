[app]

title = Almanca by Laurence
package.name = almancavokabeln
package.domain = org.vokabeln

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,docx,gif,mp3

version = 0.1

requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.0,gtts,requests,urllib3,certifi,idna,charset-normalizer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

p4a.branch = v2024.01.21
p4a.extra_args = --graphics=sdl2

[buildozer]

log_level = 2
warn_on_root = 1
