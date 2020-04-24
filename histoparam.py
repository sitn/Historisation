'''
Created on January, 29th 2020

@author: arxit
'''
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsFeatureRequest, QgsExpression, QgsFeature

from .layer import Layer

NOM_TABLE = "nom_table"
DISPLAY_FIELD = "display_field"
ID_FIELD = "id_field"


class HistoParamTable(Layer):
    def __init__(self, uri):
        super().__init__(uri)
        self.histoParamLayer = self.createVectorLayer()

    def getVectorLayer(self):
        return self.histoParamLayer

    @staticmethod
    def fromOtherLayerUri(uri: QgsDataSourceUri):
        histoParamLayerUri = QgsDataSourceUri()
        histoParamLayerUri.setConnection(uri.host(), uri.port(), uri.database(), uri.username(), uri.password(), uri.sslMode(), uri.authConfigId())
        histoParamLayerUri.setDataSource(uri.schema(), "histo_param", None, None, "id")

        return HistoParamTable(histoParamLayerUri)

    def isValid(self):
        return self.histoParamLayer.isValid()

    def containsTableName(self, tableName: str) -> bool:
        request = QgsFeatureRequest(QgsExpression("nom_table='{0}'".format(tableName)))
        features = self.getFeatures(request)

        for feature in features:
            return True

        return False

    def addTableName(self, tableName: str, displayField: str, idField: str) -> bool:
        feature = QgsFeature(self.getVectorLayer().fields())
        feature.setAttribute(NOM_TABLE, tableName)
        feature.setAttribute(DISPLAY_FIELD, displayField)
        feature.setAttribute(ID_FIELD, idField)
        self.getVectorLayer().dataProvider().addFeature(feature)

    def getTableConfiguration(self, tableName: str) -> (str, str):
        request = QgsFeatureRequest(QgsExpression("nom_table='{0}'".format(tableName))).setSubsetOfAttributes([ID_FIELD, DISPLAY_FIELD], self.getVectorLayer().fields())
        features = self.getFeatures(request)

        for feature in features:
            return feature.attribute(ID_FIELD), feature.attribute(DISPLAY_FIELD)

        return None, None
