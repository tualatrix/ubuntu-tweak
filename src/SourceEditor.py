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
import gobject
import gettext
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

class SourceView(gtk.TextView):
    def __init__(self):
        super(SourceView, self).__init__()

        self.create_tags()
        self.update_content()

    def update_content(self):
#        data = file('/etc/apt/sources.list').read()
        buffer = self.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
#        buffer.set_text(data)
        iter = buffer.get_iter_at_offset(0)
        for line in file('/etc/apt/sources.list'):
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

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, True, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        vbox = gtk.VBox(False, 8)
        hbox.pack_start(vbox, False, False, 5)

        self.save_button = gtk.Button(stock = gtk.STOCK_SAVE)
        self.save_button.set_sensitive(False)
        self.save_button.connect('clicked', self.on_save_button_clicked)
        vbox.pack_start(self.save_button, False, False, 0)

        self.redo_button = gtk.Button(stock = gtk.STOCK_REDO)
        self.redo_button.set_sensitive(False)
        self.redo_button.connect('clicked', self.on_redo_button_clicked)
        vbox.pack_start(self.redo_button, False, False, 0)

        self.textview = SourceView()
        self.textview.set_sensitive(False)
        sw.add(self.textview)
        buffer = self.textview.get_buffer()
        buffer.connect('changed', self.on_buffer_changed)

        # button
        hbox = gtk.HBox(False, 0)
        self.pack_end(hbox, False ,False, 5)

        un_lock = PolkitButton()
        un_lock.connect('authenticated', self.on_polkit_action)
        un_lock.connect('failed', self.on_auth_failed)
        hbox.pack_end(un_lock, False, False, 5)

        self.show_all()

    def on_buffer_changed(self, buffer):
        self.save_button.set_sensitive(True)
        self.redo_button.set_sensitive(True)

    def on_save_button_clicked(self, wiget):
        text = self.textview.get_text()
        self.save_button.set_sensitive(False)
        self.redo_button.set_sensitive(False)

    def on_redo_button_clicked(self, widget):
        dialog = QuestionDialog(_('I will reload the file and currenly content will be lost!'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.textview.update_content()
            self.save_button.set_sensitive(False)
            self.redo_button.set_sensitive(False)

        dialog.destroy()

    def on_auth_failed(self, widget):
        gtk.gdk.threads_enter()
        ErrorDialog(_('<b><big>Could not authenticate</big></b>\n\nAn unexpected error has occurred.')).launch()
        gtk.gdk.threads_leave()

    def on_polkit_action(self, widget):
        gtk.gdk.threads_enter()
        proxy = DbusProxy.get_proxy()

        if proxy:
            self.textview.set_sensitive(True)
        else:
            ErrorDialog(_("<b><big>Service hasn't initialized yet</big></b>\n\nYou need to restart your Ubuntu.")).launch()

        gtk.gdk.threads_leave()

if __name__ == '__main__':
    from Utility import Test
    Test(SourceEditor)
