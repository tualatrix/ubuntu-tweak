import pynotify

class Notify(pynotify.Notification):
    def __init__(self):
        if not pynotify.init('ubuntu-tweak'):
                    sys.exit (1)

        super(Notify, self).__init__('Notify')

notify = Notify()
