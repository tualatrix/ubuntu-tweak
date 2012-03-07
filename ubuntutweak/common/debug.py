#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
#
# Copyright (C) 2007-2010 TualatriX <tualatrix@gmail.com>
# The Logging System is hacked from Conduit
# Copyright (C) Conduit Authors
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
import logging
import StringIO
import traceback
import webbrowser

from gi.repository import Gtk, Gdk, Notify

from ubuntutweak import system
from ubuntutweak.common.consts import CONFIG_ROOT

#The terminal has 8 colors with codes from 0 to 7
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ =  "\033[1m"

#The background is set with 40 plus the number of the color,
#and the foreground with 30
COLORS = {
    'WARNING':  COLOR_SEQ % (30 + YELLOW) + 'WARNING' + RESET_SEQ,
    'INFO':     COLOR_SEQ % (30 + WHITE) + 'INFO' + RESET_SEQ,
    'DEBUG':    COLOR_SEQ % (30 + BLUE) + 'DEBUG' + RESET_SEQ,
    'CRITICAL': COLOR_SEQ % (30 + YELLOW) + 'CRITICAL' + RESET_SEQ,
    'ERROR':    COLOR_SEQ % (30 + RED) + 'ERROR' + RESET_SEQ,
}


def on_copy_button_clicked(widget, text):
    atom = Gdk.atom_intern('CLIPBOARD', True)
    clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), atom)
    clipboard.set_text(text, -1)

    notify = Notify.Notification()
    notify.update(summary=_('Error message has been copied'),
                  body=_('Now click "Report" to enter the bug '
                         'report website. Make sure to attach the '
                         'error message in "Further information".'),
                  icon='ubuntu-tweak')
    notify.show()


def run_traceback(level, textview_only=False, text_only=False):
    '''Two level: fatal and error'''
    from ubuntutweak.gui import GuiBuilder

    output = StringIO.StringIO()
    exc = traceback.print_exc(file=output)

    worker = GuiBuilder('traceback.ui')

    textview = worker.get_object('%s_view' % level)

    buffer = textview.get_buffer()
    iter = buffer.get_start_iter()
    anchor = buffer.create_child_anchor(iter)
    button = Gtk.Button(label=_('Copy Error Message'))
    button.show()

    textview.add_child_at_anchor(button, anchor)

    error_text = "\nDistribution: %s\nApplication: %s\nDesktop:%s\n\n%s" % (system.DISTRO,
                                       system.APP,
                                       system.DESKTOP,
                                       output.getvalue())

    buffer.insert(iter, error_text)
    button.connect('clicked', on_copy_button_clicked, error_text)

    if text_only:
        return error_text

    if textview_only:
        return textview
    else:
        dialog = worker.get_object('%sDialog' % level.capitalize())

        to_report = (dialog.run() == Gtk.ResponseType.YES)

        dialog.destroy()
        output.close()

        if to_report:
            open_bug_report()


def open_bug_report():
    if system.is_supported():
        webbrowser.open('https://bugs.launchpad.net/ubuntu-tweak/+filebug')
    else:
        from ubuntutweak.gui.dialogs import ErrorDialog
        ErrorDialog(title=_("Sorry, your distribution is not supported by Ubuntu Tweak"),
                    message=_("You can't file bug for this issue. Please only use Ubuntu Tweak on Ubuntu. Or it may kill your cat.")).launch()


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        if self.use_color:
            record.levelname = COLORS.get(record.levelname, record.levelname)
        return logging.Formatter.format(self, record)


class TweakLogger(logging.Logger):
    COLOR_FORMAT = "[" + BOLD_SEQ + "%(name)s" + RESET_SEQ + \
                   "][%(levelname)s] %(message)s (" + BOLD_SEQ + \
                   "%(filename)s" + RESET_SEQ + ":%(lineno)d)"
    NO_COLOR_FORMAT = "[%(name)s][%(levelname)s] %(message)s " \
                      "(%(filename)s:%(lineno)d)"
    LOG_FILE_HANDLER = None

    def __init__(self, name):
        logging.Logger.__init__(self, name)

        #Add two handlers, a stderr one, and a file one
        color_formatter = ColoredFormatter(TweakLogger.COLOR_FORMAT)
        no_color_formatter = ColoredFormatter(TweakLogger.NO_COLOR_FORMAT,
                                              False)

        #create the single file appending handler
        if TweakLogger.LOG_FILE_HANDLER == None:
            filename = os.path.join(CONFIG_ROOT, 'ubuntu-tweak.log')
            TweakLogger.LOG_FILE_HANDLER = logging.FileHandler(filename, 'w')
            TweakLogger.LOG_FILE_HANDLER.setFormatter(no_color_formatter)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(TweakLogger.LOG_FILE_HANDLER)
        self.addHandler(console)
        return


def enable_debugging():
    logging.getLogger().setLevel(logging.DEBUG)


def disable_debugging():
    logging.getLogger().setLevel(logging.INFO)


def disable_logging():
    logging.getLogger().setLevel(logging.CRITICAL + 1)

logging.setLoggerClass(TweakLogger)

def log_func(log):
    def wrap(func):
        def func_wrapper(*args, **kwargs):
            log.debug("%s:" % func)
            for i, arg in enumerate(args):
                log.debug("\targs-%d: %s" % (i + 1, arg))
            for k, v in enumerate(kwargs):
                log.debug("\tdict args: %s: %s" % (k, v))
            return func(*args, **kwargs)
        return func_wrapper
    return wrap
