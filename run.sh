#!/bin/sh
SRC=`readlink -e $0`
SRCDIR=`dirname "$SRC"`
BUILDDIR=`pwd`
BUILDDIR=`readlink -e "$BUILDDIR"`
arch=${1:-x86_64}

set -e

DOCKERFILE="$SRCDIR"/docker/Dockerfile

case $arch in
    x86_64) ;;
    i686)
        DOCKERFILE="$DOCKERFILE".i686
        trap "rm $DOCKERFILE" EXIT
        sed -e "s/:6-x86_64/:6-i386/" \
            -e "s/libc6-dev-i386/libc6-dev-amd64/" \
            -e "s/Architecture.X86_64/Architecture.X86/" \
            -e "s/x86_64-linux-gnu/i686-linux-gnu/" \
            -e "s/appimagetool-x86_64/appimagetool-i686/" \
            "$SRCDIR"/docker/Dockerfile > $DOCKERFILE
        ;;
    *)
        echo "WARNING: Unknown architecture $arch, using x86_64"
        arch=x86_64
        ;;
esac

# TODO: Build base images with docker's mkimage.sh

docker build -t linux-portable-$arch -f "$DOCKERFILE" "$SRCDIR"/docker

docker run -it --rm \
    --privileged \
    -h squeeze-$arch \
    --name squeeze-$arch \
    -v /home/javi/src/cerbero:/home/cerbero/cerbero:ro \
    -v /home/javi/build/linux-portable/src:/home/cerbero/src \
    -v /home/javi/build/linux-portable/${arch}-build:/home/cerbero/build \
    -v /home/javi/build/linux-portable/${arch}-target:/usr/local \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /etc/localtime:/etc/localtime:ro \
    -e TERM=$TERM \
    -e LOCAL_UID=`id -u` -e LOCAL_GID=`id -g` \
    linux-portable-$arch

