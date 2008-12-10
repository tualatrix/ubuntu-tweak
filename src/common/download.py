#!/usr/bin/python

import urllib

class Download:
    def __init__(self, remote_uri, local_uri):
        urllib.urlretrieve(remote_uri, local_uri, self.update_progress)

    def update_progress(self, blocks, block_size, total_size):
        percentage = float(blocks * block_size) / total_size
        print percentage

if __name__ == '__main__':
    Download('http://ubuntu.cn99.com/ubuntu/pool/main/g/gedit/gedit_2.22.3.orig.tar.gz', 'gedit_2.22.3.orig.tar.gz')
