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

import os
from gi.repository import Gtk, Gio

from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

class Misc(TweakModule):
    __title__ = _('Miscellaneous')
    __desc__ = _('Set the cursor timeout, menus and buttons icons')
    __icon__ = 'gconf-editor'
    __category__ = 'appearance'

    def __init__(self):
        TweakModule.__init__(self)

        self.theme_box = TablePack(_('Buttons and Menus'), (
                            WidgetFactory.create('CheckButton',
                                                 label=_('Buttons have icons'),
                                                 key='org.gnome.desktop.interface.buttons-have-icons',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('CheckButton',
                                                 label=_('Menus have icons'),
                                                 key='org.gnome.desktop.interface.menus-have-icons',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('CheckButton',
                                                 label=_("Show Input Method menu in the context menu"),
                                                 key='org.gnome.desktop.interface.show-input-method-menu',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('CheckButton',
                                                 label=_("Show Unicode Control Character menu in the context menu"),
                                                 key='org.gnome.desktop.interface.show-unicode-menu',
                                                 backend='gsettings',
                                                 ),
                            ))
        self.add_start(self.theme_box, False, False, 0)

        self.theme_box = TablePack(_('Miscellaneous'), (
                            WidgetFactory.create('CheckButton',
                                                 label='Cursor blink',
                                                 key='org.gnome.desktop.interface.cursor-blink',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('Scale',
                                                 label='Cursor blink time',
                                                 key='org.gnome.desktop.interface.cursor-blink-time',
                                                 backend='gsettings',
                                                 min=100,
                                                 max=2500,
                                                 type=int,
                                                 ),
                            WidgetFactory.create('SpinButton',
                                                 label='Cursor blink timeout',
                                                 key='org.gnome.desktop.interface.cursor-blink-timeout',
                                                 backend='gsettings',
                                                 min=1,
                                                 max=2147483647,
                                                 ),
                            ))
        self.add_start(self.theme_box, False, False, 0)
