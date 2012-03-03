#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class HelloWorld:
    
    def __init__(self):

        self.builderXAC = gtk.Builder()
        self.builderXAC.add_from_file('xaudiocopy.glade')

        self.CDDBdisc = [["A", "Giorgio", "Franceschi"],
                    ["B", "Sandra", "Melina"],
                    ["C", "Luigi", "Franceschi"]]
        
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
        dlg = classCDDBSelection(self.mainWindow, self.CDDBdisc)
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


### Finestra di dialogo per la selezione dei CD da freeDB ###
class classCDDBSelection:

    # Costruttore della classe
    def __init__(self, main_window, CDDBdisc):

        # Inizilizza la variabile
        self.selected_cd = None

        # Finestra di dialogo
        #self.dlgCDDBSelection = gtk.Dialog("Select CD...", main_window,
        #             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        #            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.dlgCDDBSelection = gtk.Dialog("Select CD from freeDB...", main_window,
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.dlgCDDBSelection.set_default_size(410, 60)
        self.dlgCDDBSelection.set_border_width(5)

        # Box verticale
        self.vbox = self.dlgCDDBSelection.vbox
        self.vbox.set_spacing(2)

        # Etichetta (posizione 1 nella VBox)
        self.labelCDDB = gtk.Label("Several exact matches found. Plese select your CD")
        self.labelCDDB.set_alignment(0, 0.5)
        self.labelCDDB.set_padding(10, 10)
        self.dlgCDDBSelection.vbox.add(self.labelCDDB)
        self.labelCDDB.show()

        # TreeView (posizione 2 nella VBox)
        self.tvSelectCD = gtk.TreeView()
        self.tvSelectCD.connect("row-activated", self.on_CD_selected)
        self.dlgCDDBSelection.vbox.add(self.tvSelectCD)
        self.tvSelectCD.show()

        # Pulsante OK
        self.cmdOKCDDB = gtk.Button(label="_Ok", use_underline=True)
        self.cmdOKCDDB.connect("clicked", self.on_CD_selected)
        self.dlgCDDBSelection.add_action_widget(self.cmdOKCDDB, 1)
        self.cmdOKCDDB.show()
        #self.action_area1.show()

        # Colonne del TreeView
        cell = gtk.CellRendererText()
        column0 = gtk.TreeViewColumn("Disc ID", cell, text=0)
        column1 = gtk.TreeViewColumn("Category", cell, text=1)
        column2 = gtk.TreeViewColumn("Artist / Title", cell, text=2)
        self.tvSelectCD.append_column(column0)
        self.tvSelectCD.append_column(column1)
        self.tvSelectCD.append_column(column2)

        # Selezione
        self.selectCD = self.tvSelectCD.get_selection()

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
