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

from qgis.PyQt.QtCore import QVariant



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
        #self.VyberVrstvu.connect(self.AreaSelection())
        #self.FileOutput.clicked.connect(self.AreaSelection())
        #self.FileOutput.clicked.connect(self.ZoomToArea())
        #self.FileOutput.clicked.connect(self.ExportView())

    def AreaSelection(self):
        # Otevření dialogového okna
        self.dlgFormular.exec()
        # Zjištění, kam chce uživatel uložit výstup (výsledný soubor)
        Output = self.dlgFormular.FileOutput.filePath()
        # Zjištění adresáře, kam chce uživatel uložit výstup (bez jména souboru, jen adresář)
        self.location = os.path.dirname(Output)

        # Zjištení jakou vrstvu uživatel vybral v rozbalovacím seznamu vrstev na formuláři
        self.layer = (self.dlgFormular.VyberVrstvu.currentLayer())
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



    def cut_polygon_into_windows(self, p, window_height, window_width):
        self.layer = (self.dlgFormular.VyberVrstvu.currentLayer())

        crs = p.crs().toWkt()
        extent = p.extent()
        (xmin, xmax, ymin, ymax) = (extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum())

        # Create the grid layer
        vector_grid = QgsVectorLayer('Polygon?crs='+ crs, 'vector_grid' , 'memory')
        prov = vector_grid.dataProvider()

        # Create the grid layer
        output = QgsVectorLayer('Polygon?crs='+ crs, 'output' , 'memory')
        outprov = output.dataProvider()

        # Add ids and coordinates fields
        fields = QgsFields()
        fields.append(QgsField('ID', QVariant.Int, '', 10, 0))
        outprov.addAttributes(fields)

        # Generate the features for the vector grid
        id = 0
        y = ymax
        while y >= ymin:
            x = xmin
            while x <= xmax:
                point1 = QgsPoint(x, y)
                point2 = QgsPoint(x + window_width, y)
                point3 = QgsPoint(x + window_width, y - window_height)
                point4 = QgsPoint(x, y - window_height)
                vertices = [point1, point2, point3, point4] # Vertices of the polygon for the current id
                inAttr = [id]
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry().fromPolygon([vertices])) # Set geometry for the current id
                feat.setAttributes(inAttr) # Set attributes for the current id
                prov.addFeatures([feat])
                x = x + window_width
                id += 1
            y = y - window_height

        index = QgsSpatialIndex() # Spatial index
        for ft in vector_grid.getFeatures():
            index.insertFeature(ft)

        for feat in p.getFeatures():
            geom = feat.geometry()
            idsList = index.intersects(geom.boundingBox())
            for gridfeat in vector_grid.getFeatures(QgsFeatureRequest().setFilterFids(idsList)):
                tmp_geom = QgsGeometry(gridfeat.geometry())
                tmp_attrs = gridfeat.attributes()
                if geom.intersects(tmp_geom):
                    int = QgsGeometry(geom.intersection(tmp_geom))
                    outfeat = QgsFeature()
                    outfeat.setGeometry(int)
                    outfeat.setAttributes(tmp_attrs)
                    outprov.addFeatures([outfeat])

        output.updateFields()

        return output


        # Load the layer
        p = self.layer

        # Set width and height as you want
        window_width = 5000
        window_height = 5000

        # Run the function
        divided_area = cut_polygon_into_windows(p, window_height, window_width)

        # Add the layer to the Layers panel
        QgsMapLayerRegistry.instance().addMapLayers([divided_area])