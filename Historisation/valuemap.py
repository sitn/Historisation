'''
Created on February, 05th 2020

@author: arxit
'''
from qgis.core import QgsDataSourceUri, QgsFeature, QgsProject

from .layer import Layer


class ValueMap(object):
    def __init__(self, sourceFieldName: str, destinationFieldName: str, valueMap: dict):
        self.sourceFieldName = sourceFieldName
        self.destinationFieldName = destinationFieldName
        self.valueMap = valueMap

    @staticmethod
    def fromValueMapConfig(fieldName: str, config: dict):
        sourceFieldName = fieldName
        destinationFieldName = fieldName+"_desc"
        valueMap = dict()

        for item in config["map"]:
            for k, v in item.items():
                valueMap[v] = k

        return ValueMap(sourceFieldName, destinationFieldName, valueMap)

    @staticmethod
    def fromValueRelationConfig(fieldName: str, config: dict):
        sourceFieldName = fieldName
        destinationFieldName = fieldName+"_desc"
        valueMap = dict()

        relatedLayerId = config["Layer"]

        relatedLayer = None

        for layer in QgsProject.instance().mapLayers().values():
            if layer.id() == relatedLayerId:
                relatedLayer = Layer(layer.dataProvider().uri())

        if relatedLayer is not None:
            for feature in relatedLayer.getFeatures():
                valueMap[str(feature.attribute(config["Key"]))] = str(feature.attribute(config["Value"]))

        return ValueMap(sourceFieldName, destinationFieldName, valueMap)

    def setDestinationValue(self, sourceFeature: QgsFeature, destinationFeature: QgsFeature):
        sourceValue = str(sourceFeature.attribute(self.sourceFieldName))

        if sourceValue not in self.valueMap:
            return

        destinationFeature.setAttribute(self.destinationFieldName, self.valueMap[sourceValue])
