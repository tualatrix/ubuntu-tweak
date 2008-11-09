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

class BaseMessageDialog(gtk.MessageDialog):
    def __init__(self, type, buttons):
        gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL, type, buttons)

    def set_title(self, title):
        self.set_markup('<big><b>%s</b></big>' % title)

    def set_content(self, message, title):
        if title:
            self.set_title(title)
            self.format_secondary_markup(message)
        else:
            self.set_markup(message)

    def launch(self):
        self.run()
        self.destroy()

class InfoDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_OK, title = None):
        BaseMessageDialog.__init__(self, type, buttons)
        self.set_content(message, title)

class QuestionDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO, title = None):
        BaseMessageDialog.__init__(self, type, buttons)
        self.set_content(message, title)

class ErrorDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, title = None):
        BaseMessageDialog.__init__(self, type, buttons)
        self.set_content(message, title)

class WarningDialog(BaseMessageDialog):
    def __init__(self, message, type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_YES_NO, title = None):
        BaseMessageDialog.__init__(self, type, buttons)
        self.set_content(message, title)

class AuthenticateFailDialog(ErrorDialog):
    def __init__(self):
        ErrorDialog.__init__(_('An unexpected error has occurred.'), 
                title = _('Could not authenticate'))

class ServerErrorDialog(ErrorDialog):
    def __init__(self):
        ErrorDialog.__init__(_('You need to restart your computer.'), 
                title = _("Service hasn't initialized yet"))
