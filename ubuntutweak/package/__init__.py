#packagi!/usr/bin/python

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

import re
import os
import sys
import gtk
import gettext
import time
import thread
import tempfile
import subprocess
import apt
import apt_pkg
from aptdaemon import client
from aptdaemon.enums import *
from aptdaemon.gtkwidgets import AptErrorDialog, AptProgressDialog, AptMessageDialog

from xdg.DesktopEntry import DesktopEntry

p_kernel = re.compile('\d')

#TODO make different backedns

class PackageWorker:
    basenames = ['linux-image', 'linux-headers', 'linux-image-debug',
                  'linux-ubuntu-modules', 'linux-header-lum',
                  'linux-backport-modules',
                  'linux-header-lbm', 'linux-restricted-modules']

    def __init__(self):
        self.uname = os.uname()[2]
        self.uname_no_generic = '-'.join(self.uname.split('-')[:2])
        self.ac = client.AptClient()

        self.cache = self.get_cache()

    def is_current_kernel(self, pkg):
        for base in self.basenames:
            if pkg == '%s-%s' % (base, self.uname) or pkg == '%s-%s' % (base, self.uname_no_generic):
                return True
        return False

    def _show_messages(self, trans):
        while gtk.events_pending():
            gtk.main_iteration()
        for msg in trans._messages:
            d = AptMessageDialog(msg.enum, msg.details, parent=self.window_main)
            d.run()
            d.hide()

    def list_autoremovable(self):
        list = []
        for pkg in self.cache.keys():
            p = self.cache[pkg]
            try:
                need_remove = getattr(p, 'isAutoRemovable')
            except:
                need_remove = p.isInstalled and p._depcache.IsGarbage(p._pkg)

            if need_remove:
                list.append(pkg)

        return list

    def get_local_pkg(self):
        #TODO More check
        list = []
        for pkg in self.get_cache():
            if pkg.candidateDownloadable == 0:
                list.append(pkg)
        return list

    def list_unneeded_kerenl(self):
        list = []
        for pkg in self.cache.keys():
            if self.cache[pkg].isInstalled:
                for base in self.basenames:
                    if pkg.startswith(base) and p_kernel.findall(pkg) and not self.is_current_kernel(pkg):
                        list.append(pkg)
        return list

    def get_pkgsummary(self, pkg):
        return self.cache[pkg].summary

    def get_pkgversion(self, pkg):
        return pkg in self.cache and self.cache[pkg].installedVersion or None

    def perform_action(self, window_main, to_add=None, to_rm=None):
        self.window_main = window_main
        window_main.set_sensitive(False)
        window_main.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        t = self.ac.commit_packages(list(to_add), [], list(to_rm), [], [], exit_handler=self._on_exit)
        dia = AptProgressDialog(t, parent=window_main)                
        dia.run()
        dia.hide()                     
        self._show_messages(t)  

        window_main.set_sensitive(True)
        window_main.window.set_cursor(None)

    def _on_exit(self, trans, exit):
        if exit == EXIT_FAILED:
            d = AptErrorDialog(trans.get_error(), parent=self.window_main)
            d.run()
            d.hide()

    def get_install_status(self, to_add, to_rm):
        done = True

        for pkg in to_add:
            if not PackageInfo(pkg).check_installed():
                done = False
                break

        for pkg in to_rm:
            try:
                if PackageInfo(pkg).check_installed():
                    done = False
                    break
            except:
                pass

        return done

    def get_cache(self):
        try:
            self.update_apt_cache()
        except:
            return None
        else:
            return self.cache

    def update_apt_cache(self, init=False):
        '''if init is true, force to update, or it will update only once'''
        if init or not hasattr(self, 'cache'):
            apt_pkg.init()
            self.cache = apt.Cache()

    def get_new_package(self):
        old = self.get_cache().keys()
        self.update_apt_cache(True)
        new = self.get_cache().keys()

        return set(new).difference(set(old))

    def get_update_package(self):
        for pkg in self.get_cache():
            if pkg.isUpgradable == 1:
                yield pkg.name

package_worker = PackageWorker()

class AptCheckButton(gtk.CheckButton):
    def __init__(self, label, pkgname, tooltip = None):
        gtk.CheckButton.__init__(self, label)

        self.pkgname = pkgname
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.set_active(self.get_state())

    def get_state(self):
        try:
            pkg = package_worker.get_cache()[self.pkgname]
        except KeyError:
            self.set_sensitive(False)
            label = self.get_property('label')
            label = label + _('(Not available)')
            self.set_property('label', label)
            return False

        return pkg.isInstalled

    def button_toggled(self, widget, data = None):
        pass

    def reset_active(self):
        self.set_active(self.get_state())

class PackageInfo:
    DESKTOP_DIR = '/usr/share/app-install/desktop/'

    def __init__(self, name):
        self.name = name
        self.pkg = package_worker.get_cache()[name]
        self.desktopentry = DesktopEntry(self.DESKTOP_DIR + name + '.desktop')

    def check_installed(self):
        return self.pkg.isInstalled

    def get_comment(self):
        return self.desktopentry.getComment()

    def get_name(self):
        appname = self.desktopentry.getName()
        if appname == '':
            return self.name.title()

        return appname

if __name__ == '__main__':
    update_apt_cache()
    print worker.list_unneeded_kerenl()
