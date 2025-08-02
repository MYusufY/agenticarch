#!/bin/bash

set -x

user_mounts="/run/media/$(whoami)"
mkdir -p "$user_mounts"

handle_new_device() {
    local device=$1
    local mount_point="$user_mounts/$device"
    
    local storage_info=$(df -h "$mount_point" --output=source,size,fstype | tail -n 1)
    local storage_size=$(echo "$storage_info" | awk '{print $2}')
    local filesystem=$(echo "$storage_info" | awk '{print $3}')
    local device_source=$(echo "$storage_info" | awk '{print $1}')

    notify-send -i drive-removable-media "USB Device Connected" \
                "Device: $device\nPath: $mount_point\nSource: $device_source\nSize: $storage_size\nType: $filesystem" \
                -a "USBAgent" -u normal \
                --action="open_usbagent=Open USBAgent" \
                | while read response; do
        if [ "$response" = "open_usbagent" ]; then
            python3 /ace/agent/usbagent.py "$mount_point" "$device" &
        fi
    done
}

inotifywait -m "$user_mounts" -e create --format '%f' | while read device_name; do
    if [ -d "$user_mounts/$device_name" ]; then
        handle_new_device "$device_name"
    fi
done
