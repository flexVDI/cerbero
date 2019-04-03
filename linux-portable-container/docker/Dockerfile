FROM amd64/debian:wheezy-backports
RUN apt-get update && apt-get install -y \
    sudo vim git wget fuse-utils make gcc g++ \
    libgmp3-dev libmpfr-dev libmpc-dev libc6-dev-i386 \
    autoconf automake libtool gettext pkg-config \
    zlib1g-dev \
    python python-argparse python-pyparsing cmake libfuse-dev libglib2.0-dev texinfo gtk-doc-tools \
    flex bison python-dev libxcb-damage0-dev libxcb-shm0-dev libxcb-xfixes0-dev libxcb-xtest0-dev libxi-dev \
    libdbus-1-dev libxtst-dev libegl1-mesa-dev libudev-dev libtext-csv-perl libxrender-dev python-setuptools \
    strace libasound2-dev libxcursor-dev libpciaccess-dev libxrandr-dev libxinerama-dev libxv-dev \
    selinux-policy-dev libpam-dev fonts-lato python3

# Pre-setup user cerbero
RUN echo "cerbero ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
ADD appimagetool-x86_64.AppImage /home/cerbero/bin/appimagetool
ADD bashrc /home/cerbero/.bash_profile
ADD gitconfig /home/cerbero/.gitconfig
ADD cerbero.cbc /home/cerbero/.cerbero/cerbero.cbc
RUN sed -i -e 's/__arch__/arch = target_arch = Architecture.X86_64/' \
    -e 's/__build__/build = "x86_64-linux-gnu"/' /home/cerbero/.cerbero/cerbero.cbc
ADD wgetrc /home/cerbero/.wgetrc
ADD setup_user.sh /root/setup_user.sh
RUN chmod 755 /home/cerbero/bin/* /root/setup_user.sh
CMD [ "/root/setup_user.sh" ]

