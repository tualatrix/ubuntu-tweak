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

import thread

from gi.repository import GObject, Gtk, Gdk, Pango, Vte

from ubuntutweak.gui.gtk import set_busy, unset_busy


class BaseDialog(Gtk.MessageDialog):
    def __init__(self, **kwargs):
        title = kwargs.pop('title', '')
        message = kwargs.pop('message', '')

        GObject.GObject.__init__(self, **kwargs)

        if title:
            self.set_title(title)

        if message:
            self.set_content(message)

    def set_title(self, title):
        self.set_markup('<big><b>%s</b></big>' % title)

    def set_content(self, message):
        if self.get_property('text'):
            self.format_secondary_markup(message)
        else:
            self.set_markup(message)
    
    def launch(self):
        self.run()
        self.destroy()

    def add_option_button(self, button):
        '''Add an option button to the left. It will not grab the default response.'''
        vbox = self.get_content_area()
        hbuttonbox = vbox.get_children()[-1]

        hbox = Gtk.HBox(spacing=12)
        vbox.pack_start(hbox, False, False, 0)
        vbox.remove(hbuttonbox)

        new_hbuttonbox = Gtk.HButtonBox()
        new_hbuttonbox.set_layout(Gtk.ButtonBoxStyle.START)
        new_hbuttonbox.pack_start(button, True, True, 0)

        hbox.pack_start(new_hbuttonbox, True, True, 0)
        hbox.pack_start(hbuttonbox, True, True, 0)

        hbuttonbox.get_children()[-1].grab_focus()

        vbox.show_all()


class ErrorDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, message_type=type, buttons=buttons)


class InfoDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, message_type=type, buttons=buttons)


class WarningDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, message_type=type, buttons=buttons)


class QuestionDialog(BaseDialog):
    def __init__(self, title='', message='', parent=None,
                 type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO):
        BaseDialog.__init__(self, title=title, message=message,
                            parent=parent, message_type=type, buttons=buttons)


class BusyDialog(Gtk.Dialog):
    def __init__(self, parent=None):
        GObject.GObject.__init__(self, parent=parent)

        if parent:
            self.parent_window = parent
        else:
            self.parent_window = None

    def set_busy(self):
        set_busy(self.parent_window)

    def unset_busy(self):
        unset_busy(self.parent_window)

    def run(self):
        self.set_busy()
        return super(BusyDialog, self).run()

    def destroy(self):
        self.unset_busy()
        super(BusyDialog, self).destroy()


class ProcessDialog(BusyDialog):
    __gsignals__ = {
        'error': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING,)),
        'done': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent):
        super(ProcessDialog, self).__init__(parent=parent)

        self.set_border_width(6)
        self.set_title('')
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        vbox = self.get_content_area()
        vbox.set_spacing(6)

        self._label = Gtk.Label()
        self._label.set_alignment(0, 0.5)
        vbox.pack_start(self._label, False, False, 0)

        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_ellipsize(Pango.EllipsizeMode.END)
        self._progressbar.set_size_request(320, -1)
        vbox.pack_start(self._progressbar, False, False, 0)

        self.show_all()

    def pulse(self):
        self._progressbar.pulse()

    def set_fraction(self, fraction):
        self._progressbar.set_fraction(fraction)

    def set_dialog_lable(self, text):
        self._label.set_markup('<b><big>%s</big></b>' % text)

    def set_progress_text(self, text):
        self._progressbar.set_text(text)

    def process_data(self):
        return NotImplemented


class SmartTerminal(Vte.Terminal):
    def insert(self, string):
        self.feed(string, -1)

    def future_insert(self, string):
        #TODO use this in Gtk+3.0
        column_count = self.get_column_count()
        column, row = self.get_cursor_position()
        if column == 0:
            column = column_count
        if column != column_count:
            self.feed(' ' * (column_count - column))
        space_length = column_count - len(string)
        string = string + ' ' * space_length
        self.feed(string)


class TerminalDialog(ProcessDialog):
    def __init__(self, parent):
        super(TerminalDialog, self).__init__(parent=parent)

        vbox = self.get_content_area()

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.expendar = Gtk.Expander()
        self.expendar.set_spacing(6)
        self.expendar.set_label(_('Details'))
        vbox.pack_start(self.expendar, False, False, 6)

        self.terminal = SmartTerminal()
        self.terminal.set_size_request(562, 362)
        self.expendar.add(self.terminal)

        self.show_all()


class AuthenticateFailDialog(ErrorDialog):
    def __init__(self):
        ErrorDialog.__init__(self,
                             title=_('Could not authenticate'),
                             message=_('An unexpected error has occurred.'))


class ServerErrorDialog(ErrorDialog):
    def __init__(self):
        ErrorDialog.__init__(self,
                             title=_("Service hasn't initialized yet"),
                             message=_('You need to restart your computer.'))
