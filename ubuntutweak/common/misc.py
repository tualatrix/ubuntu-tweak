from gettext import ngettext
from sgmllib import SGMLParser

def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    try:
        bytes = float(bytes)
    except TypeError:
        return "0 bytes"

    if bytes < 1024:
        return ngettext("%(size)d byte", "%(size)d bytes", bytes) % {'size': bytes}
    if bytes < 1024 * 1024:
        return _("%.1f KB") % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return _("%.1f MB") % (bytes / (1024 * 1024))
    return _("%.1f GB") % (bytes / (1024 * 1024 * 1024))

class URLLister(SGMLParser):
    def __init__(self, result):
        SGMLParser.__init__(self)
        self.result = result
        self.open = False

    def start_a(self, attrs):
        self.open = True

    def handle_data(self, text):
        if self.open and not text.startswith('.'):
            self.result.append(text.strip('/\\'))

    def end_a(self):
        if self.open:
            self.open = False

if __name__ == '__main__':
    import urllib
    url = urllib.urlopen('http://archive.ubuntu.org.cn/ubuntu-cn/')

    result = []
    parse = URLLister(result)
    data = url.read()
    parse.feed(data)
    print result
