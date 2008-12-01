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

class DistroInfo:
    distro = GnomeVersion.distributor
    if  distro == "Ubuntu":
        distro = file('/etc/issue').readline().split('\\n')[0]

class SystemInfo:
    gnome = GnomeVersion.description
    distro = DistroInfo.distro

class SystemModule:
    def has_apt(self):
        try:
            import apt_pkg
            return True
        except ImportError:
            return False

    def has_ccm(self):
        try:
            import ccm
            return True
        except ImportError:
            return False

    def has_right_compiz(self):
        if self.has_ccm():
            import ccm
            if ccm.Version >= '0.7.4':
                return True
            else:
                return False
        elif self.has_apt():
            from package import worker, update_apt_cache
            update_apt_cache()
            version = str(worker.get_pkgversion('compiz'))
            if version.find(':') != -1 and version.split(':')[1] >= '0.7.4':
                return True
            else:
                return False
        else:
            return False

    def get_gnome_version(self):
        return int(GnomeVersion.minor)

    def is_supported_ubuntu(self):
        return self.is_hardy() or self.is_intrepid()

    def is_hardy(self):
        return 'Mint' in SystemInfo.distro or '8.04' in SystemInfo.distro

    def is_intrepid(self):
        return 'Mint' in SystemInfo.distro or '8.10' in SystemInfo.distro \
                or 'intrepid' in SystemInfo.distro

    def get_codename(self):
        if self.is_hardy():
            return 'hardy'
        elif self.is_intrepid():
            return 'intrepid'
        else:
            return 'NULL'

    def has_gio(self):
        try:
            import gio
            return True
        except:
            return False

module_check = SystemModule()
            
if __name__ == "__main__":
    print 'has pat', module_check.has_apt()
    print 'has ccm', module_check.has_ccm()
    print 'has right compiz', module_check.has_right_compiz()
    print 'gnome version', module_check.get_gnome_version()
    print 'is hardy', module_check.is_hardy()
    print 'is inprepid', module_check.is_intrepid()
