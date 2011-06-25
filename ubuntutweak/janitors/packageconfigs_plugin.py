import os
import logging

import gobject
from gi.repository import Gtk

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitors import JanitorPlugin, PackageObject
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.utils import icon, filesizeformat
from ubuntutweak.gui.dialogs import TerminalDialog
from ubuntutweak.policykit.dbusproxy import proxy


log = logging.getLogger('PackageConfigsPlugin')

class PackageConfigObject(PackageObject):
    def __init__(self, name):
        self.name = name

    def get_icon(self):
        return icon.get_from_name('text-plain')

    def get_size_display(self):
        return ''

    def get_size(self):
        return 0


class CleanConfigDialog(TerminalDialog):
    def __init__(self, parent, pkgs):
        super(CleanConfigDialog, self).__init__(parent=parent)
        #FIXME the window should not be delete
        self.pkgs = pkgs
        self.done = False

        self.set_dialog_lable(_('Cleaning Configuration Files'))

    def run(self):
        proxy.clean_configs(self.pkgs)
        gobject.timeout_add(100, self.on_timeout)
        return super(CleanConfigDialog, self).run()

    def on_timeout(self):
        self.pulse()

        line, returncode = proxy.get_cmd_pipe()
        log.debug("Clean config result is: %s, returncode: %s" % (line, returncode))
        if line != '':
            line = line.rstrip()
            if line:
                self.set_progress_text(line)
                self.terminal.insert(line)
            else:
                self.terminal.insert('\n')

        if returncode != 'None':
            self.done = True
            if returncode != '0':
                self.emit('error', returncode)

        if not self.done:
            log.debug("Not done, return True")
            return True
        else:
            self.destroy()


class PackageConfigsPlugin(JanitorPlugin):
    __title__ = _('Package Configs')
    __category__ = 'system'

    def get_cruft(self):
        count = 0

        for line in os.popen('dpkg -l'):
            try:
                temp_list = line.split()
                status, pkg = temp_list[0], temp_list[1]
                if status == 'rc':
                    des = temp_list[3:]
                    count += 1
                    self.emit('find_object',
                              PackageConfigObject(pkg))
            except:
                pass

        self.emit('scan_finished', True, count, 0)

    def clean_cruft(self, parent, cruft_list):
        set_busy(parent)
        dialog = CleanConfigDialog(parent, [cruft.get_name() for cruft in cruft_list])
        dialog.run()
        dialog.destroy()
        self.emit('cleaned', True)
        unset_busy(parent)

    def get_summary(self, count, size):
        if count:
            return _('Packages Configs (%d package configs to be removed)') % count
        else:
            return _('Packages Configs (No package config to be removed)')
