#!/usr/bin/env python
import UserDict
from Widgets import *
from SystemInfo import GnomeVersion
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XmlHandler(ContentHandler):
        def __init__(self, dict):
		self.dict = dict

        def startElement(self, name, attrs):
                if name == "item":
			try:
				minor = attrs["version"]
			except KeyError:
				self.dict[attrs["title"]] = attrs["key"]
			else:
				if GnomeVersion.minor >= minor:
					self.dict[attrs["title"]] = attrs["key"]

class GconfKeys:
	"""This class used to store the keys, it will create for only once"""
	keys = {}
	parser = make_parser()
	handler = XmlHandler(keys)
	parser.setContentHandler(handler)
	parser.parse("tweaks.xml")

class Factory:
	keys = GconfKeys.keys
	@staticmethod
	def create(widget = None, *argv):
		if len(argv) == 1:
			return getattr(Factory(), "create_%s" % widget)(argv[0])
		elif len(argv) == 2:
			return getattr(Factory(), "create_%s" % widget)(argv[0], argv[1])
		elif len(argv) == 3:
			return getattr(Factory(), "create_%s" % widget)(argv[0], argv[1], argv[2])
		elif len(argv) == 4:
			return getattr(Factory(), "create_%s" % widget)(argv[0], argv[1], argv[2], argv[3])
	
	def create_gconfcheckbutton(self, label, key, tooltip = None):
		if key in self.keys:
			button = GconfCheckButton(label, self.keys[key])
			if tooltip:
				button.set_tooltip_text(tooltip)
			return button
		else:
			return None

	def create_cgconfcheckbutton(self, label, key, mediator, tooltip = None):
		if key in self.keys:
			button = CGconfCheckButton(label, self.keys[key], mediator)
			if tooltip:
				button.set_tooltip_text(tooltip)
			return button
		else:
			return None

	def create_strgconfcheckbutton(self, label, key, mediator, tooltip = None):
		if key in self.keys:
			button = StrGconfCheckButton(label, self.keys[key], mediator)
			if tooltip:
				button.set_tooltip_text(tooltip)
			return button
		else:
			return None

	def create_gconfentry(self, key, mediator = None, tooltip = None):
		if key in self.keys:
			entry = GconfEntry(self.keys[key])
			if tooltip:
				entry.set_tooltip_text(tooltip)
			return entry
		else:
			return None

	def create_gconfcombobox(self, key, texts, values):
		if key in self.keys:
			combobox = GconfCombobox(self.keys[key], texts, values)
			return combobox.combobox
		else:
			return None

	def create_gconfscale(self, min, max, key, digits = None):
		if key in self.keys:
			scale = GconfScale(min, max, self.keys[key], digits)
			return scale
		else:
			return None

if __name__ == "__main__":
	print Factory().keys
