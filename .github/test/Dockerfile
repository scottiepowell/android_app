FROM ubuntu:22.04

LABEL org.opencontainers.image.source="https://github.com/scottiepowell/android_app"

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-distutils \
    python3-dev \
    git \
    openjdk-11-jdk \
    unzip \
    zip \
    wget \
    build-essential \
    libncurses5 \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    zlib1g-dev \
    libjpeg-dev \
    python3-setuptools \
    python3-virtualenv \
    && pip3 install --upgrade pip

ENV PIP_ROOT_USER_ACTION=ignore

# Install Buildozer & Dependencies
RUN pip3 install --no-cache-dir \
    buildozer \
    cython \
    appdirs \
    colorama>=0.3.3 \
    jinja2 \
    "sh>=1.10,<2.0; sys_platform!='win32'" \
    build \
    toml \
    packaging \
    setuptools

# Pre-install Apache ANT for Buildozer
ENV ANT_VERSION=1.9.4
ENV ANT_HOME=/opt/ant
RUN wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
    && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
    && mv /opt/apache-ant-${ANT_VERSION} $ANT_HOME \
    && rm apache-ant-${ANT_VERSION}-bin.tar.gz
ENV PATH="${ANT_HOME}/bin:$PATH"

# Install Android command line tools (sdkmanager)
ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
ENV ANDROID_SDK_ROOT=$ANDROID_HOME
RUN mkdir -p $ANDROID_HOME/cmdline-tools
WORKDIR $ANDROID_HOME/cmdline-tools
RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip \
    && unzip -q commandlinetools-linux-9477386_latest.zip \
    && rm commandlinetools-linux-9477386_latest.zip

# Because the cmdline-tools are inside a folder named "cmdline-tools" again
# we rename them "latest" or "tools" to keep sdkmanager at a stable path
RUN mv cmdline-tools tools

# Accept licenses and install a minimal set of packages.  This can be minimal
# because buildozer might still download additional components
# as needed. But at least sdkmanager must exist.
ENV PATH=$ANDROID_HOME/cmdline-tools/tools/bin:$PATH
RUN yes | sdkmanager \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.2" \
    "ndk;25.2.9519653"

# Create final working dir
WORKDIR /app
COPY . /app