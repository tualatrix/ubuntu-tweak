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

import gconf

from ubuntutweak.widgets import *
from ubuntutweak.common.consts import *
from ubuntutweak.conf import GconfKeys

def on_reset_button_clicked(widget, reset_target):
    log.debug("Reset value for %s" % reset_target)
    if issubclass(reset_target.__class__, gtk.CheckButton):
        reset_target.set_active(widget.get_default_value())
    elif issubclass(reset_target.__class__, gtk.Scale):
        reset_target.set_value(widget.get_default_value())
    elif issubclass(reset_target.__class__, gtk.SpinButton):
        reset_target.set_value(widget.get_default_value())
    elif issubclass(reset_target.__class__, gtk.Entry):
        reset_target.set_text(widget.get_default_value())

class WidgetFactory:
    keys = GconfKeys.keys
    client = gconf.client_get_default()
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
        label = gtk.Label(kwargs.pop('label'))
        signal_dict = kwargs.pop('signal_dict', None)

        has_reset = kwargs.has_key('reset')
        if has_reset:
            kwargs.pop('reset')

        new_widget = globals().get(widget)(**kwargs)

        if signal_dict:
            for signal, method in signal_dict.items():
                new_widget.connect(signal, method)

        if has_reset:
            reset_button = GconfResetButton(kwargs['key'])
            reset_button.connect('clicked', on_reset_button_clicked, new_widget)

            return label, new_widget, reset_button
        else:
            return label, new_widget

    @classmethod
    def do_create(cls, widget, **kwargs):
        if kwargs.has_key('reset'):
            kwargs.pop('reset')

            hbox = gtk.HBox(False, 0)

            new_widget = globals().get(widget)(**kwargs)
            hbox.pack_start(new_widget, False, False, 0)

            reset_button = GconfResetButton(kwargs['key'])
            reset_button.connect('clicked', on_reset_button_clicked, new_widget)
            hbox.pack_end(reset_button, False, False, 0)

            return hbox
        else:
            return globals().get(widget)(**kwargs)

if __name__ == '__main__':
    for k,v in GconfKeys.keys.items():
        print '%s\t%s\n' % (k, v)
