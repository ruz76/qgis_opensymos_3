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

from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
import processing

# for polygon in vrstva
#     zistiť tie emisie v tych poygonoch
#     emisia na polygon / body
# zapísať hodnotu emisie na bode do nového stĺpca
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
        cell_size = int(self.spinBox.value())
        self.SelectedAreas = []
        self.CurrentPosition = 0
        layer = self.layer


        # vyber_atributu = (self.VyberAtribut.setLayer(self.VyberVrstvu.currentLayer()))
        #
        # features = vyber_atributu.getFeatures()
        #
        # attrs = features.attributes()
        # var = attrs[1]
        # QgsMessageLog.logMessage("Hodnota atributu: ", str(var),  "Messages")



        # for atribut in emise:
        #     count_atributes = sum(int(self.VyberAtribut.value()))
        # QgsMessageLog.logMessage("Suma čísel zo zvoleného atributu: ", str(count_atributes),  "Messages")
        # #atributes = int(self.VyberAtribut.value())


        #cellsize = 100 #Cell Size in WGS 84 will be 100 x 100 meters
        for polygon in self.layer:

            crs = QgsProject().instance().crs().toWkt() #WGS 84 System
            #input = layer #Use the processing.getObject to get information from our vector layer
            xmin = (polygon.extent().xMinimum()) #extract the minimum x coord from our layer
            xmax = (polygon.extent().xMaximum()) #extract our maximum x coord from our layer
            ymin = (polygon.extent().yMinimum()) #extract our minimum y coord from our layer
            ymax = (polygon.extent().yMaximum()) #extract our maximum y coord from our layer
            #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
            extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
        #processing.run('qgis:vectorgrid', extent, cellsize, cellsize, 0, grid)
            grid_creation = processing.run("native:creategrid", {'TYPE':0,'EXTENT': extent,
                                                             'HSPACING':cellsize,'VSPACING':cell_size,
                                                             'HOVERLAY':0,'VOVERLAY':0,'CRS': crs,'OUTPUT': 'memory'})
            grid = QgsVectorLayer(grid_creation['OUTPUT'], 'grid', 'ogr')

        #novy grid podle zvolene vrstvy (pouziti fce intersect)
        grid_create2 = processing.run("native:intersection",
                       {'INPUT': grid, 'OVERLAY': layer,
                        'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [], 'OVERLAY_FIELDS_PREFIX': '',
                        'OUTPUT': 'TEMPORARY_OUTPUT', 'GRID_SIZE': None})
        finalgrid = grid_create2['OUTPUT']
        finalgrid.setName('Terka_is_Best')
        QgsMessageLog.logMessage("Finálny grid je hotový.", "Messages")
        QgsProject.instance().addMapLayer(finalgrid)

        #prida novy atribut emise
        layer_provider = finalgrid.dataProvider()
        layer_provider.addAttributes([QgsField("emise", QVariant.Double)])
        finalgrid.updateFields()
        print(finalgrid.fields().names())

        # vypocita hodnoty v atributu emise (nejde)
        # expression = QgsExpression ('DruhPozemk'/10)
        # index = finalgrid.fieldNameIndex("emise")
        # expression.prepare(finalgrid.pendingFields())
        # finalgrid.startEditing()
        # for feature in finalgrid.getFeatures():
        #     value = expression.evaluate(feature)
        #     finalgrid.changeAttributeValue(feature.id(), index, value)
        #
        # finalgrid.commitChanges()


# Otevření výstupního souboru
        Output = self.FileOutput.filePath()
        with open(Output, mode='w', encoding='utf-8') as soubor:
            # Procházení seznamu všech geoprvků/parcel
            for area in areas:
                print("<p> " + str(area["Id"]) + " - " + " <img src=area_" + str(area["Id"]) + ".png width=300/></p>\n", file=soubor)
        QgsMessageLog.logMessage("Výsledek byl uložen do: " + str(Output), "Messages")

    def ExportView(self):
        # Uložení obrázku mapového pole (pojmenování obr. dle id aktuálně zpracovávané parcely)
        self.iface.mapCanvas().saveAsImage(self.location + "\area_" + str(self.SelectedAreas[self.CurrentPosition]["Id"]) + ".png")