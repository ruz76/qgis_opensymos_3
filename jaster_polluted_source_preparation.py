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

from qgis.core import QgsMessageLog
from qgis.gui import *


# for polygon in vrstva
#     boundingbox každeho polygonu
#     zistiť tie emisii v tych poygonoch
#     metoda na vygenerovanie pravidelneho gridu buniek (10*10) v tom boudingboxu, podľa prekryvu s pôvodným poylgonom, kde 1 sa vytvorí bunka a 0 nie
#     zmeniť bunky na body (seznam bodov ktore su vnutri boundindBoxu polygonu)
#     emisia na polygon / body
# zapísať hodnotu emisie na bode do nového stĺpca / prepísať pôvodný stlpec emisie
# export novej bodovej vrstvy s tym novou hodnotou emisii



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
        self.setupUi(self)
        self.VyberVrstvu.layerChanged.connect(self.SelectLayerFields)

    # def AreaSelection(self):
    #     # Otevření dialogového okna
    #     self.dlgFormular.exec()
    #     # Zjištění, kam chce uživatel uložit výstup (výsledný soubor)
    #     Output = self.dlgFormular.FileOutput.filePath()
    #     # Zjištění adresáře, kam chce uživatel uložit výstup (bez jména souboru, jen adresář)
    #     self.location = os.path.dirname(Output)
    #
    #     # Zjištení jakou vrstvu uživatel vybral v rozbalovacím seznamu vrstev na formuláři
    #     self.layer = (self.VyberVrstvu.currentLayer())
    #     QgsMessageLog.logMessage("Zpracovávaná/vybraná vrstva: " + self.layer.name(), "Messages")
    #     # Zjištení jaký druh parcely uživatel vybral v rozbalovacím seznamu na formuláři
    #     #AreaType = self.dlgFormular.VyberAtribut.currentText()



    def SelectLayerFields(self):
        self.layer = (self.VyberVrstvu.currentLayer())
        self.VyberAtribut.setLayer(self.VyberVrstvu.currentLayer())

    # Získání všech geoprvků z vybrané vrstvy (seznam)
        areas = self.layer.getFeatures()
        self.SelectedAreas = []
        self.CurrentPosition = 0


       # for polygon in self.layer:

        layer = self.layer
        newlayer = QgsVectorLayer("Polygon?crs={}&index=yes".format(layer.crs().authid()), "BoundingBoxes", "memory")

        with edit(newlayer):
            newlayer.dataProvider().addAttributes(layer.fields()) # copy the fields to the outputlayer
            newlayer.updateFields() # save the changes
            for polygon in layer.getFeatures(): # iterate over inputlayer
                bbox = polygon.geometry().boundingBox() # get the Boundingbox as QgsRectangle
                bbox_geom = QgsGeometry.fromRect(bbox) # Turn the QgsRectangle into QgsGeometry
                outpolygon = QgsFeature() # Create a new feature
                outpolygon.setAttributes(polygon.attributes()) # copy the attributes to the outputlayer
                outpolygon.setGeometry(bbox_geom) # set the geometry of the outputfeature to the bbox of the inputfeature
                newlayer.dataProvider().addFeature(outpolygon) # add the feature to the outputlayer

        QgsProject.instance().addMapLayer(newlayer)

        # Otevření výstupního souboru
        Output = self.FileOutput.filePath()
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