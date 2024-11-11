[app]
title = whats_in_the_box
package.name = kivyapp
package.domain = org.box
source.dir = .
requirements = python3,kivy,sqlalchemy,click,sqlite3
icon.filename = ../assets/pencil.png
presplash.filename = ../assets/pencil.png
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
version = 0.0.1
orientation = portrait

source.include_patterns = src/*

[buildozer]
log_level = 2
warn_on_root = 1
