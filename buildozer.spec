[app]
title = whats_in_the_box
package.name = kivyapp
package.domain = org.box
source.dir = .
requirements = python3,kivy,sqlalchemy,click,sqlite3
icon.filename = assets/pencil.png
presplash.filename = assets/pencil.png
android.permissions = INTERNET
version = 0.0.1
orientation = portrait
source.include_patterns = src/*, assets/pencil.png
android.build_tools_version = 33.0.2
android.api = 33

android.ant_path = /opt/ant

[buildozer]
storage_dir = /mnt/storage/.buildozer
log_level = 2
warn_on_root = 0
p4a.buildtools = 33.0.2