import gettext

APP = 'ubuntu-tweak'
VERSION = '0.3.5'
DATA_DIR = 'data'

def InitLocale():
    gettext.install(APP, unicode = True)
