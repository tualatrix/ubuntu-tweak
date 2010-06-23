__all__ = (
        'APP',
        'PACKAGE',
        'VERSION',
        'DATA_DIR',
        'init_locale',
        )

import os
import glib
import gettext
import pynotify

def applize(package):
    return ' '.join([a.capitalize() for a in package.split('-')])

PACKAGE = 'ubuntu-tweak'
VERSION = '0.5.4.1'
DATA_DIR = '/usr/share/ubuntu-tweak/'
APP = applize(PACKAGE)
CONFIG_ROOT = os.path.join(glib.get_user_config_dir(), 'ubuntu-tweak')
IS_INSTALLED = True

if not os.path.exists(CONFIG_ROOT):
    os.makedirs(CONFIG_ROOT)

try:
    LANG = os.getenv('LANG').split('.')[0].lower().replace('_','-')
except:
    LANG = 'en-us'

if not __file__.startswith('/usr'):
    datadir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    DATA_DIR = os.path.join(datadir, 'data')
    IS_INSTALLED = False

def init_locale():
    global INIT
    try:
        INIT
    except:
        gettext.install(PACKAGE, unicode=True)

        INIT = True

def install_ngettext():
    #FIXME
    gettext.bindtextdomain(PACKAGE, "/usr/share/locale")
    gettext.textdomain(PACKAGE)

init_locale()

if not pynotify.init('ubuntu-tweak'):
    sys.exit (1)
