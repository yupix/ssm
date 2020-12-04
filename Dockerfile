#FROM oblique/archlinux-yay AS base
FROM alpine AS base

WORKDIR /ssm

FROM base AS builder

#RUN sudo -u aur yay --noconfirm -S \
#    open-jtalk

#RUN pacman --noconfirm -Sy \
#    python-pip \
#    python \

RUN apk add \
    py3-pip \
    libxml2 \
    libxslt-dev \
    python3 \
    python3-dev \
    gcc \
    g++

COPY . ./

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
