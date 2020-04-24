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

import Temporalite.main

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ajoutTable_dialog.ui'))


class AjoutTableDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        '''
        Constructor.
        '''

        super(AjoutTableDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pushButton.clicked.connect(self.onButtonClicked)
        # self.mapLayerComboBox.layerChanged.connect(self.onLayerChanged)

    def onButtonClicked(self):
        # if self.libelleComboBox.currentText() != "" and self.idComboBox.currentText() != "":
        #     if not self.existingLayer():
        #         self.addLayer()
        #     else:
        #         self.throwErrorExistingLayer()
        self.displayField = self.libelleComboBox.currentText()
        self.idField = self.idComboBox.currentText()

        self.accept()

    # def setExceptedLayerList(self):
    #     historised_layers = list()
    #     if Temporalite.main.current_project.histo_param:
    #         for feature in Temporalite.main.current_project.histo_param.getFeatures():
    #             h = QgsProject.instance().mapLayersByName(feature["nom_table"])
    #             if h:
    #                 historised_layers.append(h[0])

    #     self.mapLayerComboBox.setExceptedLayerList(historised_layers)
    #     self.onLayerChanged()

    # def is_empty(self):
    #     return self.mapLayerComboBox.currentLayer() is None

    def setLayer(self, mapLayer: QgsVectorLayer):
        self.mapLayerComboBox.clear()
        self.libelleComboBox.clear()
        self.idComboBox.clear()

        self.mapLayerComboBox.addItem(mapLayer.dataProvider().uri().table())

        for field in mapLayer.dataProvider().fields():
            self.libelleComboBox.addItem(str(field.name()))
            self.idComboBox.addItem(str(field.name()))

    # def existingLayer(self):
    #     return False

    # def throwErrorExistingLayer(self):
    #     pass

    # def addLayer(self):
    #     if Temporalite.main.current_project.histo_param:
    #         (res, outFeats) = self.addToHistoParam()
    #         self.createHTable()
    #     else:
    #         Temporalite.main.QGIS_INTERFACE.messageBar().pushMessage("Toutes les opérations d'historisation sont impossibles", "Fichier config.ini vide ou manquant au projet", 2)

    # def addToHistoParam(self):
    #     feature = QgsFeature(Temporalite.main.current_project.histo_param.fields())
    #     feature.setAttribute('nom_table', self.mapLayerComboBox.currentLayer().name())
    #     feature.setAttribute('display_field', self.libelleComboBox.currentText())
    #     feature.setAttribute('id_field', self.idComboBox.currentText())
    #     return Temporalite.main.current_project.histo_param.dataProvider().addFeatures([feature])

    # def createHTable(self):
    #     config = configparser.RawConfigParser()
    #     path = os.path.join(QgsProject.instance().readPath("./"), 'config.ini')
    #     config.read(path)

    #     host = config.get('POSTGRES', 'host')
    #     user = config.get('POSTGRES', 'user')
    #     passwd = config.get('POSTGRES', 'passwd')
    #     db = config.get('POSTGRES', 'db')
    #     port = config.get('POSTGRES', 'port')
    #     schema = str(config.get('POSTGRES', 'schema')).replace("'", "''").replace(";", "")

    #     try:
    #         conn = psycopg2.connect(
    #             user=user,
    #             password=passwd,
    #             host=host,
    #             port=port,
    #             database=db
    #         )
    #         layerName = str(self.mapLayerComboBox.currentLayer().name()).replace("'", "''").replace(";", "")
    #         idObj = str(self.idComboBox.currentText()).replace("'", "''").replace(";", "")
    #         cursor = conn.cursor()
    #         query = "SELECT " + schema + ".createhtable("
    #         query += "'" + str(getpass.getuser()).replace("'", "''").replace(";", "") + "',"
    #         query += "'" + schema + "',"
    #         query += "'" + layerName + "',"
    #         query += "'" + idObj + "',"
    #         query += "'{"

    #         layer = QgsProject.instance().mapLayersByName(layerName)[0]
    #         hasValueMap = False
    #         for field in layer.fields():
    #             if field.editorWidgetSetup().type() == 'ValueMap':
    #                 if hasValueMap:
    #                     query += ","
    #                 query += str(field.name()).replace("'", "''").replace(";", "")
    #                 hasValueMap = True
    #         query += "}' )"
    #         cursor.execute(query)
    #         data = cursor.fetchall()
    #         conn.commit()

    #         for field in layer.fields():
    #             if field.editorWidgetSetup().type() == 'ValueMap':
    #                 for assoc in field.editorWidgetSetup().config()["map"]:
    #                     for cle, valeur in assoc.items():
    #                         query = "UPDATE " + schema + "." + layerName + "_H SET " + str(field.name()).replace("'", "''").replace(";", "") + "_desc = '" + str(cle).replace(
    #                             "'", "''").replace(";", "") + "' WHERE " + str(field.name()).replace("'", "''").replace(";", "") + " = '" + str(valeur).replace("'", "''").replace(";", "") + "'"
    #                         cursor.execute(query)
    #                         conn.commit()

    #         Temporalite.main.current_project.reloadHistoTable()
    #         mapLayer = self.mapLayerComboBox.currentLayer()
    #         self.setExceptedLayerList()
    #         Temporalite.main.QGIS_INTERFACE.messageBar().pushMessage("Succès", str(mapLayer.name()) + " est historisée", 0)
    #         if hasattr(mapLayer, 'beforeCommitChanges'):
    #             mapLayer.beforeCommitChanges.connect(lambda ml=mapLayer: Temporalite.main.current_project.beforeCommitChanges(ml))

        # except (Exception, psycopg2.Error) as error:
        #     print("Error while fetching data from PostgreSQL", error)

        # finally:
        #     if conn:
        #         cursor.close()
        #         conn.close()
