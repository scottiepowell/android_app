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

# ── Install QEMU for ARM emulation ─────────────────────────────
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

# ── python‑for‑android & deps ─────────────────────────────────
RUN pip3 install --no-cache-dir \
      python-for-android \
      cython \
      packaging

###########################
# Apache ANT (needed by p4a)
###########################
ENV ANT_VERSION=1.9.4 \
    ANT_HOME=/opt/ant
RUN wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
 && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
 && mv /opt/apache-ant-${ANT_VERSION} $ANT_HOME \
 && rm apache-ant-${ANT_VERSION}-bin.tar.gz
ENV PATH="$ANT_HOME/bin:$PATH"

###########################
# Android SDK + NDK
###########################
ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
ENV ANDROID_SDK_ROOT=$ANDROID_HOME

RUN mkdir -p $ANDROID_HOME/cmdline-tools \
 && cd $ANDROID_HOME/cmdline-tools \
 && wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip \
 && unzip -q commandlinetools-linux-9477386_latest.zip \
 && rm commandlinetools-linux-9477386_latest.zip \
 && mv cmdline-tools tools

ENV PATH="$ANDROID_HOME/cmdline-tools/tools/bin:$PATH"

# install exactly what we need
RUN yes | sdkmanager \
      "platform-tools" \
      "platforms;android-33" \
      "build-tools;33.0.2" \
      "ndk;25.2.9519653"

ENV NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
ENV PATH="$NDK_HOME:$PATH"

# legacy “tools/” symlink so p4a finds sdkmanager
RUN mkdir -p $ANDROID_HOME/tools/bin \
 && ln -sf $ANDROID_HOME/cmdline-tools/tools/bin/sdkmanager \
       $ANDROID_HOME/tools/bin/sdkmanager

# ── Also expose sdkmanager at sdk-dir/bin/sdkmanager ─────
RUN mkdir -p $ANDROID_HOME/bin \
 && ln -sf $ANDROID_HOME/tools/bin/sdkmanager \
       $ANDROID_HOME/bin/sdkmanager

# ── Your app sources ───────────────────────────────────────────
WORKDIR /app
COPY . /app