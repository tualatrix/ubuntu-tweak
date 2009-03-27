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

import pygtk
pygtk.require('2.0')
from xml.sax import make_parser
from xml.dom import minidom

class GnomeVersion:
    xmldoc = minidom.parse("/usr/share/gnome-about/gnome-version.xml")

    platform = xmldoc.getElementsByTagName("platform")[0].firstChild.data
    minor = xmldoc.getElementsByTagName("minor")[0].firstChild.data
    micro = xmldoc.getElementsByTagName("micro")[0].firstChild.data
    distributor = xmldoc.getElementsByTagName("distributor")[0].firstChild.data
    date = xmldoc.getElementsByTagName("date")[0].firstChild.data
    description = "GNOME %s.%s.%s (%s %s)" % (platform, minor, micro, distributor, date)

class parse_lsb:
    data = open('/etc/lsb-release').read()
    dict = {}
    for line in data.split('\n'):
        try:
            key, value = line.split('=')
            dict[key] = value
        except:
            pass

class DistroInfo:
    distro = GnomeVersion.distributor
    if parse_lsb.dict['DISTRIB_ID'] == "Ubuntu" or distro == "Ubuntu":
        distro = file('/etc/issue.net').readline()[:-1]

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
            version = str(worker.get_pkgversion('compizconfig-settings-manager'))
            print version
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
        return 'hardy' in cls.get_codename()

    @classmethod
    def is_intrepid(cls):
        return 'intrepid' in cls.get_codename()

    @classmethod
    def is_jaunty(cls):
        return 'jaunty' in cls.get_codename()

    @classmethod
    def get_codename(cls):
        try:
            return parse_lsb.dict['DISTRIB_CODENAME']
        except:
            return 'NULL'

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
    print 'is inprepid', module_check.is_intrepid()
    print 'is jaunty', module_check.is_jaunty()
