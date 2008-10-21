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
from xmlrpclib import ServerProxy, Error
from common.LookupIcon import *
from common.PolicyKit import DbusProxy, PolkitButton
from common.Widgets import TweakPage, InfoDialog, QuestionDialog, ErrorDialog

(
    COLUMN_CHECK,
    COLUMN_ICON,
    COLUMN_NAME,
    COLUMN_DESC,
    COLUMN_DISPLAY,
) = range(5)

#SOURCES_LIST = '/etc/apt/sources.list'
SOURCES_LIST = '/home/tualatrix/Desktop/sources.list'

class SelectSourceDialog(gtk.Dialog):
    def __init__(self):
        super(SelectSourceDialog, self).__init__()

        self.set_title(_('Select the source what you want'))
        self.set_border_width(10)
        self.set_resizable(False)

        label = gtk.Label()
        label.set_markup('<b><big>Select the source</big></b>\n\nYou can read the title and comment to determine which source is suitable for you')
        label.set_alignment(0, 0)
        self.vbox.pack_start(label, False, False, 0)

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

        self.expander = gtk.Expander('Details')
        self.vbox.pack_start(self.expander)
        self.expander.add(self.detail)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(_('Change'), gtk.RESPONSE_YES)

        self.show_all()

    def on_button_toggled(self, widget, value):
        self.detail.set_text(value)

class SubmitDialog(gtk.Dialog):
    def __init__(self):
        super(SubmitDialog, self).__init__()

        l_title = gtk.Label()
        l_title.set_text_with_mnemonic(_("_Source Title:"))
        l_title.set_alignment(0, 0)
        l_locale = gtk.Label()
        l_locale.set_text_with_mnemonic(_("Locale"))
        l_locale.set_alignment(0, 0)
        l_comment = gtk.Label()
        l_comment.set_text_with_mnemonic(_("Comm_ent:"))
        l_comment.set_alignment(0, 0)

        self.e_title = gtk.Entry ();
        self.e_title.set_tooltip_text(_('Enter the title of the source, such as "Ubuntu Official Repostory"'))
#        self.e_title.connect("activate", self.on_entry_activate)
        self.e_locale = gtk.Entry ();
        self.e_locale.set_tooltip_text(_("If the locale isn't correct, you can edit by you self"))
        self.e_locale.set_text(os.getenv('LANG'))
#        self.e_locale.connect("activate", self.on_entry_activate)
        self.e_comment = gtk.Entry ();
#        self.e_comment.connect("activate", self.on_entry_activate)

        table = gtk.Table(3, 2)
        table.attach(l_title, 0, 1, 0, 1, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(l_locale, 0, 1, 1, 2, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(l_comment, 0, 1, 2, 3, xoptions = gtk.FILL, xpadding = 10, ypadding = 10)
        table.attach(self.e_title, 1, 2, 0, 1)
        table.attach(self.e_locale, 1, 2, 1, 2)
        table.attach(self.e_comment, 1, 2, 2, 3)

        self.vbox.pack_start(table)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(_('Submit'), gtk.RESPONSE_YES)

        self.set_default_response(gtk.RESPONSE_YES)

        self.show_all()

    def get_source_data(self):
        return (self.e_title.get_text().strip(), 
                self.e_locale.get_text().strip(), 
                self.e_comment.get_text().strip(),
                file(SOURCES_LIST).read())

    def check_fill_data(self):
        return self.e_title.get_text().strip() \
                and self.e_locale.get_text().strip() \
                and self.e_comment.get_text().strip()

class ProcessDialog(gtk.Dialog):
    def __init__(self, data):
        super(ProcessDialog, self).__init__()

        socket.setdefaulttimeout(10)

        self.count = 0
        self.error = None
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
        ErrorDialog('hello').launch()
        gtk.gdk.threads_leave()

class UploadDialog(ProcessDialog):
    def __init__(self, data = None):
        super(UploadDialog, self).__init__(data)

        self.progressbar.set_text(_('Uploding...'))

    def process_data(self, data):
        self.processing = True
        try:
            title, locale, comment, source = data
            self.server.putsource(title, locale, comment, source)
        except:
            self.error = True

        self.processing = False

class UpdateDialog(ProcessDialog):
    def __init__(self):
        super(UpdateDialog, self).__init__(None)

        self.progressbar.set_text(_('Updating...'))
        
    def process_data(self, data):
        global SOURCES_DATA
        self.processing = True
        try:
            SOURCES_DATA = self.server.getsource(os.getenv('LANG'))
        except:
            self.error = True

        self.processing = False

class SourceView(gtk.TextView):
    def __init__(self):
        super(SourceView, self).__init__()

        self.create_tags()
        self.update_content()

    def update_content(self):
        buffer = self.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
#        buffer.set_text(data)
        iter = buffer.get_iter_at_offset(0)
        for line in file(SOURCES_LIST):
            if line.strip():
                if line.strip()[0] == '#':
                    buffer.insert_with_tags_by_name(iter, line, 'full_comment')
                else:
                    buffer.insert_with_tags_by_name(iter, line.split()[0], 'type')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, line.split()[1], 'uri')
                    self.insert_blank(buffer, iter)
                    buffer.insert_with_tags_by_name(iter, line.split()[2], 'distro')
                    self.insert_blank(buffer, iter)
                    self.seprarte_component(buffer, line.split()[3:], iter)
                    self.insert_line(buffer, iter)
            else:
                buffer.insert(iter, line)

    def create_tags(self):
        import pango
        buffer = self.get_buffer()

        buffer.create_tag('full_comment', foreground = "blue")
        buffer.create_tag('type', weight = pango.WEIGHT_BOLD)
        buffer.create_tag('uri', underline = pango.UNDERLINE_SINGLE)
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
        self.insert_blank(buffer, iter)
        if has_comment:
            buffer.insert_with_tags_by_name(iter, ' '.join(list[stop_i:]), 'addon_comment')

    def get_text(self):
        buffer = self.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())

class SourceEditor(TweakPage):
    def __init__(self):
        super(SourceEditor, self).__init__(
                _('Source Editor'),
                _('By editing the sources.list to make it what you like'))

        self.online_data = {}
        self.proxy = DbusProxy()
        
        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        vbox = gtk.VBox(False, 8)
        hbox.pack_start(vbox, False, False, 5)

        self.submit_button = gtk.Button(_('Submit'))
        self.submit_button.connect('clicked', self.on_submit_button_clicked)
        vbox.pack_start(self.submit_button, False, False, 0)

        self.update_button = gtk.Button(_('Update'))
        self.update_button.set_sensitive(False)
        self.update_button.connect('clicked', self.on_update_button_clicked)
        vbox.pack_start(self.update_button, False, False, 0)

        self.textview = SourceView()
        self.textview.set_sensitive(False)
        sw.add(self.textview)
        buffer = self.textview.get_buffer()
        buffer.connect('changed', self.on_buffer_changed)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 5)

        self.save_button = gtk.Button(stock = gtk.STOCK_SAVE)
        self.save_button.set_sensitive(False)
        self.save_button.connect('clicked', self.on_save_button_clicked)
        hbox.pack_start(self.save_button, False, False, 0)

        self.redo_button = gtk.Button(stock = gtk.STOCK_REDO)
        self.redo_button.set_sensitive(False)
        self.redo_button.connect('clicked', self.on_redo_button_clicked)
        hbox.pack_start(self.redo_button, False, False, 0)

        un_lock = PolkitButton()
        un_lock.connect('changed', self.on_polkit_action)
        hbox.pack_end(un_lock, False, False, 5)

        self.show_all()

    def on_network_failed(self, widget):
        ErrorDialog('NetWork Error').launch()

    def on_submit_button_clicked(self, widget):
        dialog = SubmitDialog()
        source_data = ()
        if dialog.run() == gtk.RESPONSE_YES:
            if dialog.check_fill_data():
                source_data = dialog.get_source_data()
            else:
                ErrorDialog('Wow').launch()
        dialog.destroy()

        if source_data:
            self.submit_source_data(source_data)

    def on_update_button_clicked(self, widget):
        dialog = UpdateDialog()
        dialog.run()
        self.open_source_select_dialog()

    def open_source_select_dialog(self):
        if 'SOURCES_DATA' in globals():
            dialog = SelectSourceDialog()
            if dialog.run() == gtk.RESPONSE_YES:
                print 'I have choice'
            dialog.destroy()
        else:
            ErrorDialog('No source here').launch()

    def submit_source_data(self, data):
        dialog = UploadDialog(data)
        dialog.run()

    def on_buffer_changed(self, buffer):
        self.save_button.set_sensitive(True)
        self.redo_button.set_sensitive(True)

    def on_save_button_clicked(self, wiget):
        text = self.textview.get_text()
        if self.proxy.edit_file(SOURCES_LIST, text) == 'error':
            ErrorDialog('Error').launch()
        else:
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

    def on_redo_button_clicked(self, widget):
        dialog = QuestionDialog(_('I will reload the file and currenly content will be lost!'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.textview.update_content()
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

        dialog.destroy()

    def on_polkit_action(self, widget, action):
        proxy = self.proxy.get_proxy()

        if action:
            if proxy:
                self.textview.set_sensitive(True)
                self.update_button.set_sensitive(True)
            else:
                ErrorDialog(_("<b><big>Service hasn't initialized yet</big></b>\n\nYou need to restart your Ubuntu.")).launch()
        else:
            ErrorDialog(_('<b><big>Could not authenticate</big></b>\n\nAn unexpected error has occurred.')).launch()

if __name__ == '__main__':
    from Utility import Test
    Test(SourceEditor)
