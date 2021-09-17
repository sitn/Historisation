'''
Created on 2 august 2019

@author: arxit
'''
from __future__ import absolute_import
from typing import List
from qgis.core import *
from qgis.PyQt.QtCore import QFileInfo, QVariant, QObject, pyqtSignal, QSettings
from qgis.PyQt.QtWidgets import QAction, QPushButton, QMenu, QMessageBox, QDialog

from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject
import db_manager.db_plugins.postgis.connector as con
import configparser
import psycopg2

from . import main
from .widgets.configuration.ajoutTable_dialog import AjoutTableDialog
from .maplayer import MapLayer


class Project(QObject):

    ready = pyqtSignal()

    def __init__(self, iface):
        '''
        Constructor
        '''
        super(Project, self).__init__()
        self.iface = iface
        self.layers = dict()

        QgsProject.instance().layersAdded.connect(self.onLayersAdded)
        self.onLayersAdded(QgsProject.instance().mapLayers().values())

    def onLayersAdded(self, layers: List[QgsMapLayer]):
        for layer in layers:
            mapLayer = self.getLayer(layer)
            mapLayer.setListenToCommit(True)

    def onLayersRemoved(self, layerIds: List[str]):
        for layerId in layerIds:
            mapLayer = self.getLayerFromId(layerId)

            if mapLayer is not None:
                mapLayer.setListenToCommit(False)

    def activateHistoryOnSelectedLayer(self):
        selectedLayer = self.getSelectedLayer()

        if selectedLayer is None:
            return

        if not selectedLayer.isHistorisable():
            self.iface.messageBar().pushMessage("Erreur", "La couche sélectionnée n'est pas historisable", Qgis.Warning)
            return

        if selectedLayer.isAlreadyHistorized():
            self.iface.messageBar().pushMessage("Attention", "La couche sélectionnée est déjà historisée", Qgis.Info)
            return

        dlg = AjoutTableDialog()
        dlg.setLayer(selectedLayer.getVectorLayer())
        answer = dlg.exec()

        if answer != QDialog.Accepted:
            return

        answer = QMessageBox.question(self.iface.mainWindow(), "Attention", "L'historisation de la couche va commencer, l'opération peut durer plusieurs minutes, voulez-vous continuer?")

        if answer == QMessageBox.No:
            return

        selectedLayer.historizeTable(dlg.displayField, dlg.idField)

        del self.layers[selectedLayer.getVectorLayer().id()]
        self.onLayersAdded([selectedLayer.getVectorLayer()])

        self.iface.messageBar().pushMessage("Information", "L'historisation de la couche est terminée", Qgis.Info)

    def getSelectedLayer(self) -> MapLayer:
        return self.getLayer(self.iface.activeLayer())

    def getLayer(self, layer: QgsVectorLayer) -> MapLayer:

        if layer is None:
            self.iface.messageBar().pushMessage("Information", "Il n'y a pas de couche", Qgis.Info)
            return

        if layer.id() not in self.layers:
            self.layers[layer.id()] = MapLayer(layer, self.iface)

        return self.layers[layer.id()]

    def getLayerFromId(self, layerId: str) -> MapLayer:
        if layerId not in self.layers:
            return None

        return self.layers[layerId]
