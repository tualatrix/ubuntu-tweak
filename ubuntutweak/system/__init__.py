import os
import platform

from ubuntutweak.system.wm import GnomeVersion
from ubuntutweak.common.consts import APP, VERSION

def get_distro():
    '''It should be "Ubuntu 10.10 maverick"'''
    return ' '.join(platform.dist())

def has_apt():
    try:
        import apt_pkg
        return True
    except ImportError:
        return False

def get_codename():
    try:
        codename = os.popen('lsb_release -cs').read().strip()
        if codename in ['karmic', 'helena', 'Helena']:
            return 'karmic'
        elif codename in ['lucid', 'isadora', 'Isadora']:
            return 'lucid'
        return codename
    except:
        pass
    return ''

def has_ccm():
    try:
        import ccm
        return True
    except:
        return False

def has_right_compiz():
    '''Return 1 if OK, return 0 if no ccm, return -1 if compiz broken'''
    try:
        if has_ccm():
            import ccm
            if ccm.Version >= '0.7.4':
                return 1
            else:
                return 0
        else:
            return 0
    except:
        return 0

def get_desktop():
    '''gnome, kde, and others'''
    if os.popen('xprop -root _DT_SAVE_MODE | grep xfce').read() != '':
        return 'xfce'
    elif os.getenv('KDE_FULL_SESSION'):
        return 'kde'
    elif os.getenv('DESKTOP_SESSION') == 'Lubuntu':
        return 'lxde'
    elif os.getenv('GDMSESSION') == 'une':
        return 'une'
    elif os.popen('xlsclients | grep -i gnome-session').read() != '':
        return 'gnome'
    else:
        return ''

def get_desktop_version():
    '''Return the desktop version with tuple
    >>> get_desktop_version()
    (2, 32, 0)
    '''
    return GnomeVersion.platform, GnomeVersion.minor, GnomeVersion.micro

def get_desktop_fullname():
    '''GNOME 2.30'''
    return GnomeVersion.description

def get_app():
    '''Ubuntu Tweak 0.5.x'''
    return " ".join([APP, VERSION])

DISTRO = get_distro()
CODENAME = get_codename()
DESKTOP = get_desktop()
DESKTOP_FULLNAME = get_desktop_fullname()
DESKTOP_VERSION = get_desktop_version()
APP = get_app()

def is_supported(codename=CODENAME):
    return codename in ('karmic', 'lucid', 'maverick', 'natty')
