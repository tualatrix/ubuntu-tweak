import os
import glob
import logging

from ubuntutweak.common.debug import log_func

log = logging.getLogger('utils.ppa')

PPA_URL = 'ppa.launchpad.net'

def is_ppa(url):
    return PPA_URL in url

def get_list_name(url):
    if os.uname()[-1] == 'x86_64':
        arch = 'amd64'
    else:
        arch = 'i386'

    section = url.split('/')
    name = '/var/lib/apt/lists/ppa.launchpad.net_%s_%s_*%s_Packages' % (section[3], section[4], arch)
    log.debug("lists name: %s" % name)
    names = glob.glob(name)
    log.debug("lists names: %s" % names)
    if len(names) == 1:
        return names[0]
    else:
        return ''

def get_basename(url):
    section = url.split('/')
    return '%s/%s' % (section[3], section[4])

@log_func(log)
def get_short_name(url):
    return 'ppa:%s' % get_basename(url)

def get_long_name(url):
    basename = get_basename(url)

    return '<b>%s</b>\nppa:%s' % (basename, basename)

def get_homepage(url):
    section = url.split('/')
    return 'https://launchpad.net/~%s/+archive/%s' % (section[3], section[4])

def get_source_file_name(url):
    section = url.split('/')
    return '%s-%s' % (section[3], section[4])

def get_ppa_origin_name(url):
    section = url.split('/')
    # Due to the policy of ppa orgin naming, if an ppa is end with "ppa", so ignore it
    if section[4] == 'ppa':
        return 'LP-PPA-%s' % section[3]
    else:
        return 'LP-PPA-%s-%s' % (section[3], section[4])
