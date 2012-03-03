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


import os
import sys
try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    pass  
try:
    import gtk    
    import gobject
except:  
    print("GTK Not Availible")
    sys.exit(1)
try:
    import pygst
    pygst.require("0.10")
    import gst
except:
    print("Gstreamer Not Availible")
from AudioFile import *
from FileList import *
from Player import *


file = "/media/GIORGIO/Sviluppo/Xaudiocopy/Musica/Carioca.mp3"

audioFileList = FileList([file])
print audioFileList
print audioFileList.filelist
print audioFileList.filelist[0]
print audioFileList.filelist[0].uri
print audioFileList.filelist[0].title
print audioFileList.filelist[0].get_tags()