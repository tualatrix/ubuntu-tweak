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

from gi.repository import Gtk, Unique

from ubuntutweak.common.consts import DATA_DIR

class GuiBuilder(object):
    def __init__(self, file_name):
        file_path = os.path.join(DATA_DIR, 'ui', file_name)

        self.builder = Gtk.Builder()
        self.builder.set_translation_domain('ubuntu-tweak')
        self.builder.add_from_file(file_path)
        self.builder.connect_signals(self)

        for o in self.builder.get_objects():
            if issubclass(type(o), Gtk.Buildable):
                name = Gtk.Buildable.get_name(o)
                setattr(self, name, o)
            else:
                print >>sys.stderr, "WARNING: can not get name for '%s'" % o

    def get_object(self, name):
        return self.builder.get_object(name)
