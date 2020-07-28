# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConfigureDialog
                                 A QGIS plugin
 Plugin d'historisation de SITN
                             -------------------
        begin                : 2015-09-09
        git sha              : $Format:%H$
        copyright            : (C) 2015 by arx iT
        email                : mba@arxit.com
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
from __future__ import absolute_import

import os
import configparser
import psycopg2
import getpass

from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.core import QgsDataSourceUri, QgsFeature, QgsVectorLayer, QgsVectorLayerExporter, QgsField, QgsProject
import db_manager.db_plugins.postgis.connector as con
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QVariant

import Historisation.main

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ajoutTable_dialog.ui'))


class AjoutTableDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        '''
        Constructor.
        '''

        super(AjoutTableDialog, self).__init__(parent)

        self.setupUi(self)
        self.pushButton.clicked.connect(self.onButtonClicked)

    def onButtonClicked(self):

        self.displayField = self.libelleComboBox.currentText()
        self.idField = self.idComboBox.currentText()

        self.accept()

    def setLayer(self, mapLayer: QgsVectorLayer):
        self.mapLayerComboBox.clear()
        self.libelleComboBox.clear()
        self.idComboBox.clear()

        self.mapLayerComboBox.addItem(mapLayer.dataProvider().uri().table())

        for field in mapLayer.dataProvider().fields():
            self.libelleComboBox.addItem(str(field.name()))
            self.idComboBox.addItem(str(field.name()))
