import glob
from setuptools import setup, find_packages
from ubuntutweak0 import __version__

setup(name='ubuntu-tweak-0',
      version=__version__,
      description='magic tool to configure Ubuntu',
      author='TualatriX',  
      author_email='tualatrix@gmail.com',
      url='http://ubuntu-tweak.com',
      scripts=['ubuntu-tweak-0'],
      packages=find_packages(),
      data_files=[
          ('../etc/dbus-1/system.d/', ['data/ubuntu-tweak-daemon-0.conf']),
          ('share/dbus-1/system-services', ['data/com.ubuntu_tweak.daemonold.service']),
          ('share/ubuntu-tweak-0/ui/', glob.glob('data/ui/*.ui')),
          ('share/ubuntu-tweak-0/pixmaps/', glob.glob('data/pixmaps/*.png')),
          ('share/ubuntu-tweak-0/scripts/', glob.glob('data/scripts/*')),
          ('share/ubuntu-tweak-0/templates/', glob.glob('data/templates/*')),
          ('share/ubuntu-tweak-0/', ['data/keys.xml']),
          ('share/ubuntu-tweak-0/', ['data/script-worker', 'data/uturl', 'data/ubuntu-tweak-daemon', 'data/merge_sourceslist.py']),
          ],
      license='GNU GPL',
      platforms='linux',
      test_suite='tests',

)
