[app]
title = dummy
package.name = dummy
package.domain = org.example
source.dir = /tmp/dummy-src
requirements = python3
android.api = 33
android.build_tools_version = 33.0.2
android.ndk = 25b
android.ndk_path = /root/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = /root/.buildozer/android/platform/android-sdk
android.ant_path = /opt/ant
android.accept_sdk_license = True
# Prevent auto-installation of new SDK components
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 0
p4a.install_build_tools = false
android.accept_sdk_license = True
storage_dir = /tmp/dummy_buildozer
