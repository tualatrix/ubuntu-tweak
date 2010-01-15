import os
import random
import time
import datetime

from ubuntutweak.common.consts import install_ngettext
from gettext import ngettext
from urlparse import urljoin

install_ngettext()

DEV_MODE = os.getenv('UT_DEV')
DATA_MIRRORS = (
    'http://ubuntu-tweak.com/',
    'http://ubuntu-tweak.lfeng.me/'
)

if DEV_MODE == 'local':
    URL_PREFIX = 'http://127.0.0.1:8000/'
else:
    URL_PREFIX = DATA_MIRRORS[random.randint(0, len(DATA_MIRRORS)-1)]

def get_version_url(version_url):
    if DEV_MODE:
        return urljoin(URL_PREFIX, '%sdev/' % version_url)
    else:
        return urljoin(URL_PREFIX, version_url)

def get_download_url(download_url):
    return urljoin(URL_PREFIX, download_url)

def get_local_timestamp(folder):
    local_timestamp = os.path.join(folder, 'timestamp')

    if os.path.exists(local_timestamp):
        local_version = open(local_timestamp).read()
    else:
        local_version = '0'

    return local_version

def get_local_time(folder):
    timestamp = get_local_timestamp(folder)
    if timestamp > '0':
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(float(timestamp)))
    else:
        return _('Never')

def save_synced_timestamp(folder):
    synced = os.path.join(folder, 'synced')
    f = open(synced, 'w')
    f.write(str(int(time.time())))
    f.close()

def get_last_synced(folder):
    try:
        timestamp = open(os.path.join(folder, 'synced')).read()
        now = time.time()

        o_delta = datetime.timedelta(seconds=float(timestamp))
        n_delta = datetime.timedelta(seconds=now)

        difference = n_delta - o_delta

        weeks, days = divmod(difference.days, 7)

        minutes, seconds = divmod(difference.seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if weeks:
            return ngettext('%d week ago', '%d weeks ago', weeks) % weeks
        if days:
            return ngettext('%d day ago', '%d days ago', days) % days
        if hours:
            return ngettext('%d hour ago', '%d hours ago', hours) % hours
        if minutes:
            return ngettext('%d minute ago', '%d minutes ago', minutes) % minutes
        return _('Just Now')
    except IOError:
        return _('Never')
