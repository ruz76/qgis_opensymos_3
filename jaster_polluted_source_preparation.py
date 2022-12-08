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
        self.exec()
        self.layer = (self.VyberVrstvu.currentLayer())
        self.VyberAtribut.setLayer(self.VyberVrstvu.currentLayer())

        atribut = self.VyberAtribut.currentField()

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
# newlayer = QgsVectorLayer("Polygon?crs={}&index=yes".format(layer.crs().authid()), "BoundingBoxes", "memory")
#
# with edit(newlayer):
#     newlayer.dataProvider().addAttributes(layer.fields()) # copy the fields to the outputlayer
#     newlayer.updateFields() # save the changes
#     for polygon in layer.getFeatures(): # iterate over inputlayer
#         bbox = polygon.geometry().boundingBox() # get the Boundingbox as QgsRectangle
#         bbox_geom = QgsGeometry.fromRect(bbox) # Turn the QgsRectangle into QgsGeometry
#         outpolygon = QgsFeature() # Create a new feature
#         outpolygon.setAttributes(polygon.attributes()) # copy the attributes to the outputlayer
#         outpolygon.setGeometry(bbox_geom) # set the geometry of the outputfeature to the bbox of the inputfeature
#         newlayer.dataProvider().addFeature(outpolygon) # add the feature to the outputlayer
#
# QgsProject.instance().addMapLayer(newlayer)




        # #cellsize = 100 #Cell Size in WGS 84 will be 100 x 100 meters
        # for polygon in areas:
        #
        #     crs = QgsProject().instance().crs().toWkt() #WGS 84 System
        #     #input = layer #Use the processing.getObject to get information from our vector layer
        #     xmin = (polygon.geometry().boundingBox().xMinimum()) #extract the minimum x coord from our layer
        #     xmax = (polygon.geometry().boundingBox().xMaximum()) #extract our maximum x coord from our layer
        #     ymin = (polygon.geometry().boundingBox().yMinimum()) #extract our minimum y coord from our layer
        #     ymax = (polygon.geometry().boundingBox().yMaximum()) #extract our maximum y coord from our layer
        #     #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
        #     extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
        # #processing.run('qgis:vectorgrid', extent, cellsize, cellsize, 0, grid)
        #     grid_creation = processing.run("native:creategrid", {'TYPE':2,'EXTENT': extent,
        #                                                      'HSPACING':cell_size,'VSPACING':cell_size,
        #                                                      'HOVERLAY':0,'VOVERLAY':0,'CRS': crs,'OUTPUT': 'memory'})
        #     grid = QgsVectorLayer(grid_creation['OUTPUT'], 'grid', 'ogr')

        # crs = QgsProject().instance().crs().toWkt() #WGS 84 System
        # input = layer #Use the processing.getObject to get information from our vector layer
        # xmin = (input.extent().xMinimum()) #extract the minimum x coord from our layer
        # xmax = (input.extent().xMaximum()) #extract our maximum x coord from our layer
        # ymin = (input.extent().yMinimum()) #extract our minimum y coord from our layer
        # ymax = (input.extent().yMaximum()) #extract our maximum y coord from our layer
        # #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
        # extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
        # create_rastr = processing.run("gdal:rasterize", {'INPUT': layer,'FIELD':'Id','BURN':0,'USE_Z':False,'UNITS':1,'WIDTH':cell_size,'HEIGHT':cell_size,
        #                                   'EXTENT':extent,'NODATA':0,'OPTIONS':'','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'})
        # rastr = create_rastr['OUTPUT']
        # #rastr.setName('polygon_raster')
        # QgsMessageLog.logMessage("Rastrový grid je hotový.", "Messages")
        # #QgsProject.instance().addMapLayer(rastr)
        #
        # create_centroids = processing.run("native:pixelstopoints", {'INPUT_RASTER':rastr,'RASTER_BAND':1,'FIELD_NAME':'VALUE','OUTPUT':'TEMPORARY_OUTPUT'})
        # centroids = create_centroids['OUTPUT']
        # centroids.setName('polygon_centroids')
        # QgsMessageLog.logMessage("Centroidy sú hotové.", "Messages")
        # QgsProject.instance().addMapLayer(centroids)
        #
        # create_count = processing.run("native:countpointsinpolygon", {'POLYGONS': layer,'POINTS': centroids,'WEIGHT':'','CLASSFIELD':'','FIELD':'NUMPOINTS','OUTPUT':'TEMPORARY_OUTPUT'})
        # count = create_count['OUTPUT']
        # count.setName('count')
        # QgsMessageLog.logMessage("Prekryt polygonov s centroidmi je hotový.", "Messages")
        # QgsProject.instance().addMapLayer(count)
        #
        # prov = count.dataProvider()
        # fld = QgsField('emise', QVariant.Int)
        # prov.addAttributes([fld])
        # count.updateFields()
        # idx = count.fields().lookupField('emise')
        # #print(count.fields().names())
        #
        # count.startEditing()
        #
        # e = QgsExpression('DruhPozemk / NUMPOINTS')
        # c = QgsExpressionContext()
        # s = QgsExpressionContextScope()
        # s.setFields(count.fields())
        # c.appendScope(s)
        # e.prepare(c)
        #
        # for f in count.getFeatures():
        #     c.setFeature(f)
        #     value = e.evaluate(c)
        #     atts = {idx: value}
        #     count.dataProvider().changeAttributeValues({f.id(): atts})
        # count.commitChanges()

        # for terka in count:
        #     emise = atribut/"NUMPOINTS"
        # features = count.getFeatures()
        # count.startEditing()
        # for f in features:
        #     emise = 10 + 10
        #     layer_provider.changeAttributeValues(emise)
        # count.commitChanges()
        # #vypocita hodnoty v atributu emise (nejde)
        # expression = QgsExpression(int('DruhPozemk')/int('NUMPOINTS'))
        # index = count.fieldNameIndex('emise')
        # expression.prepare(count.pendingFields())
        # count.startEditing()
        # for feature in count.getFeatures():
        #     value = expression.evaluate(feature)
        #     count.changeAttributeValue(feature.id(), index, value)
        # #
        # finalgrid.commitChanges()
        # for polygon in areas:


        crs = QgsProject().instance().crs().toWkt() #WGS 84 System
        input = layer #Use the processing.getObject to get information from our vector layer
        xmin = (input.extent().xMinimum()) #extract the minimum x coord from our layer
        xmax = (input.extent().xMaximum()) #extract our maximum x coord from our layer
        ymin = (input.extent().yMinimum()) #extract our minimum y coord from our layer
        ymax = (input.extent().yMaximum()) #extract our maximum y coord from our layer
        #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
        extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)
        #processing.run('qgis:vectorgrid', extent, cellsize, cellsize, 0, grid)
        grid_creation = processing.run("native:creategrid", {'TYPE':0,'EXTENT': extent,
                                                             'HSPACING':cell_size,'VSPACING':cell_size,
                                                             'HOVERLAY':0,'VOVERLAY':0,'CRS': crs,'OUTPUT': 'memory'})
        grid = QgsVectorLayer(grid_creation['OUTPUT'], 'grid', 'ogr')
        QgsMessageLog.logMessage("Grid je hotový.", "Messages")
        QgsProject.instance().addMapLayer(grid)


        create_count = processing.run("native:countpointsinpolygon", {'POLYGONS': layer,'POINTS': grid,
                                                                      'WEIGHT':'','CLASSFIELD':'','FIELD':'NUMPOINTS',
                                                                      'OUTPUT':'TEMPORARY_OUTPUT'})
        count = create_count['OUTPUT']
        count.setName('count')
        QgsMessageLog.logMessage("Prekryt polygonov s centroidmi je hotový.", "Messages")
        QgsProject.instance().addMapLayer(count)

        #novy grid podle zvolene vrstvy (pouziti fce intersect)
        grid_create2 = processing.run("native:intersection",
                       {'INPUT': grid, 'OVERLAY': count,
                        'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [], 'OVERLAY_FIELDS_PREFIX': '',
                        'OUTPUT': 'TEMPORARY_OUTPUT', 'GRID_SIZE': None})
        finalgrid = grid_create2['OUTPUT']
        finalgrid.setName('final_grid')
        QgsMessageLog.logMessage("Finálny grid je hotový.", "Messages")
        QgsProject.instance().addMapLayer(finalgrid)


        prov = finalgrid.dataProvider()
        fld = QgsField('emise', QVariant.Double, "double", 10, 2)
        prov.addAttributes([fld])
        finalgrid.updateFields()
        idx = finalgrid.fields().lookupField('emise')
        #print(count.fields().names())

        finalgrid.startEditing()

        e = QgsExpression(atribut / 'NUMPOINTS')
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

        #prida novy atribut emise

        # layer_provider = finalgrid.dataProvider()
        # layer_provider.addAttributes([QgsField("emise", QVariant.Double)])
        # finalgrid.updateFields()
        # print(finalgrid.fields().names())

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