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


import gobject, time, os, shlex, tempfile
import threading
import Queue

try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	print("Gstreamer not available")
try:
	import Image
	IMAGE = True
except:
	print("Image (PIL) not available")
	IMAGE = False

from AudioFile import *
from Preferences import *
from Pipeline import *
from Encoder import *
from TagFinder import *


### Thread che avvia la pipeline per la conversione dei file con gstreamer###
class Converter(threading.Thread):

	def __init__(self, mainapp, prefs, request_queue):

		threading.Thread.__init__(self)

		self.mainapp = mainapp
		self.request_queue = request_queue
		self.prefs = prefs
		if bool(int(self.prefs.get_option("playlist"))):
			self.listsongs = []
			self.listsongs.append("#EXTM3U" + "\n")

	def run(self):

		self.queue_complete = False
		while 1:
			# Blocca finché c'è qualcosa da processare nella coda
			request = self.request_queue.get()
			# Se l'elemento della coda è None esce
			if request is None:
				break
			# Estrae dall'elemento della coda da processare
			n, sel = request

			# Avanza la progressbar
			self.work_complete = False
			self.amount_completed = 0
			self.idevent = gobject.timeout_add(200, self.mainapp.on_ProgressBar)

			# Seleziona il file da processare
			af = sel[0]
			it = sel[1]
			try:
				self.mainapp.FileTable.tvSelection.select_iter(it)
			except: pass

			# Prepara il messaggio per la status bar
			self.n = n
			if af.get_tag("title") != "Unknown title" and af.get_tag("artist") != "Unknown artist":
				self.msg = af.get_tag("artist") + " - " + af.get_tag("title")
			else:
				self.msg = af.get_filename()

			# Percorso di ingresso
			if af.get_uri()[:7] == "file://":
				input_path = af.get_uri()[7:]
			elif af.get_uri()[:7] == "cdda://":
				input_path = af.get_uri()[7:]
			else:
				input_path = af.get_uri()

			# Se usa gstreamer per la conversione
			if not bool(int(self.prefs.get_option("use-external-encoder"))):
				# Estrae le opzioni per la conversione
				print self.Options(af, self.prefs)
				format, mode, qual, bitrate, save_path, output_file_name, tagsv1, tagsv2 = self.Options(af, self.prefs)
				# Pipeline
				converter_pipe = Pipeline(input_path, format, mode, qual, bitrate, save_path + "/" + output_file_name)

				# Rimane nel ciclo finché la pipeline non è finita
				while 1:
					state, pending, timeout = converter_pipe.pipe.get_state()
					if pending == gst.STATE_NULL:
						print "Finito:", input_path
						self.work_complete = True
						gobject.source_remove(self.idevent)
						break
					else:
						position = converter_pipe.pipe.query_position(gst.FORMAT_TIME, None)[0]
						perc = float(position)/converter_pipe.duration
						if perc > 1:
							perc = 0
						time.sleep(0.1)
						self.amount_completed = perc

				# Scrive i tags
				af_output = AudioFile("file://" + save_path + "/" + output_file_name + "." + format)
				if tagsv1:
					af_output.set_tags_as_dict(af.get_tags_as_dict())
					af_output.set_tag("comment", "X Audio Copy")
					af_output.write_metadata()
				else:
					af_output.remove_metadata()
				if tagsv2:
					af_output.write_ID3v2()

				if bool(int(self.prefs.get_option("playlist"))):
					if "/CD" in save_path:
						self.savepath = save_path[:save_path.index("/CD")]
					else:
						self.savepath = save_path
					self.playlistname = af_output.get_tag("artist") + " - " + af_output.get_tag("album")
					self.listsongs.append("#EXTINF:" + str(int(af_output.get_duration())) + "," + af_output.get_tag("artist") + " - " + af_output.get_tag("title") + "\n")
					self.listsongs.append(save_path[save_path.index("/CD") + 1:] + "/" + af_output.get_filename() + "\n")
				self.work_complete = True

			# Se usa un encoder esterno. Prima decodifica il file.
			elif bool(int(self.prefs.get_option("use-external-encoder"))) and self.Options(af, self.prefs):

				# Estrae le opzioni per la conversione
				opt_string, input_path, output_path, tagsv1, tagsv2 = self.Options(af, self.prefs)

				if af.get_type() == "audio/x-wav":
					opt_string = opt_string.replace('"temporarypath"', '"' + input_path + '"')
					perc = 0.0
				else:
					# Directory temporanea
					tempdir = tempfile.mkdtemp()
					#Pipeline per decodificare in wav
					converter_pipe = Pipeline(input_path, "wav", None, None, None, tempdir + "/temp_file")

					# Rimane nel ciclo finché la pipeline non è finita
					while 1:
						state, pending, timeout = converter_pipe.pipe.get_state()
						if pending == gst.STATE_NULL:
							print "Decodifica finita"
							break
						else:
							position = converter_pipe.pipe.query_position(gst.FORMAT_TIME, None)[0]
							perc = float(position)/converter_pipe.duration/50
							if perc > 1:
								perc = 0
							time.sleep(0.1)
							self.amount_completed = perc
					# Passa il file decodificato all'encoder esterno
					opt_string = opt_string.replace('"temporarypath"', '"' + tempdir + '/temp_file.wav"')

				init_encoder_time = time.time()
				encoder_args = shlex.split(opt_string)
				encoder = Encoder(encoder_args)
				# Rimane nel ciclo finché il sub-processo non è finito
				while 1:
					if encoder.process.poll() == 0:
						print "Finito:", input_path
						self.work_complete = True
						gobject.source_remove(self.idevent)
						break
					else:
						if (time.time() - init_encoder_time > 1):
							if perc < 1:
								tag = TagFinder("file://" + output_path)
								encoding_done = tag.get_duration()
								perc = float(encoding_done)/af.get_duration()/2.1
								print "PERCENTUALE: ", perc
								if perc < 1:
									self.amount_completed = perc
								else:
									self.amount_completed = 1
							else:
								self.amount_completed = 1
						time.sleep(2)
				try:
					walk = os.walk(tempdir)
					for dirpath, subdir, filenames in walk:
						for f in filenames:
							os.remove(os.path.join(dirpath, f))
					os.rmdir(tempdir)
				except: pass

				# Scrive la playlist
				if bool(int(self.prefs.get_option("playlist"))):
					if "/CD" in output_path:
						self.savepath = os.path.split(output_path)[0][:os.path.split(output_path)[0].index("/CD")]
					else:
						self.savepath = os.path.split(output_path)[0]
					self.playlistname = af.get_tag("artist") + " - " + af.get_tag("album")
					self.listsongs.append("#EXTINF:" + str(int(af.get_duration())) + "," + af.get_tag("artist") + " - " + af.get_tag("title") + "\n")
					self.listsongs.append(output_path[len(self.savepath + "/"):] + "\n")
				
				self.work_complete = True
			else:
				gobject.source_remove(self.idevent)
				self.msg = "nothing. No external encoder. Please choise a valid encoder"

			# Cancella i file originali se previsto
			if bool(int(self.prefs.get_option("delete-original-files"))):
				if af.get_uri()[:7] == "file://":
					os.remove(af.get_filepath())

		self.queue_complete = True
		self.mainapp.on_ProgressBar()

	# Carica le prefenze per la conversione
	def Options(self, af, prefs):

		# Percorso di salvataggio
		if bool(int(prefs.get_option("save-in-home"))):
			save_path = DIRMUSIC
		elif bool(int(prefs.get_option("save-in-same-folder"))):
			if af.get_foldername() == "Audio CD":
				save_path = DIRMUSIC
			else:
				save_path = af.get_foldername()
		elif bool(int(prefs.get_option("save-in-last-folder"))):
			save_path = prefs.get_option("last-save-folder")
		elif bool(int(prefs.get_option("select-path"))):
			save_path = prefs.get_option("alt-save-folder")

		# Memorizza nelle pref il percorso di salvataggio (selza subdir)
		prefs.set_option("last-save-folder", save_path)

		# Aggiunge le sottodirectory se richiesto
		if bool(int(prefs.get_option("create-subfolders"))):
			for sfp in SUBFOLDERS_PATH:
				if prefs.get_option("path-subfolder") == sfp[0]:
					save_path = save_path + "/" + expand_title(sfp[1],
								af.get_tag("artist"),
								af.get_tag("album"),
								af.get_tag("year"),
								str(af.get_tag("track_number")),
								af.get_tag("title"),
								"",
								disc_number_str=str(af.get_tag("disc_number")))

		# Crea le sottodirectory se non esistono
		if not os.path.exists(save_path):
			save_path_split = save_path.split("/")
			path_d=""
			for d in save_path_split:
				if len(d)>0:
					path_d = path_d + "/" + d
					if not os.path.exists(path_d):
						os.mkdir(path_d)

		# Nome del file di uscita
		if prefs.get_option("filename-pattern") == "Same as imput, but replacing the suffix":
			output_file_name = af.get_filename()[:-4]
		elif prefs.get_option("filename-pattern") == "Same as imput, but with an additional suffix":
			output_file_name = af.get_filename()
		elif prefs.get_option("filename-pattern") == "Alternate filename pattern":
			output_file_name = expand_title(re.sub('(?=\w)', '%', prefs.get_option("alternate-filename-pattern")), af.get_tag("artist"), af.get_tag("album"), af.get_tag("year"), af.get_tag("track_number"), af.get_tag("title"), af.get_tag("disc_number"))
		else:
			for fnp in FILENAME_PATTERN:
				if prefs.get_option("filename-pattern") == fnp[0]:
					output_file_name = expand_title(fnp[1], af.get_tag("artist"), af.get_tag("album"), af.get_tag("year"), af.get_tag("track_number"), af.get_tag("title"), af.get_tag("disc_number"))
		
		# Sostituisce gli spazi con gli underscore
		if bool(int(prefs.get_option("replace-spaces-by-underscores"))):
			output_file_name = re.compile(" ").sub("_", output_file_name)

		print "###outputfilename###: ", output_file_name

		# Formato di uscita e qualità
		if not bool(int(prefs.get_option("use-external-encoder"))):
			if prefs.get_option("output-format") == "ogg":
				mode = None
				qual = int(prefs.get_option("vorbis-quality"))
				bitrate = None
			elif prefs.get_option("output-format") == "mp3":
				mode = prefs.get_option("mp3-bitrate-mode")
				qual = int(prefs.get_option("mp3-quality"))
				bitrate = int(prefs.get_option("mp3-bitrate"))
			elif prefs.get_option("output-format") == "flac":
				mode = None
				qual = int(prefs.get_option("flac-quality"))
				bitrate = None
			elif prefs.get_option("output-format") == "wav":
				mode = None
				qual = None
				bitrate = None
			# Inserisce nella coda gli elementi da processare:
			# numero selezione, selezione, formato di output, mode (per mp3), qualità, bitrate,
			# path di uscita, nome del file di uscita, tags v1 e tags v2
			request = [prefs.get_option("output-format"),
				mode, qual, bitrate, save_path, output_file_name,
				bool(int(prefs.get_option("write-ID3v1"))),
				bool(int(prefs.get_option("write-ID3v2")))]

			return request

		if bool(int(prefs.get_option("use-external-encoder"))):
			str2num = lambda x : str(x) == "" and "0" or str(x)
			if prefs.get_option("external-encoder") == "oggenc":
				if bool(int(prefs.get_option("write-ID3v1"))):
					if af.get_tag("cover") and IMAGE:
						# TODO: Come inserire la copertina? (COVERART nei Vorbis comment)
						#tag_cover = ' -c "COVERART=' + str(af.get_tag("cover")) + '"'
						tag_cover = ''
					else:
						tag_cover = ''
					if af.get_tag("album_artist")and len(af.get_tag("album_artist")) > 0:
						tag_album_artist = ' -c albumartist="' + af.get_tag("album_artist") + '"'
					else:
						tag_album_artist = ''
					if af.get_tag("composer") and len(af.get_tag("composer")) > 0:
						tag_composer = ' -c composer="'+ af.get_tag("composer") + '"'
					else:
						tag_composer = ''
					if af.get_tag("disc_number") and len(str(af.get_tag("disc_number"))) > 0:
						tag_POS = ' -c discnumber="' + str(af.get_tag("disc_number")) + '"'
					else:
						tag_POS = ''
					tag_string = tag_composer + tag_cover + tag_POS + tag_album_artist + \
						' -t "' + af.get_tag("title") + '"' + \
						' -a "' + af.get_tag("artist") + '"' + \
						' -l "' + af.get_tag("album") + '"' + \
						' -d "' + str(af.get_tag("year")) + '"' + \
						' -N "' + str('%(#)02d' %{'#': int(str2num(af.get_tag("track_number")))}) + '"' + \
						' -G "' + af.get_tag("genre") + '"' + \
						' -c "comment=X Audio Copy with oggenc"'
				else:
					tag_string = ''
				vorbis_string = str('oggenc -Q ' + prefs.get_option("vorbis-options") + \
						tag_string + \
						' -o "' + save_path + '/' + output_file_name + '.ogg"' + \
						' "' + "temporarypath" + '"')
				return [vorbis_string,
					str(af.get_filepath()),
					save_path + '/' + output_file_name + '.ogg',
					bool(int(prefs.get_option("write-ID3v1"))),
					False]

			elif prefs.get_option("external-encoder") == "lame":
				if bool(int(prefs.get_option("write-ID3v1"))):
					if af.get_tag("cover") and IMAGE:
						tag_cover = ' --ti "' + self.Cover(af) + '"'
					else:
						tag_cover = ''
					if af.get_tag("album_artist")and len(af.get_tag("album_artist")) > 0:
						tag_album_artist = ' --tv TPE2="' + af.get_tag("album_artist") + '"'
					else:
						tag_album_artist = ''
					if af.get_tag("composer") and len(af.get_tag("composer")) > 0:
						tag_composer = ' --tv TCOM="' + af.get_tag("composer") + '"'
					else:
						tag_composer = ''
					if af.get_tag("disc_number") and len(str(af.get_tag("disc_number"))) > 0:
						tag_POS = ' --tv TPOS="'  + str(af.get_tag("disc_number")) + '"'
					else:
						tag_POS = ''
					tag_string = tag_cover + tag_composer + tag_album_artist + tag_POS + \
						' --tt "' + af.get_tag("title") + '"' + \
						' --ta "' + af.get_tag("artist") + '"' + \
						' --tl "' + af.get_tag("album") + '"' + \
						' --ty "' + str(af.get_tag("year")) + '"' + \
						' --tn "' + str('%(#)02d' %{'#': int(str2num(af.get_tag("track_number")))}) + '"' + \
						' --tg "' + af.get_tag("genre") + '"' + \
						' --tc "X Audio Copy with lame"'
					if bool(int(prefs.get_option("write-ID3v2"))):
						tag_string = tag_string + ' --add-id3v2'
					else:
						tag_string = tag_string + ' --id3v1-only'
				else:
					tag_string = ''
				lame_string = str('lame --silent ' + prefs.get_option("lame-options") + \
						tag_string + \
						' "' + "temporarypath" + '"' + \
						' "' + save_path + '/' + output_file_name + '.mp3"')
				return [lame_string,
					str(af.get_filepath()),
					save_path + '/' + output_file_name + '.mp3',
					bool(int(prefs.get_option("write-ID3v1"))),
					bool(int(prefs.get_option("write-ID3v2")))]

			elif prefs.get_option("external-encoder") == "flac":
				if bool(int(prefs.get_option("write-ID3v1"))):
					if af.get_tag("cover") and IMAGE:
						tag_cover = ' --picture="' + self.Cover(af) + '"'
					else:
						tag_cover = ''
					if af.get_tag("album_artist") and len(af.get_tag("album_artist")) > 0:
						tag_album_artist = ' -T ALBUMARTIST="'+ af.get_tag("album_artist") + '"'
					else:
						tag_album_artist = ''
					if af.get_tag("composer") and len(af.get_tag("composer")) > 0:
						tag_composer = ' -T COMPOSER="'+ af.get_tag("composer") + '"'
					else:
						tag_composer = ''
					if af.get_tag("disc_number") and len(str(af.get_tag("disc_number"))) > 0:
						tag_POS = ' -T DISCNUMBER="'  + str(af.get_tag("disc_number")) + '"'
					else:
						tag_POS = ''
					tag_string = tag_composer + tag_cover + tag_POS + tag_album_artist+ \
						' -T TITLE="' + af.get_tag("title") + '"' + \
						' -T ARTIST="' + af.get_tag("artist") + '"' + \
						' -T ALBUM="' + af.get_tag("album") + '"' + \
						' -T DATE="' + str(af.get_tag("year")) + '"' + \
						' -T TRACKNUMBER="' + str('%(#)02d' %{'#': int(str2num(af.get_tag("track_number")))}) + '"' + \
						' -T GENRE="' + af.get_tag("genre") + '"' + \
						' -T COMMENT="X Audio Copy with flac"'
				else:
					tag_string = ''
				flac_string = str('flac -s -f ' + prefs.get_option("flac-options") + \
						tag_string + \
						' -o "' + save_path + '/' + output_file_name + '.flac"' + \
						' "' + "temporarypath" + '"')
				return [flac_string,
					str(af.get_filepath()),
					save_path + '/' + output_file_name + '.flac',
					bool(int(prefs.get_option("write-ID3v1"))),
					False]

			elif prefs.get_option("external-encoder") == "user":
				if len(prefs.get_option("user-defined-encoder-command")) > 0:
					if "lame" in prefs.get_option("user-defined-encoder-command"):
						return [prefs.get_option("user-defined-encoder-command") + ' "temporarypath" ' + \
							' "' + save_path + '/' + output_file_name + '.mp3"',
						str(af.get_filepath()),
						save_path + '/' + output_file_name + '.mp3',
						False, False]
					elif  "ogg" in prefs.get_option("user-defined-encoder-command"):
						return [prefs.get_option("user-defined-encoder-command") + \
							' -o "' + save_path + '/' + output_file_name + '.ogg" "' + \
							'temporarypath' + '"',
						str(af.get_filepath()),
						save_path + '/' + output_file_name + '.ogg',
						False, False]
					elif  "flac" in prefs.get_option("user-defined-encoder-command"):
						return [prefs.get_option("user-defined-encoder-command") + \
							' -o "' + save_path + '/' + output_file_name + '.flac" "' + \
							'temporarypath' + '"',
						str(af.get_filepath()),
						save_path + '/' + output_file_name + '.flac',
						False, False]
					else:
						return [prefs.get_option("user-defined-encoder-command") + \
							' "' + save_path + '/' + output_file_name + '" "' + \
							'temporarypath' + '"',
						str(af.get_filepath()),
						save_path + '/' + output_file_name,
						False, False]
				else:
					return False
			

	# Ricava la copertina per inserirla nei tag (se esiste nel file e se è installato il modulo PIL)
	def Cover(self, audiofile):

		if audiofile.get_tag("cover") and IMAGE:
			covers = []
			if isinstance(audiofile.get_tag("cover"), list):
				cover = audiofile.get_tag("cover")[0]
			else:
				cover = audiofile.get_tag("cover")
			cover_file = open(XACHOME + "/cover.jpg", "w")
			cover_file.write(cover)
			cover_file.close()
			img = Image.open(XACHOME + "/cover.jpg")
			if os.path.getsize(img.filename) > 128*1024:
				new_size = 600, 600
				k = 1.0
				while 1:
					new_size = int(new_size[0]*k), int(new_size[1]*k)
					img = Image.open(img.filename)
					img.resize(new_size, Image.ANTIALIAS).save(img.filename)
					k = k / 2.0
					if os.path.getsize(img.filename) < 128*1024:
						break
			return img.filename
		else:
			return None
