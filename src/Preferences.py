#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# X Audio Copy - GTK and GNOME application for ripping CD-Audio and encoding in lossy and lossless audio formats.
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
import ConfigParser

### Un po' di costanti ###

# About
ICON = "../data/xaudiocopy-monochrome.png"
NAME = "X Audio Copy"
VERSION = "0.02.1 alpha"
COMMENTS = "GTK and GNOME application for playing audio files, ripping CD-Audio and encoding in lossy and lossless audio formats."
COPYRIGHT_OWNER = "Giorgio Franceschi"
COPYRIGHT_YEAR = "2010-2013"
COPYRIGHT = "Copyright © " + "%s %s" % (COPYRIGHT_YEAR, COPYRIGHT_OWNER)
AUTHORS = [COPYRIGHT_OWNER]
TRANSLATORS = "The program has not yet been translated"

LICENSE = \
"""This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program (see COPYING); if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

# Percorso per salvare le preferenze
XACHOME = os.path.expandvars("$HOME") + "/.xaudiocopy" # Directory di salvataggio (dir nascosta dentro la HOME)
XACCONFIG = ".xaudiocopyconf" # File di configurazione
XACCONFIGPATH = XACHOME + "/" + XACCONFIG # Path completo del file di configurazione
DIRMUSIC = os.path.expandvars("$HOME") + "/Musica" # Directory di default per i file musicali. TODO: Rendere traducibile "/Musica"

# Impostazioni per il programma
GLADE_NAME = "xaudiocopy.glade"
GLADE = "@datadir@/xaudiocopy/" + GLADE_NAME

# Permette di lanciare il programma dalla cartella del codice sorgente
LOCAL_GLADE = "../data/" + GLADE_NAME
if os.path.exists(LOCAL_GLADE):
	GLADE = LOCAL_GLADE
else:
	GLADE = GLADE_NAME

# Titolo delle finestre
WINDOW_TITLE = "%s %s" % (NAME, VERSION)

# Individua il sistema operativo e esce se non trova Windows o *nix
OPSYS = None
if os.name == "nt":
	WINNT = True
	UNIX = False
	OPSYS = "Win"
elif os.name == "posix":
	WINNT = False
	UNIX = True
	OPSYS = "Unix"
else:
	md = gtk.MessageDialog(None,
		0, gtk.MESSAGE_WARNING,
		gtk.BUTTONS_CLOSE, (NAME + " non è compatibile con questo sistema operativo"))
	re = md.run()
	if re == gtk.RESPONSE_CLOSE:
		md.hide()
		md.destroy()
		sys.exit()

# Nome e estensione per i file da scegliere nella finestra
# di dialogo apertura file
FILE_PATTERN = (
		("MP3","*.mp3"),
		("Ogg Vorbis","*.ogg"),
		("iTunes AAC ","*.m4a"),
		("WAV","*.wav"),
		("AAC","*.aac"),
		("FLAC","*.flac"),
		("AC3","*.ac3"),
		("APE","*.ape"),
		("CD-Audio","*.cda"),
)

# Pattern per le sottodirectory
SUBFOLDERS_PATH = [("Artist-Album", "%a-%d"),
		("Artist - Album", "%a - %d"),
		("Artist - [Year] Album", "%a - [%y] %d"),
		("[Year] Artist - Album", "[%y] %a - %d"),
		("Artist/Album", "%a/%d"),
		("Artist/[Year] Album", "%a/[%y] %d"),
		("Artist/[Year] Artist - Album", "%a/[%y] %a - %d"),
		("Album", "%d"),
		("[Year] Album", "[%y] %d"),
		("Artist-Album/CD", "%a-%d/%s"),
		("Artist - Album/CD", "%a - %d/%s"),
		("Artist - [Year] Album/CD", "%a - [%y] %d/%s"),
		("[Year] Artist - Album/CD", "[%y] %a - %d/%s"),
		("Artist/Album/CD", "%a/%d/%s"),
		("Artist/[Year] Album/CD", "%a/[%y] %d/%s"),
		("Artist/[Year] Artist - Album/CD", "%a/[%y] %a - %d/%s"),
		("Album/CD", "%d/%s"),
		("[Year] Album/CD", "[%y] %d/%s"),
		]

# Pattern per i nomi dei file
FILENAME_PATTERN = [("Alternate filename pattern", ""),
		("Same as imput, but replacing the suffix", ""),
		("Same as imput, but with an additional suffix", ""),
		("Track number - Title", "%n - %t"),
		("Track number Title", "%n %t"),
		("Track number. Title", "%n. %t"),
		("Artist - Title", "%a - %t"),
		("Disc number.Track number - Title", "%s.%n - %t"),
		("Disc number.Track number Title", "%s.%n %t"),
		("Disc number.Track number. Title", "%s.%n. %t"),
		]

# Lista di percorsi dove trovare eseguibili
BIN_PATHS = os.path.expandvars("$PATH").split(":")

# Encoder interni richiesti (se presenti nei plug-in di gstreamer
REQ_INTERNAL_ENCODERS = [("Ogg Vorbis", "ogg"),
			("MP3", "mp3"),
			("FLAC lossless", "flac"),
			("WAV 16 bit PCM", "wav"),
			#("AAC", "m4a"),
			]
					
#TODO: Filtrare i codec presenti in gstreamer
INTERNAL_ENCODERS = REQ_INTERNAL_ENCODERS

# Encoder esterni richiesti
REQ_EXTERNAL_ENCODERS = [("Lame mp3 encoder", "lame"),
		("Ogg Vorbis encoder", "oggenc"),
		("Free Lossless Audio Codec", "flac"),
		]
# Encoder esterni disponibili
EXTERNAL_ENCODERS = []
EXTERNAL_ENCODERS_NOT_AVAILABLE = []
for bp in BIN_PATHS:
	for prog in REQ_EXTERNAL_ENCODERS:
		if os.path.exists(bp + "/" + prog[1]):
			EXTERNAL_ENCODERS.append(prog)
for prog in REQ_EXTERNAL_ENCODERS:
	if not prog in EXTERNAL_ENCODERS:
		EXTERNAL_ENCODERS_NOT_AVAILABLE.append(prog)
EXTERNAL_ENCODERS.insert(0, ("User defined encoder", "user"))

# Qualità per Vorbis
OGG_QUAL = [("Hightest", 10),
	("Very high", 9),
	("Standard high", 8),
	("Good", 7),
	("Medium", 6),
	("More than acceptable", 5),
	("Acceptable", 4),
	("Low", 3),
	("Very low", 2),
	("Lowest", 1),
	("No quality", 0),
	("Unqualified", -1),
	]

# Modalità cbr, abr o vbr per MP3
MP3_MODE = [("Constant bitrate", "CBR"),
	("Average bitrate", "ABR"),
	("Variable bitrate", "VBR"),
	]

# Bitrate per MP3 (per cbr e abr)
MP3_BITRATE = [8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]

# Qualità per MP3 (per vbr)
MP3_QUAL = [("Hightest", 0),
	("Very high", 1),
	("Standard high", 2),
	("Good", 3),
	("Medium", 4),
	("More than acceptable", 5),
	("Acceptable", 6),
	("Low", 7),
	("Very low", 8),
	("Lowest", 9),
	]

# Qualità per MP3
FLAC_QUAL = [("Fastest", 0),
	("Fast", 3),
	("Standard", 5),
	("High", 7),
	("Hightest", 8),
	]

# Valori per il ricampionamento
RESAMPLE_VALUE = [11025, 22050, 44100, 48000, 72000, 96000, 128000]

# Legenda per il pattern dei nomi dei file
INFO_PATTERN = """<i>track <b>n</b>umber</i>  (%n)
<i>track <b>t</b>itle</i>  (%t)
<i><b>a</b>rtist</i>  (%a)
<i>album/<b>d</b>isc title</i>  (%d)
<i><b>y</b>ear</i>  (%y)
<i>part of <b>s</b>et/disc number</i>  (%s)"""

# Funzione per i pattern
def expand_title(pattern, artist=None, album=None, year=None, track_number=None, title=None, disc_number=None, disc_number_str=None):
	if artist and len(artist) > 0:
		pattern = re.compile("%a").sub(artist, pattern)
	else:
		pattern = re.compile("%a").sub("", pattern)
	if album and len(album) > 0:
		pattern = re.compile("%d").sub(album, pattern)
	else:
		pattern = re.compile("%d").sub("", pattern)
	if year and len(str(year)) > 0:
		pattern = re.compile("%y").sub(str(year), pattern)
	else:
		pattern = re.compile("%y").sub("", pattern)
	if track_number and len(str(track_number)) > 0:
		pattern = re.compile("%n").sub(str("%(#)02d" %{"#": int(track_number)}), pattern)
	else:
		pattern = re.compile("%n").sub("", pattern)
	if title and len(title) > 0:
		pattern = re.compile("%t").sub(title, pattern)
	else:
		pattern = re.compile("%t").sub("", pattern)
	if disc_number and len(str(disc_number)) > 0:
		pattern = re.compile("%s").sub(str("%(#)1d" %{"#": int(disc_number)}), pattern)
	elif disc_number_str:
		pattern = re.compile("%s").sub("CD" + str("%(#)1d" %{"#": int(disc_number_str)}), pattern)
	else:
		pattern = re.compile("%s").sub("", pattern)
	return pattern

# Estensioni valide
# fileext = (".mp3", ".ogg", ".oga",".m4a", ".wav", ".aac", ".flac", ".ac3", ".ape", ".cda")

# Pattern per i nomi dei file
FILENAME2TAG_PATTERN = [("Alternate filename pattern", ""),
		("Track number - Title", "%n - %t"),
		("Track number Title", "%n %t"),
		("Track number. Title", "%n. %t"),
		("Artist - Title", "%a - %t"),
		("Disc.Track number - Title", "%s.%n - %t"),
		("Disc.Track number Title", "%s.%n %t"),
		("Disc.Track number. Title", "%s.%n. %t"),
		]


### Classe che utilizza ConfigParser per scrivere/leggere il file con le preferenze ###
class Preferences:

	def __init__(self, mainapp=None):

		# Opzioni di default
		# "0" per False; "1" per True
		self.default_prefs = {"settings" : {"last-used-folder": DIRMUSIC},
					"rip" : {"rip-compressed" : "0"},
					"folders" : {"save-in-home" : "0",
							"save-in-same-folder" : "0",
							"save-in-last-folder" : "1",
							"last-save-folder": DIRMUSIC,
							"alt-save-folder" : "",
							"select-path" : "0",
							"create-subfolders" : "0",
							"path-subfolder" : "Artist/[Year] Artist - Album"},
					"filename" : {"filename-pattern" : "Track number - Title",
							"alternate-filename-pattern" : "n - t",
							"replace-spaces-by-underscores" : "0",
							"write-ID3v1" : "1",
							"write-ID3v2" : "1",
							"playlist" : "1"},
					"converter" : {"save-all-tracks" : "1",
							"delete-original-files" : "0",
							"output-format" : "ogg",
							"vorbis-quality" : "6",
							"mp3-bitrate-mode" : "VBR",
							"mp3-bitrate" : "160",
							"mp3-quality" : "4",
							"flac-quality" : "5",
							"resample" : "0",
							"resample-freq" : "44100"},
					"external" : {"use-external-encoder" : "0",
							"external-encoder" : "oggenc",
							"lame-options" : "-V2",
							"vorbis-options" : "-q 6",
							"flac-options" : "-5",
							"user-defined-encoder-command" : "/usr/bin/oggenc -q 8"},
					"file2tag" : {"filename2tag-pattern" : "",
							"alternate-filename2tag-pattern" : "n - t"}
					}
	
		self.config_parser = ConfigParser.SafeConfigParser()

		# Verifica se esiste la directory di config del programma nella home
		# altrimenti la crea
		if not os.path.exists(XACHOME):
			os.mkdir(XACHOME)
		#	print "La direcotory", XACHOME, "è stata creata"
		#else:
		#	print "La direcotory", XACHOME, "esiste"

		# Verifica se esiste il file di configurazione
		# altrimenti lo crea e lo riempie con i valori di default
		for dirpath, dirnames, filenames in os.walk(XACHOME):
			# Verifica se esiste
			if not XACCONFIG in filenames:
				# Se non esiste apre un nuovo file vuoto
				pref_file = open(XACCONFIGPATH, "w")
				# Lo riempie con le opzioni di default
				for section in self.default_prefs:
					self.config_parser.add_section(section)
					for option in self.default_prefs[section]:
						self.config_parser.set(
								section,
								option,
								self.default_prefs[section][option])
				# Scrive il file
				self.config_parser.write(pref_file)
				# Chiude il file
				pref_file.close()
			#else:
			#	print "Il file", XACCONFIGPATH, "esiste"

		# Carica le opzioni
		self.config_parser.read(XACCONFIGPATH)

	# Scrive una opzione passata come argomento
	def set_option(self, option, value):

		pref_file = open(XACCONFIGPATH, "w")
		for section in self.config_parser.sections():
			if self.config_parser.has_option(section, option):
				self.config_parser.set(section, option,	value)
		# Scrive il file
		self.config_parser.write(pref_file)
		# Chiude il file
		pref_file.close()

	# Legge le opzioni
	def get_option(self, option):

		for section in self.config_parser.sections():
			if self.config_parser.has_option(section, option):
				return self.config_parser.get(section, option)
	
	def reset(self):
		if not os.path.exists(XACHOME):
			os.mkdir(XACHOME)
		# Verifica se esiste il file di configurazione
		# altrimenti lo crea e lo riempie con i valori di default
		for dirpath, dirnames, filenames in os.walk(XACHOME):
			# Verifica se esiste e lo cancella
			if XACCONFIG in filenames:
				os.remove(XACCONFIGPATH)
				self.__init__()

