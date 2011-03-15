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

import gobject
from gi.repository import Gtk, Unique, Pango

from ubuntutweak.gui import GuiBuilder


class WelcomePage(Gtk.VBox):
    def __init__(self):
        gobject.GObject.__init__(self)

        self.set_border_width(20)

        title = Gtk.MenuItem(label='')
        label = title.get_child()
        label.set_markup(_('\n<span size="xx-large">Welcome to <b>Ubuntu Tweak!</b></span>\n'))
        label.set_alignment(0.5, 0.5)
        title.select()
        self.pack_start(title, False, False, 10)

        tips = self.create_tips(
                _('Tweak otherwise hidden settings.'),
                _('Clean up unused packages to free up diskspace.'),
                _('Easily install up-to-date versions of many applications.'),
                _('Configure file templates and shortcut scripts for easy access to common tasks.'),
                _('Many more useful features!'),
                )

    def create_tips(self, *tips):
        for tip in tips:
            hbox = Gtk.HBox()
            image = Gtk.Image.new_from_stock(Gtk.STOCK_GO_FORWARD,
                                             Gtk.IconSize.BUTTON)
            hbox.pack_start(image, False, False, 15)

            label = Gtk.Label()
            label.set_alignment(0.0, 0.5)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            label.set_markup(tip)
            hbox.pack_start(label, True, True, 0)

            self.pack_start(hbox, False, False, 10)


class UbuntuTweakApp(Unique.App, GuiBuilder):
    def __init__(self, name='com.ubuntu-tweak.main', startup_id=''):
        Unique.App.__init__(self, name=name, startup_id=startup_id)
        GuiBuilder.__init__(self, file_name='mainwindow.ui')

        self.tweaknotebook.append_page(WelcomePage(), Gtk.Label(label=_('Welcome')))

        self.watch_window(self.mainwindow)
        self.connect('message-received', self.on_message_received)

        self.mainwindow.show_all()

    def on_mainwindow_destroy(self, widget):
        Gtk.main_quit()

    def on_message_received(self, app, command, message, time):
        if command == Unique.Command.ACTIVATE:
            self.mainwindow.present()

        return False

    def run(self):
        Gtk.main()
