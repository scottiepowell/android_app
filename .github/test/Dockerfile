# ------------------------------------------------------------
# ❶  arm64 base layer + qemu‑x86_64 so we can execute x86‑64
# ------------------------------------------------------------
    FROM --platform=linux/arm64 ubuntu:22.04

    # QEMU static binary – copied from the official multiarch image
    COPY --from=multiarch/qemu-user-static:latest \
          /usr/bin/qemu-x86_64-static /usr/bin/
    
    # Enable the amd64 architecture *inside* the arm64 rootfs so that we can
    # install the x86‑64 C runtime the Android Build‑Tools need.
    RUN dpkg --add-architecture amd64 && \
        apt-get update && \
        # ––––– minimal x86‑64 runtime and loader –––––
        DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
            libc6:amd64 libstdc++6:amd64 zlib1g:amd64
    
    # ------------------------------------------------------------
    # ❷  common build dependencies (arm64 packages are fine here)
    # ------------------------------------------------------------
    RUN apt-get install -y --no-install-recommends \
            python3-pip python3-dev python3-distutils python3-setuptools \
            git openjdk-11-jdk wget unzip zip build-essential \
            libffi-dev libssl-dev libsqlite3-dev libjpeg-dev libncurses5 && \
        pip3 install --upgrade pip
    
    # Buildozer + helpers (pure‑python → architecture‑independent)
    RUN pip3 install --no-cache-dir \
            buildozer==1.4.0 cython appdirs colorama jinja2 \
            "sh>=1.10,<2.0; sys_platform!='win32'" \
            build toml packaging setuptools
    
    # ------------------------------------------------------------
    # ❸  Apache Ant (needed by Buildozer)
    # ------------------------------------------------------------
    ENV ANT_VERSION=1.9.4 \
        ANT_HOME=/opt/ant
    RUN wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
     && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
     && mv /opt/apache-ant-${ANT_VERSION} "$ANT_HOME" \
     && rm apache-ant-${ANT_VERSION}-bin.tar.gz
    ENV PATH="$ANT_HOME/bin:${PATH}"
    
    # ------------------------------------------------------------
    # ❹  Android SDK / NDK (still the x86‑64 binaries)
    # ------------------------------------------------------------
    ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk \
        ANDROID_SDK_ROOT=/root/.buildozer/android/platform/android-sdk
    
    RUN mkdir -p "$ANDROID_HOME/cmdline-tools" && \
        cd "$ANDROID_HOME/cmdline-tools" && \
        wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
        unzip -q commandlinetools-linux-9477386_latest.zip && \
        rm commandlinetools-linux-9477386_latest.zip && \
        mv cmdline-tools tools
    
    ENV PATH="$ANDROID_HOME/cmdline-tools/tools/bin:${PATH}"
    
    # pre‑install only what Buildozer really needs
    RUN yes | sdkmanager --licenses >/dev/null && \
        yes | sdkmanager \
            "platform-tools" \
            "platforms;android-33" \
            "build-tools;33.0.2" \
            "ndk;25.2.9519653"
    
    ENV NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
    ENV PATH="$NDK_HOME:${PATH}"
    
    # ------------------------------------------------------------
    # ❺  your application source
    # ------------------------------------------------------------
    WORKDIR /app
    COPY . /app    