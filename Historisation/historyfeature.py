'''
Created on February, 05th 2020

@author: arxit
'''
from typing import Tuple

from qgis.core import QgsFeature

from .featuremode import Mode


class HistoryFeature(object):
    def __init__(self, feature: QgsFeature, mode: Mode):
        self.feature = feature
        self.mode = mode
        self.eventIndex = None
