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


from cerbero.commands import Command, register_command
from cerbero.utils import _, N_, ArgparseArgument, shell


class Run(Command):
    doc = N_('Runs a command in the cerbero shell')
    name = 'run'

    def __init__(self):
        Command.__init__(self,
            [ArgparseArgument('cmd', nargs='+',
                             help=_('command to run')),
             ArgparseArgument('-v', '--verbose',
                             action='store_true',
                             default=False,
                             help=_('verbose mode'))
            ])

    def run(self, config, args):
        command = ' '.join(args.cmd)
        shell.call(command, '.', True, args.verbose)


register_command(Run)
