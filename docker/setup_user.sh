#!/bin/sh
[ -n "$LOCAL_UID" -a -n "$LOCAL_GID" ] || {
    echo Define the environment variables LOCAL_UID and LOCAL_GID
    exit 1
}
groupadd -g $LOCAL_GID cerbero
useradd -d /home/cerbero -g cerbero -M -u $LOCAL_UID -s /bin/bash -G fuse cerbero
find /home/cerbero -xdev -exec chown cerbero:cerbero \{\} \;
exec su -l cerbero

