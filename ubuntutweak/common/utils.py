#!/usr/bin/python

import os
import gtk
#TODO Should not use gnome.ui any more.
from gnome import ui

__all__ = (
    'set_label_for_stock_button',
    'get_icon_with_type',
    'get_icon_with_app',
    'get_icon_with_cate',
    'get_icon_with_name',
)

icontheme = gtk.icon_theme_get_default()

def set_label_for_stock_button(button, text):
    label = button.get_child().get_child().get_children()[1]
    label.set_text_with_mnemonic(text)

def get_icon_with_type(filepath, size=24):
    icon = ui.icon_lookup(icontheme, None, filepath)

    try:
        pixbuf = icontheme.load_icon(icon[0], size, 0)
    except:
        return get_icon_with_name('gtk-execute', size)

    if pixbuf.get_height() != size:
        return pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)
    
    return pixbuf

def get_icon_with_cate(cate, size):
    pass

def get_icon_with_name(name, size=24):
    try:
        pixbuf = icontheme.load_icon(name, size, 0)
    except:
        pixbuf = icontheme.load_icon('gtk-execute', size, 0)

    if pixbuf.get_height() != size:
        return pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)

    return pixbuf

def get_icon_with_file(file, size):
    try:
        return gtk.gdk.pixbuf_new_from_file_at_size(file, size, size)
    except:
        return get_icon_with_name('gtk-execute', size)

def mime_type_get_icon(mime, size = 24):
    import gio
    try:
        gicon = gio.content_type_get_icon(mime)
        iconinfo = icontheme.choose_icon(gicon.get_names(), size, gtk.ICON_LOOKUP_USE_BUILTIN)
        if not iconinfo:
            pixbuf = get_icon_with_name('application-x-executable', size)
        else:
            pixbuf = iconinfo.load_icon()

        if pixbuf.get_width() != size:
            return pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)
    except:
        return get_icon_with_name('gtk-execute', size)

    return pixbuf

def get_icon_with_app(app, size):
    try:
        import gio
        gicon = app.get_icon()

        if gicon:
            if isinstance(gicon, gio.ThemedIcon):
                names = gicon.get_names()
                names_list = []
                for name in names:
                    if name.rfind('.') != -1:
                        names_list.append(name[:name.rfind('.')])
                    else:
                        names_list.append(name)

                iconinfo = icontheme.choose_icon(names_list, size, gtk.ICON_LOOKUP_USE_BUILTIN)
                if not iconinfo:
                    return get_icon_with_name('application-x-executable', size)

                return iconinfo.load_icon()
            elif isinstance(gicon, gio.FileIcon):
                file = app.get_icon().get_file().get_path()
                return get_icon_with_file(file, size)
        else:
            return get_icon_with_name('application-x-executable', size)
    except:
        return get_icon_with_name('gtk-execute', size)

if __name__ == '__main__':
#    print get_icon_with_name('start-here', 24)
#    print get_icon_with_type('/home/tualatrixx', 24)
    print mime_type_get_icon('application/msword')
