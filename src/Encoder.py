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

import subprocess


### Processo esterno per la codifica ###
class Encoder:

	def __init__(self, popenargs):

		self.encoding_end = False
		# Subprocesso per la conversione del file audio
		print popenargs
		self.process = subprocess.Popen(popenargs, shell=False, stdout=subprocess.PIPE)

		'''# Rimane nel ciclo finché il sub-processo non è finito
		while 1:
			if process.poll() == 0:
				print "encoding finito"
				self.encoding_end = True
				break
			else:
				print "encoding in corso"
				time.sleep(0.1)'''
