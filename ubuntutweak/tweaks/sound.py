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
from gi.repository import Gtk, Gio

from ubuntutweak.utils import walk_directories
from ubuntutweak.gui.containers import ListPack, GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.configsettings import SystemConfigSetting

class Sound(TweakModule):
    __title__ = _('Sound')
    __desc__ = _('Set the sound theme for Ubuntu')
    __icon__ = 'sound'
    __category__ = 'appearance'

    utext_event_sounds = _('Event sounds:')
    utext_input_feedback = _('Input feedback sounds:')
    utext_sound_theme = _('Sound theme:')
    utext_login_sound = _('Play login sound:')

    def __init__(self):
        TweakModule.__init__(self)

        valid_themes = self._get_valid_themes()

        theme_box = GridPack(
                        WidgetFactory.create('Switch',
                            label=self.utext_event_sounds,
                            key='org.gnome.desktop.sound.event-sounds',
                            backend='gsettings'),
                        WidgetFactory.create('Switch',
                            label=self.utext_login_sound,
                            key='/usr/share/glib-2.0/schemas/50_unity-greeter.gschema.override::com.canonical.unity-greeter#play-ready-sound',
                            backend='systemconfig'),
                        WidgetFactory.create('Switch',
                            label=self.utext_input_feedback,
                            key='org.gnome.desktop.sound.input-feedback-sounds',
                            backend='gsettings'),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_sound_theme,
                            key='org.gnome.desktop.sound.theme-name',
                            backend='gsettings',
                            texts=valid_themes,
                            values=valid_themes),
                        )

        self.add_start(theme_box, False, False, 0)

    def _get_valid_themes(self):
        dirs = ( '/usr/share/sounds',
                 os.path.join(os.path.expanduser("~"), ".sounds"))
        valid = walk_directories(dirs, lambda d:
                    os.path.exists(os.path.join(d, "index.theme")))

        valid.sort()

        return valid
