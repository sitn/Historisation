from qgis.PyQt.QtWidgets import QMessageBox, QDialog

from . import main
from .widgets.configuration.ajoutConfigurationBD_dialog import ajoutConfigurationBD

def defineDBSettings(plugin):

    dlg = ajoutConfigurationBD()

    answer = dlg.exec()

    if answer == 1:
        action = plugin.actions[0]
        action.setEnabled(True)
