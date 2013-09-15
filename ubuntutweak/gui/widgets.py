import time
import logging

from gi.repository import GObject, Gtk, Gdk

from ubuntutweak.common.debug import log_func
from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.settings.configsettings import ConfigSetting
from ubuntutweak.settings.gconfsettings import GconfSetting, UserGconfSetting
from ubuntutweak.settings.compizsettings import CompizSetting
from ubuntutweak.settings.configsettings import SystemConfigSetting

log = logging.getLogger('widgets')

class SettingWidget(object):
    def __init__(self, **kwargs):
        key = kwargs['key']
        backend = kwargs['backend']
        default = kwargs['default']
        type = kwargs['type']

        if backend == 'gconf':
            self._setting = GconfSetting(key=key, default=default, type=type)
        elif backend == 'gsettings':
            self._setting = GSetting(key=key, default=default, type=type)
        elif backend == 'config':
            self._setting = ConfigSetting(key=key, type=type)
        elif backend == 'compiz':
            self._setting = CompizSetting(key=key)
        elif backend == 'systemconfig':
            self._setting = SystemConfigSetting(key=key, default=default, type=type)

        if hasattr(self._setting, 'connect_notify') and \
                hasattr(self, 'on_value_changed'):
            log.debug("Connect the setting notify to on_value_changed: %s" % key)
            self.get_setting().connect_notify(self.on_value_changed)

    def get_setting(self):
        return self._setting


class CheckButton(Gtk.CheckButton, SettingWidget):
    def __str__(self):
        return '<CheckButton with key: %s>' % self.get_setting().key

    def __init__(self, label=None, key=None,
                 default=None, tooltip=None, backend='gconf'):
        GObject.GObject.__init__(self, label=label)
        SettingWidget.__init__(self, key=key, default=default, type=bool, backend=backend)

        self.set_active(self.get_setting().get_value())

        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect('toggled', self.on_button_toggled)

    @log_func(log)
    def on_value_changed(self, *args):
        self.set_active(self.get_setting().get_value())

    @log_func(log)
    def on_button_toggled(self, widget):
        self.get_setting().set_value(self.get_active())


class Switch(Gtk.Switch, SettingWidget):
    def __str__(self):
        return '<Switch with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None,
                 on=True, off=False,
                 tooltip=None,
                 reverse=False,
                 backend='gconf'):
        GObject.GObject.__init__(self)
        SettingWidget.__init__(self, key=key, default=default, type=bool, backend=backend)

        self._on = on
        self._off = off
        self._reverse = reverse

        self._set_on_off()

        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect('notify::active', self.on_switch_activate)

    def _set_on_off(self):
        self.set_active(self._off != self.get_setting().get_value())

    def set_active(self, bool):
        if self._reverse:
            log.debug("The value is reversed")
            bool = not bool
        log.debug("Set the swtich to: %s" % bool)
        super(Switch, self).set_active(bool)

    def get_active(self):
        if self._reverse:
            return not super(Switch, self).get_active()
        else:
            return super(Switch, self).get_active()

    @log_func(log)
    def on_value_changed(self, *args):
        self.handler_block_by_func(self.on_switch_activate)
        self._set_on_off()
        self.handler_unblock_by_func(self.on_switch_activate)

    @log_func(log)
    def on_switch_activate(self, widget, value):
        try:
            if self.get_active():
                self.get_setting().set_value(self._on)
            else:
                self.get_setting().set_value(self._off)
        except Exception, e:
            log.error(e)
            self.on_value_changed(self, None)

    def reset(self):
        self.set_active(self._off != self.get_setting().get_schema_value())

class UserCheckButton(Gtk.CheckButton, SettingWidget):
    def __str__(self):
        return '<UserCheckButton with key: %s, with user: %s>' % (self.get_setting().key, self.user)

    def __init__(self, user=None, label=None, key=None, default=None,
                 tooltip=None, backend='gconf'):
        GObject.GObject.__init__(self, label=label)
        SettingWidget.__init__(self, key=key, default=default, type=bool, backend=backend)

        self.user = user

        self.set_active(bool(self.get_setting().get_value(self.user)))
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect('toggled', self.button_toggled)

    def button_toggled(self, widget):
        self.get_setting().set_value(self.user, self.get_active())


class ResetButton(Gtk.Button):
    def __str__(self):
        return '<ResetButton with key: %s: reverse: %s>' % \
                (self._setting.key, self._reverse)

    def __init__(self, setting, reverse=False):
        GObject.GObject.__init__(self)

        self._setting = setting
        self._reverse = reverse

        self.set_property('image', 
                          Gtk.Image.new_from_stock(Gtk.STOCK_REVERT_TO_SAVED, Gtk.IconSize.MENU))

        self.set_tooltip_text(_('Reset setting to default value: %s') % self.get_default_value())

    def get_default_value(self):
        schema_value = self._setting.get_schema_value()
        if self._reverse and type(schema_value) == bool:
            return not schema_value
        else:
            return schema_value


class StringCheckButton(CheckButton):
    '''This class use to moniter the key with StringSetting, nothing else'''
    def __str__(self):
        return '<StringCheckButton with key: %s>' % self.get_setting().key

    def __init__(self, **kwargs):
        CheckButton.__init__(self, **kwargs)

    def on_button_toggled(self, widget):
        '''rewrite the toggled function, it do nothing with the setting'''
        pass

    def on_value_changed(self, *args):
        pass


class Entry(Gtk.Entry, SettingWidget):
    def __str__(self):
        return '<Entry with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None, backend='gconf'):
        GObject.GObject.__init__(self)
        SettingWidget.__init__(self, key=key, default=default, type=str, backend=backend)

        string = self.get_setting().get_value()
        if string:
            self.set_text(str(string))

        text_buffer = self.get_buffer()
        text_buffer.connect('inserted-text', self.on_edit_finished_cb)
        text_buffer.connect('deleted-text', self.on_edit_finished_cb)

        self.connect('activate', self.on_edit_finished_cb)

    def is_changed(self):
        return self.get_setting().get_value() != self.get_text()

    @log_func(log)
    def on_value_changed(self, *args):
        self.handler_block_by_func(self.on_edit_finished_cb)
        self.set_text(self.get_setting().get_value())
        self.handler_unblock_by_func(self.on_edit_finished_cb)

    def get_gsetting(self):
        return self.get_setting()

    def on_edit_finished_cb(self, widget, *args):
        log.debug('Entry: on_edit_finished_cb: %s' % self.get_text())
        self.get_setting().set_value(self.get_text())


class ComboBox(Gtk.ComboBox, SettingWidget):
    def __str__(self):
        return '<ComboBox with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None,
                 texts=None, values=None,
                 type=str, backend='gconf'):
        GObject.GObject.__init__(self)
        SettingWidget.__init__(self, key=key, default=default, type=type, backend=backend)

        if type == int:
            model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        else:
            model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        self.set_model(model)

        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        self.update_texts_values_pair(texts, values)

        self.connect("changed", self.value_changed_cb)

    def update_texts_values_pair(self, texts, values):
        self._texts = texts
        self._values = values

        self._set_value(self.get_setting().get_value())

    def _set_value(self, current_value):
        model = self.get_model()
        model.clear()

        for text, value in zip(self._texts, self._values):
            iter = model.append((text, value))
            if current_value == value:
                self.set_active_iter(iter)

    @log_func(log)
    def on_value_changed(self, *args):
        self.handler_block_by_func(self.value_changed_cb)
        self._set_value(self.get_setting().get_value())
        self.handler_unblock_by_func(self.value_changed_cb)

    def value_changed_cb(self, widget):
        iter = widget.get_active_iter()
        if iter:
            text = self.get_model().get_value(iter, 1)
            log.debug("ComboBox value changed to %s" % text)

            self.get_setting().set_value(text)

    def reset(self):
        self._set_value(self.get_setting().get_schema_value())


class FontButton(Gtk.FontButton, SettingWidget):
    def __str__(self):
        return '<FontButton with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None, backend='gconf'):
        GObject.GObject.__init__(self)
        SettingWidget.__init__(self, key=key, default=default, type=str, backend=backend)

        self.set_use_font(True)
        self.set_use_size(True)

        self.on_value_changed()

        self.connect('font-set', self.on_font_set)

    def on_font_set(self, widget=None):
        self.get_setting().set_value(self.get_font_name())

    @log_func(log)
    def on_value_changed(self, *args):
        string = self.get_setting().get_value()

        if string:
            self.set_font_name(string)

    def reset(self):
        self.set_font_name(self.get_setting().get_schema_value())
        self.get_setting().set_value(self.get_font_name())


class Scale(Gtk.Scale, SettingWidget):
    def __str__(self):
        return '<Scale with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None, min=None, max=None, step=None, type=int, digits=0,
                 reverse=False, orientation=Gtk.Orientation.HORIZONTAL, backend='gconf'):
        GObject.GObject.__init__(self,
                                 orientation=orientation)

        if digits > 0:
            type = float
        else:
            type = int

        if step:
            self.set_increments(step, step)

        SettingWidget.__init__(self, key=key, default=default, type=type, backend=backend)

        self._reverse = reverse
        self._max = max
        self._default = default

        self.set_range(min, max)
        self.set_digits(digits)
        try:
            self.add_mark(default or self.get_setting().get_schema_value(),
                          Gtk.PositionType.BOTTOM,
                          '')
        except Exception, e:
            log.error(e)

        self.set_value_pos(Gtk.PositionType.RIGHT)

        self.connect("value-changed", self.on_change_value)
        self.on_value_changed()

    @log_func(log)
    def on_value_changed(self, *args):
        self.handler_block_by_func(self.on_change_value)
        self.set_value(self.get_setting().get_value())
        self.handler_unblock_by_func(self.on_change_value)

    def set_value(self, value):
        if self._reverse:
            super(Scale, self).set_value(self._max - value)
        else:
            super(Scale, self).set_value(value)

    def get_value(self):
        if self._reverse:
            return self._max - super(Scale, self).get_value()
        else:
            return super(Scale, self).get_value()

    def on_change_value(self, widget):
        if self._reverse:
            self.get_setting().set_value(100 - widget.get_value())
        else:
            self.get_setting().set_value(widget.get_value())

    def reset(self):
        self.set_value(self._default or self.get_setting().get_schema_value())


class SpinButton(Gtk.SpinButton, SettingWidget):
    def __str__(self):
        return '<SpinButton with key: %s>' % self.get_setting().key

    def __init__(self, key, default=None, min=0, max=0, step=0, backend='gconf'):
        SettingWidget.__init__(self, key=key, default=default, type=int, backend=backend)

        adjust = Gtk.Adjustment(self.get_setting().get_value(), min, max, step)
        GObject.GObject.__init__(self, adjustment=adjust)
        self.connect('value-changed', self.on_change_value)

    def on_change_value(self, *args):
        self.set_value(self, self.get_setting().get_value())

    @log_func(log)
    def on_value_changed(self, widget):
        self.handler_block_by_func(self.on_change_value)
        self.get_setting().set_value(widget.get_value())
        self.handler_unblock_by_func(self.on_change_value)


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


class ColorButton(Gtk.ColorButton, SettingWidget):
    def __str__(self):
        return '<ColorButton with key: %s>' % self.get_setting().key

    def __init__(self, key=None, default=None, backend='gconf'):
        GObject.GObject.__init__(self)
        self.set_use_alpha(True)
        SettingWidget.__init__(self, key=key, default=default, type=str, backend=backend)

        self._set_gdk_rgba()

        self.connect('color-set', self.on_color_set)

    def _set_gdk_rgba(self, new_value=None):
        color_value = new_value or self.get_setting().get_value()
        red, green, blue = color_value[:-1]
        color = Gdk.RGBA()
        color.red, color.green, color.blue = red / 65535.0, green / 65535.0, blue / 65535.0
        color.alpha = color_value[-1] / 65535.0
        self.set_rgba(color)

    @log_func(log)
    def on_color_set(self, widget=None):
        color = self.get_rgba()
        self.get_setting().set_value([color.red * 65535,
                                 color.green * 65535,
                                 color.blue * 65535,
                                 color.alpha * 65535])

    def set_value(self, value):
        self.get_setting().set_value(value)
        self.set_rgba(Gdk.RGBA(0,0,0,0))

    @log_func(log)
    def on_value_changed(self, *args):
        self.handler_block_by_func(self.on_color_set)
        self._set_gdk_rgba()
        self.handler_unblock_by_func(self.on_color_set)

    def reset(self):
        self._set_gdk_rgba(self.get_setting().get_schema_value())
        self.on_color_set()
