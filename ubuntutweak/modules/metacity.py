#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
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
        'close': _('Close'),
        'spacer': _('Spacer'),
    }

    def __init__(self):
        gtk.IconView.__init__(self)

        self.config = GconfSetting(key='/apps/metacity/general/button_layout')
        model = self.__create_model()
        self.set_model(model)
        self.update_model()

        self.set_text_column(self.COLUMN_LABEL)
        self.set_reorderable(True)
        self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.connect('selection-changed', self.on_button_changed)

    def __create_model(self):
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

        return model

    def update_model(self, default=None):
        model = self.get_model()
        model.clear()

        value = default or self.config.get_value()
        if value:
            list = value.replace(':', ',:,').split(',')
        else:
            return model

        for k in list:
            k = k.strip()
            iter = model.append()
            if k in self.values:
                model.set(iter,
                          self.COLUMN_KEY, k,
                          self.COLUMN_LABEL, self.values[k])
            else:
                continue

        return model

    def on_button_changed(self, widget, data=None):
        model = widget.get_model()
        value = ','.join([i[self.COLUMN_KEY] for i in model])
        value = value.replace(',:', ':').replace(':,', ':')
        self.config.set_value(value)

    def add_button(self, text):
        model = self.get_model()
        iter = model.append()
        model.set(iter,
                  self.COLUMN_KEY, text,
                  self.COLUMN_LABEL, self.values[text])
        self.on_button_changed(self)

    def remove_button(self, text):
        model = self.get_model()
        for i, row in enumerate(model):
            if row[self.COLUMN_KEY] == text:
                del model[i, self.COLUMN_KEY]
                break
        self.on_button_changed(self)

    def has_button(self, text):
        model = self.get_model()
        for i, row in enumerate(model):
            if row[self.COLUMN_KEY] == text:
                return True
        return False

class Metacity(TweakModule):
    __title__ = _('Window Manager Settings')
    __desc__ = _('Manage Metacity Window Manager settings')
    __icon__ = 'preferences-system-windows'
    __url__ = 'http://ubuntu-tweak.com'
    __category__ = 'desktop'
    __desktop__ = 'gnome'

    ADD_SPACER = _('Add Spacer')
    REMOVE_SPACER = _('Remove Spacer')

    def __init__(self):
        TweakModule.__init__(self)

        label = gtk.Label(_('Arrange the buttons on the titlebar by dragging and dropping'))
        label.set_alignment(0, 0.5)

        swindow = gtk.ScrolledWindow()
        swindow.set_size_request(-1, 54)
        swindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        buttonview1 = ButtonView()
        swindow.add(buttonview1)

        hbox = gtk.HBox(False, 12)
        button1 = gtk.Button(stock=gtk.STOCK_REDO)
        hbox.pack_end(button1, False, False, 0)
        button2 = gtk.Button()
        if buttonview1.has_button('spacer'):
            button2.set_label(self.REMOVE_SPACER)
        else:
            button2.set_label(self.ADD_SPACER)
        button2.connect('clicked', self.on_spacer_clicked, buttonview1)
        button1.connect('clicked', self.on_redo_clicked, (button2, buttonview1))
        hbox.pack_end(button2, False, False, 0)

        box = ListPack(_('Window Titlebar Button Layout'), (label,
                                                            swindow,
                                                            hbox))
        self.add_start(box, False, False, 0)

        table = TablePack(_('Window Titlebar Actions'), (
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

        box = TablePack(_('Window Decoration Effects'), (
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
                                      label=_("Enable Metacity's compositing feature"),
                                      key='compositing_manager')
        if button:
            box = ListPack(_('Compositing Manager'), (button,))
            button.connect('toggled', self.on_compositing_button_toggled)

            self.add_start(box, False, False, 0)

    def on_redo_clicked(self, widget, data):
        button, view = data
        view.update_model(default='menu:minimize,maximize,close')
        view.on_button_changed(view)
        button.set_label(self.ADD_SPACER)

    def on_spacer_clicked(self, widget, view):
        if view.has_button('spacer'):
            view.remove_button('spacer')
            widget.set_label(self.ADD_SPACER)
        else:
            view.add_button('spacer')
            widget.set_label(self.REMOVE_SPACER)

    def on_compositing_button_toggled(self, widget):
        if widget.get_active():
            InfoDialog(_('To enable Metacity\'s compositing feature, you should manually disable Visual Effects in "Appearance".')).launch()
