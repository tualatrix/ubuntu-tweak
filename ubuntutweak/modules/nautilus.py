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
import gobject
import gconf
import gettext
import thread

try:
    from ubuntutweak.package import package_worker, AptCheckButton
    if package_worker.get_cache():
        DISABLE = False
    else:
        DISABLE = True
except ImportError:
    DISABLE = True

from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.misc import filesizeformat
from ubuntutweak.common.factory import WidgetFactory
from ubuntutweak.widgets import ListPack, TablePack
from ubuntutweak.widgets.dialogs import InfoDialog, QuestionDialog
from ubuntutweak.common.utils import set_label_for_stock_button

(
    COLUMN_ICON,
    COLUMN_TITLE,
) = range(2)

class CleanDialog(gtk.Dialog):
    def __init__(self, parent):
        super(CleanDialog, self).__init__(title = '', parent = parent)

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

class EmblemsView(gtk.IconView):
    def __init__(self):
        gtk.IconView.__init__()

        model = self.__create_model()
        self.set_model(model)

    def __create_model(self):
        model = gtk.ListStore(
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING)

        return model

    def __add_colums(self):
        renderer = gtk.CellRendererPixbuf()
        self.pack_start(renderer, False)
        self.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.set_attributes(renderer, text = COLUMN_TITLE)

    def update_model(self):
        pass

class Nautilus(TweakModule):
    __title__ = _('Nautilus Settings')
    __desc__ = _('Settings your default file manager')
    __icon__ = ['file-manager', 'nautilus']
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        button = WidgetFactory.create("GconfCheckButton", 
                                      label = _('Show advanced permissions in the Nautilus "File Properties" window'),
                                      key = "show_advanced_permissions")

        box = ListPack(_("File Browser"), (button, )) 
        self.add_start(box, False, False, 0)

        boxes = []
        hbox1 = gtk.HBox(False, 5)
        label = gtk.Label(_('Default thumbnail icon size (pixels)'))
        hbox1.pack_start(label, False, False, 0)
        boxes.append(hbox1)

        button = WidgetFactory.create('GconfSpinButton', 
                                      key = 'thumbnail_size',
                                      min = 16, max = 512, step = 16)
        hbox1.pack_end(button, False, False, 0)

        button = WidgetFactory.create('GconfSpinButton', 
                                      key = 'maximum_size',
                                      min = -1, max = 512, step = 1)
        if button:
            hbox2 = gtk.HBox(False, 5)
            label = gtk.Label(_('Maximum size of the thumbnail cache (megabytes)'))

            hbox2.pack_start(label, False, False, 0)
            hbox2.pack_end(button, False, False, 0)
            boxes.append(hbox2)

        button = WidgetFactory.create('GconfSpinButton', 
                                      key = 'maximum_age',
                                      min = -1, max = 180, step = 1)

        if button:
            hbox3 = gtk.HBox(False, 5)
            label = gtk.Label(_('Maximum age for the thumbnail in the cache (days)'))
            hbox3.pack_start(label, False, False, 0)
            hbox3.pack_end(button, False, False, 0)
            boxes.append(hbox3)

        hbox4 = gtk.HBox(False, 5)
        button = gtk.Button(stock = gtk.STOCK_CLEAR)
        self.set_clean_button_label(button)
        button.connect('clicked', self.on_clean_thumbnails_clicked)
        hbox4.pack_end(button, False, False, 0)
        boxes.append(hbox4)

        box = ListPack(_('Thumbnails Settings'), boxes)
        self.add_start(box, False, False, 0)


        if not DISABLE:
            self.package_worker = package_worker

            self.nautilus_terminal = AptCheckButton(_('Nautilus with Open Terminal'), 'nautilus-open-terminal')
            self.nautilus_terminal.connect('toggled', self.colleague_changed)
            self.nautilus_root = AptCheckButton(_('Nautilus with Root Privileges'), 'nautilus-gksu')
            self.nautilus_root.connect('toggled', self.colleague_changed)
            self.nautilus_wallpaper = AptCheckButton(_('Nautilus with Wallpaper'), 'nautilus-wallpaper')
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
        set_label_for_stock_button(button, _('Clean up the thumbnails cache (will free %s of disk space)') % filesizeformat(size))

    def on_clean_thumbnails_clicked(self, widget):
        question = QuestionDialog(_('The thumbnails cache will be cleaned, Do you wish to continue?'), 
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

        self.package_worker.perform_action(widget.get_toplevel(), to_add, to_rm)
        self.package_worker.update_apt_cache(True)

        done = package_worker.get_install_status(to_add, to_rm)

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
