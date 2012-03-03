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


import os, re, time
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
try:
	import Image
	IMAGE = True
except:
	print("Image (PIL) not available")
	IMAGE = False

from Preferences import XACHOME, NAME, FILENAME2TAG_PATTERN, INFO_PATTERN, expand_title
from WarningDialog import *
from AudioFile import *

COVER_PATTERN = (
		("JPEG","*.jpg"),
		("JPEG","*.jpeg"),
		("PNG","*.png"),
		("GIF","*.gif"),
)


### Finestra di dialogo per la modifica dei tag ###
class TaggerDialog:

	# Costruttore della classe
	def __init__(self, mainapp, main_window, sel):

		self.mainapp = mainapp
		self.main_window = main_window
		self.sel = sel
		self.af = sel[0]
		self.it = sel[1]
		self.prefs = self.mainapp.prefs

		# Finestra di dialogo
		self.dlg = gtk.Dialog("Modify tags...", self.main_window ,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.dlg.set_default_size(410, 400)
		self.dlg.set_border_width(5)
		self.dlg.vbox.set_homogeneous(False)
		self.dlg.set_resizable(False)
		self.dlg.vbox.set_spacing(0)

		'''menuItem = gtk.Toolbar()
		self.dlg.vbox.pack_start(menuItem, expand=False)
		menuItem.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
		menuItem.show()

		buttonPrev = gtk.ToolButton(gtk.STOCK_MEDIA_PREVIOUS)
		buttonPrev.connect("clicked", self.on_Previous)
		menuItem.insert(buttonPrev, 0)
		buttonPrev.show()

		buttonNext = gtk.ToolButton(gtk.STOCK_MEDIA_NEXT)
		buttonNext.connect("clicked", self.on_Next)
		menuItem.insert(buttonNext, 1)
		buttonNext.show()'''

		# Notebook
		self.notebook = gtk.Notebook()
		self.dlg.vbox.pack_start(self.notebook, expand=False)
		self.notebook.show()

		# Pagina 0
		labelNotebookTag = gtk.Label()
		labelNotebookTag.set_use_markup(True)
		labelNotebookTag.set_label("Metadata")
		labelNotebookTag.show()

		# Cornice per la modifica dei metadata
		self.vboxMetadata = gtk.VBox()
		self.vboxMetadata.show()
		self.vboxMetadata.set_spacing(5)
		self.notebook.append_page(self.vboxMetadata, labelNotebookTag)

		# Tabella
		table = gtk.Table(11, 3)
		self.vboxMetadata.pack_start(table, expand=False, padding=5)
		table.show()

		# Titolo
		hboxTitle = gtk.HBox()
		hboxTitle.show()

		labelTitle = gtk.Label("""<span size='medium'>Title:</span>""")
		labelTitle.set_use_markup(True)
		labelTitle.set_justify(gtk.JUSTIFY_LEFT)
		labelTitle.set_line_wrap(True)
		hboxTitle.pack_start(labelTitle, expand=False)
		labelTitle.show()

		self.entryTitle = gtk.Entry()
		self.entryTitle.set_size_request(250, -1)
		self.entryTitle.show()

		'''self.checkTitle = gtk.CheckButton("All", True)
		self.checkTitle.connect("toggled", self.on_all)
		self.checkTitle.show()'''

		table.attach(hboxTitle, 1, 2, 1, 2, xpadding=10, ypadding=0)
		table.attach(self.entryTitle, 2, 3, 1, 2, xpadding=5, ypadding=0)
		'''table.attach(self.checkTitle, 3, 4, 1, 2, xpadding=10, ypadding=0)'''

		# Artista
		hboxArtist = gtk.HBox()
		hboxArtist.show()

		labelArtist = gtk.Label("""<span size='medium'>Artist:</span>""")
		labelArtist.set_use_markup(True)
		labelArtist.set_justify(gtk.JUSTIFY_LEFT)
		labelArtist.set_line_wrap(True)
		hboxArtist.pack_start(labelArtist, expand=False)
		labelArtist.show()

		self.entryArtist = gtk.Entry()
		self.entryArtist.set_size_request(250, -1)
		self.entryArtist.show()

		self.checkArtist = gtk.CheckButton("All", True)
		self.checkArtist.connect("toggled", self.on_all)
		self.checkArtist.show()

		table.attach(hboxArtist, 1, 2, 2, 3, xpadding=10, ypadding=0)
		table.attach(self.entryArtist, 2, 3, 2, 3, xpadding=5, ypadding=0)
		table.attach(self.checkArtist, 3, 4, 2, 3, xpadding=10, ypadding=0)

		# Album
		hboxAlbum = gtk.HBox()
		hboxAlbum.show()

		labelAlbum = gtk.Label("""<span size='medium'>Album:</span>""")
		labelAlbum.set_use_markup(True)
		labelAlbum.set_justify(gtk.JUSTIFY_LEFT)
		labelAlbum.set_line_wrap(True)
		hboxAlbum.pack_start(labelAlbum, expand=False)
		labelAlbum.show()

		self.entryAlbum = gtk.Entry()
		self.entryAlbum.set_size_request(250, -1)
		self.entryAlbum.show()

		self.checkAlbum = gtk.CheckButton("All", True)
		self.checkAlbum.connect("toggled", self.on_all)
		self.checkAlbum.show()

		table.attach(hboxAlbum, 1, 2, 3, 4, xpadding=10, ypadding=0)
		table.attach(self.entryAlbum, 2, 3, 3, 4, xpadding=5, ypadding=0)
		table.attach(self.checkAlbum, 3, 4, 3, 4, xpadding=10, ypadding=0)

		# Tabella 2
		table2 = gtk.Table(2, 6)
		self.vboxMetadata.pack_start(table2, expand=False)
		table2.show()

		# Anno
		hboxYear = gtk.HBox()
		hboxYear.show()

		labelYear = gtk.Label("""<span size='medium'>Year:</span>""")
		labelYear.set_use_markup(True)
		labelYear.set_justify(gtk.JUSTIFY_LEFT)
		labelYear.set_line_wrap(True)
		hboxYear.pack_start(labelYear, expand=False)
		labelYear.show()

		self.entryYear = gtk.Entry()
		self.entryYear.set_size_request(80, -1)
		self.entryYear.set_max_length(4)
		self.entryYear.show()

		self.checkYear = gtk.CheckButton("All", True)
		self.checkYear.connect("toggled", self.on_all)
		self.checkYear.show()

		table2.attach(hboxYear, 1, 2, 1, 2, xpadding=10, ypadding=0)
		table2.attach(self.entryYear, 2, 3, 1, 2, xpadding=5, ypadding=0)
		table2.attach(self.checkYear, 3, 4, 1, 2, xpadding=10, ypadding=0)

		# Genere
		hboxGenre = gtk.HBox()
		hboxGenre.show()

		labelGenre = gtk.Label("""<span size='medium'>Genre:</span>""")
		labelGenre.set_use_markup(True)
		labelGenre.set_justify(gtk.JUSTIFY_LEFT)
		labelGenre.set_line_wrap(True)
		hboxGenre.pack_start(labelGenre, expand=False)
		labelGenre.show()

		self.entryGenre = gtk.Entry()
		self.entryGenre.set_size_request(80, -1)
		self.entryGenre.show()

		self.checkGenre = gtk.CheckButton("All", True)
		self.checkGenre.connect("toggled", self.on_all)
		self.checkGenre.show()

		table2.attach(hboxGenre, 1, 2, 2, 3, xpadding=10, ypadding=0)
		table2.attach(self.entryGenre, 2, 3, 2, 3, xpadding=5, ypadding=0)
		table2.attach(self.checkGenre, 3, 4, 2, 3, xpadding=10, ypadding=0)

		# Numero traccia
		hboxTrack = gtk.HBox()
		hboxTrack.show()

		labelTrack = gtk.Label("""<span size='medium'>Track:</span>""")
		labelTrack.set_use_markup(True)
		labelTrack.set_justify(gtk.JUSTIFY_LEFT)
		labelTrack.set_line_wrap(True)
		hboxTrack.pack_start(labelTrack, expand=False)
		labelTrack.show()

		self.entryTrack = gtk.Entry()
		self.entryTrack.set_size_request(55, -1)
		self.entryTrack.show()

		'''self.checkTrack = gtk.CheckButton("All", True)
		self.checkTrack.connect("toggled", self.on_all)
		self.checkTrack.show()'''

		table2.attach(hboxTrack, 4, 5, 1, 2, xpadding=10, ypadding=0)
		table2.attach(self.entryTrack, 5, 6, 1, 2, xpadding=5, ypadding=0)
		'''table2.attach(self.checkTrack, 6, 7, 1, 2, xpadding=10, ypadding=0)'''

		# Numero disco
		hboxDisc = gtk.HBox()
		hboxDisc.show()

		labelDisc = gtk.Label("""<span size='medium'>Disc:</span>""")
		labelDisc.set_use_markup(True)
		labelDisc.set_justify(gtk.JUSTIFY_LEFT)
		labelDisc.set_line_wrap(True)
		hboxDisc.pack_start(labelDisc, expand=False)
		labelDisc.show()

		self.entryDisc = gtk.Entry()
		self.entryDisc.set_size_request(80, -1)
		self.entryDisc.show()

		self.checkDisc = gtk.CheckButton("All", True)
		self.checkDisc.connect("toggled", self.on_all)
		self.checkDisc.show()

		table2.attach(hboxDisc, 4, 5, 2, 3,  xpadding=10, ypadding=0)
		table2.attach(self.entryDisc, 5, 6, 2, 3, xpadding=5, ypadding=0)
		table2.attach(self.checkDisc, 6, 7, 2, 3, xpadding=10, ypadding=0)

		# Commento
		hboxComment = gtk.HBox()
		hboxComment.show()

		labelComment = gtk.Label("""<span size='medium'>Comment:</span>""")
		labelComment.set_use_markup(True)
		labelComment.set_justify(gtk.JUSTIFY_LEFT)
		labelComment.set_line_wrap(True)
		hboxComment.pack_start(labelComment, expand=False)
		labelComment.show()

		self.entryComment = gtk.Entry()
		self.entryComment.set_size_request(250, -1)
		self.entryComment.show()

		self.checkComment = gtk.CheckButton("All", True)
		self.checkComment.connect("toggled", self.on_all)
		self.checkComment.show()

		table.attach(hboxComment, 1, 2, 8, 9, xpadding=10, ypadding=0)
		table.attach(self.entryComment, 2, 3, 8, 9, xpadding=5, ypadding=0)
		table.attach(self.checkComment, 3, 4, 8, 9, xpadding=10, ypadding=0)

		# Compositore
		hboxComposer = gtk.HBox()
		hboxComposer.show()

		labelComposer = gtk.Label("""<span size='medium'>Composer:</span>""")
		labelComposer.set_use_markup(True)
		labelComposer.set_justify(gtk.JUSTIFY_LEFT)
		labelComposer.set_line_wrap(True)
		hboxComposer.pack_start(labelComposer, expand=False)
		labelComposer.show()

		self.entryComposer = gtk.Entry()
		self.entryComposer.set_size_request(250, -1)
		self.entryComposer.show()

		self.checkComposer = gtk.CheckButton("All", True)
		self.checkComposer.connect("toggled", self.on_all)
		self.checkComposer.show()

		table.attach(hboxComposer, 1, 2, 9, 10, xpadding=10, ypadding=0)
		table.attach(self.entryComposer, 2, 3, 9, 10, xpadding=5, ypadding=0)
		table.attach(self.checkComposer, 3, 4, 9, 10, xpadding=10, ypadding=0)

		# Album_Artist
		hboxAlbum_Artist = gtk.HBox()
		hboxAlbum_Artist.show()

		labelAlbum_Artist = gtk.Label("""<span size='medium'>Album artist:</span>""")
		labelAlbum_Artist.set_use_markup(True)
		labelAlbum_Artist.set_justify(gtk.JUSTIFY_LEFT)
		labelAlbum_Artist.set_line_wrap(True)
		hboxAlbum_Artist.pack_start(labelAlbum_Artist, expand=False)
		labelAlbum_Artist.show()

		self.entryAlbum_Artist = gtk.Entry()
		self.entryAlbum_Artist.set_size_request(250, -1)
		self.entryAlbum_Artist.show()

		self.checkAlbum_Artist = gtk.CheckButton("All", True)
		self.checkAlbum_Artist.connect("toggled", self.on_all)
		self.checkAlbum_Artist.show()

		table.attach(hboxAlbum_Artist, 1, 2, 10, 11, xpadding=10, ypadding=0)
		table.attach(self.entryAlbum_Artist, 2, 3, 10, 11, xpadding=5, ypadding=0)
		table.attach(self.checkAlbum_Artist, 3, 4, 10, 11, xpadding=10, ypadding=0)

		# Tabella 3
		table3 = gtk.Table(1, 3)
		self.vboxMetadata.pack_start(table3, expand=False)
		table3.show()

		# Copertina
		vboxCover = gtk.VBox()
		vboxCover.show()

		hboxCover = gtk.HBox()
		vboxCover.pack_start(hboxCover, expand=False, padding=5)
		hboxCover.show()

		labelCover = gtk.Label("""<span size='medium'>Cover:</span>""")
		labelCover.set_use_markup(True)
		labelCover.set_justify(gtk.JUSTIFY_LEFT)
		labelCover.set_line_wrap(True)
		hboxCover.pack_start(labelCover, expand=False)
		labelCover.show()

		# Pulsante add cover
		cmdAddCover = gtk.Button(label="_Add", use_underline=True)
		cmdAddCover.connect("clicked", self.on_AddCover)
		vboxCover.pack_start(cmdAddCover, expand=False, padding=0)
		cmdAddCover.show()

		# Pulsante remove cover
		cmdRemoveCover = gtk.Button(label="_Remove", use_underline=True)
		cmdRemoveCover.connect("clicked", self.on_RemoveCover)
		vboxCover.pack_start(cmdRemoveCover, expand=False, padding=0)
		cmdRemoveCover.show()

		# Pulsante save cover
		cmdSaveCover = gtk.Button(label="_Save", use_underline=True)
		cmdSaveCover.connect("clicked", self.on_SaveCover)
		vboxCover.pack_start(cmdSaveCover, expand=False, padding=0)
		cmdSaveCover.show()

		self.hboxCover1 = gtk.HBox()
		self.hboxCover1.show()
		self.imgCovers = []

		self.checkCover = gtk.CheckButton("All", True)
		self.checkCover.connect("toggled", self.on_all)
		self.checkCover.show()

		table3.attach(vboxCover, 1, 2, 1, 2, xpadding=10, ypadding=5)
		table3.attach(self.hboxCover1, 2, 3, 1, 2, xpadding=5, ypadding=5)
		table3.attach(self.checkCover, 3, 4, 1, 2, xpadding=10, ypadding=0)

		# Pagina 1
		labelNotebookF2T = gtk.Label()
		labelNotebookF2T.set_use_markup(True)
		labelNotebookF2T.set_label("Load tags")
		labelNotebookF2T.show()

		# Cornice per caricare i tag dal nome del file
		self.frameFile = gtk.Frame()
		self.frameFile.set_shadow_type(gtk.SHADOW_NONE)
		self.frameFile.show()
		self.notebook.append_page(self.frameFile, labelNotebookF2T)

		# Label della cornice per caricare i tag dal nome del file
		labelFileTag = gtk.Label()
		labelFileTag.set_use_markup(True)
		labelFileTag.set_label("<b>Tags from filename</b>")
		labelFileTag.set_padding(0, 10)
		self.frameFile.set_label_widget(labelFileTag)
		labelFileTag.show()

		# VBox per la scelta del nome file
		vboxFileTag = gtk.VBox()
		self.frameFile.add(vboxFileTag)
		vboxFileTag.set_spacing(10)
		vboxFileTag.set_homogeneous(False)
		vboxFileTag.show()

		# ComboBox per il nome dei file
		hboxFileTag1 = gtk.HBox()
		hboxFileTag1.set_homogeneous(True)
		vboxFileTag.pack_start(hboxFileTag1, expand = False)
		hboxFileTag1.show()
		pref_pattern =  self.prefs.get_option("filename2tag-pattern")
		self.comboFileTag = gtk.combo_box_new_text()
		for fnp in FILENAME2TAG_PATTERN:
			if fnp[0] == pref_pattern:
				pattern_index = FILENAME2TAG_PATTERN.index(fnp)
			if fnp[1] == "":
				self.comboFileTag.append_text(fnp[0])
			else:
				self.comboFileTag.append_text(fnp[0] + " (" + fnp[1] + ")")
		try:
			self.comboFileTag.set_active(pattern_index) #setta il default
		except:
			self.comboFileTag.set_active(1)
		hboxFileTag1.pack_start(self.comboFileTag, padding=20, expand=False)
		self.comboFileTag.show()

		# Entry per il pattern con la sua label
		hboxFileTag2 = gtk.HBox()
		hboxFileTag2.set_homogeneous(False)
		vboxFileTag.pack_start(hboxFileTag2, expand = False)
		hboxFileTag2.show()
		self.labelPattern = gtk.Label("Pattern:")
		hboxFileTag2.pack_start(self.labelPattern, expand=False, padding=20)
		self.labelPattern.set_sensitive(False)
		self.labelPattern.show()
		self.entryFileTag = gtk.Entry()
		self.entryFileTag.set_size_request(30,-1)
		hboxFileTag2.pack_start(self.entryFileTag, expand=True)
		self.entryFileTag.set_sensitive(False)
		self.entryFileTag.show()

		# Attiva l'evento della combo e verifica l'index nelle preferenze
		self.comboFileTag.connect("changed", self.on_filename_pattern_changed)
		prefs_alt_pat = self.prefs.get_option("alternate-filename2tag-pattern")
		self.entryFileTag.set_text(re.sub('(?=\w)', '%', prefs_alt_pat))
		self.checkFileTag = gtk.CheckButton("All", True)
		self.checkFileTag.connect("toggled", self.on_all)
		hboxFileTag2.pack_start(self.checkFileTag, expand=False, padding=0)
		self.checkFileTag.show()

		self.cmdFileTag = gtk.Button(label="_Apply", use_underline=True)
		self.cmdFileTag.connect("clicked", self.on_FileToTag)
		hboxFileTag2.pack_start(self.cmdFileTag, expand=False, padding=20)
		self.cmdFileTag.show()

		hboxFileTag3 = gtk.HBox()
		hboxFileTag3.set_homogeneous(False)
		vboxFileTag.pack_start(hboxFileTag3, expand = False)
		hboxFileTag3.show()
		self.labelFilename = gtk.Label()
		self.labelFilename.set_use_markup(True)
		self.labelFilename.set_justify(gtk.JUSTIFY_LEFT)
		hboxFileTag3.pack_start(self.labelFilename, expand=False, padding=20)
		self.labelFilename.show()

		hboxFileTag4 = gtk.HBox()
		hboxFileTag4.set_homogeneous(False)
		vboxFileTag.pack_start(hboxFileTag4, expand = False)
		hboxFileTag4.show()
		self.labelNewTag2 = gtk.Label("<b>Result:</b>")
		self.labelNewTag2.set_use_markup(True)
		self.labelNewTag2.set_justify(gtk.JUSTIFY_LEFT)
		hboxFileTag4.pack_start(self.labelNewTag2, expand=False, padding=20)
		self.labelNewTag2.show()

		# Istruzioni e risultato
		hboxFileTagI = gtk.HBox()
		hboxFileTagI.set_homogeneous(False)
		vboxFileTag.pack_start(hboxFileTagI, expand=False)
		hboxFileTagI.show()

		self.labelInfoPattern = gtk.Label(INFO_PATTERN)
		self.labelInfoPattern.set_use_markup(True)
		hboxFileTagI.pack_start(self.labelInfoPattern, expand=False, padding=20)
		self.labelInfoPattern.show()

		self.labelTagsResults = gtk.Label()
		self.labelTagsResults.set_use_markup(True)
		hboxFileTagI.pack_start(self.labelTagsResults, expand=False, padding=20)
		self.labelTagsResults.show()

		self.on_filename_pattern_changed()
		self.entryFileTag.connect("changed", self.on_entry_pattern_changed)
		self.on_entry_pattern_changed()

		# Pagina 2
		labelNotebookT2F = gtk.Label()
		labelNotebookT2F.set_use_markup(True)
		labelNotebookT2F.set_label("Rename files")
		labelNotebookT2F.show()

		# Cornice per caricare i tag dal nome del file
		self.frameT2F = gtk.Frame()
		self.frameT2F.set_shadow_type(gtk.SHADOW_NONE)
		self.frameT2F.show()
		self.notebook.append_page(self.frameT2F, labelNotebookT2F)

		# Label della cornice per caricare i tag dal nome del file
		labelT2F = gtk.Label()
		labelT2F.set_use_markup(True)
		labelT2F.set_label("<b>Filename from tags</b>")
		labelT2F.set_padding(0, 10)
		self.frameT2F.set_label_widget(labelT2F)
		labelT2F.show()

		# VBox per la scelta del nome file
		vboxT2F = gtk.VBox()
		self.frameT2F.add(vboxT2F)
		vboxT2F.set_spacing(5)
		vboxT2F.set_homogeneous(False)
		vboxT2F.show()

		# ComboBox per il nome dei file
		hboxFileT2F1 = gtk.HBox()
		hboxFileT2F1.set_homogeneous(True)
		vboxT2F.pack_start(hboxFileT2F1, expand = False)
		hboxFileT2F1.show()
		pref_pattern2 =  self.prefs.get_option("filename2tag-pattern")
		self.comboT2F = gtk.combo_box_new_text()
		for fnp2 in FILENAME2TAG_PATTERN:
			if fnp2[0] == pref_pattern2:
				pattern_index = FILENAME2TAG_PATTERN.index(fnp2)
			if fnp2[1] == "":
				self.comboT2F.append_text(fnp2[0])
			else:
				self.comboT2F.append_text(fnp2[0] + " (" + fnp2[1] + ")")
		try:
			self.comboT2F.set_active(pattern_index) #setta il default
		except:
			self.comboT2F.set_active(1)
		hboxFileT2F1.pack_start(self.comboT2F, padding=20, expand=False)
		self.comboT2F.show()

		# Entry per il pattern con la sua label
		hboxFileT2F2 = gtk.HBox()
		hboxFileT2F2.set_homogeneous(False)
		vboxT2F.pack_start(hboxFileT2F2, expand = False)
		hboxFileT2F2.show()
		self.labelPattern2 = gtk.Label("Filename pattern:")
		hboxFileT2F2.pack_start(self.labelPattern2, expand=False, padding=20)
		self.labelPattern2.set_sensitive(False)
		self.labelPattern2.show()
		self.entryT2F = gtk.Entry()
		self.entryT2F.set_size_request(30,-1)
		hboxFileT2F2.pack_start(self.entryT2F, expand=True, padding=20)
		self.entryT2F.set_sensitive(False)
		self.entryT2F.show()

		# Attiva l'evento della combo e verifica l'index nelle preferenze
		self.comboT2F.connect("changed", self.on_filename_pattern_changed2)
		prefs_alt_pat2 = self.prefs.get_option("alternate-filename2tag-pattern")
		self.entryT2F.set_text(re.sub('(?=\w)', '%', prefs_alt_pat2))

		# Istruzioni
		hboxIst = gtk.HBox()
		hboxIst.set_homogeneous(False)
		vboxT2F.pack_start(hboxIst, expand = False)
		hboxIst.show()
		self.labelInfoPattern2 = gtk.Label(INFO_PATTERN)
		self.labelInfoPattern2.set_use_markup(True)
		hboxIst.pack_start(self.labelInfoPattern2, expand=False, padding=60)
		self.labelInfoPattern2.show()
		
		# Check button per gli underscore
		hboxFileUnder = gtk.HBox()
		hboxFileUnder.set_homogeneous(False)
		vboxT2F.pack_start(hboxFileUnder, expand = False)
		hboxFileUnder.show()
		self.checkUnder = gtk.CheckButton("Replaces spaces by underscores", True)
		hboxFileUnder.pack_start(self.checkUnder, expand=False, padding=40)
		self.checkUnder.connect("toggled", self.on_under)
		self.checkUnder.show()

		# Check button per l'estensione del file
		hboxFileExt = gtk.HBox()
		hboxFileExt.set_homogeneous(False)
		vboxT2F.pack_start(hboxFileExt, expand = False)
		hboxFileExt.show()
		self.checkExt = gtk.CheckButton("Change the file extension", True)
		hboxFileExt.pack_start(self.checkExt, expand=False, padding=40)
		self.checkExt.connect("toggled", self.on_ext)
		self.checkExt.show()
		self.entryExt = gtk.Entry()
		self.entryExt.set_size_request(50,-1)
		hboxFileExt.pack_start(self.entryExt, expand=False)
		self.entryExt.connect("changed", self.on_entry_ext_changed)
		self.entryExt.set_sensitive(False)
		self.entryExt.show()
		
		# Risultato
		hboxFileT2F3 = gtk.HBox()
		hboxFileT2F3.set_homogeneous(False)
		vboxT2F.pack_start(hboxFileT2F3, expand = False, padding=2)
		hboxFileT2F3.show()
		self.labelFilename2 = gtk.Label()
		self.labelFilename2.set_use_markup(True)
		self.labelFilename2.set_justify(gtk.JUSTIFY_LEFT)
		hboxFileT2F3.pack_start(self.labelFilename2, expand=False, padding=20)
		self.labelFilename2.show()

		# Check per inominare tutti i file
		hboxFileT2F4 = gtk.HBox()
		hboxFileT2F4.set_homogeneous(False)
		vboxT2F.pack_start(hboxFileT2F4, expand = False)
		hboxFileT2F4.show()

		self.checkT2F = gtk.CheckButton("All", True)
		#self.checkT2F.connect("toggled", self.on_all)
		hboxFileT2F4.pack_start(self.checkT2F, expand=False, padding=40)
		self.checkT2F.show()

		# Comando rinomina il/i file		
		self.cmdT2F = gtk.Button(label="_Rename", use_underline=True)
		self.cmdT2F.connect("clicked", self.on_TagToFile)
		hboxFileT2F4.pack_start(self.cmdT2F, expand=False, padding=10)
		self.cmdT2F.show()

		self.on_filename_pattern_changed2()
		self.entryT2F.connect("changed", self.on_entry_pattern_changed2)
		self.on_entry_pattern_changed2()

		# Base

		# VBox per la scelta dei tag
		vboxTag = gtk.VBox()
		self.dlg.vbox.pack_start(vboxTag, expand=False, padding=5)
		vboxTag.set_homogeneous(False)
		vboxTag.set_spacing(0)
		vboxTag.show()

		# Check button per salvare i tag dei file originali
		hboxOriginal = gtk.HBox()
		hboxOriginal.set_homogeneous(False)
		vboxTag.pack_start(hboxOriginal, expand=False, padding=5)
		hboxOriginal.show()
		self.checkOriginal = gtk.CheckButton("""Save tags of original files""", False)
		self.checkOriginal.connect("toggled", self.on_original)
		hboxOriginal.pack_start(self.checkOriginal, padding=20)
		self.checkOriginal.show()
		self.checkOriginal.set_active(False)
		self.checkOriginalAll = gtk.CheckButton("All", True)
		hboxOriginal.pack_start(self.checkOriginalAll, padding=10)
		self.checkOriginalAll.show()
		self.checkOriginalAll.set_active(False)

		# Check button per gli ID3v2
		hboxID3v2 = gtk.HBox()
		hboxID3v2.set_homogeneous(False)
		vboxTag.pack_start(hboxID3v2, expand=False)
		hboxID3v2.show()
		self.checkID3v2 = gtk.CheckButton("Additional write ID3v2.4 tags in MP3 files", True)
		hboxID3v2.pack_start(self.checkID3v2, padding=20)
		self.checkID3v2.show()

		# Rimuovi i tag dai file originali
		hboxRemove = gtk.HBox()
		hboxRemove.set_homogeneous(False)
		vboxTag.pack_start(hboxRemove, expand=False, padding=5)
		hboxRemove.show()
		self.checkRemove = gtk.CheckButton("Remove tags of original files", False)
		self.checkRemove.connect("toggled", self.on_remove)
		hboxRemove.pack_start(self.checkRemove, padding=20)
		self.checkRemove.show()
		self.checkRemove.set_active(False)
		self.checkRemoveAll = gtk.CheckButton("All", True)
		hboxRemove.pack_start(self.checkRemoveAll, padding=10)
		self.checkRemoveAll.show()
		self.checkRemoveAll.set_active(False)

		# Pulsanti precedente/prossimo
		buttonPrev = gtk.Button(stock=gtk.STOCK_MEDIA_PREVIOUS)
		buttonPrev.connect("clicked", self.on_Previous)
		self.dlg.action_area.pack_start(buttonPrev, expand=False, padding=0)
		buttonPrev.show()

		buttonNext = gtk.Button(stock=gtk.STOCK_MEDIA_NEXT)
		buttonNext.connect("clicked", self.on_Next)
		self.dlg.action_area.pack_start(buttonNext, expand=False, padding=0)
		buttonNext.show()

		# Pulsante Calcel
		self.cmdCancel = gtk.Button(label="_Cancel", use_underline=True)
		self.cmdCancel.connect("clicked", self.on_Cancel)
		self.dlg.add_action_widget(self.cmdCancel, 1)
		self.cmdCancel.show()

		# Pulsante OK
		self.cmdOK = gtk.Button(label="_Ok", use_underline=True)
		self.cmdOK.connect("clicked", self.on_Ok)
		self.dlg.add_action_widget(self.cmdOK, 2)
		self.cmdOK.show()
		self.dlg.set_focus(self.cmdOK)

		self.on_original()
		self.on_remove()
		self.load_tags(self.sel)

	# Carica i tag del brano selezionato
	def load_tags(self, sel):

		af = sel[0]
		it = sel[1]
		self.entryTitle.set_text(af.get_tag("title"))
		self.entryArtist.set_text(af.get_tag("artist"))
		self.entryAlbum.set_text(af.get_tag("album"))
		self.entryYear.set_text(str(af.get_tag("year")))
		self.entryGenre.set_text(af.get_tag("genre"))
		self.entryTrack.set_text(str(af.get_tag("track_number")))
		self.entryDisc.set_text(str(af.get_tag("disc_number")))
		self.entryComment.set_text(af.get_tag("comment"))
		self.entryComposer.set_text(af.get_tag("composer"))
		self.entryAlbum_Artist.set_text(af.get_tag("album_artist"))
		self.labelFilename.set_label("""<b>Filename:    </b>""" + af.get_filename())

		self.on_entry_pattern_changed()
		self.on_entry_pattern_changed2()

		# Copertina (se esiste nel file e se è installato il modulo PIL)
		if af.get_tag("cover") and IMAGE:
			covers = []
			if isinstance(af.get_tag("cover"), list):
				for cov in af.get_tag("cover"):
					covers.append(cov)
			else:
				covers.append(af.get_tag("cover"))
			covers_file = []
			for i in range(len(covers)):
				covers_file.append(open(XACHOME + "/cover" + str(i) + ".jpg", "w"))
				covers_file[i].write(covers[i])
				covers_file[i].close()
				img = Image.open(XACHOME + "/cover" + str(i) + ".jpg")
				new_size = 110, 110
				img.resize(new_size, Image.ANTIALIAS).save(XACHOME + "/cover_resized" + str(i) + ".jpg")
				imgres = Image.open(XACHOME + "/cover_resized" + str(i) + ".jpg")
				self.imgCovers.append(gtk.Image())
				self.imgCovers[i].set_from_file(imgres.filename)
				self.hboxCover1.pack_start(self.imgCovers[i], expand=True, padding=5)
				self.imgCovers[i].show()
				try:
					os.remove(XACHOME + "/cover" + str(i) + ".jpg")
					os.remove(XACHOME + "/cover_resized" + str(i) + ".jpg")
				except: pass
		else:
			self.imgCovers.append(gtk.Image())
			self.imgCovers[0].set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_DIALOG)
			self.hboxCover1.pack_start(self.imgCovers[0], expand=True, padding=5)
			self.imgCovers[0].show()

	# Aggiorna i tag sulla base del contenuto degli entry
	def update_tags(self, sel):

		af = sel[0]
		it = sel[1]
		af.set_tag("title", self.entryTitle.get_text())
		af.set_tag("artist", self.entryArtist.get_text())
		af.set_tag("album", self.entryAlbum.get_text())
		af.set_tag("year", self.entryYear.get_text())
		af.set_tag("genre", self.entryGenre.get_text())
		af.set_tag("track_number", self.entryTrack.get_text())
		af.set_tag("disc_number", self.entryDisc.get_text())
		af.set_tag("comment", self.entryComment.get_text())
		af.set_tag("composer", self.entryComposer.get_text())
		af.set_tag("album_artist", self.entryAlbum_Artist.get_text())
		'''if len(self.imgCovers) > 0:
			for i in range(len(self.imgCovers)):
				#if not self.imgCovers[i].get_stock()[0]:
				cover = self.imgCovers[i].get_pixbuf().save(XACHOME + "/saved_cover" + str(i) + ".jpg", "jpeg", {"quality":"100"})'''

	# Carica i tag del brano precedente
	def on_Previous(self, *args):

		self.update_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

		model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()
		if len(pathlist) > 0:
			rowpath = pathlist[0]
			self.mainapp.FileTable.tvSelection.unselect_all()
			prev_pointer = 0
			prev_it = None
			curr_it = self.mainapp.FileTable.listStore.get_iter(rowpath)
			for af in self.mainapp.audioFileList.filelist:
				if str(af.pointer) == model.get_string_from_iter(curr_it):
					prev_pointer = af.pointer - 1
			if prev_pointer > -1:
				self.mainapp.FileTable.tvSelection.select_all()
				model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()

				if pathlist:
					iterlist = []
					for rowpath in pathlist:
						try:
							iterlist.append(model.get_iter(rowpath))
						except ValueError:
							pass
					for it in iterlist:
						if str(prev_pointer) == model.get_string_from_iter(it):
							prev_it = it
					if prev_it:
						self.mainapp.FileTable.tvSelection.unselect_all()
						self.mainapp.FileTable.tvSelection.select_iter(prev_it)
					else:
						self.mainapp.FileTable.tvSelection.unselect_all()
						self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())
			else:
				self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())
		else:
			self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())

		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Carica i tag del brano successivo
	def on_Next(self, *args):

		self.update_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

		model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()
		rowpath = pathlist[0]
		self.mainapp.FileTable.tvSelection.unselect_all()
		it = self.mainapp.FileTable.listStore.get_iter(rowpath)
		root_it = self.mainapp.FileTable.listStore.get_iter_root()
		next_it = self.mainapp.FileTable.listStore.iter_next(it)
		if next_it:
			self.mainapp.FileTable.tvSelection.select_iter(next_it)
		else:
			try:
				self.mainapp.FileTable.tvSelection.select_iter(root_it)
			except:
				pass
		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	def on_original(self, *args):

		if self.checkOriginal.get_active():
			self.checkID3v2.set_sensitive(True)
			self.checkID3v2.set_active(True)
			self.checkOriginalAll.set_sensitive(True)
		if not self.checkOriginal.get_active():
			self.checkID3v2.set_sensitive(False)
			self.checkID3v2.set_active(False)
			self.checkOriginalAll.set_sensitive(False)
			self.checkOriginalAll.set_active(False)

	def on_remove(self, *args):

		if not self.checkRemove.get_active():
			self.checkOriginal.set_sensitive(True)
			#self.checkOriginal.set_active(True)
			self.checkRemoveAll.set_sensitive(False)
			self.checkRemoveAll.set_active(False)
		if self.checkRemove.get_active():
			self.checkOriginal.set_sensitive(False)
			self.checkOriginal.set_active(False)
			self.checkRemoveAll.set_sensitive(True)

	# Cambia il tag in tutti i file
	def on_all(self, *args):

		if self.checkArtist.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("artist", self.entryArtist.get_text())
		if self.checkAlbum.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("album", self.entryAlbum.get_text())
		if self.checkYear.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("year", self.entryYear.get_text())
		if self.checkGenre.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("genre", self.entryGenre.get_text())
		if self.checkDisc.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("disc_number", self.entryDisc.get_text())
		if self.checkComment.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("comment", self.entryComment.get_text())
		if self.checkComposer.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("composer", self.entryComposer.get_text())
		if self.checkAlbum_Artist.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("album_artist", self.entryAlbum_Artist.get_text())
		if self.checkCover.get_active():
			for af in self.mainapp.audioFileList.filelist:
				af.set_tag("cover", self.mainapp.Selection(self.mainapp.FileTable)[0][0].get_tag("cover"))

		self.update_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Carica una nuova copertina
	def on_AddCover(self, *args):

		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]

		choiseImage = gtk.FileChooserDialog("Select image...", self.dlg,
				gtk.FILE_CHOOSER_ACTION_OPEN,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		choiseImage.set_select_multiple(False)
		choiseImage.set_local_only(False)
		choiseImage.set_current_folder(self.mainapp.prefs.get_option("last-used-folder"))

		# Crea un filtro per le immagini
		filter0 = gtk.FileFilter()
		filter0.set_name("Images")
		for n, p in COVER_PATTERN:
			filter0.add_pattern(p)
		choiseImage.add_filter(filter0)

		# Crea un filtro per tutti i file
		filter1 = gtk.FileFilter()
		filter1.set_name("All files (*.*)")
		filter1.add_pattern("*")
		choiseImage.add_filter(filter1)

		# Crea un filtro per ogni tipo di file immagine
		for n, p in COVER_PATTERN:
			filter2 = gtk.FileFilter()
			filter2.set_name(n)
			filter2.add_pattern(p)
			choiseImage.add_filter(filter2)

		response = choiseImage.run()

		if response == gtk.RESPONSE_OK:
			for child in self.hboxCover1.get_children():
				self.hboxCover1.remove(child)
			new_cover_filename = choiseImage.get_filename()
			print new_cover_filename
			img = Image.open(new_cover_filename)
			if os.path.getsize(img.filename) > 128*1024:
				new_size = 600, 600
				k = 1.0
				while 1:
					new_size = int(new_size[0]*k), int(new_size[1]*k)
					print "NEW SIZE: ", new_size
					img_resized = Image.open(img.filename)
					#img_resized.resize(new_size, Image.ANTIALIAS).save(XACHOME + "/cover_resized.jpg")
					img_resized.resize(new_size, Image.ANTIALIAS).save(XACHOME + "/" + str(new_size[0]) + "cover_resized.jpg")
					img_resized = Image.open(XACHOME + "/" + str(new_size[0]) + "cover_resized.jpg")
					k = k / 1.5
					print img_resized.filename
					print os.path.getsize(img_resized.filename)
					if os.path.getsize(img_resized.filename) < 128*1024:
						break
				img = img_resized
			new_cover_file = open(img.filename, "r")
			af.set_tag("cover", new_cover_file.read())

			self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

		else:
			pass

		choiseImage.destroy()

	# Rimuove la copertina
	def on_RemoveCover(self, *args):

		for child in self.hboxCover1.get_children():
			self.hboxCover1.remove(child)
		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
		af.set_tag("cover", None)
		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Salva la copertina
	def on_SaveCover(self, *args):

		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]

		if af.get_tag("cover"):
			covers = []
			if isinstance(af.get_tag("cover"), list):
				for cov in af.get_tag("cover"):
					covers.append(cov)
			else:
				covers.append(af.get_tag("cover"))
			covers_file = []

			saveImage = gtk.FileChooserDialog("Save image...", self.dlg,
					gtk.FILE_CHOOSER_ACTION_SAVE,
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_SAVE, gtk.RESPONSE_OK))
			saveImage.set_select_multiple(False)
			saveImage.set_local_only(False)
			saveImage.set_current_folder(self.mainapp.prefs.get_option("last-used-folder"))
			saveImage.set_current_name(af.get_tag("artist") + " - " + af.get_tag("album") + " cover")
			# Crea un filtro per tutti i file
			filter0 = gtk.FileFilter()
			filter0.set_name("JPEG (*.jpg)")
			filter0.add_pattern("*.jpg")
			saveImage.add_filter(filter0)

			response = saveImage.run()

			if response == gtk.RESPONSE_OK:
				for i in range(len(covers)):
					if i == 0:
						covers_file.append(open(saveImage.get_filename() + ".jpg", "w"))
					else:
						covers_file.append(open(saveImage.get_filename() + " " + str(i) + ".jpg", "w"))
					covers_file[i].write(covers[i])
					covers_file[i].close()
			saveImage.destroy()

	# Alla modifica del pattern per caricare i tag
	def on_entry_pattern_changed(self, *args):

		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
		try:
			disc_number, track_number, title, artist, album, year = self.File2Tag(af.get_filename(), self.entryFileTag.get_text())
		except: pass
		self.labelTagsResults.set_label(track_number + "\n" + \
						title + "\n" + \
						artist + "\n" + \
						album + "\n" + \
						year + "\n" + \
						disc_number)

	# Al cambiare del combobox per caricare i tag dal nome del file
	def on_filename_pattern_changed(self, *args):
		if self.comboFileTag.get_active() == 0:
			self.entryFileTag.set_sensitive(True)
			self.entryFileTag.set_text(FILENAME2TAG_PATTERN[1][1])
			self.labelPattern.set_sensitive(True)
		else:
			self.entryFileTag.set_sensitive(True)
			self.labelPattern.set_sensitive(False)
			self.entryFileTag.set_text(FILENAME2TAG_PATTERN[self.comboFileTag.get_active()][1])
			self.entryFileTag.set_sensitive(False)

	# Restituisce i tag in base al nome file a la pattern
	def File2Tag(self, filename, pattern):

		path, filename = os.path.split(filename)
		path, pattern = os.path.split(pattern)

		regex = re.compile('([-.\[\]()])')

		fsplit = regex.split(filename[:-4])
		flist = []
		for w in fsplit:
			flist.append(w.rstrip(" ").lstrip(" "))

		psplit = regex.split(pattern)
		plist = []
		for w in psplit:
			plist.append(w.rstrip(" ").lstrip(" "))
		print flist
		print plist
		f = []
		p = []
		try:
			for member in plist:
				if member.count("%") == 1:
					f.append(flist[plist.index(member)])
					p.append(member)
				else:
					tf = re.split(" ", flist[plist.index(member)], 1)
					tp = re.split(" ", member)
					for k in tp:
						f.append(tf[tp.index(k)])
						p.append(k)
		except: pass

		disc_number = track_number = title = artist = album = year = ""
		for pat in p:
			if pat == "%s":
				disc_number = f[p.index(pat)]
			elif pat == "%n":
				track_number = f[p.index(pat)]
			elif pat == "%t":
				title = f[p.index(pat)]
			elif pat == "%a":
				artist = f[p.index(pat)]
			elif pat == "%d":
				album = f[p.index(pat)]
			elif pat == "%y":
				year = f[p.index(pat)]
			else:
				dummy = f[p.index(pat)]

		return disc_number, track_number, title, artist, album, year

	# Carica i tag dal nome del file (multipli se checkFileTag è selezionato)
	def on_FileToTag(self, *args):

		if self.checkFileTag.get_active():
			for af in self.mainapp.audioFileList.filelist:
				disc_number, track_number, title, artist, album, year = self.File2Tag(af.get_filename(), self.entryFileTag.get_text())
				if len(disc_number) > 0:
					af.set_tag("disc_number", '%(#)02d' %{"#": int(disc_number)})
				if len(track_number) > 0:
					af.set_tag("track_number", '%(#)02d' %{"#": int(track_number)})
				af.set_tag("title", title)
				af.set_tag("artist", artist)
				af.set_tag("album", album)
				af.set_tag("year", year)
		else:
			af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
			disc_number, track_number, title, artist, album, year = self.File2Tag(af.get_filename(), self.entryFileTag.get_text())
			if len(disc_number) > 0:
				af.set_tag("disc_number", '%(#)02d' %{"#": int(disc_number)})
			if len(track_number) > 0:
				af.set_tag("track_number", '%(#)02d' %{"#": int(track_number)})
			af.set_tag("title", title)
			af.set_tag("artist", artist)
			af.set_tag("album", album)
			af.set_tag("year", year)

		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Al cambiare del combobox per rinominare i file
	def on_filename_pattern_changed2(self, *args):
		if self.comboT2F.get_active() == 0:
			self.entryT2F.set_sensitive(True)
			self.entryT2F.set_text(FILENAME2TAG_PATTERN[1][1])
			self.labelPattern2.set_sensitive(True)
		else:
			self.entryT2F.set_sensitive(True)
			self.labelPattern2.set_sensitive(False)
			self.entryT2F.set_text(FILENAME2TAG_PATTERN[self.comboT2F.get_active()][1])
			self.entryT2F.set_sensitive(False)

	# Aggionra il rislutato del file da rinominare in base al pattern inserito
	def on_entry_pattern_changed2(self, *args):

		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
		filename = self.Tag2File(af, self.entryT2F.get_text())
		if not filename or filename == "":
			return
		self.entryExt.set_text(os.path.splitext(af.get_filepath())[1])
		if self.checkExt.get_active():
			self.labelFilename2.set_label("""<b>New filename:    </b>""" + filename + self.entryExt.get_text())
		else:
			self.labelFilename2.set_label("""<b>New filename:    </b>""" + filename + os.path.splitext(af.get_filepath())[1])

	# Cambia l'estensione del nuovo file in base all'entry
	def on_entry_ext_changed(self, *args):

		af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
		filename = self.Tag2File(af, self.entryT2F.get_text())
		self.labelFilename2.set_label("""<b>New filename:    </b>""" + filename + self.entryExt.get_text())		


	# Costruisce il nome file dai tags
	def Tag2File(self, af, pattern):

		if not self.file_exists(af):
			return False
		filename = expand_title(pattern, af.get_tag("artist"), af.get_tag("album"), af.get_tag("year"), af.get_tag("track_number"), af.get_tag("title"), af.get_tag("disc_number"))

		# Sostituisce gli spazi con gli underscore se richiesto
		if self.checkUnder.get_active():
			filename = re.compile(" ").sub("_",filename)

		return filename

	# Attiva l'etry per la nuova estensione
	def on_ext(self, *args):

		if self.checkExt.get_active():
			self.entryExt.set_sensitive(True)
		else:
			self.entryExt.set_sensitive(False)
		self.on_entry_pattern_changed2()

	# Alla modifica del check per gli underscore aggiorna la label
	def on_under(self, *args):
		self.on_entry_pattern_changed2()

	# Rinomina il file in base ai tags
	def on_TagToFile(self, *args):

		# Rinomina il file e restituisce un nuovo AudioFile
		def rename(af):
			new_filename = self.Tag2File(af, self.entryT2F.get_text())
			if not new_filename or new_filename == "":
				return None
			if self.file_exists(af):
				if self.checkExt.get_active():
					new_filepath = af.get_foldername() + "/" + new_filename + self.entryExt.get_text()
				else:
					new_filepath = af.get_foldername() + "/" + new_filename + os.path.splitext(af.get_filepath())[1]
				os.rename(af.get_filepath(), new_filepath)
				while 1:
					if os.path.exists(new_filepath):
						break
					else:
						time.sleep(0.01)
				return AudioFile("file://" + new_filepath)

		# Tutti i file
		new_listfile = []
		if self.checkT2F.get_active():
			for af in self.mainapp.audioFileList.filelist:
				new_af = rename(af)
				if isinstance(new_af, AudioFile):
					self.mainapp.audioFileList.remove(af.get_uri())
					self.mainapp.audioFileList.append(new_af)
		else:
			af = self.mainapp.Selection(self.mainapp.FileTable)[0][0]
			new_af = rename(af)
			if isinstance(new_af, AudioFile):
				self.mainapp.audioFileList.remove(af.get_uri())
				self.mainapp.audioFileList.append(new_af)

		# Ricarica i file audio cambiati
		if len(self.mainapp.audioFileList.filelist) > 0:
			self.mainapp.FileTable.purge()
			self.mainapp.FileTable.append(self.mainapp.audioFileList)
			self.dlg.destroy()

	# Funzione che verifica se il file audio esiste.
	# In caso contrario manda un messaggio e esce
	def file_exists(self, af):

		if os.path.exists(af.get_filepath()):
			return True
		elif af.get_uri()[:7] == "cdda://":
			return True
		else:
			dlg = WarningDialog(self.main_window , NAME + " - Warning", "The file " + af.get_filepath()  + " does not exist in the specified path. Perhaps it was deleted.")
			return False


	# Attiva e visualizza la finestra di dialogo
	def show(self, *args):
		self.response = None
		self.dlg.run()
		self.dlg.destroy()

	# Chiude e salva
	def on_Ok(self, *args):

		self.update_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

		if self.checkOriginal.get_active():
			self.save_tags = True
		else:
			self.save_tags = False

		if self.checkOriginalAll.get_active:
			self.save_tags_all = True
		else:
			self.save_tags_all = False

		if self.checkRemove.get_active():
			self.remove_tags = True
		else:
			self.remove_tags = False

		if self.checkRemoveAll.get_active():
			self.remove_tags_all = True
		else:
			self.remove_tags_all = False

		if self.checkID3v2.get_active():
			self.id3v2 = True
		else:
			self.id3v2 = False

		self.response = gtk.RESPONSE_OK
		self.dlg.destroy()

	def on_Cancel(self, *args):

		self.dlg.destroy()
