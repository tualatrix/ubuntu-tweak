# Ubuntu Tweak - PyGTK based desktop configuration tool
#
# Copyright (C) 2010 TualatriX <tualatrix@gmail.com>
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
import glob
import glib
import logging
import subprocess

from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import ListPack, TablePack
from ubuntutweak.widgets.dialogs import ErrorDialog
from ubuntutweak.policykit import PolkitButton, proxy

from ubuntutweak.common.factory import WidgetFactory
from ubuntutweak.common.systeminfo import module_check
from ubuntutweak.conf.gconfsetting import UserGconfSetting

log = logging.getLogger('LoginSettings')

class LoginSettings(TweakModule):
    __title__ = _('Login Settings')
    __desc__ = _('Control the appearance and behaviour of your login screen')
    __icon__ = 'gdm-setup'
    __category__ = 'startup'
    __desktop__ = 'gnome'

    def __init__(self):
        TweakModule.__init__(self, 'loginsettings.ui')

        log.debug('Start to build "Session Options"')
        self.options_box = ListPack(_("Login Options"), (
                    WidgetFactory.create("UserGconfCheckButton",
                                         user='gdm',
                                         label=_("Disable user list in gdm"),
                                         key="/apps/gdm/simple-greeter/disable_user_list"),
                    WidgetFactory.create("UserGconfCheckButton",
                                         user='gdm',
                                         label=_("Play sound at login"),
                                         key="/desktop/gnome/sound/event_sounds"),
                    WidgetFactory.create("UserGconfCheckButton",
                                         user='gdm',
                                         label=_("Disable showing the restart buttons"),
                                         key="/apps/gdm/simple-greeter/disable_restart_buttons"),
            ))
        for item in self.options_box.items:
            log.debug('Set widget %s to sensitive False', item)
            item.set_sensitive(False)
        log.debug('Build "Session Options" finished')

        self.add_start(self.options_box, False, False, 0)

        self.icon_setting = UserGconfSetting('/apps/gdm/simple-greeter/logo_icon_name')
        self.icon_theme_setting = UserGconfSetting('/desktop/gnome/interface/icon_theme')
        self.__setup_logo_image()
        self.__setup_background_image()
        self.vbox1.unparent()
        self.vbox1.set_sensitive(False)

        box = ListPack(_('Login Theme'), (self.vbox1))
        self.add_start(box, False, False, 0)

        hbox = gtk.HBox(False, 12)
        polkit_button = PolkitButton()
        polkit_button.connect('changed', self.on_polkit_action)
        hbox.pack_end(polkit_button, False, False, 0)
        self.add_start(hbox, False, False, 0)

    def __setup_logo_image(self):
        icon_name = self.icon_setting.get_value(user='gdm')
        log.debug('Get icon_name from user: gdm, icon name: %s' % icon_name)

        path = os.path.expanduser('~gdm/.icons/%s/apps/64/%s.png' % (
                                    self.icon_theme_setting.get_value(user='gdm'),
                                    self.icon_setting.get_value(user='gdm')))

        if proxy.is_exists(path):
            path = proxy.get_as_tempfile(path)
            log.debug('Custom log is exits, the tempfile is %s' % path)
            self.logo_image.set_from_file(path)
        else:
            icontheme = gtk.IconTheme()
            icontheme.set_custom_theme(self.icon_theme_setting.get_value(user='gdm'))
            self.logo_image.set_from_pixbuf(icontheme.load_icon(icon_name, 64, 0))

    def __setup_background_image(self):
        self.background_setting = UserGconfSetting('/desktop/gnome/background/picture_filename')
        background_path = self.background_setting.get_value(user='gdm')
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(background_path)
            pixbuf = pixbuf.scale_simple(160, 120, gtk.gdk.INTERP_NEAREST)
            self.background_image.set_from_pixbuf(pixbuf)
        except:
            pass

    def on_polkit_action(self, widget, action):
        if action:
            if proxy.get_proxy():
                for item in self.options_box.items:
                    item.set_sensitive(True)
                self.vbox1.set_sensitive(True)
            else:
                ServerErrorDialog().launch()
        else:
            AuthenticateFailDialog().launch()

    def on_logo_button_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_('Choose a new logo image'),
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_REVERT_TO_SAVED, gtk.RESPONSE_DELETE_EVENT,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name(_("PNG image with 64x64 size (*.png)"))
        filter.add_mime_type("image/png")
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)

        dest = os.path.expanduser('~gdm/.icons/%s/apps/64/%s.png' % (
                                    self.icon_theme_setting.get_value(user='gdm'),
                                    self.icon_setting.get_value(user='gdm')))

        revert_button = dialog.action_area.get_children()[-1]
        if not proxy.is_exists(dest):
            revert_button.set_sensitive(False)

        filename = ''
        response = dialog.run()

        if response == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            dialog.destroy()

            if filename:
                pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                w, h = pixbuf.get_width(), pixbuf.get_height()
                if w != 64 or h != 64:
                    ErrorDialog(_("This image size isn't suitable for the logo.\nIt should be 64x64.")).launch()
                    return
                else:
                    proxy.exec_command('mkdir -p %s' % os.path.dirname(dest))
                    log.debug('Copy %s to %s' % (filename, dest))
                    proxy.exec_command('cp %s %s' % (filename, dest))

                    self.logo_image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename))
        elif response == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            proxy.exec_command('rm -rf %s' % dest)
            self.__setup_logo_image()
        else:
            dialog.destroy()
            return

    def on_background_button_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_('Choose a new background image'),
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_REVERT_TO_SAVED, gtk.RESPONSE_DELETE_EVENT,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name(_('All images'))
        filter.add_pattern('*.jpg')
        filter.add_pattern('*.png')
        dialog.set_current_folder('/usr/share/backgrounds')
        dialog.add_filter(filter)

        if module_check.get_codename() == 'karmic':
            orignal_background = '/usr/share/images/xsplash/bg_2560x1600.jpg'
        else:
            orignal_background = '/usr/share/backgrounds/warty-final-ubuntu.png'

        revert_button = dialog.action_area.get_children()[-1]
        if not proxy.is_exists(orignal_background):
            revert_button.set_sensitive(False)

        filename = ''
        response = dialog.run()

        if response == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            dialog.destroy()

            if filename:
                self.background_setting.set_value(user='gdm', value=filename)
                self.__setup_background_image()
        elif response == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            self.background_setting.set_value(user='gdm',
                                              value=orignal_background)
            self.__setup_background_image()
        else:
            dialog.destroy()
            return
