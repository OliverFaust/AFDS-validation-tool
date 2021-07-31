# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 09:19:13 2020

@author: Oliver Faust
"""
from PyQt5.QtCore import QRunnable, QMetaObject, Qt, Q_ARG
import excelProcessing
from datetime import datetime
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

from pycsp.parallel import process, Channel, Parallel, shutdown, AltSelect
from pycsp.parallel import InputGuard
noWorkers = 5

class PlotProcessing(QRunnable):
    def __init__(self, main, workbook):
        QRunnable.__init__(self)
        self.main = main
        self.__workbook = workbook

    def run(self):
        data = self.getPlotData(self.__workbook)
        end = round(len(data["estAfTsVec"])/2) + round(
            len(data["estAfTsVec"])*0.05)
        start = round(len(data["estAfTsVec"])/2) - round(
            len(data["estAfTsVec"])*0.05)
        defaultRegion = [data["estAfTsVec"][start], data["estAfTsVec"][end]]
        data.update({"defaultRegion": defaultRegion})
        QMetaObject.invokeMethod(self.main, "setPlotProcessed",
                                 Qt.QueuedConnection,
                                 Q_ARG(dict, data))
        
    @process
    def getHrData(self, hrRes_out, workbook):
        timestampVec = []
        tsVec, rrVec = excelProcessing.getTsRrVEC(workbook)
        for ts in tsVec:
            timestamp = datetime.strptime(ts,
                                          '%Y-%m-%d %H:%M:%S.%f')
            timestampVec.append(timestamp.timestamp())
        data = {"rrTsVec": timestampVec,
                "rrVec": rrVec,
                }
        hrRes_out(data)
    
    @process 
    def getEstAfData(self, estAfRes_out, workbook):
        timestampVec = []
        tsVec, estAfVec = excelProcessing.getTsEstAfVEC(workbook)
        for ts in tsVec:
            timestamp = datetime.strptime(ts,
                                          '%Y-%m-%d %H:%M:%S.%f')
            timestampVec.append(timestamp.timestamp())
        data = {"estAfTsVec": timestampVec,
                "estAfVec": estAfVec,
                }
        estAfRes_out(data)
        
    @process
    def sink(self, hrRes_in, estAfRes_in, data):
        for i in range(2):
            g, msg = AltSelect(InputGuard(hrRes_in), InputGuard(estAfRes_in))
            data.update(msg)    
    
    def getPlotData(self, workbook):
        data = {}
        hrRes = Channel()
        estAfRes = Channel()
        Parallel(
            self.getHrData(-hrRes, workbook),
            self.getEstAfData(-estAfRes, workbook),
            self.sink(+hrRes, +estAfRes, data)
        )
        shutdown()
        return data