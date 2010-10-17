#!/usr/bin/env python
# -*- encoding=utf8 -*-
#
# Copyright © 2010 Hsin Yi Chen
#
# Lazyscripts is a free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this software; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
import commands
import platform


class DistrobutionNotFound(Exception):
    "The distrobution can not be detected."

class Distribution(object):

    """
    Hyper Layer Distribution Informateions
    """

    #{{{def __str__(self):
    def __str__(self):
        return "%s %s (%s)" % (self.name,self.version,self.codename)
    #}}}

    #{{{def __repr__(self):
    def __repr__(self):
        return self.__str__()
    #}}}

    #{{{def __init__(self):
    def __init__(self):
        # linux_distribution is insted of dist
        # Ref: http://docs.python.org/library/platform.html
        self.system = platform.system()
        if self.system == 'Linux':
            if platform.python_version() < '2.6.0':
                (self.name, self.version, self.codename) = platform.dist()
            else:
                (self.name, self.version, self.codename) = platform.linux_distribution()

        # Because built-in funciton may not recognize all distrobution.
            self._reduce_name()
            self._reduce_version()
            self.codename = self.codename.lower()
            self._reduce_ut_codename()
            self._get_is_supported()
        elif self.system == 'Darwin':
            self.name = 'macosx'
            self.version = platform.mac_ver()[0]
    #}}}

    #{{{def _reduce_name(self):
    def _reduce_name(self):
        self.name = self.name.lower().strip()
        if not self.name:
            if os.path.exists('/etc/arch-release'):
                self.name = 'arch'
            elif os.path.exists('/usr/bin/pkg') and commands.getoutput('cat /etc/release | grep "OpenSolaris"'):
                self.name = 'opensolaris'
            elif os.path.exists('/etc/redflag-release'):
                if commands.getoutput('cat /etc/redflag-release | grep "RedFlag"'):
                    self.name = 'redflag'
                elif commands.getoutput('cat /etc/redflag-release | grep "Qomo"'):
                    self.name = 'qomo'
            elif os.path.exists('/etc/slackware-version'):
                self.name = 'slackware'
            elif os.path.exists('/etc/linpus-release'):
                self.name = 'linpus'
            elif os.path.exists('/etc/magic-release'):
                self.name = 'magiclinux'
            else:
                print "Lazyscripts not support your Linux distribution."
                self.name = None
                raise DistrobutionNotFound()
        elif self.name == 'susE':
            if commands.getoutput('cat /etc/SuSE-release | grep "openSUSE"'):
                self.name = 'opensuse'
        elif self.name == 'redhat':
            if commands.getoutput('cat /etc/redhat-release | grep "Red Hat"'):
                self.name = 'redhat'
            elif commands.getoutput('cat /etc/redhat-release | grep "CentOS"'):
                self.name = 'centos'
        elif self.name == 'mandrake':
            if os.path.exists('/etc/mandriva-release') and commands.getoutput('cat /etc/mandriva-release | grep "Mandriva"'):
                self.name = 'mandriva'
            elif os.path.exists('/etc/pclinuxos-release') and commands.getoutput('cat /etc/pclinuxos-release | grep "PCLinuxOS"'):
                self.name = 'pclinuxos'
        elif self.name == 'gentoo':
            if os.path.exists('/etc/sabayon-release'):
                self.name = 'sabayon'
    #}}}

    #{{{def _reduce_version(self):
    def _reduce_version(self):
        if self.name == 'opensolaris' and not self.version:
            self.version = commands.getoutput('cat /etc/release | grep "OpenSolaris" | cut -d " " -f 27')
        elif self.name == 'sabayon' :
            self.version = commands.getoutput('cat /etc/sabayon-edition | cut -d " " -f 3')
        elif self.name == 'redflag':
            self.version = commands.getoutput('cat /etc/redflag-release | cut -d " " -f 4')
        elif self.name == 'qomo':
            self.version = commands.getoutput('cat /etc/redflag-release | cut -d " " -f 2')
        elif self.name == 'linpus':
            self.version = commands.getoutput('cat /etc/linpus-release | cut -d " " -f 4')
        elif self.name == 'magiclinux':
            self.version = commands.getoutput('cat /etc/ark-release')
    #}}}

    def _reduce_ut_codename(self):
        # Ubuntu-Tweak use only ubuntu version to distinguish.
        if self.name == 'linuxmint':
            if self.codename == 'helena':
                self.ut_codename = 'karmic'
            elif self.codename == 'isadora':
                self.ut_codename = 'lucid'
        else:
            self.ut_codename = self.codename

    def _get_is_supported(self):
        if self.name == 'ubuntu':
            if self.codename in ['karmic', 'lucid', 'maverick']:
                self.is_supported = True
        elif self.name == 'linuxmint':
            if self.codename in ['helena', 'isadora']:
                self.is_supported = True
        else:
            self.is_supported = False

pass
