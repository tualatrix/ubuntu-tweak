import os
import json
import urllib
from ubuntutweak.conf import settings

class Parser(dict):
    def __init__(self, file, key):
        try:
            self.__data = json.loads(open(file).read())
            self.init_items(key)
        except:
            self.is_available = False
        else:
            self.is_available = True

    def init_items(self, key):
        for item in self.__data:
            item['fields']['id'] = item['pk']
            self[item['fields'][key]] = item['fields']

    def get_by_lang(self, key, field):
        value = self[key][field]
        if settings.LANG in value.keys():
            return value[settings.LANG]
        else:
            return value['raw']

class AppParser(Parser):
    def __init__(self):
        app_data = os.path.join(settings.CONFIG_ROOT, 'apps.json')

        Parser.__init__(self, app_data, 'package')

    def get_summary(self, key):
        return self.get_by_lang(key, 'summary')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

    def get_category(self, key):
        return self[key]['category']

class CateParser(Parser):
    def __init__(self):
        cate_data = os.path.join(settings.CONFIG_ROOT, 'cates.json')

        Parser.__init__(self, cate_data , 'slug')

    def get_name(self, key):
        return self.get_by_lang(key, 'name')

if __name__ == '__main__':
    parser = CateParser()
    import pdb
    pdb.set_trace()
