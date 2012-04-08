# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2012 Tualatrix Chou <tualatrix@gmail.com>
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
import glob
import shutil
import logging

from ubuntutweak.janitor import JanitorPlugin, CruftObject
from ubuntutweak.utils import icon, filesizeformat

log = logging.getLogger('chromecache_plugin')

class ChromeObject(CruftObject):
    def __init__(self, name, path, size):
        self.name = name
        self.path = path
        self.size = size

    def get_path(self):
        return self.path

    def get_name(self):
        return '%s' % self.name

    def get_icon(self):
        return icon.get_from_name('google-chrome')

    def get_size_display(self):
        return filesizeformat(self.size)


class ChromeCachePlugin(JanitorPlugin):
    __title__ = _('Chrome Cache')
    __category__ = 'application'

    root_path = os.path.expanduser('~/.cache/google-chrome/Default')

    def __str__(self):
        return 'ChromeCachePlugin'

    def get_cruft(self):
        try:
            count = 0
            total_size = 0
            for root, dirs, files in os.walk(self.root_path):
                if root == self.root_path and dirs:
                    for dir in dirs:
                        dir_path = os.path.join(self.root_path, dir)

                        try:
                            size = os.popen('du -bs "%s"' % dir_path).read().split()[0]
                        except:
                            size = 0
                        count += 1
                        total_size += int(size)

                        self.emit('find_object',
                                  ChromeObject(dir, dir_path, size))
                    else:
                        continue

            self.emit('scan_finished', True, count, total_size)
        except Exception, e:
            log.error(e)
            self.emit('scan_error', e)

    def on_done(self, widget):
        widget.destroy()

    def clean_cruft(self, cruft_list=[], parent=None):
        for index, cruft in enumerate(cruft_list):
            log.debug('Cleaning...%s' % cruft.get_name())
            shutil.rmtree(cruft.get_path())
            self.emit('object_cleaned', cruft)

        self.emit('all_cleaned', True)

    def get_summary(self, count, size):
        if count:
            return _('Chrome Cache (%d cache to be cleaned, total size: %s)') % (count, filesizeformat(size))
        else:
            return _('Chrome Cache (No cache to be cleaned)')
