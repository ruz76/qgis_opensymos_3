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
    os.path.dirname(__file__), 'main_dialog_base_v2.ui'))


class MainDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MainDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.init_param()
        self.setupUi(self)
        self.btnSelectXMLPointSource.clicked.connect(self.selectPointSourceFile)
        self.btnWindRose.clicked.connect(self.selectWindRose)
        self.btnCalculate.clicked.connect(self.calculate)
        self.btnSaveSettings.clicked.connect(self.selectConfigFileSave)
        self.btnReadSettings.clicked.connect(self.selectConfigFileOpen)
        self.mMapLayerComboBoxReceptor.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBoxPointSource.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBoxTerrain.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.mFieldComboBoxIdPointSource.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxPointSourceEmission.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxChimneyHeight.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxGasVolume.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxGasTemperature.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxChimneyDiameter.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxGasVelocity.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxUsingPerYear.setFilters(QgsFieldProxyModel.Numeric)
        self.mFieldComboBoxUsingPerDay.setFilters(QgsFieldProxyModel.Numeric)
        self.rbtnImportPointSourceXML.clicked.connect(self.changePointSourceSelection2)
        self.mMapLayerComboBoxPointSource.currentIndexChanged.connect(self.fillingFields)
        # self.btnImportPointSourceFromLayer.clicked.connect(self.importPointSources)

    def selectPointSourceFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path, _ = self.fileDialog.getOpenFileName()
        self.txtXMLPointSource.setText(path)
        self.saveConfig('')

    def selectWindRose(self):
        self.fileDialog = QFileDialog(self)
        path, _ = self.fileDialog.getOpenFileName()
        self.txtWindRose.setText(path)
        self.saveConfig('')

    def saveConfig(self, path):
        if path == '':
            path = self.wd + "config"

        f = open(path, 'w')
        f.write(str(self.cmbPollution.currentIndex()) + '\n')
        f.write(str(self.cmbCalculationType.currentIndex()) + '\n')
        f.write(self.txtXMLPointSource.text() + '\n')
        f.write(str(self.mMapLayerComboBoxTerrain.currentIndex()) + '\n')
        f.write(self.txtTerrainFixedElevation.text() + '\n')
        f.write(str(self.mMapLayerComboBoxReceptor.currentIndex()) + '\n')
        f.write(self.txtReceptorHeigth_2.text() + '\n')
        f.write(self.txtWindRose.text() + '\n')
        f.write(self.txtLimit.text() + '\n')
        f.close()

    def selectConfigFileSave(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path, _ = self.fileDialog.getSaveFileName()
        if path != '':
            self.saveConfig(path)

    def selectConfigFileOpen(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path, _ = self.fileDialog.getOpenFileName()
        if path != '':
            f = open(path, 'r')        
            self.cmbPollution.setCurrentIndex(int(f.readline()))
            self.cmbTCalculationType.setCurrentIndex(int(f.readline()))
            self.txtXMLPointSource.setText(f.readline().strip('\n\r'))
            self.mMapLayerComboBoxTerrain.setCurrentIndex(int(f.readline()))
            self.txtTerrainFixedElevation.setText(f.readline().strip('\n\r'))
            self.mMapLayerComboBoxReceptor.setCurrentIndex(int(f.readline()))
            self.txtTerrainFixedElevation.setText(f.readline().strip('\n\r'))
            self.txtWindRose.setText(f.readline().strip('\n\r'))
            self.txtLimit.setText(f.readline().strip('\n\r'))                
            f.close()

    def init_param(self):
        #self.wd = '/tmp/' #tempfile.gettempdir()
        self.wd = os.path.join(os.path.dirname(__file__), "tmp/")

    def get_type_of_pollution(self, index):
        types = ["sirovodik", "chlorovodik", "peroxid_vodiku", "dimetyl_sulfid",
                 "oxid_siricity", "oxid_dusnaty", "oxid_dusicity", "amoniak",
                 "sirouhlik", "formaldehyd", "oxid_dusny", "oxid_uhelnaty",
                 "oxid_uhlicity", "metan", "vyssi_uhlovodiky", "metyl_chlorid",
                 "karbonyl_sulfid", "prach"]
        return types[index]

    def calculate(self):
        self.main = Main()
        if self.txtXMLPointSource.text() == '':
            #TODO
            #http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&PollutionNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*
            layer = self.mMapLayerComboBoxPointSource.currentLayer()
            id = self.mFieldComboBoxIdPointSource.currentText()
            emission = self.mFieldComboBoxPointSourceEmission.currentText()
            chimneyHeight = self.mFieldComboBoxChimneyHeight.currentText()
            gasVolume = self.mFieldComboBoxGasVolume.currentText()
            gasTemperature = self.mFieldComboBoxGasTemperature.currentText()
            chimneyDiameter = self.mFieldComboBoxChimneyDiameter.currentText()
            gasVelocity = self.mFieldComboBoxGasVelocity.currentText()
            usingPerYear = self.mFieldComboBoxUsingPerYear.currentText()
            usingPerDay = self.mFieldComboBoxUsingPerDay.currentText()
            self.main.inicializuj_zdroje_vrstva(layer, id, emission, chimneyHeight, gasVolume, gasTemperature, chimneyDiameter,gasVelocity,usingPerYear,usingPerDay)
        else:                    
            self.main.inicializuj_zdroje(self.txtXMLPointSource.text())

        layer = self.mMapLayerComboBoxReceptor.currentLayer()
        self.main.inicializuj_ref_body(layer)

        # TODO - badly implemented
        fixed_h = None
        if self.txtTerrainFixedElevation.text() != '':
            fixed_h = float(self.txtTerrainFixedElevation.text())
        layer = self.mMapLayerComboBoxTerrain.currentLayer()
        self.main.inicializuj_teren(layer.source())

        if self.cmbCalculationType.currentIndex() == 1 or self.cmbCalculationType.currentIndex() == 2:
            if self.txtWindRose.text() == '':
                self.showMessage(u"Wind rose was not set. Complete input data.")
                return
            else:
                self.main.inicializuj_vetrnou_ruzici(self.txtWindRose.text())
        if self.cmbCalculationType.currentIndex() == 2:
            if self.txtLimit.text() == '':
                self.showMessage(u"Limit eas not set. Complete input data.")
                return

        height = fixed_h
        if self.rbtnImportTerrain.isChecked():
            height = None

        self.main.vypocti(self.txtStatus, self.progressBar, self.get_type_of_pollution(self.cmbPollution.currentIndex()), self.cmbCalculationType.currentIndex() + 1, float(self.txtLimit.text()), float(self.txtReceptorHeigth_2.text()), height)
        typ_zkr = ''

        if self.cmbCalculationType.currentIndex() == 0:
            typ_zkr = 'max'
        if self.cmbCalculationType.currentIndex() == 1:
            typ_zkr = 'prum'
        if self.cmbCalculationType.currentIndex() == 2:
            typ_zkr = 'limit'
        pollution = self.cmbPollution.currentText()
        x = self.cmbPollution.currentText() + "_" + typ_zkr + "_" + str(uuid.uuid1())
        x = x.replace("-", "_")
        #shppath = os.path.join(os.path.dirname(__file__), "vysledky/" + x + ".shp")
        #TODO set temp dir
        shppath = os.path.join(tempfile.gettempdir(), x + ".shp")
        self.main.export(self.cmbCalculationType.currentIndex() + 1,"shp",shppath)
        copyfile(os.path.join(os.path.dirname(__file__), 'templates/5514.prj'), os.path.join(tempfile.gettempdir(), x + ".prj"))
        copyfile(os.path.join(os.path.dirname(__file__), 'templates/5514.qpj'), os.path.join(tempfile.gettempdir(), x + ".qpj"))
        style_name = self.cmbPollution.currentText() + "_" + typ_zkr
        style_name = style_name.replace("-", "_")
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'templates/' + style_name + '.qml')):
            #copyfile(os.path.join(os.path.dirname(__file__), 'templates/default.qml'), os.path.join(tempfile.gettempdir(), x + ".qml"))
            QgsMessageLog.logMessage(u"Style for " + style_name + u" was not defined. Define and save it " + style_name + u" into templates in plugin folder.", u"Open SYMOS")
        else:
            copyfile(os.path.join(os.path.dirname(__file__), 'templates/' + style_name + '.qml'), os.path.join(tempfile.gettempdir(), x + ".qml"))
        layer = QgsVectorLayer(shppath, x, "ogr")
        if not layer.isValid():
            print ("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(layer)

    def getReceptory(self):
        # mMapLayerComboBoxReceptors
        layer = self.mMapLayerComboBoxReceptor.currentLayer()
        # layer = QgsMapLayerRegistry.instance().mapLayersByName(self.mMapLayerComboBoxReceptor.currentText())[0]
        iter = layer.getFeatures()
        for feature in iter:
            geom = feature.geometry()
            print (geom.asPoint().x())
            print (geom.asPoint().y())
            print ("Feature ID %d: " % feature.id())

    def changePointSourceSelection(self):
        self.gboxImportPointSourceXML.setEnabled(False)
        self.gboxImportPointSource.setEnabled(True)

    def changePointSourceSelection2(self):

        self.gboxImportPointSourceXML.setEnabled(True)
        self.gboxImportPointSource.setEnabled(False)

    def fillingFields(self):
        self.mFieldComboBoxIdPointSource.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxPointSourceEmission.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxChimneyHeight.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxGasVolume.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxGasTemperature.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxChimneyDiameter.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxGasVelocity.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxUsingPerYear.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxUsingPerDay.setLayer(self.mMapLayerComboBoxPointSource.currentLayer())
        self.mFieldComboBoxIdPointSource.setEnabled(True)
        self.mFieldComboBoxPointSourceEmission.setEnabled(True)
        self.mFieldComboBoxChimneyHeight.setEnabled(True)
        self.mFieldComboBoxGasVolume.setEnabled(True)
        self.mFieldComboBoxGasTemperature.setEnabled(True)
        self.mFieldComboBoxChimneyDiameter.setEnabled(True)
        self.mFieldComboBoxGasVelocity.setEnabled(True)
        self.mFieldComboBoxUsingPerYear.setEnabled(True)
        self.mFieldComboBoxUsingPerDay.setEnabled(True)

    def showMessage(self, message):                    
        msgBox = QtGui.QMessageBox(self)
        msgBox.setText(message)
        msgBox.open()
