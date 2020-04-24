# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveManagementTool
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

import os
import time
import getpass
import itertools

from typing import List, Tuple

from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, QComboBox, QTableWidgetItem, QAbstractItemView, QWidget, QCheckBox, QHBoxLayout, QPushButton, QHeaderView
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.core import QgsFeatureRequest, QgsProject, QgsFeature

from ...featuremode import Mode
from ...historyfeature import HistoryFeature
from ...histoparam import HistoParamTable
from ...histoeventtype import HistoEventTypeTable

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'saveManagementToolDialog.ui'))


class Column():
    Couche = 0
    Identifiant = 1
    Libelle = 2
    Changement = 3
    Enregistrer = 4
    Type = 5
    Description = 6


class SaveManagementToolDialog(QDialog, FORM_CLASS):
    lastDescription = None

    def __init__(
            self,
            layerName: str,
            tableName: str,
            histoParamTable: HistoParamTable,
            histoEventTypeTable: HistoEventTypeTable,
            addedFeatures: List[QgsFeature],
            modifiedFeatures: List[QgsFeature],
            deletedFeatures: List[QgsFeature],
            parent=None):
        '''
        Constructor.
        '''
        super(SaveManagementToolDialog, self).__init__(parent)
        self.events = []
        self.featuresToHistorize = []

        self.layerName = layerName
        self.id_field, self.display_field = histoParamTable.getTableConfiguration(tableName)
        self.eventTypes = histoEventTypeTable.events()

        self.features = []

        for feature in addedFeatures:
            self.features.append(HistoryFeature(feature, Mode(Mode.Ajout)))
        for feature in modifiedFeatures:
            self.features.append(HistoryFeature(feature, Mode(Mode.Modification)))
        for feature in deletedFeatures:
            self.features.append(HistoryFeature(feature, Mode(Mode.Suppression)))

        self.setupUi(self)

        headerList = ['Couche', 'Identifiant', 'Libellé', 'Changement', 'Enregistrer', 'Type', 'Description']
        self.tableSMT.setHorizontalHeaderLabels(headerList)

        self._setupTable()
        self._setupGroupModificationPanel()

        header = self.tableSMT.horizontalHeader()
        for i in range(0, len(headerList)-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.saveButton.clicked.connect(self._saveClick)

    def finalEvents(self) -> List[Tuple[int, unicode]]:
        return self.events

    def finalFeaturesToHistorize(self) -> List[HistoryFeature]:
        return self.featuresToHistorize

    def _setupTable(self):
        self.tableSMT.setRowCount(len(self.features))

        rowIndex = 0

        for feature in self.features:
            rowIndex = self._addRow(rowIndex, feature.feature, feature.mode)

    def _addRow(self, rowIndex: int, feature: QgsFeature, mode: Mode) -> int:
        self.tableSMT.setItem(rowIndex, Column.Couche, self._getTextCell(self.layerName))
        self.tableSMT.setItem(rowIndex, Column.Identifiant, self._getTextCell(str(feature.attribute(self.id_field))))
        self.tableSMT.setItem(rowIndex, Column.Libelle, self._getTextCell(str(feature.attribute(self.display_field))))
        self.tableSMT.setItem(rowIndex, Column.Changement, self._getTextCell(mode.toStr()))
        self.tableSMT.setCellWidget(rowIndex, Column.Enregistrer, self._getCheckbox())
        self.tableSMT.setCellWidget(rowIndex, Column.Type, self._getEventTypesComboBox())
        self.tableSMT.setItem(rowIndex, Column.Description, self._getTextCell("", True))

        return rowIndex + 1

    def _getTextCell(self, text: str, enabled: bool = False) -> QTableWidgetItem:
        widget = QTableWidgetItem(text)
        widget.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        if not enabled:
            widget.setFlags(Qt.ItemIsEditable)

        return widget

    def _getEventTypesComboBox(self, selectedValue: int = None):
        widget = QComboBox()
        selectedIndex = 0
        currentIndex = 0

        for k, v in self.eventTypes.items():
            widget.addItem(v, k)
            if k == selectedValue:
                selectedIndex = currentIndex
            currentIndex += 1

        widget.setCurrentIndex(selectedIndex)

        return widget

    def _getCheckbox(self, checked: bool = True):
        widget = QWidget()
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        return widget

    def _setupGroupModificationPanel(self):
        self.groupTypeCombobox.clear()

        for k, v in self.eventTypes.items():
            self.groupTypeCombobox.addItem(v, k)

        if SaveManagementToolDialog.lastDescription:
            self.groupDescriptionLineEdit.setText(SaveManagementToolDialog.lastDescription)

        self.applyGroupSettingsToSelectedButton.clicked.connect(self._applyGroupModificationToSelectedClick)
        self.applyGroupSettingsToAllButton.clicked.connect(self._applyGroupModificationToAllClick)

    def _applyGroupModificationToSelectedClick(self):
        selectedRows = list(map(lambda x: x.row(), self.tableSMT.selectionModel().selectedRows()))

        for rowIndex in selectedRows:
            self._setEnregistrerFromGroupModification(rowIndex)
            self._setTypeFromGroupModification(rowIndex)
            self._setDescriptionFromGroupModification(rowIndex)

    def _applyGroupModificationToAllClick(self):
        for rowIndex in range(0, self.tableSMT.rowCount()):
            self._setEnregistrerFromGroupModification(rowIndex)
            self._setTypeFromGroupModification(rowIndex)
            self._setDescriptionFromGroupModification(rowIndex)

    def _getEnregistrer(self, rowIndex: int) -> bool:
        return self.tableSMT.cellWidget(rowIndex, Column.Enregistrer).layout().itemAt(0).widget().isChecked()

    def _setEnregistrerFromGroupModification(self, rowIndex: int):
        return self.tableSMT.setCellWidget(rowIndex, Column.Enregistrer, self._getCheckbox(self.groupHistorizeCheckbox.isChecked()))

    def _getType(self, rowIndex: int) -> int:
        return self.tableSMT.cellWidget(rowIndex, Column.Type).currentData()

    def _setTypeFromGroupModification(self, rowIndex: int):
        return self.tableSMT.setCellWidget(rowIndex, Column.Type, self._getEventTypesComboBox(self.groupTypeCombobox.currentData()))

    def _getDescription(self, rowIndex: int) -> int:
        return self.tableSMT.item(rowIndex, Column.Description).text()

    def _setDescriptionFromGroupModification(self, rowIndex: int):
        return self.tableSMT.setItem(rowIndex, Column.Description, self._getTextCell(self.groupDescriptionLineEdit.text()))

    def _saveClick(self):
        rowIndicesToSave = list(filter(lambda x: self._getEnregistrer(x), range(0, self.tableSMT.rowCount())))
        events = set()

        for rowIndex in rowIndicesToSave:
            events.add((self._getType(rowIndex), self._getDescription(rowIndex)))

        self.events = list(events)

        for rowIndex in rowIndicesToSave:
            self.features[rowIndex].eventIndex = self.events.index((self._getType(rowIndex), self._getDescription(rowIndex)))
            self.featuresToHistorize.append(self.features[rowIndex])

        SaveManagementToolDialog.lastDescription = self.groupDescriptionLineEdit.text()

        self.accept()
