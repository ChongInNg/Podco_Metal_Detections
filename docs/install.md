# install in raspberry pi
```
python -m venv kivy_venv

source kivy_venv\Scripts\activate


sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev \
    libgdk-pixbuf2.0-dev libjpeg8-dev liblcms2-dev libblas-dev libatlas-base-dev \
    gfortran libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    xorg-dev libglu1-mesa libgles2-mesa libegl1-mesa libinput-dev \
    libfreetype6-dev libfontconfig1-dev libx11-dev libxkbcommon-dev \
    libmtdev-dev

python3 -m pip install kivy[base] kivy_examples

```