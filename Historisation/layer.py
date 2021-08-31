'''
Created on February, 04th 2020

@author: arxit
'''
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsFeatureRequest, QgsFeatureIterator, QgsExpression, QgsFeature
from qgis.PyQt.QtCore import QSettings
import psycopg2
import re


class Layer(object):
    def __init__(self, uri: QgsDataSourceUri):
        self.uri = uri
        settings = QSettings()
        self.pg_db_database = settings.value("HistorisationSITN/DB", '')
        self.pg_db_host = settings.value("HistorisationSITN/DBHost", '')
        self.pg_db_port = settings.value("HistorisationSITN/DBPort", 5432)
        self.pg_db_user = settings.value("HistorisationSITN/DBUser", '')
        self.pg_db_password = settings.value("HistorisationSITN/DBPassword", '')


    def getVectorLayer(self) -> QgsVectorLayer:
        return self.createVectorLayer()

    def createVectorLayer(self):
        if(self.tableExists()):
            return QgsVectorLayer(self.uri.uri(), self.uri.table(), "postgres")
        else:
            return QgsVectorLayer()

    def getSqlConnection(self):
        return psycopg2.connect(
            user=self.pg_db_user,
            password=self.pg_db_password,
            host=self.pg_db_host,
            port=self.pg_db_port,
            database=self.pg_db_database
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

    def tableExists(self) -> bool:
        query = "SELECT EXISTS (SELECT * FROM information_schema.tables WHERE table_schema='{0}' AND table_name='{1}')".format(self.uri.schema(), self.uri.table())

        conn = self.getSqlConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        return data[0]
