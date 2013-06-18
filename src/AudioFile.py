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

import os, string, re, wave, mimetypes, time

try:
	import gobject
	import pygst
	pygst.require("0.10")
	import gst
except:
	print("Gstreamer not available")
	sys.exit(1)

try:
	from mutagen.oggvorbis import OggVorbis
	from mutagen.flac import FLAC
	from mutagen.flac import Picture as FlacPicture
	from mutagen import id3
	from mutagen.id3 import ID3NoHeaderError
	from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TALB, TDRC, TCON, COMM, TPE2, TCOM, TPOS, APIC
	MUTAGEN = True
except:
	print ("mutagen not available")
	MUTAGEN = False

from TagFinder import *
from TypeFinder import *
from InfoFinder import *

# Estensioni valide
fileext = (".mp3", ".ogg", ".oga",".m4a", ".wav", ".aac", ".flac", ".ac3", ".ape", ".cda")

# MIME type dei formati audio validi
MIME_WHITE_LIST = (
	"audio/",
	"audio/x-wav",
	"audio/x-mpg",
	"audio/mpeg",
	"audio/ogg",
	"audio/flac",
	"audio/x-raw-int",
	"video/",
	"video/x-matroska",
	"video/x-msvideo",
	"video/mp4"
	"application/ogg",
	"application/x-id3",
	"application/x-ape",
	"application/vnd.rn-realmedia",
	"application/x-pn-realaudio",
	"application/x-shockwave-flash",
	"application/x-3gp",
)

# Elenco delle chiavi per il dizionario dei tag
TAGS_KEY = [
	"track_number",
	"title",
	"artist",
	"album",
	"year",
	"genre",
	"comment",
	"album_artist",
	"composer",
	"track_count",
	"disc_number",
	"cover",
	]


### Classe per gestire un file audio ###
class AudioFile:

	# Costruttore della classe
	# Inizializza gli attributi passati come parametro
	# alla creazione dell'istanza
	def __init__(self, uri, pointer=None):

		print "\n==== Istanza di AudioFile ====\n"

		# Puntatore esterno
		self.pointer = pointer

		#Indirizzo da usare per la riproduzione ('gstreamer')
		self.__uri = uri

		# Nome del file con o senza path e path derivati dall'uri
		(self.__folderuri, self.__filename) = os.path.split(self.__uri)
		if self.__folderuri == "cdda:":
			self.__foldername = "Audio CD"
			self.__filepath = self.__uri
		elif ("cdda:" in self.__folderuri) and self.__filename.endswith(".wav"):
			self.__folderuri = "cdda:"
			res = re.compile('\d+').findall(self.__filename)
			self.__uri = self.__folderuri + "//" + "%.02d" % (int(res[0]))
			self.__foldername = "Audio CD"
			self.__filename = "Track " + "%.02d" % (int(res[0])) + ".wav"
			self.__filepath = self.__uri
		elif self.__folderuri.startswith("file://"):
			self.__foldername = self.__folderuri[7:]
			self.__filepath = self.__foldername + "/" + self.__filename
		else:
			self.__foldername = self.__folderuri
			self.__filepath = self.__uri

		print "Uri: ", self.__uri
		print "Folder Uri: ", self.__folderuri
		print "Folder name: ", self.__foldername
		print "File name: ", self.__filename
		print "File path: ", self.__filepath

		# Inizializza i tag principali
		self.__tags_dict = {
			"track_number" : "",
			"title" : "",
			"artist" : "",
			"album" : "",
			"year" : "",
			"genre" : "",
			"comment" : "",
			"album_artist" : "",
			"composer" : "",
			"track_count": "",
			"disc_number" : "",
			"cover" : None,
			}

		# Inizializza altri attributi
		self.__filesize = None
		# Durata in secondi (float)
		self.__duration = None
		# Durata come stringa "h:mm:ss,mil"
		self.__duration_mm_ss = None
		# Inizio e fine in un CD
		self.__start_time = None
		self.__end_time = None
		# Mime type
		self.__mime_type = None
		# Numero di canali
		self.__n_channels = None
		# Byte per campione
		self.__sampwidth_B = None
		# Bit per campione
		self.__sampwidth_b = None
		# Frequenza di campionamento
		self.__framerate = None
		# Numero di campioni
		self.__n_frames = None
		# Tipo di compressione (none per i file wav)
		self.__comp_type = None
		# Tipo ricavato con gstreamer
		self.__gst_type = None
		# Dizionario con i tag ricavati con gstreamer
		self.__gst_tags = None
		# Formato del contenitore (es. ogg)
		self.__container_format = None
		# Codec audio (es. H.264/AVC Video)
		self.__audio_codec = None
		# Codec video (es. vorbis)
		self.__video_codec = None
		# Bitrate file compressi
		self.__bitrate = None
		# Bitrate nominale file compressi (Vorbis comment)
		self.__nominal_bitrate = None
		# Stere o join stereo
		self.__channel_mode = None
		# CRC
		self.__has_crc = None
		# Encoder e versione
		self.__encoder = None
		self.__encoder_version = None
		self.__private_frame = None
		# Flac
		self.__extended_comment = None

		# Dimensioni del file
		if os.path.exists(self.__filepath):
			self.__filesize = os.stat(self.__filepath).st_size

		# Trova il mimetype del file (usa il modulo "mimetypes")
		# Non funziona con i CD
		self.__mime_type = mimetypes.guess_type(self.__uri)[0]
		print "Mime type: ", self.__mime_type
		# Dovrebbero già essere stati filtrati in sede di apertura,
		# ma è meglio verificare
		if str(self.__mime_type) in MIME_WHITE_LIST:
			print "Mime type valido"
		else:
			print "Mime type non valido"

		# Trova il tipo di file con gstreamer
		if "cdda:" in self.__folderuri:
			self.__gst_type = "audio/x-raw-int"
		else:
			typeFinder = TypeFinder(self.__uri)
			self.__gst_type = typeFinder.get_type()

		# Cerca i tag nel file con gst
		tagFinder = TagFinder(self.__uri)
		self.__gst_tags = tagFinder.get_tags()

		# Ricava la durata del brano in secondi
		self.__duration = tagFinder.get_duration()

		#Inizializza i dati audio SOLO per file wav (usa il modulo "wave")
		if self.__mime_type == "audio/x-wav":
			w = wave.open(self.__filepath)
			self.__n_channels = w.getnchannels()
			self.__sampwidth_B = w.getsampwidth()
			self.__sampwidth_b = self.__sampwidth_B * 8
			self.__framerate = w.getframerate()
			self.__n_frames = w.getnframes()
			w.close()
		else:
			infoFinder = InfoFinder(self.__uri, self.__gst_type)
			info = infoFinder.get_info()
			self.__n_channels = info["n_channels"]
			self.__sampwidth_B = info["sampwidth_B"]
			self.__sampwidth_b = info["sampwidth_b"]
			self.__framerate = info["framerate"]
			self.__n_frames = info["n_frames"]

		print "n_channels: ", self.__n_channels
		print "sampwidth_B: ",self.__sampwidth_B
		print "sampwidth_b: ", self.__sampwidth_b
		print "framerate: ", self.__framerate
		print "n_frames: ", self.__n_frames

		# Se gstreamer non è riuscito a calcolare la durata del brano
		if self.__duration == None:
			if self.__mime_type == "audio/x-wav":
			# Altrimenti prova a calcolare la durata per i file wav
				size = os.stat(self.__filepath + "/" + self.__filepath).st_size
				if self.__comp_type == "NONE":
					self.__duration = float(float(self.__n_frames)/float(self.__framerate))
					print "Duration from size: ", self.__duration

		if not (self.__duration == None):
			self.__duration_h = int(self.__duration / 3600)
			self.__duration_m = int(self.__duration / 60) - self.__duration_h * 60
			self.__duration_s = int(self.__duration) - self.__duration_m * 60 - self.__duration_h * 3600
			self.__duration_mil = int(round(1000 * (self.__duration - int(self.__duration))))
			mm_ss = str(self.__duration_m) + ":" + '%(#)02d' %{"#": self.__duration_s} + "." + '%(#)03d' %{"#": self.__duration_mil}
			if not (self.__duration_h == 0):
				self.__duration_mm_ss = str(self.__duration_h) + "h " + mm_ss
			else:
				self.__duration_mm_ss = mm_ss
			print "duration_mm_ss: ", self.__duration_mm_ss

		# Riempie i tag
		try:
			self.__tags_dict["track_number"] = self.__gst_tags["track-number"]
		except KeyError:
			# Se il tag "track-number" passato da gst è vuoto, cerca di
			# assegnare il numero di traccia se presente nel titolo come "nn" o "n".
			# Utile se i file sono tracce di CD o file nominati come
			# "Track nn.wav" oppure "Track nn.cda" oppure
			# "nn - Artist - Title.*" o simili.
			for ext in fileext:
				if self.__filename.endswith(ext):
					print "self.__filename[-4:]: ", self.__filename[-4:]
					if re.compile('\d+' + ext).findall(self.__filepath):
						res = re.compile('\d+' + ext).findall(self.__filepath)
						print "res: ", res
						for e in res:
							print "e: ", e
							res = re.compile('\d+').findall(e)
							for n in res:
								print "n: ", n
								self.__tags_dict["track_number"] = n
				elif re.compile('\d+').findall(self.__filename[0:2]):
					res = re.compile('\d+').findall(self.__filename[0:2])
					self.__tags_dict["track_number"] = res[0]
		try:
			# Mette uno zero davanti al numero se manca
			self.__tags_dict["track_number"] = "%.02d" %(self.__tags_dict["track_number"])
		except:
			pass
		try:
			self.__tags_dict["title"] = self.__gst_tags["title"]
		except KeyError: pass
		try:
			self.__tags_dict["artist"] = self.__gst_tags["artist"]
		except KeyError: pass
		try:
			self.__tags_dict["album"] = self.__gst_tags["album"]
		except KeyError: pass
		try:
			self.__tags_dict["year"] = self.__gst_tags["date"].year
		except KeyError: pass
		try:
			self.__tags_dict["genre"] = self.__gst_tags["genre"]
		except KeyError: pass
		try:
			self.__tags_dict["comment"] = self.__gst_tags["comment"]
		except KeyError: pass
		try:
			self.__tags_dict["album_artist"] = self.__gst_tags["album-artist"]
		except KeyError: pass
		try:
			self.__tags_dict["composer"] = self.__gst_tags["composer"]
		except KeyError: pass
		try:
			self.__tags_dict["track_count"] = str(self.__gst_tags["track-count"])
		except KeyError: pass
		try:
			self.__tags_dict["disc_number"] = self.__gst_tags["album-disc-number"]
		except KeyError: pass
		# Cover per mp3
		try:
			self.__tags_dict["cover"] = self.__gst_tags["image"]
		except KeyError: pass
		# Cover per ogg
		try:
			self.__tags_dict["cover"] = self.__gst_tags["preview-image"]
		except KeyError: pass

		# Altre proprietà del brano da gstreamer
		try:
			self.__container_format = self.__gst_tags["container-format"]
		except KeyError: pass
		try:
			self.__audio_codec = self.__gst_tags["audio-codec"]
		except KeyError: pass
		try:
			self.__video_codec = self.__gst_tags["video-codec"]
		except KeyError: pass
		try:
			self.__bitrate = self.__gst_tags["bitrate"]
		except KeyError: pass
		try:
			self.__nominal_bitrate = self.__gst_tags["nominal-bitrate"]
		except KeyError: pass
		try:
			self.__channel_mode = self.__gst_tags["channel-mode"]
		except KeyError: pass
		try:
			self.__has_crc = self.__gst_tags["has-crc"]
		except KeyError: pass
		try:
			self.__encoder = self.__gst_tags["encoder"]
		except KeyError: pass
		try:
			self.__encoder_version = self.__gst_tags["encoder-version"]
		except KeyError: pass
		try:
			self.__private_frame = self.__gst_tags["private-id3v2-frame"]
		except KeyError: pass
		try:
			self.__extended_comment = self.__gst_tags["extended-comment"]
		except KeyError: pass


	# Scrive un tag come elemento del dizionario
	def set_tag(self, key, value):

		try:
			if key in TAGS_KEY:
				self.__tags_dict[key] = value
			else:
				raise KeyError
		except KeyError:
			print "'%s' is an invalid tag." %(key)

	# Restituisce un tag come elemento del dizionario
	def get_tag(self, key):

		try:
			return self.__tags_dict[key]
		except KeyError:
			print "'%s' is not a valid tag." %(key)

	# Scrive i tag passati come dizionario
	def set_tags_as_dict(self, tags_dict):

		try:
			for key in tags_dict:
				if key in TAGS_KEY:
					self.__tags_dict[key] = tags_dict[key]
				else:
					raise KeyError
		except KeyError:
			print "'%s' contains invalid tags." %(tags_dict)

	# Restituisce i tag come dizionario
	def get_tags_as_dict(self):
		return self.__tags_dict

	# Funzioni get/set per i vari attributi
	def get_uri(self):
		if self.__uri:
			return self.__uri

	def set_filename(self, filename):
		self.__filename = filename

	def get_filename(self):
		return self.__filename

	def set_filepath(self, filepath):
		self.__filepath = filepath

	def get_filepath(self):
		return self.__filepath

	def get_foldername(self):
		return self.__foldername

	def get_filesize(self):
		return self.__filesize

	def get_duration(self):
		return self.__duration

	def get_duration_mm_ss(self):
		return self.__duration_mm_ss

	def get_start_time(self):
		return self.__start_time

	def get_end_time(self):
		return self.__end_time

	def get_mime_type(self):
		return self.__mime_type

	def get_num_channels(self):
		return self.__n_channels

	def get_sampwidth_B(self):
		return self.__sampwidth_B

	def get_sampwidth_b(self):
		return self.__sampwidth_b

	def get_framerate(self):
		return self.__framerate

	def get_num_frame(self):
		return self.__n_frames

	def get_type(self):
		return self.__gst_type

	def get_container(self):
		return self.__container_format

	def get_audio_codec(self):
		return self.__audio_codec

	def get_video_codec(self):
		return self.__video_codec

	def get_bitrate(self):
		return self.__bitrate

	def get_channel_mode(self):
		return self.__channel_mode

	def get_has_crc(self):
		return self.__has_crc

	def get_encoder(self):
		return self.__encoder

	def get_extended_comment(self):
		return self.__extended_comment

	def get_private_frame(self):
		return self.__private_frame

	# Funzione che scrive i tag
	# ID3v1 per MP3, Vorbis Comment per Vorbis, FLAC Comment per FLAC
	# TODO: aggiungere APEv2, ecc.
	# TODO: aggiungere copertine
	# TODO: aggiungere metodo per ID3v1 senza mutagen
	def write_metadata(self):
		if MUTAGEN:
			if "MP3" in self.__audio_codec:
				# Prima scrive i tag v1 e v2, poi rimuove i v2
				self.write_ID3v2()
				self.remove_ID3v2()
			elif "ogg" in self.__gst_type:
				tags = OggVorbis(self.__filepath)
				tags["tracknumber"] = unicode(int(self.get_tag("track_number")))
				tags["title"] = unicode(self.get_tag("title"))
				tags["artist"] = unicode(self.get_tag("artist"))
				tags["album"] = unicode(self.get_tag("album"))
				tags["date"] = unicode(self.get_tag("year"))
				tags["genre"] = unicode(self.get_tag("genre"))
				tags["comment"] = unicode(self.get_tag("comment"))
				tags["albumartist"] = unicode(self.get_tag("album_artist"))
				tags["composer"] = unicode(self.get_tag("composer"))
				tags["discnumber"] = unicode(self.get_tag("disc_number"))
				# TODO: Come salvare la copertina in un file Vorbis???
				# Questo non funziona:	
				#tags["coverart"] = [self.get_tag("cover")]
				
				tags.save(self.__filepath)
				
			elif "flac" in self.__gst_type:
				tags = FLAC(self.__filepath)
				tags["tracknumber"] = unicode(int(self.get_tag("track_number")))
				tags["title"] = unicode(self.get_tag("title"))
				tags["artist"] = unicode(self.get_tag("artist"))
				tags["album"] = unicode(self.get_tag("album"))
				tags["date"] = unicode(self.get_tag("year"))
				tags["genre"] = unicode(self.get_tag("genre"))
				tags["comment"] = unicode(self.get_tag("comment"))
				tags["albumartist"] = unicode(self.get_tag("album_artist"))
				tags["composer"] = unicode(self.get_tag("composer"))
				tags["discnumber"] = unicode(self.get_tag("disc_number"))
				# TODO: Come salvare la copertina in un file FLAC???
				# Questo non funziona:	
				#tags.add_picture(self.get_tag("cover"))
				
				tags.save(self.__filepath)

	# Funzione che scrive i tag ID3v2.4 per gli MP3
	# TODO: opzione per distinguere tra v2.3 e v2.4
	def write_ID3v2(self):
		if MUTAGEN:
			if "MP3" in self.__audio_codec:
				try:
					tags = ID3(self.__filepath)
				except ID3NoHeaderError:
					tags = ID3()

				# Track number
				tags["TRCK"] = TRCK(encoding=3, text=unicode(self.get_tag("track_number")))
				# Title
				tags["TIT2"] = TIT2(encoding=3, text=unicode(self.get_tag("title")))
				# Artist
				tags["TPE1"] = TPE1(encoding=3, text=unicode(self.get_tag("artist")))
				# Album
				tags["TALB"] = TALB(encoding=3, text=unicode(self.get_tag("album")))
				# Year
				tags["TDRC"] = TDRC(encoding=3, text=unicode(self.get_tag("year")))
				# Genre
				tags["TCON"] = TCON(encoding=3, text=unicode(self.get_tag("genre")))
				# Comment
				tags["COMM"] = COMM(encoding=3, lang=u'eng', desc='desc', text=unicode(self.get_tag("comment")))
				#tags["COMM"] = COMM(encoding=3, text=unicode(self.get_tag("comment")))
				# Album artist
				tags["TPE2"] = TPE2(encoding=3, text=unicode(self.get_tag("album_artist")))
				# Composer 
				tags["TCOM"] = TCOM(encoding=3, text=unicode(self.get_tag("composer")))
				# Disc number
				tags["TPOS"] = TPOS(encoding=3, text=unicode(self.get_tag("disc_number")))
				# Cover
				tags["APIC"] = APIC(3, 'image/jpeg', 3, 'Front cover', self.get_tag("cover"))
				
				#tags.update_to_v24()
				tags.save(self.__filepath, v1=2)

	# Rimuove tutti i tag
	# TODO: metodo senza mutagen
	def remove_metadata(self):
		if MUTAGEN:
			if "MP3" in self.__audio_codec:
				try:
					tags = ID3(self.__filepath)
				except ID3NoHeaderError:
					return
				tags.delete(self.__filepath, delete_v1=True, delete_v2=True)
			elif "ogg" in self.__gst_type:
				tags = OggVorbis(self.__filepath)
				tags.delete()
			elif "flac" in self.__gst_type:
				tags = FLAC(self.__filepath)
				tags.delete()

	# Rimuove gli ID3v2 agli MP3
	def remove_ID3v2(self):
		if MUTAGEN:
			if "MP3" in self.__audio_codec:
				try:
					tags = ID3(self.__filepath)
				except ID3NoHeaderError:
					return
				tags.delete(self.__filepath, delete_v1=False, delete_v2=True)
	
	# Rimuove gli ID3v1 agli MP3
	def remove_ID3v1(self):
		if MUTAGEN:
			if "MP3" in self.__audio_codec:
				try:
					tags = ID3(self.__filepath)
				except ID3NoHeaderError:
					return
				tags.delete(self.__filepath, delete_v1=True, delete_v2=False)

