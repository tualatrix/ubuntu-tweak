#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

class HelloWorld:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_border_width(10)
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
    
        self.button = gtk.Button("Hello World")
        self.button.connect("clicked", self.hello)
        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        self.window.add(self.button)
        self.window.show_all()

    def hello(self, widget):
        print 'Hello World'

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"

        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
