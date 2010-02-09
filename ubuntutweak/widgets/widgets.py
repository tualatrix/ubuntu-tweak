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
import gobject
import time

from ubuntutweak.conf import GconfSetting, SystemGconfSetting
from ubuntutweak.policykit import PolkitButton, proxy

class GconfCheckButton(gtk.CheckButton):
    def __init__(self, label=None, key=None, default=None, tooltip=None):
        super(GconfCheckButton, self).__init__()
        self.__setting = GconfSetting(key=key, default=default, type=bool)

        self.set_label(label)
        self.set_active(self.__setting.get_value())
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.__setting.get_client().notify_add(key, self.value_changed)
        self.connect('toggled', self.button_toggled)

    def value_changed(self, client, id, entry, data=None):
        self.set_active(self.__setting.get_value())

    def button_toggled(self, widget, data=None):
        self.__setting.set_value(self.get_active())

class SystemGconfCheckButton(gtk.CheckButton):
    def __init__(self, label=None, key=None, default=None, tooltip=None):
        super(SystemGconfCheckButton, self).__init__()
        self.__setting = SystemGconfSetting(key, default)

        self.set_label(label)
        self.set_active(self.__setting.get_value())
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect('toggled', self.button_toggled)

    def button_toggled(self, widget):
        self.__setting.set_value(self.get_active())
        
class StrGconfCheckButton(GconfCheckButton):
    '''This class use to moniter the key with StringSetting, nothing else'''
    def __init__(self, **kwargs):
        super(StrGconfCheckButton, self).__init__(**kwargs)

    def button_toggled(self, widget, data = None):
        '''rewrite the toggled function, it do nothing with the setting'''
        pass

class GconfEntry(gtk.Entry):
    def __init__(self, key=None, default=None):
        gtk.Entry.__init__(self)
        self.__setting = GconfSetting(key=key, default=default, type=str)

        string = self.__setting.get_value()
        if string:
            self.set_text(string)
        else:
            self.set_text(_("Unset"))

    def is_changed(self):
        return self.get_string_value() != self.get_text()

    def get_string_value(self):
        return self.__setting.get_value()

    def connect_activate_signal(self):
        self.connect('activate', self.on_edit_finished_cb)

    def get_gsetting(self):
        return self.__setting

    def reset(self):
        self.set_text(self.get_string_value())

    def on_edit_finished_cb(self, widget):
        string = self.get_text()
        client = self.__setting.get_client()
        key = self.__setting.get_key()
        if string:
            client.set_string(key, self.get_text())
        else:
            client.unset(key)
            self.set_text(_("Unset"))

def GconfComboBox(key=None, texts=None, values=None):
    def value_changed_cb(widget, setting):
        text = widget.get_active_text()

        setting.get_client().set_value(setting.get_key(), \
                                setting.values[setting.texts.index(text)])

    combobox = gtk.combo_box_new_text()
    setting = GconfSetting(key=key)
    setting.texts = texts
    setting.values = values

    for text in texts:
        combobox.append_text(text)

    if setting.get_value() in values:
        combobox.set_active(values.index(setting.get_value()))
    combobox.connect("changed", value_changed_cb, setting)

    return combobox

class GconfScale(gtk.HScale):
    def __init__(self, key=None, min=None, max=None, digits=0):
        gtk.HScale.__init__(self)
        if digits > 0:
            self.__setting = GconfSetting(key=key, type=float)
        else:
            self.__setting = GconfSetting(key=key, type=int)
        
        self.set_range(min, max)
        self.set_digits(digits)
        self.set_value_pos(gtk.POS_RIGHT)
        self.connect("value-changed", self.on_value_changed) 
        self.set_value(self.__setting.get_value())

    def on_value_changed(self, widget, data=None):
        self.__setting.set_value(widget.get_value())

class GconfSpinButton(gtk.SpinButton):
    def __init__(self, key, min=0, max=0, step=0):
        self.__setting = GconfSetting(key=key, type=int)
        adjust = gtk.Adjustment(self.__setting.get_value(), min, max, step)

        gtk.SpinButton.__init__(self, adjust)
        self.connect('value-changed', self.on_value_changed) 

    def on_value_changed(self, widget):
        self.__setting.set_value(widget.get_value())

"""Popup and KeyGrabber come from ccsm"""
KeyModifier = ["Shift", "Control", "Mod1", "Mod2", "Mod3", "Mod4",
               "Mod5", "Alt", "Meta", "Super", "Hyper", "ModeSwitch"]

class Popup (gtk.Window):
    def __init__ (self, parent, text=None, child=None, decorated=True, mouse=False, modal=True):
        gtk.Window.__init__ (self, gtk.WINDOW_TOPLEVEL)
        self.set_type_hint (gtk.gdk.WINDOW_TYPE_HINT_UTILITY)
        self.set_position (mouse and gtk.WIN_POS_MOUSE or gtk.WIN_POS_CENTER_ALWAYS)
        if parent:
            self.set_transient_for (parent.get_toplevel ())
        self.set_modal (modal)
        self.set_decorated (decorated)
        self.set_title("")
        if text:
            label = gtk.Label (text)
            align = gtk.Alignment ()
            align.set_padding (20, 20, 20, 20)
            align.add (label)
            self.add (align)
        elif child:
            self.add (child)
        while gtk.events_pending ():
            gtk.main_iteration ()


    def destroy (self):
        gtk.Window.destroy (self)
        while gtk.events_pending ():
            gtk.main_iteration ()

class KeyGrabber(gtk.Button):

    __gsignals__ = {"changed" : (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            [gobject.TYPE_INT, gobject.TYPE_INT]),
                    "current-changed" : (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            [gobject.TYPE_INT, gobject.TYPE_INT])}

    key     = 0
    mods    = 0
    handler = None
    popup   = None

    label   = None

    def __init__ (self, parent = None, key = 0, mods = 0, label = None):
        '''Prepare widget'''
        super (KeyGrabber, self).__init__ ()

        self.main_window = parent
        self.key = key
        self.mods = mods

        self.label = label

        self.connect ("clicked", self.begin_key_grab)
        self.set_label ()

    def begin_key_grab (self, widget):
        self.add_events (gtk.gdk.KEY_PRESS_MASK)
        self.popup = Popup (self.main_window, _("Please press the new key combination"))
        self.popup.show_all()
        self.handler = self.popup.connect ("key-press-event",
                           self.on_key_press_event)
        while gtk.gdk.keyboard_grab (self.popup.window) != gtk.gdk.GRAB_SUCCESS:
            time.sleep (0.1)

    def end_key_grab (self):
        gtk.gdk.keyboard_ungrab (gtk.get_current_event_time ())
        self.popup.disconnect (self.handler)
        self.popup.destroy ()

    def on_key_press_event (self, widget, event):
        mods = event.state & gtk.accelerator_get_default_mod_mask ()

        if event.keyval in (gtk.keysyms.Escape, gtk.keysyms.Return) \
            and not mods:
            if event.keyval == gtk.keysyms.Escape:
                self.emit ("changed", self.key, self.mods)
            self.end_key_grab ()
            self.set_label ()
            return

        key = gtk.gdk.keyval_to_lower (event.keyval)
        if (key == gtk.keysyms.ISO_Left_Tab):
            key = gtk.keysyms.Tab

        if gtk.accelerator_valid (key, mods) \
            or (key == gtk.keysyms.Tab and mods):
            self.set_label (key, mods)
            self.end_key_grab ()
            self.key = key
            self.mods = mods
            self.emit ("changed", self.key, self.mods)
            return

        self.set_label (key, mods)

    def set_label (self, key = None, mods = None):
        if self.label:
            if key != None and mods != None:
                self.emit ("current-changed", key, mods)
            gtk.Button.set_label (self, self.label)
            return
        if key == None and mods == None:
            key = self.key
            mods = self.mods
        label = gtk.accelerator_name (key, mods)
        if not len (label):
            label = _("Disabled")
        gtk.Button.set_label (self, label)
