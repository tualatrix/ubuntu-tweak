import os
import json
import urllib

#FIXME it should be done in server side
MEDIA_ROOT = 'http://127.0.0.1:8000/static/'

class Parser(dict):
    def __init__(self, file, key):
        try:
            self.__data = json.loads(open(file).read())
            self.init_items(key)
        except:
            pass

    def init_items(self, key):
        for item in self.__data:
            item['fields']['id'] = item['pk']
            item['fields']['logo32'] = MEDIA_ROOT + item['fields']['logo32']

            self[item['fields'][key]] = item['fields']

if __name__ == '__main__':
    file = os.path.expanduser('~/.ubuntu-tweak/apps/data/apps.json')
    parser = Parser(file)
    import pdb
    pdb.set_trace()
