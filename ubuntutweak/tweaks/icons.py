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

from ubuntutweak import system
from gi.repository import GObject, Gtk

from ubuntutweak.gui.containers import GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

computer_icon = {
    "label": _('Show "Computer" icon'),
    "visible_key": "org.gnome.nautilus.desktop.computer-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.computer-icon-name",
    "icon_name": "gnome-fs-client"
}

home_icon = {
    "label": _('Show "Home Folder" icon'),
    "visible_key": "org.gnome.nautilus.desktop.home-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.home-icon-name",
    "icon_name": "gnome-fs-home"
}

trash_icon = {
    "label": _('Show "Trash" icon'),
    "visible_key": "org.gnome.nautilus.desktop.trash-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.trash-icon-name",
    "icon_name": "gnome-fs-trash-empty"
}

network_icon = {
    "label": _('Show "Network Servers" icon'),
    "visible_key": "org.gnome.nautilus.desktop.network-icon-visible",
    "name_key": "org.gnome.nautilus.desktop.network-icon-name",
    "icon_name": "network-workgroup"
}

if system.CODENAME == 'saucy':
    desktop_icons = (home_icon, trash_icon, network_icon)
else:
    desktop_icons = (computer_icon, home_icon, trash_icon, network_icon)

class DesktopIcon(Gtk.VBox):
    def __init__(self, item):
        GObject.GObject.__init__(self)

        self.show_button = WidgetFactory.create("CheckButton",
                                                label=item["label"],
                                                key=item["visible_key"],
                                                backend="gsettings")
        self.show_button.connect('toggled', self.on_show_button_changed)
        self.pack_start(self.show_button, False, False, 0)

        self.show_hbox = Gtk.HBox(spacing=12)
        self.pack_start(self.show_hbox, False, False, 0)

        if not self.show_button.get_active():
            self.show_hbox.set_sensitive(False)

        icon = Gtk.Image.new_from_icon_name(item["icon_name"], Gtk.IconSize.DIALOG)
        self.show_hbox.pack_start(icon, False, False, 0)

        self.rename_button = WidgetFactory.create("StringCheckButton",
                                                  label=_('Rename'),
                                                  key=item["name_key"],
                                                  backend="gsettings")
        self.rename_button.connect('toggled', self.on_show_button_changed)
        vbox = Gtk.VBox(spacing=6)
        self.show_hbox.pack_start(vbox, False, False, 0)
        vbox.pack_start(self.rename_button, False, False, 0)

        self.entry = WidgetFactory.create("Entry", key=item["name_key"], backend="gsettings")
        self.entry.connect('insert-at-cursor', self.on_entry_focus_out)
        if not self.rename_button.get_active():
            self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, False, False, 0)

    def on_entry_focus_out(self, widget, event):
        self.entry.get_setting().set_value(self.entry.get_text())

    def on_show_button_changed(self, widget):
        self.show_hbox.set_sensitive(self.show_button.get_active())
        active = self.rename_button.get_active()

        if active:
            self.entry.set_sensitive(True)
            self.entry.grab_focus()
        else:
            self.entry.set_sensitive(False)
            self.entry.get_setting().unset()
            self.entry.set_text('')


class Icons(TweakModule):
    __title__ = _('Desktop Icons')
    __desc__ = _("Rename and toggle visibilty of desktop icons")
    __icon__ = 'preferences-desktop-wallpaper'
    __category__ = 'desktop'
    __desktop__ = ['ubuntu', 'ubuntu-2d', 'gnome', 'gnome-classic', 'gnome-shell', 'gnome-fallback', 'gnome-fallback-compiz']

    utext_show_icon = _("Show desktop icons:")
    utext_mount_volume = _("Show mounted volumes")
    utext_home_folder = _('Show contents of "Home Folder"')

    def __init__(self):
        TweakModule.__init__(self)

        show_label, show_switch = WidgetFactory.create("Switch",
                                                label=self.utext_show_icon,
                                                key="org.gnome.desktop.background.show-desktop-icons",
                                                backend="gsettings")

        setting_list = []
        show_switch.connect('notify::active', self.on_show_button_changed, setting_list)

        for item in desktop_icons:
            setting_list.append(DesktopIcon(item))

        volumes_button = WidgetFactory.create("CheckButton",
                                      label=self.utext_mount_volume,
                                      key="org.gnome.nautilus.desktop.volumes-visible",
                                      backend="gsettings")
        setting_list.append(volumes_button)

        if system.CODENAME != 'saucy':
            home_contents_button = WidgetFactory.create("CheckButton",
                                          label=self.utext_home_folder,
                                          key="org.gnome.nautilus.preferences.desktop-is-home-dir",
                                          backend="gsettings")
            setting_list.append(home_contents_button)

        notes_label = Gtk.Label()
        notes_label.set_property('halign', Gtk.Align.START)
        notes_label.set_markup('<span size="smaller">%s</span>' % \
                _('Note: switch off this option will make the desktop unclickable'))
        notes_label._ut_left = 1

        grid_box = GridPack((show_label, show_switch),
                            notes_label,
                            *setting_list)
        self.add_start(grid_box)
        self.on_show_button_changed(show_switch, None, setting_list)

    def on_show_button_changed(self, widget, value, setting_list):
        for item in setting_list:
            item.set_sensitive(widget.get_active())
