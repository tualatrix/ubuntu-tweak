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
import shutil
import logging
from gi.repository import Gtk, GLib

from ubuntutweak.gui import GuiBuilder
from ubuntutweak.modules import ModuleLoader
from ubuntutweak.settings import GSetting
from ubuntutweak.clips import Clip
from ubuntutweak.gui.dialogs import ErrorDialog, QuestionDialog
from ubuntutweak.utils.tar import TarFile
from ubuntutweak.common.consts import TEMP_ROOT


log = logging.getLogger('PreferencesDialog')


class PreferencesDialog(GuiBuilder):
    (CLIP_CHECK,
     CLIP_ICON,
     CLIP_NAME) = range(3)

    page_dict = {'overview': 0,
                 'tweaks': 1,
                 'admins': 2}

    def __init__(self, parent):
        GuiBuilder.__init__(self, file_name='preferences.ui')

        self.preferences_dialog.set_transient_for(parent)
        self.clips_settings = GSetting('com.ubuntu-tweak.tweak.clips')
        self.clips_location_settings = GSetting('com.ubuntu-tweak.tweak.last-clip-location')

    def on_clip_toggle_render_toggled(self, cell, path):
        iter = self.clip_model.get_iter(path)
        checked = not self.clip_model[iter][self.CLIP_CHECK]
        self.clip_model[iter][self.CLIP_CHECK] = checked

        self._do_update_clip_store()

    def _do_update_clip_store(self):
        clip_list = []
        for row in self.clip_model:
            if row[self.CLIP_CHECK]:
                clip_list.append(row[self.CLIP_NAME])

        log.debug("on_clip_toggle_render_toggled: %s" % clip_list)
        self.clips_settings.set_value(clip_list)

    def run(self, feature='overview'):
        self._update_clip_model()

        if feature in self.page_dict:
            self.preference_notebook.set_current_page(self.page_dict[feature])

        return self.preferences_dialog.run()

    def hide(self):
        return self.preferences_dialog.hide()

    def on_move_up_button_clicked(self, widget):
        model, iter = self.clip_view.get_selection().get_selected()

        if iter:
            previous_path = str(int(model.get_string_from_iter(iter)) - 1)

            if int(previous_path) >= 0:
                previous_iter = model.get_iter_from_string(previous_path)
                model.move_before(iter, previous_iter)
                self._do_update_clip_store()

    def on_move_down_button_clicked(self, widget):
        model, iter = self.clip_view.get_selection().get_selected()

        if iter:
            next_iter = model.iter_next(iter)
            model.move_after(iter, next_iter)
            self._do_update_clip_store()

    def on_clip_install_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Choose a clip extension'),
                                        action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_('Clip Extension (*.py, *.tar.gz)'))
        filter.add_pattern('*.py')
        filter.add_pattern('*.tar.gz')
        dialog.add_filter(filter)
        dialog.set_current_folder(self.clips_location_settings.get_value() or
                                  GLib.get_home_dir())

        filename = ''

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
        dialog.destroy()

        if filename:
            self.clips_location_settings.set_value(os.path.dirname(filename))

            log.debug("Start to check the class in %s" % filename)
            if filename.endswith('.tar.gz'):
                tar_file = TarFile(filename)
                if tar_file.is_valid():
                    tar_file.extract(TEMP_ROOT)
                    #TODO if multi-root
                    if tar_file.get_root_name():
                        temp_dir = os.path.join(TEMP_ROOT, tar_file.get_root_name())

                if ModuleLoader.is_target_class(temp_dir, Clip):
                    target = os.path.join(ModuleLoader.get_user_extension_dir('clips'), os.path.basename(temp_dir))
                    copy = True
                    if os.path.exists(target):
                        dialog = QuestionDialog(message=_("Would you like to remove it then install again?"),
                                                title=_('"%s" has already installed' % os.path.basename(target)))
                        response = dialog.run()
                        dialog.destroy()

                        if response == Gtk.ResponseType.YES:
                            shutil.rmtree(target)
                        else:
                            copy = False

                    if copy:
                        log.debug("Now copying tree...")
                        shutil.move(temp_dir, target)
                    else:
                        shutil.rmtree(temp_dir)
                elif ModuleLoader.is_target_class(filename):
                    shutil.copy(filename, ModuleLoader.get_user_extension_dir('clips'))
                self._update_clip_model()

                # To force empty the clips_settings to make load_cips
                value = self.clips_settings.get_value()
                self.clips_settings.set_value([''])
                self.clips_settings.set_value(value)
            else:
                ErrorDialog(message=_('"%s" is not a Clip Extension!' % os.path.basename(filename))).launch()

    def _update_clip_model(self):
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
