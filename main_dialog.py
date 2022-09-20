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
from .line_to_points_dialog import LineToPointsDialog

from PyQt5 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'main_dialog_base.ui'))


class MainDialog(QtGui.QDialog, FORM_CLASS):
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
        self.btnZdroj.clicked.connect(self.selectZdrojFile)
        self.btnRuzice.clicked.connect(self.selectRuziceFile)
        self.btnCalculate.clicked.connect(self.calculate)
        self.btnUlozit.clicked.connect(self.selectConfigFileSave)
        self.btnNacist.clicked.connect(self.selectConfigFileOpen)
        self.pushButton.clicked.connect(self.linesToPoints)
        self.mMapLayerComboBoxReceptory.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBoxZdroje.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.mMapLayerComboBoxTeren.setFilters(QgsMapLayerProxyModel.RasterLayer)

    def linesToPoints(self):
        self.linetopints = LineToPointsDialog()
        self.linetopints.show()

    def selectZdrojFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path, _ = self.fileDialog.getOpenFileName()
        self.txtZdroj.setText(path)
        self.saveConfig('')

    def selectRuziceFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path, _ = self.fileDialog.getOpenFileName()
        self.txtRuzice.setText(path)
        self.saveConfig('')

    def saveConfig(self, path):
        if path == '':
            path = self.wd + "config"

        f = open(path, 'w')
        f.write(str(self.cmbLatka.currentIndex()) + '\n')
        f.write(str(self.cmbTypVypoctu.currentIndex()) + '\n')
        f.write(self.txtZdroj.text() + '\n')
        f.write(str(self.cmbTeren.currentIndex()) + '\n')
        f.write(self.txtTeren2.text() + '\n')
        f.write(str(self.cmbReceptory.currentIndex()) + '\n')
        f.write(self.txtReceptoryVyska.text() + '\n')
        f.write(self.txtRuzice.text() + '\n')
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
            self.cmbLatka.setCurrentIndex(int(f.readline()))
            self.cmbTypVypoctu.setCurrentIndex(int(f.readline()))
            self.txtZdroj.setText(f.readline().strip('\n\r'))        
            self.cmbTeren.setCurrentIndex(int(f.readline()))
            self.txtTeren2.setText(f.readline().strip('\n\r'))
            self.cmbReceptory.setCurrentIndex(int(f.readline()))
            self.txtReceptoryVyska.setText(f.readline().strip('\n\r'))
            self.txtRuzice.setText(f.readline().strip('\n\r'))
            self.txtLimit.setText(f.readline().strip('\n\r'))                
            f.close()

    def init_param(self):
        #self.wd = '/tmp/' #tempfile.gettempdir()
        self.wd = os.path.join(os.path.dirname(__file__), "tmp/")

    def calculate(self):
        self.main = Main()
        if self.txtZdroj.text() == '':
            #TODO
            #http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&LatkaNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*
            layer = self.mMapLayerComboBoxZdroje.currentLayer()
            self.main.inicializuj_zdroje_vrstva(layer)
        else:                    
            self.main.inicializuj_zdroje(self.txtZdroj.text())

        layer = self.mMapLayerComboBoxReceptory.currentLayer()
        self.main.inicializuj_ref_body(layer)

        # TODO - badly implemented
        fixed_h = None
        if self.txtTeren2.text() != '':
            fixed_h = float(self.txtTeren2.text())
        layer = self.mMapLayerComboBoxTeren.currentLayer()
        self.main.inicializuj_teren(layer.source())

        if self.cmbTypVypoctu.currentIndex() == 1 or self.cmbTypVypoctu.currentIndex() == 2:
            if self.txtRuzice.text() == '':
                self.showMessage(u"Nebyla vybrána větrná růžice. Není možno počítat.")
                return
            else:
                self.main.inicializuj_vetrnou_ruzici(self.txtRuzice.text())
        if self.cmbTypVypoctu.currentIndex() == 2:
            if self.txtLimit.text() == '':
                self.showMessage(u"Nebyl nastaven limit Není možno počítat.")
                return

        self.main.vypocti(self.txtStatus, self.progressBar, self.cmbLatka.currentText(), self.cmbTypVypoctu.currentIndex() + 1, float(self.txtLimit.text()), float(self.txtReceptoryVyska.text()), fixed_h)
        typ_zkr = ''
        if self.cmbTypVypoctu.currentIndex() == 0:
            typ_zkr = 'max'
        if self.cmbTypVypoctu.currentIndex() == 1:
            typ_zkr = 'prum'
        if self.cmbTypVypoctu.currentIndex() == 2:
            typ_zkr = 'limit'
        x = self.cmbLatka.currentText() + "_" + typ_zkr + "_" + str(uuid.uuid1())        
        x = x.replace("-", "_")
        #shppath = os.path.join(os.path.dirname(__file__), "vysledky/" + x + ".shp")
        #TODO Nastavit temp dir
        shppath = os.path.join(tempfile.gettempdir(), x + ".shp")
        self.main.export(self.cmbTypVypoctu.currentIndex() + 1,"shp",shppath)
        copyfile(os.path.join(os.path.dirname(__file__), 'templates/5514.prj'), os.path.join(tempfile.gettempdir(), x + ".prj"))
        copyfile(os.path.join(os.path.dirname(__file__), 'templates/5514.qpj'), os.path.join(tempfile.gettempdir(), x + ".qpj"))
        style_name = self.cmbLatka.currentText() + "_" + typ_zkr
        style_name = style_name.replace("-", "_")
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'templates/' + style_name + '.qml')):
            #copyfile(os.path.join(os.path.dirname(__file__), 'templates/default.qml'), os.path.join(tempfile.gettempdir(), x + ".qml"))
            QgsMessageLog.logMessage(u"Styl pro " + style_name + u" není nadefinován. Nadefinujte a uložte pod názvem " + style_name + u" do složky templates v adresáři pluginu.", u"Open SYMOS")
        else:
            copyfile(os.path.join(os.path.dirname(__file__), 'templates/' + style_name + '.qml'), os.path.join(tempfile.gettempdir(), x + ".qml"))
        layer = QgsVectorLayer(shppath, x, "ogr")
        if not layer.isValid():
            print ("Layer failed to load!")
        else:
            QgsProject.instance().addMapLayer(layer)

    def getReceptory(self):
        # mMapLayerComboBoxReceptory
        layer = self.mMapLayerComboBoxReceptory.currentLayer()
        # layer = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbReceptory.currentText())[0]
        iter = layer.getFeatures()
        for feature in iter:
            geom = feature.geometry()
            print (geom.asPoint().x())
            print (geom.asPoint().y())
            print ("Feature ID %d: " % feature.id())

    def showMessage(self, message):                    
        msgBox = QtGui.QMessageBox(self)
        msgBox.setText(message)
        msgBox.open()
