# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
import tarfile

from cerbero.config import Architecture
from cerbero.packages import PackageType, PackagerBase
from cerbero.packages.disttarball import DistTarball
from cerbero.errors import UsageError


class AndroidPackager(DistTarball):
    ''' Creates a distribution tarball for Android '''

    def __init__(self, config, package, store):
        DistTarball.__init__(self, config, package, store)

    def files_list(self, package_type, force):
        if self.config.target_arch != Architecture.UNIVERSAL:
            # Nothing special to do for normal arches, just chain up
            return PackagerBase.files_list(self, package_type, force)
        else:
            # For the universal architecture, collect files from each
            # sub-archtecture
            if package_type == PackageType.DEVEL:
                files = self.package.devel_files_list()
            else:
                files = self.package.files_list()

            all_files = []

            if isinstance(self.config.universal_archs, list):
                archs = self.config.universal_archs
            elif isinstance(self.config.universal_archs, dict):
                archs = self.config.universal_archs.keys()
            else:
                raise ConfigurationError('universal_archs must be a list or a dict')

            for arch in archs:
                all_files += [os.path.join(str(arch), f) for f in files]

            return all_files

    def _create_tarball(self, output_dir, package_type, files, force,
                        package_prefix):
        filenames = []

        # Filter out some unwanted directories for the development package
        if package_type == PackageType.DEVEL:
            for filt in ['bin/', 'share/aclocal']:
                files = [x for x in files if not x.startswith(filt)]

        # Create the bz2 file first
        filename = os.path.join(output_dir, self._get_name(package_type))
        if os.path.exists(filename):
            if force:
                os.remove(filename)
            else:
                raise UsageError("File %s already exists" % filename)

        tar = tarfile.open(filename, "w:bz2")

        for f in files:
            filepath = os.path.join(self.prefix, f)
            tar.add(filepath, os.path.join(package_prefix, f))
        tar.close()
        filenames.append(filename)

        return  ' '.join(filenames)

    def _get_name(self, package_type, ext='tar.bz2'):
        if package_type == PackageType.DEVEL:
            package_type = ''
        elif package_type == PackageType.RUNTIME:
            package_type = '-runtime'

        return "%s%s-%s-%s-%s%s.%s" % (self.package_prefix, self.package.name,
                self.config.target_platform, self.config.target_arch,
                self.package.version, package_type, ext)


def register():
    from cerbero.packages.packager import register_packager
    from cerbero.config import Distro
    register_packager(Distro.ANDROID, AndroidPackager)
