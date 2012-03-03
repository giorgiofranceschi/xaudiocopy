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
try:
	import pygst
	pygst.require("0.10")
	import gst
except:
	pass

### Classe che ricava il tipo del file audio ###
class TypeFinder:

	# Costruttore della classe
	def __init__(self, uri):

		self.__uri = uri

		self.pipe = gst.Pipeline("pipe")

		#filesource = gst.element_factory_make("filesrc", "filesource")
		#filesource.set_property("location", self.__location)
		filesource = gst.element_make_from_uri(gst.URI_SRC, self.__uri)

		fakesink = gst.element_factory_make("fakesink", "sink")

		typefind = gst.element_factory_make("typefind", "typefinder")
		typefind.connect("have_type", self.on_find_type)

		self.pipe.add(filesource, typefind, fakesink)
		gst.element_link_many(filesource, typefind, fakesink)

		self.bus = self.pipe.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_message)

		self.pipe.set_state(gst.STATE_PLAYING)
		#self.mainloop = gobject.MainLoop()
		#self.mainloop.run()

	def on_find_type(self, typefind, probability, caps):
		self.__type = caps.to_string()
		for struct in caps:
			self.__type = struct.get_name()

		print "Media type %s found, probability %d%% " %(self.__type, probability)
		self.pipe.set_state(gst.STATE_NULL)
		#self.mainloop.quit()

	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS or t == gst.MESSAGE_ASYNC_DONE:
			self.pipe.set_state(gst.STATE_NULL)
			#self.mainloop.quit()
		elif t == gst.MESSAGE_ERROR:
			self.pipe.set_state(gst.STATE_NULL)
			#self.mainloop.quit()
			err, debug = message.parse_error()
			print "Error: %s" % err, debug

	def get_type(self):
		if self.__type:
			return self.__type
		else:
			return None

### Test ###
#tf=TypeFinder("cdda://01")
#tf=TypeFinder("file:///home/giorgio/Musica/Filediingresso/01 Carioca.mp3")

