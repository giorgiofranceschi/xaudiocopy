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

import gobject
import os, time, wave
try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	pass

from Preferences import XACHOME


### Classe che legge le informazioni audio di un file audio convertendone un pezzo in wav ###
class InfoFinder:

	# Costruttore della classe
	def __init__(self, uri, gst_type):

		self.__uri = uri
		self.__gst_type = gst_type
		self.__taglist = {}

		# Pipeline di gstreamer
		self.pipe = gst.Pipeline("pipe")

		# File sorgente
		filesource = gst.element_make_from_uri(gst.URI_SRC, self.__uri)

		# Decodebin2 con l'evento
		decoder = gst.element_factory_make("decodebin2", "decoder")
		decoder.connect("new-decoded-pad", self.on_pad)

		# Aggiunge i primi due alla pipeline e li collega
		self.pipe.add(filesource, decoder)
		gst.element_link_many(filesource, decoder)

		# Audioconverter
		self.converter = gst.element_factory_make("audioconvert", "converter")

		# Formato grezzo
		caps = gst.Caps("audio/x-raw-int")
		capsfilter = gst.element_factory_make("capsfilter", "filter")
		capsfilter.set_property("caps", caps)
		# Encoder wav
		encoder = gst.element_factory_make("wavenc", "wavencoder")

		# File risultato
		dest = gst.element_factory_make("filesink", "file-dest")
		dest.set_property("location", XACHOME + "/tempfile.wav")

		# Aggiunge e collega gli ultimi
		self.pipe.add(self.converter, capsfilter, encoder, dest)
		gst.element_link_many(self.converter, capsfilter, encoder, dest)

		self.bus = self.pipe.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_message)

		self.pipe.set_state(gst.STATE_PLAYING)
		self.mainloop = gobject.MainLoop()
		self.mainloop.run()

	def on_pad(self, dbin, pad, islast):
		try:
			pad.link(self.converter.get_pad("sink"))
		except gst.LinkError:
			pass

	def on_message(self, bus, message):

		t = message.type
		print t
		if t == gst.MESSAGE_TAG:
			pass

		elif t == gst.MESSAGE_EOS:
			self.pipe.set_state(gst.STATE_NULL)
			self.mainloop.quit()
		elif t == gst.MESSAGE_ERROR:
			self.pipe.set_state(gst.STATE_NULL)
			self.mainloop.quit()
			err, debug = message.parse_error()
			print "Error: %s" % err, debug

		while 1:
			state, pending, timeout = self.pipe.get_state()
			if pending == gst.STATE_PLAYING:
				time.sleep(0.05)
				break
		self.pipe.set_state(gst.STATE_NULL)

		if os.path.exists(XACHOME + "/tempfile.wav"):
			print "ESISTE"
			w = wave.open(XACHOME + "/tempfile.wav")
			self.__n_channels = w.getnchannels()
			# TODO - Scoprire perché sampwidth è 4 per mp3, ogg, ecc.
			#        Dipende dalla conversione di gst? Coi CD funziona.
			if self.__gst_type == "audio/x-raw-int":
				self.__sampwidth_B = w.getsampwidth()
			else:
				self.__sampwidth_B = w.getsampwidth() / 2
			self.__sampwidth_b = self.__sampwidth_B * 8
			self.__framerate = w.getframerate()
			self.__n_frames = w.getnframes()
			self.__comp_type = w.getcomptype()
			w.close()
			os.remove(XACHOME + "/tempfile.wav")
		self.mainloop.quit()

	def get_info (self):
		
		return {"n_channels" : self.__n_channels, 
			"sampwidth_B" : self.__sampwidth_B, 
			"sampwidth_b" : self.__sampwidth_b, 
			"framerate" : self.__framerate, 
			"n_frames" : self.__n_frames}


### Test ###
'''loc = "file:///home/giorgio/Musica/Filediingresso/"
uri = loc + "01 Carioca.wav"
uri = loc + "LZ.wav.mp3"
info = InfoFinder(uri)'''

