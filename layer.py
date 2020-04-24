'''
Created on February, 04th 2020

@author: arxit
'''
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsFeatureRequest, QgsFeatureIterator, QgsExpression, QgsFeature

import psycopg2
import re


class Layer(object):
    def __init__(self, uri: QgsDataSourceUri):
        self.uri = uri

    def getVectorLayer(self) -> QgsVectorLayer:
        return self.createVectorLayer()

    def createVectorLayer(self):
        return QgsVectorLayer(self.uri.uri(), self.uri.table(), "postgres")

    def getSqlConnection(self):
        return psycopg2.connect(
            user=self._getUsername(),
            password=self._getPassword(),
            host=self.uri.host(),
            port=self.uri.port(),
            database=self.uri.database()
        )

    def getFeatures(self, request: QgsFeatureRequest = QgsFeatureRequest()) -> QgsFeatureIterator:
        return self.getVectorLayer().getFeatures(request)

    def getDatabaseFeatures(self, request: QgsFeatureRequest = QgsFeatureRequest()) -> QgsFeatureIterator:
        return self.getVectorLayer().dataProvider().getFeatures(request)

    def addFeature(self, feature: QgsFeature):
        self.getVectorLayer().addFeature(feature)

    def updateFeature(self, feature: QgsFeature):
        return self.getVectorLayer().updateFeature(feature)

    def startEditing(self):
        self.getVectorLayer().startEditing()

    def commitChanges(self):
        self.getVectorLayer().commitChanges()

    def _getUsername(self) -> str:
        if self.uri.username() != '':
            return self.uri.username()
        else:
            return re.search("user='([^']+)", self.uri.uri()).group(1)

    def _getPassword(self) -> str:
        if self.uri.password() != '':
            return self.uri.password()
        else:
            return re.search("password='([^']+)", self.uri.uri()).group(1)
