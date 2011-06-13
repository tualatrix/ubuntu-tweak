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
import gobject
from gi.repository import Gtk
from ubuntutweak.gui.gtk import set_busy, unset_busy

from aptdaemon import policykit1
from defer import inline_callbacks

class PolkitAction(gobject.GObject):
    """
    PolicyKit action, if changed return 0, means authenticate failed, 
    return 1, means authenticate successfully
    """

    def __init__(self):
        gobject.GObject.__init__(self)

    @inline_callbacks
    def do_authenticate(self):
        bus = dbus.SystemBus()
        name = bus.get_unique_name()
        action = 'com.ubuntu-tweak.daemon'
        flags = policykit1.CHECK_AUTH_ALLOW_USER_INTERACTION

        yield policykit1.check_authorization_by_name(name, action, flags=flags)


class PolkitButton(Gtk.Button):
    __gsignals__ = {
        'authenticated': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self.set_label(_('_Unlock'))
        self.set_use_underline(True)
        image = Gtk.Image.new_from_stock(Gtk.STOCK_DIALOG_AUTHENTICATION,
                                         Gtk.IconSize.BUTTON)
        self.set_image(image)

        self._action = PolkitAction()
        self.connect('clicked', self.on_button_clicked)

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
        image = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.BUTTON)
        self.set_image(image)
        self.set_sensitive(False)
