[app]

title = ServiClick
package.name = com.servi.click
package.domain = org.test
version = 1.0 # ¡Añade esta línea!
source.dir = .
source.include_exts = py,png,jpg,kv,json

requirements = python3,kivy,sqlite3,matplotlib

orientation = portrait

android.api = 33
android.minapi = 21
android.ndk = 25b

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE

# Services
# services = MyService:service.py

# Presplash
# android.presplash_color = #000000
# android.presplash_image = %(source)s/data/presplash.png

# Debug
# android.debug = 1

# Release
# android.release_keystore = %(user_dir)s/.android/debug.keystore
# android.release_keystore_alias = debug
# android.release_keystore_pass = android

# Icon
# icon.filename = %(source)s/data/icon.png

# Exclude
# exclude_dirs = .buildozer, .git, __pycache__, bin, venv, .github
