#!/bin/sh
arch=${1:-x86_64}

docker run -it --rm \
    --privileged \
    -h squeeze-$arch \
    --name squeeze-$arch \
    -v /home/javi/src/cerbero:/home/cerbero/cerbero \
    -v /home/javi/build/linux-portable/src:/home/cerbero/src \
    -v /home/javi/build/linux-portable/${arch}-build:/home/cerbero/build \
    -v /home/javi/build/linux-portable/${arch}-target:/usr/local \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /etc/localtime:/etc/localtime:ro \
    -e TERM=$TERM \
    -e LOCAL_UID=`id -u` -e LOCAL_GID=`id -g` \
    linux-portable-$arch
