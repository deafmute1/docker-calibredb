FROM ubuntu:hirsuite
LABEL maintainer="ethan@ethandjeric.com"
LABEL version="1.3"
LABEL metadata.default.db_version="3.39.1-debian10"

RUN apt-get update && \
    apt-get install -y \
    # ubuntu hirsuite has calibre v5
        calibre \ 
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
        KindleComicConverter-headless && \
    # install app requirements
    pip3 install -r /app/requirements.txt && \
    # multi arch for i386 kindlegen binary support
    dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install libc6-i386 && \
    # clean up
    apt-get clean && \
    rm -rf \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/cache/apt/* \
    /var/tmp/*

COPY root/ /

USER root

RUN calibre-customize --add-plugin /calibre/plugins/DeDRM_7.2.1.zip

ENTRYPOINT ["python3", "/calibre/app/main.py"]
