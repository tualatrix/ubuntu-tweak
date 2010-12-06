from ubuntutweak import system

def is_ubuntu(distro):
    if type(distro) == list:
        for dis in distro:
            if system.is_supported(dis):
                return True
            return False
    else:
        if system.is_supported(distro):
            return True
        return False

def filter_sources():
    newsource = []
    for item in SOURCES_DATA:
        distro = item[1]
        if is_ubuntu(distro):
            if system.codename in distro:
                newsource.append([item[0], system.codename, item[2], item[3]])
        else:
            newsource.append(item)

    return newsource
