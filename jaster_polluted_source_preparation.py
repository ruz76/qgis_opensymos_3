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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'jaster_polluted_source_preparation.ui'))

class Formular(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Formular, self).__init__(parent)
        self.setupUi(self)
        self.VyberVrstvu.layerChanged.connect(self.ChangeLayer)
        self.pushButton.clicked.connect(self.PolygonToPoints)

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

    def ChangeLayer(self):
        self.layer = (self.VyberVrstvu.currentLayer())
        self.VyberAtribut.setLayer(self.VyberVrstvu.currentLayer())
        if self.pushButton.clicked:
            QgsMessageLog.logMessage("Spustení aplikace nad vrstvou: " + self.layer.name(), "Messages")

    def PolygonToPoints(self):
        atribut = self.VyberAtribut.currentField()
        areas = self.layer.getFeatures()
        cell_size = int(self.spinBox.value())
        self.SelectedAreas = []
        self.CurrentPosition = 0
        layer = self.layer
        if self.pushButton.clicked:
            QgsMessageLog.logMessage("Velikost gridové buňky: " + str(cell_size), "Messages")
            QgsMessageLog.logMessage("Rozdělení emisí z atributu: " + str(atribut), "Messages")

        crs = QgsProject().instance().crs().toWkt()
        input = layer
        xmin = (input.extent().xMinimum()) #extract the minimum x coord from our layer
        xmax = (input.extent().xMaximum())
        ymin = (input.extent().yMinimum())
        ymax = (input.extent().yMaximum())
        extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
        grid_creation = processing.run("native:creategrid", {'TYPE':0,'EXTENT': extent,
                                                             'HSPACING':cell_size,'VSPACING':cell_size,
                                                             'HOVERLAY':0,'VOVERLAY':0,'CRS': crs,'OUTPUT': 'memory'})
        grid = QgsVectorLayer(grid_creation['OUTPUT'], 'grid', 'ogr')
        #QgsMessageLog.logMessage("Bodový Grid je hotový.", "Messages")
        #QgsProject.instance().addMapLayer(grid)


        create_count = processing.run("native:countpointsinpolygon", {'POLYGONS': layer,'POINTS': grid,
                                                                      'WEIGHT':'','CLASSFIELD':'','FIELD':'NUMPOINTS',
                                                                      'OUTPUT':'TEMPORARY_OUTPUT'})
        count = create_count['OUTPUT']
        count.setName('count')
        #QgsMessageLog.logMessage("Prekryt polygonov s centroidmi je hotový.", "Messages")
        #QgsProject.instance().addMapLayer(count)

        grid_create2 = processing.run("native:intersection",
                       {'INPUT': grid, 'OVERLAY': count,
                        'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [], 'OVERLAY_FIELDS_PREFIX': '',
                        'OUTPUT': 'TEMPORARY_OUTPUT', 'GRID_SIZE': None})
        finalgrid = grid_create2['OUTPUT']
        finalgrid.setName('emise')
        QgsMessageLog.logMessage("Finální vrstva emisí uložena v projektu.", "Messages")
        QgsProject.instance().addMapLayer(finalgrid)

        prov = finalgrid.dataProvider()
        fld = QgsField('emise', QVariant.Double, "double", 10, 2)
        prov.addAttributes([fld])
        finalgrid.updateFields()
        idx = finalgrid.fields().lookupField('emise')
        #print(count.fields().names())

        finalgrid.startEditing()
        vzorec = atribut + ' / NUMPOINTS'

        e = QgsExpression(vzorec)
        c = QgsExpressionContext()
        s = QgsExpressionContextScope()
        s.setFields(finalgrid.fields())
        c.appendScope(s)
        e.prepare(c)

        for f in finalgrid.getFeatures():
            c.setFeature(f)
            value = e.evaluate(c)
            atts = {idx: value}
            finalgrid.dataProvider().changeAttributeValues({f.id(): atts})
        finalgrid.commitChanges()

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

            QgsMessageLog.logMessage("Výsledek byl uložen do: " + str(vystupniSoubor), "Messages")