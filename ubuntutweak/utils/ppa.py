import glob

PPA_URL = 'ppa.launchpad.net'

def is_ppa(url):
    return PPA_URL in url

def get_list_name(url):
    section = url.split('/')
    name = '/var/lib/apt/lists/ppa.launchpad.net_%s_%s_*_Packages' % (section[3], section[4])
    names = glob.glob(name)
    if len(names) == 1:
        return names[0]
    else:
        return ''

def get_short_name(url):
    section = url.split('/')
    return 'ppa:%s/%s' % (section[3], section[4])

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
