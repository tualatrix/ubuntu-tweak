import os

if os.getenv('UT_DEV'):
    URL_PREFIX = 'http://127.0.0.1:8000/'
else:
    URL_PREFIX = 'http://ubuntu-tweak.com'
