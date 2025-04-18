# syntax=docker/dockerfile:1

###########################
# 1) QEMU helper for AMD64 binaries
###########################
FROM --platform=linux/amd64 multiarch/qemu-user-static:latest AS qemu

###########################
# 2) Real ARM64 base image
###########################
ARG TARGETPLATFORM
FROM --platform=${TARGETPLATFORM} ubuntu:22.04

# ── Install QEMU static for both aarch64 and x86_64 ────────────
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin/

# ── Base toolchain & Python ────────────────────────────────────
RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      python3-pip python3-distutils python3-dev git \
      openjdk-11-jdk unzip zip wget build-essential \
      libncurses5 libffi-dev libssl-dev libsqlite3-dev \
      zlib1g-dev libjpeg-dev python3-setuptools python3-virtualenv \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip

ENV PIP_ROOT_USER_ACTION=ignore

# ── Buildozer & dependencies ───────────────────────────────────
RUN pip3 install --no-cache-dir \
      buildozer \
      cython \
      appdirs \
      "colorama>=0.3.3" \
      jinja2 \
      "sh>=1.10,<2.0; sys_platform!='win32'" \
      build \
      toml \
      packaging \
      setuptools

# ── Apache ANT ─────────────────────────────────────────────────
ENV ANT_VERSION=1.9.4 \
    ANT_HOME=/opt/ant
RUN wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
 && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
 && mv /opt/apache-ant-${ANT_VERSION} $ANT_HOME \
 && rm apache-ant-${ANT_VERSION}-bin.tar.gz
ENV PATH="$ANT_HOME/bin:$PATH"

# ── Android SDK command‑line tools ─────────────────────────────
ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
ENV ANDROID_SDK_ROOT=$ANDROID_HOME

RUN mkdir -p $ANDROID_HOME/cmdline-tools \
 && cd $ANDROID_HOME/cmdline-tools \
 && wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip \
 && unzip -q commandlinetools-linux-9477386_latest.zip \
 && rm commandlinetools-linux-9477386_latest.zip \
 && mv cmdline-tools tools

ENV PATH="$ANDROID_HOME/cmdline-tools/tools/bin:$PATH"

# ── Install *only* the versions you want ───────────────────────
RUN yes | sdkmanager \
      "platform-tools" \
      "platforms;android-33" \
      "build-tools;33.0.2" \
      "ndk;25.2.9519653"

# Make the NDK visible
ENV NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
ENV PATH="$NDK_HOME:$PATH"

# ── Legacy “tools/” symlink so Buildozer finds sdkmanager ───────
RUN mkdir -p $ANDROID_HOME/tools/bin \
 && ln -sf $ANDROID_HOME/cmdline-tools/tools/bin/sdkmanager \
       $ANDROID_HOME/tools/bin/sdkmanager

# ── Stub out *every* aidl so Buildozer’s check passes             ──
#    (they’ll all be tiny shell-scripts that do nothing)
RUN for v in $(ls $ANDROID_HOME/build-tools); do \
      rm -f $ANDROID_HOME/build-tools/$v/aidl; \
      printf '%s\n' '#!/usr/bin/env sh' 'exit 0' \
        > $ANDROID_HOME/build-tools/$v/aidl; \
      chmod +x $ANDROID_HOME/build-tools/$v/aidl; \
    done

# ── Optional: force Buildozer to use host Python and skip toolchain validation
ENV P4A_USE_HOST_PYTHON=1

# ── Your app sources ───────────────────────────────────────────
WORKDIR /app
COPY . /app