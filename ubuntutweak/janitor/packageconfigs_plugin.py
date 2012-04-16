import os
import time
import logging

from gi.repository import GObject, Gtk

from ubuntutweak.gui.gtk import set_busy, unset_busy
from ubuntutweak.janitor import JanitorPlugin, PackageObject
from ubuntutweak.utils import icon, filesizeformat
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
                              PackageConfigObject(pkg),
                              count)
            except:
                pass

        self.emit('scan_finished', True, count, 0)

    def clean_cruft(self, cruft_list=[], parent=None):
        for index, cruft in enumerate(cruft_list):
            log.debug('Cleaning...%s' % cruft.get_name())
            proxy.clean_configs(cruft.get_name())
            line, returncode = proxy.get_cmd_pipe()
            while returncode == 'None':
                log.debug('output: %s, returncode: %s' % (line, returncode))
                time.sleep(0.2)
                line, returncode = proxy.get_cmd_pipe()

            if returncode != '0':
                self.emit('clean_error', returncode)
                break
            else:
                self.emit('object_cleaned', cruft, index + 1)

        self.emit('all_cleaned', True)

    def get_summary(self, count):
        if count:
            return _('[%d] Packages Configs') % count
        else:
            return _('Packages Configs (No package config to be removed)')
