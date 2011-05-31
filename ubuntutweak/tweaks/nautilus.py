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

import gobject
from gi.repository import GConf

from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.gui.containers import ListPack, TablePack


class Nautilus(TweakModule):
    __title__ = _('Nautilus Settings')
    __desc__ = _('Manage the default file manager')
    __icon__ = ['file-manager', 'nautilus']
    __category__ = 'system'

    def __init__(self):
        TweakModule.__init__(self)

        box = ListPack(_("File Browser"), (
                  WidgetFactory.create("CheckButton",
                                       label=_('Show advanced permissions in the Nautilus "File Properties" window'),
                                       enable_reset=True,
                                       key="/apps/nautilus/preferences/show_advanced_permissions",
                                       backend=GConf),
                  WidgetFactory.create("CheckButton",
                                       label=_('Always use the location entry, instead of the pathbar'),
                                       enable_reset=True,
                                       key="/apps/nautilus/preferences/always_use_location_entry",
                                       backend=GConf)))
        self.add_start(box, False, False, 0)

        box = TablePack(_('Thumbnail Settings'), (
                    WidgetFactory.create('SpinButton',
                                         key='/apps/nautilus/icon_view/thumbnail_size',
                                         enable_reset=True,
                                         min=16, max=512, step=16,
                                         label=_('Default thumbnail icon size (pixels)'),
                                         backend=GConf),
                    WidgetFactory.create('SpinButton',
                                         key='/desktop/gnome/thumbnail_cache/maximum_size',
                                         enable_reset=True,
                                         min=-1, max=512, step=1,
                                         label=_('Maximum thumbnail cache size (megabytes)'),
                                         backend=GConf),
                    WidgetFactory.create('SpinButton',
                                          key='/desktop/gnome/thumbnail_cache/maximum_age',
                                          enable_reset=True,
                                          min=-1, max=180, step=1,
                                          label=_('Thumbnail cache time (days)'),
                                          backend=GConf),
            ))
        self.add_start(box, False, False, 0)
