#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
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
import gtk
import thread
import socket
import gobject
import gettext

from ubuntutweak.modules  import TweakModule
from thirdsoft import refresh_source
from xmlrpclib import ServerProxy, Error
from ubuntutweak.common.utils import *
from ubuntutweak.common.gui import GuiWorker
from ubuntutweak.common.systeminfo import module_check
from ubuntutweak.policykit import PolkitButton, proxy
from ubuntutweak.common.utils import set_label_for_stock_button
from ubuntutweak.package import package_worker
from ubuntutweak.widgets.dialogs import *

(
    COLUMN_CHECK,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
) = range(5)

DEFAULT_SOURCE = '''deb http://archive.ubuntu.com/ubuntu/ %(distro)s main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ %(distro)s-security main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ %(distro)s-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ %(distro)s-proposed main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ %(distro)s-backports main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu/ %(distro)s main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu/ %(distro)s-security main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu/ %(distro)s-updates main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu/ %(distro)s-proposed main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu/ %(distro)s-backports main restricted universe multiverse''' % {'distro': module_check.get_codename()}

SOURCES_LIST = '/etc/apt/sources.list'

class SelectSourceDialog(gtk.Dialog):
    def __init__(self, parent):
        super(SelectSourceDialog, self).__init__(parent = parent)

        self.set_title(_('Choose the sources'))
        self.set_border_width(10)
        self.set_resizable(False)

        label = gtk.Label()
        label.set_markup('<b><big>%s</big></b>\n\n%s' % (_('Choose the sources'),
            _('You can read the title and comment to determine which source is suitable for you.')))
        label.set_alignment(0, 0)
        self.vbox.pack_start(label, False, False, 5)

        group = None
        self.detail = gtk.Label()

        for i, (k, v) in enumerate(SOURCES_DATA.items()):
            title, comment = k.split('\n')
            button = gtk.RadioButton(group = group, label = "%s: %s" % (title, comment))
            button.connect('toggled', self.on_button_toggled, v)
            if i == 0:
                group = button
                self.detail.set_text(v)
            self.vbox.pack_start(button, False, False, 5)

        self.expander = gtk.Expander(_('Details'))
        self.vbox.pack_start(self.expander)
        self.expander.add(self.detail)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_YES)

        self.show_all()

    def on_button_toggled(self, widget, value):
        self.detail.set_text(value)

    def get_source_data(self):
        return self.detail.get_text()

class SubmitDialog(gtk.Dialog):
    def __init__(self, parent):
        super(SubmitDialog, self).__init__(parent = parent)

        self.set_title(_('Submit your sources'))
        self.set_border_width(5)

        label = gtk.Label()
        label.set_markup('<big><b>%s</b></big>\n\n%s'  % 
            (_('Submit your sources'), _('You can submit your sources to the server '
            'for other people to use.')))
        self.vbox.pack_start(label, False, False, 5)

        l_title = gtk.Label()
        l_title.set_text_with_mnemonic(_('_Source Title:'))
        l_title.set_alignment(0, 0)
        l_locale = gtk.Label()
        l_locale.set_text_with_mnemonic(_('_Locale:'))
        l_locale.set_alignment(0, 0)
        l_comment = gtk.Label()
        l_comment.set_text_with_mnemonic(_('Comm_ent:'))
        l_comment.set_alignment(0, 0)

        self.e_title = gtk.Entry();
        self.e_title.set_tooltip_text(_('Enter the title of the source, e.g. "Ubuntu Official Repostory"'))
        self.e_locale = gtk.Entry ();
        self.e_locale.set_tooltip_text(_("If the locale isn't correct you can edit manually"))
        self.e_locale.set_text(os.getenv('LANG'))
        self.e_comment = gtk.Entry ();

        table = gtk.Table(3, 2)
        table.attach(l_title, 0, 1, 0, 1, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(l_locale, 0, 1, 1, 2, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(l_comment, 0, 1, 2, 3, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(self.e_title, 1, 2, 0, 1)
        table.attach(self.e_locale, 1, 2, 1, 2)
        table.attach(self.e_comment, 1, 2, 2, 3)

        self.vbox.pack_start(table, True, False, 5)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(_('Submit'), gtk.RESPONSE_YES)

        self.set_default_response(gtk.RESPONSE_YES)

        self.show_all()

    def get_source_data(self):
        return (self.e_title.get_text().strip(), 
                self.e_locale.get_text().strip(), 
                self.e_comment.get_text().strip(),
                open(SOURCES_LIST).read())

    def check_fill_data(self):
        return self.e_title.get_text().strip() \
                and self.e_locale.get_text().strip() \
                and self.e_comment.get_text().strip()

class ProcessDialog(gtk.Dialog):
    def __init__(self, data, parent):
        super(ProcessDialog, self).__init__(title = '', parent = parent)

        socket.setdefaulttimeout(10)

        self.count = 0
        self.error = None
#        self.server = ServerProxy("http://localhost:8080/xmlrpc")
        self.server = ServerProxy("http://ubuntu-tweak.appspot.com/xmlrpc")

        self.progressbar = gtk.ProgressBar()
        self.vbox.add(self.progressbar)

        self.show_all()
        gobject.timeout_add(100, self.on_timeout)
        thread.start_new_thread(self.process_data, (data,))
        
    def on_timeout(self):
        self.progressbar.pulse()
        self.count = self.count + 1

        if not self.processing or self.count == 100:
            self.destroy()
            if self.error or self.count == 100:
                self.show_error()
        else:
            return True

    def show_error(self):
        gtk.gdk.threads_enter()
        ErrorDialog(_('Please check your network connection!'), title = _('Network Error')).launch()
        gtk.gdk.threads_leave()

class UploadDialog(ProcessDialog):
    def __init__(self, data, parent):
        super(UploadDialog, self).__init__(data, parent)

        self.progressbar.set_text(_('Uploading...'))

    def process_data(self, data):
        self.processing = True
        try:
            title, locale, comment, source = data
            self.server.putsource(title, locale, comment, module_check.get_codename(), source)
        except:
            self.error = True

        self.processing = False

class UpdateDialog(ProcessDialog):
    def __init__(self, parent):
        super(UpdateDialog, self).__init__(None, parent)

        self.progressbar.set_text(_('Updating...'))
        
    def process_data(self, data):
        global SOURCES_DATA
        self.processing = True
        try:
            SOURCES_DATA = self.server.getsource(os.getenv('LANG'), module_check.get_codename())
        except:
            self.error = True

        self.processing = False

class SourceView(gtk.TextView):
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

    def parse_and_insert(self, buffer, iter, line, break_line = False):
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
        import pango
        buffer = self.get_buffer()

        buffer.create_tag('full_comment', foreground = "blue")
        buffer.create_tag('type', weight = pango.WEIGHT_BOLD)
        buffer.create_tag('uri', underline = pango.UNDERLINE_SINGLE, foreground = 'blue')
        buffer.create_tag('distro', weight = pango.WEIGHT_BOLD)
        buffer.create_tag('component', foreground = "red")
        buffer.create_tag('addon_comment', foreground = "blue")

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
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

class SourceEditor(TweakModule):
    __title__ = _('Source Editor')
    __desc__ = _('Freely edit your software sources to fit your needs.\n'
                'Click "Update Sources" if you want to change the sources.\n'
                'Click "Submit Sources" if you want to share your sources with other people.')
    __icon__ = 'system-software-update'
    __category__ = 'application'

    def __init__(self):
        TweakModule.__init__(self, 'sourceeditor.ui')

        self.online_data = {}

        set_label_for_stock_button(self.update_button, _('Update Sources'))

        set_label_for_stock_button(self.submit_button, _('Submit Sources'))

        self.textview = SourceView(SOURCES_LIST)
        self.textview.set_sensitive(False)
        self.sw1.add(self.textview)
        buffer = self.textview.get_buffer()
        buffer.connect('changed', self.on_buffer_changed)

        self.setup_source_combo()
        self.update_source_combo()

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        self.hbox2.pack_end(un_lock, False, False, 0)
        self.hbox2.reorder_child(un_lock, 1)

    def reparent(self):
        self.main_vbox.reparent(self.inner_vbox)

    def setup_source_combo(self):
        model = gtk.ListStore(gobject.TYPE_STRING,
                        gobject.TYPE_STRING)
        self.source_combo.set_model(model)

        textcell = gtk.CellRendererText()
        self.source_combo.pack_start(textcell, True)
        self.source_combo.add_attribute(textcell, 'text', 1)

    def update_source_combo(self):
        model = self.source_combo.get_model()
        iter = self.source_combo.get_active_iter()
        if iter:
            (i, ) = model.get_path(iter)
        else:
            i = 0
        model.clear()

        iter = model.append()
        model.set(iter, 0, '/etc/apt/sources.list')
        model.set(iter, 1, 'sources.list')

        SOURCE_LIST_D = '/etc/apt/sources.list.d'
        if not os.path.exists(SOURCE_LIST_D):
            self.source_combo.set_active(0)
            return
        files = os.listdir(SOURCE_LIST_D)
        files.sort()
        for file in files:
            fullpath=os.path.join(SOURCE_LIST_D, file)
            if os.path.isdir(fullpath):
                continue
            iter = model.append()
            model.set(iter, 0, fullpath)
            model.set(iter, 1, file)

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

    def on_refresh_button_clicked(self, widget):
        refresh_source(widget.get_toplevel())

        self.emit('update', 'thirdsoft', 'update_thirdparty')

    def update_sourceslist(self):
        self.textview.update_content()
        self.redo_button.set_sensitive(False)
        self.save_button.set_sensitive(False)
        self.emit('call', 'mainwindow', 'get_notify', {})

    def on_submit_button_clicked(self, widget):
        dialog = SubmitDialog(widget.get_toplevel())
        source_data = ()
        if dialog.run() == gtk.RESPONSE_YES:
            if dialog.check_fill_data():
                source_data = dialog.get_source_data()
            else:
                ErrorDialog(_('Please input the correct information about sources!')).launch()
        dialog.destroy()

        if source_data:
            self.submit_source_data(source_data)

    def on_update_button_clicked(self, widget):
        dialog = UpdateDialog(widget.get_toplevel())
        dialog.run()
        if not dialog.error:
            if 'SOURCES_DATA' in globals() and SOURCES_DATA:
                    self.open_source_select_dialog()
            else:
                dialog = QuestionDialog(_('You can submit your sources to our server to help building the sources list, '
                        'or you can use the official sources.\n'
                        'Do you wish to use the official sources?'), 
                        title = _('No source data available'))
                if dialog.run() == gtk.RESPONSE_YES:
                    self.textview.update_content(DEFAULT_SOURCE)

                dialog.destroy()

    def open_source_select_dialog(self):
        dialog = SelectSourceDialog(self.get_toplevel())
        if dialog.run() == gtk.RESPONSE_YES:
            content = dialog.get_source_data()
            self.textview.update_content(content)
        dialog.destroy()

    def submit_source_data(self, data):
        dialog = UploadDialog(data, self.get_toplevel())
        dialog.run()
        if not dialog.error:
            InfoDialog(_('Your sources will be reviewed and made available for others soon.\nThank you!'), 
                    title = _('Successfully submitted')).launch()

    def on_buffer_changed(self, buffer):
        if buffer.get_modified():
            self.save_button.set_sensitive(True)
            self.redo_button.set_sensitive(True)
            self.emit('call', 'mainwindow', 'prepare_notify', {'data': self.notify_save})
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

    def notify_save(self):
        dialog = QuestionDialog(_("You've changed the sources.list without saving it.\nDo you want to save it?"))

        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_YES:
            self.emit('call', 'mainwindow', 'select_module', {'name': 'sourceeditor'})

    def on_save_button_clicked(self, wiget):
        text = self.textview.get_text().strip()
        if proxy.edit_file(self.textview.get_path(), text) == 'error':
            ErrorDialog(_('Please check the permission of the sources.list file'),
                    title=_('Save failed!')).launch()
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)
            self.refresh_button.set_sensitive(True)
            self.emit('call', 'mainwindow', 'get_notify', {})
            self.emit('update', 'thirdsoft', 'update_thirdparty')

    def on_redo_button_clicked(self, widget):
        dialog = QuestionDialog(_('The current content will be lost after reloading!\nDo you wish to continue?'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.textview.update_content()
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

        self.emit('call', 'mainwindow', 'get_notify', {})
        dialog.destroy()

    def on_delete_button_clicked(self, widget):
        if self.textview.get_path() ==  SOURCES_LIST:
            ErrorDialog(_('You can\'t delete sources.list!')).launch()
        else:
            dialog = QuestionDialog(_('The "%s" will be deleted!\nDo you wish to continue?') % self.textview.get_path())
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                model = self.source_combo.get_model()
                iter = self.source_combo.get_active_iter()
                (i, ) = model.get_path(iter)
                proxy.delete_file(model.get_value(iter, 0))
                model.remove(iter)

                iter = model.get_iter(i-1)
                self.source_combo.set_active_iter(iter)
            self.emit('call', 'mainwindow', 'get_notify', {})
            self.emit('update', 'thirdsoft', 'update_thirdparty')

    def on_polkit_action(self, widget, action):
        if action:
            if proxy.get_proxy():
                self.textview.set_sensitive(True)
                self.update_button.set_sensitive(True)
                self.submit_button.set_sensitive(True)
                self.refresh_button.set_sensitive(True)
                self.delete_button.set_sensitive(True)
            else:
                ServerErrorDialog().launch()
        else:
            AuthenticateFailDialog().launch()
