#!/bin/bash
# Build newer gcc, run from build dir

set -e

SRC=`dirname "$0"`
SRC=`readlink -e "$SRC"`
NP=`grep processor /proc/cpuinfo | wc -l`
ARCH=`if file /bin/ls | grep -q "32-bit"; then echo i686; else echo x86_64; fi`

gitclone() {
    local url="$1"
    local dst="$2"
    test -d "$dst" || git clone "$url" "$dst"
}

getarchive() {
    local url="$1"
    local ar="$2"
    local dst="$3"
    test -f "$ar" || wget "$url" -O "$ar"
    test -d "$dst" || {
        local ar_dir=`dirname "$ar"`
        local untar_dir="$ar_dir"/`tar taf "$ar" | tail -1 | cut -d / -f 1`
        tar xaf "$ar" -C "$ar_dir"
        test "$untar_dir" == "$dst" || mv "$untar_dir" "$dst"
    }
}

setdst() {
    test -d "$1" || mkdir "$1"
    cd "$1"
}

autotools_configure() {
    local src="$1"
    shift
    test -f $src/configure || $src/autogen.sh
    test -f Makefile || $src/configure "$@"
}

GCC_VER=gcc-4.8.5
GCC_AR=${GCC_VER}.tar.bz2
GCC_URL=ftp://ftp.lip6.fr/pub/gcc/releases/$GCC_VER/$GCC_AR
CONFIG_OPTS="--enable-languages=c,c++ --enable-shared --enable-multiarch --enable-linker-build-id --with-system-zlib --without-included-gettext --enable-threads=posix --enable-nls --with-arch-32=i686 --with-tune=generic --enable-checking=release"
if [ "$ARCH" == i686 ]; then
   CONFIG_OPTS="$CONFIG_OPTS --build=i686-linux-gnu --host=i686-linux-gnu --target=i686-linux-gnu"
fi

getarchive $GCC_URL $SRC/$GCC_AR $SRC/$GCC_VER
setdst $GCC_VER
autotools_configure $SRC/$GCC_VER $CONFIG_OPTS
test -f gcc/xgcc || make -j$NP
test /usr/local/bin/gcc -nt gcc/xgcc || make install

