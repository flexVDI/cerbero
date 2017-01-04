FROM jcelaya/debian:6-x86_64
ARG uid=1000
ARG user_name
RUN test -n "$user_name" || { echo "user_name must be defined" >&2 ; exit 1; }
ARG user_group=users
RUN apt-get update && apt-get install -y \
    sudo vim git wget fuse-utils \
    libgmp3-dev libmpfr-dev libmpc-dev libc6-dev-i386 \
    autoconf automake libtool gettext pkg-config \
    zlib1g-dev

# Create current user
ENV HOME /home/$user_name
RUN useradd -d $HOME -g $user_group -M -u $uid -s /bin/bash $user_name
RUN echo $user_name "ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN sed -i 's/\(^fuse:.*\)/\1'${user_name}'/' /etc/group
RUN mkdir -p $HOME/bin
ADD bashrc $HOME/.bashrc
ADD cerbero.cbc $HOME/.cerbero/cerbero.cbc
RUN sed -i 's;/home/user;'${HOME}';' $HOME/.cerbero/cerbero.cbc
ADD appimagetool-x86_64.AppImage $HOME/bin/appimagetool
RUN chown -R $user_name:$user_group $HOME

# Cerbero dependencies
RUN echo "deb http://archive.debian.org/debian-backports squeeze-backports main" >> /etc/apt/sources.list
RUN apt-get -o Acquire::Check-Valid-Until=false update
RUN apt-get install -y \
    python python-argparse python-pyparsing cmake libfuse-dev libglib2.0-dev texinfo gtk-doc-tools \
    flex bison python-dev libxcb-damage0-dev libxcb-shm0-dev libxcb-xfixes0-dev libxcb-xtest0-dev libxi-dev \
    libdbus-1-dev libxtst-dev libegl1-mesa-dev libudev-dev libtext-csv-perl libxrender-dev python-setuptools
RUN ln -s /usr/bin/python2.6 /usr/bin/python2

USER $user_name
RUN echo "arch = target_arch = Architecture.X86_64" >> $HOME/.cerbero/cerbero.cbc
RUN echo 'build = "x86_64-linux-gnu"' >> $HOME/.cerbero/cerbero.cbc
RUN git config --global user.name $user_name
RUN git config --global user.email $user_name@linux-portable
RUN git config --global credential.helper store
RUN chmod 755 $HOME/bin/*
CMD [ "/bin/bash", "-i" ]

