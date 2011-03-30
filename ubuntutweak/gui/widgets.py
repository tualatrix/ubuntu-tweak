import time

import gobject
from gi.repository import Gtk, Gdk, GConf

from ubuntutweak.settings.gconfsettings import GconfSetting


class CheckButton(Gtk.CheckButton):
    def __init__(self, label=None, key=None,
                 default=None, tooltip=None, backend=GConf):
        gobject.GObject.__init__(self, label=label)
        if backend == GConf:
            self.setting = GconfSetting(key=key, default=default, type=bool)
        else:
            #TODO Gio
            pass

        self.set_active(self.setting.get_value())
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.setting.connect_notify(self.on_value_changed)
        self.connect('toggled', self.on_button_toggled)

    def on_value_changed(self, client, id, entry, data):
        self.set_active(self.setting.get_value())

    def on_button_toggled(self, widget):
        self.setting.set_value(self.get_active())


class ResetButton(Gtk.Button):
    def __init__(self, key, backend=GConf):
        gobject.GObject.__init__(self)

        if backend == GConf:
            self.setting = GconfSetting(key=key, type=bool)
        else:
            #TODO Gio
            pass

        self.set_property('image', 
                          Gtk.Image.new_from_stock(Gtk.STOCK_REVERT_TO_SAVED, Gtk.IconSize.MENU))

        self.set_tooltip_text(_('Reset setting to default value: %s') % self.get_default_value())

    def get_default_value(self):
        return self.setting.get_schema_value()


class StringCheckButton(CheckButton):
    '''This class use to moniter the key with StringSetting, nothing else'''
    def __init__(self, **kwargs):
        CheckButton.__init__(self, **kwargs)

    def on_button_toggled(self, widget):
        '''rewrite the toggled function, it do nothing with the setting'''
        pass


class Entry(Gtk.Entry):
    def __init__(self, key=None, default=None, backend=GConf):
        gobject.GObject.__init__(self)

        if backend == GConf:
            self.setting = GconfSetting(key=key, default=default, type=str)
        else:
            #TODO Gio
            pass

        string = self.setting.get_value()
        if string:
            self.set_text(string)
        else:
            self.set_text(_("Unset"))

    def is_changed(self):
        return self.setting.get_value() != self.get_text()

    def connect_activate_signal(self):
        self.connect('activate', self.on_edit_finished_cb)

    def get_gsetting(self):
        return self.setting

    def on_edit_finished_cb(self, widget):
        if self.get_text():
            self.setting.set_value(self.get_text())
        else:
            self.setting.client.unset(self.setting.key)
            self.set_text(_("Unset"))


class SpinButton(Gtk.SpinButton):
    def __init__(self, key, min=0, max=0, step=0, backend=GConf):
        if backend == GConf:
            self.setting = GconfSetting(key=key, type=int)
        else:
            #TODO Gio
            pass

        adjust = Gtk.Adjustment(self.setting.get_value(), min, max, step)
        gobject.GObject.__init__(self, adjustment=adjust)
        self.connect('value-changed', self.on_value_changed)

    def on_value_changed(self, widget):
        self.setting.set_value(widget.get_value())


"""Popup and KeyGrabber come from ccsm"""
KeyModifier = ["Shift", "Control", "Mod1", "Mod2", "Mod3", "Mod4",
               "Mod5", "Alt", "Meta", "Super", "Hyper", "ModeSwitch"]


class Popup(Gtk.Window):
    def __init__(self, parent, text=None, child=None,
                 decorated=True, mouse=False, modal=True):
        gobject.GObject.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_position(mouse and Gtk.WindowPosition.MOUSE or
                          Gtk.WindowPosition.CENTER_ALWAYS)

        if parent:
            self.set_transient_for(parent.get_toplevel())

        self.set_modal(modal)
        self.set_decorated(decorated)
        self.set_title("")

        if text:
            label = Gtk.Label(label=text)
            align = Gtk.Alignment()
            align.set_padding(20, 20, 20, 20)
            align.add(label)
            self.add(align)
        elif child:
            self.add(child)

        while Gtk.events_pending():
            Gtk.main_iteration()

    def destroy(self):
        Gtk.Window.destroy(self)
        while Gtk.events_pending():
            Gtk.main_iteration()


class KeyGrabber(Gtk.Button):
    __gsignals__ = {
        "changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_INT, gobject.TYPE_INT)),
        "current-changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                            (gobject.TYPE_INT, Gdk.ModifierType))
    }

    key = 0
    mods = 0
    handler = None
    popup = None

    label = None

    def __init__ (self, parent=None, key=0, mods=0, label=None):
        '''Prepare widget'''
        gobject.GObject.__init__(self)

        self.main_window = parent
        self.key = key
        self.mods = mods

        self.label = label

        self.connect("clicked", self.begin_key_grab)
        self.set_label()

    def begin_key_grab(self, widget):
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.popup = Popup(self.main_window,
                           _("Please press the new key combination"))
        self.popup.show_all()

        self.handler = self.popup.connect("key-press-event",
                                          self.on_key_press_event)
        while Gdk.keyboard_grab(self.popup.window,
                                True,
                                Gtk.get_current_event_time()) != Gdk.GrabStatus.SUCCESS:
            time.sleep (0.1)

    def end_key_grab(self):
        Gdk.keyboard_ungrab(Gtk.get_current_event_time())
        self.popup.disconnect(self.handler)
        self.popup.destroy()

    def on_key_press_event(self, widget, event):
        #mods = event.get_state() & Gtk.accelerator_get_default_mod_mask()
        mods = event.get_state()

        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_Return) and not mods:
            if event.keyval == Gdk.KEY_Escape:
                self.emit("changed", self.key, self.mods)
            self.end_key_grab()
            self.set_label()
            return

        key = Gdk.keyval_to_lower(event.keyval)
        if (key == Gdk.KEY_ISO_Left_Tab):
            key = Gdk.KEY_Tab

        if Gtk.accelerator_valid(key, mods) or (key == Gdk.KEY_Tab and mods):
            self.set_label(key, mods)
            self.end_key_grab()
            self.key = key
            self.mods = mods
            self.emit("changed", self.key, self.mods)
            return

        self.set_label(key, mods)

    def set_label(self, key=None, mods=None):
        if self.label:
            if key != None and mods != None:
                self.emit("current-changed", key, mods)
            Gtk.Button.set_label(self, self.label)
            return
        if key == None and mods == None:
            key = self.key
            mods = self.mods
        label = Gtk.accelerator_name(key, mods)
        if not len(label):
            label = _("Disabled")
        Gtk.Button.set_label(self, label)
