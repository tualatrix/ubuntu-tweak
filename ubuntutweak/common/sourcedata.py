from ubuntutweak.common.systeminfo import module_check

def is_ubuntu(distro):
    if type(distro) == list:
        for dis in distro:
            if dis in module_check.get_supported_ubuntu():
                return True
            return False
    else:
        if distro in module_check.get_supported_ubuntu():
            return True
        return False

def filter_sources():
    newsource = []
    for item in SOURCES_DATA:
        distro = item[1]
        if is_ubuntu(distro):
            if module_check.get_codename() in distro:
                newsource.append([item[0], module_check.get_codename(), item[2], item[3]])
        else:
            newsource.append(item)

    return newsource
