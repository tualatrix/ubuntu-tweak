#!/usr/bin/python
# coding: utf-8

import os
import sys
import pygtk
pygtk.require('2.0')
import gtk
import gconf
import urllib
import thread
import socket
import threading
import gobject

from common.consts import *
from common.systeminfo import SystemInfo
from xmlrpclib import ServerProxy, Error
from common.config import TweakSettings

socket.setdefaulttimeout(10)

class Downloader(gobject.GObject):
    __gsignals__ = {
              'downloading': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
              }

    tempdir = os.path.join(os.path.join(os.getenv("HOME"), '.ubuntu-tweak', 'temp'))

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

    def start(self, remote_uri):
        if not os.path.exists(self.tempdir) or os.path.isfile(self.tempdir):
            self.create_tempdir()
        self.clean_tempdir()

        self.save_to = os.path.join(self.tempdir, os.path.basename(remote_uri))

        urllib.urlretrieve(remote_uri, self.save_to, self.update_progress)

    def update_progress(self, blocks, block_size, total_size):
        self.percentage = float(blocks * block_size) / total_size
        self.emit('downloading')

class UpdateManager(gtk.Window):
    time_count = 1

    def __init__(self, parent = None):
        gtk.Window.__init__(self)

        self.__settings = TweakSettings()

        self.set_modal(True)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_size_request(360, 40)
        self.set_title(_('Update Manager'))
        self.connect('destroy', lambda *w: self.destroy())
        if parent:
            self.set_transient_for(parent)

        self.progress_bar = gtk.ProgressBar()
        self.add(self.progress_bar)
        self.downloader = Downloader()
        self.downloader.connect('downloading', self.on_downloading)

        self.show_all()
        self.start_download(self.__settings.get_url())

    def on_downloading(self, widget):
        percentage = self.downloader.percentage

        if percentage < 1:
            self.progress_bar.set_text(_('Downloading...%d') % int(percentage * 100)+ '%')
            self.progress_bar.set_fraction(percentage)

            return True
        else:
            gobject.timeout_add(1000, self.on_start_install)

    def on_start_install(self):
        thread.start_new_thread(self.start_install, ())

    def start_install(self):
        gtk.gdk.threads_enter()

        os.system('gdebi-gtk %s &' % self.downloader.save_to)
        gtk.main_quit()

        gtk.gdk.threads_leave()

    def start_download(self, url):
        thread.start_new_thread(self.download_thread, (url,))

    def download_thread(self, url):
        self.downloader.start(url)

    def check_percentage(self):
        percentage = self.downloader.percentage

        if percentage < 1:
            self.progress_bar.set_text(_("Downloading...%d") % int(percentage * 100)+ '%')
            self.progress_bar.set_fraction(percentage)

            return True
        else:
            self.progress_bar.set_text(_("Finished"))
            self.progress_bar.set_fraction(1)
            gobject.timeout_add(1000, self.on_start_install)

    def main(self):
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
    
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
