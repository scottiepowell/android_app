FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
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
    && apt clean

# Install buildozer and Cython
RUN pip install --upgrade pip \
    && pip install buildozer cython

WORKDIR /app
