import os
from urlparse import urljoin

DEV_MODE = os.getenv('UT_DEV')

if DEV_MODE == 'local':
    URL_PREFIX = 'http://127.0.0.1:8000/'
else:
    URL_PREFIX = 'http://ubuntu-tweak.com/'

def get_utdata_version_url(version_url):
    if DEV_MODE:
        return urljoin(URL_PREFIX, '%sdev/' % version_url)
    else:
        return urljoin(URL_PREFIX, version_url)

def get_utdata_download_url(download_url):
    return urljoin(URL_PREFIX, download_url)
