#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import subprocess
import pygtk
import gtk
import gobject
import threading
import time
import os


class RipThread(threading.Thread):
    def __init__(self, mainview):
        threading.Thread.__init__(self)
        self.mainview = mainview

    def run(self):
        self.work_complete = False
	self.amount_completed = 0
        gobject.timeout_add(100, self.mainview.update_bar)

class Encoder(threading.Thread):
    def __init__(self, mainview):
        threading.Thread.__init__(self)
        self.mainview = mainview

    def run(self):
		self.sizewav=os.path.getsize('/home/giorgio/Musica/01 Carioca.wav')
		print "Dimensione wav: ", self.sizewav
		self.process=subprocess.Popen(['lame', '--silent', '-V0', '/home/giorgio/Musica/01 Carioca.wav', '/home/giorgio/Musica/01 Carioca.mp3'], shell=False, stdout=subprocess.PIPE)

		self.comp_rate=6.5

		while 1:
			if self.process.poll() == 0:
				self.mainview.worker.work_complete = True
				break
			else:
				try:
					sizemp3=os.path.getsize('/home/giorgio/Musica/01 Carioca.mp3')
					print "Dimensione mp3: ", sizemp3
					perc=float(sizemp3)/float(self.sizewav)*self.comp_rate
					print "Percentuale: ", perc
					if perc > 1:
						perc = 0
				except: pass
				time.sleep(0.2)
				try:
					self.mainview.worker.amount_completed = perc
				except: pass
		#self.c=self.process.communicate()[0]
		#print self.process.stdout.readline()
		#self.mainviewtb.set_text(self.c)

class classTest:

	def __init__(self):
		dlg = gtk.Dialog("Prova testo", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK, gtk.RESPONSE_CANCEL))
		dlg.show()

		t=gtk.Label()
		dlg.vbox.add(t)
		t.show()
		t.set_text("Encoding...")

		self.tb=gtk.TextBuffer()
		tv=gtk.TextView(self.tb)
		dlg.vbox.add(tv)
		tv.show()

		self.progressbar = gtk.ProgressBar()
		dlg.vbox.add(self.progressbar)
		self.progressbar.set_fraction(0)
		self.progressbar.show()

		self.worker = RipThread(self)
       		
		self.sizewav=os.path.getsize('/home/giorgio/Musica/01 Carioca.wav')
		print "Dimensione wav: ", self.sizewav
		self.process=subprocess.Popen(['lame', '--silent', '-V0', '/home/giorgio/Musica/01 Carioca.wav', '/home/giorgio/Musica/01 Carioca.mp3'], shell=False, stdout=subprocess.PIPE)
		self.worker.start()

		self.comp_rate=6.5

		while 1:
			if self.process.poll() == 0:
				self.worker.work_complete = True
				break
			else:
				try:
					sizemp3=os.path.getsize('/home/giorgio/Musica/01 Carioca.mp3')
					print "Dimensione mp3: ", sizemp3
					perc=float(sizemp3)/float(self.sizewav)*self.comp_rate
					print "Percentuale: ", perc
					if perc > 1:
						perc = 0
				except: pass
				time.sleep(0.2)
				try:
					self.worker.amount_completed = perc
				except: pass

	def update_bar(self):
	        self.progressbar.set_fraction(self.worker.amount_completed)
	        if self.worker.work_complete:
		    self.progressbar.set_fraction(1)
	            self.progressbar.set_text("Complete!")
	        else:
	            self.progressbar.set_text("%d%%" % (self.worker.amount_completed * 100))
	        return not self.worker.work_complete

	def main(self):
		gtk.main()

### Main ###
if __name__ == "__main__" :
	gobject.threads_init()
	test = classTest()
	test.main()
