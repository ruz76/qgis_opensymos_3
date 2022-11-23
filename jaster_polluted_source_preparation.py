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
import qgis.utils
import processing
import re

import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np


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
        self.VyberVrstvu.layerChanged.connect(self.SelectLayerFields)

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
        # Zjištení jaký druh parcely uživatel vybral v rozbalovacím seznamu na formuláři
        #AreaType = self.dlgFormular.VyberAtribut.currentText()



    def SelectLayerFields(self):
        self.VyberAtribut.setLayer(self.VyberVrstvu.currentLayer())

    # Získání všech geoprvků z vybrané vrstvy (seznam)
        areas = self.layer.getFeatures()
        self.SelectedAreas = []
        self.CurrentPosition = 0

        #spusteníe rozdelenia-------------------------------------------------------

        if self.dlgFormular.DivideArea.isChecked():
            try:

                cell_size = 30
                layer = self.layer
                selected = AreaType
                crs = self.layer.crs().authid()

                ids = []
                x_maxs = []
                x_mins = []
                y_maxs = []
                y_mins = []

                for lay in selected:
                    id = lay.id()
                    ids.append(id)
                    print("working on: " + str(id))

                    x_min, y_min, x_max, y_max = re.split(":|,",  lay.geometry().boundingBox().toString().replace(" ", ""))
                x_mins.append(float(x_min))
                x_maxs.append(float(x_max))
                y_mins.append(float(y_min))
                y_maxs.append(float(y_max))

                extent = str(min(x_mins)) + "," + str(max(x_maxs)) + "," + str(min(y_mins)) + "," + str(max(y_maxs))
                print(extent)

                grid_parameters = {"TYPE":  1,
                                "EXTENT": extent,
                                "HSPACING": cell_size,
                                "VSPACING":cell_size,
                                #"HOVERLAY": 0,
                                #"VOVERLAY": 0,
                                "CRS": crs,
                                "OUTPUT": None}

                grid = processing.runalg("qgis:creategrid",  grid_parameters)

                intersection_parameters = {"INPUT":  layer,
                                        "INPUT2": grid["OUTPUT"],
                                        "IGNORE_NULL": True,
                                        "OUTPUT": None}

                intersect = processing.runalg("qgis:intersection", intersection_parameters)

                mem_intersect = QgsVectorLayer(intersect["OUTPUT"], "lyr_intersect", "ogr")

                fields_to_delete = []
                fieldnames = set(["left", "right",  "top", "bottom"])
                for field in mem_intersect.fields():
                    if field.name() in fieldnames:
                        fields_to_delete.append(mem_intersect.fieldNameIndex(field.name()))

                mem_intersect.dataProvider().deleteAttributes(fields_to_delete)
                mem_intersect.updateFields()

                features = []
                for feat in mem_intersect.getFeatures():
                    features.append(feat)

                with edit(layer):
                    layer.deleteFeatures(ids)
                    layer.dataProvider().addFeatures(features)
            except TypeError:
                QgsMessageLog.logMessage("niečo je zle.", "Messages")

        # pokus 2------------------------------------------------------------------------------
        if self.dlgFormular.DivideArea.isChecked():
            try:
                data = gpd.read_file(self.layer)

                xmin, ymin, xmax, ymax = data.total_bounds

                length = 1000
                wide = 1200

                cols = list(np.arange(xmin, xmax + wide, wide))
                rows = list(np.arange(ymin, ymax + length, length))

                polygons = []
                for x in cols[:-1]:
                    for y in rows[:-1]:
                        polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))

                grid = gpd.GeoDataFrame({'geometry':polygons})
                grid.to_file("grid.shp")
            except TypeError:
                QgsMessageLog.logMessage("niečo je zle.", "Messages")

        # -------------------------------------------------------------------------------------

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