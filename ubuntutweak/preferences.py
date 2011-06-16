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

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.settings import GSetting

class PreferencesDialog(GuiBuilder):
    (CLIP_CHECK,
     CLIP_ICON,
     CLIP_NAME) = range(3)

    def __init__(self, parent):
        GuiBuilder.__init__(self, file_name='preferences.ui')

        self.preferences_dialog.set_transient_for(parent)
        self.clips_settings = GSetting('com.ubuntu-tweak.tweak.clips')

    def on_clip_toggle_render_toggled(self, cell, path):
        iter = self.clip_model.get_iter(path)
        checked = not self.clip_model[iter][self.CLIP_CHECK]

        self.clip_model[iter][self.CLIP_CHECK] = checked

    def run(self):
        clips = self.clips_settings.get_value()

        loader = ModuleLoader('clips')

        self.clip_model.clear()

        if clips:
            for clip_name in clips:
                ClipClass = loader.get_module(clip_name)

                self.clip_model.append((True,
                                        ClipClass.get_pixbuf(),
                                        ClipClass.get_name()))

            for name, ClipClass in loader.module_table.items():
                if name not in clips:
                    self.clip_model.append((False,
                                            ClipClass.get_pixbuf(),
                                            ClipClass.get_name()))
        else:
            #By default, load 5 clips
            clip_list = []
            for i, (name, ClipClass) in enumerate(loader.module_table.items()):
                clip_list.append(name)
                self.clip_model.append((i < 5,
                                        ClipClass.get_pixbuf(),
                                        ClipClass.get_name()))

            self.clips_settings.set_value(clip_list[:5])

        return self.preferences_dialog.run()

    def hide(self):
        return self.preferences_dialog.hide()
