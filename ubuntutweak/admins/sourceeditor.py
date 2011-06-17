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
import glob
import thread
import socket
import gettext

from gi.repository import Gtk, Gdk, GObject, Pango

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui import GuiBuilder
from ubuntutweak.gui.dialogs import ErrorDialog, QuestionDialog
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.utils.package import AptWorker


SOURCES_LIST = '/etc/apt/sources.list'


class SourceView(Gtk.TextView):
    def __init__(self, path):
        super(SourceView, self).__init__()

        self.path = path
        self.create_tags()
        self.update_content()

        buffer = self.get_buffer()
        buffer.connect('end-user-action', self.on_buffer_changed)

    def on_buffer_changed(self, widget):
        self.update_from_buffer()

    def update_from_buffer(self):
        buffer = self.get_buffer()
        content = self.get_text()

        offset = buffer.get_iter_at_mark(buffer.get_insert()).get_offset()

        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
        iter = buffer.get_iter_at_offset(0)
        if content[-2:] == '\n\n':
            content = content[:-1]
        for i, line in enumerate(content.split('\n')):
            self.parse_and_insert(buffer, iter, line, i != content.count('\n'))

        iter = buffer.get_iter_at_offset(offset)
        buffer.place_cursor(iter)

    def update_content(self, content = None):
        buffer = self.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
        iter = buffer.get_iter_at_offset(0)
        if content is None:
            content = open(self.path).read()

        for i, line in enumerate(content.split('\n')):
            self.parse_and_insert(buffer, iter, line, i != content.count('\n'))

    def parse_and_insert(self, buffer, iter, line, break_line=False):
        try:
            if line.lstrip().startswith('#'):
                buffer.insert_with_tags_by_name(iter, line, 'full_comment')
                self.insert_line(buffer, iter)
            elif line.strip() == '':
                self.insert_line(buffer, iter)
            else:
                has_end_blank = line.endswith(' ')
                list = line.split()
                if list is None:
                    self.insert_line(buffer, iter)
                elif has_end_blank:
                    list[-1] = list[-1] + ' '
                if len(list) >= 4:
                    type, uri, distro, component = list[0], list[1], list[2], list[3:]

                    buffer.insert_with_tags_by_name(iter, type, 'type')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, uri, 'uri')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, distro, 'distro')
                    self.insert_blank(buffer, iter)
                    self.seprarte_component(buffer, component, iter)
                    if break_line:
                        self.insert_line(buffer, iter)
                elif len(list) == 3:
                    type, uri, distro = list[0], list[1], list[2]

                    buffer.insert_with_tags_by_name(iter, type, 'type')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, uri, 'uri')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, distro, 'distro')
                    if break_line:
                        self.insert_line(buffer, iter)
                else:
                    buffer.insert(iter, line)
        except:
            buffer.insert(iter, line)

    def create_tags(self):
        buffer = self.get_buffer()

        buffer.create_tag('full_comment', foreground="blue")
        buffer.create_tag('type', weight=Pango.Weight.BOLD)
        buffer.create_tag('uri', underline=Pango.Underline.SINGLE, foreground='blue')
        buffer.create_tag('distro', weight=Pango.Weight.BOLD)
        buffer.create_tag('component', foreground="red")
        buffer.create_tag('addon_comment', foreground="blue")

    def insert_blank(self, buffer, iter):
        buffer.insert(iter, ' ')

    def insert_line(self, buffer, iter):
        buffer.insert(iter, '\n')

    def seprarte_component(self, buffer, list, iter):
        component = []
        stop_i = -1
        has_comment = False
        for i, text in enumerate(list):
            stop_i = i
            if text[0] != '#':
                component.append(text)
            else:
                has_comment = True
                break

        buffer.insert_with_tags_by_name(iter, ' '.join(component), 'component')
        if has_comment:
            self.insert_blank(buffer, iter)
            buffer.insert_with_tags_by_name(iter, ' '.join(list[stop_i:]), 'addon_comment')

    def get_text(self):
        buffer = self.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path


class SourceEditor(TweakModule):
    __title__ = _('Source Editor')
    __desc__ = _('Manually edit your software sources to suit your needs.')
    __icon__ = 'system-software-update'
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self, 'sourceeditor.ui')

        self.textview = SourceView(SOURCES_LIST)
        self.textview.set_sensitive(False)
        self.sw1.add(self.textview)
        self.textview.get_buffer().connect('changed', self.on_buffer_changed)

        self.update_source_combo()

        un_lock = PolkitButton()
        un_lock.connect('authenticated', self.on_polkit_action)
        self.hbuttonbox2.pack_end(un_lock, False, False, 0)

        self.reparent(self.main_vbox)

    def update_source_combo(self):
        model = self.source_combo.get_model()
        iter = self.source_combo.get_active_iter()
        if iter:
            i = int(model.get_path(iter).to_string())
        else:
            i = 0
        model.clear()

        model.append(('/etc/apt/sources.list', 'sources.list'))

        SOURCE_LIST_D = '/etc/apt/sources.list.d'
        if not os.path.exists(SOURCE_LIST_D):
            self.source_combo.set_active(0)
            return
        files = glob.glob(SOURCE_LIST_D + '/*.list')
        files.sort()
        for file in files:
            if os.path.isdir(file):
                continue
            model.append((file, os.path.basename(file)))

        if i:
            iter = model.get_iter(i)
            self.source_combo.set_active_iter(iter)
        else:
            self.source_combo.set_active(0)

    def on_source_combo_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        if iter:
            self.textview.set_path(model.get_value(iter, 0))
            self.update_sourceslist()

    def on_update_button_clicked(self, widget):
        self.set_busy()
        daemon = AptWorker(widget.get_toplevel(), lambda t, s, d: self.unset_busy())
        daemon.update_cache()

    def update_sourceslist(self):
        self.textview.update_content()
        self.redo_button.set_sensitive(False)
        self.save_button.set_sensitive(False)

    def on_save_button_clicked(self, widget):
        text = self.textview.get_text().strip()
        if proxy.edit_source(self.textview.get_path(), text) == 'error':
            ErrorDialog(_('Please check the permission of the sources.list file'),
                    title=_('Save failed!')).launch()
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

    def on_redo_button_clicked(self, widget):
        dialog = QuestionDialog(_('The current content will be lost after reloading!\nDo you wish to continue?'))
        if dialog.run() == Gtk.ResponseType.YES:
            self.textview.update_content()
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

        dialog.destroy()

    def on_buffer_changed(self, buffer):
        if buffer.get_modified():
            self.save_button.set_sensitive(True)
            self.redo_button.set_sensitive(True)
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

    def on_delete_button_clicked(self, widget):
        if self.textview.get_path() ==  SOURCES_LIST:
            ErrorDialog(_('You can\'t delete sources.list!')).launch()
        else:
            dialog = QuestionDialog(_('The "%s" will be deleted!\nDo you wish to continue?') % self.textview.get_path())
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                model = self.source_combo.get_model()
                iter = self.source_combo.get_active_iter()
                i = model.get_path(iter).to_string()
                proxy.delete_source(model.get_value(iter, 0))
                model.remove(iter)

                iter = model.get_iter(int(i) - 1)
                self.source_combo.set_active_iter(iter)
                self.update_source_combo()

    def on_polkit_action(self, widget):
        self.textview.set_sensitive(True)
        self.delete_button.set_sensitive(True)
