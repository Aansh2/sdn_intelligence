# Mininet
FROM ubuntu:16.04

MAINTAINER Fernando Benayas <ferbenayas94@gmail.com>
#Based on the Dockerfile provided by Iwase Yusuke (https://hub.docker.com/r/iwaseyusuke/mininet)

USER root
WORKDIR /root

COPY entrypoint.sh /
COPY mininet .

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sudo \
    iproute2 \
    iputils-ping \
    net-tools \
    socat \
    tcpdump \
    python \
    python-pip \
    python-setuptools \
    python-matplotlib \
    vim \
    x11-xserver-utils \
    xterm \
    git-all\
    lsb-release\
 && rm -rf /var/lib/apt/lists/* \
 && mv /bin/ping /sbin/ping \
 && mv /bin/ping6 /sbin/ping6 \
 && mv /usr/sbin/tcpdump /usr/bin/tcpdump \
 && chmod +x /entrypoint.sh \
 && chmod -R +x ./net \
 && pip install networkx \
    matplotlib

RUN git config --global url.https://github.com/.insteadOf git://github.com/
RUN git clone https://github.com/mininet/mininet
WORKDIR /root/mininet
RUN git checkout -b 2.2.2 2.2.2
WORKDIR /root
RUN chmod +x mininet/util/install.sh
RUN mininet/util/install.sh -a

RUN pip install --upgrade pip
RUN pip install -U pip setuptools

EXPOSE 6640
ENTRYPOINT ["/entrypoint.sh"]