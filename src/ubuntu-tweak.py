#!/usr/bin/env python

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

import os
import gtk
import thread
import gettext

from Widgets import show_info
from Constants import *
gettext.install(App, unicode = True)

class TweakLauncher:
    def __init__(self):
            thread.start_new_thread(self.show_splash, ())

            try:
                from PackageWorker import update_apt_cache
            except ImportError:
                pass

            from MainWindow import MainWindow

            window = MainWindow()

    def show_splash(self):
        gtk.gdk.threads_enter()
        win = gtk.Window(gtk.WINDOW_POPUP)
        win.set_position(gtk.WIN_POS_CENTER)

        vbox = gtk.VBox(False, 0)
        image = gtk.Image()
        image.set_from_file('pixmaps/splash.png')

        vbox.pack_start(image)
        win.add(vbox)

        win.show_all()

        while gtk.events_pending ():
            gtk.main_iteration ()

        win.destroy()
        gtk.gdk.threads_leave()

    def main(self):
        os.system("./CheckVersion.py &")
        gtk.main()

if __name__ == "__main__":
    #determine whether the gnome is the default desktop
#    if os.getenv("GNOME_DESKTOP_SESSION_ID"):
#        from SystemInfo import GnomeVersion
#        if GnomeVersion.minor < 18:
#            show_info(_("Sorry!\n\nUbuntu Tweak can only run under <b>GNOME 2.18 or above.</b>\n"))
#        else:
            gtk.gdk.threads_init()
            launcher = TweakLauncher()
            launcher.main()
#    else:
#        show_info(_("Sorry!\n\nUbuntu Tweak can only run in <b>GNOME Desktop.</b>\n"))
