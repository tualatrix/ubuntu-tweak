raise DeprecationWarning("Don't use THIS")

from gettext import ngettext
from sgmllib import SGMLParser

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
