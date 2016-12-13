#!/bin/sh
arch=${1:-x86_64}

docker run -it --rm \
    --privileged \
    -h squeeze-$arch \
    -v /home/javi/src/linux-portable/src:/home/javi/src \
    -v /home/javi/build/linux-portable/${arch}-build:/home/javi/build \
    -v /home/javi/build/linux-portable/${arch}-target:/usr/local \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e TERM=$TERM \
    linux-portable-$arch
