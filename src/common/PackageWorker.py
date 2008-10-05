#!/usr/bin/env python

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
import sys
import gtk
import gettext
import time
import thread
import tempfile
import subprocess
import apt
import apt_pkg
from xdg.DesktopEntry import DesktopEntry

def update_apt_cache(init = False):
    '''if init is true, force to update, or it will update only once'''
    global cache

    if init:
        try:
            cache
        except NameError:
            pass
        else:
            return

    apt_pkg.init()
    cache = apt.Cache(apt.progress.OpTextProgress())

class AptCheckButton(gtk.CheckButton):
    def __init__(self, label, pkgname, tooltip = None):
        gtk.CheckButton.__init__(self, label)

        self.pkgname = pkgname
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.set_active(self.get_state())

    def get_state(self):
        try:
            pkg = cache[self.pkgname]
        except KeyError:
            self.set_sensitive(False)
            label = self.get_property('label')
            label = label + _('(Not available)')
            self.set_property('label', label)
            return False

        return pkg.isInstalled

    def button_toggled(self, widget, data = None):
        pass

class PackageInfo:
    DESKTOP_DIR = '/usr/share/app-install/desktop/'

    def __init__(self, name):
        self.name = name
        self.pkg = cache[name]
        self.desktopentry = DesktopEntry(self.DESKTOP_DIR + name + ".desktop")

    def check_installed(self):
        return self.pkg.isInstalled

    def get_comment(self):
        return self.desktopentry.getComment()

    def get_name(self):
        appname = self.desktopentry.getName()
        if appname == "":
            return self.name.title()

        return appname

class PackageWorker:
    def run_synaptic(self, id, lock, to_add = None, to_rm = None):
        cmd = []
        if os.getuid() != 0:
            cmd = ["/usr/bin/gksu",
                   "--desktop", "/usr/share/applications/synaptic.desktop",
                   "--"]
        cmd += ["/usr/sbin/synaptic",
                "--hide-main-window",
                "--non-interactive",
                "-o", "Synaptic::closeZvt=true",
                "--parent-window-id", "%s" % (id) ]

        f = tempfile.NamedTemporaryFile()

        for item in to_add:
            f.write("%s\tinstall\n" % item)

        for item in to_rm:
            f.write("%s\tuninstall\n" % item)

        cmd.append("--set-selections-file")
        cmd.append("%s" % f.name)
        f.flush()

        self.return_code = subprocess.call(cmd)
        lock.release()
        f.close()

    def list_autoremovable(self):
        list = []
        for pkg in cache.keys():
            p = cache[pkg]
            try:
                need_remove = getattr(p, 'isAutoRemovable')
            except:
                need_remove = p.isInstalled and p._depcache.IsGarbage(p._pkg)

            if need_remove:
                list.append(pkg)

        return list

    def get_pkgsummary(self, pkg):
        return cache[pkg].summary

    def perform_action(self, window_main, to_add = None, to_rm = None):
        window_main.set_sensitive(False)
        window_main.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        lock = thread.allocate_lock()
        lock.acquire()
        t = thread.start_new_thread(self.run_synaptic, (window_main.window.xid, lock, to_add, to_rm))
        while lock.locked():
            while gtk.events_pending():
                gtk.main_iteration()
            time.sleep(0.05)
        window_main.set_sensitive(True)
        window_main.window.set_cursor(None)

        return self.return_code

if __name__ == '__main__':
    update_apt_cache()
    print PackageWorker().list_autoremovable()
