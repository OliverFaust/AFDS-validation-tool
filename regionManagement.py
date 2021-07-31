"""
Copyright (c) 01.07.2021, Dr Dr Oliver Faust

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License (GPL) as published by
the Free Software Foundation, either version 3 of this License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty, without even the implied warranty of
merchantibility or fitness for a particular purpose.
See the GNU General Public License for more details.

You should have received a copy of the GNU GPL along with this program.
If not, please see <https://www.gnu.org/licenses/#GPL>.
"""

from PyQt5.QtCore import Qt
import pyqtgraph as pg
import functools
from PyQt5 import QtWidgets
from datetime import datetime

class RegionManagement():
    def __init__(self):
        self.regionCnt = 0
        self.regions = []
        self.regionList=[]
        
    def remove(self, regionTable, graphWidget):
        for i in range(regionTable.rowCount()):
            item = regionTable.item(i, 0)
            if item.checkState() == Qt.Checked:
                regionTable.removeRow(i) 
                graphWidget.removeItem(self.regions[i])
                del self.regions[i]
                del self.regionList[i]
                self.remove(regionTable, graphWidget)
                return

    def addDefaultRegion(self, regionTable, graphWidget, onChange, pos, color):
        span = pos[1]-pos[0]
        center = pos[0]+span/2
        start = center-span*0.05
        end = center+span*0.05
        self.addRegion(regionTable, graphWidget, onChange, start, end, color)
        
    def addRegion(self, regionTable, graphWidget, onChange, start, end, color): 
        region = pg.LinearRegionItem(brush=pg.mkBrush(color))
        region.setZValue(10)
        if len(self.regionList) == 0:
            idx=1
        else:
            idx = max(self.regionList) + 1                    
        self.regionList.append(idx)
        region.sigRegionChanged.connect(functools.partial(
            onChange, idx))
        region.setRegion([start, end])
        graphWidget.addItem(region, ignoreBounds=True)
        self.regions.append(region)
        rowPosition = regionTable.rowCount()
        regionTable.insertRow(rowPosition)
        regionItem = QtWidgets.QTableWidgetItem("AF region ")
        regionItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        regionItem.setCheckState(Qt.Unchecked)
        startTime = datetime.fromtimestamp(start)
        startItem = QtWidgets.QTableWidgetItem(
            datetime.strftime(startTime, '%Y-%m-%d %H:%M:%S.%f'))
        endTime = datetime.fromtimestamp(end)
        endItem = QtWidgets.QTableWidgetItem(
            datetime.strftime(endTime, '%Y-%m-%d %H:%M:%S.%f'))
        regionTable.setItem(rowPosition, 0, regionItem)
        regionTable.setItem(rowPosition, 1, startItem)
        regionTable.setItem(rowPosition, 2, endItem)   
        
    def highlightRow(self, regionTable, evt):
        for i in range(len(self.regions)):
            if self.regions[i].sceneBoundingRect().contains(evt):
                regionTable.selectRow(i)
                return
        regionTable.clearSelection()
    
    def setRegions(self, regionTable, graphWidget, onChange, regionPositions, color):
        self.regionCnt = 0
        self.regions = []
        self.regionList=[]
        while (regionTable.rowCount() > 0):
            regionTable.removeRow(0)
            
        for pos in regionPositions:
            region = pg.LinearRegionItem(brush=pg.mkBrush(color))
            region.setZValue(10)
            if len(self.regionList) == 0:
                idx=1
            else:
                idx = max(self.regionList) + 1                    
            self.regionList.append(idx)
            region.sigRegionChanged.connect(functools.partial(
                onChange, idx))
            startMs = datetime.strptime(pos[0], '%Y-%m-%d %H:%M:%S.%f')
            endMs = datetime.strptime(pos[1], '%Y-%m-%d %H:%M:%S.%f')
            region.setRegion([startMs.timestamp(), endMs.timestamp()])            
            self.regions.append(region)
            graphWidget.addItem(region, ignoreBounds=True)
            regionItem = QtWidgets.QTableWidgetItem("AF region ")
            regionItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            regionItem.setCheckState(Qt.Unchecked)
            startItem = QtWidgets.QTableWidgetItem(pos[0])
            endItem = QtWidgets.QTableWidgetItem(pos[1])
            rowPosition = regionTable.rowCount()
            regionTable.insertRow(rowPosition)
            regionTable.setItem(rowPosition, 0, regionItem)
            regionTable.setItem(rowPosition, 1, startItem)
            regionTable.setItem(rowPosition, 2, endItem)
            
    def getStartEndList(self, regionTable):
        startEndList = []
        for i in range(regionTable.rowCount()):
            start = datetime.strptime(regionTable.item(i, 1).text(),
                                          '%Y-%m-%d %H:%M:%S.%f')
            end = datetime.strptime(regionTable.item(i, 2).text(),
                                          '%Y-%m-%d %H:%M:%S.%f')
            startEndList.append([start,end])
        return startEndList
    
    def getSequencedStartEndList(self, regionTable):
        startEndList = []
        for i in range(regionTable.rowCount()):
            start = datetime.strptime(regionTable.item(i, 1).text(),
                                          '%Y-%m-%d %H:%M:%S.%f')
            end = datetime.strptime(regionTable.item(i, 2).text(),
                                          '%Y-%m-%d %H:%M:%S.%f')
            startEndList.append(start)
            startEndList.append(end)
        return startEndList