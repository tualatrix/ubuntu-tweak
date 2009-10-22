import glob
from setuptools import *

setup(name='ubuntu-tweak',
      version='0.5.0',
      description="DBus driven daemon for APT",
      author="TualatriX",  
      author_email='tualatrix@gmail.com',
      url='http://ubuntu-tweak.com',
      scripts=['ubuntu-tweak'],
      packages=[
          'ubuntutweak',
          'ubuntutweak.common',
          'ubuntutweak.backends',
          'ubuntutweak.network',
          'ubuntutweak.policykit',
          'ubuntutweak.widgets',
          'ubuntutweak.modules',
          'ubuntutweak.utils',
      ],
#      scripts=["aptd", "aptdcon"],
      data_files=[
          ("../etc/dbus-1/system.d/", ["daemon/ubuntu-tweak-daemon.conf"]),
          ('share/ubuntu-tweak/appcates/', glob.glob("data/appcates/*.png")),
          ('share/ubuntu-tweak/applogos/', glob.glob("data/applogos/*.png")),
          ('share/ubuntu-tweak/gui/', glob.glob("data/appcates/*.glade")),
          ('share/ubuntu-tweak/pixmaps/', glob.glob("data/pixmaps/*.png")),
          ('share/ubuntu-tweak/status/', glob.glob("data/status/*.png")),
          ('share/ubuntu-tweak/', ['data/keys.xml']),
          ],
      license = "GNU GPL",
      platforms = 'linux',
)
