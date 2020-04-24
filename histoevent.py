'''
Created on February, 05th 2020

@author: arxit
'''
import getpass
from PyQt5.QtCore import QDateTime
from qgis.core import QgsDataSourceUri, QgsFeature, QgsVectorLayer, QgsFeatureRequest, QgsExpression

from .layer import Layer

ID = "id"
EVENT_DATE = "event_date"
AUTHOR = "author"
TYPE_ID = "type_id"
DESCRIPTION = "description"


class HistoEvent(Layer):
    def __init__(self, uri: QgsDataSourceUri):
        super().__init__(uri)
        self.histoEventLayer = self.createVectorLayer()

    def getVectorLayer(self):
        return self.histoEventLayer

    @staticmethod
    def fromOtherLayerUri(uri: QgsDataSourceUri):
        histoEventUri = QgsDataSourceUri()
        histoEventUri.setConnection(uri.host(), uri.port(), uri.database(), uri.username(), uri.password(), uri.sslMode(), uri.authConfigId())
        histoEventUri.setDataSource(uri.schema(), "histo_event", None, None, "id")

        return HistoEvent(histoEventUri)

    def addEvent(self, type: int, description: str, date: QDateTime = QDateTime.currentDateTime(), author: str = getpass.getuser()) -> int:
        feature = QgsFeature(self.getVectorLayer().fields())
        feature.setAttribute(EVENT_DATE, date)
        feature.setAttribute(AUTHOR, author)
        feature.setAttribute(TYPE_ID, type)
        feature.setAttribute(DESCRIPTION, description)

        self.startEditing()

        self.addFeature(feature)

        self.commitChanges()

        sql = "event_date='{0}' AND author='{1}' AND type_id={2} AND description='{3}'"
        sql = sql.format(date.toString("yyyy-MM-dd hh:mm:ss.zzz"), author, type, description)

        for feature in self.getFeatures(QgsFeatureRequest(QgsExpression(sql))):
            return feature.attribute(ID)

        return -1
