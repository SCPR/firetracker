FROM python:2.7.13-alpine

MAINTAINER Ben Titcomb <btitcomb@scpr.org>

RUN apk update && apk add \
  autoconf \
  bash \
  g++ \
  gcc \
  git \
  libc-dev \
  libffi-dev \
  libgcc \
  libxml2-dev \
  libxslt-dev \
  make \
  mariadb-dev \
  py-mysqldb \
  yaml \
  yaml-dev \
  zlib-dev

USER root
ENV HOME /root
WORKDIR $HOME
COPY . .

ENV PATH="/root/bin:${PATH}"

RUN pip install -r requirements.txt
RUN echo "titlecase==0.5.1" >> requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT /bin/bash

