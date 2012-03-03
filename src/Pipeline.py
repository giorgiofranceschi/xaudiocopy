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

import os, time
try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	pass


### Pipeline per convertire i file audio ###
class Pipeline:

	def __init__(self, input_path, format, mode, qual, bitrate, output_path):
		
		if not os.path.exists(input_path):
			print "Track not found"
			return

		# Pipeline di gstreamer
		self.pipe = gst.Pipeline("pipe")

		# File sorgente
		source = gst.element_factory_make("filesrc", "file-source")
		source.set_property("location", input_path)

		# Decodebin2 con l'evento
		decoder = gst.element_factory_make("decodebin2", "decoder")
		decoder.connect("new-decoded-pad", self.on_pad)

		# Aggiunge i primi due alla pipeline e li collega
		self.pipe.add(source, decoder)
		gst.element_link_many(source, decoder)

		# Audioconverter
		self.converter = gst.element_factory_make("audioconvert", "converter")

		if format == "wav":
			# Formato grezzo
			caps = gst.Caps("audio/x-raw-int, width=16")
			capsfilter = gst.element_factory_make("capsfilter", "filter")
			capsfilter.set_property("caps", caps)
			# Encoder wav
			encoder = gst.element_factory_make("wavenc", "wavencoder")
		elif format == "ogg":
			#Encoder
			encoder = gst.element_factory_make("vorbisenc", "vorbisencoder")
			encoder.set_property("quality", float(qual)/10)
			# Muxer
			muxer = gst.element_factory_make("oggmux", "muxer")
		elif format == "mp3":
			#Encoder
			encoder = gst.element_factory_make("lamemp3enc", "lameencoder")
			if mode == "CBR":
				encoder.set_property("target", "bitrate")
				encoder.set_property("bitrate", bitrate)
				encoder.set_property("cbr", True)
			if mode == "ABR":
				encoder.set_property("target", "bitrate")
				encoder.set_property("bitrate", bitrate)
			if mode == "VBR":
				encoder.set_property("target", "quality")
				encoder.set_property("quality", float(qual))
			xingmuxer = gst.element_factory_make("xingmux", "xingmuxer")
		elif format == "flac":
			#Encoder
			encoder = gst.element_factory_make("flacenc", "flacencoder")
			encoder.set_property("quality", qual)

		# File risultato
		dest = gst.element_factory_make("filesink", "file-dest")
		dest.set_property("location",  output_path + "." + format)
		print dest.get_property("location")

		# Aggiunge e collega gli ultimi
		if format == "wav":
			self.pipe.add(self.converter, capsfilter, encoder, dest)
			gst.element_link_many(self.converter, capsfilter, encoder, dest)
		elif format == "ogg":
			self.pipe.add(self.converter, encoder, muxer, dest)
			gst.element_link_many(self.converter, encoder, muxer, dest)
		elif format == "mp3":
			self.pipe.add(self.converter, encoder, xingmuxer, dest)
			gst.element_link_many(self.converter, encoder, xingmuxer, dest)
		elif format == "flac":
			self.pipe.add(self.converter, encoder, dest)
			gst.element_link_many(self.converter, encoder, dest)

		# Bus
		self.bus = self.pipe.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_end)

		# Esegue la pipeline
		self.pipe.set_state(gst.STATE_PLAYING)

		# Durata della pipeline
		# Dentro un loop perché query_duration a volte dà errore (PERCHE'?)
		while 1:
			print "loop in corso"
			try:
				self.duration = self.pipe.query_duration(gst.FORMAT_TIME)[0]
				break
			except:
				time.sleep(0.01)
		print "DURATION", self.duration

	# Evento "new-decoded-pad" di decodebin2
	# Thanks to http://www.jonobacon.org/2006/11/03/gstreamer-dynamic-pads-explained/
	def on_pad(self, dbin, pad, islast):

		pad.link(self.converter.get_pad("sink"))

	# Evento al termine della pipeline
	def on_end(self, bus, message):

		t = message.type
		if t == gst.MESSAGE_EOS:
			#self.mainloop.quit()
			self.pipe.set_state(gst.STATE_NULL)
		elif t == gst.MESSAGE_ERROR:
			self.pipe.set_state(gst.STATE_NULL)
			#self.mainloop.quit()
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
