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
try:
	import Image
	IMAGE = True
except:
	print("Image (PIL) not available")
	IMAGE = False

from Preferences import XACHOME

### Finestra di dialogo per le proprietà della canzone ###
class PropertyDialog:

	# Costruttore della classe
	def __init__(self, mainapp, main_window, sel):

		self.mainapp = mainapp
		self.main_window = main_window

		# Finestra di dialogo
		self.dlg = gtk.Dialog("Property...", self.main_window ,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		self.dlg.set_default_size(50, 400)
		self.dlg.set_border_width(5)
		self.dlg.vbox.set_homogeneous(False)
		self.dlg.set_resizable(True)
		self.dlg.vbox.set_spacing(5)

		# Pulsanti precedente/prossimo
		buttonPrev = gtk.Button(stock=gtk.STOCK_MEDIA_PREVIOUS)
		buttonPrev.connect("clicked", self.on_Previous)
		self.dlg.action_area.pack_start(buttonPrev, expand=False, padding=0)
		buttonPrev.show()

		buttonNext = gtk.Button(stock=gtk.STOCK_MEDIA_NEXT)
		buttonNext.connect("clicked", self.on_Next)
		self.dlg.action_area.pack_start(buttonNext, expand=False, padding=0)
		buttonNext.show()
	   
		# Pulsante OK
		self.cmdOK = gtk.Button(label="_Ok", use_underline=True)
		self.cmdOK.connect("clicked", self.on_Ok)
		self.dlg.add_action_widget(self.cmdOK, 2)
		self.cmdOK.show()
		self.dlg.set_focus(self.cmdOK)

		self.load_tags(sel)

	# Carica i tag del brano selezionato
	def load_tags(self, sel):

		af = sel[0]
		it = sel[1]

		fl = lambda x : x=="" and "Unknown album" or x
		ft = lambda x : x=="" and "Unknown title" or x
		fa = lambda x : x=="" and "Unknown artist" or x
		fg = lambda x : x=="" and "Unknown genre" or x
		fy = lambda x : x=="" and "Unknown year" or x 

		# Label testata (artista e titolo)
		hboxSubject = gtk.HBox()
		hboxSubject.set_homogeneous(False)
		self.dlg.vbox.pack_start(hboxSubject, expand=False)
		hboxSubject.show()
		labelSubject = gtk.Label()
		labelSubject.set_use_markup(True)
		labelSubject.set_justify(gtk.JUSTIFY_LEFT)
		labelSubject.set_line_wrap(True)
		labelSubject.set_label("""<span size='x-large'><b>{0}
<i>{1}</i></b> </span>""".format(fa(af.get_tag("artist")), ft(af.get_tag("title"))))
		labelSubject.set_padding(0, 10)
		hboxSubject.pack_start(labelSubject, expand=False, padding = 20)
		labelSubject.show()
	
		# Box per copertina e tag
		hboxDisc = gtk.HBox()
		hboxDisc.set_homogeneous(False)
		self.dlg.vbox.pack_start(hboxDisc, expand=False)
		hboxDisc.show()

		labelSpazio = gtk.Label("")
		labelSpazio.set_use_markup(True)
		labelSpazio.set_justify(gtk.JUSTIFY_LEFT)
		hboxDisc.pack_start(labelSpazio, expand=False, padding=10)
		labelSpazio.show()

		# Copertina (se esiste nel file e se è installato il modulo PIL)
		imgCover = gtk.Image()
		if af.get_tag("cover") and IMAGE:
			covers = []
			if isinstance(af.get_tag("cover"), list):
				for cov in af.get_tag("cover"):
					covers.append(cov)
			else:
				covers.append(af.get_tag("cover"))
			covers_file = []
			imgCovers = []
			print range(len(covers))
			for i in range(len(covers)):
				print i
				covers_file.append(open(XACHOME + "/cover" + str(i) + ".jpg", "w"))
				covers_file[i].write(covers[i])
				covers_file[i].close()
				img = Image.open(XACHOME + "/cover" + str(i) + ".jpg")
				new_size = 100, 100
				img.resize(new_size, Image.ANTIALIAS).save(XACHOME + "/cover_resized" + str(i) + ".jpg")
				imgres = Image.open(XACHOME + "/cover_resized" + str(i) + ".jpg")
				imgCovers.append(gtk.Image())
				imgCovers[i].set_from_file(imgres.filename)
				hboxDisc.pack_start(imgCovers[i], expand=False, padding=5)
				imgCovers[i].show()
				try:
					os.remove(XACHOME + "/cover" + str(i) + ".jpg")
					os.remove(XACHOME + "/cover_resized" + str(i) + ".jpg")
				except: pass
		else:
			imgCover.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_DIALOG)
			hboxDisc.pack_start(imgCover, expand=False, padding=20)
			imgCover.show()

		# Tag
		vboxDisc = gtk.VBox()
		vboxDisc.set_homogeneous(False)
		hboxDisc.pack_start(vboxDisc, expand=False, padding=10)
		vboxDisc.set_spacing(5)
		vboxDisc.show()

		hboxAlbum = gtk.HBox()
		hboxAlbum.set_homogeneous(False)
		vboxDisc.pack_start(hboxAlbum, expand=False)
		hboxAlbum.show()
		labelAlbum = gtk.Label("""<span size='small'>Album:   <i>{0}</i> </span>""".format(fl(af.get_tag("album"))))
		labelAlbum.set_use_markup(True)
		labelAlbum.set_justify(gtk.JUSTIFY_LEFT)
		labelAlbum.set_line_wrap(True)
		hboxAlbum.pack_start(labelAlbum, expand=False)
		labelAlbum.show()

		if af.get_tag("disc_number") and len(str(af.get_tag("disc_number"))) > 0:
			hboxDiscNumber = gtk.HBox()
			hboxDiscNumber.set_homogeneous(False)
			vboxDisc.pack_start(hboxDiscNumber, expand=False)
			hboxDiscNumber.show()
			labelDiscNumber = gtk.Label("""<span size='small'>Disc:   {0} </span>""".format(af.get_tag("disc_number")))
			labelDiscNumber.set_use_markup(True)
			labelDiscNumber.set_justify(gtk.JUSTIFY_LEFT)
			labelDiscNumber.set_line_wrap(True)
			hboxDiscNumber.pack_start(labelDiscNumber, expand=False)
			labelDiscNumber.show()

		if af.get_tag("track_number")and len(str(af.get_tag("track_number"))) > 0:
			hboxTrackNumber = gtk.HBox()
			hboxTrackNumber.set_homogeneous(False)
			vboxDisc.pack_start(hboxTrackNumber, expand=False)
			hboxTrackNumber.show()
			if len(af.get_tag("track_count")) > 0:
				labelTrackNumber = gtk.Label("""<span size='small'>Track number:   {0}/{1} </span>""".format(af.get_tag("track_number"), af.get_tag("track_count")))
			else:
				labelTrackNumber = gtk.Label("""<span size='small'>Track number:   {0} </span>""".format(af.get_tag("track_number")))
			labelTrackNumber.set_use_markup(True)
			labelTrackNumber.set_justify(gtk.JUSTIFY_LEFT)
			labelTrackNumber.set_line_wrap(True)
			hboxTrackNumber.pack_start(labelTrackNumber, expand=False)
			labelTrackNumber.show()

		hboxYear = gtk.HBox()
		hboxYear.set_homogeneous(False)
		vboxDisc.pack_start(hboxYear, expand=False)
		hboxYear.show()
		labelYear = gtk.Label("""<span size='small'>Year:   {0} </span>""".format(fy(af.get_tag("year"))))
		labelYear.set_use_markup(True)
		labelYear.set_justify(gtk.JUSTIFY_LEFT)
		labelYear.set_line_wrap(True)
		hboxYear.pack_start(labelYear, expand=False)
		labelYear.show()

		hboxGenre = gtk.HBox()
		hboxGenre.set_homogeneous(False)
		vboxDisc.pack_start(hboxGenre, expand=False)
		hboxGenre.show()
		labelGenre = gtk.Label("""<span size='small'>Genre:   {0} </span>""".format(fg(af.get_tag("genre"))))
		labelGenre.set_use_markup(True)
		labelGenre.set_justify(gtk.JUSTIFY_LEFT)
		labelGenre.set_line_wrap(True)
		hboxGenre.pack_start(labelGenre, expand=False)
		labelGenre.show()

		if af.get_tag("composer") and len(af.get_tag("composer")) > 0:
			hboxComposer = gtk.HBox()
			hboxComposer.set_homogeneous(False)
			vboxDisc.pack_start(hboxComposer, expand=False)
			hboxComposer.show()
			labelComposer = gtk.Label("""<span size='small'>Composer:   {0} </span>""".format(af.get_tag("composer")))
			labelComposer.set_use_markup(True)
			labelComposer.set_justify(gtk.JUSTIFY_LEFT)
			labelComposer.set_line_wrap(True)
			hboxComposer.pack_start(labelComposer, expand=False)
			labelComposer.show()

		if af.get_tag("album_artist") and len(af.get_tag("album_artist")) > 0:
			hboxAlbumArtist = gtk.HBox()
			hboxAlbumArtist.set_homogeneous(False)
			vboxDisc.pack_start(hboxAlbumArtist, expand=False)
			hboxAlbumArtist.show()
			labelAlbumArtist = gtk.Label("""<span size='small'>Album artist:   {0} </span>""".format(af.get_tag("album_artist")))
			labelAlbumArtist.set_use_markup(True)
			labelAlbumArtist.set_justify(gtk.JUSTIFY_LEFT)
			labelAlbumArtist.set_line_wrap(True)
			hboxAlbumArtist.pack_start(labelAlbumArtist, expand=False)
			labelAlbumArtist.show()

		if af.get_tag("comment") and len(af.get_tag("comment")) > 0:
			hboxComment = gtk.HBox()
			hboxComment.set_homogeneous(False)
			vboxDisc.pack_start(hboxComment, expand=False)
			hboxComment.show()
			labelComment = gtk.Label("""<span size='small'>Comment:   {0} </span>""".format(af.get_tag("comment")))
			labelComment.set_use_markup(True)
			labelComment.set_justify(gtk.JUSTIFY_LEFT)
			labelComment.set_line_wrap(True)
			hboxComment.pack_start(labelComment, expand=False)
			labelComment.show()

		# Dati sul file (posizione e dimensione)
		hboxLocation = gtk.HBox()
		hboxLocation.set_homogeneous(False)
		self.dlg.vbox.pack_start(hboxLocation, expand=False)
		hboxLocation.show()
		labelLocation = gtk.Label("""<b>Location</b>""")
		labelLocation.set_use_markup(True)
		labelLocation.set_padding(0, 5)
		labelLocation.set_justify(gtk.JUSTIFY_LEFT)
		hboxLocation.pack_start(labelLocation, expand=False, padding=20)
		labelLocation.show()

		if af.get_filename() and len(af.get_filename()) > 0:
			hboxFilename = gtk.HBox()
			hboxFilename.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxFilename, expand=False)
			hboxFilename.show()
			labelFilename = gtk.Label("""<span size='small'>File name:   {0} </span>""".format(af.get_filename()))
			labelFilename.set_use_markup(True)
			labelFilename.set_justify(gtk.JUSTIFY_LEFT)
			labelFilename.set_line_wrap(True)
			hboxFilename.pack_start(labelFilename, expand=False, padding=20)
			labelFilename.show()

		if af.get_foldername() and len(af.get_foldername()) > 0:
			hboxFoldername = gtk.HBox()
			hboxFoldername.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxFoldername, expand=False)
			hboxFoldername.show()
			labelFoldername = gtk.Label("""<span size='small'>Folder name:   {0} </span>""".format(af.get_foldername()))
			labelFoldername.set_use_markup(True)
			labelFoldername.set_justify(gtk.JUSTIFY_LEFT)
			labelFoldername.set_line_wrap(True)
			hboxFoldername.pack_start(labelFoldername, expand=False, padding=20)
			labelFoldername.show()

		'''if len(af.get_filepath()) > 0:
			hboxFilepath = gtk.HBox()
			hboxFilepath.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxFilepath, expand=False)
			hboxFilepath.show()
			labelFilepath = gtk.Label("""<span size='small'>File path:   {0} </span>""".format(af.get_filepath()))
			labelFilepath.set_use_markup(True)
			labelFilepath.set_justify(gtk.JUSTIFY_LEFT)
			hboxFilepath.pack_start(labelFilepath, expand=False, padding=20)
			labelFilepath.show()'''

		if af.get_filesize() and af.get_filesize() > 0:
			hboxFilesize = gtk.HBox()
			hboxFilesize.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxFilesize, expand=False)
			hboxFilesize.show()
			labelFilesize = gtk.Label("""<span size='small'>File size:   %0.2f MB (%0.0f bytes) </span>""" %(float(af.get_filesize())/1048576, af.get_filesize()))
			labelFilesize.set_use_markup(True)
			labelFilesize.set_justify(gtk.JUSTIFY_LEFT)
			labelFilesize.set_line_wrap(True)
			hboxFilesize.pack_start(labelFilesize, expand=False, padding=20)
			labelFilesize.show()

		if af.get_mime_type() and  len(af.get_mime_type())> 0:
			hboxMime = gtk.HBox()
			hboxMime.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxMime, expand=False)
			hboxMime.show()
			labelMine = gtk.Label("""<span size='small'>File type:   %s </span>""" %(af.get_mime_type()))
			labelMine.set_use_markup(True)
			labelMine.set_justify(gtk.JUSTIFY_LEFT)
			labelMine.set_line_wrap(True)
			hboxMime.pack_start(labelMine, expand=False, padding=20)
			labelMine.show()

		# Dati sull'audio
		hboxAudio = gtk.HBox()
		hboxAudio.set_homogeneous(False)
		self.dlg.vbox.pack_start(hboxAudio, expand=False)
		hboxAudio.show()
		if af.get_video_codec() and len(af.get_video_codec()) > 0:
			labelAudio = gtk.Label("""<b>Audio/Video</b>""")
		else:
			labelAudio = gtk.Label("""<b>Audio</b>""")
		labelAudio.set_use_markup(True)
		labelAudio.set_padding(0, 5)
		labelAudio.set_justify(gtk.JUSTIFY_LEFT)
		hboxAudio.pack_start(labelAudio, expand=False, padding=20)
		labelAudio.show()

		# Durata
		if af.get_duration() and af.get_duration() > 0:
			hboxDuration = gtk.HBox()
			hboxDuration.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxDuration, expand=False)
			hboxDuration.show()
			labelDuration = gtk.Label("""<span size='small'>Duration:   %s (%0.2f s) </span>""" %(af.get_duration_mm_ss(), af.get_duration()))
			labelDuration.set_use_markup(True)
			labelDuration.set_justify(gtk.JUSTIFY_LEFT)
			labelDuration.set_line_wrap(True)
			hboxDuration.pack_start(labelDuration, expand=False, padding=20)
			labelDuration.show()

		# Codec
		if af.get_audio_codec() and len(af.get_audio_codec()) > 0:
			hboxCodec = gtk.HBox()
			hboxCodec.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxCodec, expand=False)
			hboxCodec.show()
			labelCodec = gtk.Label("""<span size='small'>Codec:   %s</span>""" %(af.get_audio_codec()))
			labelCodec.set_use_markup(True)
			labelCodec.set_justify(gtk.JUSTIFY_LEFT)
			labelCodec.set_line_wrap(True)
			hboxCodec.pack_start(labelCodec, expand=False, padding=20)
			labelCodec.show()

		# Eventuale codec video
		if af.get_video_codec() and len(af.get_video_codec()) > 0:
			hboxVideoCodec = gtk.HBox()
			hboxVideoCodec.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxVideoCodec, expand=False)
			hboxVideoCodec.show()
			labelVideoCodec = gtk.Label("""<span size='small'>Video codec:   %s</span>""" %(af.get_video_codec()))
			labelVideoCodec.set_use_markup(True)
			labelVideoCodec.set_justify(gtk.JUSTIFY_LEFT)
			labelVideoCodec.set_line_wrap(True)
			hboxVideoCodec.pack_start(labelVideoCodec, expand=False, padding=20)
			labelVideoCodec.show()

		# Container
		if af.get_container() and len(af.get_container()) > 0 and not af.get_container() == "Tag ID3":
			hboxContainer = gtk.HBox()
			hboxContainer.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxContainer, expand=False)
			hboxContainer.show()
			labelContainer = gtk.Label("""<span size='small'>Container:   %s</span>""" %(af.get_container()))
			labelContainer.set_use_markup(True)
			labelContainer.set_justify(gtk.JUSTIFY_LEFT)
			labelContainer.set_line_wrap(True)
			hboxContainer.pack_start(labelContainer, expand=False, padding=20)
			labelContainer.show()

		# Encoder
		if af.get_encoder() and len(af.get_encoder()) > 0:
			hboxEncoder = gtk.HBox()
			hboxEncoder.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxEncoder, expand=False)
			hboxEncoder.show()
			labelEncoder = gtk.Label("""<span size='small'>Encoder:   %s</span>""" %(af.get_encoder()))
			labelEncoder.set_use_markup(True)
			labelEncoder.set_justify(gtk.JUSTIFY_LEFT)
			labelEncoder.set_line_wrap(True)
			hboxEncoder.pack_start(labelEncoder, expand=False, padding=20)
			labelEncoder.show()

		# Bitrate
		if af.get_bitrate() and af.get_bitrate() > 0:
			hboxBitrate = gtk.HBox()
			hboxBitrate.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxBitrate, expand=False)
			hboxBitrate.show()
			labelBitrate = gtk.Label("""<span size='small'>Bitrate:   %s kbit/s </span>""" %(af.get_bitrate()/1000))
			labelBitrate.set_use_markup(True)
			labelBitrate.set_justify(gtk.JUSTIFY_LEFT)
			labelBitrate.set_line_wrap(True)
			hboxBitrate.pack_start(labelBitrate, expand=False, padding=20)
			labelBitrate.show()

		# Canali
		if af.get_num_channels() and af.get_num_channels() > 0:
			hboxChannels = gtk.HBox()
			hboxChannels.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxChannels, expand=False)
			hboxChannels.show()
			if af.get_channel_mode() and len(af.get_channel_mode()) > 0:
				labelChannels = gtk.Label("""<span size='small'>Channels:   %s (%s)</span>""" %(af.get_num_channels(), af.get_channel_mode()))
			else:
				labelChannels = gtk.Label("""<span size='small'>Channels:   %s </span>""" %(af.get_num_channels()))
			labelChannels.set_use_markup(True)
			labelChannels.set_justify(gtk.JUSTIFY_LEFT)
			labelChannels.set_line_wrap(True)
			hboxChannels.pack_start(labelChannels, expand=False, padding=20)
			labelChannels.show()

		# Dimensione del campione
		if af.get_sampwidth_b() and af.get_sampwidth_b() > 0:
			hboxSampleWidth = gtk.HBox()
			hboxSampleWidth.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxSampleWidth, expand=False)
			hboxSampleWidth.show()
			labelSampleWidth = gtk.Label("""<span size='small'>Sample width:   %s bit </span>""" %(af.get_sampwidth_b()))
			labelSampleWidth.set_use_markup(True)
			labelSampleWidth.set_justify(gtk.JUSTIFY_LEFT)
			labelSampleWidth.set_line_wrap(True)
			hboxSampleWidth.pack_start(labelSampleWidth, expand=False, padding=20)
			labelSampleWidth.show()

		# Frequenza di campionamento
		if af.get_framerate() and af.get_framerate() > 0:
			hboxSampleRate = gtk.HBox()
			hboxSampleRate.set_homogeneous(False)
			self.dlg.vbox.pack_start(hboxSampleRate, expand=False)
			hboxSampleRate.show()
			labelSampleRate = gtk.Label("""<span size='small'>Sample rate:   %s Hz </span>""" %(af.get_framerate()))
			labelSampleRate.set_use_markup(True)
			labelSampleRate.set_justify(gtk.JUSTIFY_LEFT)
			labelSampleRate.set_line_wrap(True)
			hboxSampleRate.pack_start(labelSampleRate, expand=False, padding=20)
			labelSampleRate.show()
   
	# Attiva e visualizza la finestra di dialogo
	def show(self, *args):

		self.dlg.run()
		self.dlg.destroy()

	# Carica i tag del brano successivo
	def on_Next(self, *args):

		for w in self.dlg.vbox:
			if not isinstance(w, gtk.HButtonBox):
				self.dlg.vbox.remove(w)

		model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()
		rowpath = pathlist[0]
		self.mainapp.FileTable.tvSelection.unselect_all()
		it = self.mainapp.FileTable.listStore.get_iter(rowpath)
		root_it = self.mainapp.FileTable.listStore.get_iter_root()
		next_it = self.mainapp.FileTable.listStore.iter_next(it)
		if next_it:
			self.mainapp.FileTable.tvSelection.select_iter(next_it)
		else:
			try:
				self.mainapp.FileTable.tvSelection.select_iter(root_it)
			except:
				pass
		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Carica i tag del brano precedente
	def on_Previous(self, *args):

		for w in self.dlg.vbox:
			if not isinstance(w, gtk.HButtonBox):
				self.dlg.vbox.remove(w)

		model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()
		if len(pathlist) > 0:
			rowpath = pathlist[0]
			self.mainapp.FileTable.tvSelection.unselect_all()
			prev_pointer = 0
			prev_it = None
			curr_it = self.mainapp.FileTable.listStore.get_iter(rowpath)
			for af in self.mainapp.audioFileList.filelist:
				if str(af.pointer) == model.get_string_from_iter(curr_it):
					prev_pointer = af.pointer - 1
			if prev_pointer > -1:
				self.mainapp.FileTable.tvSelection.select_all()
				model, pathlist = self.mainapp.FileTable.tvSelection.get_selected_rows()

				if pathlist:
					iterlist = []
					for rowpath in pathlist:
						try:
							iterlist.append(model.get_iter(rowpath))
						except ValueError:
							pass
					for it in iterlist:
						if str(prev_pointer) == model.get_string_from_iter(it):
							prev_it = it
					if prev_it:
						self.mainapp.FileTable.tvSelection.unselect_all()
						self.mainapp.FileTable.tvSelection.select_iter(prev_it)
					else:
						self.mainapp.FileTable.tvSelection.unselect_all()
						self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())
			else:
				self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())
		else:
			self.mainapp.FileTable.tvSelection.select_iter(self.mainapp.FileTable.listStore.get_iter_root())

		self.load_tags(self.mainapp.Selection(self.mainapp.FileTable)[0])

	# Chiude e salva tutte le preferenze
	def on_Ok(self, *args):

		self.dlg.destroy()
