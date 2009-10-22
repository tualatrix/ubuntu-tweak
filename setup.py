from setuptools import *

setup(name='ubuntu-tweak',
      version='0.5.0',
      description="DBus driven daemon for APT",
      author="TualatriX",  
      author_email='tualatrix@gmail.com',
      url='http://ubuntu-tweak.com',
      packages=[
          'ubuntutweak',
          'ubuntutweak.backends',
          'ubuntutweak.common',
          'ubuntutweak.common.network',
          'ubuntutweak.common.policykit',
          'ubuntutweak.common.widgets',
          'ubuntutweak.modules',
          'ubuntutweak.tweak',
      ],
#      scripts=["aptd", "aptdcon"],
      data_files=[("../etc/dbus-1/system.d/", ["ubuntu-tweak-daemon.conf"]),
          ],
      license = "GNU GPL",
)
