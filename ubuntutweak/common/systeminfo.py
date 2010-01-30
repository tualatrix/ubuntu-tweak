#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
from xml.sax import make_parser
from xml.dom import minidom

class GnomeVersion:
    _xmldoc = minidom.parse("/usr/share/gnome-about/gnome-version.xml")

    platform = _xmldoc.getElementsByTagName("platform")[0].firstChild.data
    minor = _xmldoc.getElementsByTagName("minor")[0].firstChild.data
    micro = _xmldoc.getElementsByTagName("micro")[0].firstChild.data
    distributor = _xmldoc.getElementsByTagName("distributor")[0].firstChild.data
    date = _xmldoc.getElementsByTagName("date")[0].firstChild.data
    description = "GNOME %s.%s.%s (%s %s)" % (platform, minor, micro, distributor, date)

def parse_codename():
    try:
        codename = os.popen('lsb_release -cs').read().strip()
        if codename in ['karmic', 'helena', 'Helena']:
            return 'karmic'
        elif codename in ['lucid']:
            return 'lucid'
    except:
        pass
    return ''

def parse_distro():
    return file('/etc/issue.net').readline()[:-1]

class DistroInfo:
    distributor = GnomeVersion.distributor
    if GnomeVersion.distributor in ['Ubuntu', 'Linux Mint', 'Greenie', 'Jolicloud']:
        codename = parse_codename()
        distro = parse_distro()
    else:
        codename = None
        distro = GnomeVersion.distributor

class SystemInfo:
    gnome = GnomeVersion.description
    distro = DistroInfo.distro

class module_check:
    codename = DistroInfo.codename
    distribution = DistroInfo.distro

    @classmethod
    def has_apt(cls):
        try:
            import apt_pkg
            return True
        except ImportError:
            return False

    @classmethod
    def has_ccm(cls):
        try:
            import ccm
            return True
        except ImportError:
            return False

    @classmethod
    def has_right_compiz(cls):
        try:
            if cls.has_ccm():
                import ccm
                if ccm.Version >= '0.7.4':
                    return True
                else:
                    return False
            elif cls.has_apt():
                return True
            else:
                return False
        except:
            return False

    @classmethod
    def get_gnome_version(cls):
        return int(GnomeVersion.minor)

    @classmethod
    def is_supported_ubuntu(cls):
        return cls.codename in ['karmic', 'lucid']

    @classmethod
    def get_supported_ubuntu(cls):
        return ['karmic', 'lucid']

    @classmethod
    def get_codename(cls):
        return cls.codename

    @classmethod
    def is_ubuntu(cls, distro):
        if type(distro) == list:
            for dis in distro:
                if dis in cls.get_supported_ubuntu():
                    return True
                return False
        else:
            if distro in cls.get_supported_ubuntu():
                return True
            return False

if __name__ == "__main__":
    print SystemInfo.distro
    print 'has pat', module_check.has_apt()
    print 'has ccm', module_check.has_ccm()
    print 'has right compiz', module_check.has_right_compiz()
    print 'gnome version', module_check.get_gnome_version()
