#!/usr/bin/env bash

sudo systemctl start lightdm

WALLPAPER="/ace/wallpapers/bg.png"
MONITORS=$(xrandr --query | grep " connected" | cut -d ' ' -f1)
for MONITOR in $MONITORS; do
  for WORKSPACE in $(seq 0 9); do
    PROP="/backdrop/screen0/monitor${MONITOR}/workspace${WORKSPACE}/last-image"
    if ! xfconf-query -c xfce4-desktop -p "$PROP" &>/dev/null; then
      xfconf-query -c xfce4-desktop -p "$PROP" --create -t string -s "$WALLPAPER"
    else
      xfconf-query -c xfce4-desktop -p "$PROP" -s "$WALLPAPER"
    fi
  done
done

xfdesktop --reload

chmod +x /usr/local/bin/agent

bash /ace/agent/usbagent.sh > /dev/null 2>&1 &