import os

from ubuntutweak.utils import walk_directories

def get_valid_icon_themes():
    # This function is taken from gnome-tweak-tool
    dirs = ( '/usr/share/icons',
             os.path.join(os.path.expanduser("~"), ".icons"))
    valid = walk_directories(dirs, lambda d:
                os.path.isdir(d) and \
                    not os.path.exists(os.path.join(d, "cursors")))

    valid.sort()

    return valid

def get_valid_themes():
    # This function is taken from gnome-tweak-tool
    """ Only shows themes that have variations for gtk+-3 and gtk+-2 """
    dirs = ( '/usr/share/themes',
             os.path.join(os.path.expanduser("~"), ".themes"))
    valid = walk_directories(dirs, lambda d:
                os.path.exists(os.path.join(d, "gtk-2.0")) and \
                    os.path.exists(os.path.join(d, "gtk-3.0")))

    valid.sort()

    return valid

def get_valid_cursor_themes():
    dirs = ( '/usr/share/icons',
             os.path.join(os.path.expanduser("~"), ".icons"))
    valid = walk_directories(dirs, lambda d:
                os.path.isdir(d) and \
                    os.path.exists(os.path.join(d, "cursors")))

    valid.sort()

    return valid

def get_valid_window_themes():
    dirs = ( '/usr/share/themes',
             os.path.join(os.path.expanduser("~"), ".themes"))
    valid = walk_directories(dirs, lambda d:
                os.path.exists(os.path.join(d, "metacity-1")))

    valid.sort()

    return valid
