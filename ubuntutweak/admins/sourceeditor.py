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
import re
import glob
import time
import thread
import socket
import gettext

from gi.repository import Gtk, Gdk, GObject, Pango

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui import GuiBuilder
from ubuntutweak.gui.dialogs import ErrorDialog, QuestionDialog
from ubuntutweak.policykit import PK_ACTION_SOURCE
from ubuntutweak.policykit.dbusproxy import proxy
from ubuntutweak.utils.package import AptWorker
from ubuntutweak.admins.desktoprecovery import GetTextDialog
from ubuntutweak.settings import GSetting


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
            try:
                content = open(self.path).read()

                for i, line in enumerate(content.split('\n')):
                    self.parse_and_insert(buffer, iter, line, i != content.count('\n'))

            except:
                pass

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
    __policykit__ = PK_ACTION_SOURCE
    __category__ = 'system'
    _authenticated = False

    def __init__(self):
        TweakModule.__init__(self, 'sourceeditor.ui')

        self.auto_backup_setting = GSetting('com.ubuntu-tweak.tweak.auto-backup')

        self.textview = SourceView(SOURCES_LIST)
        self.textview.set_sensitive(False)
        self.sw1.add(self.textview)
        self.textview.get_buffer().connect('changed', self.on_buffer_changed)

        self.list_selection = self.list_view.get_selection()
        self.list_selection.connect("changed", self.on_selection_changed)

        self.infobar = Gtk.InfoBar()
        self.info_label = Gtk.Label(label='Current view the list')
        self.info_label.set_alignment(0, 0.5)
        self.infobar.get_content_area().add(self.info_label)
        self.infobar.connect("response", self.on_infobar_response)
        self.infobar.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.infobar.hide()
        self.text_vbox.pack_start(self.infobar, False, False, 0)

        self.connect('realize', self.on_ui_realize)
        self.add_start(self.hpaned1)

    def on_ui_realize(self, widget):
        self.infobar.hide()
        self.update_source_model()
        self.list_selection.select_iter(self.list_model.get_iter_first())
        self.auto_backup_button.set_active(self.auto_backup_setting.get_value())
        self.auto_backup_button.connect('toggled', self.on_auto_backup_button_toggled)

    def set_infobar_backup_info(self, name, list_name):
        self.info_label.set_markup(_('You\'re viewing the backup "<b>%(backup_name)s</b>" for '
                                     '"<b>%(list_name)s</b>"') % {'backup_name': name,
                                                                  'list_name': list_name})

    def on_auto_backup_button_toggled(self, widget):
        self.auto_backup_setting.set_value(widget.get_active())

    def on_infobar_response(self, widget, response_id):
        model, iter = self.list_selection.get_selected()

        if iter:
            list_path = model[iter][0]

            self.textview.set_path(list_path)
            self.textview.update_content()

            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

            self.infobar.hide()

    def on_selection_changed(self, selection):
        model, iter = selection.get_selected()

        if iter:
            self.textview.set_path(model[iter][0])
            self.update_sourceslist()
            self.update_backup_model()

    def update_source_model(self):
        model = self.list_model

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

    def update_backup_model(self):
        def file_cmp(f1, f2):
            return cmp(os.stat(f1).st_ctime, os.stat(f2).st_ctime)

        model, iter = self.list_selection.get_selected()

        if iter:
            source_list = model[iter][0]

            self.backup_model.clear()

            files = glob.glob(source_list + '.*')
            files.sort(cmp=file_cmp, reverse=True)

            for path in files:
                if os.path.isdir(path):
                    continue
                self.backup_model.append((path,
                    os.path.basename(path).split('.list.')[-1].split('.save')[0]))

            if not files:
                self.backup_model.append((None, _('No backup yet')))
                self.backup_edit_button.set_sensitive(False)
                self.backup_delete_button.set_sensitive(False)
                self.recover_button.set_sensitive(False)
                self.backup_view_button.set_sensitive(False)
                self.infobar.hide()
            elif self._authenticated == True:
                self.backup_edit_button.set_sensitive(True)
                self.backup_delete_button.set_sensitive(True)
                self.recover_button.set_sensitive(True)
                self.backup_view_button.set_sensitive(True)

            self.backup_combobox.set_active(0)

    def on_source_combo_changed(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()

        if self.has_backup_value(iter):
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

        if self.auto_backup_setting.get_value():
            proxy.backup_source(self.textview.get_path(), self.get_time_stamp())
            self.update_backup_model()

        if proxy.edit_source(self.textview.get_path(), text) == 'error':
            ErrorDialog(message=_('Please check the permission of the '
                                  'sources.list file'),
                        title=_('Save failed!')).launch()
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

    def on_recover_button_clicked(self, widget):
        model, iter = self.list_selection.get_selected()

        if iter:
            list_path = model[iter][0]
            list_name = model[iter][1]

            backup_iter = self.backup_combobox.get_active_iter()

            if backup_iter:
                backup_path = self.backup_model[backup_iter][0]
                backup_name = self.backup_model[backup_iter][1]

                dialog = QuestionDialog(message=_('Would you like to recover the '
                                        'backup "<b>%(backup_name)s</b>" for "<b>%(list_name)s</b>"?') % \
                                                {'backup_name': backup_name,
                                                 'list_name': list_name})
                response = dialog.run()
                dialog.destroy()

                if response == Gtk.ResponseType.YES:
                    if proxy.restore_source(backup_path, list_path):
                        self.infobar.response(Gtk.ResponseType.CLOSE)
                    else:
                        ErrorDialog(title=_('Recovery Failed!'),
                                   message=_('You may need to check the permission '
                                             'of source list.')).launch()

    def on_backup_view_button_clicked(self, widget=None):
        model, iter = self.list_selection.get_selected()

        if iter:
            list_name = model[iter][1]

            iter = self.backup_combobox.get_active_iter()

            if self.has_backup_value(iter):
                name = self.backup_model[iter][1]
                self.set_infobar_backup_info(name, list_name)

                self.textview.set_path(self.backup_model[iter][0])
                self.textview.update_content()
                self.save_button.set_sensitive(False)
                self.redo_button.set_sensitive(False)

                self.infobar.show()

    def on_backup_combobox_changed(self, widget):
        if self.infobar.get_visible():
            self.on_backup_view_button_clicked()

    def on_backup_button_clicked(self, widget):
        model, iter = self.list_selection.get_selected()

        if iter:
            path = model[iter][0]

            dialog = GetTextDialog(message=_('Please enter the name for your backup:'),
                                   text=self.get_time_stamp())
            response = dialog.run()
            dialog.destroy()
            backup_name = dialog.get_text()

            if response == Gtk.ResponseType.YES and backup_name:
                if self.is_valid_backup_name(backup_name):
                    if proxy.backup_source(path, backup_name):
                        self.update_backup_model()
                    else:
                        ErrorDialog(message=_('Backup Failed!')).launch()
                else:
                    ErrorDialog(message=_('Please only use alphanumeric characters'
                                        ' and "_" and "-".'),
                                title=_('Backup name is invalid')).launch()

    def on_backup_delete_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        path = self.backup_model[iter][0]

        dialog = QuestionDialog(message=_('Would you like to delete the backup '
                                          '"<b>%s</b>"?') % os.path.basename(path))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            proxy.delete_source(path)
            self.update_backup_model()

    def on_backup_edit_button_clicked(self, widget):
        iter = self.backup_combobox.get_active_iter()
        path = self.backup_model[iter][0]
        name = self.backup_model[iter][1]

        dialog = GetTextDialog(message=_('Please enter a new name for your backup:'),
                               text=name)
        response = dialog.run()
        dialog.destroy()
        new_name = dialog.get_text()

        if response == Gtk.ResponseType.YES and new_name and name != new_name:
            if self.is_valid_backup_name(new_name):
                proxy.rename_backup(path, name, new_name)
                self.update_backup_model()
            else:
                ErrorDialog(message=_('Please only use alphanumeric characters'
                                    ' and "_" and "-".'),
                            title=_('Backup name is invalid')).launch()

    def on_redo_button_clicked(self, widget):
        dialog = QuestionDialog(message=_('The current content will be lost after reloading!\nDo you wish to continue?'))
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
            dialog = QuestionDialog(message=_('The "%s" will be deleted!\nDo you wish to continue?') % self.textview.get_path())
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                model, iter = self.list_selection.get_selected()

                if iter:
                    list_path = model[iter][0]
                    proxy.delete_source(list_path)
                    self.update_source_model()
                    self.update_backup_model()

    def on_polkit_action(self, widget):
        self._authenticated = True
        self.textview.set_sensitive(True)
        self.delete_button.set_sensitive(True)
        self.recover_button.set_sensitive(True)
        self.backup_button.set_sensitive(True)
        self.backup_edit_button.set_sensitive(True)
        self.backup_delete_button.set_sensitive(True)
        self.backup_view_button.set_sensitive(True)

    def is_valid_backup_name(self, name):
        pattern = re.compile('[\w\-]+')

        match = pattern.search(name)

        return match and name == match.group()

    def has_backup_value(self, iter):
        return iter and self.backup_model[iter][0]

    def get_time_stamp(self):
        return time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
