#!/bin/bash

sudo systemctl stop dhcpcd
sudo systemctl disable dhcpcd

echo "stop dhcpcd successfully."
