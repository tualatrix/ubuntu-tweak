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
import os
import gtk
import gconf
import gobject
import logging

from ubuntutweak import system
from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.consts import DATA_DIR
from ubuntutweak.widgets import ListPack, SinglePack
from ubuntutweak.widgets.dialogs import InfoDialog

log = logging.getLogger('compiz')

try:
    from ubuntutweak.common.package import PACKAGE_WORKER, AptCheckButton
except:
    pass

def load_ccm():
    global ccm
    try:
        import ccm
    except:
        log.error('No ccm available')
        pass

load_ccm()

plugins = \
{
    'expo': _('Show Workspaces'),
    'scale': _('Show Windows'),
    'core': _('Show Desktop'),
    'widget': _('Show Widgets'),
}

plugins_settings = \
{
    'expo': 'expo_edge',
    'scale': 'initiate_all_edge',
    'core': 'show_desktop_edge',
    'widget': 'toggle_edge',
}

class CompizPlugin:
    if system.has_ccm() and system.has_right_compiz() == 1:
        import compizconfig as ccs
        context = ccs.Context()
    elif system.has_right_compiz() == 0:
        context = None
        error = False

    @classmethod
    def update_context(cls):
        if system.has_ccm() and system.has_right_compiz():
            import compizconfig as ccs
            load_ccm()
            cls.context = ccs.Context()

    def __init__(self, name):
        self.__plugin = self.context.Plugins[name]

    def set_enabled(self, bool):
        self.__plugin.Enabled = int(bool)
        self.save()

    def get_enabled(self):
        return self.__plugin.Enabled

    def save(self):
        self.context.Write()

    def resolve_conflict(self):
        conflicts = self.get_enabled() and self.__plugin.DisableConflicts \
                                       or self.__plugin.EnableConflicts
        conflict = ccm.PluginConflict(self.__plugin, conflicts)
        return conflict.Resolve()

    @classmethod
    def is_available(cls, name, setting):
        if ccm.Version >= '0.9.2':
            target = 'Screen'
        else:
            target = 'Display'

        return cls.context.Plugins.has_key(name) and \
                getattr(cls.context.Plugins[name], target).has_key(setting)

    def create_setting(self, key, target):
        settings = (self.__plugin, target)

        #TODO remove it in the future
        if ccm.Version >= '0.9.2':
            target = 'Screen'
        else:
            if not target:
                target = 'Display'

        settings = getattr(self.__plugin, target)

        if type(settings) == list:
            return settings[0][key]
        else:
            return settings[key]

class CompizSetting:
    def __init__(self, plugin, key, target=''):
        self.__plugin = plugin
        self.__setting = self.__plugin.create_setting(key, target)

    def set_value(self, value):
        self.__setting.Value = value
        self.__plugin.save()

    def get_value(self):
        return self.__setting.Value

    def is_default_and_enabled(self):
        return self.__setting.Value == self.__setting.DefaultValue and \
                self.__plugin.get_enabled()

    def reset(self):
        self.__setting.Reset()
        self.__plugin.save()

class OpacityMenu(gtk.CheckButton):
    menu_match = 'Tooltip | Menu | PopupMenu | DropdownMenu'

    def __init__(self, label):
        gtk.CheckButton.__init__(self, label)

        self.plugin = CompizPlugin('obs')

        if not self.plugin.get_enabled():
            self.plugin.set_enabled(True)
        self.setting_matches = CompizSetting(self.plugin, 'opacity_matches', target='Screens')
        self.setting_values = CompizSetting(self.plugin, 'opacity_values', target='Screens')

        if self.menu_match in self.setting_matches.get_value():
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            self.setting_matches.set_value([self.menu_match])
            self.setting_values.set_value([90])
        else:
            self.setting_matches.set_value([])
            self.setting_values.set_value([])

class WobblyMenu(gtk.CheckButton):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = CompizPlugin('wobbly')
        self.map_window_setting = CompizSetting(self.plugin, 'map_window_match', target='Screens')
        self.map_effect_setting = CompizSetting(self.plugin, 'map_effect', target='Screens')

        if self.map_window_setting.is_default_and_enabled() and self.map_effect_setting.get_value() == 1:
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.mediator.snap.set_active(False)
                self.plugin.set_enabled(True)
                self.map_window_setting.reset()
                self.map_effect_setting.set_value(1)
        else:
            self.map_window_setting.set_value("")
            self.map_effect_setting.set_value(0)

        if self.map_window_setting.is_default_and_enabled():
            self.set_active(True)
        else:
            self.set_active(False)

class WobblyWindow(gtk.CheckButton):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = CompizPlugin('wobbly')
        self.setting = CompizSetting(self.plugin, 'move_window_match', target='Screens')
        
        if self.setting.is_default_and_enabled():
            self.set_active(True)

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.mediator.snap.set_active(False)
                self.plugin.set_enabled(True)
                self.setting.reset()
        else:
            self.setting.set_value("")

        if self.setting.is_default_and_enabled():
            self.set_active(True)
        else:
            self.set_active(False)

class SnapWindow(gtk.CheckButton):
    def __init__(self, label, mediator):
        gtk.CheckButton.__init__(self, label)

        self.mediator = mediator
        self.plugin = CompizPlugin('snap')

        self.set_active(self.plugin.get_enabled())

        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            if self.plugin.resolve_conflict():
                self.plugin.set_enabled(True)
                self.mediator.wobbly_w.set_active(False)
                self.mediator.wobbly_m.set_active(False)
        else:
            self.plugin.set_enabled(False)

class ViewpointSwitcher(gtk.CheckButton):
    def __init__(self, label):
        gtk.CheckButton.__init__(self, label)

        self.plugin = CompizPlugin('vpswitch')
        self.left_button_setting = CompizSetting(self.plugin, 'left_button')
        self.right_button_setting = CompizSetting(self.plugin, 'right_button')

        self.set_active(self.__get_setting_enabled())
        self.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget):
        if self.get_active():
            log.debug("The viewport button is enabled")
            if self.plugin.resolve_conflict():
                self.plugin.set_enabled(True)
                self.left_button_setting.set_value('Button4')
                self.right_button_setting.set_value('Button5')
        else:
            log.debug("The viewport button is disabled")
            self.plugin.set_enabled(False)

    def __get_setting_enabled(self):
        if self.plugin.get_enabled() and self.left_button_setting.get_value() == 'Button4' \
                and self.right_button_setting.get_value() == 'Button5':
                    return True
        else:
            return False

class Compiz(TweakModule):
    __title__ = _('Compiz Settings')
    __desc__ = _('Settings for some amazing desktop eye-candy')
    __icon__ = ['compiz', 'wmtweaks']
    __category__ = 'desktop'
    __desktop__ = 'gnome'

    def __init__(self):
        TweakModule.__init__(self)

        self.create_interface()

    def create_interface(self):
        if system.has_apt() and PACKAGE_WORKER.get_cache():
            self.PACKAGE_WORKER = PACKAGE_WORKER

            self.advanced_settings = AptCheckButton(_("Install Advanced Desktop Effects Settings Manager"),
                    'compizconfig-settings-manager')
            self.advanced_settings.connect('toggled', self.colleague_changed)
            self.simple_settings = AptCheckButton(_("Install Simple Desktop Effects Settings Manager"),
                    'simple-ccsm')
            self.simple_settings.connect('toggled', self.colleague_changed)
            self.screenlets = AptCheckButton(_("Install Screenlets Widget Application"),
                    'screenlets')
            self.screenlets.connect('toggled', self.colleague_changed)

        if CompizPlugin.context:
            hbox = gtk.HBox(False, 0)
            hbox.pack_start(self.create_edge_setting(), True, False, 0)
            edge_setting = SinglePack(_(' Workspace Edge Settings'), hbox)
            self.add_start(edge_setting, False, False, 0)

            self.snap = SnapWindow(_("Enable snapping windows"), self)
            self.wobbly_w = WobblyWindow(_("Enable wobbly windows"), self);
            self.viewport = ViewpointSwitcher(_('Enable workspace switching with mouse wheel'))

            box = ListPack(_("Desktop Effects"), (self.snap, self.wobbly_w, self.viewport))
            self.add_start(box, False, False, 0)

            button1 = OpacityMenu(_("Enable transparent menus"))
            self.wobbly_m = WobblyMenu(_("Enable wobbly menus"), self)

            box = ListPack(_("Menu Effects"), (button1, self.wobbly_m))
            self.add_start(box, False, False, 0)

            if system.has_apt() and PACKAGE_WORKER.get_cache():
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
        elif CompizSetting.context == None:
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
        """If the current setting is none, then select the add edge"""
        current = widget.current
        text = widget.get_active_text()
        for k, v in plugins.items():
            if v == text:
                text = k
                break

        log.debug("The current value: %s and next value: %s" % (current, text))

        if current:
            # Clean old data
            log.debug("Clean old data from the same box")
            self.set_data(current, None)
            CompizSetting(CompizPlugin(current), plugins_settings[current]).set_value('')

        if self.get_data(text):
            log.debug("Clean old data from the other box")
            current_combox = self.get_data(text)

            if current_combox and current_combox != widget:
                # Set the current value holder to -, and set the current value to None
                current_combox.handler_block_by_func(self.combo_box_changed_cb)
                current_combox.current = None
                self.set_data(text, None)
                current_combox.set_active(self.get_data('max_index'))
                current_combox.handler_unblock_by_func(self.combo_box_changed_cb)

            log.debug("Clean old value, set %s to None" % text)

        if text == '-':
            self.set_data(widget.current, None)
            widget.current = None
        else:
            plugin = CompizPlugin(text)
            plugin.set_enabled(True)
            setting = CompizSetting(plugin, plugins_settings[text])
            setting.set_value(edge)
            widget.current = text
            self.set_data(text, widget)
            log.debug("set the current %s" % text)

    def create_edge_combo_box(self, edge):
        global plugins_settings, plugins
        combobox = gtk.combo_box_new_text()
        combobox.current = None

        enable = False
        count = 0
        for k, v in plugins_settings.items():
            if CompizPlugin.is_available(k, v):
                plugin = CompizPlugin(k)
                combobox.append_text(plugins[k])
                if CompizSetting(plugin, v).get_value() == edge:
                    combobox.current = k
                    combobox.set_active(count)
                    enable = True
                    self.set_data(k, combobox)
                    log.info("The %s is holding %s" % (edge, k))
                count = count + 1
            else:
                plugins.pop(k)
                plugins_settings.pop(k)

        combobox.append_text("-")
        if not enable:
            combobox.set_active(count)
        self.set_data('max_index', count)
        combobox.connect("changed", self.combo_box_changed_cb, edge)

        return combobox

    def create_edge_setting(self):
        hbox = gtk.HBox(False, 0)

        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, False, False, 0)

        self.TopLeft = self.create_edge_combo_box("TopLeft")
        vbox.pack_start(self.TopLeft, False, False, 0)

        self.BottomLeft = self.create_edge_combo_box("BottomLeft")
        vbox.pack_end(self.BottomLeft, False, False, 0)

        client = gconf.client_get_default()
        wallpaper = client.get_string("/desktop/gnome/background/picture_filename")

        system_wallpaper = os.path.join(DATA_DIR, "pixmaps/splash.png")
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
        
        self.TopRight = self.create_edge_combo_box("TopRight")
        vbox.pack_start(self.TopRight, False, False, 0)

        self.BottomRight = self.create_edge_combo_box("BottomRight")
        vbox.pack_end(self.BottomRight, False, False, 0)

        return hbox

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

        CompizPlugin.update_context()
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
