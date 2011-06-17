#packagi!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
import time
import thread
import tempfile
import subprocess
import logging

import apt_pkg
import gobject
from gi.repository import Gtk, Gdk
from xdg.DesktopEntry import DesktopEntry

from ubuntutweak.common.debug import run_traceback
from ubuntutweak.gui.dialogs import InfoDialog, ErrorDialog

log = logging.getLogger('PackageWorker')

raise DeprecationWarning("Don't use THIS")

def get_ppa_origin_name(url):
    section = url.split('/')
    # Due to the policy of ppa orgin naming, if an ppa is end with "ppa", so ignore it
    if section[4] == 'ppa':
        return 'LP-PPA-%s' % section[3]
    else:
        return 'LP-PPA-%s-%s' % (section[3], section[4])

class NoNeedDowngradeException(Exception):
    pass

class PackageWorker:

    def __init__(self):
        # E.G. 2.6.35-24
        self.current_kernel_version = '-'.join(os.uname()[2].split('-')[:2])
        log.debug("The current_kernel_version is: %s" % self.current_kernel_version)

        self.is_apt_broken = False
        self.apt_broken_message = ''
        self.cache = self.get_cache()

    def run_synaptic(self, id, lock, to_add=[], to_rm=[]):
        cmd = []
        if os.getuid() != 0:
            cmd = ['/usr/bin/gksu',
                   '--desktop', '/usr/share/applications/synaptic.desktop',
                   '--']
        cmd += ['/usr/sbin/synaptic',
                '--hide-main-window',
                '--non-interactive',
                '-o', 'Synaptic::closeZvt=true',
                '--parent-window-id', '%s' % (id) ]

        f = tempfile.NamedTemporaryFile()

        for item in to_add:
            f.write('%s\tinstall\n' % item)

        for item in to_rm:
            f.write('%s\tuninstall\n' % item)

        cmd.append('--set-selections-file')
        cmd.append('%s' % f.name)
        f.flush()

        log.debug("The cmd is: %s" % ' '.join(cmd))
        self.return_code = subprocess.call(cmd)
        log.debug("The return code is: %s" % self.return_code)
        lock.release()
        f.close()

    def get_local_pkg(self):
        #TODO More check
        list = []
        for pkg in self.get_cache():
            if pkg.candidateDownloadable == 0:
                list.append(pkg)
        return list

    def get_pkgsummary(self, pkg):
        return self.cache[pkg].summary

    def get_pkgversion(self, pkg):
        return pkg in self.cache and self.cache[pkg].installedVersion or None

    def perform_action(self, window_main, to_add=[], to_rm=[]):
        window_main.set_sensitive(False)
        window_main.window.set_cursor(Gdk.Cursor.new(Gdk.WATCH))
        lock = thread.allocate_lock()
        lock.acquire()
        t = thread.start_new_thread(self.run_synaptic, (window_main.window.xid, lock, to_add, to_rm))
        while lock.locked():
            while Gtk.events_pending():
                Gtk.main_iteration()
            time.sleep(0.05)
        window_main.set_sensitive(True)
        window_main.window.set_cursor(None)

        return self.return_code

    def get_install_status(self, to_add, to_rm):
        #TODO make deprecated
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

    def show_installed_status(self, to_add, to_rm):
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

        if done:
            InfoDialog(_('Update Successful!')).launch()
        else:
            ErrorDialog(_('Update Failed!')).launch()

    def get_cache(self):
        try:
            self.update_apt_cache()
        except Exception, e:
            self.is_apt_broken = True
            self.apt_broken_message = e
            log.error("Error happened when get_cache(): %s" % str(e))
            return None
        else:
            return self.cache

    def update_apt_cache(self, init=False):
        '''if init is true, force to update, or it will update only once'''
        if init or not hasattr(self, 'cache'):
            import apt
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

PACKAGE_WORKER = PackageWorker()

class AptCheckButton(Gtk.CheckButton):
    def __init__(self, label, pkgname, tooltip=None):
        gobject.GObject.__init__(self, label=label)

        self.pkgname = pkgname
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.set_active(self.get_state())

    def get_state(self):
        try:
            pkg = PACKAGE_WORKER.get_cache()[self.pkgname]
        except:
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
        self.pkg = PACKAGE_WORKER.get_cache()[name]
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

    def get_version(self):
        try:
            return self.pkg.versions[0].version
        except:
            return ''

if __name__ == '__main__':
    update_apt_cache()
    print worker.list_unneeded_kerenl()
