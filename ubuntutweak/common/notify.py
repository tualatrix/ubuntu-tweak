from gi.repository import Notify

class Notify(Notify.Notification):
    def __init__(self):
        if not Notify.init('ubuntu-tweak'):
            return

        super(Notify, self).__init__('Notify')
        self.set_hint_string('x-canonical-append', "")

notify = Notify()
