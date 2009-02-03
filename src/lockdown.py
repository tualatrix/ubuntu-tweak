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

from common.factory import WidgetFactory
from common.widgets import ListPack, TweakPage

class LockDown(TweakPage):
    """Lock down some function"""
    def __init__(self):
        TweakPage.__init__(self)

        box = ListPack(_("System Security options"), (
                    WidgetFactory.create("GconfCheckButton", 
                                         label = _("Disable \"Run Application\" dialog (Alt+F2)"), 
                                         key = "disable_command_line"),
                    WidgetFactory.create("GconfCheckButton",
                                         label = _('Disable "Lock Screen"'), 
                                         key = "disable_lock_screen"),
                    WidgetFactory.create("GconfCheckButton", 
                                         label = _("Disable printing"), 
                                         key = "disable_printing"),
                    WidgetFactory.create("GconfCheckButton", 
                                         label = _("Disable print setup"), 
                                         key = "disable_print_setup"),
                    WidgetFactory.create("GconfCheckButton", 
                                         label = _("Disable save to disk"), 
                                         key = "disable_save_to_disk"),
                    WidgetFactory.create("GconfCheckButton", 
                                         label = _('Disable "Fast User Switching"'), 
                                         key = "disable_user_switching"),
            ))

        self.pack_start(box, False, False, 0)

if __name__ == "__main__":
    from utility import Test
    Test(LockDown)
