# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import re

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QSizePolicy, QGridLayout
from qgis.core import Qgis
from qgis.gui import QgsMessageBar

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QSettings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ajoutConfigurationBD_dialog.ui'))


class ajoutConfigurationBD(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        '''
        Constructor.
        '''

        super(ajoutConfigurationBD, self).__init__(parent)
        QDialog.__init__(self)
        self.bar = QgsMessageBar()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.onButtonClicked)
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.bar, 0, 0, alignment=QtCore.Qt.AlignTop)
        settings = QSettings()
        is_defined = QSettings().value("HistorisationSITN/DB", None)
        if is_defined:
           self.pg_db_database.setText(settings.value("HistorisationSITN/DB", ''))
           self.pg_db_host.setText(settings.value("HistorisationSITN/DBHost", ''))
           self.pg_db_port.setText(settings.value("HistorisationSITN/DBPort", 5432))
           self.pg_db_user.setText(settings.value("HistorisationSITN/DBUser", ''))
           self.pg_db_password.setText(settings.value("HistorisationSITN/DBPassword", ''))


    def onButtonClicked(self):

        pg_db_database = self.pg_db_database.text()
        pg_db_user = self.pg_db_user.text()
        pg_db_password = self.pg_db_password.text()
        pg_db_port = self.pg_db_port.text()
        pg_db_host = self.pg_db_host.text()
        errors = False
        if pg_db_host is None or pg_db_host == '':
            self.bar.pushMessage("Paramètres", "un hôte pour la BD doit être défini", level=Qgis.Critical)
            errors = True
        if pg_db_database is None or pg_db_database == '':
            self.bar.pushMessage("Paramètres", "une BD doit être définie", level=Qgis.Critical)
            errors = True
        if pg_db_port is None or pg_db_port == '' or re.match(r'^[0-9]+$', pg_db_port) is None:
            self.bar.pushMessage("Paramètres", "un port doit être défini", level=Qgis.Critical)
            errors = True
        if pg_db_user is None or pg_db_user == '':
            self.bar.pushMessage("Paramètres", "un utilisateur doit être spécifié", level=Qgis.Critical)
            errors = True
        if pg_db_password is None or pg_db_password == '':
            self.bar.pushMessage("Paramètres", "un mot de passe doit être spécifié", level=Qgis.Critical)
            errors = True
        
        if errors is False:
            settings = QSettings()
            settings.setValue("HistorisationSITN/DB", pg_db_database)
            settings.setValue("HistorisationSITN/DBHost", pg_db_host)
            settings.setValue("HistorisationSITN/DBPort", pg_db_port)
            settings.setValue("HistorisationSITN/DBUser", pg_db_user)
            settings.setValue("HistorisationSITN/DBPassword", pg_db_password)

            self.accept()
