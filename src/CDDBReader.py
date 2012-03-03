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

import os, string, re

#try:
import CDDB, DiscID
#except:
#    print "CDDB not avalaible"


### Classe per leggere i dati del CD da FreeDB (http://www.freedb.org/)
class CDDBReader():
    
    # Costruttore della classe
    def __init__(self):
    
        cdaudio = DiscID.open()
        print "CD: ", cdaudio

        try:
            self.disc_id = DiscID.disc_id(cdaudio)
            print "disc_id: ", self.disc_id
            self.is_audio_cd = True
        except:
            print "No CD"
            disc_id = None
            self.is_audio_cd = False
            self.song_list = []
            cdaudio.close()
            raise
        
        if self.is_audio_cd:
            try:
                self.query_status, self.query_info = CDDB.query(self.disc_id)
                print "query_status: ", self.query_status
                print "query_info: ", self.query_info
            except:
                print 'IOError'
                self.song_list = []
                cdaudio.close()
                self.query_status = 409
                self.query_info = {"disc_id": "", "category": "", "title":""}
                pass

    def get_CDDB_tag(self, query_status, query_info):

        if self.is_audio_cd:
            read_status, read_info = CDDB.read(query_info['category'], query_info['disc_id'])
            print "read status: ", read_status
            print "read info: ", read_info
        else:
            return
        
        self.song_list = []
        if query_status in [200, 210]:
            self.is_audio_cd = True
            self.cddb_disc_id_b10 = self.disc_id[0]
            self.cddb_disc_id_b16 = query_info['disc_id']
            self.total_tracks = self.disc_id[1]
            
            if read_status == 210:
                for i in range(self.disc_id[1]):
                    n = "%.02d" %(i + 1)
                    title = "%s" %(read_info['TTITLE' + `i`])
                    frame = self.disc_id[i+2] 
                    self.song_list.append({"track_number":int(n), "title":title, "num_frame":frame})

                print "Song_list: ", self.song_list
                if read_info['DTITLE']:
                    disc_title = read_info['DTITLE']
                else:
                    disc_title = query_info[0]['title']
                self.artist, self.album = re.split(" / ", disc_title)
                if "," in self.artist:
                    a, b = re.split(", ", self.artist)
                    self.artist = b.title() + " " + a.title()
                try:
                    self.disc_len = read_info['disc_len']
                except:
                    self.disc_len = self.disc_id[2+self.disc_id[1]]
                self.year = read_info['DYEAR']
                if read_info['DGENRE']:
                    self.cddb_genre = read_info['DGENRE']
                else:
                    self.cddb_genre = query_info[0]['category']
            
            elif read_status in [401, 402, 403, 409, 417]:
                self.error = read_status
            else:
                return
            
        elif query_status in [211, 202, 403, 409]:
            self.error = query_status
            try:
                cdaudio.close()
            except:
                pass
            return self.error
        else:
            cdaudio.close()
            return
        
       
### Test ###
#cddb = CDDBReader()
