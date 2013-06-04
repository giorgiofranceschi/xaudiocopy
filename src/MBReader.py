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

import os, string, re, hashlib, base64
# Importa la libreria cdrom.so distribuita con python-cddb (CDDB.py e DiscID.py)
import cdrom


### Classe per ottenere i tag del CD da MusicBrainz (http://www.musicbrainz.org/)
class MBReader():
	
	# Costruttore della classe
	def __init__(self):
	
		cdaudio = cdrom.open()
		print "CD: ", cdaudio

		try:
			first, last = cdrom.toc_header(cdaudio)
			print "toc_header: ", first, last
			self.is_audio_cd = True
		except:
			print "No CD"
			disc_id = None
			self.is_audio_cd = False
			raise

		# Legge la TOC del disco
		if self.is_audio_cd:
			frames = []
			for i in range(first, last + 1):
				print cdrom.toc_entry(cdaudio, i)
				(m, s, frame) = cdrom.toc_entry(cdaudio, i)
				frames.append(m*60*75 + s*75 + frame)
			m, s, frame = cdrom.leadout(cdaudio)
			frames.append(m*60*75 + s*75 + frame)
			
			# Ordina i dati della TOC nel formato adatto a MusicBrainz
			self.MB_full_toc = [first, last, frames[-1]] + frames[:-1]
		cdaudio.close()
		
	# Determina il Disc ID di MusicBrainz a partire dalla TOC
	#TODO - Dischi ibridi e multisessione
	def get_MB_disc_id(self):

		if self.is_audio_cd:
			sha = hashlib.sha1()
			# Numero della prima traccia
			sha.update("%02X" % self.MB_full_toc [0])
			# Numero della seconda traccia
			sha.update("%02X" % self.MB_full_toc [1])
			# Settore finale
			sha.update("%08X" % self.MB_full_toc [2])
			# Altri settori
			for i in range(1, 100):
				try:
					offset = self.MB_full_toc[2 + i]
				except IndexError:
					offset = 0
				sha.update("%08X" % offset)

			digest = sha.digest()
			assert len(digest) == 20, "Digest should be 20 chars, not %d" % len(digest)
			MB_disc_id = base64.b64encode(digest, '._')
			MB_disc_id = "-".join(MB_disc_id.split("="))
			assert len(MB_disc_id) == 28, "MB_disc_id should be 28 characters, not %d" % len(result)
			print "MusicBrainz Disc ID: ", MB_disc_id
			return MB_disc_id
		else:
			return
		
	   
### Test ###
#MBdisciID = MBReader()
#MBdisciID.get_MB_disc_id()
