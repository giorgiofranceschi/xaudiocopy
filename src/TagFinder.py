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
import time
try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	pass


### Classe che legge i tag da un file audio ###
class TagFinder:

	# Costruttore della classe
	def __init__(self, uri):

		self.__uri = uri
		self.__taglist = {}

		self.pipe = gst.Pipeline("pipe")

		#filesource = gst.element_factory_make("filesrc", "filesource")
		#filesource.set_property("location", self.__location)
		filesource = gst.element_make_from_uri(gst.URI_SRC, self.__uri)

		decoder = gst.element_factory_make("decodebin2", "decoder")
		decoder.connect("new-decoded-pad", self.on_pad)
		self.pipe.add(filesource, decoder)
		gst.element_link_many(filesource, decoder)

		self.converter = gst.element_factory_make("audioconvert", "converter")
		fakesink = gst.element_factory_make("fakesink", "sink")
		self.pipe.add(self.converter, fakesink)
		gst.element_link_many(self.converter, fakesink)

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
		if t == gst.MESSAGE_TAG:
			gst_taglist = message.parse_tag()
			for key in gst_taglist.keys():
				if not ((key == "image") or (key == "preview-image")):
					print '%s = %s' % (key, gst_taglist[key])
				else:
					print key
				if not (key in self.__taglist.keys()):
					self.__taglist[key] = gst_taglist[key]
		
		elif t == gst.MESSAGE_EOS or t == gst.MESSAGE_ASYNC_DONE:
			# Ricava la durata del brano
			while 1:
				try:
					self.__duration = float(self.pipe.query_duration(gst.FORMAT_TIME)[0])/gst.SECOND
					print "Duration from gst.query_duration: ", self.__duration
					break
				except:
					# Aspetta per completare la query
					time.sleep(0.01)

			self.pipe.set_state(gst.STATE_NULL)
			self.mainloop.quit()
		elif t == gst.MESSAGE_ERROR:
			self.pipe.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.mainloop.quit()

	#Restituisce i tag letti
	def get_tags(self):

		if self.__taglist:
			return self.__taglist
		else:
			return None
	# Restituisce la durata in secondi
	def get_duration(self):

		try:
			return self.__duration
		except:
			return None
