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

from Preferences import *


### Finestra di dialogo per la conversione ###
class PreferencesDialog:

	# Costruttore della classe
	def __init__(self, main_window, prefs):

		self.prefs = prefs
		self.main_window = main_window

		# Finestra di dialogo
		self.dlg = gtk.Dialog("Preferences...", self.main_window ,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		#self.dlg = gtk.Dialog("Preferences...", self.main_window , gtk.DIALOG_DESTROY_WITH_PARENT)
		self.dlg.set_default_size(410, 400)
		self.dlg.set_border_width(5)
		self.dlg.vbox.set_homogeneous(False)
		self.dlg.set_resizable(False)
		self.dlg.vbox.set_spacing(5)

		# Notebook
		self.notebook = gtk.Notebook()
		self.dlg.vbox.add(self.notebook)
		self.notebook.show()


		# Pagina 0
		labelNotebookRipper = gtk.Label()
		labelNotebookRipper.set_use_markup(True)
		labelNotebookRipper.set_label("Ripper")
		# VBox per dividere la pagina
		vboxNotebookRipper = gtk.VBox()
		vboxNotebookRipper.set_spacing(10)
		vboxNotebookRipper.set_homogeneous(False)
		self.notebook.append_page(vboxNotebookRipper, labelNotebookRipper)
		labelNotebookRipper.show()
		vboxNotebookRipper.show()

		# Cornice per la scelta del tipo
		frameType = gtk.Frame()
		frameType.set_shadow_type(gtk.SHADOW_NONE)
		vboxNotebookRipper.pack_start(frameType, expand=False)
		frameType.show()

		# Label della cornice per la scelta del tipo
		labelType = gtk.Label()
		labelType.set_use_markup(True)
		labelType.set_label("<b>Save uncompressed or compressed tracks?</b>")
		labelType.set_padding(0, 10)
		frameType.set_label_widget(labelType)
		labelType.show()

		# VBox per i radio buttons
		vboxType = gtk.VBox()
		frameType.add(vboxType)
		vboxType.set_homogeneous(False)
		vboxType.set_spacing(6)
		vboxType.show()

		# Radio button per scegliere di salvare non compresse
		hboxType1 = gtk.HBox()
		hboxType1.set_homogeneous(True)
		vboxType.pack_start(hboxType1, expand=False)
		hboxType1.show()
		self.radioUncompressed = gtk.RadioButton(None, "Save uncompressed tracks", True)
		hboxType1.pack_start(self.radioUncompressed, padding=20)
		self.radioUncompressed.show()

		# Radio button per scegliere salvare compresse
		hboxType2 = gtk.HBox()
		hboxType2.set_homogeneous(True)
		vboxType.pack_start(hboxType2, expand=False)
		hboxType2.show()
		self.radioCompressed = gtk.RadioButton(None, "Save compressed tracks", True)
		hboxType2.pack_start(self.radioCompressed, padding=20)
		self.radioCompressed.show()
		
		# Setta i radiobutton
		if bool(int(self.prefs.get_option("rip-compressed"))):
			self.radioUncompressed.set_group(self.radioCompressed)
		elif not bool(int(self.prefs.get_option("rip-compressed"))):
			self.radioCompressed.set_group(self.radioUncompressed)
		else:
			self.radioCompressed.set_group(self.radioUncompressed)

		# Pagina 1
		# Label della pagina
		labelNotebookFolder = gtk.Label()
		labelNotebookFolder.set_use_markup(True)
		labelNotebookFolder.set_label("Folders")
		# Cornice per la scelta del path
		framePath = gtk.Frame()
		framePath.set_shadow_type(gtk.SHADOW_NONE)
		self.notebook.append_page(framePath, labelNotebookFolder)
		labelNotebookFolder.show()
		framePath.show()

		# Label della cornice per la scelta del path
		labelPath = gtk.Label()
		labelPath.set_use_markup(True)
		labelPath.set_label("<b>Where to place the results?</b>")
		labelPath.set_padding(0, 10)
		framePath.set_label_widget(labelPath)
		labelPath.show()

		# VBox per la scelta del path
		vboxPath = gtk.VBox()
		framePath.add(vboxPath)
		vboxPath.set_homogeneous(False)
		vboxPath.set_spacing(6)
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
		if bool(int(self.prefs.get_option("save-in-home"))):
			self.radioHome.set_group(None)
			self.radioSamePath.set_group(self.radioHome)
			self.radioLast.set_group(self.radioHome)
			self.radioAltPath.set_group(self.radioHome)
		elif bool(int(self.prefs.get_option("save-in-same-folder"))):
			self.radioSamePath.set_group(None)
			self.radioHome.set_group(self.radioSamePath)
			self.radioLast.set_group(self.radioSamePath)
			self.radioAltPath.set_group(self.radioSamePath)
		elif bool(int(self.prefs.get_option("select-path"))):
			self.radioAltPath.set_group(None)
			self.radioHome.set_group(self.radioAltPath)
			self.radioSamePath.set_group(self.radioAltPath)
			self.radioLast.set_group(self.radioAltPath)
			self.on_alt_path()
		elif bool(int(self.prefs.get_option("save-in-last-folder"))):
			self.radioLast.set_group(None)
			self.radioHome.set_group(self.radioLast)
			self.radioSamePath.set_group(self.radioLast)
			self.radioAltPath.set_group(self.radioLast)
			self.lastSaveFolder = self.prefs.get_option("last-save-folder")
		else:
			self.radioHome.set_group(None)
			self.radioSamePath.set_group(self.radioHome)
			self.radioLast.set_group(self.radioHome)
			self.radioAltPath.set_group(self.radioHome)

		# Check button per il nome delle sottocartelle
		hboxPath5 = gtk.HBox()
		hboxPath5.set_homogeneous(False)
		vboxPath.pack_start(hboxPath5, expand=False)
		hboxPath5.show()
		self.checkFolders = gtk.CheckButton("Create subfolders", True)
		self.checkFolders.connect("toggled", self.on_create_sub_folders)
		hboxPath5.pack_start(self.checkFolders, padding=40)
		self.checkFolders.show()

		# ComboBox per le sottocartelle
		hboxPath6 = gtk.HBox()
		hboxPath6.set_homogeneous(False)
		vboxPath.pack_start(hboxPath6, expand=False)
		hboxPath6.show()
		self.comboFolders = gtk.combo_box_new_text()
		prefs_path = self.prefs.get_option("path-subfolder")
		for sp in SUBFOLDERS_PATH:
			self.comboFolders.append_text(sp[0] + " (" + sp[1] + ")")
			if sp[0] == prefs_path:
				pathindex = SUBFOLDERS_PATH.index(sp)
		try:
			self.comboFolders.set_active(pathindex) #dafault
		except:
			self.comboFolders.set_active(6)
		space = gtk.Label("")
		hboxPath6.pack_start(space, padding=10, expand=False)
		space.show()
		hboxPath6.pack_start(self.comboFolders, expand=False, padding = 20)
		self.comboFolders.set_sensitive(False)
		self.comboFolders.show()

		# Setta il check
		if bool(int(self.prefs.get_option("create-subfolders"))):
			self.checkFolders.set_active(True)
			self.on_create_sub_folders()
		else:
			self.checkFolders.set_active(False)


		# Pagina 2
		# Label della pagina
		labelNotebookFileName = gtk.Label()
		labelNotebookFileName.set_use_markup(True)
		labelNotebookFileName.set_label("Filename/Tags")

		# VBox per dividere la pagina
		vboxNotebookFileName = gtk.VBox()
		vboxNotebookFileName.set_spacing(10)
		vboxNotebookFileName.set_homogeneous(False)
		self.notebook.append_page(vboxNotebookFileName, labelNotebookFileName)
		labelNotebookFileName.show()
		vboxNotebookFileName.show()

		# Cornice per la scelta del nome file
		frameFileName = gtk.Frame()
		frameFileName.set_shadow_type(gtk.SHADOW_NONE)
		vboxNotebookFileName.pack_start(frameFileName, expand=False)
		frameFileName.show()

		# Label per la scelta del nome file
		labelFileName = gtk.Label()
		labelFileName.set_use_markup(True)
		labelFileName.set_label("<b>How to name files?</b>")
		labelFileName.set_padding(0, 10)
		frameFileName.set_label_widget(labelFileName)
		labelFileName.show()

		# VBox per la scelta del nome file
		vboxFileName = gtk.VBox()
		frameFileName.add(vboxFileName)
		vboxFileName.set_spacing(10)
		vboxFileName.set_homogeneous(False)
		vboxFileName.show()

		# ComboBox per il nome dei file
		hboxFileName1 = gtk.HBox()
		hboxFileName1.set_homogeneous(True)
		vboxFileName.pack_start(hboxFileName1, expand = False)
		hboxFileName1.show()
		pref_pattern =  self.prefs.get_option("filename-pattern")
		self.comboFileName = gtk.combo_box_new_text()
		for fnp in FILENAME_PATTERN:
			if fnp[0] == pref_pattern:
				pattern_index = FILENAME_PATTERN.index(fnp)
			if fnp[1] == "":
				self.comboFileName.append_text(fnp[0])
			else:
				self.comboFileName.append_text(fnp[0] + " (" + fnp[1] + ")")
		try:
			self.comboFileName.set_active(pattern_index) #setta il default
		except:
			self.comboFileName.set_active(3)
		hboxFileName1.pack_start(self.comboFileName, padding=20)
		self.comboFileName.show()

		# Entry per il nome dei file personalizzato
		hboxFileName2 = gtk.HBox()
		hboxFileName2.set_homogeneous(False)
		vboxFileName.pack_start(hboxFileName2, expand = False)
		hboxFileName2.show()
		self.labelPattern = gtk.Label("Filename pattern:")
		hboxFileName2.pack_start(self.labelPattern, expand=False, padding=20)
		self.labelPattern.set_sensitive(False)
		self.labelPattern.show()
		self.entryFileName = gtk.Entry()
		self.entryFileName.set_size_request(10,-1)
		hboxFileName2.pack_start(self.entryFileName, expand=True, padding=20)
		self.entryFileName.set_sensitive(False)
		self.entryFileName.show()
		# Attiva l'evento della combo e verifica l'index nelle preferenze
		self.comboFileName.connect("changed", self.on_filename_pattern_changed)
		self.on_filename_pattern_changed()
		prefs_alt_pat = self.prefs.get_option("alternate-filename-pattern")
		self.entryFileName.set_text(re.sub('(?=\w)', '%', prefs_alt_pat))

		# Istruzioni
		hboxFileName3 = gtk.HBox()
		hboxFileName3.set_homogeneous(False)
		vboxFileName.pack_start(hboxFileName3, expand = False)
		hboxFileName3.show()
		self.labelInfoPattern = gtk.Label(INFO_PATTERN)
		self.labelInfoPattern.set_use_markup(True)
		hboxFileName3.pack_start(self.labelInfoPattern, expand=False, padding=40)
		self.labelInfoPattern.show()

		# Underscore
		hboxFileName4 = gtk.HBox()
		hboxFileName4.set_homogeneous(False)
		vboxFileName.pack_start(hboxFileName4, expand = False)
		hboxFileName4.show()
		self.checkUnderscore = gtk.CheckButton("Replace spaces by underscores", True)
		#self.checkUnderscore.connect("toggled", self.on_underscores)
		hboxFileName4.pack_start(self.checkUnderscore, padding=20)
		self.checkUnderscore.show()

		# Setta il check
		if bool(int(self.prefs.get_option("replace-spaces-by-underscores"))):
			self.checkUnderscore.set_active(True)
			#self.on_underscores()
		else:
			self.checkUnderscore.set_active(False)

		# Cornice per gli ID tag
		self.frameTag = gtk.Frame()
		self.frameTag.set_shadow_type(gtk.SHADOW_NONE)
		vboxNotebookFileName.pack_start(self.frameTag, expand=False)
		self.frameTag.show()

		# Label per gli ID tag
		labelTag = gtk.Label()
		labelTag.set_use_markup(True)
		labelTag.set_label("<b>Would you write metadata tags?</b>")
		labelTag.set_padding(0, 10)
		self.frameTag.set_label_widget(labelTag)
		labelTag.show()

		# VBox per la scelta dei tag
		vboxTag = gtk.VBox()
		self.frameTag.add(vboxTag)
		vboxTag.set_homogeneous(False)
		vboxTag.set_spacing(6)
		vboxTag.show()

		# Check button per gli ID3v1
		hboxID3v1 = gtk.HBox()
		hboxID3v1.set_homogeneous(False)
		vboxTag.pack_start(hboxID3v1, expand=False)
		hboxID3v1.show()
		self.checkID3v1 = gtk.CheckButton("Write tags (ID3v1.1, Vorbis comment, FLAC comment)", True)
		self.checkID3v1.connect("toggled", self.on_create_id3v1)
		hboxID3v1.pack_start(self.checkID3v1, padding=20)
		self.checkID3v1.show()

		# Check button per gli ID3v2
		hboxID3v2 = gtk.HBox()
		hboxID3v2.set_homogeneous(False)
		vboxTag.pack_start(hboxID3v2, expand=False)
		hboxID3v2.show()
		self.checkID3v2 = gtk.CheckButton("Additional write ID3v2.4 tags in MP3 files", True)
		#self.checkID3v2.connect("toggled", self.on_create_id3v2)
		hboxID3v2.pack_start(self.checkID3v2, padding=20)
		self.checkID3v2.show()
		self.checkID3v2.set_sensitive(False)

		# Setta il check
		if bool(int(self.prefs.get_option("write-id3v1"))):
			self.checkID3v1.set_active(True)
		else:
			self.checkID3v1.set_active(False)

		if bool(int(self.prefs.get_option("write-id3v2"))):
			self.checkID3v2.set_active(True)
			#self.on_create_id3v2()
		else:
			self.checkID3v2.set_active(False)
		self.on_create_id3v1()

		# Playlist
		hboxPlaylist = gtk.HBox()
		hboxPlaylist.set_homogeneous(False)
		vboxTag.pack_start(hboxPlaylist, expand=False)
		hboxPlaylist.show()
		self.checkPlaylist = gtk.CheckButton("Create playlist (*.m3u)", True)
		#self.checkPlaylist.connect("toggled", self.on_playlist)
		hboxPlaylist.pack_start(self.checkPlaylist, padding=20)
		self.checkPlaylist.show()

		# Setta il check
		if bool(int(self.prefs.get_option("playlist"))):
			self.checkPlaylist.set_active(True)
		else:
			self.checkPlaylist.set_active(False)


		# Pagina 3
		# Label della pagina
		self.labelNotebookConverter = gtk.Label()
		self.labelNotebookConverter.set_use_markup(True)
		self.labelNotebookConverter.set_label("Converter")

		# VBox per dividere la pagina
		self.vboxNotebookConverter = gtk.VBox()
		self.vboxNotebookConverter.set_spacing(10)
		self.vboxNotebookConverter.set_homogeneous(False)
		self.notebook.append_page(self.vboxNotebookConverter, self.labelNotebookConverter)
		self.labelNotebookConverter.show()
		self.vboxNotebookConverter.show()

		# Cornice per i radio buttons convert
		frameChoise = gtk.Frame()
		self.vboxNotebookConverter.pack_start(frameChoise, expand=False)
		frameChoise.set_shadow_type(gtk.SHADOW_NONE)
		frameChoise.show()

		# Etichetta del frame
		labelSelectFile = gtk.Label()
		labelSelectFile.set_use_markup(True)
		labelSelectFile.set_label("<b>Convert all or only selected tracks?</b>")
		labelSelectFile.set_padding(0, 10)
		frameChoise.set_label_widget(labelSelectFile)
		labelSelectFile.show()

		# VBox per i radio buttons
		vboxChoise = gtk.VBox()
		frameChoise.add(vboxChoise)
		vboxChoise.set_homogeneous(False)
		vboxChoise.set_spacing(6)
		vboxChoise.show()

		# Radio button per scegliere di convertire tutte le tracce
		hboxChoise1 = gtk.HBox()
		hboxChoise1.set_homogeneous(True)
		vboxChoise.pack_start(hboxChoise1, expand=False)
		hboxChoise1.show()
		self.radioAll = gtk.RadioButton(None, "Convert all tracks", True)
		hboxChoise1.pack_start(self.radioAll, padding=20)
		self.radioAll.show()

		# Radio button per scegliere di rippare solo le tracce selezionate
		hboxChoise2 = gtk.HBox()
		hboxChoise2.set_homogeneous(True)
		vboxChoise.pack_start(hboxChoise2, expand=False)
		hboxChoise2.show()
		self.radioSelected = gtk.RadioButton(None, "Convert only selected tracks", True)
		hboxChoise2.pack_start(self.radioSelected, padding=20)
		self.radioSelected.show()

		if not bool(int(self.prefs.get_option("save-all-tracks"))):
			self.radioSelected.set_group(None)
			self.radioAll.set_group(self.radioSelected)
		else:
			self.radioAll.set_group(None)
			self.radioSelected.set_group(self.radioAll)

		# Check button per cancellare i file originali
		hboxChoise3 = gtk.HBox()
		hboxChoise3.set_homogeneous(False)
		vboxChoise.pack_start(hboxChoise3, expand=False)
		hboxChoise3.show()
		self.checkDelete = gtk.CheckButton("Delete original files", True)
		self.checkDelete.connect("toggled", self.on_delete_original_files)
		hboxChoise3.pack_start(self.checkDelete, padding=40)
		self.checkDelete.show()

		# Setta il check
		if bool(int(self.prefs.get_option("delete-original-files"))):
			self.checkDelete.set_active(True)
		else:
			self.checkDelete.set_active(False)

		# Cornice per la scelta dell'encoder
		frameEncoder = gtk.Frame()
		frameEncoder.set_shadow_type(gtk.SHADOW_NONE)
		self.vboxNotebookConverter.pack_start(frameEncoder, expand=False)
		frameEncoder.show()

		# Label per la scelta dell'encoder
		labelEncoder = gtk.Label()
		labelEncoder.set_use_markup(True)
		labelEncoder.set_label("<b>Type of result?</b>")
		labelEncoder.set_padding(0, 10)
		frameEncoder.set_label_widget(labelEncoder)
		labelEncoder.show()

		# VBox per la scelta dell'encoder
		vboxEncoder = gtk.VBox()
		frameEncoder.add(vboxEncoder)
		vboxEncoder.set_homogeneous(False)
		vboxEncoder.set_spacing(6)
		vboxEncoder.show()

		# Check button per la scelta di un encoder esterno
		# Se selezionato visualizza self.vboxExternalEncoder
		# Altrimenti visualizza self.vboxInternalEncoder
		hboxEncoder = gtk.HBox()
		hboxEncoder.set_homogeneous(False)
		vboxEncoder.pack_start(hboxEncoder, expand=False)
		hboxEncoder.show()
		self.checkExternalEncoder = gtk.CheckButton("Use external encoder", True)
		self.checkExternalEncoder.connect("toggled", self.on_external_encoder)
		hboxEncoder.pack_start(self.checkExternalEncoder, padding=20, expand=False)
		self.checkExternalEncoder.show()

		# Vbox per encoder esterni
		self.vboxExternalEncoder = gtk.VBox()
		vboxEncoder.pack_start(self.vboxExternalEncoder, expand=False)
		self.vboxExternalEncoder.set_homogeneous(False)
		self.vboxExternalEncoder.set_spacing(6)
		# Solo se checkExternalEncoder è selezionato
		#self.vboxExternalEncoder.show()

		# ComboBox per la scelta di un encoder esterno
		hboxExternalEncoder1 = gtk.HBox()
		hboxExternalEncoder1.set_homogeneous(False)
		self.vboxExternalEncoder.pack_start(hboxExternalEncoder1, expand = False)
		hboxExternalEncoder1.show()
		prefs_ext_enc = self.prefs.get_option("external-encoder")
		self.comboExternalEncoder = gtk.combo_box_new_text()
		for ex in EXTERNAL_ENCODERS:
			if ex[1] == prefs_ext_enc:
				ext_enc_index = EXTERNAL_ENCODERS.index(ex)
			if ex[0] == "User defined encoder":
				self.comboExternalEncoder.insert_text(0, ex[0])
			else:
				self.comboExternalEncoder.insert_text(EXTERNAL_ENCODERS.index(ex), ex[0] + " (" + ex[1] + ")")
		try:
			self.comboExternalEncoder.set_active(ext_enc_index) #setta il default
		except:
			self.comboExternalEncoder.set_active(0)
		self.comboExternalEncoder.connect("changed", self.on_external_encoder_select)
		hboxExternalEncoder1.pack_start(self.comboExternalEncoder, padding=20, expand = False)
		self.comboExternalEncoder.show()

		# Il relativo pulsante che apre il FileChooser
		self.cmdExternalEncoder = gtk.Button("Browse...")
		self.cmdExternalEncoder.connect("clicked", self.on_external_encoder_choise)
		hboxExternalEncoder1.pack_end(self.cmdExternalEncoder, expand=False, padding=20)
		self.cmdExternalEncoder.set_sensitive(False)
		self.cmdExternalEncoder.show()

		# Contenitore di VBox per encoder esterni
		self.listVboxExternal = []
		
		# Vbox per comando personalizzato
		self.vboxUserEncoder = gtk.VBox()
		self.listVboxExternal.insert(self.encoder_index("user", EXTERNAL_ENCODERS), self.vboxUserEncoder)
		self.vboxExternalEncoder.pack_start(self.vboxUserEncoder, expand=False)
		self.vboxUserEncoder.set_homogeneous(False)
		self.vboxUserEncoder.set_spacing(6)
		#self.vboxUserEncoder.show()

		# Eventuale comando esterno
		hboxUserEncoder1 = gtk.HBox()
		hboxUserEncoder1.set_homogeneous(False)
		self.vboxUserEncoder.pack_start(hboxUserEncoder1, expand = False)
		# Si attiva solo se selezionato dal combo box e se
		# l'utente ha restituito un programma eseguibile
		hboxUserEncoder1.show()
		self.labelUserEncoder = gtk.Label("External command used for compression:")
		self.labelUserEncoder.set_padding(0, 5)
		hboxUserEncoder1.pack_start(self.labelUserEncoder, expand=False, padding=20)
		self.labelUserEncoder.show()
		hboxUserEncoder2 = gtk.HBox()
		hboxUserEncoder2.set_homogeneous(False)
		self.vboxUserEncoder.pack_start(hboxUserEncoder2, expand = False)
		# Si attiva solo se selezionato dal combo box e se
		# l'utente ha restituito un programma eseguibile
		hboxUserEncoder2.show()
		self.entryUserEncoder = gtk.Entry()
		self.entryUserEncoder.set_size_request(10,-1)
		#self.entryUserEncoder.connect("changed", self.on_user_encoder_entry)
		self.entryUserEncoder.connect("focus-out-event", self.on_user_encoder_entry)
		hboxUserEncoder2.pack_start(self.entryUserEncoder, expand=True, padding=20)
		self.entryUserEncoder.show()
		try:
			self.entryUserEncoder.set_text(self.prefs.get_option("user-defined-encoder-command"))
		except:
			self.entryUserEncoder.set_text("")
		
		# Vbox per Lame a linea di comando
		if self.encoder_index("lame", EXTERNAL_ENCODERS) != None:
			self.vboxLameEncoder = gtk.VBox()
			self.listVboxExternal.insert(self.encoder_index("lame", EXTERNAL_ENCODERS), self.vboxLameEncoder)
			self.vboxExternalEncoder.pack_start(self.vboxLameEncoder, expand=False)
			self.vboxLameEncoder.set_homogeneous(False)
			self.vboxLameEncoder.set_spacing(6)
			
			# Label per le istruzioni di Lame
			hboxLameEncoder1 = gtk.HBox()
			hboxLameEncoder1.set_homogeneous(False)
			self.vboxLameEncoder.pack_start(hboxLameEncoder1, expand=False)
			hboxLameEncoder1.show()
			labelLameEncoder = gtk.Label()
			labelLameEncoder.set_use_markup(True)
			labelLameEncoder.set_justify(gtk.JUSTIFY_LEFT)
			labelLameEncoder.set_label('''Encoder options:''')
			labelLameEncoder.set_padding(0, 5)
			hboxLameEncoder1.pack_start(labelLameEncoder, expand=False, padding=20)
			labelLameEncoder.show()

			# Label per le info su Lame
			hboxLameEncoder2 = gtk.HBox()
			hboxLameEncoder2.set_homogeneous(False)
			self.vboxLameEncoder.pack_start(hboxLameEncoder2, expand=False)
			hboxLameEncoder2.show()
			labelLameInfo = gtk.Label()
			labelLameInfo.set_use_markup(True)
			labelLameInfo.set_justify(gtk.JUSTIFY_LEFT)
			labelLameInfo.set_label('''<span size='small'><b>Recommended:  -V2</b>
<i>See </i>'lame --help'<i> and visit </i>http://www.mp3dev.org/</span>''')
			#labelLameInfo.set_padding(0, 5)
			hboxLameEncoder2.pack_start(labelLameInfo, expand=False, padding=40)
			labelLameInfo.show()

			# Entry per inserire le opzioni di Lame
			hboxLameEncoder3 = gtk.HBox()
			hboxLameEncoder3.set_homogeneous(False)
			self.vboxLameEncoder.pack_start(hboxLameEncoder3, expand=False)
			hboxLameEncoder3.show()
			self.entryLameOptions = gtk.Entry()
			self.entryLameOptions.set_size_request(10,-1)
			hboxLameEncoder1.pack_start(self.entryLameOptions, expand=True, padding=20)
			self.entryLameOptions.show()
			try:
				self.entryLameOptions.set_text(self.prefs.get_option("lame-options"))
			except:
				self.entryLameOptions.set_text("")
				
		# Vbox per Ogg a linea di comando
		if self.encoder_index("oggenc", EXTERNAL_ENCODERS) != None:
			self.vboxOggEncoder = gtk.VBox()
			self.listVboxExternal.insert(self.encoder_index("oggenc", EXTERNAL_ENCODERS), self.vboxOggEncoder)
			self.vboxExternalEncoder.pack_start(self.vboxOggEncoder, expand=False)
			self.vboxOggEncoder.set_homogeneous(False)
			self.vboxOggEncoder.set_spacing(6)
			
			# Label per le istruzioni di Ogg
			hboxOggEncoder1 = gtk.HBox()
			hboxOggEncoder1.set_homogeneous(False)
			self.vboxOggEncoder.pack_start(hboxOggEncoder1, expand=False)
			hboxOggEncoder1.show()
			labelOggEncoder = gtk.Label()
			labelOggEncoder.set_use_markup(True)
			labelOggEncoder.set_justify(gtk.JUSTIFY_LEFT)
			labelOggEncoder.set_label('''Encoder options:''')
			labelOggEncoder.set_padding(0, 5)
			hboxOggEncoder1.pack_start(labelOggEncoder, expand=False, padding=20)
			labelOggEncoder.show()

			# Label per le info su Ogg
			hboxOggEncoder2 = gtk.HBox()
			hboxOggEncoder2.set_homogeneous(False)
			self.vboxOggEncoder.pack_start(hboxOggEncoder2, expand=False)
			hboxOggEncoder2.show()
			labelOggInfo = gtk.Label()
			labelOggInfo.set_use_markup(True)
			labelOggInfo.set_justify(gtk.JUSTIFY_LEFT)
			labelOggInfo.set_label('''<span size='small'><b>Recommended:  -q 6</b>
<i>See </i>'oggenc -h'<i> and visit 
</i>http://vorbis.com/ <i>or</i> http://xiph.org/vorbis/</span>''')
			#labelOggInfo.set_padding(0, 5)
			hboxOggEncoder2.pack_start(labelOggInfo, expand=False, padding=40)
			labelOggInfo.show()

			# Entry per inserire le opzioni di Ogg
			hboxOggEncoder3 = gtk.HBox()
			hboxOggEncoder3.set_homogeneous(False)
			self.vboxOggEncoder.pack_start(hboxOggEncoder3, expand=False)
			hboxOggEncoder3.show()
			self.entryOggOptions = gtk.Entry()
			self.entryOggOptions.set_size_request(10,-1)
			hboxOggEncoder1.pack_start(self.entryOggOptions, expand=True, padding=20)
			self.entryOggOptions.show()
			try:
				self.entryOggOptions.set_text(self.prefs.get_option("vorbis-options"))
			except:
				self.entryOggOptions.set_text("")
				
		# Vbox per Flac a linea di comando
		if self.encoder_index("flac", EXTERNAL_ENCODERS) != None:
			self.vboxFlacEncoder = gtk.VBox()
			self.listVboxExternal.insert(self.encoder_index("flac", EXTERNAL_ENCODERS), self.vboxFlacEncoder)
			self.vboxExternalEncoder.pack_start(self.vboxFlacEncoder, expand=False)
			self.vboxFlacEncoder.set_homogeneous(False)
			self.vboxFlacEncoder.set_spacing(6)
			
			# Label per le istruzioni di Flac
			hboxFlacEncoder1 = gtk.HBox()
			hboxFlacEncoder1.set_homogeneous(False)
			self.vboxFlacEncoder.pack_start(hboxFlacEncoder1, expand=False)
			hboxFlacEncoder1.show()
			labelFlacEncoder = gtk.Label()
			labelFlacEncoder.set_use_markup(True)
			labelFlacEncoder.set_justify(gtk.JUSTIFY_LEFT)
			labelFlacEncoder.set_label('''Encoder options:''')
			labelFlacEncoder.set_padding(0, 5)
			hboxFlacEncoder1.pack_start(labelFlacEncoder, expand=False, padding=20)
			labelFlacEncoder.show()

			# Label per le info su Flac
			hboxFlacEncoder2 = gtk.HBox()
			hboxFlacEncoder2.set_homogeneous(False)
			self.vboxFlacEncoder.pack_start(hboxFlacEncoder2, expand=False)
			hboxFlacEncoder2.show()
			labelFlacInfo = gtk.Label()
			labelFlacInfo.set_use_markup(True)
			labelFlacInfo.set_justify(gtk.JUSTIFY_LEFT)
			labelFlacInfo.set_label('''<span size='small'><b>Recommended:  -5</b>
<i>See </i>'flac --help'<i> and visit </i>http://flac.sourceforge.net/</span>''')
			#labelFlacInfo.set_padding(0, 5)
			hboxFlacEncoder2.pack_start(labelFlacInfo, expand=False, padding=40)
			labelFlacInfo.show()

			# Entry per inserire le opzioni di Flac
			hboxFlacEncoder3 = gtk.HBox()
			hboxFlacEncoder3.set_homogeneous(False)
			self.vboxFlacEncoder.pack_start(hboxFlacEncoder3, expand=False)
			hboxFlacEncoder3.show()
			self.entryFlacOptions = gtk.Entry()
			self.entryFlacOptions.set_size_request(10,-1)
			hboxFlacEncoder1.pack_start(self.entryFlacOptions, expand=True, padding=20)
			self.entryFlacOptions.show()
			try:
				self.entryFlacOptions.set_text(self.prefs.get_option("flac-options"))
			except:
				self.entryFlacOptions.set_text("")

		# Visualizza le opzioni dell'encoder esterno di defualt
		self.on_external_encoder_select()

		# Encoder a linea di comando non disponibili
		if len(EXTERNAL_ENCODERS_NOT_AVAILABLE) > 0:

			self.vboxNotAv = gtk.VBox()
			vboxEncoder.pack_end(self.vboxNotAv, expand = True)
			self.vboxNotAv.set_homogeneous(False)
			self.vboxNotAv.set_spacing(6)
			#self.vboxNotAv.show()

			hboxExternalEncoder2 = gtk.HBox()
			hboxExternalEncoder2.set_homogeneous(False)
			self.vboxNotAv.pack_end(hboxExternalEncoder2, expand = False)
			hboxExternalEncoder2.show()

			imgNA = gtk.Image()
			imgNA.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_DND)
			hboxExternalEncoder2.pack_start(imgNA, expand=False, padding=20)
			imgNA.show()
			self.labelNotAvailable = gtk.Label()
			self.labelNotAvailable.set_use_markup(True)
			hboxExternalEncoder2.pack_start(self.labelNotAvailable, expand=False)
			notavailablestring = ""
			for prog in EXTERNAL_ENCODERS_NOT_AVAILABLE:
				if notavailablestring == "":
					notavailablestring = prog[0] + " (" + prog[1] + ")"
				elif len(notavailablestring.split(", ")) == (len(EXTERNAL_ENCODERS_NOT_AVAILABLE) -1 ):
					notavailablestring = notavailablestring + " and " + prog[0] + " (" + prog[1] + ")"
				else:
					notavailablestring = notavailablestring + ", " + prog[0] + " (" + prog[1] + ")"
			self.labelNotAvailable.set_size_request(270, -1)
			self.labelNotAvailable.set_padding(0, 2)
			self.labelNotAvailable.set_line_wrap(True)
			self.labelNotAvailable.set_justify(gtk.JUSTIFY_LEFT)
			self.labelNotAvailable.set_label("""<span size='x-small'>""" + notavailablestring + """ not available. Please install the program. Try using your packet manager (e.g. 'apt-get install <i>packet-name</i>') or visit the program website.</span>""")
			self.labelNotAvailable.show()
			separator = gtk.HSeparator()
			self.vboxNotAv.pack_end(separator, expand = False)
			separator.show()

		# Vbox per encoder interni
		self.vboxInternalEncoder = gtk.VBox()
		vboxEncoder.pack_start(self.vboxInternalEncoder, expand=False)
		self.vboxInternalEncoder.set_homogeneous(False)
		self.vboxInternalEncoder.set_spacing(6)
		# Solo se checkExternalEncoder NON è selezionato (default)
		self.vboxInternalEncoder.show()
		
		# ComboBox e label per la scelta di un encoder interno
		hboxInternalEncoder1 = gtk.HBox()
		hboxInternalEncoder1.set_homogeneous(False)
		self.vboxInternalEncoder.pack_start(hboxInternalEncoder1, expand = False)
		hboxInternalEncoder1.show()
		labelInternalEncoder = gtk.Label()
		labelInternalEncoder.set_use_markup(True)
		labelInternalEncoder.set_justify(gtk.JUSTIFY_LEFT)
		labelInternalEncoder.set_label('''Output format:''')
		labelInternalEncoder.set_padding(0, 5)
		hboxInternalEncoder1.pack_start(labelInternalEncoder, expand=False, padding=20)
		labelInternalEncoder.show()
		self.comboInternalEncoder = gtk.combo_box_new_text()
		pref_intenc = self.prefs.get_option("output-format")
		for ex in INTERNAL_ENCODERS:
			if ex[1] == pref_intenc:
				intenc_index = INTERNAL_ENCODERS.index(ex)
			self.comboInternalEncoder.insert_text(INTERNAL_ENCODERS.index(ex), ex[0] + " (." + ex[1] + ")")
		try:
			self.comboInternalEncoder.set_active(intenc_index) #setta il default
		except:
			self.comboInternalEncoder.set_active(0)
		self.comboInternalEncoder.connect("changed", self.on_internal_encoder_select)
		self.comboInternalEncoder.set_size_request(220,-1)
		hboxInternalEncoder1.pack_end(self.comboInternalEncoder, padding=20, expand=False)
		self.comboInternalEncoder.show()
		
		# Contenitore di VBox per encoder interni
		self.listVboxInternal = []
		
		# Vbox per Ogg Vorbis
		if self.encoder_index("ogg", INTERNAL_ENCODERS) != None:
			self.vboxOGG = gtk.VBox()
			self.listVboxInternal.insert(self.encoder_index("ogg", INTERNAL_ENCODERS), self.vboxOGG)
			self.vboxInternalEncoder.pack_start(self.vboxOGG, expand=False)
			self.vboxOGG.set_homogeneous(False)
			self.vboxOGG.set_spacing(6)

			# ComboBox e label per la scelta della qualità
			hboxOGG2 = gtk.HBox()
			hboxOGG2.set_homogeneous(False)
			self.vboxOGG.pack_start(hboxOGG2, expand = False)
			hboxOGG2.show()
			labelOGGQuality = gtk.Label()
			labelOGGQuality.set_use_markup(True)
			labelOGGQuality.set_justify(gtk.JUSTIFY_LEFT)
			labelOGGQuality.set_label('''Quality:''')
			labelOGGQuality.set_padding(0, 5)
			hboxOGG2.pack_start(labelOGGQuality, expand=False, padding=20)
			labelOGGQuality.show()
			prefs_ogg_qual = int(self.prefs.get_option("vorbis-quality"))
			self.comboOGGQuality = gtk.combo_box_new_text()
			for qu in OGG_QUAL:
				if qu[1] == prefs_ogg_qual:
					qual_ogg_index = OGG_QUAL.index(qu)
				self.comboOGGQuality.insert_text(OGG_QUAL.index(qu), qu[0])
			try:
				self.comboOGGQuality.set_active(qual_ogg_index)
			except:
				self.comboOGGQuality.set_active(4)
			#self.comboOGGQuality.connect("changed", self.on_ogg_quality_select)
			self.comboOGGQuality.set_size_request(220,-1)
			hboxOGG2.pack_end(self.comboOGGQuality, padding=20, expand=False)
			self.comboOGGQuality.show()
		
		# Vbox per MP3
		if self.encoder_index("mp3", INTERNAL_ENCODERS) != None:
			self.vboxMP3 = gtk.VBox()
			self.listVboxInternal.insert(self.encoder_index("mp3", INTERNAL_ENCODERS), self.vboxMP3)
			self.vboxInternalEncoder.pack_start(self.vboxMP3, expand=False)
			self.vboxMP3.set_homogeneous(False)
			self.vboxMP3.set_spacing(6)
			
			# ComboBox e label per la scelta del bitrate
			hboxMP31 = gtk.HBox()
			hboxMP31.set_homogeneous(False)
			self.vboxMP3.pack_start(hboxMP31, expand = False)
			hboxMP31.show()
			labelMP3Bitrate = gtk.Label()
			labelMP3Bitrate.set_use_markup(True)
			labelMP3Bitrate.set_justify(gtk.JUSTIFY_LEFT)
			labelMP3Bitrate.set_label('''Bitrate mode:''')
			labelMP3Bitrate.set_padding(0, 5)
			hboxMP31.pack_start(labelMP3Bitrate, expand=False, padding=20)
			labelMP3Bitrate.show()
			prefs_mp3_br = self.prefs.get_option("mp3-bitrate-mode")
			self.comboMP3Mode = gtk.combo_box_new_text()
			for br in MP3_MODE:
				if br[1] == prefs_mp3_br:
					mp3_br_index = MP3_MODE.index(br)
				self.comboMP3Mode.insert_text(MP3_MODE.index(br), br[0] + " (" + br[1] + ")")
			try:
				self.comboMP3Mode.set_active(mp3_br_index)
			except:
				self.comboMP3Mode.set_active(2) #setta il default
			self.comboMP3Mode.connect("changed", self.on_mp3_mode_select)
			self.comboMP3Mode.set_size_request(220,-1)
			hboxMP31.pack_end(self.comboMP3Mode, padding=20, expand=False)
			self.comboMP3Mode.show()
			
			# ComboBox e label per la scelta della qualità
			self.hboxMP32 = gtk.HBox()
			self.hboxMP32.set_homogeneous(False)
			self.vboxMP3.pack_start(self.hboxMP32, expand = False)
			#self.hboxMP32.show()
			labelMP3Quality = gtk.Label()
			labelMP3Quality.set_use_markup(True)
			labelMP3Quality.set_justify(gtk.JUSTIFY_LEFT)
			labelMP3Quality.set_label('''Quality:''')
			labelMP3Quality.set_padding(0, 5)
			self.hboxMP32.pack_start(labelMP3Quality, expand=False, padding=20)
			labelMP3Quality.show()
			prefs_mp3_qual = int(self.prefs.get_option("mp3-quality"))
			self.comboMP3Quality = gtk.combo_box_new_text()
			for qu in MP3_QUAL:
				if prefs_mp3_qual == qu[1]:
					mp3_qual_index = MP3_QUAL.index(qu)
				self.comboMP3Quality.insert_text(MP3_QUAL.index(qu), qu[0])
			try:
				self.comboMP3Quality.set_active(mp3_qual_index) #setta il default
			except:
				self.comboMP3Quality.set_active(4)
			#self.comboMP3Quality.connect("changed", self.on_mp3_quality_select)
			self.comboMP3Quality.set_size_request(220,-1)
			self.hboxMP32.pack_end(self.comboMP3Quality, padding=20, expand=False)
			self.comboMP3Quality.show()

			# ComboBox e label per la scelta del bitrate
			self.hboxMP33 = gtk.HBox()
			self.hboxMP33.set_homogeneous(False)
			self.vboxMP3.pack_start(self.hboxMP33, expand = False)
			#self.hboxMP33.show()
			labelMP3Bitrate = gtk.Label()
			labelMP3Bitrate.set_use_markup(True)
			labelMP3Bitrate.set_justify(gtk.JUSTIFY_LEFT)
			labelMP3Bitrate.set_label('''Bitrate:''')
			labelMP3Bitrate.set_padding(0, 5)
			self.hboxMP33.pack_start(labelMP3Bitrate, expand=False, padding=20)
			labelMP3Bitrate.show()
			prefs_mp3_bitrate = int(self.prefs.get_option("mp3-bitrate"))
			self.comboMP3Bitrate = gtk.combo_box_new_text()
			for bit in MP3_BITRATE:
				if prefs_mp3_bitrate == bit:
					mp3_bitrate_index = MP3_BITRATE.index(bit)
				self.comboMP3Bitrate.insert_text(MP3_BITRATE.index(bit), str(bit) + " kbit/s")
			try:
				self.comboMP3Bitrate.set_active(mp3_bitrate_index) #setta il default
			except:
				self.comboMP3Quality.set_active(12)
			#self.comboMP3Bitrate.connect("changed", self.on_mp3_bitrate_select)
			self.comboMP3Bitrate.set_size_request(220,-1)
			self.hboxMP33.pack_end(self.comboMP3Bitrate, padding=20, expand=False)
			self.comboMP3Bitrate.show()
			
			if self.prefs.get_option("mp3-bitrate-mode") == "VBR":
				self.hboxMP32.show()
				self.hboxMP33.hide()
			else:
				self.hboxMP32.hide()
				self.hboxMP33.show()
				
		
		# Vbox per FLAC
		if self.encoder_index("flac", INTERNAL_ENCODERS) != None:
			self.vboxFLAC = gtk.VBox()
			self.listVboxInternal.insert(self.encoder_index("flac", INTERNAL_ENCODERS), self.vboxFLAC)
			self.vboxInternalEncoder.pack_start(self.vboxFLAC, expand=False)
			self.vboxFLAC.set_homogeneous(False)
			self.vboxFLAC.set_spacing(6)
			
			# ComboBox e label per la scelta della qualità
			hboxFLAC2 = gtk.HBox()
			hboxFLAC2.set_homogeneous(False)
			self.vboxFLAC.pack_start(hboxFLAC2, expand = False)
			hboxFLAC2.show()
			labelFLACQuality = gtk.Label()
			labelFLACQuality.set_use_markup(True)
			labelFLACQuality.set_justify(gtk.JUSTIFY_LEFT)
			labelFLACQuality.set_label('''Quality:''')
			labelFLACQuality.set_padding(0, 5)
			hboxFLAC2.pack_start(labelFLACQuality, expand=False, padding=20)
			labelFLACQuality.show()
			prefs_FLAC_qual = int(self.prefs.get_option("flac-quality"))
			self.comboFLACQuality = gtk.combo_box_new_text()
			for qu in FLAC_QUAL:
				if qu[1] == prefs_FLAC_qual:
					qual_FLAC_index = FLAC_QUAL.index(qu)
				self.comboFLACQuality.insert_text(FLAC_QUAL.index(qu), qu[0])
			try:
				self.comboFLACQuality.set_active(qual_FLAC_index)
			except:
				self.comboFLACQuality.set_active(4)
			#self.comboFLACQuality.connect("changed", self.on_FLAC_quality_select)
			self.comboFLACQuality.set_size_request(220,-1)
			hboxFLAC2.pack_end(self.comboFLACQuality, padding=20, expand=False)
			self.comboFLACQuality.show()
			
		# Vbox per WAV
		if self.encoder_index("wav", INTERNAL_ENCODERS) != None:
			self.vboxWAV = gtk.VBox()
			self.listVboxInternal.insert(self.encoder_index("wav", INTERNAL_ENCODERS), self.vboxWAV)
			self.vboxInternalEncoder.pack_start(self.vboxWAV, expand=False)
			self.vboxWAV.set_homogeneous(False)
			self.vboxWAV.set_spacing(6)
			
		# Visualizza le opzioni dell'encoder interno di defualt
		self.on_internal_encoder_select()

		# Checkbox e ComboBox per il ricampionamento
		self.hboxResample = gtk.HBox()
		self.hboxResample.set_homogeneous(False)
		vboxEncoder.pack_start(self.hboxResample, expand = False)
		self.hboxResample.show()
		self.checkResample = gtk.CheckButton("Resample", True)
		self.checkResample.connect("toggled", self.on_resample)
		self.hboxResample.pack_start(self.checkResample, padding=20)
		self.checkResample.show()
		self.comboResampleQuality = gtk.combo_box_new_text()
		prefs_freq = int(self.prefs.get_option("resample-freq"))
		for fr in RESAMPLE_VALUE:
			if prefs_freq == fr:
				fr_index = RESAMPLE_VALUE.index(fr)
			self.comboResampleQuality.insert_text(RESAMPLE_VALUE.index(fr), str(fr) + " Hz")
		try:
			self.comboResampleQuality.set_active(fr_index) #setta il default
		except:
			self.comboResampleQuality.set_active(2)
		#self.comboResampleQuality.connect("changed", self.on_resample_changed)
		self.comboResampleQuality.set_size_request(220,-1)
		self.hboxResample.pack_end(self.comboResampleQuality, padding=20, expand=False)
		self.comboResampleQuality.show()
		self.comboResampleQuality.set_sensitive(False)

		# Setta il checkExternalEncoder
		if bool(int(self.prefs.get_option("use-external-encoder"))):
			self.checkExternalEncoder.set_active(True)
		else:
			self.checkExternalEncoder.set_active(False)

		# Setta il checkResample
		if bool(int(self.prefs.get_option("resample"))):
			self.checkResample.set_active(True)
			self.on_resample()
		else:
			self.checkResample.set_active(False)


		# Pulsante Reset
		self.cmdReset = gtk.Button(label="_Default", use_underline=True)
		self.cmdReset.connect("clicked", self.on_Reset)
		self.dlg.add_action_widget(self.cmdReset, 3)
		self.cmdReset.show()	

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

	# Attiva e visualizza la finestra di dialogo
	def show(self, *args):
		self.response = None
		self.dlg.run()
		self.dlg.destroy()
		

	# Evento del pulsante Reset
	# Torna alle impostazioni di default
	def on_Reset(self, *args):
		
		self.prefs.reset()
		self.dlg.destroy()
		self.__init__(self.main_window, self.prefs)

	# Evento per la scelta dei file da convertire (SERVE?)
	def on_Choise(self, *args):

		if self.radioAll.get_active():
			self.state_all = True
			self.state_selected = False
		elif self.radioSelected.get_active():
			self.state_all = False
			self.state_selected = True
		else:
			raise

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
			choisePath.set_current_folder(self.prefs.get_option("last-save-folder"))
		except:
			choisePath.set_current_folder(os.path.expandvars("$HOME"))
		response = choisePath.run()
		if response == gtk.RESPONSE_OK:
			self.prefs.set_option("alt-save-folder", choisePath.get_filename())
		else:
			self.prefs.set_option("alt-save-folder", self.prefs.get_option("last-save-folder"))
		choisePath.destroy()

	def on_filename_pattern_changed(self, *args):
		if self.comboFileName.get_active() == 0:
			self.entryFileName.set_sensitive(True)
			self.entryFileName.set_text(FILENAME_PATTERN[1][1])
			self.labelPattern.set_sensitive(True)
		else:
			self.entryFileName.set_sensitive(False)
			self.labelPattern.set_sensitive(False)

	def on_create_sub_folders(self, *args):

		if self.checkFolders.get_active():
			self.comboFolders.set_sensitive(True)
		elif not self.checkFolders.get_active():
			self.comboFolders.set_sensitive(False)

	def on_underscores(self, *args):
		pass

	def on_create_id3v1(self, *args):

		if self.checkID3v1.get_active():
			self.checkID3v2.set_sensitive(True)
		if not self.checkID3v1.get_active():
			self.checkID3v2.set_sensitive(False)
			self.checkID3v2.set_active(False)

	def on_delete_original_files(self, *args):
		pass
	
	# Se si è scelto un encoder interno
	def on_internal_encoder_select(self, *args):
			
			for box1 in self.listVboxInternal:
				box1.hide()

			self.listVboxInternal[self.comboInternalEncoder.get_active()].show()

	def on_mp3_mode_select(self, *args):
		
		for mp3_mode in MP3_MODE: 
			if self.comboMP3Mode.get_active() == MP3_MODE.index(("Constant bitrate", "CBR")):
				self.hboxMP32.hide()
				self.hboxMP33.show()
			elif self.comboMP3Mode.get_active() == MP3_MODE.index(("Average bitrate", "ABR")):
				self.hboxMP32.hide()
				self.hboxMP33.show()
			elif self.comboMP3Mode.get_active() == MP3_MODE.index(("Variable bitrate", "VBR")):
				self.hboxMP32.show()
				self.hboxMP33.hide()			

	# Evento per scegliere o meno di usare un encoder esterno
	# (attivato da checkExternalEncoder)
	def on_external_encoder(self, *args):

		if self.checkExternalEncoder.get_active():
			self.vboxExternalEncoder.show()
			if len(EXTERNAL_ENCODERS_NOT_AVAILABLE) > 0:
				self.vboxNotAv.show()
			self.hboxResample.hide()
			self.vboxInternalEncoder.hide()
			self.on_external_encoder_select()
		else:
			self.vboxExternalEncoder.hide()
			if len(EXTERNAL_ENCODERS_NOT_AVAILABLE) > 0:
				self.vboxNotAv.show()
			self.hboxResample.show()
			self.vboxInternalEncoder.show()
	
	# Se si è scelto un encoder esterno
	def on_external_encoder_select(self, *args):
		
		for box in self.listVboxExternal:
			box.hide()

		self.listVboxExternal[self.comboExternalEncoder.get_active()].show()

		# Se si vuole usare un comando esterno definito dall'utente
		if self.comboExternalEncoder.get_active() == self.encoder_index("user", EXTERNAL_ENCODERS):
			self.cmdExternalEncoder.set_sensitive(True)
			if self.entryUserEncoder.get_text() != "":
				self.vboxUserEncoder.show()
			else:
				self.vboxUserEncoder.hide()
		else:
			self.cmdExternalEncoder.set_sensitive(False)
		
	# Apre il FileChooser per la scelta del comando esterno e ne mostra il percorso
	def on_external_encoder_choise(self, *args):

		choiseEncoder = gtk.FileChooserDialog("Choise external encoder...", self.dlg,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		choiseEncoder.set_select_multiple(False)
		choiseEncoder.set_local_only(False)
		choiseEncoder.set_current_folder(os.path.expandvars("$HOME"))
		response = choiseEncoder.run()
		if response == gtk.RESPONSE_OK:
			# Verifica se è un eseguibile
			if self.is_exe(choiseEncoder.get_filename()):
				self.external_encoder_path = choiseEncoder.get_filename()
				self.vboxUserEncoder.show()
				self.entryUserEncoder.set_text(choiseEncoder.get_filename())
			else:
				self.external_encoder_path = None
				self.vboxUserEncoder.hide()
				self.entryUserEncoder.set_text("")
		else:
			self.external_encoder_path = None
		choiseEncoder.destroy()

	# Verifica che il testo nella entry sia un file eseguibile o un percorso corretto
	def on_user_encoder_entry(self, widget, event):
		
		try:
			isex = self.is_exe(self.entryUserEncoder.get_text())
		except:
			isex = False
		if isex:
			return
		elif self.entryUserEncoder.get_text() == "":
			return
		else:
			self.entryUserEncoder.set_text("<please, entry a valid executable path or none>")
				
	# Verifica se il percorso del comando immesso è un eseguibile
	def is_exe(self, exec_com):
		
		# Elimina le eventuali opzioni e lascia solo il comando
		# completo di percorso
		exec_enc = exec_com.split()[0]
		
		try:
			exFile = open(exec_enc, "r")
			isELF = exFile.readline()
			exFile.close()
		except:
			return False
		# TODO: Verificare se serve controllare gli script
		if os.access(exec_enc, os.X_OK) and isELF[1:4] == "ELF":
			return True
		else:
			return False

	def on_resample(self, *args):
		
		if self.checkResample.get_active():
			self.comboResampleQuality.set_sensitive(True)
		elif not self.checkResample.get_active():
			self.comboResampleQuality.set_sensitive(False)

	# Chiude e salva tutte le preferenze
	def on_Ok(self, *args):
		
		if self.radioCompressed.get_active():
			self.prefs.set_option("rip-compressed", "1")
		else:
			self.prefs.set_option("rip-compressed", "0")
			
		if self.radioHome.get_active():
			self.prefs.set_option("save-in-home", "1")
			self.prefs.set_option("save-in-same-folder", "0")
			self.prefs.set_option("save-in-last-folder", "0")
			self.prefs.set_option("select-path", "0")
		if self.radioSamePath.get_active():
			self.prefs.set_option("save-in-home", "0")
			self.prefs.set_option("save-in-same-folder", "1")
			self.prefs.set_option("save-in-last-folder", "0")
			self.prefs.set_option("select-path", "0")
		if self.radioLast.get_active():
			self.prefs.set_option("save-in-home", "0")
			self.prefs.set_option("save-in-same-folder", "0")
			self.prefs.set_option("save-in-last-folder", "1")
			self.prefs.set_option("select-path", "0")
		if self.radioAltPath.get_active():
			self.prefs.set_option("save-in-home", "0")
			self.prefs.set_option("save-in-same-folder", "0")
			self.prefs.set_option("save-in-last-folder", "0")
			self.prefs.set_option("select-path", "1")
		'''else:
			self.prefs.set_option("save-in-home", "0")
			self.prefs.set_option("save-in-same-folder", "0")
			self.prefs.set_option("save-in-last-folder", "1")
			self.prefs.set_option("select-path", "0")'''
			
		if self.checkFolders.get_active():
			self.prefs.set_option("create-subfolders", "1")
		else:
			self.prefs.set_option("create-subfolders", "0")

		self.prefs.set_option("path-subfolder", SUBFOLDERS_PATH[self.comboFolders.get_active()][0])
		self.prefs.set_option("filename-pattern", FILENAME_PATTERN[self.comboFileName.get_active()][0])
		self.prefs.set_option("alternate-filename-pattern", re.sub('%', '', self.entryFileName.get_text()))
		
		if self.checkUnderscore.get_active():
			self.prefs.set_option("replace-spaces-by-underscores", "1")
		else:
			self.prefs.set_option("replace-spaces-by-underscores", "0")
		
		if self.checkID3v1.get_active():
			self.prefs.set_option("write-id3v1", "1")
		else:
			self.prefs.set_option("write-id3v1", "0")
		
		if self.checkID3v2.get_active():
			self.prefs.set_option("write-id3v2", "1")
		else:
			self.prefs.set_option("write-id3v2", "0")

		if self.checkPlaylist.get_active():
			self.prefs.set_option("playlist", "1")
		else:
			self.prefs.set_option("playlist", "0")
			
		if self.radioSelected.get_active():
			self.prefs.set_option("save-all-tracks", "0")
		elif self.radioAll.get_active():
			self.prefs.set_option("save-all-tracks", "1")
		else:
			self.prefs.set_option("save-all-tracks", "1")
			
		if self.checkDelete.get_active():
			self.prefs.set_option("delete-original-files", "1")
		else:
			self.prefs.set_option("delete-original-files", "0")
			
		if self.checkExternalEncoder.get_active():
			self.prefs.set_option("use-external-encoder", "1")
		else:
			self.prefs.set_option("use-external-encoder", "0")
		
		self.prefs.set_option("external-encoder", EXTERNAL_ENCODERS[self.comboExternalEncoder.get_active()][1])
		if self.encoder_index("oggenc", EXTERNAL_ENCODERS) != None:
			self.prefs.set_option("vorbis-options", self.entryOggOptions.get_text())
		if self.encoder_index("lame", EXTERNAL_ENCODERS) != None:	
			self.prefs.set_option("lame-options", self.entryLameOptions.get_text())
		if self.encoder_index("flac", EXTERNAL_ENCODERS) != None:
			self.prefs.set_option("flac-options", self.entryFlacOptions.get_text())
		
		if self.entryUserEncoder.get_text() != "<please, entry a valid executable path or none>":
			self.prefs.set_option("user-defined-encoder-command", self.entryUserEncoder.get_text())
		else:
			self.prefs.set_option("user-defined-encoder-command", "")
		
		self.prefs.set_option("output-format", INTERNAL_ENCODERS[self.comboInternalEncoder.get_active()][1])
		self.prefs.set_option("vorbis-quality", str(OGG_QUAL[self.comboOGGQuality.get_active()][1]))
		self.prefs.set_option("mp3-quality", str(MP3_QUAL[self.comboMP3Quality.get_active()][1]))
		self.prefs.set_option("mp3-bitrate-mode", MP3_MODE[self.comboMP3Mode.get_active()][1])
		self.prefs.set_option("mp3-bitrate", str(MP3_BITRATE[self.comboMP3Bitrate.get_active()]))

		self.prefs.set_option("flac-quality", str(FLAC_QUAL[self.comboFLACQuality.get_active()][1]))
		if self.checkResample.get_active():
			self.prefs.set_option("resample", "1")
		else:
			self.prefs.set_option("resample", "0")
		
		self.prefs.set_option("resample-freq", str(RESAMPLE_VALUE[self.comboResampleQuality.get_active()]))
		
		self.response = gtk.RESPONSE_OK
		self.dlg.destroy()

	def on_Cancel(self, *args):

		self.state_all = False
		self.state_selected = False
		self.dlg.destroy()

	# Trova la posizione dell'encoder esterno nella lista
	# degli esistenti
	def encoder_index(self, enc, enc_list):

		for i in range(len(enc_list)):
			if enc_list[i][1] == enc:
				return i

	def change_title(self):
		pass		
