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

import logging

from gi.repository import Gtk

from ubuntutweak.gui.dialogs import *
from ubuntutweak.gui.widgets import *
from ubuntutweak.gui.containers import *

log = logging.getLogger('factory')

def on_reset_button_clicked(widget, reset_target):
    log.debug("Reset value for %s" % reset_target)

    if issubclass(reset_target.__class__, Gtk.CheckButton):
        reset_target.set_active(widget.get_default_value())
    elif issubclass(reset_target.__class__, Gtk.SpinButton):
        reset_target.set_value(widget.get_default_value())
    elif issubclass(reset_target.__class__, Gtk.Scale):
        reset_target.set_value(widget.get_default_value())


class WidgetFactory:
    composite_capable = ('SpinButton', 'Entry', 'ComboBox', 'Scale')

    @classmethod
    def create(cls, widget, **kwargs):
        if widget in cls.composite_capable and kwargs.has_key('label'):
            return getattr(cls, 'do_composite_create')(widget, **kwargs)
        else:
            return getattr(cls, 'do_create')(widget, **kwargs)

    @classmethod
    def do_composite_create(cls, widget, **kwargs):
        label = Gtk.Label(label=kwargs.pop('label'))
        signal_dict = kwargs.pop('signal_dict', None)

        enable_reset = kwargs.has_key('enable_reset')
        if enable_reset:
            kwargs.pop('enable_reset')

        new_widget = globals().get(widget)(**kwargs)

        if signal_dict:
            for signal, method in signal_dict.items():
                new_widget.connect(signal, method)

        if enable_reset:
            try:
                reset_button = ResetButton(kwargs['key'], kwargs['backend'])
                reset_button.connect('clicked', on_reset_button_clicked, new_widget)
            except Exception, e:
                log.error(e)
                reset_button = None
            finally:
                return label, new_widget, reset_button

        return label, new_widget

    @classmethod
    def do_create(cls, widget, **kwargs):
        signal_dict = kwargs.pop('signal_dict', None)

        enable_reset = kwargs.has_key('enable_reset')
        if enable_reset:
            kwargs.pop('enable_reset')

        new_widget = globals().get(widget)(**kwargs)

        if signal_dict:
            for signal, method in signal_dict.items():
                new_widget.connect(signal, method)

        if enable_reset:
            try:
                reset_button = ResetButton(kwargs['key'], kwargs['backend'])
                reset_button.connect('clicked', on_reset_button_clicked, new_widget)

                hbox = Gtk.HBox()
                hbox.set_data('widget', new_widget)
                hbox.set_data('reset_button', reset_button)

                hbox.pack_start(new_widget, False, False, 0)
                hbox.pack_end(reset_button, False, False, 0)

                return hbox
            except Exception, e:
                log.error(e)

        return new_widget
