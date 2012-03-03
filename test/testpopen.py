import subprocess, shlex
import pygtk
import gtk
import time

class Converter:

	def main(self):
		gtk.main()

	def __init__(self):
		self.dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, "Conversione di un file mp3...")
		self.dlg.set_title("Convertire?")
		self.dlg.show()

		lame_string = str('lame --silent "/media/GIORGIO/Sviluppo/Musica/As Cidades/01 Carioca.wav" "/home/giorgio/Musica/carioca.mp3"')
		print lame_string
		lame_args = shlex.split(lame_string)

		self.popen = subprocess.Popen(lame_args, preexec_fn=self.Converting())

		while 1:
			if not self.popen.poll() == 0:
				print "Ok: ", self.popen.poll()
				time.sleep(2)
			elif self.popen.poll() == 0:
				print "Else: ", self.popen.poll()
				break
		self.dlg.set_title("Fatto")


		#self.dlg.destroy()


	def Converting(self):
		self.dlg.set_title("Conversione in corso...")
		self.dlg.run()



### Main ###
if __name__ == "__main__" :
	c=Converter()


