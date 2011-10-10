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

from gi.repository import GObject, Gtk

from ubuntutweak.modules  import TweakModule
from ubuntutweak.gui.dialogs import InfoDialog
from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.settings.gconfsettings import GconfSetting


class ButtonView(Gtk.IconView):
    (COLUMN_VALUE,
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

    config = GconfSetting(key='/apps/metacity/general/button_layout')

    def __init__(self):
        GObject.GObject.__init__(self)

        model = self._create_model()
        self.set_model(model)
        self.update_model()

        self.set_text_column(self.COLUMN_LABEL)
        self.set_reorderable(True)
        self.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.connect('selection-changed', self.on_selection_changed)

    def _create_model(self):
        model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)

        return model

    @classmethod
    def get_control_items(cls):
        dict = cls.values.copy()
        dict.pop(':')
        return dict.items()

    @classmethod
    def is_value(cls, value):
        if value == cls.config.get_value():
            return True
        else:
            return False

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
            if k in self.values:
                model.append((k, self.values[k]))
            else:
                continue

    def on_selection_changed(self, widget, data=None):
        model = widget.get_model()
        value = ','.join([i[self.COLUMN_VALUE] for i in model])
        value = value.replace(',:', ':').replace(':,', ':')
        self.config.set_value(value)

    def add_button(self, value):
        model = self.get_model()
        model.append((value, self.values[value]))
        self.on_selection_changed(self)

    def remove_button(self, value):
        model = self.get_model()
        for i, row in enumerate(model):
            if row[self.COLUMN_VALUE] == value:
                del model[i, self.COLUMN_VALUE]
        self.on_selection_changed(self)

    def has_button(self, value):
        model = self.get_model()
        for i, row in enumerate(model):
            if row[self.COLUMN_VALUE] == value:
                return True
        return False


class WindowControlButton(Gtk.CheckButton):
    '''The individual checkbutton to control window control'''

    def __init__(self, label, value, view):
        '''Init the button, the view must be the ButtonView'''
        self._label = label
        self._value = value
        self._view = view

        GObject.GObject.__init__(self, label=self._label)
        self.set_active(self._view.has_button(self._value))

        self._handle_id = self.connect('toggled', self.on_toggled)

    def on_toggled(self, widget):
        '''Emit extra signal when toggle button'''
        if widget.get_active():
            self._view.add_button(self._value)
        else:
            self._view.remove_button(self._value)

    def update_status(self):
        '''Update status is called from others, not user, so need to block the handler'''
        self.handler_block(self._handle_id)
        self.set_active(self._view.has_button(self._value))
        self.handler_unblock(self._handle_id)


class Metacity(TweakModule):
    __title__ = _('Window Manager Settings')
    __desc__ = _('Manage Metacity Window Manager settings')
    __icon__ = 'preferences-system-windows'
    __url__ = 'http://ubuntu-tweak.com'
    __category__ = 'desktop'

    left_default = 'close,minimize,maximize:'
    right_default = ':minimize,maximize,close'

    def __init__(self):
        TweakModule.__init__(self, 'metacity.ui')

        swindow = Gtk.ScrolledWindow()
        swindow.set_size_request(-1, 54)
        swindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.buttonview = ButtonView()
        swindow.add(self.buttonview)
        self.vbox2.pack_start(swindow, False, False, 0)

        for value, label in ButtonView.get_control_items():
            button = WindowControlButton(label, value, self.buttonview)
            self.control_hbox.pack_start(button, False, False, 0)

        box = ListPack(_('Window Titlebar Button Layout'),
                       [child for child in self.main_vbox.get_children()])
        self.add_start(box, False, False, 0)
        self.init_control_buttons()

        table = TablePack(_('Window Titlebar Actions'), (
                    WidgetFactory.create('ComboBox',
                                         label=_('Titlebar mouse wheel action'),
                                         key='/apps/gwd/mouse_wheel_action',
                                         enable_reset=True,
                                         backend='gconf',
                                         texts=[_('None'), _('Roll up')],
                                         values=['none', 'shade']
                                         ),
                    #TODO the toggle_maximize_horizontally and vertically may not work
                    WidgetFactory.create('ComboBox',
                                         label=_('Titlebar double-click action'),
                                         key='/apps/metacity/general/action_double_click_titlebar',
                                         enable_reset=True,
                                         backend='gconf',
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
                    WidgetFactory.create('ComboBox',
                                         label=_('Titlebar middle-click action'),
                                         key='/apps/metacity/general/action_middle_click_titlebar',
                                         enable_reset=True,
                                         backend="gconf",
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
                    WidgetFactory.create('ComboBox',
                                         label=_('Titlebar right-click action'),
                                         key='/apps/metacity/general/action_right_click_titlebar',
                                         enable_reset=True,
                                         backend="gconf",
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
                    WidgetFactory.create('CheckButton',
                                          label=_('Use Metacity window theme'),
                                          enable_reset=True,
                                          backend="gconf",
                                          key='/apps/gwd/use_metacity_theme'),
                    WidgetFactory.create('CheckButton',
                                          label=_('Enable active window transparency'),
                                          backend="gconf",
                                          enable_reset=True,
                                          key='/apps/gwd/metacity_theme_active_shade_opacity'),
                    WidgetFactory.create('Scale',
                                          label=_('Active window transparency level'),
                                          key='/apps/gwd/metacity_theme_active_opacity',
                                          backend="gconf",
                                          enable_reset=True,
                                          min=0, max=1, digits=2),
                    WidgetFactory.create('CheckButton',
                                          label=_('Enable inactive window transparency'),
                                          enable_reset=True,
                                          backend="gconf",
                                          key='/apps/gwd/metacity_theme_shade_opacity'),
                    WidgetFactory.create('Scale',
                                          label=_('Inactive window shade transparency level'),
                                          backend="gconf",
                                          key='/apps/gwd/metacity_theme_opacity',
                                          enable_reset=True,
                                          min=0, max=1, digits=2),
            ))
        self.add_start(box, False, False, 0)

        button = WidgetFactory.create('CheckButton',
                                      label=_("Enable Metacity's compositing feature"),
                                      enable_reset=True,
                                      backend="gconf",
                                      signal_dict={'toggled': self.on_compositing_button_toggled},
                                      key='/apps/metacity/general/compositing_manager')
        if button:
            box = ListPack(_('Compositing Manager'), (button,))
            self.add_start(box, False, False, 0)

    def init_control_buttons(self):
        if ButtonView.is_value(self.left_default):
            self.left_radio.set_active(True)
        elif ButtonView.is_value(self.right_default):
            self.right_radio.set_active(True)
        else:
            self.place_hbox.set_sensitive(False)
            self.custom_button.set_active(True)
            self.custom_hbox.set_sensitive(True)

    def on_custom_button_toggled(self, widget, data=None):
        if not widget.get_active():
            self.place_hbox.set_sensitive(True)
            self.custom_button.set_active(False)
            self.custom_hbox.set_sensitive(False)
        else:
            self.place_hbox.set_sensitive(False)
            self.custom_button.set_active(True)
            self.custom_hbox.set_sensitive(True)

    def on_right_radio_toggled(self, widget, data=None):
        if widget.get_active():
            self.buttonview.update_model(default=self.right_default)
            self.buttonview.on_selection_changed(self.buttonview)
            self.update_control_buttons()

    def on_left_radio_toggled(self, widget, data=None):
        if widget.get_active():
            self.buttonview.update_model(default=self.left_default)
            self.buttonview.on_selection_changed(self.buttonview)
            self.update_control_buttons()

    def update_control_buttons(self):
        for button in self.control_hbox.get_children():
            if type(button) == WindowControlButton:
                button.update_status()

    def on_compositing_button_toggled(self, widget):
        if widget.get_active():
            InfoDialog(message=_('To enable Metacity\'s compositing feature, '
                       'you should manually disable Visual Effects in "Appearance".')).launch()
