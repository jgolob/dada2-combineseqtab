# dada2-fast-combineseqtab
#
# VERSION               golob/dada2-fast-combineseqtab:0.6.7


FROM --platform=amd64 debian:bookworm-slim

RUN export TZ=Etc/UTC
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get update && \
apt-get -y install tzdata && \
apt-get install -y \
    r-base \
    pigz \
    python3-pip \
&& apt-get clean \
&& apt-get purge \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD . /src/

RUN cd /src/ && \
pip3 install --break-system-packages . && \
cd /root/

WORKDIR /root/