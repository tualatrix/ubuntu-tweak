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

from ubuntutweak.modules  import TweakModule
from ubuntutweak.factory import WidgetFactory
from ubuntutweak.gui.containers import ListPack, TablePack
from ubuntutweak.gui.dialogs import ErrorDialog

class Session(TweakModule):
    __title__ = _('Session Control')
    __desc__ = _('Control your system session releated features')
    __icon__ = 'gnome-session-hibernate'
    __category__ = 'startup'

    def __init__(self):
        TweakModule.__init__(self)

        box = ListPack(_("Session Menu Options"), (
                  WidgetFactory.create("CheckButton",
                      label=_("Remove the log out item from the session menu"),
                      enable_reset=True,
                      backend=Gio,
                      key="com.canonical.indicator.session.suppress-logout-menuitem"),
                  WidgetFactory.create("CheckButton",
                      label=_("Remove the restart item from the session menu"),
                      enable_reset=True,
                      backend=Gio,
                      key="com.canonical.indicator.session.suppress-restart-menuitem"),
                  WidgetFactory.create("CheckButton",
                      label=_("Remove the shutdown item from the session menu"),
                      enable_reset=True,
                      backend=Gio,
                      key="com.canonical.indicator.session.suppress-shutdown-menuitem"),
                  WidgetFactory.create("CheckButton",
                      label=_("Suppress the dialog to confirm logout, restart and shutdown action"),
                      enable_reset=True,
                      backend=Gio,
                      key="com.canonical.indicator.session.suppress-logout-restart-shutdown"),
                ))

        self.add_start(box, False, False, 0)

        box = ListPack(_("User Menu Options"), (
                    WidgetFactory.create("CheckButton",
                                    label=_('Show user menu'),
                                    enable_reset=True,
                                    backend=Gio,
                                    key='com.canonical.indicator.session.user-show-menu'),
                    WidgetFactory.create("CheckButton",
                                    label=_("Show user's real name on the panel"),
                                    enable_reset=True,
                                    backend=Gio,
                                    key="com.canonical.indicator.session.show-real-name-on-panel"),
            ))
        self.add_start(box, False, False, 0)
