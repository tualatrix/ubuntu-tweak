import pynotify

class Notify(pynotify.Notification):
    def __init__(self):
        super(Notify, self).__init__('Tweak')
        self.set_timeout(8000)
		
notify = Notify()
