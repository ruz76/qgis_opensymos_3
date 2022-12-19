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
from qgis.core import *
from qgis import processing

from PyQt5 import uic
from PyQt5.QtWidgets import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'receptory.ui'))

class CreateReferencePoints(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(CreateReferencePoints, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btnCalculate.clicked.connect(self.CreateReferencePoints)
        self.SaveRefferencePointsAs.setStorageMode(3)
    def CreateReferencePoints(self):
        # Otevření dialogového okna
        QgsMessageLog.logMessage("Chystam se otvrit okno ", "Messages")
        # Zjištění, kam chce uživatel uložit výstup (výsledný soubor)
        vystupniSoubor = self.SaveRefferencePointsAs.filePath()
        # Zjištění adresáře, kam chce uživatel uložit výstup (bez jména souboru, jen adresář)
        self.location = os.path.dirname(vystupniSoubor)

        # Zjištení jakou vrstvu uživatel vybral v rozbalovacím seznamu vrstev na formuláři
        self.layer = (self.ExtentDMR.currentLayer())
        QgsMessageLog.logMessage("Zpracovávaná/vybraná vrstva: " + self.layer.name(), "Messages")
        # Získání všech geoprvků z vybrané vrstvy (seznam)
        # DMR = self.layer.getFeatures()

        # nastaveni rozestupu bodu pravidelne site
        self.SpacingX = []
        self.SpacingY = []

        SpacingX = int(self.SBX.value())
        SpacingY = int(self.SBY.value())


    # vytvoreni pravidelne site bodu

        crs = QgsProject().instance().crs().toWkt()
        grid = processing.run("native:creategrid", {'TYPE': 0,
                                             'EXTENT': self.layer,
                                             'HSPACING': SpacingX , 'VSPACING': SpacingY, 'HOVERLAY': 0, 'VOVERLAY': 0,
                                             'CRS': crs,
                                             'OUTPUT': 'TEMPORARY_OUTPUT'})
        gridoutput = grid["OUTPUT"]
        QgsProject.instance().addMapLayer(gridoutput)
        Output3 = self.SaveRefferencePointsAs.filePath()
        # self.location = os.path.dirname(Output3)
        vystup2 = 'grid'
        processing.run("native:savefeatures",
                       {'INPUT': gridoutput,
                        'OUTPUT': Output3,
                        'LAYER_NAME': vystup2, 'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''})

        VybranyObjekt = (self.DensePoints.currentLayer())

        Vzdalenost = int(self.BufferSpacing.value())
        buffer = processing.run("native:buffer", {'INPUT': VybranyObjekt,'DISTANCE': Vzdalenost, 'SEGMENTS': 1,'DISSOLVE': False, 'OUTPUT': 'TEMPORARY_OUTPUT'})
        bufferoutput = buffer["OUTPUT"]
        points = processing.run("native:pointsalonglines",
                       {'INPUT': bufferoutput, 'DISTANCE': self.PointSpacing.value(), 'START_OFFSET': 0,
                        'END_OFFSET': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'})
        output = points["OUTPUT"]
        QgsProject.instance().addMapLayer(output)

        Output2 = self.SaveRefferencePointsAs_2.filePath()
        # self.location = os.path.dirname(Output2)
        vystup = 'grid'
        processing.run("native:savefeatures",
                       {'INPUT': output,
                        'OUTPUT': Output2,
                        'LAYER_NAME': vystup, 'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''})
