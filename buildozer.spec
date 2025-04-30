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
android.build_tools_version = 36.0.0
android.api = 33
android.sdk_path = /opt/android-sdk

android.ant_path = /opt/ant

[buildozer]
storage_dir = /.buildozer
log_level = 2
warn_on_root = 0
p4a.install_build_tools = false