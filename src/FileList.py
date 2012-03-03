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


from AudioFile import *


### Classe per gestire una lista di file audio di classe AudioFile() ###
class FileList:

    # Costruttore della classe
    # La classe accetta come argomento una lista di file con percorso assoluto.
    def __init__(self, uris=None):

        self.purge()
	if uris:
	        self.add_list(uris)

    # Aggiunge una lista di file
    def add_list(self, uris):
        try:
            for uri in uris:
                af = AudioFile(uri)
                self.filelist.append(af)
        except:
            self.filelist=[]
        # Elimina i duplicati
        self.filelist = self.uniq(self.filelist)
        #self.sort()

    # Aggiunge un singolo file audio tramite il suo uri
    def add(self, uri):
        af = AudioFile(uri)
        self.filelist.append(af)
        # Elimina i duplicati
        self.filelist = self.uniq(self.filelist)

    # Aggiunge un singolo file audio come oggetto
    def append(self, af):
        self.filelist.append(af)
        # Elimina i duplicati
        self.filelist = self.uniq(self.filelist)

    # Verifica l'unicità del file nella lista e riordina la lista
    def uniq(self, in_fl):
        out_fl = []
        out_fl_uri = []
        
        for x in in_fl:
            if x.get_uri() not in out_fl_uri:
                out_fl.append(x)
                out_fl_uri.append(x.get_uri())
            else:
                print "file duplicato"
        return out_fl
    
    def sort(self):
        if self.filelist:
            self.filelist.sort(lambda x, y: cmp(x.get_tag("track_number"), y.get_tag("track_number")))
        
    # Rimuove un file dalla lista
    def remove(self, uri):
        newlist = self.filelist[:]
        i=-1
        for af in newlist:
            i=i+1
            if af.get_uri() == uri:
                del newlist[i]
        self.filelist = newlist[:]

    # Svuota la lista dei file
    def purge(self):
        self.filelist = []


            
        
