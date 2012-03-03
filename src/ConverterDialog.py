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

from PreferencesDialog import *


### Subclasse che contiene le preferenze solo per la conversione ###
class ConverterDialog(PreferencesDialog):
    
    # Costruttore della classe
    def __init__(self, main_window, prefs):
        PreferencesDialog.__init__(self, main_window, prefs)

        self.dlg.set_title("Audio file converter...")
        self.notebook.set_current_page(3)
        self.notebook.remove_page(0)
        self.cmdOK.set_label("C_onvert")
        self.cmdReset.hide()
