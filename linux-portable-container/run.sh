#!/bin/sh
set -e

SRCDIR="$(readlink -e "$(dirname "$0")")"
if [ -f $HOME/.cerbero/cerbero.cbc ]; then
    BUILDDIR=$(python - <<EOF
import sys, os, os.path, imp
sys.path.append(os.path.join("$SRCDIR", ".."))
cerbero = imp.load_source("config", os.path.join(os.getenv("HOME"), ".cerbero/cerbero.cbc"))
print cerbero.home_dir
EOF
    )
else
    BUILDDIR=$(readlink -e .)
    if [ "$BUILDDIR" == "$SRCDIR" ]; then
        BUILDDIR="$BUILDDIR"/build
    fi
    mkdir -p "$BUILDDIR"/sources/local
fi

arch=${1:-x86_64}
EXTRA_VOLUMES=$(
    IFS=:
    for d in $EXTRA_SOURCES; do
        IFS=, read dir mount <<< "$d"
        dir=$(readlink -e "$dir")
        if [ -z "$mount" ]; then mount=$(basename "$dir"); fi
        echo -n " -v $dir:/home/cerbero/build/sources/local/$mount:ro"
    done
)

DOCKERFILE="$SRCDIR"/docker/Dockerfile

case $arch in
    x86_64)
        ;;
    i686)
        DOCKERFILE="$DOCKERFILE".i686
        trap "rm $DOCKERFILE" EXIT
        sed -e "s/amd64/i386/" \
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

[ -S ~/.git-credential-cache/socket ] && GIT_CREDENTIAL_CACHE="-v $HOME/.git-credential-cache/socket:/home/cerbero/.git-credential-cache/socket"
docker run -it --rm \
    --privileged \
    -h squeeze-$arch \
    --name squeeze-$arch \
    -v "$SRCDIR"/..:/home/cerbero/cerbero:ro \
    -v "$BUILDDIR":/home/cerbero/build \
    $GIT_CREDENTIAL_CACHE \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /etc/localtime:/etc/localtime:ro \
    $EXTRA_VOLUMES \
    -e TERM=$TERM \
    -e LOCAL_UID=`id -u` -e LOCAL_GID=`id -g` \
    linux-portable-$arch

