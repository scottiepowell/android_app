# syntax=docker/dockerfile:1

###########################
# 1) QEMU helper stage
###########################
FROM --platform=${BUILDPLATFORM} multiarch/qemu-user-static:latest AS qemu

###########################
# 2) Real ARM64 image
###########################
ARG TARGETPLATFORM
FROM --platform=${TARGETPLATFORM} ubuntu:22.04

# QEMU binary for ARM emulation
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin/

# Base setup
RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      python3-pip python3-distutils python3-dev git \
      openjdk-11-jdk unzip zip wget build-essential \
      libncurses5 libffi-dev libssl-dev libsqlite3-dev \
      zlib1g-dev libjpeg-dev python3-setuptools python3-virtualenv \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip

ENV PIP_ROOT_USER_ACTION=ignore

# Buildozer and Python deps
RUN pip3 install --no-cache-dir \
      buildozer cython appdirs "colorama>=0.3.3" jinja2 \
      "sh>=1.10,<2.0; sys_platform!='win32'" build toml packaging setuptools

###########################
# Apache ANT
###########################
ENV ANT_VERSION=1.9.4
ENV ANT_HOME=/opt/ant
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

# Install commandline-tools
RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    cd $ANDROID_HOME/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mv cmdline-tools tools

# Ensure PATH includes sdkmanager
ENV PATH="$ANDROID_HOME/cmdline-tools/tools/bin:$PATH"

# Install only compatible versions
RUN yes | sdkmanager \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.2" \
    "ndk;25.2.9519653"

ENV NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
ENV PATH="$NDK_HOME:$PATH"

# Legacy symlink fixes for sdkmanager detection
RUN mkdir -p $ANDROID_HOME/tools/bin && \
    ln -sf $ANDROID_HOME/cmdline-tools/tools/bin/sdkmanager $ANDROID_HOME/tools/bin/sdkmanager

# Remove all traces of newer build-tools to prevent fallback
RUN rm -rf $ANDROID_HOME/build-tools/36.0.0 || true

# Force symlink to correct version to intercept auto-pick
RUN ln -sfn $ANDROID_HOME/build-tools/33.0.2 $ANDROID_HOME/build-tools/36.0.0

###########################
# Copy source & set workdir
###########################
WORKDIR /app
COPY . /app