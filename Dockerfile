FROM ubuntu:hirsute
LABEL maintainer="ethan@ethandjeric.com"
LABEL version="v2.0.1"
LABEL metadata.default.db_version="3.39.1"
LABEL calibre_verison="5.11.0+dfsg-1"

    # enable i386 for kindlegen support
RUN dpkg --add-architecture i386 && \  
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        # ubuntu hirsuite has calibre v5
        calibre \ 
        # kindlegen support
        libc6-i386 \ 
    # install kcc and deps
        python3 \
        python3-wheel \
        python3-dev \
        python3-pip \
        python3-setuptools \
        libpng-dev \
        libjpeg-dev \
        p7zip-full && \
    pip3 install \
        pillow \
        python-slugify==2.0.1 \
        psutil \ 
        KindleComicConverter-headless \
    # install /app requirements
        watchdog \ 
        schedule && \
    # clean up
    apt-get clean && \
    rm -rf \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/cache/apt/* \
    /var/tmp/*

COPY root/ /

USER root

RUN /bin/sh /usr/local/bin/after_build.sh

ENTRYPOINT ["python3", "/app/main.py"]
