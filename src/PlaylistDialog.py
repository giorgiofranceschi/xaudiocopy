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


import os, re
try:
	import pygtk
	pygtk.require("2.0")
except:
	print("PyGTK not available")
	sys.exit(1)

try:
	import gtk
	import gobject
except:
	print("GTK not available")
	sys.exit(1)

from Preferences import DIRMUSIC


### Finestra di dialogo per il salvataggio delle playlist ###
class PlaylistDialog:

	# Costruttore della classe
	def __init__(self, mainapp, main_window):

		self.mainapp = mainapp
		self.main_window = main_window
		self.mainapp.prefs = self.mainapp.prefs

		# Finestra di dialogo
		self.dlg = gtk.Dialog("Create playlist...", self.main_window ,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.dlg.set_default_size(410, 400)
		self.dlg.set_border_width(5)
		self.dlg.vbox.set_homogeneous(False)
		self.dlg.set_resizable(False)
		self.dlg.vbox.set_spacing(12)

		# VBox per la scelta della playlist
		vboxPL = gtk.VBox()
		self.dlg.vbox.pack_start(vboxPL, expand=False)
		vboxPL.set_homogeneous(False)
		vboxPL.set_spacing(4)
		vboxPL.show()

		# Radio button per scegliere di salvare nella HOME/Musica
		hboxPL1 = gtk.HBox()
		hboxPL1.set_homogeneous(True)
		vboxPL.pack_start(hboxPL1, expand=False)
		hboxPL1.show()
		self.radioAll = gtk.RadioButton(None, "All files", True)
		hboxPL1.pack_start(self.radioAll, padding=20)
		self.radioAll.show()

		# Radio button per scegliere di salvare nella stessa cartella
		hboxPL2 = gtk.HBox()
		hboxPL2.set_homogeneous(True)
		vboxPL.pack_start(hboxPL2, expand=False)
		hboxPL2.show()
		self.radioSelected = gtk.RadioButton(self.radioAll, "Only selected files", True)
		hboxPL2.pack_start(self.radioSelected, padding=20)
		self.radioSelected.show()

		# VBox per la scelta del path
		vboxPath = gtk.VBox()
		self.dlg.vbox.pack_start(vboxPath, expand=False)
		vboxPath.set_homogeneous(False)
		vboxPath.set_spacing(4)
		vboxPath.show()

		# Radio button per scegliere di salvare nella HOME/Musica
		hboxPath1 = gtk.HBox()
		hboxPath1.set_homogeneous(True)
		vboxPath.pack_start(hboxPath1, expand=False)
		hboxPath1.show()
		self.radioHome = gtk.RadioButton(None, "Save in " + DIRMUSIC, True)
		hboxPath1.pack_start(self.radioHome, padding=20)
		self.radioHome.show()

		# Radio button per scegliere di salvare nella stessa cartella
		hboxPath2 = gtk.HBox()
		hboxPath2.set_homogeneous(True)
		vboxPath.pack_start(hboxPath2, expand=False)
		hboxPath2.show()
		self.radioSamePath = gtk.RadioButton(None, "Save in the same folder as the imput files", True)
		hboxPath2.pack_start(self.radioSamePath, padding=20)
		self.radioSamePath.show()

		# Radio button per scegliere di salvare nell'ultima cartella usata
		hboxPath3 = gtk.HBox()
		hboxPath3.set_homogeneous(True)
		vboxPath.pack_start(hboxPath3, expand=False)
		hboxPath3.show()
		self.radioLast = gtk.RadioButton(None, "Save in the last used folder", True)
		hboxPath3.pack_start(self.radioLast, padding=20)
		self.radioLast.show()

		# Radio button per scegliere di salvare in un'altra posizione
		hboxPath4 = gtk.HBox()
		hboxPath4.set_homogeneous(False)
		vboxPath.pack_start(hboxPath4, expand=False)
		hboxPath4.show()
		self.radioAltPath = gtk.RadioButton(None, "Select path:", True)
		self.radioAltPath.connect("toggled", self.on_alt_path)
		hboxPath4.pack_start(self.radioAltPath, padding=20, expand=False)
		self.radioAltPath.show()

		# Il relativo pulsante che apre il FileChooser
		self.cmdChoise = gtk.Button("Choise...")
		self.cmdChoise.connect("clicked", self.on_Path)
		hboxPath4.pack_start(self.cmdChoise, expand=False, padding=20)
		self.cmdChoise.set_sensitive(False)
		self.cmdChoise.show()

		# Setta i radiobutton
		if bool(int(self.mainapp.prefs.get_option("save-in-home"))):
			self.radioHome.set_group(None)
			self.radioSamePath.set_group(self.radioHome)
			self.radioLast.set_group(self.radioHome)
			self.radioAltPath.set_group(self.radioHome)
		elif bool(int(self.mainapp.prefs.get_option("save-in-same-folder"))):
			self.radioSamePath.set_group(None)
			self.radioHome.set_group(self.radioSamePath)
			self.radioLast.set_group(self.radioSamePath)
			self.radioAltPath.set_group(self.radioSamePath)
		elif bool(int(self.mainapp.prefs.get_option("select-path"))):
			self.radioAltPath.set_group(None)
			self.radioHome.set_group(self.radioAltPath)
			self.radioSamePath.set_group(self.radioAltPath)
			self.radioLast.set_group(self.radioAltPath)
			self.on_alt_path()
		elif bool(int(self.mainapp.prefs.get_option("save-in-last-folder"))):
			self.radioLast.set_group(None)
			self.radioHome.set_group(self.radioLast)
			self.radioSamePath.set_group(self.radioLast)
			self.radioAltPath.set_group(self.radioLast)
			self.lastSaveFolder = self.mainapp.prefs.get_option("last-save-folder")
		else:
			self.radioHome.set_group(None)
			self.radioSamePath.set_group(self.radioHome)
			self.radioLast.set_group(self.radioHome)
			self.radioAltPath.set_group(self.radioHome)


		# Pulsante Calcel
		self.cmdCancel = gtk.Button(label="_Cancel", use_underline=True)
		self.cmdCancel.connect("clicked", self.on_Cancel)
		self.dlg.add_action_widget(self.cmdCancel, 1)
		self.cmdCancel.show()

		# Pulsante OK
		self.cmdOK = gtk.Button(label="_Save", use_underline=True)
		self.cmdOK.connect("clicked", self.on_Ok)
		self.dlg.add_action_widget(self.cmdOK, 2)
		self.cmdOK.show()
		self.dlg.set_focus(self.cmdOK)


	def on_alt_path(self, *args):

		if self.radioAltPath.get_active():
			self.cmdChoise.set_sensitive(True)
		else:
			self.cmdChoise.set_sensitive(False)

	# Seleziona il path altenativo per il salvataggio
	def on_Path(self, *args):

		choisePath = gtk.FileChooserDialog("Choise path...", self.dlg,
					gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		choisePath.set_select_multiple(False)
		choisePath.set_local_only(False)
		try:
			choisePath.set_current_folder(self.mainapp.prefs.get_option("last-save-folder"))
		except:
			choisePath.set_current_folder(DIRMUSIC)
		response = choisePath.run()
		if response == gtk.RESPONSE_OK:
			self.altsavepath = choisePath.get_filename()
		else:
			self.altsavepath = self.mainapp.prefs.get_option("last-save-folder")
		choisePath.destroy()


	# Attiva e visualizza la finestra di dialogo
	def show(self, *args):
		self.response = None
		self.dlg.run()
		self.dlg.destroy()

	# Chiude e salva
	def on_Ok(self, *args):

		#Carica la lista dei file selezionati
		if self.radioAll.get_active():
			self.samesavepath = self.mainapp.audioFileList.filelist[0].get_foldername()
			self.playlistname = self.mainapp.audioFileList.filelist[0].get_tag("artist") + " - " + self.mainapp.audioFileList.filelist[0].get_tag("album")
		elif self.radioSelected.get_active():
			self.selplay = self.mainapp.Selection(self.mainapp.FileTable)
			try:
				sel = self.selplay[0]
			except IndexError:
				sel = None
			if sel:
				af = sel[0]
				it = sel[1]
				self.samesavepath = af.get_foldername()
				self.playlistname = af.get_tag("artist") + " - " + af.get_tag("album")
				if af.get_foldername() == "Audio CD":
					self.samesavepath = self.mainapp.prefs.get_option("last-save-folder")
			else: self.samesavepath = self.mainapp.prefs.get_option("last-save-folder")

		if self.radioHome.get_active():
			self.savepath = DIRMUSIC
		if self.radioSamePath.get_active():
			self.savepath = self.samesavepath
		if self.radioLast.get_active():
			self.savepath = self.mainapp.prefs.get_option("last-save-folder")
		if self.radioAltPath.get_active():
			try:
				self.savepath = self.altsavepath
			except:
				self.savepath =  self.mainapp.prefs.get_option("last-save-folder")
		print "SAVEPATH: ", self.savepath

		playlist = open(self.savepath + "/" + self.playlistname + ".m3u", "wb")

		listsongs = []
		listsongs.append("#EXTM3U" + "\n")
		if self.radioAll.get_active():
			for af in self.mainapp.audioFileList.filelist:
				listsongs.append("#EXTINF:" + str(af.get_duration()) + "," + af.get_tag("artist") + " - " + af.get_tag("title") + "\n")
				listsongs.append(af.get_filepath()[len(self.savepath + "/"):] + "\n")
		elif self.radioSelected.get_active():
			self.selplay = self.mainapp.Selection(self.mainapp.FileTable)
			for sel in self.selplay:
				print sel[0].get_filename()
				listsongs.append("#EXTINF:" + str(sel[0].get_duration()) + "," + sel[0].get_tag("artist") + " - " + sel[0].get_tag("title") + "\n")
				listsongs.append(sel[0].get_filepath()[len(self.savepath + "/"):] + "\n")
		playlist.writelines(listsongs)
		playlist.close()

		self.response = gtk.RESPONSE_OK
		self.dlg.destroy()

	def on_Cancel(self, *args):

		self.dlg.destroy()
