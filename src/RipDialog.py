#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# X Audio Copy - GTK and GNOME application for ripping CD-Audio and encoding in lossy audio format.
# Copyright 2010 Giorgio Franceschi
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

from PreferencesDialog import *


### Subclasse che contiene le preferenze solo per la conversione ###
class RipDialog(PreferencesDialog):

	# Costruttore della classe
	def __init__(self, main_window, prefs):
		PreferencesDialog.__init__(self, main_window, prefs)

		self.dlg.set_title("Extract audio file from Audio CD...")
		self.notebook.set_current_page(0)
		self.cmdOK.set_label("_Rip")
		self.cmdReset.hide()
		self.radioSamePath.hide()
		self.radioHome.set_active(True)
		self.radioUncompressed.connect("toggled", self.on_Choise)
		if bool(int(self.prefs.get_option("rip-compressed"))):
			self.labelNotebookConverter.show()
			self.vboxNotebookConverter.show()
			self.frameTag.show()
		else:
			self.labelNotebookConverter.hide()
			self.vboxNotebookConverter.hide()
			self.frameTag.hide()

	def on_Choise(self, *args):

		if self.radioUncompressed.get_active():
			self.labelNotebookConverter.hide()
			self.vboxNotebookConverter.hide()
			self.frameTag.hide()
		elif self.radioCompressed.get_active():
			self.labelNotebookConverter.show()
			self.vboxNotebookConverter.show()
			self.frameTag.show()
		else:
			raise

