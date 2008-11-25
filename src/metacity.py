#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
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

import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from common.factory import Factory
from common.widgets import ListPack, TablePack, TweakPage
from common.widgets.dialogs import InfoDialog

class Metacity(TweakPage):
    '''Some options about Metacity Window Manager'''
    def __init__(self):
        TweakPage.__init__(self)

        box = TablePack(_('Window Decorate Effect'), [
                [Factory.create('gconfcheckbutton', _('Use Metacity window theme'), 'use_metacity_theme')],
                [Factory.create('gconfcheckbutton', _('Enable active window transparency'), 'metacity_theme_active_shade_opacity')],
                [gtk.Label(_('Active window transparency level')), Factory.create('gconfscale', 0, 1, 'metacity_theme_active_opacity', 2)],
                [Factory.create('gconfcheckbutton', _('Enable inactive window transparency'), 'metacity_theme_shade_opacity')],
                [gtk.Label(_('Inactive window shade transparency level')), Factory.create('gconfscale', 0, 1, 'metacity_theme_opacity', 2)],
            ])
        self.pack_start(box, False, False, 0)

        table = TablePack(_('Window Titlebar Action'), [
                [gtk.Label(_('Titlebar mouse wheel action')), 
                    Factory.create('gconfcombobox', 'mouse_wheel_action', 
                        [_('None'), _('Roll up')], 
                        ['none', 'shade'])],
                [gtk.Label(_('Titlebar double-click action')), 
                    Factory.create('gconfcombobox', 'action_double_click_titlebar', 
                        [_('None'), _('Maximize'), _('Minimize'), _('Roll up'), _('Lower'), _('Menu')], 
                        ['none', 'toggle_maximize', 'minimize', 'toggle_shade', 'lower', 'menu'])],
                [gtk.Label(_('Titlebar middle-click action')), 
                    Factory.create('gconfcombobox', 'action_middle_click_titlebar', 
                        [_('None'), _('Maximize'), _('Minimize'), _('Roll up'), _('Lower'), _('Menu')], 
                        ['none', 'toggle_maximize', 'minimize', 'toggle_shade', 'lower', 'menu'])],
                [gtk.Label(_('Titlebar right-click action')), 
                    Factory.create('gconfcombobox', 'action_right_click_titlebar', 
                        [_('None'), _('Maximize'), _('Minimize'), _('Roll up'), _('Lower'), _('Menu')], 
                        ['none', 'toggle_maximize', 'minimize', 'toggle_shade', 'lower', 'menu'])],
                ])

        self.pack_start(table, False, False, 0)

        button = Factory.create('gconfcheckbutton', _('Enable the Metacity compositing manager feature'), 'compositing_manager')
        if button:
            box = ListPack(_('Compositing Manager'), (button,))
            button.connect('toggled', self.on_compositing_button_toggled)

            self.pack_start(box, False, False, 0)

    def on_compositing_button_toggled(self, widget):
        if widget.get_active():
            InfoDialog(_('You sould turn off compiz')).launch()

if __name__ == '__main__':
    from utility import Test
    Test(Metacity)
