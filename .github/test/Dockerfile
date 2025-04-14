FROM ubuntu:22.04

LABEL org.opencontainers.image.source="https://github.com/scottiepowell/android_app"

RUN apt update && apt install -y \
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

# Install Buildozer and all the packages it tries to use:
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

# Download and install Apache ANT (Buildozer expects 1.9.4 by default)
ENV ANT_VERSION=1.9.4
ENV ANT_HOME=/opt/ant

RUN wget https://archive.apache.org/dist/ant/binaries/apache-ant-${ANT_VERSION}-bin.tar.gz \
    && tar -xzf apache-ant-${ANT_VERSION}-bin.tar.gz -C /opt \
    && mv /opt/apache-ant-${ANT_VERSION} $ANT_HOME \
    && rm apache-ant-${ANT_VERSION}-bin.tar.gz

# Add ANT to PATH
ENV PATH="${ANT_HOME}/bin:$PATH"


ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
RUN mkdir -p $ANDROID_HOME

WORKDIR /app
COPY . /app