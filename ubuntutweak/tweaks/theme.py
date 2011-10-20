# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
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
from gi.repository import Gtk, Gio

from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class Theme(TweakModule):
    __title__ = _('Theme')
    __desc__ = _('Set the gtk theme, icon theme, cursor theme and others')
    __icon__ = 'preferences-desktop-theme'
    __category__ = 'appearance'

    """Lock down some function"""
    def __init__(self):
        TweakModule.__init__(self)

        valid_themes = self._get_valid_themes()
        valid_icon_themes = self._get_valid_icon_themes()
        valid_cursor_themes = self._get_valid_cursor_themes()
        valid_window_themes = self._get_valid_window_themes()

        self.theme_box = TablePack(_('Desktop theme'), (
                            WidgetFactory.create('ComboBox',
                                                 label='Gtk theme',
                                                 key='org.gnome.desktop.interface.gtk-theme',
                                                 backend='gsettings',
                                                 texts=valid_themes,
                                                 values=valid_themes,
                                                 ),
                            WidgetFactory.create('ComboBox',
                                                 label='Icon theme',
                                                 key='org.gnome.desktop.interface.icon-theme',
                                                 backend='gsettings',
                                                 texts=valid_icon_themes,
                                                 values=valid_icon_themes,
                                                 ),
                            WidgetFactory.create('ComboBox',
                                                 label='Cursor theme',
                                                 key='org.gnome.desktop.interface.cursor-theme',
                                                 backend='gsettings',
                                                 texts=valid_cursor_themes,
                                                 values=valid_cursor_themes,
                                                 ),
                            WidgetFactory.create('ComboBox',
                                                 label='Window theme',
                                                 key='/apps/metacity/general/theme',
                                                 backend='gconf',
                                                 texts=valid_window_themes,
                                                 values=valid_window_themes,
                                                 ),
                            ))
        self.add_start(self.theme_box, False, False, 0)

    def walk_directories(self, dirs, filter_func):
        # This function is taken from gnome-tweak-tool
        valid = []
        try:
            for thdir in dirs:
                if os.path.isdir(thdir):
                    for t in os.listdir(thdir):
                        if filter_func(os.path.join(thdir, t)):
                             valid.append(t)
        except:
            log.critical("Error parsing directories", exc_info=True)
        return valid

    def _get_valid_icon_themes(self):
        # This function is taken from gnome-tweak-tool
        dirs = ( '/usr/share/icons',
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = self.walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        not os.path.exists(os.path.join(d, "cursors")))
        return valid

    def _get_valid_themes(self):
        # This function is taken from gnome-tweak-tool
        """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
        dirs = ( '/usr/share/themes',
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = self.walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "gtk-2.0")) and \
                        os.path.exists(os.path.join(d, "gtk-3.0")))
        return valid

    def _get_valid_cursor_themes(self):
        dirs = ( '/usr/share/icons',
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = self.walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        os.path.exists(os.path.join(d, "cursors")))
        return valid

    def _get_valid_window_themes(self):
        dirs = ( '/usr/share/themes',
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = self.walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "metacity-1")))
        return valid
