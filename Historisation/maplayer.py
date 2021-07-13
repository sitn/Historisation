'''
Created on January, 29th 2020

@author: arxit
'''
from datetime import datetime
from PyQt5.QtCore import QDateTime
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsFeatureRequest, Qgis
from qgis.gui import QgisInterface

from .histoparam import HistoParamTable
from .layer import Layer
from .histolayer import HistoLayer
from .histoevent import HistoEvent
from .histoeventtype import HistoEventTypeTable
from .historyfeature import HistoryFeature
from .featuremode import Mode
from .valuemap import ValueMap

from .widgets.saveManagementTool.saveManagementToolDialog import SaveManagementToolDialog


class MapLayer(Layer):
    def __init__(self, mapLayer: QgsVectorLayer, iface: QgisInterface):
        super().__init__(mapLayer.dataProvider().uri())

        self.iface = iface
        self.isValid = False

        if type(mapLayer) is not QgsVectorLayer:
            return

        if mapLayer.providerType() != "postgres":
            return

        self.isValid = mapLayer.isValid()

        self.mapLayer = mapLayer
        self.listenToCommit = False

        self.histoParamTable = HistoParamTable.fromOtherLayerUri(mapLayer.dataProvider().uri())
        self.histoLayer = HistoLayer.fromMapLayerUri(mapLayer.dataProvider().uri(), self.histoParamTable)
        self.histoEvent = HistoEvent.fromOtherLayerUri(mapLayer.dataProvider().uri())
        self.histoEventTypeTable = HistoEventTypeTable.fromOtherLayerUri(mapLayer.dataProvider().uri())
        self._initValueMaps()

    def _initValueMaps(self):
        self.valueMaps = []

        for field in self.mapLayer.fields():
            if field.editorWidgetSetup().type() == "ValueMap":
                self.valueMaps.append(ValueMap.fromValueMapConfig(field.name(), field.editorWidgetSetup().config()))
            if field.editorWidgetSetup().type() == "ValueRelation":
                self.valueMaps.append(ValueMap.fromValueRelationConfig(field.name(), field.editorWidgetSetup().config()))

    def getVectorLayer(self):
        return self.mapLayer

    def isHistorisable(self) -> bool:
        return self.isValid and type(self.mapLayer) is QgsVectorLayer and self.histoParamTable.isValid()

    def isAlreadyHistorized(self) -> bool:
        return self.isHistorisable() and self.histoParamTable.containsTableName(self.uri.table())

    def setListenToCommit(self, listen: bool):
        if not self.isAlreadyHistorized():
            return

        if self.listenToCommit == listen:
            return

        if listen:
            self.getVectorLayer().beforeCommitChanges.connect(self.onBeforeCommitChanges)
            self.getVectorLayer().committedFeaturesAdded.connect(self.onCommittedFeaturesAdded)
            self.getVectorLayer().committedAttributeValuesChanges.connect(self.onCommittedAttributeValuesChanges)
            self.getVectorLayer().committedGeometriesChanges.connect(self.onCommittedGeometriesChanges)
            self.getVectorLayer().committedFeaturesRemoved.connect(self.onCommittedFeaturesRemoved)
            self.getVectorLayer().afterCommitChanges.connect(self.onAfterCommitChanges)
        else:
            self.getVectorLayer().beforeCommitChanges.disconnect(self.onBeforeCommitChanges)
            self.getVectorLayer().committedFeaturesAdded.disconnect(self.onCommittedFeaturesAdded)
            self.getVectorLayer().committedAttributeValuesChanges.disconnect(self.onCommittedAttributeValuesChanges)
            self.getVectorLayer().committedGeometriesChanges.disconnect(self.onCommittedGeometriesChanges)
            self.getVectorLayer().committedFeaturesRemoved.disconnect(self.onCommittedFeaturesRemoved)
            self.getVectorLayer().afterCommitChanges.disconnect(self.onAfterCommitChanges)

    def historizeTable(self, displayField: str, idField: str):
        now = QDateTime.currentDateTime()

        codeFields = []

        for valueMap in self.valueMaps:
            codeFields.append(valueMap.sourceFieldName)

        query = "SELECT {0}.create_h_table('{0}', '{1}', '{2}', ARRAY[{3}]::text[] );".format(self.uri.schema(), self.uri.table(),
                                                                                              self.uri.geometryColumn(), "'{0}'".format("','".join(codeFields)) if len(codeFields) > 0 else "")
        conn = self.getSqlConnection()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchone()
        conn.commit()

        eventId = self.histoEvent.addEvent(0, "Historisation de la table " + self.uri.table(), now)

        self.histoParamTable.addTableName(self.uri.table(), displayField, idField)

        self.histoLayer = HistoLayer.fromMapLayerUri(self.mapLayer.dataProvider().uri(), self.histoParamTable)

        self.histoLayer.initializeTable(now, eventId, self.valueMaps)

    def onBeforeCommitChanges(self):
        self.added = []
        self.modifiedGeometries = []
        self.modifiedAttributes = []
        self.deletedIds = []

    def onCommittedFeaturesAdded(self, layerId, addedFeatures):
        self.added = addedFeatures

    def onCommittedAttributeValuesChanges(self, layerId, changedAttributesValues):
        self.modifiedAttributes = changedAttributesValues

    def onCommittedGeometriesChanges(self, layerId, changedGeometries):
        self.modifiedGeometries = changedGeometries

    def onCommittedFeaturesRemoved(self, layerId, deletedFeatureIds):
        self.deletedIds = deletedFeatureIds

    def onAfterCommitChanges(self):
        # Get modifications
        addedIds = list(map(lambda x: x.id(), self.added))
        added = [] if len(addedIds) == 0 else list(self.getFeatures(QgsFeatureRequest(addedIds)))

        modifiedIds = list(set(list(self.modifiedGeometries)+list(self.modifiedAttributes)))
        modified = [] if len(modifiedIds) == 0 else list(self.getFeatures(QgsFeatureRequest(modifiedIds)))

        deletedIds = list(self.deletedIds)
        deleted = [] if len(deletedIds) == 0 else list(self.getDatabaseFeatures(QgsFeatureRequest(deletedIds)))

        # Get user events
        dlg = SaveManagementToolDialog(self.getVectorLayer().name(), self.uri.table(), self.histoParamTable, self.histoEventTypeTable, added, modified, deleted)
        dlg.exec()

        # Add events
        eventDate = QDateTime.currentDateTime()
        eventMap = dict()

        for index, event in enumerate(dlg.finalEvents()):
            (type, description) = event
            eventId = self.histoEvent.addEvent(type, description, eventDate)
            eventMap[index] = eventId

        # History features
        self.histoLayer.startEditing()

        for historyFeature in dlg.finalFeaturesToHistorize():
            if historyFeature.mode.mode == Mode.Ajout:
                self.histoLayer.addHistoFeature(historyFeature.feature, eventDate, eventMap[historyFeature.eventIndex], self.valueMaps)
            elif historyFeature.mode.mode == Mode.Modification:
                self.histoLayer.updateHistoFeature(historyFeature.feature, eventDate, eventMap[historyFeature.eventIndex], self.valueMaps)
            elif historyFeature.mode.mode == Mode.Suppression:
                self.histoLayer.deleteHistoFeature(historyFeature.feature, eventDate, eventMap[historyFeature.eventIndex])

        self.histoLayer.commitChanges()

        self.iface.messageBar().pushMessage("Information", "L'historisation des objets est terminée", Qgis.Info)
