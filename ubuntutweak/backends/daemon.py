#!/usr/bin/python

# Copyright (C) 2007-2010 TualatriX <tualatrix@gmail.com>
#
# The class AptAuth is modified from softwareproperty. Author: Michael Vogt <mvo@debian.org>
# The original file is: softwareproperties/AptAuth.py
# GPL v2+
# Copyright (c) 2004 Canonical

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import apt
import apt_pkg
import dbus
import dbus.glib
import dbus.service
import dbus.mainloop.glib
import gobject
import gettext
import subprocess
import tempfile

from subprocess import PIPE
from aptsources.sourceslist import SourceEntry, SourcesList
from ubuntutweak.backends import PolicyKitService
from ubuntutweak.common.systeminfo import module_check

apt_pkg.init()

PPA_KEY = '''-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: SKS 1.0.10

mI0ESXTUHwEEAMtdNPmcgQcoPN3JcUcRrmdm1chJSmX6gj28OamOgE3Nxp3XgkDdg/vLFPv6
Tk8zIMxQnvuSpuG1YGp3x8atcKlQAlEHncAo27Vlio6pk8jG+qipDBKq7X7FyXE6X9Peg/k7
t7eXMLwH6ZJFN6IEmvPRTsiiQEd/dXRRuIRhPHirABEBAAG0G0xhdW5jaHBhZCBQUEEgZm9y
IFR1YWxhdHJpWIi2BBMBAgAgBQJJdNQfAhsDBgsJCAcDAgQVAggDBBYCAwECHgECF4AACgkQ
avDhlAYkoiC8mAQAmaxr4Kw/R2WZKde7MfbTPy7O9YoL/NQeThYGwxX6ICVr0IZUj9nxFQ/v
tmhZ59p53bpdR8jpPXjdDwjZIIlxTf72Fky6Ri3/zsC4YRD6idS4c4L50dTy74W6IabCt8GQ
LtJy5YASlEp5OGwRNptRSFxVE59LuOPRo2kvLIAa0Dc=
=3itC
-----END PGP PUBLIC KEY BLOCK-----'''

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
    cache = apt.Cache()
    PPA_URL = 'ppa.launchpad.net'
    stable_url = 'http://ppa.launchpad.net/tualatrix/ppa/ubuntu'
    ppa_list = []

    def __init__ (self, bus, mainloop):
        bus_name = dbus.service.BusName(INTERFACE, bus=bus)
        PolicyKitService.__init__(self, bus_name, PATH)
        self.mainloop = mainloop

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
                         in_signature='', out_signature='')
    def disable_ppa(self):
        self.list.refresh()
        self.ppa_list = []

        for source in self.list:
            if self.PPA_URL in source.uri and not source.disabled:
                self.ppa_list.append(source.uri)
                source.set_enabled(False)

        self.list.save()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def enable_ppa(self):
        self.list.refresh()

        for source in self.list:
            url = source.uri
            if self.PPA_URL in url and url in self.ppa_list:
                source.set_enabled(True)

        self.list.save()

    @dbus.service.method(INTERFACE,
                         in_signature='sv', out_signature='')
    def upgrade_sources(self, check_string, source_dict):
        self.list.refresh()

        for source in self.list:
            if source.uri in source_dict:
                source.dist = source_dict[source.uri]
                source.comment = source.comment.split(check_string)[0]
                source.set_enabled(True)

        self.list.save()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def enable_stable_source(self):
        self.list.refresh()

        for source in self.list:
            if self.stable_url in source.str() and source.type == 'deb' and not source.disabled:
                return

        self.set_separated_entry(self.stable_url, module_check.get_codename(),
                                 'main', 'Ubuntu Tweak Stable Source', True,
                                 'ubuntu-tweak-stable')
        self.add_apt_key_from_content(PPA_KEY)

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='b')
    def get_stable_source_enabled(self):
        self.list.refresh()

        for source in self.list:
            if self.stable_url in source.str() and source.type == 'deb' and not source.disabled:
                return True

        return False

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
                         in_signature='s', out_signature='b')
    def get_package_status(self, package):
        try:
            pkg = self.cache[package]
            return pkg.isInstalled
        except Exception, e:
            print e
        else:
            return False

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
                         in_signature='s', out_signature='s',
                         sender_keyword='sender')
    def exec_command(self, command, sender=None):
        self._check_permission(sender)
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s')
    def get_as_tempfile(self, path):
        f = tempfile.NamedTemporaryFile()
        new_path = f.name
        f.close()
        os.popen('cp %s %s' % (path, new_path))
        return new_path

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='s')
    def get_user_gconf(self, user, key):
        command = 'sudo -u %s gconftool-2 --get %s' % (user, key)
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='sssss', out_signature='s',
                         sender_keyword='sender')
    def set_user_gconf(self, user, key, value, type, list_type='', sender=None):
        self._check_permission(sender)
        command = 'sudo -u %s gconftool-2 --type %s' % (user, type)
        if list_type == '':
            command = '%s --set %s %s' % (command, key, value)
        else:
            command = '%s --type %s --list-type %s --set %s %s' % (command,
                                                                   list_type,
                                                                   key, value)
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s')
    def get_system_gconf(self, key):
        command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --get %s' % key
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='ssss', out_signature='s',
                         sender_keyword='sender')
    def set_system_gconf(self, key, value, type, list_type='', sender=None):
        self._check_permission(sender)
        if list_type == '':
            command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type %s --set %s %s' % (type, key, value)
        else:
            command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type %s --list-type %s --set %s %s' % (type, list_type, key, value)
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def exit(self):
        self.mainloop.quit()

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    mainloop = gobject.MainLoop()
    Daemon(dbus.SystemBus(), mainloop)
    mainloop.run()
