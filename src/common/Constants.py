__all__ = (
        'APP',
        'VERSION',
        'DATA_DIR',
        'InitLocale',
        )

import gettext

APP = 'ubuntu-tweak'
VERSION = '0.3.4'
DATA_DIR = 'data'

def InitLocale():
    global INIT
    try:
        INIT
    except:
        gettext.install(APP, unicode = True)
        INIT = True

InitLocale()
