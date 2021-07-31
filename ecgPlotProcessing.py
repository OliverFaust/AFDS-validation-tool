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

from PyQt5.QtCore import QRunnable, QMetaObject, Qt, Q_ARG
from datetime import datetime, timedelta
from pycsp.parallel import process, Channel, Parallel, shutdown, retire
import excelProcessing
noWorkers = 5

class EcgPlotProcessing(QRunnable):
    def __init__(self, main, workbook, startEnd):
        QRunnable.__init__(self)
        self.main = main
        self.__workbook = workbook
        self.startEnd = startEnd

    def run(self):
        ecgSnippets = self.getEcgSnippetsPar2(self.__workbook, self.startEnd)
        QMetaObject.invokeMethod(self.main, "setEcgPlotProcessed",
                                 Qt.QueuedConnection,
                                 Q_ARG(list, ecgSnippets))
        
    def inRange(self, timestamp, startEnd, cnt):
        preFetch = 10
        postFetch = 10    
        if cnt == len(startEnd):
            return False
        roi = startEnd[cnt]
        start = roi - timedelta(seconds=preFetch)
        end = roi + timedelta(seconds=postFetch)
        if timestamp  >= start and timestamp < end:       
            return True
        return self.inRange(timestamp, startEnd, cnt+1)
    
    @process
    def timestampSource(self, data_out, sheet):
        chanNo = 0
        cout = [x.writer() for x in data_out]
        for row in range(2, sheet.max_row+1):
            cell_name = "{}{}".format("B", row)      
            data = {"timestamp": sheet[cell_name].value,
                    "row": row,
                    "inRoi": False}
            cout[chanNo](data)
            chanNo = (chanNo + 1) % len(cout)
        for c in cout:
            retire(c)
                 
    @process
    def worker(self,data_in, res_out, startEnd):
        while True:
            data = data_in()
            data["timestamp"] = datetime.strptime(data["timestamp"],
                          '%Y-%m-%d %H:%M:%S.%f')
            data["inRoi"] = self.inRange(data["timestamp"], startEnd, 0)
            res_out(data)
        
    @process
    def timestampSink(self, res_in, sheet, ecgSnippets):
        inRoiDelay = False
        timestampVec = []
        ecgVec = []    
        cin = [c.reader() for c in res_in]
        while True:
            for c in cin:
                data = c()
                if data["inRoi"] == True:
                    cell_name = "{}{}".format("A", data["row"])
                    ecgVec.append(sheet[cell_name].value)
                    timestampVec.append(data["timestamp"].timestamp())
                else:
                    if inRoiDelay == True:
                        ecgSnippets.append({"exgTimestampVec": timestampVec,
                        "ecgVec": ecgVec,
                        })
                inRoiDelay = data["inRoi"]      
        
    def getEcgSnippetsPar2(self, workbook, startEnd):     
        data = Channel(buffer=10)*noWorkers
        res = Channel(buffer=10)*noWorkers
        sheetName = 'LT Setup Mode'
        sheet = excelProcessing.getSheet(workbook, sheetName)
        if sheet == None:
            return 
        ecgSnippets = []
        Parallel(
            self.timestampSource(data, sheet),
            [self.worker(+s, -d, startEnd) for s, d in zip(data, res)],
            self.timestampSink(res, sheet, ecgSnippets)
        ) 
        shutdown()
        return ecgSnippets    
        
    def getEcgSnippetsPar(self, workbook, startEnd):     
        sheetName = 'LT Setup Mode'
        inRoi = False
        inRoiDelay = False
        timestampVec = []
        ecgVec = []    
        ecgSnippets = []
        sheet = excelProcessing.getSheet(workbook, sheetName)
        if sheet == None:
            return ecgSnippets
        for row in range(2, sheet.max_row+1):
            cell_name = "{}{}".format("B", row)      
            timestamp = datetime.strptime(sheet[cell_name].value,
                                  '%Y-%m-%d %H:%M:%S.%f')
            inRoi = self.inRange(timestamp, startEnd, 0)
            if inRoi == True:
                cell_name = "{}{}".format("A", row)
                ecgVec.append(sheet[cell_name].value)
                timestampVec.append(timestamp.timestamp())
            else:
                if inRoiDelay == True:
                    ecgSnippets.append({"exgTimestampVec": timestampVec,
                    "ecgVec": ecgVec,
                    })
            inRoiDelay = inRoi 
        return ecgSnippets
            
    def getEcgSnippets(self, workbook, startEnd):       
        sheetName = 'LT Setup Mode'
        name = sheetName
        inRoi = False
        inRoiDelay = False
        timestampVec = []
        ecgVec = []    
        ecgSnippets = []
        preFetch = 10
        postFetch = 10
        sheet = excelProcessing.getSheet(workbook, name)
        if sheet == None:
            return ecgSnippets
        name = sheetName 
        for row in range(2, sheet.max_row+1):
            cell_name = "{}{}".format("B", row)
            timestamp = datetime.strptime(sheet[cell_name].value,
                                          '%Y-%m-%d %H:%M:%S.%f')
            for roi in startEnd:
                start = roi - timedelta(seconds=preFetch)
                end = roi + timedelta(seconds=postFetch)
                if timestamp  >= start and timestamp < end: 
                    cell_name = "{}{}".format("A", row)
                    ecgVec.append(sheet[cell_name].value)
                    timestampVec.append(timestamp.timestamp())
                    inRoi = True
                    break
                inRoi = False
            if inRoi == False and inRoiDelay == True:
                ecgSnippets.append({"exgTimestampVec": timestampVec,
                "ecgVec": ecgVec,
                })
            inRoiDelay = inRoi
        return ecgSnippets        