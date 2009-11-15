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

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import apt_pkg
import dbus
import dbus.glib
import dbus.service
import dbus.mainloop.glib
import gobject
import subprocess
import tempfile

from subprocess import PIPE
from aptsources.sourceslist import SourceEntry, SourcesList
from ubuntutweak.backends import PolicyKitService

apt_pkg.init()

#This class is modified from softwareproperty. Author: Michael Vogt <mvo@debian.org>
class AptAuth:
    def __init__(self):
        self.gpg = ["/usr/bin/gpg"]
        self.base_opt = self.gpg + ["--no-options", "--no-default-keyring",
                                    "--secret-keyring", "/etc/apt/secring.gpg",
                                    "--trustdb-name", "/etc/apt/trustdb.gpg",
                                    "--keyring", "/etc/apt/trusted.gpg"]
        self.list_opt = self.base_opt + ["--with-colons", "--batch",
                                         "--list-keys"]
        self.rm_opt = self.base_opt + ["--quiet", "--batch",
                                       "--delete-key", "--yes"]
        self.add_opt = self.base_opt + ["--quiet", "--batch",
                                        "--import"]
        
       
    def list(self):
        res = []
        #print self.list_opt
        p = subprocess.Popen(self.list_opt,stdout=PIPE).stdout
        for line in p.readlines():
            fields = line.split(":")
            if fields[0] == "pub":
                name = fields[9]
                res.append("%s %s\n%s" %((fields[4])[-8:],fields[5], _(name)))
        return res

    def add(self, filename):
        #print "request to add " + filename
        cmd = self.add_opt[:]
        cmd.append(filename)
        p = subprocess.Popen(cmd)
        return (p.wait() == 0)
        
    def update(self):
        cmd = ["/usr/bin/apt-key", "update"]
        p = subprocess.Popen(cmd)
        return (p.wait() == 0)

    def rm(self, key):
        #print "request to remove " + key
        cmd = self.rm_opt[:]
        cmd.append(key)
        p = subprocess.Popen(cmd)
        return (p.wait() == 0)

INTERFACE = "com.ubuntu_tweak.daemon"
PATH = "/com/ubuntu_tweak/daemon"

class Daemon(PolicyKitService):
    #TODO use signal
    liststate = None
    list = SourcesList()

    def __init__ (self, bus):
        bus_name = dbus.service.BusName(INTERFACE, bus=bus)
        PolicyKitService.__init__(self, bus_name, PATH)

    @dbus.service.method(INTERFACE,
                         in_signature='ssssb', out_signature='s',
                         sender_keyword='sender')
    def set_entry(self, url, distro, comps, comment, enabled, sender=None):
        self._check_permission(sender)
        self.list.refresh()

        if enabled:
            self.list.add('deb', url, distro, comps.split(' '), comment)
            self.list.save()
            return 'enabled'
        else:
            for entry in self.list:
                if url in entry.str():
                    entry.disabled = True

            self.list.save()
            return 'disabled'

    @dbus.service.method(INTERFACE,
                         in_signature='ssssbs', out_signature='s',
                         sender_keyword='sender')
    def set_separated_entry(self, url, distro,
                            comps, comment, enabled, file,
                            sender=None):
        self._check_permission(sender)
        self.list.refresh()

        partsdir = apt_pkg.Config.FindDir("Dir::Etc::sourceparts")
        if not os.path.exists(partsdir):
            os.mkdir(partsdir)
        file = os.path.join(partsdir, file+'.list')

        if enabled:
            self.list.add('deb', url, distro, comps.split(' '), comment, -1, file)
            self.list.save()
            return 'enabled'
        else:
            for entry in self.list:
                if url in entry.str():
                    entry.disabled = True

            self.list.save()
            return 'disabled'

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def replace_entry(self, old_url, new_url, sender=None):
        self._check_permission(sender)
        self.list.refresh()

        for entry in self.list:
            if old_url in entry.uri:
                entry.uri = entry.uri.replace(old_url, new_url)
            elif new_url in entry.uri and entry.disabled:
                self.list.remove(entry)

        self.list.save()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='s')
    def get_list_state(self):
        if self.liststate:
            return self.liststate
        else:
            return "normal"

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='s',
                         sender_keyword='sender')
    def clean_apt_cache(self, sender=None):
        self._check_permission(sender)
        os.system('apt-get clean')

        return 'done'
            
    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s',
                         sender_keyword='sender')
    def delete_file(self, path, sender=None):
        self._check_permission(sender)
        os.system('rm "%s"' % path)
        if os.path.exists(path):
            return 'error'
        else:
            return 'done'

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def link_file(self, src, dst, sender=None):
        self._check_permission(sender)
        if not os.path.exists(dst):
            os.symlink(src, dst)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def unlink_file(self, path, sender=None):
        self._check_permission(sender)
        if os.path.exists(path):
            os.unlink(path)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def set_list_state(self, state, sender=None):
        self._check_permission(sender)
        self.liststate = state

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def edit_file(self, path, content, sender=None):
        self._check_permission(sender)
        file = open(path, 'w')
        file.write(content)
        file.close()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s',
                         sender_keyword='sender')
    def clean_config(self, pkg, sender=None):
        self._check_permission(sender)
        return str(os.system('sudo dpkg --purge %s' % pkg))

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def add_apt_key(self, filename, sender=None):
        self._check_permission(sender)
        apt_key = AptAuth()
        apt_key.add(filename)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def add_apt_key_from_content(self, content, sender=None):
        #TODO leave only one method
        self._check_permission(sender)

        f = tempfile.NamedTemporaryFile()
        f.write(content)
        f.flush()

        apt_key = AptAuth()
        apt_key.add(f.name)
        f.close()

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def save_to_disk(self, text, filename, sender=None):
        self._check_permission(sender)
        f = file(filename, 'w')
        f.write(text)
        f.close()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_exists(self, path):
        return os.path.exists(path)

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='b',
                         sender_keyword='sender')
    def is_authorized(self, sender=None):
        self._check_permission(sender)
        return True

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def exit(self):
        mainloop.quit()

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    Daemon(dbus.SystemBus())

    mainloop = gobject.MainLoop()
    mainloop.run()
