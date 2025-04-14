FROM ubuntu:22.04

# Link the image to the GitHub repository (optional)
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

# Tells pip not to complain about root install
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip3 install buildozer cython

ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
RUN mkdir -p $ANDROID_HOME

WORKDIR /app
COPY . /app