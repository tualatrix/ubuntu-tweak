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

from ubuntutweak import system
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.treeviews import get_local_path
from ubuntutweak.gui.containers import ListPack, GridPack
from ubuntutweak.policykit import PK_ACTION_TWEAK
from ubuntutweak.utils import theme
from ubuntutweak.settings.configsettings import SystemConfigSetting
from ubuntutweak.settings.gsettings import GSetting

log = logging.getLogger('LoginSettings')

class LoginSettings(TweakModule):
    __title__ = _('Login Settings')
    __desc__ = _('Control the appearance and behaviour of your login screen')
    __icon__ = 'gdm-setup'
    __policykit__ = PK_ACTION_TWEAK
    __category__ = 'startup'

    utext_allow_guest = _('Guest account:')
    utext_draw_grid = _('Draw grid:')
    utext_login_sound = _('Play login sound:')
    utext_gtk_theme = _('Gtk theme:')
    utext_icon_theme = _('Icon theme:')

    @classmethod
    def is_active(cls):
        return os.path.exists('/usr/sbin/lightdm')

    def __init__(self):
        TweakModule.__init__(self, 'loginsettings.ui')

        valid_themes = theme.get_valid_themes()
        valid_icon_themes = theme.get_valid_icon_themes()

        notes_label = Gtk.Label()
        notes_label.set_property('halign', Gtk.Align.START)
        notes_label.set_markup('<span size="smaller">%s</span>' % \
                _('Note: you may need to reboot to take effect'))
        notes_label._ut_left = 1

        self.login_box = GridPack(
                        WidgetFactory.create('Switch',
                            label=self.utext_allow_guest,
                            key='/etc/lightdm/lightdm.conf::SeatDefaults#allow-guest',
                            default=True,
                            backend='systemconfig'),
                        notes_label,
                        WidgetFactory.create('Switch',
                            label=self.utext_draw_grid,
                            key='50_unity-greeter.gschema.override::com.canonical.unity-greeter#draw-grid',
                            backend='systemconfig'),
                        WidgetFactory.create('Switch',
                            label=self.utext_login_sound,
                            key='50_unity-greeter.gschema.override::com.canonical.unity-greeter#play-ready-sound',
                            backend='systemconfig'),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_gtk_theme,
                            key='50_unity-greeter.gschema.override::com.canonical.unity-greeter#theme-name',
                            backend='systemconfig',
                            texts=valid_themes,
                            values=valid_themes),
                        WidgetFactory.create('ComboBox',
                            label=self.utext_icon_theme,
                            key='50_unity-greeter.gschema.override::com.canonical.unity-greeter#icon-theme-name',
                            backend='systemconfig',
                            texts=valid_icon_themes,
                            values=valid_icon_themes),
                        )

        self.login_box.set_sensitive(False)
        self.add_start(self.login_box, False, False, 0)

        if system.CODENAME != 'saucy':
            self.add_start(Gtk.Separator(), False, False, 6)

            self._setup_logo_image()
            self._setup_background_image()

            box = ListPack('', (self.main_vbox))
            self.add_start(box, False, False, 0)

    def _setup_logo_image(self):
        self._greeter_logo = SystemConfigSetting('50_unity-greeter.gschema.override::com.canonical.unity-greeter#logo', type=str)
        logo_path = self._greeter_logo.get_value()

        if logo_path:
            self.logo_image.set_from_file(logo_path)

    def _setup_background_image(self):
        self._greeter_background = SystemConfigSetting('50_unity-greeter.gschema.override::com.canonical.unity-greeter#background', type=str)
        background_path = self._greeter_background.get_value()

        log.debug("Setup the background file: %s" % background_path)

        if background_path:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(background_path)
                pixbuf = pixbuf.scale_simple(160, 120, GdkPixbuf.InterpType.NEAREST)
                self.background_image.set_from_pixbuf(pixbuf)
            except Exception, e:
                log.error("Loading background failed, message is %s" % e)

    def _get_desktop_background_path(self):
        return get_local_path(GSetting('org.gnome.desktop.background.picture-uri').get_value())

    def on_polkit_action(self, widget):
        self.main_vbox.set_sensitive(True)
        if hasattr(self, 'login_box'):
            self.login_box.set_sensitive(True)

    def on_logo_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_('Choose a new logo image'),
                                        action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_REVERT_TO_SAVED, Gtk.ResponseType.DELETE_EVENT,
                                                 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        filter = Gtk.FileFilter()
        filter.set_name(_('All images (*.PNG)'))
        filter.add_pattern('*.png')
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)
        self._set_preview_widget_for_dialog(dialog)

        orignal_logo = '/usr/share/unity-greeter/logo.png'

        filename = ''
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            dialog.destroy()

            if filename:
                self._greeter_logo.set_value(filename)
                self._setup_logo_image()
        elif response == Gtk.ResponseType.DELETE_EVENT:
            dialog.destroy()
            self._greeter_logo.set_value(orignal_logo)
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
        filter.add_pattern('*.JPG')
        filter.add_pattern('*.PNG')
        dialog.set_current_folder('/usr/share/backgrounds')
        dialog.add_filter(filter)
        self._set_preview_widget_for_dialog(dialog)

        orignal_background = '/usr/share/backgrounds/warty-final-ubuntu.png'
        filename = ''
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            log.debug("Get background file, the path is: %s" % filename)
            dialog.destroy()

            if filename:
                self._greeter_background.set_value(filename)

                self._setup_background_image()
        elif response == Gtk.ResponseType.DELETE_EVENT:
            dialog.destroy()
            self._greeter_background.set_value(orignal_background)
            self._setup_background_image()
        else:
            dialog.destroy()
            return

    def on_same_background_button_clicked(self, widget):
        log.debug('on_same_background_button_clicked')
        background_path = self._get_desktop_background_path()

        if background_path and \
                background_path != self._greeter_background.get_value():
            self._greeter_background.set_value(background_path)
            self._setup_background_image()
