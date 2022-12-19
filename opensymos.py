# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Open Symos
			A QGIS plugin
 Calculates pollutants concentration according to SYMOS methodology.
 This plugin was developed by Jan Ruzicka, Katerina Ruzickova, Radek Furmanek and Ondrej Kolodziej.
 The plugin is based on Open Symos software developed by Karel Psota.

 Code has been ported to QGIS 3 in 2022 year.

                             -------------------
        begin                : 2016-12-19
        copyright            : (C) 2016 by Jan Ruzicka, Katerina Ruzickova, Radek Furmanek, Ondrej Kolodziej
        email                : jan.ruzicka.vsb@gmail.com, katerina.ruzickova@vsb.cz

 ***************************************************************************/
"""
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from osgeo.gdalconst import *
from osgeo.gdalnumeric import *
from qgis.core import *
from qgis.gui import *

from .main_dialog import MainDialog
from .receptors import CreateReferencePoints

class Open_symos:
    # Implementace QGIS pluginu
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Ulozeni reference na QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.dlg = MainDialog()
        self.receptors_dlg = CreateReferencePoints()

    def initGui(self):
        # Vytvoreni a konfigurace nastrojove listy pro spusteni pluginu
        self.toolbar = self.iface.addToolBar("OpenSYMOS")
        self.toolbar.setObjectName("OpenSYMOS")

        self.show_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "opensymos.png")),
                                "OpenSYMOS", self.iface.mainWindow())
        self.receptors_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "createReferencePointsIcon.png")),
                                "OpenSYMOS", self.iface.mainWindow())
        self.toolbar.addActions([self.show_btn, self.receptors_btn])
        self.show_btn.triggered.connect(self.showDialog)
        self.receptors_btn.triggered.connect(self.showReceptorsDialog)

    def showDialog(self):
        self.dlg.show()

    def showReceptorsDialog(self):
        self.receptors_dlg.show()

    def unload(self):
        # odstraneni ikony z panelu nastroju QGISu
        del self.toolbar


if __name__ == '__main__':
    print("OpenSYMOS plugin")
