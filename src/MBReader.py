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

import os, string, re, hashlib, base64, urllib, urlparse
# Importa la libreria cdrom.so distribuita con python-cddb (CDDB.py e DiscID.py)
import cdrom


### Classe per ottenere i tag del CD da MusicBrainz (http://www.musicbrainz.org/)
class MBReader():
	
	# Costruttore della classe
	def __init__(self):
	
		self.error = None
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
			self.__MB_full_toc = [first, last, frames[-1]] + frames[:-1]
			# Numero di tracce
			self.num_tracks = last
		cdaudio.close()

	# Restituisce la TOC del disco
	def get_MB_full_toc(self):
		return self.__MB_full_toc
		
	# Determina il Disc ID di MusicBrainz a partire dalla TOC
	#TODO - Dischi ibridi e multisessione
	def get_MB_disc_id(self):

		if self.is_audio_cd:
			sha = hashlib.sha1()
			# Numero della prima traccia
			sha.update("%02X" % self.__MB_full_toc [0])
			# Numero della seconda traccia
			sha.update("%02X" % self.__MB_full_toc [1])
			# Settore finale
			sha.update("%08X" % self.__MB_full_toc [2])
			# Altri settori
			for i in range(1, 100):
				try:
					offset = self.__MB_full_toc[2 + i]
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
			return None

	# Restituisce le varie release di uno stesso disco per lo stesso Disc ID
	def get_MB_releases(self):

		if self.is_audio_cd:
			try:
				from musicbrainzngs import musicbrainz, ResponseError, NetworkError
			except ImportError as imperr:
				print "musicbrainzngs not available"
				self.error = ("100", "Import error", imperr)
				raise

			MBhost = "mm.musicbrainz.org"
			disc_id = self.get_MB_disc_id()
        		query = urllib.urlencode({
            			"id": disc_id,
            			"toc": " ".join([str(value) for value in self.__MB_full_toc]),
            			"tracks": self.num_tracks,
       				})
			print urlparse.urlunparse(("http", MBhost, "/bare/cdlookup.html", "", query, ""))

			try:
				musicbrainz.set_useragent("xaudiocopy", "0.02.1")
			except:
				self.error("101", "User agent error", "")
				raise
			# Scarica le release del disco in base al Disc ID
			try:
				releases = musicbrainz.get_releases_by_discid(disc_id, 
					includes=["artists", "recordings", "release-groups", "labels"])
			except ResponseError as reserr:
				if reserr.cause.code == 404:
					print "Disc not found", reserr
					self.error = (reserr.cause.code, "Disc not found", reserr)
					raise
				else:
					print "Bad response from the MB server", reserr
					self.error = (reserr.cause.code, "Bad response from the MB server", reserr)
					raise
			except NetworkError as neterr:
				print "Network connection error", neterr
				self.error = ("402", "Network connection error", neterr)
				raise
				""" Eccezione non gestita nella versione 0.2 di musicbrainzngs
			except AuthenticationError as auterr:
				print "Receved a HTTP 401 response while accessing a protected resource"
				self.error = (auterr, "Receved a HTTP 401 response while accessing a protected resource", auterr)		
				raise"""
			i = 0
			# Lista che contiene tutte le release
			MB_releases = []

			for release in releases['disc']['release-list']:
				#res = musicbrainz.get_release_by_id(release['id'],
            			#	includes=["artists", "artist-credits", "recordings", "discids"])
				
				# Dizionario che contiene le informazioni di ogni release
				MB_release = {
					"artist" : "",
					"album-title" : "",
					"album-id" : "",
					"barcode" : "",
					"catalog" : [],
					"packaging" : "",
					"date" : "",
					"country" : "",
					"disc-id" : disc_id,
				}

				# Artista
				if release.get("artist-credit-phrase"):
					MB_release["artist"] = release["artist-credit-phrase"]
				# Titolo
				if release.get("title"):
					MB_release["album-title"] = release["title"]
				# MusicBrainz ID
				if release.get("id"):
					MB_release["album-id"] = release["id"]
				# Codice a barre EAN/UPC
				if release.get("barcode"):
					MB_release["barcode"] = release["barcode"]
				# Label e numero di catalogo (dizionari in una lista)
				if release.get("label-info-list"):
					for info in release["label-info-list"]:
						catalog = {"label" : "", "catalog-number" : ""}
						if info.get("label"):
							catalog["label"] = info["label"]["name"]
						if info.get("catalog-number"):
							catalog["catalog-number"] = info["catalog-number"]
						MB_release["catalog"].append(catalog)
				else:
					MB_release["catalog"].append({"label" : "", "catalog-number" : ""})
				# Packaging
				if release.get("packaging"):
					MB_release["packaging"] = release["packaging"]
				# Data
				if release.get("date"):
					MB_release["date"] = release["date"]
				# Nazione
				if release.get("country"):
					MB_release["country"] = release["country"]

				# Aggiunge la release alla lista
				MB_releases.append(MB_release)

			# Stampa di prova
			for rel in MB_releases:
				i+=1
				print
				print "RELEASE %d" % i
				keys = rel.keys()
				for k in keys:
					print '%s = %s' % (k,rel[k])
				 				
			return MB_releases
		else:
			return None

	# Restituisce le tracce del disco in base all'ID della release
	def get_MB_tracks_from_release(self, MB_release):
			
		try:
			from musicbrainzngs import musicbrainz, ResponseError, NetworkError
		except ImportError as imperr:
			print "musicbrainzngs not available"
			self.error = ("100", "Import error", imperr)
			raise
			
		try:
			musicbrainz.set_useragent("xaudiocopy", "0.02.1")
		except:
			self.error("101", "User agent error", "")
			raise
		# Scarica la release del disco in base all'ID
		try:
			release = musicbrainz.get_release_by_id(MB_release["album-id"], 
				includes=["artists", "recordings", "release-groups", "labels"])
		except ResponseError as reserr:
			if reserr.cause.code == 404:
				print "Disc not found", reserr
				self.error = (reserr.cause.code, "Disc not found", reserr)
				raise
			else:
				print "Bad response from the MB server", reserr
				self.error = (reserr.cause.code, "Bad response from the MB server", reserr)
				raise
		except NetworkError as neterr:
			print "Network connection error", neterr
			self.error = ("402", "Network connection error", neterr)
			raise
			""" Eccezione non gestita nella versione 0.2 di musicbrainzngs
		except AuthenticationError as auterr:
			print "Receved a HTTP 401 response while accessing a protected resource"
			self.error = (auterr, "Receved a HTTP 401 response while accessing a protected resource", auterr)		
			raise"""
		print release
		
		# La release è un dict con dentro un altro dict "release"
		# TODO Esistono release che hanno altri elementi?
		release = release["release"]

		tracks_list = []
		# Per ogni disco presente (se presente) trova quello giusto
		if release["id"] == MB_release["album-id"]:
			for medium in release["medium-list"]:
				for track in medium["track-list"]:
					# Dizionario con i tag della canzone
					self.track = {
						"track-number" : int(track["position"]),
						"title" : track["recording"]["title"],
						"artist" : release["artist-credit"][0]["artist"]["name"],
						"artist-sort-name" : release["artist-credit"][0]["artist"]["sort-name"],
						"album" : release["title"],
						"recording-id" : track["recording"]["id"],
						"album-id" : release["id"],
						"artist-id" : release["artist-credit"][0]["artist"]["id"],
						#"lenght" : track["recording"]["lenght"],
						"release" : MB_release,
						}
					tracks_list.append(self.track)
				
				# Stampa di prova
				i = 0
				for t in tracks_list:
					i+=1
					print
					print "TRACK %d" % i
					keys = t.keys()
					for k in keys:
						print '%s = %s' % (k,t[k])



### Test ###
"""cd = MBReader()
try:
	releases = cd.get_MB_releases()
	print
	print "selected release: ", releases[0]["album-id"]
	print
	release = cd.get_MB_tracks_from_release(releases[0])
except:
	print cd.error
	raise
"""
