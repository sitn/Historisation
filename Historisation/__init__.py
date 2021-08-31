# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Historisation
                                 A QGIS plugin
 Historisation par SITN
                             -------------------
        begin                : 2019-08-01
        copyright            : (C) 2019 by arx iT
        email                : mba@arxit.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Historisation class from file Historisation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .main import Historisation
    return Historisation(iface)
