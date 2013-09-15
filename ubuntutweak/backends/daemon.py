#!/usr/bin/python

# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
#
# The class AptAuth is modified from softwareproperty. Author: Michael Vogt <mvo@debian.org>
# The original file is: softwareproperties/AptAuth.py
# GPL v2+
# Copyright (c) 2004 Canonical

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import glob
import fcntl
import shutil
import logging
import tempfile
import subprocess

from subprocess import PIPE

import apt
import apt_pkg
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GObject

from aptsources.sourceslist import SourcesList

from ubuntutweak import system
from ubuntutweak.utils import ppa
from ubuntutweak.backends import PolicyKitService
from ubuntutweak.policykit import PK_ACTION_TWEAK, PK_ACTION_CLEAN, PK_ACTION_SOURCE
from ubuntutweak.settings.configsettings import ConfigSetting

apt_pkg.init()

log = logging.getLogger('Daemon')

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
    cache = None
    stable_url = 'http://ppa.launchpad.net/tualatrix/ppa/ubuntu'
    ppa_list = []
    p = None
    SOURCES_LIST = '/etc/apt/sources.list'

    def __init__ (self, bus, mainloop):
        bus_name = dbus.service.BusName(INTERFACE, bus=bus)
        PolicyKitService.__init__(self, bus_name, PATH)
        self.mainloop = mainloop

    def get_cache(self):
        try:
            self.update_apt_cache()
        except Exception, e:
            log.error("Error happened when get_cache(): %s" % str(e))
        finally:
            return self.cache

    @dbus.service.method(INTERFACE,
                         in_signature='b', out_signature='b')
    def update_apt_cache(self, init=False):
        '''if init is true, force to update, or it will update only once'''
        if init or not getattr(self, 'cache'):
            apt_pkg.init()
            self.cache = apt.Cache()

    @dbus.service.method(INTERFACE,
                         in_signature='b', out_signature='bv')
    def check_sources_is_valid(self, convert_source):
        try:
            if not os.path.exists(self.SOURCES_LIST):
                os.system('touch %s' % self.SOURCES_LIST)
        except Exception, e:
            log.error(e)

        self.list.refresh()
        to_add_entry = []
        to_rm_entry = []
        disabled_list = ['']

        for entry in self.list:
            entry_line = entry.str().strip()
            if entry.invalid and not entry.disabled and entry_line and not entry_line.startswith('#'):
                try:
                    entry.set_enabled(False)
                except Exception, e:
                    log.error(e)
                if entry.file not in disabled_list:
                    disabled_list.append(entry.file)
                continue

            if convert_source:
                if os.path.basename(entry.file) == 'sources.list':
                    continue
                log.debug("Check for url: %s, type: %s, filename: %s" % (entry.uri, entry.type, entry.file))
                if ppa.is_ppa(entry.uri):
                    filename = '%s-%s.list' % (ppa.get_source_file_name(entry.uri), entry.dist)
                    if filename != os.path.basename(entry.file):
                        log.debug("[%s] %s need rename to %s" % (entry.type, entry.file, filename))
                        to_rm_entry.append(entry)
                        if os.path.exists(entry.file):
                            log.debug("%s is exists, so remove it" % entry.file)
                            os.remove(entry.file)
                        entry.file = os.path.join(os.path.dirname(entry.file), filename)
                        to_add_entry.append(entry)

        for entry in to_rm_entry:
            log.debug("To remove: ", entry.uri, entry.type, entry.file)
            self.list.remove(entry)


        valid = len(disabled_list) == 1
        if '' in disabled_list and not valid:
            disabled_list.remove('')

        self.list.list.extend(to_add_entry)
        self.list.save()

        return valid, disabled_list

    def _setup_non_block_io(self, io):
        outfd = io.fileno()
        file_flags = fcntl.fcntl(outfd, fcntl.F_GETFL)
        fcntl.fcntl(outfd, fcntl.F_SETFL, file_flags | os.O_NDELAY)

    @dbus.service.method(INTERFACE,
                         in_signature='sb', out_signature='b',
                         sender_keyword='sender')
    def set_source_enable(self, url, enable, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        self.list.refresh()

        for source in self.list:
            if url in source.str() and source.type == 'deb':
                source.disabled = not enable

        self.list.save()

        for source in self.list:
            if url in source.str() and source.type == 'deb':
                return not source.disabled

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='b',
                         sender_keyword='sender')
    def purge_source(self, url, key_fingerprint='', sender=None):
        #TODO enable
        self._check_permission(sender, PK_ACTION_SOURCE)
        self.list.refresh()
        to_remove = []

        self.set_source_enable(url, False)

        for source in self.list:
            if url in source.str() and source.type == 'deb':
                to_remove.extend(glob.glob(source.file + "*"))

        for file in to_remove:
            try:
                if file != self.SOURCES_LIST:
                    os.remove(file)
            except Exception, e:
                log.error(e)

        # Must refresh! Because the sources.list.d has been changed
        self.list.refresh()

        # Search for whether there's other source from the same owner, if exists,
        # don't remove the apt-key
        owner_url = "http://" + ppa.PPA_URL + "/" + url.split('/')[3]
        need_remove_key = True

        for source in self.list:
            if owner_url in source.str() and source.type == 'deb':
                need_remove_key = False
                break

        if key_fingerprint and need_remove_key:
            self.rm_apt_key(key_fingerprint)

        for source in self.list:
            if url in source.str() and source.type == 'deb':
                return True

        return False

    @dbus.service.method(INTERFACE,
                         in_signature='ssssb', out_signature='s',
                         sender_keyword='sender')
    def set_entry(self, url, distro, comps, comment, enabled, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
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
        self._check_permission(sender, PK_ACTION_SOURCE)
        self.list.refresh()

        partsdir = apt_pkg.config.find_dir("Dir::Etc::Sourceparts")
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
        self._check_permission(sender, PK_ACTION_SOURCE)
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
            if ppa.is_ppa(source.uri) and not source.disabled:
                self.ppa_list.append(source.uri)
                source.set_enabled(False)

        self.list.save()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def enable_ppa(self):
        self.list.refresh()

        for source in self.list:
            url = source.uri
            if ppa.is_ppa(url) and url in self.ppa_list:
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

        distro = system.CODENAME

        if distro:
            self.set_separated_entry(self.stable_url, distro, 'main',
                                     'Ubuntu Tweak Stable Source', True,
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
        self._check_permission(sender, PK_ACTION_CLEAN)
        os.system('apt-get clean')

        return 'done'

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_package_installed(self, package):
        try:
            pkg = self.get_cache()[package]
            return pkg.isInstalled
        except Exception, e:
            log.error(e)
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_package_upgradable(self, package):
        try:
            pkg = self.get_cache()[package]
            return pkg.isUpgradable
        except Exception, e:
            log.error(e)
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_package_avaiable(self, package):
        try:
            return self.get_cache().has_key(package)
        except Exception, e:
            log.error(e)
            return False
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def link_file(self, src, dst, sender=None):
        self._check_permission(sender, PK_ACTION_TWEAK)
        if not os.path.exists(dst):
            os.symlink(src, dst)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def unlink_file(self, path, sender=None):
        self._check_permission(sender, PK_ACTION_TWEAK)
        if os.path.exists(path) and os.path.islink(path):
            os.unlink(path)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def set_list_state(self, state, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        self.liststate = state

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='s',
                         sender_keyword='sender')
    def edit_source(self, path, content, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        if path.startswith(self.SOURCES_LIST):
            try:
                file = open(path, 'w')
                file.write(content)
                file.close()
            except Exception, e:
                log.error(e)
                return 'error'
            finally:
                return 'done'
        else:
            return 'error'

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s',
                         sender_keyword='sender')
    def delete_source(self, path, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        if path.startswith(self.SOURCES_LIST):
            os.system('rm "%s"' % path)
            if os.path.exists(path):
                return 'error'
            else:
                return 'done'
        else:
            return 'error'

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='b',
                         sender_keyword='sender')
    def backup_source(self, path, backup_name, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        if path.startswith(self.SOURCES_LIST):
            new_path = path + '.' + backup_name + '.save'
            shutil.copy(path, new_path)
            return os.path.exists(new_path)
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='b',
                         sender_keyword='sender')
    def restore_source(self, backup_path, restore_path, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)
        if restore_path.startswith(self.SOURCES_LIST) and \
                restore_path in backup_path:
            shutil.copy(backup_path, restore_path)
            return True
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='sss', out_signature='b',
                         sender_keyword='sender')
    def rename_backup(self, backup_path, name, new_name, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)

        if backup_path.startswith(self.SOURCES_LIST) and name and new_name:
            os.rename(backup_path, backup_path.replace(name, new_name))
            return True
        else:
            return False

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def clean_configs(self, pkg, sender=None):
        self._check_permission(sender, PK_ACTION_CLEAN)
        cmd = ['sudo', 'dpkg', '--purge']
        cmd.append(pkg)
        self.p = subprocess.Popen(cmd, stdout=PIPE)
        self._setup_non_block_io(self.p.stdout)

    @dbus.service.method(INTERFACE,
                         in_signature='as', out_signature='',
                         sender_keyword='sender')
    def install_select_pkgs(self, pkgs, sender=None):
        self._check_permission(sender, PK_ACTION_CLEAN)
        cmd = ['sudo', 'apt-get', '-y', '--force-yes', 'install']
        cmd.extend(pkgs)
        log.debug("The install command is %s" % ' '.join(cmd))
        self.p = subprocess.Popen(cmd, stdout=PIPE)
        self._setup_non_block_io(self.p.stdout)

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='v')
    def get_cmd_pipe(self):
        if self.p:
            terminaled = self.p.poll()
            if terminaled == None:
                try:
                    return self.p.stdout.readline(), str(terminaled)
                except:
                    return '', 'None'
            else:
                strings, returncode = ''.join(self.p.stdout.readlines()), str(terminaled)
                self.p = None
                return strings, returncode
        else:
            return '', 'None'

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def add_apt_key_from_content(self, content, sender=None):
        #TODO leave only one method
        self._check_permission(sender, PK_ACTION_SOURCE)

        f = tempfile.NamedTemporaryFile()
        f.write(content)
        f.flush()

        apt_key = AptAuth()
        apt_key.add(f.name)
        f.close()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def rm_apt_key(self, key_id, sender=None):
        self._check_permission(sender, PK_ACTION_SOURCE)

        apt_key = AptAuth()
        apt_key.rm(key_id)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b',
                         sender_keyword='sender')
    def delete_apt_cache_file(self, file_name, sender=None):
        self._check_permission(sender, PK_ACTION_CLEAN)

        full_path = os.path.join('/var/cache/apt/archives/', file_name)
        if os.path.exists(full_path):
            os.remove(full_path)

        return not os.path.exists(full_path)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_exists(self, path):
        return os.path.exists(path)

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='',
                         sender_keyword='sender')
    def set_login_logo(self, src, dest, sender=None):
        '''This is called by tweaks/loginsettings.py'''
        self._check_permission(sender, PK_ACTION_TWEAK)
        if not self.is_exists(os.path.dirname(dest)):
           os.makedirs(os.path.dirname(dest))
        self._delete_old_logofile(dest)
        shutil.copy(src, dest)

    def _delete_old_logofile(self, dest):
        for old in glob.glob(os.path.splitext(dest)[0] + ".*"):
            os.remove(old)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='',
                         sender_keyword='sender')
    def unset_login_logo(self, dest, sender=None):
        '''This is called by tweaks/loginsettings.py'''
        self._check_permission(sender, PK_ACTION_TWEAK)

        if dest.startswith(os.path.expanduser('~gdm/.icons')):
            self._delete_old_logofile(dest)

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='b')
    def is_link(self, path):
        return os.path.islink(path)

    @dbus.service.method(INTERFACE,
                         in_signature='si', out_signature='s')
    def get_as_tempfile(self, path, uid):
        f = tempfile.NamedTemporaryFile()
        new_path = f.name
        f.close()
        os.popen('cp %s %s' % (path, new_path))
        os.chown(new_path, uid, uid)
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
        self._check_permission(sender, PK_ACTION_TWEAK)
        command = 'sudo -u %s gconftool-2 --type %s' % (user, type)
        # Use "" to make sure the value with space will be set correctly
        if list_type == '':
            command = '%s --set %s "%s"' % (command, key, value)
        else:
            command = '%s --type %s --list-type %s --set %s "%s"' % (command,
                                                                   list_type,
                                                                   key, value)
        cmd = os.popen(command)
        return cmd.read().strip()

    @dbus.service.method(INTERFACE,
                         in_signature='s', out_signature='s')
    def get_system_gconf(self, key):
        command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --get %s' % key
        cmd = os.popen(command)
        output = cmd.read().strip()
        log.debug('get_system_gconf: %s is %s' % (key, output))
        return output

    @dbus.service.method(INTERFACE,
                         in_signature='ssss', out_signature='s',
                         sender_keyword='sender')
    def set_system_gconf(self, key, value, type, list_type='', sender=None):
        self._check_permission(sender, PK_ACTION_TWEAK)
        log.debug('set_system_gconf: %s to %s' % (key, value))
        if list_type == '':
            command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type %s --set %s %s' % (type, key, value)
        else:
            command = 'gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type %s --list-type %s --set %s %s' % (type, list_type, key, value)
        cmd = os.popen(command)
        output = cmd.read().strip()
        return output

    @dbus.service.method(INTERFACE,
                         in_signature='ss', out_signature='b',
                         sender_keyword='sender')
    def set_config_setting(self, key, value, sender=None):
        self._check_permission(sender, PK_ACTION_TWEAK)
        log.debug('set_config_setting: %s to %s' % (key, value))
        cs = ConfigSetting(key)
        cs.set_value(value)

        if cs.is_override_schema():
            os.system('glib-compile-schemas /usr/share/glib-2.0/schemas/')

        return value == cs.get_value()

    @dbus.service.method(INTERFACE,
                         in_signature='', out_signature='')
    def exit(self):
        self.mainloop.quit()

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    mainloop = GObject.MainLoop()
    Daemon(dbus.SystemBus(), mainloop)
    mainloop.run()
