#!/usr/bin/env python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gconf

class Setting:
	"""The base class of an option, client is shared by all subclass
	Every Setting hold a key and a value"""

	client = gconf.client_get_default()

	def __init__(self, key):
		self.key = key
		self.value = self.client.get(key)

		dir = self.get_dir_from_key(key)
		self.client.add_dir(dir, gconf.CLIENT_PRELOAD_NONE)
#		self.client.notify_add(key, self.value_changed, key)


	def value_changed(self, client, id, entry, data = None):
		pass

	def get_dir_from_key(self, key):
		return "/".join(key.split("/")[0: -1])

class BoolSetting(Setting):
	def __init__(self, key):
		Setting.__init__(self, key)

		self.bool = self.get_bool()

	def get_bool(self):
		self.value = self.client.get(self.key)
		if self.value:
			if self.value.type == gconf.VALUE_BOOL:
				return self.value.get_bool()
			elif self.value.type == gcon.VALUE_STRING:
				return bool(self.value.get_string())
		else:
			return False

class StringSetting(Setting):
	def __init__(self, key):
		Setting.__init__(self, key)

		self.string = self.get_string()

	def get_string(self):
		self.value = self.client.get(self.key)
		if self.value:
			return self.value.get_string()
		else:
			return None

class IntSetting(Setting):
	def __init__(self, key):
		Setting.__init__(self, key)

		self.int = self.get_int()

	def get_int(self):
		self.value = self.client.get(self.key)
		return self.value.get_int()

class FloatSetting(Setting):
	def __init__(self, key):
		Setting.__init__(self, key)

		self.int = self.get_float()

	def get_float(self):
		self.value = self.client.get(self.key)
		return self.value.get_float()

class ConstStringSetting(StringSetting):
	def __init__(self, key, values):
		StringSetting.__init__(self, key)

		self.values = values
