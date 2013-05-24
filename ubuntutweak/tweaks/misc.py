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
import re
import logging
from gi.repository import Gtk, Gio

from ubuntutweak import system
from ubuntutweak.gui.containers import ListPack, GridPack
from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory

log = logging.getLogger('Misc')

class Misc(TweakModule):
    __title__ = _('Miscellaneous')
    __desc__ = _('Set the cursor timeout, menus and buttons icons')
    __icon__ = 'gconf-editor'
    __category__ = 'appearance'

    utext_natural = _('Natural Scrolling')
    utext_menu_icon = _('Menus have icons')
    utext_button_icon = _('Buttons have icons')
    utext_context_menu = _("Show Input Method menu in the context menu")
    utext_unicode = _("Show Unicode Control Character menu in the context menu")
    utext_disable_print = _("Disable printing")
    utext_disable_print_setting = _("Disable printer settings")
    utext_save = _("Disable save to disk")
    utext_user_switch = _('Disable "Fast User Switching"')
    utext_cursor_blink = _('Cursor blink:')
    utext_overlay_scrollbar = _('Overlay scrollbars:')
    utext_cursor_blink_time = _('Cursor blink time:')
    utext_cursor_blink_timeout = _('Cursor blink timeout:')

    def __init__(self):
        TweakModule.__init__(self)

        self.natural_scrolling_switch = Gtk.Switch()
        self.set_the_natural_status()
        self.natural_scrolling_switch.connect('notify::active', self.on_natural_scrolling_changed)

        notes_label = Gtk.Label()
        notes_label.set_property('halign', Gtk.Align.START)
        notes_label.set_markup('<span size="smaller">%s</span>' % \
                _('Note: you may need to log out to take effect'))
        notes_label._ut_left = 1

        if system.CODENAME == 'precise':
           overlay_label, overlay_widget = WidgetFactory.create('Switch',
                                                 label=self.utext_overlay_scrollbar,
                                                 key='org.gnome.desktop.interface.ubuntu-overlay-scrollbars',
                                                 backend='gsettings')
        else:
          overlay_label, overlay_widget = WidgetFactory.create('ComboBox',
                                                 label=self.utext_overlay_scrollbar,
                                                 key='com.canonical.desktop.interface.scrollbar-mode',
                                                 texts=[_('Normal'),
                                                        _('Auto'),
                                                        _('Show Overlay'),
                                                        _('Never Show Overlay')],
                                                 values=['normal',
                                                         'overlay-auto',
                                                         'overlay-pointer',
                                                         'overlay-touch'],
                                                 backend='gsettings')

        self.theme_box = GridPack(
                            WidgetFactory.create('CheckButton',
                                                 label=self.utext_menu_icon,
                                                 key='org.gnome.desktop.interface.menus-have-icons',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('CheckButton',
                                label=self.utext_button_icon,
                                key='org.gnome.desktop.interface.buttons-have-icons',
                                backend='gsettings'),
                            WidgetFactory.create('CheckButton',
                                                 label=self.utext_context_menu,
                                                 key='org.gnome.desktop.interface.show-input-method-menu',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('CheckButton',
                                                 label=self.utext_unicode,
                                                 key='org.gnome.desktop.interface.show-unicode-menu',
                                                 backend='gsettings',
                                                 ),
                            Gtk.Separator(),
                            WidgetFactory.create("CheckButton",
                                                 label=self.utext_disable_print,
                                                 key="org.gnome.desktop.lockdown.disable-printing",
                                                 backend="gsettings",
                                                 blank_label=True),
                            WidgetFactory.create("CheckButton",
                                                 label=self.utext_disable_print_setting,
                                                 key="org.gnome.desktop.lockdown.disable-print-setup",
                                                 backend="gsettings",
                                                 blank_label=True),
                            WidgetFactory.create("CheckButton",
                                                 label=self.utext_save,
                                                 key="org.gnome.desktop.lockdown.disable-save-to-disk",
                                                 backend="gsettings",
                                                 blank_label=True),
                            WidgetFactory.create("CheckButton",
                                                 label=self.utext_user_switch,
                                                 key="org.gnome.desktop.lockdown.disable-user-switching",
                                                 backend="gsettings",
                                                 blank_label=True),
                            Gtk.Separator(),
                            (Gtk.Label(self.utext_natural), self.natural_scrolling_switch),
                            notes_label,
                            (overlay_label, overlay_widget),
                            WidgetFactory.create('Switch',
                                                 label=self.utext_cursor_blink,
                                                 key='org.gnome.desktop.interface.cursor-blink',
                                                 backend='gsettings',
                                                 ),
                            WidgetFactory.create('Scale',
                                                 label=self.utext_cursor_blink_time,
                                                 key='org.gnome.desktop.interface.cursor-blink-time',
                                                 backend='gsettings',
                                                 min=100,
                                                 max=2500,
                                                 step=100,
                                                 type=int,
                                                 ),
                            WidgetFactory.create('SpinButton',
                                                 label=self.utext_cursor_blink_timeout,
                                                 key='org.gnome.desktop.interface.cursor-blink-timeout',
                                                 backend='gsettings',
                                                 min=1,
                                                 max=2147483647,
                                                 ))
        self.add_start(self.theme_box, False, False, 0)

    def get_pointer_id(self):
        pointer_ids = []
        id_pattern = re.compile('id=(\d+)')
        for line in os.popen('xinput list').read().split('\n'):
            if 'id=' in line and \
               'pointer' in line and \
               'slave' in line and \
               'XTEST' not in line:
                match = id_pattern.findall(line)
                if match:
                    pointer_ids.append(match[0])

        return pointer_ids

    def get_natural_scrolling_enabled(self):
        if not self.get_natural_scrolling_from_file():
            ids = self.get_pointer_id()
            value = len(ids)
            for id in ids:
                map = os.popen('xinput get-button-map %s' % id).read().strip()
                if '4 5' in map:
                    value -= 1
                elif '5 4' in map:
                    continue

            if value == 0:
                return False
            elif value == len(ids):
                return True
        return True

    def set_the_natural_status(self):
        self.natural_scrolling_switch.set_active(self.get_natural_scrolling_enabled())

    def on_natural_scrolling_changed(self, widget, *args):
        log.debug('>>>>> on_natural_scrolling_changed: %s' % widget.get_active())

        map = '1 2 3 4 5 6 7 8 9 10 11 12'

        if widget.get_active():
            map = map.replace('4 5', '5 4')
        else:
            map = map.replace('5 4', '4 5')

        self.save_natural_scrolling_to_file(map)
        os.system('xmodmap ~/.Xmodmap')

    def get_natural_scrolling_from_file(self):
        string = 'pointer = 1 2 3 5 4'
        xmodmap = os.path.expanduser('~/.Xmodmap')
        if os.path.exists(xmodmap):
            return string in open(xmodmap).read()
        else:
            return False

    def save_natural_scrolling_to_file(self, map):
        xmodmap = os.path.expanduser('~/.Xmodmap')
        map = map + '\n'
        string = 'pointer = %s' % map

        if os.path.exists(xmodmap):
            pattern = re.compile('pointer = ([\d\s]+)')
            data = open(xmodmap).read()
            match = pattern.search(data)
            if match:
                log.debug("Match in Xmodmap: %s" % match.groups()[0])
                data = data.replace(match.groups()[0], map)
            else:
                data = data + '\n' + string
        else:
            data = string

        log.debug('Will write the content to Xmodmap: %s' % data)
        with open(xmodmap, 'w') as f:
            f.write(data)
            f.close()
