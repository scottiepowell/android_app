# syntax=docker/dockerfile:1               # enables ${TARGETPLATFORM} etc.

###########################
# 1) QEMU helper stage
###########################
FROM --platform=${BUILDPLATFORM} multiarch/qemu-user-static:latest AS qemu

###########################
# 2) Real arm64 image
###########################
ARG TARGETPLATFORM
FROM --platform=${TARGETPLATFORM} ubuntu:22.04

# ── add the right QEMU static binary ─────────────────────────────
# For arm64 builds TARGETPLATFORM = "linux/arm64", and the helper
# we need is /usr/bin/qemu-aarch64-static .
#
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin/

# ── your original tool‑chain setup (unchanged) ───────────────────
RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      python3-pip python3-distutils python3-dev git \
      openjdk-11-jdk unzip zip wget build-essential \
      libncurses5 libffi-dev libssl-dev libsqlite3-dev \
      zlib1g-dev libjpeg-dev python3-setuptools python3-virtualenv \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip

ENV PIP_ROOT_USER_ACTION=ignore

# Buildozer & friends
RUN pip3 install --no-cache-dir \
      buildozer cython appdirs "colorama>=0.3.3" jinja2 \
      "sh>=1.10,<2.0; sys_platform!='win32'" build toml packaging setuptools

###########################
# ANT
###########################
ENV ANT_VERSION=1.9.4             \
    ANT_HOME=/opt/ant
RUN wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
 && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
 && mv /opt/apache-ant-${ANT_VERSION} $ANT_HOME \
 && rm apache-ant-${ANT_VERSION}-bin.tar.gz
ENV PATH="$ANT_HOME/bin:${PATH}"

###########################
# Android SDK + NDK
###########################
ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
ENV ANDROID_SDK_ROOT=$ANDROID_HOME
RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    cd $ANDROID_HOME/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mv cmdline-tools tools

ENV PATH="$ANDROID_HOME/cmdline-tools/tools/bin:${PATH}"
RUN yes | sdkmanager \
      "platform-tools" \
      "platforms;android-33" \
      "build-tools;33.0.2" \
      "ndk;25.2.9519653"

ENV NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
ENV PATH="$NDK_HOME:${PATH}"

###########################
# app source
###########################
WORKDIR /app
COPY . /app