#!/bin/bash

source ~/kivy_venv/bin/activate

sudo chmod 666 /dev/ttyAMA0

python ~/Podco_Metal_Detections/server/main.py &

echo "Metal Detection Server start succesfully..."
