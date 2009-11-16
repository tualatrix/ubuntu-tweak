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
import gconf
import gobject

from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.consts import DATA_DIR
from ubuntutweak.widgets import ListPack, SinglePack
from ubuntutweak.widgets.dialogs import InfoDialog
from ubuntutweak.common.systeminfo import module_check
try:
    from ubuntutweak.package import package_worker, AptCheckButton
except:
    pass

def load_ccm():
    global ccm
    try:
        import ccm
    except:
        pass

load_ccm()

plugins = \
{
    'expo': _('Expo'),
    'scale': _('Show Windows'),
    'core': _('Show Desktop'),
    'widget': _('Widget'),
}

plugins_settings = \
{
    'expo': 'expo_edge',
    'scale': 'initiate_all_edge',
    'core': 'show_desktop_edge',
    'widget': 'toggle_edge',
}

class CompizSetting:
    if module_check.has_ccm() and module_check.has_right_compiz():
        import compizconfig as ccs
        context = ccs.Context()
    else:
        context = None

    @classmethod
    def update_context(cls):
        if module_check.has_ccm() and module_check.has_right_compiz():
            import compizconfig as ccs
            load_ccm()
            cls.context = ccs.Context()

    @classmethod
    def get_plugin(cls, name):
        try:
            plugin = cls.context.Plugins[name]
        except KeyError:
            return None
        else:
            return plugin

    @classmethod
    def set_plugin_active(cls, name, active):
        try:
            plugin = cls.context.Plugins[name]
            plugin.Enabled = int(active)
            cls.context.Write()
        except:
            pass

    @classmethod
    def get_plugin_active(cls, name):
        try:
            plugin = cls.context.Plugins[name]
            return bool(plugin.Enabled)
        except:
            return False

class OpacityMenu(gtk.CheckButton, CompizSetting):
    menu_match = 'Tooltip | Menu | PopupMenu | DropdownMenu'
    def __init__(self, label):
        gtk.CheckButton.__init__(self, label)

        if ccm.Version > '0.7.6':
            self.plugin = self.get_plugin('obs')
        else:
            self.plugin = self.get_plugin('core')
        if not self.plugin.Enabled:
            self.plugin.Enabled = 1
            self.context.Write()
        self.setting_matches = self.plugin.Screens[0]['opacity_matches']
        self.setting_values = self.plugin.Screens[0]['opacity_values']

        if self.menu_match in self.setting_matches.Value:
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget, data = None):
        if self.get_active():
            self.setting_matches.Value = [self.menu_match]
            self.setting_values.Value = [90]
        else:
            index = self.setting_matches.Value.index(self.menu_match)
            self.setting_matches.Value = []
            self.setting_values.Value = []
        self.context.Write()

class WobblyMenu(gtk.CheckButton, CompizSetting):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = self.context.Plugins['wobbly']
        self.setting = self.plugin.Screens[0]['map_window_match']

        if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget, data = None):
        if self.get_active():
            conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
            conflict = ccm.PluginConflict(self.plugin, conflicts)
            if conflict.Resolve():
                self.mediator.snap.set_active(False)
                if not self.plugin.Enabled: self.plugin.Enabled = True
                self.setting.Reset()
        else:
            self.setting.Value = ""

        self.context.Write()

        if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
            self.set_active(True)
        else:
            self.set_active(False)

class WobblyWindow(gtk.CheckButton, CompizSetting):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = self.context.Plugins['wobbly']
        self.setting = self.plugin.Screens[0]['move_window_match']
        
        if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget, data = None):
        if self.get_active():
            conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
            conflict = ccm.PluginConflict(self.plugin, conflicts)
            if conflict.Resolve():
                self.mediator.snap.set_active(False)
                if not self.plugin.Enabled: self.plugin.Enabled = True
                self.setting.Reset()
        else:
            self.setting.Value = ""

        self.context.Write()

        if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
            self.set_active(True)
        else:
            self.set_active(False)

class SnapWindow(gtk.CheckButton, CompizSetting):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = self.context.Plugins['snap']

        self.set_active(self.plugin.Enabled)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget, data = None):
        if self.get_active():
            conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
            conflict = ccm.PluginConflict(self.plugin, conflicts)
            if conflict.Resolve():
                self.plugin.Enabled = True
                self.mediator.wobbly_w.set_active(False)
                self.mediator.wobbly_m.set_active(False)
        else:
            self.plugin.Enabled = False

        self.context.Write()

        self.set_active(self.plugin.Enabled)

class Compiz(TweakModule, CompizSetting):
    __title__ = _('Compiz Settings')
    __desc__ = _('Setting with your amazing eye-candy desktop')
    __icon__ = ['compiz', 'wmtweaks']
    __category__ = 'desktop'

    def __init__(self):
        TweakModule.__init__(self)

        self.create_interface()

    def create_interface(self):
        if module_check.has_apt() and package_worker.get_cache():
            self.package_worker = package_worker

            self.advanced_settings = AptCheckButton(_("Install Advanced Desktop Effects Settings Manager"),
                    'compizconfig-settings-manager')
            self.advanced_settings.connect('toggled', self.colleague_changed)
            self.simple_settings = AptCheckButton(_("Install Simple Desktop Effects Settings manager"),
                    'simple-ccsm')
            self.simple_settings.connect('toggled', self.colleague_changed)
            self.screenlets = AptCheckButton(_("Install Screenlets Widget Application"),
                    'screenlets')
            self.screenlets.connect('toggled', self.colleague_changed)

        if self.context:
            hbox = gtk.HBox(False, 0)
            hbox.pack_start(self.create_edge_setting(), True, False, 0)
            edge_setting = SinglePack(_('Edge Settings'), hbox)
            self.add_start(edge_setting, False, False, 0)

            self.snap = SnapWindow(_("Enable snapping windows"), self)
            self.wobbly_w = WobblyWindow(_("Enable wobbly windows"), self);

            box = ListPack(_("Window Effects"), (self.snap, self.wobbly_w))
            self.add_start(box, False, False, 0)

            button1 = OpacityMenu(_("Enable transparent menus"))
            self.wobbly_m = WobblyMenu(_("Enable wobbly menus"), self)

            box = ListPack(_("Menu Effects"), (button1, self.wobbly_m))
            self.add_start(box, False, False, 0)

            if module_check.has_apt() and package_worker.get_cache():
                box = ListPack(_("Useful Extensions"), (
                    self.simple_settings,
                    self.screenlets,
                ))

                self.button = gtk.Button(stock = gtk.STOCK_APPLY)
                self.button.connect("clicked", self.on_apply_clicked, box)
                self.button.set_sensitive(False)
                hbox = gtk.HBox(False, 0)
                hbox.pack_end(self.button, False, False, 0)

                box.vbox.pack_start(hbox, False, False, 0)

                self.add_start(box, False, False, 0)
        else:
            box = ListPack(_("Prerequisite Conditions"), (
                self.advanced_settings,
            ))

            self.button = gtk.Button(stock = gtk.STOCK_APPLY)
            self.button.connect("clicked", self.on_apply_clicked, box)
            self.button.set_sensitive(False)
            hbox = gtk.HBox(False, 0)
            hbox.pack_end(self.button, False, False, 0)

            box.vbox.pack_start(hbox, False, False, 0)
            self.add_start(box, False, False, 0)

    def combo_box_changed_cb(self, widget, edge):
        """If the previous setting is none, then select the add edge"""
        if widget.previous:
            self.change_edge(widget, edge)
        else:
            self.add_edge(widget, edge)

    def change_edge(self, widget, edge):
        previous = widget.previous

        plugin = self.context.Plugins[previous]
        setting = plugin.Display[plugins_settings[previous]]
        setting.Value = ""
        self.context.Write()

        self.add_edge(widget, edge)    

    def add_edge(self, widget, edge):
        text = widget.get_active_text()
        for k, v in plugins.items():
            if v == text:
                text = k
                break

        if text == '-':
            widget.previous = None
        else:
            plugin = self.context.Plugins[text]
            setting = plugin.Display[plugins_settings[text]]
            setting.Value = edge
            self.context.Write()
            widget.previous = text

    def create_edge_combo_box(self, edge):
        global plugins_settings, plugins
        combobox = gtk.combo_box_new_text()
        combobox.previous = None

        enable = False
        count = 0
        for k, v in plugins_settings.items():
            if self.context.Plugins.has_key(k):
                plugin = self.context.Plugins[k]
                combobox.append_text(plugins[k])
                if not plugin.Enabled:
                    plugin.Enabled = True
                    self.context.Write()
                setting = plugin.Display[v]
                if setting.Value == edge:
                    combobox.previous = k
                    combobox.set_active(count)
                    enable = True
                count = count + 1
            else:
                plugins.pop(k)
                plugins_settings.pop(k)

        combobox.append_text("-")
        if not enable:
            combobox.set_active(count)
        combobox.connect("changed", self.combo_box_changed_cb, edge)

        return combobox

    def create_edge_setting(self):
        hbox = gtk.HBox(False, 0)

        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, False, False, 0)

        combobox = self.create_edge_combo_box("TopLeft")
        vbox.pack_start(combobox, False, False, 0)

        combobox = self.create_edge_combo_box("BottomLeft")
        vbox.pack_end(combobox, False, False, 0)

        client = gconf.client_get_default()
        wallpaper = client.get_string("/desktop/gnome/background/picture_filename")

        system_wallpaper = os.path.join(DATA_DIR, "pixmaps/ubuntu-tweak.png")
        if wallpaper:
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(wallpaper, 160, 100)
            except gobject.GError:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(system_wallpaper, 160, 100)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(system_wallpaper, 160, 100)
        image = gtk.image_new_from_pixbuf(pixbuf)
        hbox.pack_start(image, False, False, 0)
        
        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, False, False, 0)
        
        combobox = self.create_edge_combo_box("TopRight")
        vbox.pack_start(combobox, False, False, 0)

        combobox = self.create_edge_combo_box("BottomRight")
        vbox.pack_end(combobox, False, False, 0)

        return hbox

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

        CompizSetting.update_context()
        self.remove_all_children()
        self.create_interface()

        self.show_all()

    def colleague_changed(self, widget):
        if self.advanced_settings.get_state() != self.advanced_settings.get_active() or\
                self.simple_settings.get_state() != self.simple_settings.get_active() or\
                self.screenlets.get_state() != self.screenlets.get_active():
                    self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)
