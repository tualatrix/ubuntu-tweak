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
import logging

from gi.repository import GObject, Gtk, GConf, GdkPixbuf

from ubuntutweak.utils import icon
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.modules  import TweakModule
from ubuntutweak.settings.gconfsettings import GconfSetting
from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.gui.dialogs import ErrorDialog, QuestionDialog, WarningDialog

log = logging.getLogger("Gnome")


class Gnome(TweakModule):
    __title__ = _('GNOME Settings')
    __desc__ = _('A lot of GNOME settings for panels, menus and other desktop elements')
    __icon__ = ['gnome-desktop-config', 'control-center2']
    __category__ = 'desktop'

    def __init__(self):
        TweakModule.__init__(self)

        changeicon_hbox = self.create_change_icon_hbox()

        box = TablePack(_("Panel Settings"), (
                    WidgetFactory.create("CheckButton",
                                    label=_("Display warning when removing a panel"),
                                    enable_reset=True,
                                    backend=GConf,
                                    key="/apps/panel/global/confirm_panel_remove"),
                    WidgetFactory.create("CheckButton",
                                    label=_("Complete lockdown of all panels"),
                                    enable_reset=True,
                                    backend=GConf,
                                    key="/apps/panel/global/locked_down"),
                    WidgetFactory.create("CheckButton",
                                    label=_("Enable panel animations"),
                                    enable_reset=True,
                                    backend=GConf,
                                    key="/apps/panel/global/enable_animations"),
                    WidgetFactory.create('ComboBox',
                                         label=_('Me Menu Setting'),
                                         key='/system/indicator/me/display',
                                         texts=[_("Don't Display"), _('Display user name'), _('Display real name')],
                                         values=[0, 1, 2],
                                         backend=GConf,
                                         type='int')
            ))
        self.add_start(box, False, False, 0)

        box = ListPack(_("Menu Settings"), (
                    WidgetFactory.create("CheckButton",
                                    label=_("Show Input Method menu in the context menu"),
                                    enable_reset=True,
                                    backend=GConf,
                                    key="/desktop/gnome/interface/show_input_method_menu"),
                    WidgetFactory.create("CheckButton",
                                    label=_("Show Unicode Control Character menu in the context menu"),
                                    enable_reset=True,
                                    backend=GConf,
                                    key="/desktop/gnome/interface/show_unicode_menu"),
                    WidgetFactory.create("CheckButton",
                                    label=_('Show icons in menus'),
                                    enable_reset=True,
                                    backend=GConf,
                                    key='/desktop/gnome/interface/menus_have_icons'),
                    WidgetFactory.create("CheckButton",
                                    label=_('Show icons on buttons'),
                                    enable_reset=True,
                                    backend=GConf,
                                    key='/desktop/gnome/interface/buttons_have_icons'),
                    changeicon_hbox,
            ))
        self.add_start(box, False, False, 0)

        box = ListPack(_("Screensaver"), (
                    WidgetFactory.create("CheckButton",
                                         label=_("Enable user switching whilst screen is locked."),
                                         backend=GConf,
                                         enable_reset=True,
                                         key="/apps/gnome-screensaver/user_switch_enabled"),
            ))
        self.add_start(box, False, False, 0)

        current_terminal_profile_key = GconfSetting('/apps/gnome-terminal/global/default_profile')
        current_terminal_profile = current_terminal_profile_key.get_value()
        default_show_menubar_key = '/apps/gnome-terminal/profiles/%s/default_show_menubar' % current_terminal_profile
        box = ListPack(_("Terminal"), (
                    WidgetFactory.create("CheckButton",
                                         label=_("Display menubar when Terminal starts up (for current profile)"),
                                         backend=GConf,
                                         enable_reset=True,
                                         key=default_show_menubar_key),
            ))
        self.add_start(box, False, False, 0)

        #TODO unity don't have it
        self.recently_used = Gtk.CheckButton(_('Enable system-wide "Recent Documents" list'))
        self.recently_used.set_active(self.get_state())
        self.recently_used.connect('toggled', self.colleague_changed)
        box = ListPack(_("History"), (
                    self.recently_used,
            ))
        self.add_start(box, False, False, 0)

    def create_change_icon_hbox(self):
        hbox = Gtk.HBox(spacing=12)
        label = Gtk.Label(label=_('Click this button to change the menu logo image'))
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 0)

        button = Gtk.Button()
        button.connect('clicked', self.on_change_icon_clicked)
        image = Gtk.Image.new_from_pixbuf(icon.get_from_name('start-here'))
        button.set_image(image)
        hbox.pack_end(button, False, False, 0)

        return hbox

    def on_change_icon_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Choose a new logo image'),
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=(Gtk.STOCK_REVERT_TO_SAVED, Gtk.ResponseType.DELETE_EVENT,
                                                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_("PNG images with 24x24 size or SVG images"))
        filter.add_pattern('*.png')
        filter.add_pattern('*.svg')
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)

        icon_theme = GconfSetting('/desktop/gnome/interface/icon_theme').get_value()
        dest = os.path.expanduser('~/.icons/%s/apps/24/start-here' % icon_theme)

        revert_button = dialog.get_action_area().get_children()[-1]

        HAVE_ICON = os.path.exists(dest + '.png') or os.path.exists(dest + '.svg')

        if not HAVE_ICON:
            revert_button.set_sensitive(False)

        filename = ''
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            dialog.destroy()

            if filename:
                ext = os.path.splitext(filename)[1]
                log.debug('The select file name is: %s' % ext)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
                w, h = pixbuf.get_width(), pixbuf.get_height()
                dest = dest + ext

                if ext == '.png' and (w != 24 or h != 24):
                    ErrorDialog(message=_("This image size isn't suitable for the panel.\nIt should measure 24x24.")).launch()
                    return
                else:
                    os.system('mkdir -p %s' % os.path.dirname(dest))
                    os.system('cp %s %s' % (filename, dest))

                    if ext == '.svg':
                        pixbuf = pixbuf.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
                    image = Gtk.Image.new_from_pixbuf(pixbuf)
                    widget.set_image(image)
        elif response == Gtk.ResponseType.DELETE_EVENT:
            dialog.destroy()
            for dest in glob.glob(dest + '*'):
                os.remove(dest)
            image = Gtk.Image.new_from_pixbuf(icon.get_from_name('start-here', force_reload=True))
            widget.set_image(image)
        else:
            dialog.destroy()
            return

        dialog = QuestionDialog(message=_('Do you want your changes to take effect immediately?'))
        if dialog.run() == Gtk.ResponseType.YES:
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
            dialog = WarningDialog(title=_("Warning"),
                                   message=_('Disabling "Recent Documents" may break other software, for example the history feature in VMware Player.'))
            if dialog.run() == Gtk.ResponseType.YES:
                os.system('rm -r %s' % file)
                os.system('mkdir %s' % file)
            else:
                widget.set_active(True)
            dialog.destroy()
