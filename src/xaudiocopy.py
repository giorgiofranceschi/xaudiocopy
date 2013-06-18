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
try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	print("Gstreamer not available")
try:
	import CDDB, DiscID
except:
	print("CDDB not available")

from AudioFile import *
from FileList import *
from Player import *
from CDDBReader import *
from Encoder import *
from Preferences import *
from AboutDialog import *
from WarningDialog import *
from RipDialog import *
from PreferencesDialog import *
from ConverterDialog import *
from Converter import *
from TaggerDialog import *
from PlaylistDialog import *
from PropertyDialog import *
from CDDBDialog import *
from MBDialog import *
from CDSelection import *

# Setta l'icona del programma per tutte le finestre
gtk.window_set_default_icon_from_file(ICON)


### Classe della finestra principale ###
class classXAudioCopy:

	# Costruttore della classe classXAudioCopy
	def __init__(self):
		# Collega il file XML
		self.builderXAC = gtk.Builder()
		self.builderXAC.add_from_file(GLADE)
		# Collega i segnali
		self.builderXAC.connect_signals(self)

		# Carica la finestra principale "mainWindow"
		self.mainWindow = self.builderXAC.get_object("mainWindow")
		self.mainWindow.set_title(WINDOW_TITLE)
		self.mainWindow.connect("destroy", lambda on_quit: gtk.main_quit())
		gtk.window_set_default_icon_from_file

		# Carica la statusbar
		self.status = self.builderXAC.get_object("statusbar")

		# Collega il menu contestuale
		self.popupmenu = self.builderXAC.get_object("popupmenu")

		# Carica la tabella per la lista dei file (TreeView)
		self.FileTable = FileTable(self.builderXAC)

		# Visualizza la finestra principale mainWindow
		self.mainWindow.show()
		self.set_status()

		# Toglie il focus al pulsante cmdOpenFile (TODO: scoprire perché ce l'ha)
		self.mainWindow.set_focus(None)

		# Carica la barra con i tag e la nasconde all'avvio
		self.TagBar = TagBar(self.builderXAC)
		self.TagBar.hide()

		# Aggancia alcuni pulsanti e menu (per renderli sensibili o insensibili)
		self.cmdCD = self.builderXAC.get_object("cmdCD")
		self.menuCD = self.builderXAC.get_object("menuCD")

		self.cmdOpenFile = self.builderXAC.get_object("cmdOpenFile")
		self.menuOpenFile = self.builderXAC.get_object("menuOpenFile")

		self.cmdOpenFolder = self.builderXAC.get_object("cmdOpenFolder")
		self.menuOpenFolder = self.builderXAC.get_object("menuOpenFolder")

		self.cmdPlay = self.builderXAC.get_object("cmdPlay")
		self.menuPlay = self.builderXAC.get_object("menuPlay")
		self.menuPause = self.builderXAC.get_object("menuPause")
		self.popPlay = self.builderXAC.get_object("popPlay")
		self.popPause = self.builderXAC.get_object("popPause")

		self.cmdStop = self.builderXAC.get_object("cmdStop")
		self.menuStop = self.builderXAC.get_object("menuStop")
		self.popStop = self.builderXAC.get_object("popStop")

		self.cmdNext = self.builderXAC.get_object("cmdNext")
		self.menuNext = self.builderXAC.get_object("menuNext")

		self.cmdPrev = self.builderXAC.get_object("cmdPrev")
		self.menuPrev = self.builderXAC.get_object("menuPrev")

		self.cmdRewind = self.builderXAC.get_object("cmdRewind")
		self.cmdForward = self.builderXAC.get_object("cmdForward")

		self.labelTime = self.builderXAC.get_object("labelTime")
		self.scaleTime = self.builderXAC.get_object("scaleTime")

		self.volumebutton = self.builderXAC.get_object("volumebutton")
		self.volumebutton.set_value(0.5)

		self.cmdRemove = self.builderXAC.get_object("cmdRemove")
		self.menuRemove = self.builderXAC.get_object("menuRemove")

		self.cmdPurge = self.builderXAC.get_object("cmdPurge")
		self.menuPurge = self.builderXAC.get_object("menuPurge")

		self.menuSelectAll = self.builderXAC.get_object("menuSelectAll")
		self.menuUnselectAll = self.builderXAC.get_object("menuUnselectAll")

		self.cmdRip = self.builderXAC.get_object("cmdRip")
		self.menuRip = self.builderXAC.get_object("menuRip")

		self.cmdConvert = self.builderXAC.get_object("cmdConvert")
		self.menuConvert = self.builderXAC.get_object("menuConvert")

		self.menuProperty = self.builderXAC.get_object("menuProperty")
		self.menuModify = self.builderXAC.get_object("menuModify")
		self.menuPlaylist = self.builderXAC.get_object("menuPlaylist")
		self.popProperty = self.builderXAC.get_object("popProperty")
		self.popTagger = self.builderXAC.get_object("popTagger")

		# Rende insensibili alcuni menu e pulsanti all'avvio
		self.set_sensitive(False)
		self.cmdRip.set_sensitive(False)
		self.cmdConvert.set_sensitive(False)

		# Carica la progressbar per la conversione e la nasconde all'avvio
		self.progConvert = self.builderXAC.get_object("progressbar")
		self.progConvert.hide()

		# Crea l'oggetto lista dei file
		self.audioFileList = FileList()

		# Istanza del player audio
		self.player = Player(None, self)
		self.player.set_volume(self.volumebutton.get_value())
		self.player_bus = self.player.bus
		self.player_bus.connect("message", self.on_endPlay)

		# Carica le preferenze
		self.prefs = Preferences()

	# Funzione che attiva la finestra principale
	def main(self):
		gtk.main()

	# Funzione che modifica la barra di stato
	def set_status(self, text=None):

		self.status.show()
		con_id = self.status.get_context_id("SB")
		if not text:
			text = "Ready"
			self.mainWindow.set_title(WINDOW_TITLE)
		self.status.push(con_id, text)
		#print text
		while gtk.events_pending():
			gtk.main_iteration(False)

	# Funzione che rende sensibili/insensibili alcuni menu e pulsanti
	def set_sensitive(self, sensitive):

		cmd = [
			self.cmdPlay,
			self.menuPlay,
			self.popPlay,
			self.menuPause,
			self.popPause,
			self.cmdNext,
			self.menuNext,
			self.cmdPrev,
			self.menuPrev,
			self.cmdRemove,
			self.menuRemove,
			self.cmdPurge,
			self.menuPurge,
			self.cmdRewind,
			self.cmdForward,
			self.cmdConvert,
			self.menuConvert,
			self.menuSelectAll,
			self.menuUnselectAll,
			self.menuProperty,
			self.menuModify,
			self.popProperty,
			self.popTagger,
			self.menuPlaylist,
			self.TagBar
			]
		if sensitive:
			for c in cmd:
				c.set_sensitive(True)
		elif not sensitive:
			for c in cmd:
				c.set_sensitive(False)
			self.menuRip.set_sensitive(False)
			self.cmdRip.set_sensitive(False)
			self.cmdStop.set_sensitive(False)
			self.menuStop.set_sensitive(False)
			self.popStop.set_sensitive(False)
			self.scaleTime.set_sensitive(False)

	# Evento per l'uscita dal programma
	def on_Quit(self, *args):
		print "Bye..."
		gtk.main_quit()

	# Evento per l"apertura di un file
	def on_OpenFile(self, *args):
		self.set_status("Adding files...")
		# Oggetto di classe FileChooser (False se apre un file)
		FC = FileChooser(False)
		self.AddFileList(FC)
		try:
			self.player.stop()
		except:
			pass
		self.cmdPlay.set_stock_id("gtk-media-play")

	# Evento per l"apertura di una cartella
	def on_OpenFolder(self, *args):
		self.set_status("Adding forder...")
		# Oggetto di classe FileChooser (True se apre una cartella)
		FC = FileChooser(True)
		self.AddFileList(FC)
		try:
			self.player.stop()
		except:
			pass
		self.cmdPlay.set_stock_id("gtk-media-play")

	# Evento che apre la finetra informazioni
	def on_About(self, *args):
		# Oggetto di classe AboutDialog
		self.About = AboutDialog()

	# Evento che rimuove gli elementi della tabella slezionati
	def on_Remove(self, *args):
		self.FileTable.remove()
		self.on_Stop()
		self.cmdPlay.set_stock_id("gtk-media-play")
		self.mainWindow.set_title(WINDOW_TITLE)
		if len(self.audioFileList.filelist) == 0:
			self.set_sensitive(False)
			self.cmdConvert.set_sensitive(False)
			self.cmdStop.set_sensitive(False)
			self.menuStop.set_sensitive(False)
		else:
			self.set_sensitive(True)
			self.cmdConvert.set_sensitive(True)

	# Evento che pulisce la tabella
	def on_Purge(self, *args):
		self.set_status("Purge list...")
		self.FileTable.purge()
		self.audioFileList.purge()
		self.TagBar.purge()
		self.TagBar.hide()
		self.cmdOpenFile.set_sensitive(True)
		self.cmdOpenFolder.set_sensitive(True)
		self.set_status()
		self.on_Stop()
		self.cmdPlay.set_stock_id("gtk-media-play")
		self.mainWindow.set_title(WINDOW_TITLE)
		self.set_sensitive(False)
		self.cmdConvert.set_sensitive(False)
		self.cmdRip.set_sensitive(False)
		self.progConvert.hide()

	# Evento che apre la finestra preferenze
	def on_Preferences(self, *args):
		dlgPrefs = PreferencesDialog(self.mainWindow, self.prefs)
		dlgPrefs.show()

	# Evento per la riproduzione di un file
	def on_Play(self, *args):

		print self.cmdPlay.get_stock_id()
		self.cmdStop.set_sensitive(True)
		self.menuStop.set_sensitive(True)
		self.popStop.set_sensitive(True)
		self.scaleTime.set_sensitive(True)

		# Se il pulsante indica "play", riproduce la selezione
		if self.cmdPlay.get_stock_id() == "gtk-media-play":

			# Se il player è pronto, inizia la riproduzione
			if self.player.state == "ready":

				#Carica la lista dei file selezionati
				self.selplay = self.Selection(self.FileTable)
				# Riproduce solo il primo file della lista caricata
				try:
					sel = self.selplay[0]
				except IndexError:
					sel = None
				self.playing_song = sel
				if sel:
					af = sel[0]
					it = sel[1]
					if not self.file_exists(af):
						return

					self.FileTable.tvSelection.unselect_all()
					self.FileTable.tvSelection.select_iter(it)
					print "Riproduzione di: ", af.get_uri()

					self.player.play(af)

					if af.get_tag("title") != "Unknown title" and af.get_tag("artist") != "Unknown artist":
						msg = af.get_tag("artist") + " - " + af.get_tag("title")
					elif af.get_uri():
						msg = af.get_filepath()
					self.set_status("Playing " + msg)
					self.mainWindow.set_title(msg)
					self.scaleTime.set_range(0, 1)
					self.scaleTime.set_value(0)

			# Se è in pausa, riprende la riproduzione
			elif self.player.state == "paused":
				self.player.carry_on()

			if self.player.state == "playing":
				self.cmdPlay.set_stock_id("gtk-media-pause")

		# Se il pulsante indica "pause", mette in pausa
		elif self.cmdPlay.get_stock_id() == "gtk-media-pause":
			if self.player.state == "playing":
				self.player.pause()
				if self.player.state == "paused":
					self.cmdPlay.set_stock_id("gtk-media-play")

	# Thread per l'avanzamento del tempo di riproduzione
	def play_thread(self):
		# From http://pygstdocs.berlios.de/pygst-tutorial/seeking.html
		print "PLAY_THREAD"
		play_thread_id = self.player.play_thread_id
		print play_thread_id
		print self.player.play_thread_id
		gtk.gdk.threads_enter()
		self.labelTime.set_text("00:00 / 00:00")
		gtk.gdk.threads_leave()

		while play_thread_id == self.player.play_thread_id:
			try:
				time.sleep(0.2)
				if self.player.duration == -1:
					continue
				gtk.gdk.threads_enter()
				self.labelTime.set_text("00:00 / " + self.player.duration_str)
				gtk.gdk.threads_leave()
				print "OK 1"
				break
			except:
				print "QUERY_IN_CORSO"
				pass

		time.sleep(0.2)
		while play_thread_id == self.player.play_thread_id:
			# A volte la query fallisce
			try:
				pos_int = self.player.player.query_position(gst.FORMAT_TIME, None)[0]
			except: continue
			pos_str = self.player.convert_ns(pos_int)
			if play_thread_id == self.player.play_thread_id:
				gtk.gdk.threads_enter()
				self.labelTime.set_text(pos_str + " / " + self.player.duration_str)
				self.scaleTime.set_value(float(pos_int)/float(self.player.duration))
				gtk.gdk.threads_leave()
			time.sleep(0.5)

	# Evento che avanza la barra del tempo
	def on_adjust_bounds(self, *args):
		print "adjust-bound"
		self.player.change_position(self.scaleTime.get_value())

	# Evento per la modifica del volume
	def volume_changed(self, *args):
		try:
			self.player.set_volume(self.volumebutton.get_value())
		except: pass

	# Richiamato quando termina la riproduzione di un brano
	def on_endPlay(self, player_bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			print "Esecuzione terminata"
			self.set_status()
			self.mainWindow.set_title(WINDOW_TITLE)
			self.cmdStop.set_sensitive(False)
			self.menuStop.set_sensitive(False)
			self.popStop.set_sensitive(False)
			self.scaleTime.set_sensitive(False)
			self.labelTime.set_text("00:00 / 00:00")
			# Passa al brano successivo
			try:
				print "Brano successivo"
				self.on_Next()
			except:
				pass

			#self.scaleTime.set_value(1)
		elif t == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.set_status()
			self.mainWindow.set_title(WINDOW_TITLE)
			self.cmdStop.set_sensitive(False)
			self.menuStop.set_sensitive(False)
			self.popStop.set_sensitive(False)
			self.scaleTime.set_sensitive(False)
			self.labelTime.set_text("00:00 / 00:00")
			#self.scaleTime.set_value(0)

	# Evento per il menu pausa (serve per distinguere l'azione
	# da quello del pulsante play/pause)
	def on_menuPause(self, *args):
		if self.cmdPlay.get_stock_id() == "gtk-media-pause":
			self.on_Play()

	# Evento per il menu play (serve per distinguere l'azione
	# da quello del pulsante play/pause)
	def on_menuPlay(self, *args):
		if self.cmdPlay.get_stock_id() == "gtk-media-play":
			self.on_Play()
		else:
			if self.playing_song == self.Selection(self.FileTable):
				self.on_Play()
				self.on_Play()
			else:
				self.on_Stop()
				self.on_Play()

	# Evento per il doppio click su una riga della tabella
	# e riproduce la canzone clickata
	def on_row_activated(self, *args):
		print "RIGA ATTIVATA"
		try:
			self.player.stop()
			self.cmdPlay.set_stock_id("gtk-media-play")
		except:
			pass
		self.on_Play()

	# Evento per il click sulla tabella dei file
	def on_row_clicked(self, widget, event):

		# Apre il menù contestuale
		if event.button == 3:
			print "TASTO DESTRO"
			if self.Selection(self.FileTable):
				x = int(event.x)
				y = int(event.y)
				time = event.time
				pthinfo = widget.get_path_at_pos(x, y)
				if pthinfo is not None:
					path, col, cellx, celly = pthinfo
					widget.grab_focus()
					widget.set_cursor( path, col, 0)
					self.popupmenu.popup( None, None, None, event.button, time)
					return True
		if event.button == 1:
			print "TASTO SINISTRO"
		if event.type == gtk.gdk.BUTTON_PRESS:
			print "SINGOLO CLICK"
		elif event.type == gtk.gdk._2BUTTON_PRESS:
			print "DOPPIO CLICK"
		elif event.type == gtk.gdk._3BUTTON_PRESS:
			print "TRIPLO CLICK"

	# Evento per la selezione di una riga della tabella
	def on_row_selected(self, *args):
		print "RIGA SELEZIONATA"
		model, pathlist = self.FileTable.tvSelection.get_selected_rows()
		if pathlist:
			rowpath = pathlist[0]
			it = self.FileTable.listStore.get_iter(rowpath)
			for af in self.audioFileList.filelist:
				if str(af.pointer) == model.get_string_from_iter(it):
					print "SELEZIONATO IL FILE: ", af.get_filepath()

	# Evento che ferma la riproduzione
	def on_Stop(self, *args):

		try:
			self.player.stop()
		except: pass
		self.cmdPlay.set_stock_id("gtk-media-play")
		self.set_status()
		self.mainWindow.set_title(WINDOW_TITLE)
		self.cmdStop.set_sensitive(False)
		self.menuStop.set_sensitive(False)
		self.popStop.set_sensitive(False)
		self.scaleTime.set_value(0)
		self.scaleTime.set_sensitive(False)
		self.labelTime.set_text("00:00 / 00:00")


	# Evento che passa a riprodurre la canzone successiva
	def on_Next(self, *args):

		model, pathlist = self.FileTable.tvSelection.get_selected_rows()
		rowpath = pathlist[0]
		self.FileTable.tvSelection.unselect_all()
		self.on_Stop()
		#self.FileTable.tvSelection.select_path(rowpath)
		it = self.FileTable.listStore.get_iter(rowpath)
		root_it = self.FileTable.listStore.get_iter_root()
		next_it = self.FileTable.listStore.iter_next(it)
		if next_it:
			self.FileTable.tvSelection.select_iter(next_it)
			print "on_Next Successivo"
		else:
			try:
				self.FileTable.tvSelection.select_iter(root_it)
				print "on_Next Primo della lista"
			except:
				pass
		self.cmdPlay.set_stock_id("gtk-media-play")
		self.labelTime.set_text("00:00 / 00:00")
		self.on_Play()

	# Evento che passa a riprodurre la canzone precedente
	def on_Prev(self, *args):

		selection = []

		model, pathlist = self.FileTable.tvSelection.get_selected_rows()
		rowpath = pathlist[0]
		self.FileTable.tvSelection.unselect_all()
		self.on_Stop()
		prev_pointer = 0
		prev_it = None
		curr_it = self.FileTable.listStore.get_iter(rowpath)
		for af in self.audioFileList.filelist:
			if str(af.pointer) == model.get_string_from_iter(curr_it):
				prev_pointer = af.pointer - 1
				print "af.pointer: ", af.pointer
				print "prev_pointer: ", prev_pointer
		if prev_pointer > -1:
			self.FileTable.tvSelection.select_all()
			model, pathlist = self.FileTable.tvSelection.get_selected_rows()

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
					self.FileTable.tvSelection.unselect_all()
					self.FileTable.tvSelection.select_iter(prev_it)
			else:
				try:
					self.FileTable.tvSelection.select_iter(self.FileTable.listStore.get_iter_root())
				except:
					pass
		self.cmdPlay.set_stock_id("gtk-media-play")
		self.labelTime.set_text("00:00 / 00:00")
		self.on_Play()

	# Evento per l'avanzamento veloce
	def on_Forward(self, *args):

		self.player.forward()

	# Evento per il riavvolgimento veloce
	def on_Rewind(self, *args):

		self.player.rewind()

	# Evento che apre un CD_Audio e carica i tag da MusicBrainz o da FreeDB
	# se il server è disponibile
	def on_CD(self, *args):

		self.set_status("Adding Audio CD...")
		self.TagBar.purge()

		try:
			self.CDSelection = CDSelection(self.mainWindow)
		except:
			self.set_status("Insert an Audio CD into the drive...")
			self.cmdOpenFile.set_sensitive(True)
			self.cmdOpenFolder.set_sensitive(True)
			self.dlg = WarningDialog(self.mainWindow, 
					NAME + " - Warning", "No disc into the drive. Please insert one...")
			return

		if self.CDSelection.audioCD.is_audio_cd:
			self.audioFileList.purge()
			self.FileTable.purge()
			self.TagBar.show()
			self.cmdPlay.set_stock_id("gtk-media-play")
			self.on_Stop()
			
			#tags_list = self.CDSelection.select_CD_from_CDDB()
			try:
				tags_list = self.CDSelection.select_CD_from_MB()
			except: raise

			if tags_list == None:
				self.TagBar.hide()
				return

			self.TagBar.entry_tag(
					tags_list[0]["album"],
					tags_list[0]["artist"],
					tags_list[0]["year"],
					tags_list[0]["genre"])
				
			for tags in tags_list:
				self.set_status("Append " + "Track " + str(tags["n"]) + "/" + str(len(tags_list)))
				af = AudioFile(tags["uri"], tags["n"])
				af.set_tag("track_number", tags["track-number"])
				af.set_tag("title", tags["title"])
				af.set_tag("artist", tags["artist"])
				af.set_tag("album", tags["album"])
				af.set_tag("year", tags["year"])
				af.set_tag("genre", tags["genre"])
				af.set_filename("Track " + tags["track-number"])
				print af.get_tags_as_dict()
				self.audioFileList.append(af)
				self.FileTable.append(self.audioFileList)
				
			self.set_status()
			self.set_sensitive(True)
			self.cmdRip.set_sensitive(True)

			self.cmdOpenFile.set_sensitive(False)
			self.menuOpenFile.set_sensitive(False)

			self.cmdOpenFolder.set_sensitive(False)
			self.menuOpenFolder.set_sensitive(False)

			self.cmdConvert.set_sensitive(False)
			self.menuConvert.set_sensitive(False)
		else:
			self.TagBar.hide()
			return


	# Evento che cambia i dati del CD su modifica utente
	def on_entry_changed(self, *args):
		print "CHANGED"
		self.CDdata = {"album": self.TagBar.entryAlbum.get_text(),
						"artist": self.TagBar.entryArtist.get_text(),
						"year": self.TagBar.entryYear.get_text(),
						"genre": self.TagBar.entryGenre.get_text()
						}
		for af in self.audioFileList.filelist:
			af.set_tag("album", self.CDdata["album"])
			af.set_tag("artist", self.CDdata["artist"])
			af.set_tag("year", self.CDdata["year"])
			af.set_tag("genre", self.CDdata["genre"])

		self.FileTable.purge()
		self.FileTable.append(self.audioFileList)

	# Evento che apre la finestra di scelta per il ripping del CD
	def on_Rip(self, *args):

		try:
			from morituri.rip import main as Ripper
		except:
			self.dlg = WarningDialog(self.mainWindow, NAME + " - Warning",'''Morituri is not available.
Please try 'apt-get install morituri' or
visit http://thomas.apestaart.org/morituri/trac/wiki''')
			return

		#Apre la finestra di dialogo con le impostazioni
		dlgRip = RipDialog(self.mainWindow, self.prefs)
		dlgRip.show()

		if not dlgRip.response == gtk.RESPONSE_OK:
			return
		else:
			self.set_status("Ripping Audio CD ...")
			sorgente = "cd"
			# Posizione temporanea
			import tempfile
			tempdir = tempfile.mkdtemp()

			# Ripping del CD audio in una directory temporanea
			# Argomenti da passare:
			# rip_args = ['cd', 'rip', '--output-directory=' + tempdir, '--track-template=%t - %n', '--profile=wav']
			rip_args = ['cd', 'rip', '--profile=wav', '--output-directory=' + tempdir]
			'''try:
				# Avvia l'estrazione
				ret = Ripper.main(rip_args)
				ret = 0
			except:
				self.dlg = WarningDialog(self.mainWindow, NAME + " - Warning", "Task exception. Morituri don't work.")
				ret = -1
				self.set_status()
				return
			if ret == 0:
				self.set_status("Ripping completed...")'''

			# Avvia l'estrazione con morituri
			ret = Ripper.main(rip_args)

			# Carica i file da convertire
			walk = os.walk(tempdir)
			convert_filelist = []
			for dirpath, subdir, filenames in walk:
				for f in filenames:
					if f[-4:] == ".wav":
						f = os.path.join(dirpath, f)
						convert_filelist.append(AudioFile("file://" + f))

			#Carica la lista dei file selezionati
			if not bool(int(self.prefs.get_option("save-all-tracks"))):
				# Solo i file selezionati
				self.selconv = self.Selection(self.FileTable)
			else:
				# Tutti i file
				self.FileTable.tvSelection.select_all()
				self.selconv = self.Selection(self.FileTable)
				self.FileTable.tvSelection.unselect_all()

			if self.selconv:
				# Inizializza la coda
				request_queue = Queue.Queue()
				n = 0
				for sel in self.selconv:
					n += 1
					af = sel[0]
					it = sel[1]

					for convert_file in convert_filelist:
						if af.get_tag("track_number") == convert_file.get_filename()[0:2]:
							convert_file.set_tags_as_dict(af.get_tags_as_dict())
							# Salva non compressi
							if not bool(int(self.prefs.get_option("rip-compressed"))) or self.prefs.get_option("output-format") == "wav":
								self.prefs.set_option("output-format", "wav")
								request_queue.put([n, (convert_file, it)])
								self.set_status("Now save uncompressed files...")
							elif bool(int(self.prefs.get_option("rip-compressed"))):
								request_queue.put([n, (convert_file, it)])
								self.set_status("Now save compressed files...")
				self.init = time.time()
				self.progConvert.show()

				# Riempita la coda, lancia il thread dell'encoder
				self.encoder_thread = Converter(self, self.prefs, sorgente, request_queue)
				self.encoder_thread.start()

				# Svuota la coda per fermare il thread
				for sel in self.selconv:
					request_queue.put(None)
				self.FileTable.tvSelection.unselect_all()
				self.set_status("Done...")

	# Evento per la conversione dei file audio
	def on_Convert(self, *args):

		#Apre la finestra di dialogo con le impostazioni
		dlgCon = ConverterDialog(self.mainWindow, self.prefs)
		dlgCon.show()

		if not dlgCon.response == gtk.RESPONSE_OK:
			return
		
		sorgente = "file"
		#Carica la lista dei file selezionati
		if not bool(int(self.prefs.get_option("save-all-tracks"))):
			# Solo i file selezionati
			self.selconv = self.Selection(self.FileTable)
		else:
			# Tutti i file
			self.FileTable.tvSelection.select_all()
			self.selconv = self.Selection(self.FileTable)
			self.FileTable.tvSelection.unselect_all()

		if self.selconv:
			# Inizializza la coda
			request_queue = Queue.Queue()
			n = 0
			for sel in self.selconv:
				n += 1
				af = sel[0]
				it = sel[1]

				# Status bar
				if af.get_tag("title") != "Unknown title" and af.get_tag("artist") != "Unknown artist":
					self.msg = af.get_tag("artist") + " - " + af.get_tag("title")
				elif af.get_uri():
					self.msg = af.get_filepath()
				self.set_status("Converting " + self.msg + " (file " + str(n) + "/" + str(len(self.selconv)) + ")")

				# Riempie la coda caricando le preferenze
				request_queue.put([n, sel])

			self.init = time.time()
			self.progConvert.show()

			# Riempita la coda, lancia il thread dell'encoder
			self.encoder_thread = Converter(self, self.prefs, sorgente, request_queue)
			self.encoder_thread.start()

			# Svuota la coda per fermare il thread
			for sel in self.selconv:
				request_queue.put(None)

			self.FileTable.tvSelection.unselect_all()

	# Aggiorna la progressbar durante la conversione
	def on_ProgressBar(self):

		self.progConvert.set_fraction(self.encoder_thread.amount_completed)
		if self.encoder_thread.work_complete:
			self.progConvert.set_fraction(1)
			if self.encoder_thread.queue_complete:
				if bool(int(self.prefs.get_option("playlist"))):
					self.write_playlist(self.encoder_thread.savepath, self.encoder_thread.playlistname, self.encoder_thread.listsongs)
				self.progConvert.set_text("Complete!")
				print "Complete!"
				self.set_status("Done in " + str(round(time.time() - self.init, 2)) + " seconds")
				self.progConvert.set_fraction(1)
		else:
			self.progConvert.set_text("%d%%" % (self.encoder_thread.amount_completed * 100))
			self.set_status("Converting " + self.encoder_thread.msg + \
					" (file " + str(self.encoder_thread.n) + "/" + str(len(self.selconv)) + ")" + \
					" - " + ("%f" % (round(time.time() - self.init, 2)))[:4] + " seconds")
		return not self.encoder_thread.work_complete

	# Crea la playlist dei brani convertiti
	def write_playlist(self, savepath, playlistname, listsongs):

		playlist = open(savepath + "/" + playlistname + ".m3u", "wb")
		playlist.writelines(listsongs)
		playlist.close()

	# Seleziona tutte le righe
	def on_SelectAll(self, *args):

		self.FileTable.tvSelection.select_all()

	# Deseleziona tutte le righe
	def on_UnselectAll(self, *args):

		self.FileTable.tvSelection.unselect_all()

	# Proprietà della canzone
	def on_Property(self, *args):

		#Carica la lista dei file selezionati
		self.selplay = self.Selection(self.FileTable)
		# Riproduce solo il primo file della lista caricata
		try:
			sel = self.selplay[0]
		except IndexError:
			sel = None
		self.playing_song = sel
		if sel:
			af = sel[0]
			it = sel[1]
			self.FileTable.tvSelection.unselect_all()
			self.FileTable.tvSelection.select_iter(it)

			dlgprop = PropertyDialog(self, self.mainWindow, sel)
			dlgprop.show()

	# Modifica i tag
	def on_Tagger(self, *args):

		#Carica la lista dei file selezionati
		self.selplay = self.Selection(self.FileTable)
		# Riproduce solo il primo file della lista caricata
		try:
			sel = self.selplay[0]
		except IndexError:
			sel = None
		if sel:
			af = sel[0]
			it = sel[1]
			self.FileTable.tvSelection.unselect_all()
			self.FileTable.tvSelection.select_iter(it)

		dlgtag = TaggerDialog(self, self.mainWindow, sel)
		dlgtag.show()

		if not dlgtag.response == gtk.RESPONSE_OK:
			return

		if dlgtag.save_tags:
			if dlgtag.save_tags_all:
				for af in self.audioFileList.filelist:
					af.write_metadata()
					if dlgtag.id3v2:
						af.write_ID3v2()
			else:
				selection = self.Selection(self.FileTable)
				sel = selection[0]
				sel[0].write_metadata()
				if dlgtag.id3v2:
					sel[0].write_ID3v2()
				i = self.audioFileList.filelist.index(sel[0])
				self.audioFileList.remove(sel[0].get_uri())
				self.audioFileList.filelist.insert(i, AudioFile(sel[0].get_uri()))

		elif dlgtag.remove_tags:
			if dlgtag.remove_tags_all:
				for af in self.audioFileList.filelist:
					af.remove_metadata()
			else:
				selection = self.Selection(self.FileTable)
				sel = selection[0]
				sel[0].remove_metadata()
				i = self.audioFileList.filelist.index(sel[0])
				self.audioFileList.remove(sel[0].get_uri())
				self.audioFileList.filelist.insert(i, AudioFile(sel[0].get_uri()))

		self.FileTable.purge()
		self.FileTable.append(self.audioFileList)

	# Crea una playlist
	def on_Playlist(self, *args):

		dlgpl = PlaylistDialog(self, self.mainWindow)
		dlgpl.show()

		if not dlgpl.response == gtk.RESPONSE_OK:
			return


	# Restituisce una lista di file audio selezionati
	def Selection(self, FileTable):

		selection = []

		model, pathlist = FileTable.tvSelection.get_selected_rows()
		print "pathlist: ", pathlist
		if not pathlist:
			print "not"
			try:
				pathlist = [(0,)]
				print "pathlist: ", pathlist
			except:
				pass
		if pathlist:
			print "pathlist: ", pathlist
			iterlist = []
			for rowpath in pathlist:
				print "rowpath: ", rowpath
				try:
					iterlist.append(model.get_iter(rowpath))
				except ValueError:
					pass
			print "iterlist: ", iterlist
			for it in iterlist:
				print "riga da riprodurre", model.get_string_from_iter(it)
				for af in self.audioFileList.filelist:
					print "af.pointer: ", af.pointer
					print "model.get_string_from_iter(iter): ", model.get_string_from_iter(it)
					if str(af.pointer) == model.get_string_from_iter(it):
						print "sono uguali"
						selection.append((af, it))
						print "Selection: ", selection
					else:
						print "non sono uguali"
		return selection

	# Funzione che apre il selettore file e carica i file scelti
	def AddFileList(self, FileChooser):

		# Imposta la cartella corrente
		try:
			if os.path.exists(self.prefs.get_option("last-used-folder")):
				FileChooser.set_current_folder(self.prefs.get_option("last-used-folder"))
			else:
				FileChooser.set_current_folder(os.path.expandvars("$HOME"))
			# Eccezione nel caso in cui non sia definita.
			# In tal caso la cartella corrente viene settata sulla HOME.
		except:
			FileChooser.set_current_folder(os.path.expandvars("$HOME"))

		# Seleziona la risposta
		response = FileChooser.run()
		FileChooser.hide()
		if response == gtk.RESPONSE_OK:

			if FileChooser.is_folder:
				# Se il percorso restituito è una cartella
				# crea una lista con i file audio presenti nella cartella
				# e nelle sue sottocartelle.
				walk = os.walk(FileChooser.get_current_folder())

				# Restituisce una lista con tutti i file
				walk_filelist = []
				for dirpath, subdir, filenames in walk:
					for f in filenames:
						f = os.path.join(dirpath, f)
						walk_filelist.append(f)

				# Aggiunge l'uri completo ad ogni file
				furi = []
				for f in walk_filelist:
					for ext in fileext:
						if f.endswith(ext):
							furi.append("file://" + str(f))
				for l in furi:
					af = AudioFile(l)
					self.audioFileList.append(af)
					self.FileTable.append(self.audioFileList)
			else:
				# Se il percorso restituito è un file o un elenco di file
				furi = []
				filenames = FileChooser.get_filenames()
				if filenames:
					for f in filenames:
						# Se il percorso restituito è una playlist "*.m3u"
						if f.endswith(".m3u"):
							plist = open(f, "rb").readlines()
							for finlist in plist:
								if not "#EXT" in finlist:
									print re.compile("\n").sub("", finlist)
									print "PERCORSO FILE IN PLAYLIST", "file://" + FileChooser.get_current_folder() + "/" + re.compile("\n").sub("", finlist)
									furi.append("file://" + FileChooser.get_current_folder() + "/" + re.compile("\n").sub("", finlist))
						else:
							furi.append("file://" + f)
					for l in furi:
						af = AudioFile(l)
						self.audioFileList.append(af)
						self.FileTable.append(self.audioFileList)

			# Scrive i file nella tabella
			#self.FileTable.append(self.audioFileList)

		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, no files selected'

		self.prefs.set_option("last-used-folder", FileChooser.get_current_folder())
		FileChooser.destroy()
		self.set_status()

		if not self.audioFileList.filelist:
			print "LISTA VUOTA"
			self.set_sensitive(False)
			self.cmdConvert.set_sensitive(False)
		else:
			self.set_sensitive(True)
			self.cmdConvert.set_sensitive(True)

	# Funzione che verifica se il file audio esiste
	def file_exists(self, af):
		if os.path.exists(af.get_filepath()):
			return True
		elif af.get_uri()[:7] == "cdda://":
			return True
		else:
			dlg = WarningDialog(self.mainWindow, NAME + " - Warning", "The file " + af.get_filepath()  + " does not exist in the specified path. Perhaps it was deleted.")
			return False

### Classe della finestra di dialogo apertura file ###
class FileChooser:

	# Costruttore della classe
	def __init__(self, is_folder):

		self.is_folder=is_folder

		# Crea la finestra di dialogo dlgFileChooser
		self.dlgFileChooser = gtk.FileChooserDialog(None, None, gtk.FILE_CHOOSER_ACTION_OPEN,
							(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
								gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		self.dlgFileChooser.set_default_response(gtk.RESPONSE_OK)
		self.dlgFileChooser.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.dlgFileChooser.set_current_folder("$HOME")
		self.dlgFileChooser.set_local_only(False)

		if is_folder:
			# Finestra di dialogo dlgFileChooser per aprire una cartella
			self.dlgFileChooser.set_title('Add folder...')
			self.dlgFileChooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
			self.dlgFileChooser.set_select_multiple(True)
		else:
			# Crea la finestra di dialogo dlgFileChooser per aprire un file
			self.dlgFileChooser.set_title('Add files...')
			self.dlgFileChooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
			self.dlgFileChooser.set_select_multiple(True)

		#Crea un filtro per tutti i file audio
		self.filter1 = gtk.FileFilter()
		self.filter1.set_name("Audio files")
		for n, p in FILE_PATTERN:
			self.filter1.add_pattern(p)
		self.dlgFileChooser.add_filter(self.filter1)

		if not is_folder:
			# Crea un filtro per tutti i file
			self.filter2 = gtk.FileFilter()
			self.filter2.set_name("All files (*.*)")
			self.filter2.add_pattern("*")
			self.dlgFileChooser.add_filter(self.filter2)

			# Crea un filtro per le playlist "*.m3u"
			self.filter4 = gtk.FileFilter()
			self.filter4.set_name("Playlist (*.m3u)")
			self.filter4.add_pattern("*.m3u")
			self.dlgFileChooser.add_filter(self.filter4)

			# Crea un filtro per ogni tipo di file audio
			for n, p in FILE_PATTERN:
				self.filter3 = gtk.FileFilter()
				self.filter3.set_name(n)
				self.filter3.add_pattern(p)
				self.dlgFileChooser.add_filter(self.filter3)

	def __getattr__(self, attr):
		try:
			return getattr(self.dlgFileChooser, attr)
		except AttributeError:
			print AttributeError


### Tabella dei file ###
class FileTable:

	# Costruttore della classe
	def __init__(self, builderXAC):

		import pango

		# Collega il TreeView
		self.tvFileList = builderXAC.get_object("trvFileList")
		self.tvFileList.set_rules_hint(True)
		# Crea il modello ListStore con il contenuto della tabella
		self.listStore = gtk.ListStore(str, str, str, str, str, str, str)
		# Lo collega al TreeView
		self.tvFileList.set_model(self.listStore)

		# Imposta una lista con i titoli delle colonne
		columnHeader = ["Track", "Artist", "Title", "Album", "Duration", "File name", "Path"]

		# Imposta una lista con gli oggetti colonna
		columns = []

		# Colonna "Track"
		cell = gtk.CellRendererText()
		cell.set_property("editable", True)
		column_track = gtk.TreeViewColumn("Track", cell, text=0)
		column_track.set_min_width(45)
		columns.append(column_track)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 0))

		# Colonna "Artist"
		cell = gtk.CellRendererText()
		cell.set_property("editable", True)
		cell.set_property("ellipsize", pango.ELLIPSIZE_END)
		column_artist = gtk.TreeViewColumn("Artist", cell, text=1)
		column_artist.set_min_width(135)
		columns.append(column_artist)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 1))

		# Colonna "Title"
		cell = gtk.CellRendererText()
		cell.set_property("editable", True)
		cell.set_property("ellipsize", pango.ELLIPSIZE_END)
		column_title = gtk.TreeViewColumn("Title", cell, markup=2)
		column_title.set_min_width(160)
		columns.append(column_title)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 2))

		# Colonna "Album"
		cell = gtk.CellRendererText()
		cell.set_property("editable", True)
		cell.set_property("ellipsize", pango.ELLIPSIZE_END)
		column_album = gtk.TreeViewColumn("Album", cell, markup=3)
		column_album.set_min_width(160)
		columns.append(column_album)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 3))

		# Colonna "Duration"
		cell = gtk.CellRendererText()
		column_duration = gtk.TreeViewColumn("Duration", cell, text=4)
		column_duration.set_min_width(80)
		columns.append(column_duration)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 4))

		# Colonna "File name"
		cell = gtk.CellRendererText()
		cell.set_property("ellipsize", pango.ELLIPSIZE_END)
		column_file_name = gtk.TreeViewColumn("File name", cell, text=5)
		column_file_name.set_min_width(125)
		columns.append(column_file_name)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 5))

		# Colonna "Path"
		cell = gtk.CellRendererText()
		cell.set_property("ellipsize", pango.ELLIPSIZE_END)
		column_path = gtk.TreeViewColumn("Path", cell, text=6)
		column_path.set_min_width(250)
		columns.append(column_path)
		cell.connect("edited", self.on_edited_cell, (self.listStore, 6))

		# Crea le colonne della tabella dei file
		i=0
		for col in columns:
			# Aggiunge la colonna al TreeView
			self.tvFileList.append_column(col)
			col.set_resizable(True)
			col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
			#col.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
			#col.set_sort_column_id(i)
			#col.connect("clicked", lambda on_col_click:self.on_column_clicked)
			i=i+1

		# Permette la selezione multipla delle righe della tabella
		self.tvSelection = self.tvFileList.get_selection()
		self.tvSelection.connect("changed", lambda on_changed: xaudiocopy.on_row_selected())
		self.tvSelection.set_mode(gtk.SELECTION_MULTIPLE)

	# Aggiunge una riga e carica i dati
	def append(self, audioFileList):
		self.tableFileList = audioFileList
		# Prima pulisce la tabella
		self.purge()
		# Puntatore alla riga dei file inseriti
		self.pointer = -1
		for af in self.tableFileList.filelist:
			# Popola di dati le righe
			ft = lambda x : x=="" and "Unknown title" or x
			fa = lambda x : x=="" and "Unknown artist" or x
			fl = lambda x : x=="" and "Unknown album" or x
			applist = [str(af.get_tag("track_number")), fa(af.get_tag("artist")), fl("""<span><b><i>{0}</i></b></span>""".format(af.get_tag("title"))), fl("""<span><i>{0}</i></span>""".format(af.get_tag("album"))), af.get_duration_mm_ss(), af.get_filename(), af.get_filepath()]
			self.listStore.append(applist)
			self.pointer = self.pointer + 1
			af.pointer = self.pointer
			print 'canzone ' + str(af.pointer) + ': ' + af.get_uri()

	# Rimuove righe dalla lista
	# Grazie a Fabrizio Tarizzo (http://www.fabriziotarizzo.org/documenti/gtktreeview-tutorial/)
	def remove(self):
		mode = self.tvSelection.get_mode()
		if mode == gtk.SELECTION_MULTIPLE:
			model, pathlist = self.tvSelection.get_selected_rows()
			print "pathlist: ", pathlist
			if pathlist:
				iterlist = []
				for rowpath in pathlist:
					print "rowpath: ", rowpath
					iterlist.append(model.get_iter(rowpath))
				print "iterlist: ", iterlist
				for it in iterlist:
					print "iter delle righe eliminate: ", it
					#print "model.get_string_from_iter(iter): ", model.get_string_from_iter(it)
					#model.remove (it)
					for af in self.tableFileList.filelist:
						print "af.pointer: ", af.pointer
						print "model.get_string_from_iter(iter): ", model.get_string_from_iter(it)
						if str(af.pointer) == model.get_string_from_iter(it):
							print "sono uguali"
							self.tableFileList.remove(af.get_uri())
						else:
							print "non sono uguali"
					xaudiocopy.audioFileList.filelist = self.tableFileList.filelist[:]
					print model.get(it,3)
				for it in iterlist:
					model.remove (it)
				self.append(xaudiocopy.audioFileList)

		if mode == gtk.SELECTION_SINGLE:
			model, iter = self.tvSelection.get_selected()
			if iter:
				print "riga da eliminare", model.get_string_from_iter(iter)
				for af in self.tableFileList.filelist:
					print "af.pointer: ", af.pointer
					print "model.get_string_from_iter(iter): ", model.get_string_from_iter(iter)
					if str(af.pointer) == model.get_string_from_iter(iter):
						print "sono uguali"
						self.tableFileList.remove(af.get_uri())
					else:
						print "non sono uguali"
				xaudiocopy.audioFileList.filelist = self.tableFileList.filelist[:]
				print model.get(iter,3)
				model.remove (iter)
				self.append(xaudiocopy.audioFileList)

	# Pulisce la tabella
	def purge(self):
		self.listStore.clear()

	def on_column_clicked(self):
		songpath = []
		for i in range(len(self.listStore)):
			it = self.listStore.get_iter_from_string(str(i))
			songpath.append("file://" + self.listStore.get_value(it, 6) + "/" + self.listStore.get_value(it, 5))
			print "SONGPATH: ", songpath[i]
			for af in xaudiocopy.audioFileList.filelist:
				if af.get_uri() == songpath[i]:
					af.pointer = i
		xaudiocopy.audioFileList.sort(lambda x, y: cmp(x.pointer, y.pointer))
		for af in xaudiocopy.audioFileList.filelist:
			print af.get_uri()

	def on_edited_cell(self, cell, rowpath, new_text, user_data):

		model, col_id = user_data
		iter = model.get_iter (rowpath)
		model.set_value (iter, col_id, new_text)
		model, pathlist = self.tvSelection.get_selected_rows()
		if pathlist:
			rowpath = pathlist[0]
			it = self.listStore.get_iter(rowpath)
			for af in xaudiocopy.audioFileList.filelist:
				if str(af.pointer) == model.get_string_from_iter(it):
					af.set_tag("track_number", model.get_value(it, 0))
					af.set_tag("artist", model.get_value(it, 1))
					if model.get_value(it, 2).startswith("<span><b><i>"):
						tit1 = model.get_value(it, 2)[len("<span><b><i>"):]
						tit = tit1[:len(tit1) - len("</span></b></i>")]
						af.set_tag("title", tit)
					else:
						af.set_tag("title", model.get_value(it, 2))
					if model.get_value(it, 3).startswith("<span><i>"):
						alb1 = model.get_value(it, 3)[len("<span><i>"):]
						alb = alb1[:len(alb1) - len("</span></i>")]
						af.set_tag("album", alb)
					else:
						af.set_tag("album", model.get_value(it, 3))
			self.append(xaudiocopy.audioFileList)
			self.tvSelection.select_path(rowpath)


### Tabella del CD ###
class TagBar:

	# Costruttore della classe
	def __init__(self, builderXAC, album=None, artist=None, year=None, genre=None):

		# Collega gli entry
		self.labelAlbum = builderXAC.get_object("labelAlbum")
		self.labelArtist = builderXAC.get_object("labelArtist")
		self.labelYear = builderXAC.get_object("labelYear")
		self.labelGenre = builderXAC.get_object("labelGenre")
		self.entryAlbum = builderXAC.get_object("entryAlbum")
		self.entryArtist = builderXAC.get_object("entryArtist")
		self.entryYear = builderXAC.get_object("entryYear")
		self.entryGenre = builderXAC.get_object("entryGenre")
		try:
			self.entry_tag(album, artist, year, genre)
		except:
			pass

	def entry_tag(self, album=None, artist=None, year=None, genre=None):

		fa = lambda x : x=="" and "Unknown artist" or x
		fl = lambda x : x=="" and "Unknown album" or x
		fg = lambda x : x=="" and "" or x
		self.entryAlbum.set_text(fl(album))
		self.entryArtist.set_text(fa(artist))
		self.entryYear.set_text(str(year))
		self.entryGenre.set_text(fg(genre))

	def purge(self):
		self.entryAlbum.set_text("")
		self.entryArtist.set_text("")
		self.entryYear.set_text("")
		self.entryGenre.set_text("")

	def set_sensitive(self, sensitive):
		if sensitive:
			self.entryAlbum.set_sensitive(True)
			self.entryArtist.set_sensitive(True)
			self.entryYear.set_sensitive(True)
			self.entryGenre.set_sensitive(True)
		elif not sensitive:
			self.entryAlbum.set_sensitive(False)
			self.entryArtist.set_sensitive(False)
			self.entryYear.set_sensitive(False)
			self.entryGenre.set_sensitive(False)

	def show(self):
		self.labelAlbum.show()
		self.labelArtist.show()
		self.labelYear.show()
		self.labelGenre.show()
		self.entryAlbum.show()
		self.entryArtist.show()
		self.entryYear.show()
		self.entryGenre.show()

	def hide(self):
		self.labelAlbum.hide()
		self.labelArtist.hide()
		self.labelYear.hide()
		self.labelGenre.hide()
		self.entryAlbum.hide()
		self.entryArtist.hide()
		self.entryYear.hide()
		self.entryGenre.hide()


### Main ###
if __name__ == "__main__" :

	print "\n" + "#" * (len(NAME) + len(VERSION) + len("version") + 10)
	print "### %s version %s ###"%(NAME, VERSION)
	print "#" * (len(NAME) + len(VERSION) + len("version") + 10)
	print "\n%s" %(COMMENTS)
	print "%s\n" %(COPYRIGHT)
	print "LICENCE INFORMATION\n"
	print "%s\n" %(LICENSE)

	gobject.threads_init()
	xaudiocopy = classXAudioCopy() # Crea l'oggetto di classe classXAudioCopy
	xaudiocopy.main() # Metodo main che attiva la finestra principale
