FROM ubuntu:22.04

RUN apt update && apt install -y \
    python3-pip \
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

RUN pip install buildozer cython

ENV ANDROID_HOME=/root/.buildozer/android/platform/android-sdk
RUN mkdir -p $ANDROID_HOME

WORKDIR /app
COPY . /app
