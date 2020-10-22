FROM debian:buster
LABEL maintainer=me@ethandjeric.com
LABEL version="0.1 beta"
LABEL calibre_version="3.39.1"
LABEL metadata.db_version="3.39.1 - from Debian Buster VM."

ENV IMPORT_TIME=10m UMASK_SET=022

RUN apt-get update && \
    apt-get install -y \
        inotify-tools \
        # I am sticking with python2 calibre in buster that is fairly old - 3.39.1 vs 5.3.0 in stable and testing)
        # As this is a headless install I do not see the need for a newer version and 
        # v5 uses python3 which breaks compatibility with many plugins such as the popular DeDRM.
        # If you wish to include newer v5 calibre build from debian:bullseye/recent ubuntu or use the official calibre install script instead of apt.
        calibre \
        # all apt/pip below this point is for kcc
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
    apt-get clean && \
    rm -rf \
        /tmp/* \
	    /var/lib/apt/lists/* \
        /var/cache/apt/* \
	    /var/tmp/* 

COPY image_root/ /

RUN calibre-customize --add-plugin /plugins/DeDRM_6.8.0.zip

ENTRYPOINT ["/entrypoint.sh"]
