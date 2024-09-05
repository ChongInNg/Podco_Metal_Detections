#!/bash/bin

sudo systemctl enable networking.service
sudo systemctl start networking.service
echo "start networking.service successfully"

sudo systemctl enable dhcpcd
sudo systemctl start dhcpcd
echo "start dhcpcd service successfully."


