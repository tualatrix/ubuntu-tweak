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
import logging

from gi.repository import Gtk, GdkPixbuf

from ubuntutweak.factory import WidgetFactory
from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.gui.dialogs import ErrorDialog, ServerErrorDialog
from ubuntutweak.policykit import PK_ACTION_TWEAK
from ubuntutweak.policykit.widgets import PolkitButton
from ubuntutweak.policykit.dbusproxy import proxy

from ubuntutweak.settings.gconfsettings import UserGconfSetting

log = logging.getLogger('LoginSettings')

class LoginSettings(TweakModule):
    __title__ = _('Login Settings')
    __desc__ = _('Control the appearance and behaviour of your login screen')
    __icon__ = 'gdm-setup'
    __category__ = 'startup'

    def __init__(self):
        TweakModule.__init__(self, 'loginsettings.ui')

        log.debug('Start to build "Session Options"')
        self.options_box = ListPack(_("Login Options"), (
                    WidgetFactory.create("UserCheckButton",
                                         user='gdm',
                                         label=_("Disable user list in GDM"),
                                         enable_reset=True,
                                         key="/apps/gdm/simple-greeter/disable_user_list"),
                    WidgetFactory.create("UserCheckButton",
                                         user='gdm',
                                         label=_("Play sound at login"),
                                         enable_reset=True,
                                         key="/desktop/gnome/sound/event_sounds"),
                    WidgetFactory.create("UserCheckButton",
                                         user='gdm',
                                         label=_("Disable showing the restart button"),
                                         enable_reset=True,
                                         key="/apps/gdm/simple-greeter/disable_restart_buttons"),
            ))
        for item in self.options_box.items:
            log.debug('Set widget %s to sensitive False', item)
            item.set_sensitive(False)
        log.debug('Build "Session Options" finished')

        self.add_start(self.options_box, False, False, 0)

        self.icon_setting = UserGconfSetting('/apps/gdm/simple-greeter/logo_icon_name')
        self.icon_theme_setting = UserGconfSetting('/desktop/gnome/interface/icon_theme')
        self._setup_logo_image()
        self._setup_background_image()
        self.vbox1.unparent()
        self.vbox1.set_sensitive(False)

        box = ListPack(_('Login Theme'), (self.vbox1))
        self.add_start(box, False, False, 0)

        hbox = Gtk.HBox(spacing=12)
        polkit_button = PolkitButton(PK_ACTION_TWEAK)
        polkit_button.connect('authenticated', self.on_polkit_action)
        hbox.pack_end(polkit_button, False, False, 0)
        self.add_start(hbox, False, False, 0)

    def _setup_logo_image(self):
        icon_name = self.icon_setting.get_value(user='gdm')
        log.info('Get icon_name from user: gdm, icon name: %s' % icon_name)

        path = os.path.expanduser('~gdm/.icons/%s/apps/64/%s' % (
                                    self.icon_theme_setting.get_value(user='gdm'),
                                    self.icon_setting.get_value(user='gdm')))
        EXIST = False
        FORMAT = ''
        if proxy.is_exists(path + '.png'):
            path = path + '.png'
            EXIST = True
            FORMAT = '.png'
        elif proxy.is_exists(path + '.svg'):
            path = path + '.svg'
            EXIST = True
            FORMAT = '.svg'

        if EXIST:
            log.info("The icon path is: %s" % path)
            path = proxy.get_as_tempfile(path, os.getuid())
            log.debug('Custom log is exits, the tempfile is %s' % path)
            if FORMAT == '.svg':
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
                pixbuf = pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)
                self.logo_image.set_from_pixbuf(pixbuf)
            else:
                self.logo_image.set_from_file(path)
        else:
            icontheme = Gtk.IconTheme()
            icontheme.set_custom_theme(self.icon_theme_setting.get_value(user='gdm'))
            try:
                self.logo_image.set_from_pixbuf(icontheme.load_icon(icon_name, 64, 0))
            except:
                pass

    def _setup_background_image(self):
        self.background_setting = UserGconfSetting('/desktop/gnome/background/picture_filename')
        background_path = self.background_setting.get_value(user='gdm')
        log.debug("Setup the background file: %s" % background_path)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(background_path)
            pixbuf = pixbuf.scale_simple(160, 120, GdkPixbuf.InterpType.NEAREST)
            self.background_image.set_from_pixbuf(pixbuf)
        except Exception, e:
            log.error("Loading background failed, message is %s" % e)

    def on_polkit_action(self, widget):
        for item in self.options_box.items:
            item.set_sensitive(True)
        self.vbox1.set_sensitive(True)

    def on_logo_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Choose a new logo image'),
                                        action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_REVERT_TO_SAVED, Gtk.ResponseType.DELETE_EVENT,
                                                 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_("PNG images with 64x64 size or SVG images"))
        filter.add_pattern('*.png')
        filter.add_pattern('*.svg')
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)
        self._set_preview_widget_for_dialog(dialog)

        dest = os.path.expanduser('~gdm/.icons/%s/apps/64/%s' % (
                                    self.icon_theme_setting.get_value(user='gdm'),
                                    self.icon_setting.get_value(user='gdm')))

        revert_button = dialog.get_action_area().get_children()[-1]

        HAVE_ICON = proxy.is_exists(dest + '.png') or proxy.is_exists(dest + '.svg')

        if not HAVE_ICON:
            revert_button.set_sensitive(False)

        filename = ''
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            dialog.destroy()

            if filename:
                ext = os.path.splitext(filename)[1]
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
                w, h = pixbuf.get_width(), pixbuf.get_height()

                if ext == '.png' and (w != 64 or h != 64):
                    ErrorDialog(_("This image size isn't suitable for the logo.\nIt should be 64x64.")).launch()
                    return
                else:
                    dest = dest + ext
                    log.debug('Copy %s to %s' % (filename, dest))
                    proxy.set_login_logo(filename, dest)

                    if ext == '.svg':
                        pixbuf = pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)

                    self.logo_image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(filename))
        elif response == Gtk.ResponseType.DELETE_EVENT:
            dialog.destroy()
            proxy.unset_login_logo(dest)
            self._setup_logo_image()
        else:
            dialog.destroy()
            return

    def _set_preview_widget_for_dialog(self, dialog):
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', self.on_update_preview, preview)

    def on_update_preview(self, dialog, preview):
        filename = dialog.get_preview_filename()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
        except Exception, e:
            log.error(e)
            pixbuf = None

        if pixbuf:
            preview.set_from_pixbuf(pixbuf)

            dialog.set_preview_widget_active(True)
        else:
            dialog.set_preview_widget_active(False)

    def on_background_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Choose a new background image'),
                                        action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_REVERT_TO_SAVED, Gtk.ResponseType.DELETE_EVENT,
                                                 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_('All images'))
        filter.add_pattern('*.jpg')
        filter.add_pattern('*.png')
        dialog.set_current_folder('/usr/share/backgrounds')
        dialog.add_filter(filter)
        self._set_preview_widget_for_dialog(dialog)

        orignal_background = '/usr/share/backgrounds/warty-final-ubuntu.png'

        revert_button = dialog.get_action_area().get_children()[-1]

        filename = ''
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            log.debug("Get background file, the path is: %s" % filename)
            dialog.destroy()

            if filename:
                self.background_setting.set_value(user='gdm', value=filename)
                self._setup_background_image()
        elif response == Gtk.ResponseType.DELETE_EVENT:
            dialog.destroy()
            self.background_setting.set_value(user='gdm',
                                              value=orignal_background)
            self._setup_background_image()
        else:
            dialog.destroy()
            return
