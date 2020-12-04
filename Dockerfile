FROM oblique/archlinux-yay AS base

WORKDIR /ssm

FROM base AS builder

RUN sudo -u aur yay --noconfirm -S \
    open-jtalk

RUN pacman --noconfirm -Sy \
    python-pip \
    python \

COPY . ./

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
