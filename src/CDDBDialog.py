#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# X Audio Copy - GTK and GNOME application for ripping CD-Audio and encoding in lossy audio format.
# Copyright 2010 - 2013 Giorgio Franceschi
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


import os
import sys
import re
import subprocess
import time, datetime

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


### Finestra di dialogo per la selezione dei CD da freeDB ###
class CDDBDialog:

	# Costruttore della classe
	def __init__(self, main_window, CDDBdisc):

		self.main_window = main_window
		# Inizilizza la variabile
		self.selected_cd = None

		# Finestra di dialogo
		#self.dlgCDDBSelection = gtk.Dialog("Select CD...", main_window,
		#             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		#            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.dlg = gtk.Dialog("Select CD from freeDB...", self.main_window,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.dlg.set_default_size(410, 60)
		self.dlg.set_border_width(5)


		# Box della finestra
		self.vbox = self.dlg.vbox
		self.vbox.set_spacing(2)
		self.vbox.set_homogeneous(False)

		scroll = gtk.ScrolledWindow()
		self.vbox.add(scroll)
		scroll.show()

		# Etichetta (posizione 1 nella VBox)
		self.labelCDDB = gtk.Label("Several exact matches found. Plese select your CD")
		self.labelCDDB.set_alignment(0, 0.5)
		self.labelCDDB.set_padding(10, 10)
		self.dlg.vbox.add(self.labelCDDB)
		self.labelCDDB.show()

		# TreeView (posizione 2 nella VBox)
		self.tvSelectCD = gtk.TreeView()
		self.tvSelectCD.connect("row-activated", self.on_CD_selected)
		scroll.add(self.tvSelectCD)
		self.tvSelectCD.show()

		# Pulsante OK
		self.cmdOKCDDB = gtk.Button(label="_Ok", use_underline=True)
		self.cmdOKCDDB.connect("clicked", self.on_CD_selected)
		self.dlg.add_action_widget(self.cmdOKCDDB, 1)
		self.cmdOKCDDB.show()

		# Pulsante Reject
		self.cmdReject = gtk.Button(label="_Reject", use_underline=True)
		self.cmdReject.connect("clicked", self.on_Reject)
		self.dlg.add_action_widget(self.cmdReject, 1)
		self.cmdReject.show()

		# Pulsante Calcel
		self.cmdCancel = gtk.Button(label="_Cancel", use_underline=True)
		self.cmdCancel.connect("clicked", self.on_Cancel)
		self.dlg.add_action_widget(self.cmdCancel, 1)
		self.cmdCancel.show()

		# Colonne del TreeView
		cell = gtk.CellRendererText()
		column0 = gtk.TreeViewColumn("Disc ID", cell, text=0)
		column1 = gtk.TreeViewColumn("Category", cell, text=1)
		column2 = gtk.TreeViewColumn("Artist / Title", cell, text=2)
		self.tvSelectCD.append_column(column0)
		self.tvSelectCD.append_column(column1)
		self.tvSelectCD.append_column(column2)

		# Selezione
		self.selectCD = self.tvSelectCD.get_selection()

		# Crea il modello ListStore con il contenuto della tabella
		self.cdList = gtk.ListStore(str, str, str)
		# Lo collega al TreeView
		self.tvSelectCD.set_model(self.cdList)

		for cd in CDDBdisc:
			# Popola di dati le righe
			self.cdList.append(cd)

		# Attiva e visualizza la finestra di dialogo
		self.dlg.run()

	def on_CD_selected(self, *args):

		model, row_iter = self.selectCD.get_selected()
		print "model: ", model
		print "row: ", row_iter
		if not row_iter:
			row_iter = self.cdList.get_iter_root()
		self.selected_cd = self.cdList.get_string_from_iter(row_iter)
		print self.selected_cd

		self.dlg.destroy()

	def on_Reject(self, *args):
		self.selected_cd = "reject"
		self.dlg.destroy()

	def on_Cancel(self, *args):

		self.dlg.destroy()
