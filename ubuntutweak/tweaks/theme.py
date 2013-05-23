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
import logging
from gi.repository import Gtk, Gio

from ubuntutweak import system
from ubuntutweak.gui.containers import ListPack, GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.utils import theme
from ubuntutweak.utils.tar import ThemeFile
from ubuntutweak.settings.configsettings import ConfigSetting
from ubuntutweak.gui.dialogs import QuestionDialog, ErrorDialog


log = logging.getLogger('theme')


class Theme(TweakModule):
    __title__ = _('Theme')
    __desc__ = _('Set the gtk theme, icon theme, cursor theme and others')
    __icon__ = 'preferences-desktop-theme'
    __category__ = 'appearance'

    utext_icon_theme = _('Icon theme:')
    utext_gtk_theme = _('Gtk theme:')
    utext_cursor_theme = _('Cursor theme:')
    utext_window_theme = _('Window theme:')

    def __init__(self):
        TweakModule.__init__(self)

        valid_themes = theme.get_valid_themes()
        valid_icon_themes = theme.get_valid_icon_themes()
        valid_cursor_themes = theme.get_valid_cursor_themes()
        valid_window_themes = theme.get_valid_window_themes()

        theme_choose_button = Gtk.FileChooserButton()
        theme_choose_button.connect('file-set', self.on_file_set)

        icon_label, self.icon_theme, icon_reset_button = WidgetFactory.create('ComboBox',
                            label=self.utext_icon_theme,
                            key='org.gnome.desktop.interface.icon-theme',
                            backend='gsettings',
                            texts=valid_icon_themes,
                            values=valid_icon_themes,
                            enable_reset=True)

        if system.CODENAME == 'precise':
            window_theme_label, window_theme_combox, window_theme_reset_button = WidgetFactory.create('ComboBox',
                            label=self.utext_window_theme,
                            key='/apps/metacity/general/theme',
                            backend='gconf',
                            texts=valid_window_themes,
                            values=valid_window_themes,
                            enable_reset=True)
        else:
            window_theme_label, window_theme_combox, window_theme_reset_button = WidgetFactory.create('ComboBox',
                            label=self.utext_window_theme,
                            key='org.gnome.desktop.wm.preferences.theme',
                            backend='gsettings',
                            texts=valid_window_themes,
                            values=valid_window_themes,
                            enable_reset=True)


        theme_box = GridPack(
                        WidgetFactory.create('ComboBox',
                            label=self.utext_gtk_theme,
                            key='org.gnome.desktop.interface.gtk-theme',
                            backend='gsettings',
                            texts=valid_themes,
                            values=valid_themes,
                            enable_reset=True),
                        (icon_label, self.icon_theme, icon_reset_button),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_cursor_theme,
                            key='org.gnome.desktop.interface.cursor-theme',
                            backend='gsettings',
                            texts=valid_cursor_themes,
                            values=valid_cursor_themes,
                            enable_reset=True),
                        (window_theme_label, window_theme_combox, window_theme_reset_button),
                        Gtk.Separator(),
                        (Gtk.Label(_('Install theme:')), theme_choose_button),
                        )

        self.add_start(theme_box, False, False, 0)

    def on_file_set(self, widget):
        try:
            tf = ThemeFile(widget.get_filename())
        except Exception, e:
            log.error(e)
            ErrorDialog(message=_('Theme file is invalid')).launch()
        else:
            if tf.install():
                log.debug("Theme installed! Now update the combox")
                valid_icon_themes = theme.get_valid_icon_themes()
                self.icon_theme.update_texts_values_pair(valid_icon_themes, valid_icon_themes)
                dialog = QuestionDialog(title=_('"%s" installed successfully' % tf.theme_name),
                               message=_('Would you like to set your icon theme to "%s" immediatelly?') % tf.theme_name)
                response = dialog.launch()
                if response == Gtk.ResponseType.YES:
                    self.icon_theme.get_setting().set_value(tf.install_name)

    def _get_valid_icon_themes(self):
        # This function is taken from gnome-tweak-tool
        dirs = ( '/usr/share/icons',
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        not os.path.exists(os.path.join(d, "cursors")))

        valid.sort()

        return valid

    def _get_valid_themes(self):
        # This function is taken from gnome-tweak-tool
        """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
        dirs = ( '/usr/share/themes',
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "gtk-2.0")) and \
                        os.path.exists(os.path.join(d, "gtk-3.0")))

        valid.sort()

        return valid

    def _get_valid_cursor_themes(self):
        dirs = ( '/usr/share/icons',
                 os.path.join(os.path.expanduser("~"), ".icons"))
        valid = walk_directories(dirs, lambda d:
                    os.path.isdir(d) and \
                        os.path.exists(os.path.join(d, "cursors")))

        valid.sort()

        return valid

    def _get_valid_window_themes(self):
        dirs = ( '/usr/share/themes',
                 os.path.join(os.path.expanduser("~"), ".themes"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "metacity-1")))

        valid.sort()

        return valid
