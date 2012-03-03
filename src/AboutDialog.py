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

try:
    import pygtk
    pygtk.require("2.0")
except:
    print("PyGTK not available")
    sys.exit(1)

try:
    import gtk
    import gobject
except:
    print("GTK not available")
    sys.exit(1)
    
from Preferences import *


### Classe della finestra di dialogo informazioni ###
class AboutDialog:

    # Costruttore della classe
    def __init__(self):

        self.dlgAbout = gtk.AboutDialog()
        self.dlgAbout.set_title('%s %s' % ("About ",WINDOW_TITLE))
        self.dlgAbout.set_name(NAME)
        self.dlgAbout.set_version(VERSION)
        self.dlgAbout.set_authors(AUTHORS)
        self.dlgAbout.set_translator_credits(TRANSLATORS)
        self.dlgAbout.set_copyright(COPYRIGHT)
        self.dlgAbout.set_comments(COMMENTS)
        self.dlgAbout.set_license(LICENSE)
        self.dlgAbout.set_wrap_license(True)
        self.dlgAbout.run()
        self.dlgAbout.hide()


###Test###
#ad = classAboutDialog()