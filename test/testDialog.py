#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class HelloWorld:
    
    def __init__(self):

        self.builderXAC = gtk.Builder()
        self.builderXAC.add_from_file('xaudiocopy.glade')

        self.CDDBdisc = [["01", "Giorgio", "Franceschi"],
                    ["02", "Sandra", "Melina"],
                    ["03", "Luigi", "Franceschi"]]
        
        # create a new window
        self.mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        self.mainWindow.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.mainWindow.set_default_size(210, 60)
        self.mainWindow.set_border_width(10)
        self.mainWindow.connect("destroy", self.destroy)
        self.mainWindow.connect("delete_event", self.delete_event)
        
        self.hbuttonbox=gtk.HButtonBox()
        self.mainWindow.add(self.hbuttonbox)
        
        self.cmdOK = gtk.Button(label="_Ok", use_underline=True)
        self.cmdOK.connect("clicked", self.on_ok, None)
        self.hbuttonbox.add(self.cmdOK)
        self.cmdOK.show()
        
        self.cmdCancel = gtk.Button(label="_Cancel", use_underline=True)
        self.cmdCancel.connect("clicked", self.on_quit, None)
        self.hbuttonbox.add(self.cmdCancel)
        self.cmdCancel.show()
        
        self.hbuttonbox.show()
        self.mainWindow.show()
        
    def on_quit(self, *args):
        print "on_quit occurred"
        gtk.main_quit()
        
    def on_ok(self, *args):
        print "on_ok occurred: Hello World"
        self.mainWindow.set_title("Hello World")
        dlg = classCDDBSelection(self.builderXAC, self.CDDBdisc)
        print dlg.selected_cd
        dlg.dlgCDDBSelection.destroy()
        
    def delete_event(self, widget, data=None):
        print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def main(self):
        gtk.main()


### Finestra di dialogo per la selezione dei CD da CDDB ###
class classCDDBSelection:

    # Costruttore della classe
    def __init__(self, builderXAC, CDDBdisc):

        self.dlgCDDBSelection = builderXAC.get_object("dlgCDDBSelection")
        print "dlgCDDBSelection: ", self.dlgCDDBSelection
        
        self.dlgCDDBSelection.set_title("Select CD...")

        self.tvSelectCD = builderXAC.get_object("tvSelectCD")
        self.tvSelectCD.connect("row-activated", self.on_CD_selected)

        self.cmdOKCDDB = builderXAC.get_object("cmdOKCDDB")
        self.cmdOKCDDB.connect("clicked", self.on_CD_selected)

        self.labelCDDB = builderXAC.get_object("labelCDDB")
        self.labelCDDB.set_text("Several exact matches found. Plese select your CD")
        
        cell = gtk.CellRendererText()
        column0 = gtk.TreeViewColumn("Disc ID", cell, text=0)
        column1 = gtk.TreeViewColumn("Category", cell, text=1)
        column2 = gtk.TreeViewColumn("Artist / Title", cell, text=2)
        self.tvSelectCD.append_column(column0)
        self.tvSelectCD.append_column(column1)
        self.tvSelectCD.append_column(column2)

        self.selectCD = self.tvSelectCD.get_selection()
        #self.selectCD.set_mode(gtk.SELECTION_SINGLE)

        # Crea il modello ListStore con il contenuto della tabella
        self.cdList = gtk.ListStore(str, str, str)
        # Lo collega al TreeView 
        self.tvSelectCD.set_model(self.cdList)

        for cd in CDDBdisc:
            # Popola di dati le righe
            self.cdList.append(cd)

        # Attiva e visualizza la finestra di dialogo
        self.dlgCDDBSelection.run()

    def on_CD_selected(self, *args):

        model, row_iter = self.selectCD.get_selected()
        print "model: ", model
        print "row: ", row_iter
        if not row_iter:
            row_iter = self.cdList.get_iter_root()
        self.selected_cd = self.cdList.get_string_from_iter(row_iter)
        print self.selected_cd

        builderXAC = None
        self.dlgCDDBSelection.destroy()

if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
