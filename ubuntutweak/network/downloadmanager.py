#!/usr/bin/python
# coding: utf-8

import os
import gtk
import urllib
import thread
import socket
import gobject

from xmlrpclib import ServerProxy, Error
from ubuntutweak.conf import settings
from ubuntutweak.widgets.dialogs import BusyDialog

#TODO old stuff
from ubuntutweak.common.consts import *
from ubuntutweak.common.config import TweakSettings

socket.setdefaulttimeout(10)

class Downloader(gobject.GObject):
    __gsignals__ = {
      'downloading': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
      'downloaded': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }

    tempdir = os.path.join(settings.CONFIG_ROOT, 'temp')

    def __init__(self, url=None):
        if url:
            self.url = url
        super(Downloader, self).__init__()

    def create_tempdir(self):
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)
        else:
            if not os.path.isdir(self.tempdir): 
                os.remove(self.tempdir)
                os.mkdir(self.tempdir)

    def clean_tempdir(self):
        for root, dirs, files in os.walk(self.tempdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def start(self, url=None):
        if not os.path.exists(self.tempdir) or os.path.isfile(self.tempdir):
            self.create_tempdir()
        self.clean_tempdir()

        if url:
            self.url = url

        self.save_to = os.path.join(self.tempdir, os.path.basename(self.url))
        urllib.urlretrieve(self.url, self.save_to, self.update_progress)

    def update_progress(self, blocks, block_size, total_size):
        percentage = float(blocks*block_size)/total_size
        if percentage < 1:
            self.emit('downloading', percentage)
        else:
            self.emit('downloaded')

    def get_downloaded_file(self):
        return self.save_to

class DownloadDialog(BusyDialog):
    time_count = 1

    def __init__(self, url=None, title=None, parent=None):
        BusyDialog.__init__(self, parent=parent)

        self.set_default_size(320, -1)
        self.set_title('')
        self.set_has_separator(False)
        self.set_border_width(8)

        vbox = self.get_child()
        vbox.set_spacing(6)

        if title:
            label = gtk.Label()
            label.set_alignment(0, 0.5)
            label.set_markup('<big><b>%s</b></big>' % title)
            vbox.pack_start(label, False, False, 0)

        self.wait_text = _('Connecting to server')
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_text(self.wait_text)
        vbox.pack_start(self.progress_bar, True, False, 0)

        if url:
            self.url = url
            self.downloader = Downloader(url)
        else:
            self.downloader = Downloader()

        self.downloader.connect('downloading', self.on_downloading)
        self.downloader.connect('downloaded', self.on_downloaded)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.show_all()

        gobject.timeout_add(1000, self.on_network_connect)

    def on_network_connect(self):
        if self.time_count != -1:
            self.progress_bar.set_text(self.wait_text+'.' * self.time_count)
            if self.time_count < 3:
                self.time_count += 1
            else:
                self.time_count = 1

            return True

    def run(self):
        thread.start_new_thread(self._download_thread, ())
        return super(DownloadDialog, self).run()

    def destroy(self):
        super(DownloadDialog, self).destroy()

    def set_url(self, url):
        self.url = url

    def on_downloading(self, widget, percentage):
        if self.time_count != -1:
            self.time_count = -1

        if percentage < 1:
            self.progress_bar.set_text(_('Downloading...%d') % int(percentage * 100)+ '%')
            self.progress_bar.set_fraction(percentage)

    def on_downloaded(self, widget):
        self.progress_bar.set_text(_('Downloaded!'))
        self.progress_bar.set_fraction(1)
        self.response(gtk.RESPONSE_DELETE_EVENT)

    def _download_thread(self):
        self.downloader.start(self.url)

def CheckVersion():
    server = ServerProxy("http://ubuntu-tweak.appspot.com/xmlrpc")
    settings = TweakSettings()

    try:
        version = server.version()
        url = server.get_url()
    except Error, e:
        print "Error:", e
    except socket.gaierror:
        print "Bad Network!"
    else:
        settings.set_version(version)
        settings.set_url(url)

if __name__ == "__main__":
    CheckVersion()
