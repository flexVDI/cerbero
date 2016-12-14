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
RUN mkdir $HOME
ADD bashrc $HOME/.bashrc
ADD cerbero.cbc $HOME/.cerbero/cerbero.cbc
RUN sed -i 's;/home/user;'${HOME}';' $HOME/.cerbero/cerbero.cbc
RUN chown -R $user_name:$user_group $HOME

# Cerbero dependencies
RUN apt-get install -y \
    python python-argparse python-pyparsing cmake libfuse-dev libglib2.0-dev texinfo gtk-doc-tools \
    flex bison python-dev libxcb-damage0-dev libxcb-shm0-dev libxcb-xfixes0-dev libxcb-xtest0-dev libxi-dev
RUN ln -s /usr/bin/python2.6 /usr/bin/python2

USER $user_name
RUN cd $HOME && git clone https://github.com/flexVDI/cerbero.git
RUN mkdir -p $HOME/bin && cd $HOME/bin && ln -s $HOME/cerbero/cerbero-uninstalled cerbero
RUN echo "target_arch = Architecture.X86_64" >> $HOME/.cerbero/cerbero.cbc
RUN git config --global user.name $user_name
RUN git config --global credential.helper store
RUN wget https://github.com/probonopd/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    -O $HOME/bin/appimagetool && chmod 755 $HOME/bin/appimagetool
CMD [ "/bin/bash", "-i" ]

