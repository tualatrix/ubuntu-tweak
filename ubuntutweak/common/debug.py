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
import gtk
import logging
import StringIO
import traceback
import webbrowser

from ubuntutweak.common.gui import GuiWorker
from ubuntutweak.common.consts import CONFIG_ROOT
from ubuntutweak.common.systeminfo import SystemInfo

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

def run_traceback(level):
        output = StringIO.StringIO()
        exc = traceback.print_exc(file = output)

        worker = GuiWorker('traceback.ui')
        dialog = worker.get_object('%sDialog' % level.capitalize())
        textview = worker.get_object('%s_view' % level)
        buffer = textview.get_buffer()

        buffer.set_text("Distribution: %s\n"
                        "Application: %s\n"
                        "Desktop: %s\n"
                        "\n"
                        "%s" % (SystemInfo.distro,
                                SystemInfo.app,
                                SystemInfo.desktop,
                                output.getvalue()))
        if dialog.run() == gtk.RESPONSE_YES:
            webbrowser.open('https://bugs.launchpad.net/ubuntu-tweak/+filebug')
        dialog.destroy()
        output.close()

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        if self.use_color:
            record.levelname = COLORS.get(record.levelname, record.levelname)
        return logging.Formatter.format(self, record)

# Custom logger class with multiple destinations
class UbuntuTweakLogger(logging.Logger):
    COLOR_FORMAT = "["+BOLD_SEQ+"%(name)s"+RESET_SEQ+"][%(levelname)s] %(message)s ("+BOLD_SEQ+"%(filename)s"+RESET_SEQ+":%(lineno)d)"
    NO_COLOR_FORMAT = "[%(name)s][%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"
    LOG_FILE_HANDLER = None

    def __init__(self, name):
        logging.Logger.__init__(self, name)

        #Add two handlers, a stderr one, and a file one
        color_formatter = ColoredFormatter(UbuntuTweakLogger.COLOR_FORMAT)
        no_color_formatter = ColoredFormatter(UbuntuTweakLogger.NO_COLOR_FORMAT, False)

        #create the single file appending handler
        if UbuntuTweakLogger.LOG_FILE_HANDLER == None:
            filename = os.path.join(CONFIG_ROOT,'ubuntu-tweak.log')
            UbuntuTweakLogger.LOG_FILE_HANDLER = logging.FileHandler(filename, 'w')
            UbuntuTweakLogger.LOG_FILE_HANDLER.setFormatter(no_color_formatter)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(UbuntuTweakLogger.LOG_FILE_HANDLER)
        self.addHandler(console)
        return

def enable_debugging():
    logging.getLogger().setLevel(logging.DEBUG)

def disable_debugging():
    logging.getLogger().setLevel(logging.INFO)

def disable_logging():
    logging.getLogger().setLevel(logging.CRITICAL+1)

logging.setLoggerClass(UbuntuTweakLogger)
