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
import os
import gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import ListPack
from ubuntutweak.widgets.dialogs import ErrorDialog, QuestionDialog

#TODO
from ubuntutweak.common.config import TweakSettings
from ubuntutweak.common.factory import WidgetFactory
from ubuntutweak.common.utils import get_icon_with_name

class Gnome(TweakModule):
    __title__ = _('GNOME Settings')
    __desc__ = _('A lot of GNOME settings about panel and others')
    __icon__ = ['gnome-desktop-config', 'control-center2']
    __category__ = 'desktop'

    def __init__(self):
        TweakModule.__init__(self)

        self.__setting = TweakSettings()

        changeicon_hbox = self.create_change_icon_hbox()

        box = ListPack(_("Panel Settings"), (
                    WidgetFactory.create("GconfCheckButton", 
                                    label=_("Display warning when removing a panel"),
                                    key="confirm_panel_remove"),
                    WidgetFactory.create("GconfCheckButton", 
                                    label=_("Complete lockdown of all panels"),
                                    key="locked_down"),
                    WidgetFactory.create("GconfCheckButton", 
                                    label=_("Enable panel animations"),
                                    key="enable_animations"),
            ))
        self.add_start(box, False, False, 0)

        box = ListPack(_("Menu Settings"), (
                    WidgetFactory.create("GconfCheckButton", 
                                    label=_("Show Input Method menu on the context menu"),
                                    key="show_input_method_menu"),
                    WidgetFactory.create("GconfCheckButton",
                                    label=_("Show Unicode Method menu on the context menu"),
                                    key="show_unicode_menu"),
                    WidgetFactory.create("GconfCheckButton",
                                    label=_("Show Unicode Method menu on the context menu"),
                                    key="show_unicode_menu"),
                    WidgetFactory.create("GconfCheckButton",
                                    label=_('Menus have icons'),
                                    key='/desktop/gnome/interface/menus_have_icons'),
                    WidgetFactory.create("GconfCheckButton",
                                    label=_('Buttons have icons'),
                                    key='/desktop/gnome/interface/buttons_have_icons'),
                    changeicon_hbox,
            ))
        self.add_start(box, False, False, 0)

        box = ListPack(_("Screensaver"), (
                    WidgetFactory.create("GconfCheckButton", 
                                         label=_("Enable user switching when screen is locked."),
                                         key="user_switch_enabled"),
            ))
        self.add_start(box, False, False, 0)

        self.recently_used = gtk.CheckButton(_('Enable system-wide "Recently Documents" list'))
        self.recently_used.connect('toggled', self.colleague_changed)
        self.recently_used.set_active(self.get_state())
        box = ListPack(_("History"), (
                    self.recently_used,
            ))
        self.add_start(box, False, False, 0)

    def create_change_icon_hbox(self):
        hbox = gtk.HBox(False, 10)
        label = gtk.Label(_('Click the button to change the menu logo'))
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 0)

        button = gtk.Button()
        button.connect('clicked', self.on_change_icon_clicked)
        image = gtk.image_new_from_pixbuf(get_icon_with_name('start-here', 24))
        button.set_image(image)
        hbox.pack_end(button, False, False, 0)

        return hbox

    def on_change_icon_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_('Choose a new logo'),
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_REVERT_TO_SAVED, gtk.RESPONSE_DELETE_EVENT,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name(_("PNG image (*.png)"))
        filter.add_mime_type("image/png")
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)

        dest = os.path.expanduser('~/.icons/%s/24x24/places/start-here.png' % self.__setting.get_icon_theme())
        revert_button = dialog.action_area.get_children()[-1]
        if not os.path.exists(dest):
            revert_button.set_sensitive(False)

        filename = ''
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()

            if filename:
                pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                w, h = pixbuf.get_width(), pixbuf.get_height()
                if w != 24 or h != 24:
                    ErrorDialog(_("The size isn't suitable for the panel.\nIt should be 24x24.")).launch()
                else:
                    os.system('mkdir -p %s' % os.path.dirname(dest))
                    os.system('cp %s %s' % (filename, dest))

                    image = gtk.image_new_from_file(dest)
                    widget.set_image(image)
            dialog.destroy()
        elif response == gtk.RESPONSE_DELETE_EVENT:
            os.remove(dest)
            image = gtk.image_new_from_pixbuf(get_icon_with_name('start-here', 24))
            widget.set_image(image)
            dialog.destroy()
        else:
            dialog.destroy()
            return

        dialog = QuestionDialog(_('Do you want your changes to take effect immediately?'))
        if dialog.run() == gtk.RESPONSE_YES:
            os.system('killall gnome-panel')

        dialog.destroy()

    def get_state(self):
        file = os.path.join(os.path.expanduser("~"), ".recently-used.xbel")
        if os.path.exists(file):
            if os.path.isdir(file):
                return False
            elif os.path.isfile(file):
                return True
        else:
            return True

    def colleague_changed(self, widget):
        enabled = self.recently_used.get_active()
        file = os.path.expanduser("~/.recently-used.xbel")
        if enabled:
            os.system('rm -r %s' % file)
            os.system('touch %s' % file)
        else:
            os.system('rm -r %s' % file)
            os.system('mkdir %s' % file)
