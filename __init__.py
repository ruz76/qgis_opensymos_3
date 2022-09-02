# -*- coding: utf-8 -*-
"""
/***************************************************************************

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def classFactory(iface):
    """Load Cybele_trees class from file cybele_trees.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .opensymos import Open_symos
    return Open_symos(iface)
