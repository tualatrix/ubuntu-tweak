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
    # TODO: need support Mint and other distro based on Ubuntu.
    if GnomeVersion.distributor == 'Ubuntu':
        data = open('/etc/lsb-release').read()
        dict = {}
        for line in data.split('\n'):
            try:
                key, value = line.split('=')
                dict[key] = value
            except:
                pass
        return dict['DISTRIB_CODENAME']
    return None

def parse_distro():
    # TODO: need support Mint and other distro based on Ubuntu.
    if GnomeVersion.distributor == 'Ubuntu':
        return file('/etc/issue.net').readline()[:-1]
    return GnomeVersion.distributor

class DistroInfo:
    distributor = GnomeVersion.distributor
    codename = parse_codename()
    distro = parse_distro()

class SystemInfo:
    gnome = GnomeVersion.description
    distro = DistroInfo.distro

class module_check:
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
        if cls.has_ccm():
            import ccm
            if ccm.Version >= '0.7.4':
                return True
            else:
                return False
        elif cls.has_apt():
            from package import worker, update_apt_cache
            update_apt_cache()
            version = str(worker.get_pkgversion('compiz'))
            if version.find(':') != -1 and version.split(':')[1] >= '0.7.4':
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def get_gnome_version(cls):
        return int(GnomeVersion.minor)

    @classmethod
    def is_ubuntu(cls):
        return cls.is_hardy() or cls.is_intrepid() or cls.is_jaunty()

    @classmethod
    def is_supported_ubuntu(cls):
        return cls.is_hardy() or cls.is_intrepid() or cls.is_jaunty()

    @classmethod
    def get_supported_ubuntu(cls):
        return ['hardy', 'intrepid', 'jaunty']

    @classmethod
    def is_hardy(cls):
        return 'hardy' == cls.get_codename()

    @classmethod
    def is_intrepid(cls):
        return 'intrepid' == cls.get_codename()

    @classmethod
    def is_jaunty(cls):
        return 'jaunty' == cls.get_codename()

    @classmethod
    def get_codename(cls):
        return DistroInfo.codename

    @classmethod
    def has_gio(cls):
        try:
            import gio
            return True
        except:
            return False
            
if __name__ == "__main__":
    print SystemInfo.distro
    print 'has pat', module_check.has_apt()
    print 'has ccm', module_check.has_ccm()
    print 'has right compiz', module_check.has_right_compiz()
    print 'gnome version', module_check.get_gnome_version()
    print 'is hardy', module_check.is_hardy()
    print 'is intrepid', module_check.is_intrepid()
    print 'is jaunty', module_check.is_jaunty()
