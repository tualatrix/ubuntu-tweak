import os
import glib

CONFIG_ROOT=os.path.join(glib.get_user_config_dir(), 'ubuntu-tweak')

if not os.path.exists(CONFIG_ROOT):
    os.mkdir(CONFIG_ROOT)
