[app]

title = ServiClick
package.name = com.servi.click
package.domain = org.test
version = 1.0
source.dir = .
source.include_exts = py,png,jpg,kv,json

requirements = python3,kivy,sqlite3,matplotlib,certifi,requests

orientation = portrait
android.api = 33
android.minapi = 24
android.ndk = 26d
android.archs = arm64-v8a, armeabi-v7a

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Presplash
# android.presplash_color = #000000
# android.presplash_image = %(source)s/data/presplash.png

# Icon
# icon.filename = %(source)s/data/icon.png
