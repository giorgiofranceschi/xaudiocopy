from AudioFile import *

percorso = "file:///home/giorgio/Musica/Filediingresso"

#af = AudioFile(percorso + "/01 Carioca.mp3")
af = AudioFile(percorso + "/01 Carioca.ogg")
#af = AudioFile(percorso + "/01 Carioca.flac")
#af = AudioFile(percorso + "/01 Carioca.wav")

#af = AudioFile(percorso + "/01 Carioca (senza ID3).mp3")
#af = AudioFile(percorso + "/01 Carioca (ID3v1).mp3")
#af = AudioFile(percorso + "/01 Carioca (ID3v2).mp3")

#af = AudioFile(percorso + "/01 Carioca (senza tag).ogg")

#af = AudioFile(percorso + "/LZ.wav")

#af = AudioFile("cdda://01")

#af = AudioFile(percorso + "/01 Carioca.mp3")

print af.get_tags_as_dict()
'''
af.set_tag("title", "La mia canzone bella con il titolo lunghissimo")
af.set_tag("artist", "Giorgio")
af.set_tag("album", "Giorgio Greates Hits")
af.set_tag("genre", "Jazz")
af.set_tag("track_number", "09")
af.set_tag("year", "2011")
af.set_tag("comment", "Ho cambiato i tag")
af.set_tag("composer", "G. Franceschi")
af.set_tag("album_artist", "Giorgio e il suo gruppo")
af.set_tag("disc_number", "1/2")

af.write_ID3v2()

af = AudioFile(af.get_uri())
print af.get_tags_as_dict()'''

'''cover = af.get_tag("cover")
image = open(percorso[7:] + "/cover.jpg", "w")
image.write(cover)
image.close()'''

XACHOME="/home/giorgio/.xaudiocopy"
cover = af.get_tag("cover")
'''cover_file = open(XACHOME + "/cover.jpg", "w")
cover_file.write(cover)
cover_file.close()'''

img.save(XACHOME + "/cover128.jpg")


'''excom = af.get_extended_comment()
print excom
print type(af.get_extended_comment())'''

#print cover


#image=cover.get_caps()
#print image
