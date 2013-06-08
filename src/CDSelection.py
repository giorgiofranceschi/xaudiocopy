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

from Preferences import *
from WarningDialog import *
from CDDBReader import *
from MBReader import *
from CDDBDialog import *
from MBDialog import *


### Classe che gestisce l'apertura dei CD e il reperimento dei tag da MusicBrainz o da FreeDB ###
class CDSelection:

	# Costruttore della classe
	def __init__(self, main_window):
		
		self.main_window = main_window		
		self.CDdata = None
		self.error = None

		# Prova con MusicBrainz
		try:
			self.audioCD = MBReader()
		except:
			raise
		
		#try:
		#	self.audioCD = CDDBReader()
		#except: raise

	def select_CD_from_MB(self):

		tags_list = []
		if self.audioCD.is_audio_cd:
			try:
				MB_releases = self.audioCD.get_MB_releases()
			except:
				self.error = self.audioCD.error
				print "Errore. ", self.error
				numerr, errmsg, err = self.audioCD.error
				# Errore di rete
				if numerr == 402:
					msg = "No connection to the internet is current available or no server response..."
					self.dlg = WarningDialog(self.main_window, 
						NAME + " - Warning", msg)
					return
				else:
					# Disco non trovato
					if numerr == 404:
						msg = "Disc not found in the MusicBrainz's data base. Try with FreeDB..."
					# musicbrainzngs non disponibile, user agent error
					elif numerr in [7, 100, 101, 400, 401]:
						msg = errmsg + " Try with FreeDB..."
					else:
						msg = "MusicBrainz error"
						raise
					self.dlg = WarningDialog(self.main_window, 
						NAME + " - Warning", msg)

					# Se non funziona con MusicBrainz prova con FreeDB
					try:
						self.audioCD = CDDBReader()
						tags_list_CDDB = self.select_CD_from_CDDB()
						return tags_list_CDDB
					except:
						raise

			if MB_releases == None:				
				for i in range(self.audioCD.get_num_tracks()):
					n = "%.02d" %(i + 1)					
					tags = {
						"n" : i + 1,
						"uri" : "cdda://" + n,
						"track-number" : n,
						"title" : "Track " + n,
						"filename" : "Track " + n,
						"album": "Unknown album",
						"artist": "Unknown artist",
						"year": "Year",
						"genre": "Unknown genre",
						}
					tags_list.append(tags)
			else:
				self.MBDialog = MBDialog(self.main_window, MB_releases)

				if self.MBDialog.selected_cd:
					if self.MBDialog.selected_cd == "reject":
						for i in range(self.audioCD.get_num_tracks()):
							n = "%.02d" %(i + 1)
							tags = {
								"n" : i + 1,
								"uri" : "cdda://" + n,
								"track-number" : n,
								"title" : "Track " + n,
								"filename" : "Track " + n,
								"album": "Unknown album",
								"artist": "Unknown artist",
								"year": "Year",
								"genre": "Unknown genre",
								}
							tags_list.append(tags)
					else:
						selected_cd = int(self.MBDialog.selected_cd)
						tracks = self.audioCD.get_MB_tracks_from_release(MB_releases[selected_cd])

						for song in tracks:
							tags = {
								"n" : song["track-number"],
								"uri" : "cdda://" + str("%.02d" %(song["track-number"])),
								"track-number" : "%.02d" %(song["track-number"]),
								"title" : song["title"],
								"filename" : "Track " + str("%.02d" %(song["track-number"])),
								"album": song["album"],
								"artist": song["artist"],
								"year": song["release"]["date"][:4],
								"genre": "",
								}
							tags_list.append(tags)
				else:
					return
		else:
			self.audioCD = None
		print
		print "TAG LIST: ", tags_list
		print
		return tags_list



	def select_CD_from_CDDB(self):

		tags_list = []
		if self.audioCD.is_audio_cd:
			if self.audioCD.query_status == 409:				
				for i in range(self.audioCD.disc_id[1]):
					n = "%.02d" %(i + 1)					
					tags = {
						"n" : n,
						"uri" : "cdda://" + n,
						"track-number" : n,
						"title" : "Track " + n,
						"filename" : "Track " + n,
						"album": "Unknown album",
						"artist": "Unknown artist",
						"year": "Year",
						"genre": "Unknown genre",
						}
					tags_list.append(tags)
			else:
				if not type(self.audioCD.query_info).__name__ == "list":
					print "NON E' UNA LISTA"
					self.audioCD.query_info = [self.audioCD.query_info]
					print self.audioCD.query_info
				else:
					print "E'UNA LISTA"
				cds = []
				for cd in self.audioCD.query_info:
					cds.append([cd["disc_id"], cd["category"], cd["title"]])

				self.CDDBDialog = CDDBDialog(self.main_window, cds)

				if self.CDDBDialog.selected_cd:
					if self.CDDBDialog.selected_cd == "reject":
						for i in range(self.audioCD.disc_id[1]):
							n = "%.02d" %(i + 1)
							tags = {
								"n" : n,
								"uri" : "cdda://" + n,
								"track-number" : n,
								"title" : "Track " + n,
								"filename" : "Track " + n,
								"album": "Unknown album",
								"artist": "Unknown artist",
								"year": "Year",
								"genre": "Unknown genre",
								}
							tags_list.append(tags)
					else:
						selected_cd = int(self.CDDBDialog.selected_cd)
						self.audioCD.get_CDDB_tag(
								self.audioCD.query_status, 
								self.audioCD.query_info[selected_cd])

						for song in self.audioCD.song_list:
							tags = {
								"n" : song["track_number"],
								"uri" : "cdda://" + str("%.02d" %(song["track_number"])),
								"track-number" : "%.02d" %(song["track_number"]),
								"title" : song["title"],
								"filename" : "Track " + str("%.02d" %(song["track_number"])),
								"album": self.audioCD.album,
								"artist": self.audioCD.artist,
								"year": self.audioCD.year,
								"genre": self.audioCD.cddb_genre
								}
							tags_list.append(tags)
				else:
					return
		else:
			self.audioCD = None
		print
		print "TAG LIST: ", tags_list
		print
		return tags_list


