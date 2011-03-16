import gobject
from gi.repository import Gtk, GConf

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

    def connect_activate_signal(self):
        self.connect('activate', self.on_edit_finished_cb)

    def get_gsetting(self):
        return self.setting

    def on_edit_finished_cb(self, widget):
        if self.get_text():
            self.setting.set_value(self.get_text())
        else:
            print 'uset'
            self.setting.client.unset(self.setting.key)
            self.set_text(_("Unset"))
