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
import shutil
import tempfile

from cerbero.config import Architecture
from cerbero.errors import EmptyPackageError
from cerbero.packages import PackagerBase
from cerbero.packages.disttarball import DistTarball
from cerbero.packages.package import MetaPackage
from cerbero.utils import shell, _
from cerbero.utils import messages as m


SPEC_TPL = '''
%%define _topdir %(topdir)s
%%define _name %(name)s
%%define _version %(version)s
%%define _package_name %%{_name}-%%{_version}


Name:           %%{_name}-gstsdk
Version:        %%{_version}
Release:        1
Summary:        %(summary)s
Source:         %(source)s
Group:          Applications/Internet
License:	%(license)s
URL:            %(url)s
Prefix:         %(prefix)s
%(requires)s

%%description
%(description)s

%%prep
%%setup -n %%{_package_name}

%%build

%%install
mkdir -p $RPM_BUILD_ROOT/%%{prefix}
cp -r $RPM_BUILD_DIR/%%{_package_name}/* $RPM_BUILD_ROOT/%%{prefix}

%%clean
rm -rf $RPM_BUILD_ROOT

%%files
%(files)s
'''

REQUIRE_TPL = 'Requires: %s-gstsdk\n'

class RPMPackage(PackagerBase):

    def __init__(self, config, package, store):
        PackagerBase.__init__(self, config, package, store)
        self.install_dir = '/opt/usr/local/gst-sdk' 
        self.full_package_name = '%s-%s' % (self.package.name, self.package.version)

    def pack(self, output_dir, devel=False, force=False,
             pack_deps=True, tmpdir=None):
        self._empty_packages = []
        # add the -devel suffix for devel packages
        self.devel = devel
        package_name = self.package.name
        full_package_name = self.full_package_name
        if devel:
            package_name += '-devel'
            full_package_name += '-devel'

        # Create a tmpdir for packages
        tmpdir, rpmdir, srcdir = self._create_rpm_tree(tmpdir)
        
        # only build each package once
        if pack_deps:
            self._pack_deps(tmpdir, force)

        # create a tarball with all the package's files
        tarball_packager = DistTarball(self.config, self.package, self.store)
        tarball = tarball_packager.pack(output_dir, devel, True, full_package_name) 

        m.action(_("Creating RPM package for %s") % package_name)
        # fill the spec file
        self._fill_spec(os.path.split(tarball)[1], tmpdir)
        spec_path = os.path.join(tmpdir, '%s.spec' % package_name)
        with open(spec_path, 'w') as f:
            f.write(self._spec_str)

        # move the tarball to SOURCES
        shutil.move(tarball, srcdir)

        # and build the package with rpmbuild
        self._build_rpm(spec_path)

        # copy the newly created package, which should be in RPMS/$ARCH
        # to the output dir
        for d in os.listdir(rpmdir):
            for f in os.listdir(os.path.join(rpmdir, d)):
                out_path = os.path.join(output_dir, f)
                if os.path.exists(out_path):
                    if force:
                        os.remove(out_path)
                    else:
                        raise FatalError(_("File %s already exists.\
                            Use --force to override it") % out_path)
                shutil.move(os.path.join(rpmdir, d, f), output_dir)
        return output_dir
  
    def _pack_deps(self, tmpdir, force):
        for p in self.store.get_package_deps(self.package.name):
            packager = RPMPackage(self.config, self.store.get_package(p),
                                  self.store)
            try:
                packager.pack(tmpdir, self.devel, force, False, tmpdir)
            except EmptyPackageError:
                self._empty_packages.append(p)
        
    def _build_rpm(self, spec_path):
        if self.config.target_arch == Architecture.X86:
            target = 'i686-redhat-linux'
        elif self.config.target_arch == Architecture.X86_64:
            arch = 'x86_64-redhat-linux'
        else:
            raise FatalError(_('Architecture %s not supported') % \
                             self.config.target_arch)
        shell.call('rpmbuild -bb --target %s %s' % (target, spec_path))

    def _create_rpm_tree(self, tmpdir):
        # create a tmp dir to use as topdir
        if tmpdir is None:
            tmpdir = tempfile.mkdtemp()
            for d in ['BUILD', 'SOURCES', 'RPMS', 'SRPMS', 'SPECS']:
                os.mkdir(os.path.join(tmpdir, d))
        return (tmpdir, os.path.join(tmpdir, 'RPMS'),
                os.path.join(tmpdir, 'SOURCES'))

    def _fill_spec(self, sources, topdir):
        requires = self._get_requires()
        files  = self.files_list(self.devel)
        self._spec_str = SPEC_TPL % {
                'name': self.package.name,
                'version': self.package.version,
                'summary': self.package.shortdesc,
                'description': self.package.longdesc,
                'license': ' '.join(self.package.licenses),
                'url': self.package.url,
                'requires': requires,
                'prefix': self.install_dir,
                'source': sources,
                'topdir': topdir,
                'files':  files}

    def _get_requires(self):
        deps = self.store.get_package_deps(self.package.name)
        deps = list(set(deps) - set(self._empty_packages))
        return reduce(lambda x, y: x + REQUIRE_TPL % y, deps, '')

    def files_list(self, devel):
        # metapackages only have dependencies in other packages
        if isinstance(self.package, MetaPackage):
            return []
        files = PackagerBase.files_list(self, devel)
        return '\n'.join([os.path.join('%{prefix}',  x) for x in files])


class Packager(object):

    def __new__(klass, config, package, store):
        return RPMPackage(config, package, store)


def register():
    from cerbero.packages.packager import register_packager
    from cerbero.config import Distro
    register_packager(Distro.REDHAT, Packager)
