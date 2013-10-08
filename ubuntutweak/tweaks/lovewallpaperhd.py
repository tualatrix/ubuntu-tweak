# -*- coding: utf-8 -*-

import os
import json
import thread
import urllib2
import logging

from gi.repository import Notify, GLib, Gtk, Gdk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf

from ubuntutweak.settings.gsettings import GSetting
from ubuntutweak.common.consts import CONFIG_ROOT
from ubuntutweak.modules  import TweakModule
from ubuntutweak.network.downloadmanager import DownloadDialog

log = logging.getLogger('LovewallpaperHD')

class LovewallpaperHD(TweakModule):
    __title__ = _("Love Wallpaper HD")
    __desc__ = _('Browse online gallery and find your wallpaper')
    __icon__ = 'love-wallpaper.png'
    __category__ = 'desktop'

    __author__ = 'kevinzhow <kevinchou.c@gmail.com>'
    __url__ = 'http://imkevin.me'
    __url_title__ = 'Kevin Blog'

    def __init__(self):
        TweakModule.__init__(self)

        self.wallpaper_path = os.path.join(CONFIG_ROOT, 'lovewallpaper.jpg')
        self.jsonman = JsonMan(Gdk.Screen.width(), Gdk.Screen.height())

        self.image_model = Gtk.ListStore(Pixbuf, str)
        self.image_view = Gtk.IconView.new_with_model(self.image_model)
        self.image_view.set_property('halign', Gtk.Align.CENTER)
        self.image_view.set_column_spacing(5)
        self.image_view.set_item_padding(5)
        self.image_view.set_item_width(175)
        self.image_view.set_pixbuf_column(0)
        self.image_view.connect("item-activated", self.set_wallpaper)

        link_label = Gtk.Label()
        link_label.set_markup('Powered by <a href="http://www.lovebizhi.com/linux">%s</a>.' % self.__title__)
        link_label.set_line_wrap(True)

        lucky_button = Gtk.Button(_("I'm Feeling Lucky"))
        lucky_button.set_property('halign', Gtk.Align.CENTER)
        lucky_button.connect('clicked', self.on_luky_button_clicked)

        self.connect('size-allocate', self.on_size_allocate)

        try:
            self.load_imageview()
            self.add_start(self.image_view, False, False, 0)
            self.add_start(lucky_button, False, False, 0)
        except Exception, e:
            link_label.set_markup('Network issue happened when visiting <a href="http://www.lovebizhi.com/linux">%s</a>. Please check if you can access the website.' % self.__title__)
        finally:
            self.add_start(link_label, False, False, 0)

    def on_luky_button_clicked(self, widget):
        self.load_imageview()

    def load_imageview(self):
        self.image_model.clear()
        self.jsonman.get_json()
        self.image_list = self.jsonman.create_tryluck()

        for image in self.image_list:
            thread.start_new_thread(self.add_image, (image,))

    def on_size_allocate(self, width, allocation):
        if allocation.width > 0:
            self.image_view.set_columns(allocation.width / 195)

    def add_image(self, image):
        gtkimage = Gtk.Image()
        response = urllib2.urlopen(image.small)

        loader = GdkPixbuf.PixbufLoader()
        loader.write(response.read())
        loader.close()
        gtkimage.set_from_pixbuf(loader.get_pixbuf())
        self.image_model.append([gtkimage.get_pixbuf(), image.big])

    def set_wallpaper(self, view, path):
        url = self.image_model[path][1]
        dialog = DownloadDialog(url=url,
                                title=_('Downloading Wallpaper'),
                                parent=view.get_toplevel())
        dialog.downloader.connect('downloaded', self.on_wallpaper_downloaded)

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.CANCEL:
            log.debug("Download cancelled by user")
            dialog.downloader.disconnect_by_func(self.on_wallpaper_downloaded)

    def on_wallpaper_downloaded(self, downloader):
        os.rename(downloader.get_downloaded_file(), self.wallpaper_path)

        wallpaper_setting = GSetting('org.gnome.desktop.background.picture-uri')
        wallpaper_setting.set_value(GLib.filename_to_uri(self.wallpaper_path, None))

        n = Notify.Notification.new(self.__title__, "Set wallpaper successfully!", 'ubuntu-tweak')
        n.show()


class Picture:
    def __init__(self, small, big, num):
        self.small = small
        self.big = big
        self.key = num


class JsonMan:
    def __init__(self, screen_width=None, screen_height=None, parent=None):
        self.screen_height = str(screen_height)
        self.screen_width = str(screen_width)

    def get_json(self):
        json_init_url = "http://partner.lovebizhi.com/ubuntutweak.php?width=" + self.screen_width + "&height=" + self.screen_height
        fd = urllib2.urlopen(json_init_url, timeout=10).read().decode("utf-8")
        self.index = json.loads(fd)

    def create_tryluck(self):
        self.tryluck_list = []
        num = 0
        for tryluck_image in self.index:
            num += 1
            self.tryluck_list.append(Picture(tryluck_image["s"],
                                             tryluck_image['b'],
                                             str(num)))
        return self.tryluck_list
