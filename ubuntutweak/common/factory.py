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

from gi.repository import GConf
import logging

from ubuntutweak.ui import *
from ubuntutweak.common.consts import *
from ubuntutweak.conf import GconfKeys

log = logging.getLogger('factory')

def on_reset_button_clicked(widget, reset_target):
    log.debug("Reset value for %s" % reset_target)
    if issubclass(reset_target.__class__, Gtk.CheckButton):
        reset_target.set_active(widget.get_default_value())
    elif issubclass(reset_target.__class__, Gtk.ComboBox):
        model = reset_target.get_model()
        iter = model.get_iter_first()
        default_value = widget.get_default_value()
        while iter:
            if model.get_value(iter, 1) == default_value:
                reset_target.set_active_iter(iter)
                break
            iter = model.iter_next(iter)
    elif issubclass(reset_target.__class__, Gtk.Scale):
        reset_target.set_value(widget.get_default_value())
    elif issubclass(reset_target.__class__, Gtk.SpinButton):
        reset_target.set_value(widget.get_default_value())
    elif issubclass(reset_target.__class__, Gtk.Entry):
        reset_target.set_text(widget.get_default_value())

class WidgetFactory:
    keys = GconfKeys.keys
    client = GConf.Client.get_default()
    composite_capable = ('GconfEntry', 'GconfComboBox', 'GconfSpinButton', 'GconfScale')

    @classmethod
    def create(cls, widget, **kwargs):
        if 'key' in kwargs:
            key = kwargs['key']

            if key.startswith('/') and kwargs.get('dir_exists'):
                if cls.client.dir_exists(os.path.dirname(key)) == False:
                    return None
            elif not key.startswith('/'):
                if key not in cls.keys:
                    return None
                else:
                    key = cls.keys[key]

            kwargs['key'] = key

            if widget in cls.composite_capable and kwargs.has_key('label'):
                return getattr(cls, 'do_composite_create')(widget, **kwargs)
            else:
                return getattr(cls, 'do_create')(widget, **kwargs)
        else:
            return None

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
                reset_button = GconfResetButton(kwargs['key'])
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
                reset_button = GconfResetButton(kwargs['key'])
                reset_button.connect('clicked', on_reset_button_clicked, new_widget)

                hbox = Gtk.HBox(False, 0)

                hbox.pack_start(new_widget, False, False, 0)
                hbox.pack_end(reset_button, False, False, 0)

                return hbox
            except Exception, e:
                log.error(e)

        return new_widget

if __name__ == '__main__':
    for k,v in GconfKeys.keys.items():
        print '%s\t%s\n' % (k, v)
