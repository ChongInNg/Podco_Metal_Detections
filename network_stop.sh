#!/bin/bash

sudo systemctl stop networking.service
sudo systemctl disable networking.service
echo "disable networking.service successfully."


sudo systemctl stop dhcpcd
sudo systemctl disable dhcpcd
echo "disable dhcpcd successfully."
