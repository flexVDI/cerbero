#!/bin/sh
set -e

# TODO: Build base images with docker's mkimage.sh

docker build -t linux-portable-x86_64 docker

rm -f docker/Dockerfile.i686
cp docker/Dockerfile docker/Dockerfile.i686
sed -i -e "s/:6-x86_64/:6-i386/" -e "s/libc6-dev-i386/libc6-dev-amd64/" -e "s/Architecture.X86_64/Architecture.X86/" docker/Dockerfile.i686
docker build -t linux-portable-i686 -f docker/Dockerfile.i686 docker

