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
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from ubuntutweak.modules  import TweakModule
from ubuntutweak.common.consts import *
from ubuntutweak.widgets import ListPack, SinglePack
from ubuntutweak.common.factory import WidgetFactory

class Session(TweakModule):
    __title__ = _('Session control')
    __desc__ = _('Control your system session releated features')
    __icon__ = 'gnome-session-hibernate'
    __category__ = 'startup'

    def __init__(self):
        TweakModule.__init__(self)

        self.add_start(self.session_control_box(), False, False, 0)

    def session_control_box(self):
        button = WidgetFactory.create("GconfCheckButton", 
                                      label = _("Automatically save open applications when logging out"), 
                                      key = "auto_save_session")
        button2 = WidgetFactory.create("GconfCheckButton", 
                                       label = _("Show logout prompt"), 
                                       key = "logout_prompt")
        button3 = WidgetFactory.create("GconfCheckButton", 
                                       label = _("Allow TCP Connections (Remote Desktop Connect)"), 
                                       key = "allow_tcp_connections")

        box = ListPack(_("Session Control"), (button, button2, button3))
        return box
