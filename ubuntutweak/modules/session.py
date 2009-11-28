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

import pygtk
pygtk.require("2.0")
import gtk
import os

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import ListPack, TablePack
from ubuntutweak.widgets.dialogs import ErrorDialog

from ubuntutweak.common.consts import *
from ubuntutweak.common.factory import WidgetFactory

class Session(TweakModule):
    __title__ = _('Session control')
    __desc__ = _('Control your system session releated features')
    __icon__ = 'gnome-session-hibernate'
    __category__ = 'startup'
    __desktop__ = 'gnome'

    def __init__(self):
        TweakModule.__init__(self)

        data = {
             'changed': self.on_entry_changed,
         }
        label1, entry1 = WidgetFactory.create('GconfEntry',
                                         label=_('File Manager'),
                                         key='/desktop/gnome/session/required_components/filemanager',
                                         signal_dict=data,
                                         )
        label2, entry2 = WidgetFactory.create('GconfEntry',
                                         label=_('Panel'),
                                         signal_dict=data,
                                         key='/desktop/gnome/session/required_components/panel')
        label3, entry3 = WidgetFactory.create('GconfEntry',
                                         label=_('Window Manager'),
                                         signal_dict=data,
                                         key='/desktop/gnome/session/required_components/windowmanager')

        hbox1 = gtk.HBox(False, 12)
        self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        self.apply_button.changed_table = {}
        self.apply_button.set_sensitive(False)
        self.apply_button.connect('clicked', self.on_apply_clicked, (entry1, entry2, entry3))
        hbox1.pack_end(self.apply_button, False, False, 0)

        table = TablePack(_('Session Control'), (
                    (label1, entry1),
                    (label2, entry2),
                    (label3, entry3),
                    hbox1,
                ))

        self.add_start(table, False, False, 0)

        box = ListPack(_("Session Options"), (
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Automatically save open applications when logging out"),
                                         key="auto_save_session"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Show logout prompt"),
                                         key="logout_prompt"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Allow TCP Connections (Remote Desktop Connect)"),
                                         key="allow_tcp_connections"),
                    WidgetFactory.create("GconfCheckButton",
                                         label=_("Suppress the dialog to confirm logout, restart and shutdown action"),
                                         key="/apps/indicator-session/suppress_logout_restart_shutdown"),
                ))

        self.add_start(box, False, False, 0)

    def on_entry_changed(self, widget):
        if widget.is_changed():
            self.apply_button.changed_table[widget] = True
        else:
            self.apply_button.changed_table.pop(widget, None)
        self.set_apply_button_sensitive()

    def set_apply_button_sensitive(self):
        if self.apply_button.changed_table.items():
            self.apply_button.set_sensitive(True)
        else:
            self.apply_button.set_sensitive(False)

    def on_apply_clicked(self, widget, entrys):
        for entry in entrys:
            if entry.is_changed():
                if os.popen('which %s' % entry.get_text()).read():
                    entry.on_edit_finished_cb(entry)
                else:
                    ErrorDialog(_('Please enter a valid application command line.'), title=_('"%s" is not available.') % entry.get_text()).launch()
                    entry.reset()
        self.apply_button.set_sensitive(False)
