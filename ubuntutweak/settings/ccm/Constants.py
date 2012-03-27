# -*- coding: UTF-8 -*-

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors: Quinn Storm (quinn@beryl-project.org)
#          Patrick Niklaus (marex@opencompositing.org)
#          Guillaume Seguin (guillaume@segu.in)
#          Christopher Williams (christopherw@verizon.net)
# Copyright (C) 2007 Quinn Storm

from gi.repository import Gtk, Gdk

# Current Screen
#
CurrentScreenNum = Gdk.Display.get_default().get_n_screens()

# Settings Table
#
TableDef = Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND
TableX   = 4
TableY   = 2

# Action Constants
#
KeyModifier = ["Shift", "Control", "Mod1", "Mod2", "Mod3", "Mod4",
               "Mod5", "Alt", "Meta", "Super", "Hyper", "ModeSwitch"]
Edges       = ["Left", "Right", "Top", "Bottom",
               "TopLeft", "TopRight", "BottomLeft", "BottomRight"]

# Label Styles
#
HeaderMarkup = "<span size='large' weight='800'>%s</span>"

# Image Types
#
ImageNone     = 0
ImagePlugin   = 1
ImageCategory = 2
ImageThemed   = 3
ImageStock    = 4

# Filter Levels
#
FilterName = 1 << 0
FilterLongDesc = 1 << 1
FilterValue = 1 << 2    # Settings Only
FilterCategory = 1 << 3 # Plugins Only
FilterAll = FilterName | FilterLongDesc | FilterValue | FilterCategory

# Paths
#
DataDir = "/usr/share"
IconDir = DataDir+"/ccsm/icons"
PixmapDir = DataDir+"/ccsm/images"

# Version
#
Version = "0.9.4"


# Translation
#
import locale
import gettext
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain("ccsm", DataDir + "/locale")
gettext.textdomain("ccsm")
_ = gettext.gettext

# Category Transaltion Table
# Just to get them into gettext
#
CategoryTranslation = {
"General": _("General"),
"Accessibility": _("Accessibility"),
"Desktop": _("Desktop"),
"Extras": _("Extras"),
"Window Management": _("Window Management"),
"Effects": _("Effects"),
"Image Loading": _("Image Loading"),
"Utility": _("Utility"),
"All": _("All"),
"Uncategorized": _("Uncategorized")
}
