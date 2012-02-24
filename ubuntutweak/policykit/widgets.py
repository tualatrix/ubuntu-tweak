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

import dbus

from gi.repository import GObject, Gtk, Gio
from ubuntutweak.gui.gtk import set_busy, unset_busy

from aptdaemon import policykit1
from defer import inline_callbacks

class PolkitAction(GObject.GObject):
    """
    PolicyKit action, if changed return 0, means authenticate failed, 
    return 1, means authenticate successfully
    """

    def __init__(self, action):
        GObject.GObject.__init__(self)

        self.action = action

    @inline_callbacks
    def do_authenticate(self):
        bus = dbus.SystemBus()
        name = bus.get_unique_name()
        flags = policykit1.CHECK_AUTH_ALLOW_USER_INTERACTION

        yield policykit1.check_authorization_by_name(name, self.action, flags=flags)


class PolkitButton(Gtk.Button):
    __gsignals__ = {
        'authenticated': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, action):
        GObject.GObject.__init__(self)
        self.icon_unlock = ('changes-allow-symbolic', 'changes-allow')
        self.icon_lock = ('changes-prevent-symbolic', 'changes-prevent')

        self.hbox = Gtk.HBox(spacing=6)
        self.add(self.hbox)

        self.image = Gtk.Image.new_from_gicon(Gio.ThemedIcon.new_from_names(self.icon_lock),
                                         Gtk.IconSize.BUTTON)
        self.hbox.pack_start(self.image, False, False, 0)

        self.label = Gtk.Label(_('_Unlock'))
        self.label.set_use_underline(True)
        self.hbox.pack_start(self.label, False, False, 0)

        self._action = PolkitAction(action)
        self.connect('clicked', self.on_button_clicked)

        self.show_all()

    @inline_callbacks
    def on_button_clicked(self, widget):
        set_busy(widget.get_toplevel())
        try:
            yield self._action.do_authenticate()
        except Exception, e:
            import logging
            logging.getLogger('PolkitButton').debug(e)
            unset_busy(widget.get_toplevel())
            return

        self.emit('authenticated')
        self._change_button_state()
        unset_busy(widget.get_toplevel())

    def _change_button_state(self):
        self.image.set_from_gicon(Gio.ThemedIcon.new_from_names(self.icon_unlock), Gtk.IconSize.BUTTON)

        self.set_sensitive(False)
