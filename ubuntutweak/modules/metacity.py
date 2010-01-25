#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2010 TualatriX <tualatrix@gmail.com>
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

import gtk
import gobject


from ubuntutweak.modules  import TweakModule
from ubuntutweak.widgets import ListPack, TablePack
from ubuntutweak.widgets.dialogs import InfoDialog

from ubuntutweak.common.factory import WidgetFactory
from ubuntutweak.conf import GconfSetting

class ButtonView(gtk.IconView):
    (COLUMN_KEY,
     COLUMN_LABEL,
    ) = range(2)

    values = {
        'menu': _('Menu'),
        ':': _('Title'),
        'maximize': _('Maximize'),
        'minimize': _('Minimize'),
        'close': _('Close')
    }

    def __init__(self):
        gtk.IconView.__init__(self)

        self.config = GconfSetting(key='/apps/metacity/general/button_layout')
        model = self.__create_model()
        self.set_model(model)

        self.set_text_column(self.COLUMN_LABEL)
        self.set_size_request(-1, 48)
        self.set_reorderable(True)
        self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.connect('selection-changed', self.on_button_changed)

    def __create_model(self):
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

        list = self.config.get_value().replace(':', ',:,').split(',')

        for k in list:
            iter = model.append()
            model.set(iter,
                      self.COLUMN_KEY, k,
                      self.COLUMN_LABEL, self.values[k])

        return model

    def on_button_changed(self, widget, data=None):
        model = widget.get_model()
        value = ','.join([i[self.COLUMN_KEY] for i in model])
        value = value.replace(',:', ':').replace(':,', ':')
        self.config.set_value(value)

class Metacity(TweakModule):
    __title__ = _('Window Manager Settings')
    __desc__ = _('Some options about Metacity Window Manager')
    __icon__ = 'preferences-system-windows'
    __url__ = 'http://ubuntu-tweak.com'
    __category__ = 'desktop'
    __desktop__ = 'gnome'

    def __init__(self):
        TweakModule.__init__(self)

        label = gtk.Label(_('Arrange the buttons on the titlebar by dragging and dropping'))
        label.set_alignment(0, 0.5)
        buttonview1 = ButtonView()
        box = ListPack(_('Window Titlebar Button Layout'), (label, buttonview1))
        self.add_start(box, False, False, 0)

        table = TablePack(_('Window Titlebar Action'), (
                    WidgetFactory.create('GconfComboBox',
                                         label=_('Titlebar mouse wheel action'),
                                         key='mouse_wheel_action',
                                         texts=[_('None'), _('Roll up')],
                                         values=['none', 'shade']),
                    WidgetFactory.create('GconfComboBox', 
                                         label=_('Titlebar double-click action'),
                                         key='action_double_click_titlebar',
                                         texts=[_('None'), _('Maximize'), \
                                                 _('Maximize Horizontally'), \
                                                 _('Maximize Vertically'), \
                                                 _('Minimize'), _('Roll up'), \
                                                 _('Lower'), _('Menu')],
                                         values=['none', 'toggle_maximize', \
                                                 'toggle_maximize_horizontally', \
                                                 'toggle_maximize_vertically', \
                                                 'minimize', 'toggle_shade', \
                                                 'lower', 'menu']),
                    WidgetFactory.create('GconfComboBox',
                                         label=_('Titlebar middle-click action'),
                                         key='action_middle_click_titlebar',
                                         texts=[_('None'), _('Maximize'), \
                                                 _('Maximize Horizontally'), \
                                                 _('Maximize Vertically'), \
                                                 _('Minimize'), _('Roll up'), \
                                                 _('Lower'), _('Menu')],
                                         values=['none', 'toggle_maximize', \
                                                 'toggle_maximize_horizontally', \
                                                 'toggle_maximize_vertically', \
                                                 'minimize', 'toggle_shade', \
                                                 'lower', 'menu']),
                    WidgetFactory.create('GconfComboBox', 
                                         label=_('Titlebar right-click action'),
                                         key='action_right_click_titlebar',
                                         texts=[_('None'), _('Maximize'), \
                                                 _('Maximize Horizontally'), \
                                                 _('Maximize Vertically'), \
                                                 _('Minimize'), _('Roll up'), \
                                                 _('Lower'), _('Menu')],
                                         values=['none', 'toggle_maximize', \
                                                 'toggle_maximize_horizontally', \
                                                 'toggle_maximize_vertically', \
                                                 'minimize', 'toggle_shade', \
                                                 'lower', 'menu']),
                ))

        self.add_start(table, False, False, 0)

        box = TablePack(_('Window Decorate Effect'), (
                    WidgetFactory.create('GconfCheckButton',
                                          label=_('Use Metacity window theme'),
                                          key='use_metacity_theme'),
                    WidgetFactory.create('GconfCheckButton',
                                          label=_('Enable active window transparency'),
                                          key='metacity_theme_active_shade_opacity'),
                    WidgetFactory.create('GconfScale',
                                          label=_('Active window transparency level'),
                                          key='metacity_theme_active_opacity',
                                          min=0, max=1, digits=2),
                    WidgetFactory.create('GconfCheckButton',
                                          label=_('Enable inactive window transparency'),
                                          key='metacity_theme_shade_opacity'),
                    WidgetFactory.create('GconfScale',
                                          label=_('Inactive window shade transparency level'),
                                          key='metacity_theme_opacity',
                                          min=0, max=1, digits=2),
            ))
        self.add_start(box, False, False, 0)

        button = WidgetFactory.create('GconfCheckButton', 
                                      label=_("Enable Metacity's Compositing feature"),
                                      key='compositing_manager')
        if button:
            box = ListPack(_('Compositing Manager'), (button,))
            button.connect('toggled', self.on_compositing_button_toggled)

            self.add_start(box, False, False, 0)

    def on_compositing_button_toggled(self, widget):
        if widget.get_active():
            InfoDialog(_('To enable the compositing feature of metacity, you should manually disable Visual Effects in "Appearance".')).launch()
