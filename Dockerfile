FROM debian:buster
LABEL maintainer=me@ethandjeric.com

RUN apt-get update -y && \
    apt-get install -y \
    