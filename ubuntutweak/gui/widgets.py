import time
import logging

from gi.repository import GObject, Gtk, Gdk

from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.settings.gconfsettings import GconfSetting, UserGconfSetting

log = logging.getLogger('widgets')


class CheckButton(Gtk.CheckButton):
    def __str__(self):
        return '<CheckButton with key: %s>' % self._setting.key

    def __init__(self, label=None, key=None,
                 default=None, tooltip=None, backend='gconf'):
        GObject.GObject.__init__(self, label=label)
        if backend == 'gconf':
            self._setting = GconfSetting(key=key, default=default, type=bool)
        elif backend == 'gsettings':
            self._setting = GSetting(key=key, default=default, type=bool)

        self.set_active(self._setting.get_value())
        if tooltip:
            self.set_tooltip_text(tooltip)

        self._setting.connect_notify(self.on_value_changed)
        self.connect('toggled', self.on_button_toggled)

    def on_value_changed(self, *args):
        self.set_active(self._setting.get_value())

    def on_button_toggled(self, widget):
        self._setting.set_value(self.get_active())


class UserCheckButton(Gtk.CheckButton):
    def __init__(self, user=None, label=None, key=None, default=None,
                 tooltip=None, backend='gconf'):
        GObject.GObject.__init__(self, label=label)

        if backend == 'gconf':
            self._setting = UserGconfSetting(key=key, default=default, type=bool)
        else:
            #TODO 'gsettings'
            pass
        self.user = user

        self.set_active(bool(self._setting.get_value(self.user)))
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect('toggled', self.button_toggled)

    def button_toggled(self, widget):
        self._setting.set_value(self.user, self.get_active())


class ResetButton(Gtk.Button):
    def __init__(self, key, backend='gconf'):
        GObject.GObject.__init__(self)

        if backend == 'gconf':
            self._setting = GconfSetting(key=key, type=bool)
        else:
            self._setting = GSetting(key=key, type=bool)

        self.set_property('image', 
                          Gtk.Image.new_from_stock(Gtk.STOCK_REVERT_TO_SAVED, Gtk.IconSize.MENU))

        self.set_tooltip_text(_('Reset setting to default value: %s') % self.get_default_value())

    def get_default_value(self):
        return self._setting.get_schema_value()


class StringCheckButton(CheckButton):
    '''This class use to moniter the key with StringSetting, nothing else'''
    def __init__(self, **kwargs):
        CheckButton.__init__(self, **kwargs)

    def on_button_toggled(self, widget):
        '''rewrite the toggled function, it do nothing with the setting'''
        pass

    def on_value_changed(self, *args):
        pass


class Entry(Gtk.Entry):
    def __init__(self, key=None, default=None, backend='gconf'):
        GObject.GObject.__init__(self)

        if backend == 'gconf':
            self._setting = GconfSetting(key=key, default=default, type=str)
        else:
            self._setting = GSetting(key=key, default=default, type=str)

        string = self._setting.get_value()
        if string:
            self.set_text(str(string))

        text_buffer = self.get_buffer()
        text_buffer.connect('inserted-text', self.on_edit_finished_cb)
        text_buffer.connect('deleted-text', self.on_edit_finished_cb)

        self.connect('activate', self.on_edit_finished_cb)

    def is_changed(self):
        return self._setting.get_value() != self.get_text()

    def get_gsetting(self):
        return self._setting

    def on_edit_finished_cb(self, widget, *args):
        log.debug('Entry: on_edit_finished_cb: %s' % self.get_text())
        self._setting.set_value(self.get_text())


class ComboBox(Gtk.ComboBox):
    def __init__(self, key=None, texts=None, values=None,
                 type="string", backend='gconf'):
        GObject.GObject.__init__(self)

        if backend == 'gconf':
            self._setting = GconfSetting(key=key, type=str)
        else:
            self._setting = GSetting(key=key, type=str)

        if type == 'int':
            model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        else:
            model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.set_model(model)

        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        current_value = self._setting.get_value()

        for text, value in dict(zip(texts, values)).items():
            iter = model.append((text, value))
            if current_value == value:
                self.set_active_iter(iter)

        self.connect("changed", self.value_changed_cb)

    def value_changed_cb(self, widget):
        iter = widget.get_active_iter()
        text = self.get_model().get_value(iter, 1)
        log.debug("ComboBox value changed to %s" % text)

        self._setting.set_value(text)


class Scale(Gtk.HScale):
    def __init__(self, key=None, min=None, max=None, digits=0,
                 reversed=False, backend='gconf'):
        GObject.GObject.__init__(self)

        if digits > 0:
            type = float
        else:
            type = int

        if backend == 'gconf':
            self._setting = GconfSetting(key=key, type=type)
        else:
            #TODO 'gsettings'
            pass

        if reversed:
            self._reversed = True
        else:
            self._reversed = False

        self.set_range(min, max)
        self.set_digits(digits)
        self.set_value_pos(Gtk.PositionType.RIGHT)
        if self._reversed:
            self.set_value(max - self._setting.get_value())
        else:
            self.set_value(self._setting.get_value())

        self.connect("value-changed", self.on_value_changed)

    def on_value_changed(self, widget, data=None):
        if self._reversed:
            self._setting.set_value(100 - widget.get_value())
        else:
            self._setting.set_value(widget.get_value())


class SpinButton(Gtk.SpinButton):
    def __init__(self, key, min=0, max=0, step=0, backend='gconf'):
        if backend == 'gconf':
            self._setting = GconfSetting(key=key, type=int)
        else:
            self._setting = GSetting(key=key, type=int)

        adjust = Gtk.Adjustment(self._setting.get_value(), min, max, step)
        GObject.GObject.__init__(self, adjustment=adjust)
        self.connect('value-changed', self.on_value_changed)

    def on_value_changed(self, widget):
        self._setting.set_value(widget.get_value())


"""Popup and KeyGrabber come from ccsm"""
KeyModifier = ["Shift", "Control", "Mod1", "Mod2", "Mod3", "Mod4",
               "Mod5", "Alt", "Meta", "Super", "Hyper", "ModeSwitch"]


class Popup(Gtk.Window):
    def __init__(self, parent, text=None, child=None,
                 decorated=True, mouse=False, modal=True):
        GObject.GObject.__init__(self, type=Gtk.WindowType.TOPLEVEL)
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
        "changed": (GObject.SignalFlags.RUN_FIRST, None,
                    (GObject.TYPE_INT, GObject.TYPE_INT)),
        "current-changed": (GObject.SignalFlags.RUN_FIRST, None,
                            (GObject.TYPE_INT, Gdk.ModifierType))
    }

    key = 0
    mods = 0
    handler = None
    popup = None

    label = None

    def __init__ (self, parent=None, key=0, mods=0, label=None):
        '''Prepare widget'''
        GObject.GObject.__init__(self)

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

        while Gdk.keyboard_grab(self.popup.get_parent_window(),
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
