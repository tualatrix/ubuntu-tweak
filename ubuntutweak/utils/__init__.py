import gio

def get_command_for_type(mime):
    try:
        return gio.app_info_get_default_for_type('text/plain', False).get_executable()
    except:
        if os.path.exists('/usr/bin/gedit'):
            return 'gedit'
        elif os.path.exists('/usr/bin/leafpad'):
            return 'leafpad'
        elif os.path.exists('/usr/bin/gvim'):
            return 'gvim'
        else:
            return None

def set_label_for_stock_button(button, text):
    label = button.get_child().get_child().get_children()[1]
    label.set_text_with_mnemonic(text)

