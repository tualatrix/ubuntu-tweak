#!/usr/bin/python
# Ubuntu Tweak - PyGTK based desktop configuration tool
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
import gobject
import thread

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import ListPack, TablePack
from ubuntutweak.widgets.dialogs import InfoDialog, QuestionDialog

#TODO
from ubuntutweak.common.utils import set_label_for_stock_button
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.common.factory import WidgetFactory
from ubuntutweak.common.package import PACKAGE_WORKER, AptCheckButton

(
    COLUMN_ICON,
    COLUMN_TITLE,
) = range(2)

class CleanDialog(gtk.Dialog):
    def __init__(self, parent):
        super(CleanDialog, self).__init__(title='', parent=parent)

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_text(_('Cleaning...'))
        self.vbox.add(self.progressbar)

        self.show_all()
        gobject.timeout_add(100, self.on_timeout)
        thread.start_new_thread(self.process_data, ())

    def process_data(self):
        os.system('rm -rf ~/.thumbnails/*')
        
    def on_timeout(self):
        self.progressbar.pulse()

        if os.listdir(os.path.join(os.path.expanduser('~'), '.thumbnails')):
            return True
        else:
            self.destroy()

class Nautilus(TweakModule):
    __title__ = _('Nautilus Settings')
    __desc__ = _('Manage the default file manager')
    __icon__ = ['file-manager', 'nautilus']
    __category__ = 'system'
    __desktop__ = ['gnome', 'une']

    def __init__(self):
        TweakModule.__init__(self)

        button = WidgetFactory.create("GconfCheckButton", 
                                      label=_('Show advanced permissions in the Nautilus "File Properties" window'),
                                      reset=True,
                                      key="show_advanced_permissions")

        box = ListPack(_("File Browser"), (button, )) 
        self.add_start(box, False, False, 0)

        hbox1 = gtk.HBox(False, 12)
        button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.set_clean_button_label(button)
        button.connect('clicked', self.on_clean_thumbnails_clicked)
        hbox1.pack_end(button, False, False, 0)

        box = TablePack(_('Thumbnail Settings'), (
                    WidgetFactory.create('GconfSpinButton',
                                                  key='thumbnail_size',
                                                  reset=True,
                                                  min=16, max=512, step=16,
                                                  label=_('Default thumbnail icon size (pixels)')),
                    WidgetFactory.create('GconfSpinButton',
                                                  key='maximum_size',
                                                  reset=True,
                                                  min=-1, max=512, step=1,
                                                  label=_('Maximum thumbnail cache size (megabytes)')),
                    WidgetFactory.create('GconfSpinButton',
                                                  key='maximum_age',
                                                  reset=True,
                                                  min=-1, max=180, step=1,
                                                  label=_('Thumbnail cache time (days)')),
                    hbox1,
            ))
        self.add_start(box, False, False, 0)

        self.PACKAGE_WORKER = PACKAGE_WORKER

        self.nautilus_terminal = AptCheckButton(_('Open folder in terminal'), 'nautilus-open-terminal')
        self.nautilus_terminal.connect('toggled', self.colleague_changed)
        self.nautilus_root = AptCheckButton(_('Open folder with root priveleges'), 'nautilus-gksu')
        self.nautilus_root.connect('toggled', self.colleague_changed)
        self.nautilus_wallpaper = AptCheckButton(_('Nautilus with wallpaper'), 'nautilus-wallpaper')
        self.nautilus_wallpaper.connect('toggled', self.colleague_changed)
        box = ListPack(_("Nautilus Extensions"), (
            self.nautilus_terminal,
            self.nautilus_root,
            self.nautilus_wallpaper,
        ))

        self.button = gtk.Button(stock = gtk.STOCK_APPLY)
        self.button.connect("clicked", self.on_apply_clicked, box)
        self.button.set_sensitive(False)
        hbox = gtk.HBox(False, 0)
        hbox.pack_end(self.button, False, False, 0)

        box.vbox.pack_start(hbox, False, False, 0)

        self.add_start(box, False, False, 0)

    def set_clean_button_label(self, button):
        try:
            size = os.popen('du -bs ~/.thumbnails').read().split()[0]
        except:
            size = '0'
            button.set_sensitive(False)
        set_label_for_stock_button(button, _('Delete thumbnail cache (Frees %s of disk space)') % filesizeformat(size))

    def on_clean_thumbnails_clicked(self, widget):
        question = QuestionDialog(_('The thumbnail cache will be deleted. Do you wish to continue?'),
            title = _('Warning'))
        if question.run() == gtk.RESPONSE_YES:
            question.destroy()

            dialog = CleanDialog(widget.get_toplevel())
            dialog.run()
            InfoDialog(_('Clean up Successful!')).launch()
            self.set_clean_button_label(widget)
        else:
            question.destroy()

    def on_apply_clicked(self, widget, box):
        to_add = []
        to_rm = []

        for widget in box.items:
            if widget.get_active():
                to_add.append(widget.pkgname)
            else:
                to_rm.append(widget.pkgname)

        self.PACKAGE_WORKER.perform_action(widget.get_toplevel(), to_add, to_rm)
        self.PACKAGE_WORKER.update_apt_cache(True)

        done = PACKAGE_WORKER.get_install_status(to_add, to_rm)

        if done:
            self.button.set_sensitive(False)
            InfoDialog(_('Update Successful!')).launch()
        else:
            InfoDialog(_('Update Failed!')).launch()
            for widget in box.items:
                widget.reset_active()

    def colleague_changed(self, widget):
        if self.nautilus_terminal.get_state() != self.nautilus_terminal.get_active() or\
                self.nautilus_root.get_state() != self.nautilus_root.get_active() or\
                self.nautilus_wallpaper.get_state() != self.nautilus_wallpaper.get_active():
                    self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)
