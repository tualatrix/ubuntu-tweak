import glob
from setuptools import setup, find_packages
from ubuntutweak import __version__

setup(name='ubuntu-tweak',
      version=__version__,
      description='magic tool to configure Ubuntu',
      author='TualatriX',  
      author_email='tualatrix@gmail.com',
      url='http://ubuntu-tweak.com',
      scripts=['ubuntu-tweak'],
      packages=find_packages(),
      data_files=[
          ('../etc/dbus-1/system.d/', ['data/ubuntu-tweak-daemon.conf']),
          ('share/dbus-1/system-services', ['data/com.ubuntu_tweak.daemon.service']),
          ('share/ubuntu-tweak/ui/', glob.glob('data/ui/*.ui')),
          ('share/ubuntu-tweak/pixmaps/', glob.glob('data/pixmaps/*.png')),
          ('share/ubuntu-tweak/scripts/', glob.glob('data/scripts/*')),
          ('share/ubuntu-tweak/templates/', glob.glob('data/templates/*')),
          ('share/ubuntu-tweak/', ['data/keys.xml']),
          ('share/ubuntu-tweak/', ['data/script-worker', 'data/uturl', 'data/ubuntu-tweak-daemon', 'data/merge_sourceslist.py']),
          ],
      license='GNU GPL',
      platforms='linux',
      test_suite='tests',
)
