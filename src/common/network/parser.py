import os
import json
import urllib

#FIXME it should be done in server side
MEDIA_ROOT = 'http://127.0.0.1:8000/static/'

class Parser:
    def __init__(self, file):
        self.data = json.loads(open(file).read())

    def get_items(self):
        for item in self.data:
            item['fields']['id'] = item['pk']
            item['fields']['logo32'] = MEDIA_ROOT + item['fields']['logo32']
            yield item['fields']

if __name__ == '__main__':
    file = os.path.expanduser('~/.ubuntu-tweak/apps/data/apps.json')
    parser = Parser(file)
    import pdb
    pdb.set_trace()
