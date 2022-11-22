# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Open Symos
			A QGIS plugin
 Calculates pollutants concentration according to SYMOS methodology.
 This plugin was developed by Jan Ruzicka and Katerina Ruzickova.
 The plugin is baed on Open Symos software developed by Karel Psota.
                             -------------------
        begin                : 2016-12-19
        copyright            : (C) 2016 by Jan Ruzicka, Katerina Ruzickova, Radek Furmanek, Ondrej Kolodziej
        email                : jan.ruzicka.vsb@gmail.com, katerina.ruzickova@vsb.cz

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import uuid
import tempfile
from shutil import copyfile
from qgis.core import *
from .main import Main

from PyQt5 import QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'jaster_polluted_source_preparation.ui'))


class Formular(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Formular, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.iface = iface
        self.EntryDialog = Formular()

    def AreaSelection(self):
        # Otevření dialogového okna
        self.EntryDialog.exec()
        # Zjištění, kam chce uživatel uložit výstup (výsledný soubor)
        Output = self.EntryDialog.FileOutput.filePath()
        # Zjištění adresáře, kam chce uživatel uložit výstup (bez jména souboru, jen adresář)
        self.location = os.path.dirname(Output)

        # Zjištení jakou vrstvu uživatel vybral v rozbalovacím seznamu vrstev na formuláři
        self.layer = (self.EntryDialog.VyberVrstvu.currentLayer())
        QgsMessageLog.logMessage("Zpracovávaná/vybraná vrstva: " + self.layer.name(), "Messages")
        # Získání všech geoprvků z vybrané vrstvy (seznam)
        areas = self.layer.getFeatures()
        self.SelectedAreas = []
        self.CurrentPosition = 0



        # Otevření výstupního souboru
        with open(Output, mode='w', encoding='utf-8') as soubor:
            # Procházení seznamu všech geoprvků/parcel
            for area in areas:
                print("<p> " + str(area["Id"]) + " - " + " <img src=area_" + str(area["Id"]) + ".png width=300/></p>\n", file=soubor)
        # Volání metody přiblížení na parcelu
        self.ZoomToArea()
        QgsMessageLog.logMessage("Výsledek byl uložen do: " + str(Output), "Messages")


        # Metoda pro přiblížení na parcelu
    def ZoomToArea(self):
        # Zjištění plošného rozsahu vybrané parcely
        zoom = self.SelectedAreas[self.CurrentPosition].geometry().boundingBox()
        # Přiblížení na rozsah vybrané parcely
        self.iface.mapCanvas().setExtent(zoom)
        self.iface.mapCanvas().refresh()
        # Volání metody exportMap s 1s zpožděním (aby se stihlo mapové pole překreslit)
        QTimer.singleShot(1000,self.ExportView)

    def ExportView(self):
        # Uložení obrázku mapového pole (pojmenování obr. dle id aktuálně zpracovávané parcely)
        self.iface.mapCanvas().saveAsImage(self.location + "\area_" + str(self.SelectedAreas[self.CurrentPosition]["Id"]) + ".png")
        # Posun pozice (v seznamu vybraných parcel) na další
        self.CurrentPosition = self.CurrentPosition + 1
        # Pokud není na konci seznamu vybraných parcel, pak se volá přiblížení na další parcelu (s 1s zpožděním)
        if self.CurrentPosition < len(self.SelectedAreas):
            QTimer.singleShot(1000,self.ZoomToArea)