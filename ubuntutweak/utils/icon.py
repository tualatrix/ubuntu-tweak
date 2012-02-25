import os
import random
import logging

from gi.repository import Gtk, Gdk, Gio, GdkPixbuf

log = logging.getLogger("utils.icon")

icontheme = Gtk.IconTheme.get_default()
icontheme.append_search_path('/usr/share/ccsm/icons')

DEFAULT_SIZE = 24

def get_from_name(name='gtk-execute',
                  alter='',
                  size=DEFAULT_SIZE,
                  force_reload=False,
                  only_path=False):
    if force_reload:
        global icontheme
        icontheme = Gtk.IconTheme.get_default()

    name_list = [name, alter]

    gicon = Gio.ThemedIcon.new_from_names(name_list)

    if only_path:
        icon_info = icontheme.lookup_by_gicon(gicon,
                                              size,
                                              Gtk.IconLookupFlags.USE_BUILTIN)
        return icon_info.get_filename()

    icon_info = icontheme.lookup_by_gicon(gicon,
                                          size,
                                          Gtk.IconLookupFlags.USE_BUILTIN)

    return icon_info.load_icon()

def get_from_list(name_list, size=DEFAULT_SIZE):
    name_list.append('application-x-executable')

    gicon = Gio.ThemedIcon.new_from_names(name_list)

    icon_info = icontheme.lookup_by_gicon(gicon,
                                          size,
                                          Gtk.IconLookupFlags.USE_BUILTIN)

    return icon_info.load_icon()

def get_from_mime_type(mime, size=DEFAULT_SIZE):
    try:
        gicon = Gio.content_type_get_icon(mime)

        return get_from_list(gicon.get_names(), size=size)
    except Exception, e:
        log.error('get_from_mime_type failed: %s' % e)
        return get_from_name(size=size)

    return pixbuf

def get_from_file(file, size=DEFAULT_SIZE, only_path=False):
    try:
        return GdkPixbuf.Pixbuf.new_from_file_at_size(file, size, size)
    except Exception, e:
        log.error('get_from_file failed: %s' % e)
        return get_from_name(size=size, only_path=only_path)

def get_from_app(app, size=DEFAULT_SIZE):
    try:
        gicon = app.get_icon()
        pixbuf = None

        if gicon:
            if isinstance(gicon, Gio.ThemedIcon):
                return get_from_list(gicon.get_names(), size=size)
            elif isinstance(gicon, Gio.FileIcon):
                file = app.get_icon().get_file().get_path()
                return get_from_file(file, size)
        if not pixbuf:
            return get_from_name('application-x-executable', size=size)
    except Exception, e:
        log.error('get_from_app failed: %s' % e)
        return get_from_name(size=size)

def guess_from_path(filepath, size=DEFAULT_SIZE):
    if os.path.isdir(filepath):
        return get_from_name('folder', size)

    try:
        mime_type, result = Gio.content_type_guess(filepath, open(filepath).read(10))
        return get_from_mime_type(mime_type, size)
    except Exception, e:
        log.error('guess_from_path failed: %s' % e)
        return get_from_name(size=size)

if __name__ == '__main__':
    print get_from_name('ok', alter='ko')
