# hciuart.service
```
bluetooth
```

# dev-mmcblk0p2.device (cannot stop)
```
sd card mount service
```

# man-db.service
```
man-db.timer
man-db.service
```

#cups.service
```
print service
```

# raspi-config.service
```
raspi config
```

# apt-daily.service and apt-daily-upgrade.service
```
apt update
```

# update cmdline.txt
```
/boot/cmdline.txt
```

# dphys-swapfile.service
```
manage swap file
```

# avahi-daemon.service and avahi-daemon.socket
```
network discovery
```

# ModemManager.service

# colord.service
```
sudo systemctl mask colord.service
systemctl list-dependencies --reverse colord.service

sudo apt-get remove --purge colord
```

# polkit.service
```
 Authorization service
```

# rsyslog.service and syslog.socket
```
system log
```

# rng-tools-debian.service
```
```

# rpi-eeprom-update.service

# triggerhappy.service


# nfs-config.service

# odprobe@drm.service
```
modprobe@configfs.service
modprobe@fuse.service

need disable and mask
````

# plymouth-start.service
```
plymouth-quit.service
plymouth-quit-wait.service
plymouth-read-write.service
```