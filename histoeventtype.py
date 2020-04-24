'''
Created on January, 29th 2020

@author: arxit
'''
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsFeatureRequest, QgsExpression, QgsFeature

from .layer import Layer

ID = "id"
DESCRIPTION = "description"


class HistoEventTypeTable(Layer):
    def __init__(self, uri):
        super().__init__(uri)
        self.histoEventTypeTable = self.createVectorLayer()

    def getVectorLayer(self):
        return self.histoEventTypeTable

    @staticmethod
    def fromOtherLayerUri(uri: QgsDataSourceUri):
        histoEventTypeTableUri = QgsDataSourceUri()
        histoEventTypeTableUri.setConnection(uri.host(), uri.port(), uri.database(), uri.username(), uri.password(), uri.sslMode(), uri.authConfigId())
        histoEventTypeTableUri.setDataSource(uri.schema(), "histo_event_type", None, None, ID)

        return HistoEventTypeTable(histoEventTypeTableUri)

    def isValid(self):
        return self.histoEventTypeTable.isValid()

    def events(self) -> dict:
        features = self.getFeatures()
        dic = dict()

        for feature in features:
            dic[feature.attribute(ID)] = feature.attribute(DESCRIPTION)

        return dic
