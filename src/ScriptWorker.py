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

import os
import sys
import gtk
import gobject
import gnomevfs
import gettext
import shutil
from Widgets import show_info

gettext.install("ubuntu-tweak", unicode = True)

class FileChooserDialog(gtk.FileChooserDialog):
	"""Show a dialog to select a folder, or to do more thing
	The default operation is select folder"""
	def __init__(	self,
			title = None,
			parent = None,
			action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT)
			):
		gtk.FileChooserDialog.__init__(self, title, parent, action, buttons)

class FileOperation:
	"""Do the real operation"""
	def copy(self, source, dest):
		"""Copy the file or folder with necessary notice"""
		dest = os.path.join(dest, os.path.basename(source))
		if os.path.isfile(source):
			if not os.path.exists(dest):
				shutil.copy(source, dest)
			else:
				show_info(_('The file "%s" is exists!') % dest)
		elif os.path.isdir(source):
			if not os.path.exists(dest):
				shutil.copytree(source, dest)
			else:
				show_info(_('The folder "%s" is exists!') % dest)

	def move(self, source, dest):
		"""Move the file or folder with necessary notice"""
		dest = os.path.join(dest, os.path.basename(source))
		if not os.path.exists(dest):
			shutil.move(source, dest)
		else:
			show_info(_('The target "%s" is exists!') % dest)

	def link(self, source, dest):
		"""Link the file or folder with necessary notice"""
		dest = os.path.join(dest, os.path.basename(source))
		if not os.path.exists(dest):
			os.symlink(source, dest)
		else:
			show_info(_('The target "%s" is exists!') % dest)

	def get_local_path(self, uri):
		"""Convert the URI to local path"""
		return gnomevfs.get_local_path_from_uri(uri)

class Worker:
	"""The worker to do the real operation, with getattr to instrospect the operation"""
	def __init__(self, argv):
		command = argv[1]
		paras = argv[2:]

		dialog = FileChooserDialog(_("Select a folder"))
		if dialog.run() == gtk.RESPONSE_ACCEPT:
			folder = dialog.get_filename()
		dialog.destroy()

		operation = FileOperation()
		work = getattr(operation, command)
		for file in paras:
			if file[0:4] == "file":
				file = operation.get_local_path(file)
			work(file, folder)

if __name__ == "__main__":
#	show_info(' '.join([i for i in sys.argv]))
	if len(sys.argv) <= 2:
		show_info(_("Please select a target(files or folders)."))
	if len(sys.argv) > 2:
		Worker(sys.argv)
