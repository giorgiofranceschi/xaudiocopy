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


### Finestra di dialogo di avviso generica ###
class WarningDialog:

    # Costruttore della classe
    def __init__(self, main_window, title, message):

        dlg = gtk.MessageDialog(main_window, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, message)
        dlg.set_title(title)
        # Attiva e visualizza la finestra di dialogo
        dlg.run()
        dlg.destroy()