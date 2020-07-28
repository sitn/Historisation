# -*- coding: utf-8 -*-
'''
/***************************************************************************
 Historisation
                                 A QGIS plugin
 Historisation par SITN
                              -------------------
        begin                : 2019-08-01
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
'''
from __future__ import absolute_import
from builtins import object
from qgis.core import *
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QPushButton, QMenu
from qgis.PyQt.QtGui import QIcon
# Initialize Qt resources from file resources.py
from . import resources
from .project import *

# Import the code for the dialog
import os.path

# Global variables
PLUGIN_DIR = os.path.dirname(__file__)


class Historisation(object):
    '''
    QGIS Plugin Implementation.
    '''

    def __init__(self, iface):
        '''Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        '''

        # Save reference to the QGIS interface
        self.iface = iface

        # Register custom editors widgets

        # Declare instance attributes
        self.actions = []
        self.temp_actions = []
        self.menu = u'&Historisation'

        # Toolbar initialization
        self.toolbar = self.iface.addToolBar(u'Historisation')
        self.toolbar.setObjectName(u'Historisation')

        # QGIS interface hooks
        self.iface.projectRead.connect(self.onProjectOpened)
        self.iface.newProjectCreated.connect(self.onProjectOpened)

        # Load current project
        self.current_project = Project(self.iface)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        '''Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        '''

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if callback is not None:
            action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        '''
        Create the menu entries and toolbar icons inside the QGIS GUI.
        '''

        # New project
        self.add_action(
            ':/plugins/Historisation/widgets/configuration/icon.png',
            text=u'Activer l\'historisation sur la couche',
            callback=self.onConfigurationButtonClicked,
            status_tip=u'Activer l\'historisation sur la couche',
            parent=self.iface.mainWindow())

        # Update buttons availability
        self.updateGui()

    def updateGui(self):
        '''
        Updates the plugin GUI
        Disable buttons
        '''
        enabled = True

        for action in self.temp_actions:
            action.setEnabled(enabled)

    def onProjectOpened(self):
        self.current_project = Project(self.iface)

    def onConfigurationButtonClicked(self):
        if not self.current_project:
            return

        self.current_project.activateHistoryOnSelectedLayer()

    def unload(self):
        '''
        Removes the plugin menu item and icon from QGIS GUI.
        '''

        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)

        # remove the toolbar
        del self.toolbar

        # Disconnect Signals
        self.iface.projectRead.disconnect(self.onProjectOpened)
        self.iface.newProjectCreated.disconnect(self.onProjectOpened)
