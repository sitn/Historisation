'''
Created on February, 05th 2020

@author: arxit
'''
from typing import List
from PyQt5.QtCore import QDateTime
from qgis.core import QgsDataSourceUri, QgsFeature, QgsVectorLayer, QgsFeatureRequest, QgsExpression, QgsGeometry

from .layer import Layer
from .histoparam import HistoParamTable
from .valuemap import ValueMap

HISTO_ID = "histo_id"
START_DATE = "start_date"
END_DATE = "end_date"
START_EVENT_ID = "start_event_id"
END_EVENT_ID = "end_event_id"


class HistoLayer(Layer):
    def __init__(self, uri: QgsDataSourceUri, id_field: str, display_field: str):
        super().__init__(uri)
        self.histoLayer = self.createVectorLayer()
        self.id_field = id_field
        self.display_field = display_field

    def getVectorLayer(self):
        return self.histoLayer

    @staticmethod
    def fromMapLayerUri(uri: QgsDataSourceUri, histoParamTable: HistoParamTable):
        histoUri = QgsDataSourceUri()
        histoUri.setConnection(uri.host(), uri.port(), uri.database(), uri.username(), uri.password(), uri.sslMode(), uri.authConfigId())
        histoUri.setDataSource(uri.schema(), uri.table()+"_h", uri.geometryColumn() if len(uri.geometryColumn()) > 0 else None, None, HISTO_ID)

        id_field, display_field = histoParamTable.getTableConfiguration(uri.table())

        return HistoLayer(histoUri, id_field, display_field)

    def initializeTable(self, startDate: QDateTime, eventId: int, valueMaps: List[ValueMap]):
        self.startEditing()

        for feature in self.getFeatures():
            self._setStartDate(feature, startDate)
            self._setStartEventId(feature, eventId)
            for valueMap in valueMaps:
                valueMap.setDestinationValue(feature, feature)
            self.updateFeature(feature)

        self.commitChanges()

    def addHistoFeature(self, currentFeature: QgsFeature, eventDate: QDateTime, eventId: int, valueMaps: List[ValueMap]):
        histoFeature = QgsFeature(self.getVectorLayer().fields())

        histoFeature.setGeometry(QgsGeometry(currentFeature.geometry()))

        for field in currentFeature.fields():
            histoFeature.setAttribute(field.name(), currentFeature.attribute(field.name()))

        self._setStartDate(histoFeature, eventDate)
        self._setStartEventId(histoFeature, eventId)

        for valueMap in valueMaps:
            valueMap.setDestinationValue(histoFeature, histoFeature)

        self.addFeature(histoFeature)

    def updateHistoFeature(self, currentFeature: QgsFeature, eventDate: QDateTime, eventId: int, valueMaps: List[ValueMap]):
        self.deleteHistoFeature(currentFeature, eventDate, eventId)
        self.addHistoFeature(currentFeature, eventDate, eventId, valueMaps)

    def deleteHistoFeature(self, currentFeature: QgsFeature, eventDate: QDateTime, eventId: int):
        where = "{0}='{1}' AND {2} IS NULL".format(self.id_field, currentFeature.attribute(self.id_field), END_DATE)
        histoFeatures = list(self.getFeatures(QgsFeatureRequest(QgsExpression(where))))

        if len(histoFeatures) == 0:
            return  # Raise exception

        histoFeature = histoFeatures[0]

        self._setEndDate(histoFeature, eventDate)
        self._setEndEventId(histoFeature, eventId)

        self.updateFeature(histoFeature)

    def _setStartDate(self, feature: QgsFeature, startDate: QDateTime = QDateTime.currentDateTime()):
        feature.setAttribute(START_DATE, startDate)

    def _setEndDate(self, feature: QgsFeature, endDate: QDateTime = QDateTime.currentDateTime()):
        feature.setAttribute(END_DATE, endDate)

    def _setStartEventId(self, feature: QgsFeature, eventId: int):
        feature.setAttribute(START_EVENT_ID, eventId)

    def _setEndEventId(self, feature: QgsFeature, eventId: int):
        feature.setAttribute(END_EVENT_ID, eventId)
