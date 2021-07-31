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

from datetime import datetime

def loadTsRrVec(sheet):
    rrVec = []
    tsVec = []
    for row in range(2, sheet.max_row+1):
        rrCell = "{}{}".format('C', row)
        rr = sheet[rrCell].value
        tsCell = "{}{}".format('B', row)
        ts = sheet[tsCell].value
        if rr > 0:
            tsVec.append(ts)
            rrVec.append(rr)
    return tsVec, rrVec

def loadTsEstAfVec(sheet):
    estAfVec = []
    tsVec = []
    for row in range(2, sheet.max_row+1):
        tsCell = "{}{}".format('A', row)
        ts = sheet[tsCell].value
        tsVec.append(ts)
        estAfCell = "{}{}".format('B', row)
        estAf = sheet[estAfCell].value
        estAfVec.append(estAf)
    return tsVec, estAfVec

def checkSheet(workbook):
    if getRrSheet(workbook) is None:
        return False
    else:
        return True

def getRegion(workbook, sheetName):
    regionPositions = []
    sheet = getSheet(workbook, sheetName)
    if sheet is not None:
        regionPositions = []
        try:
            noRegions = int(sheet['A2'].value)
        except Exception:
            return regionPositions
        for i in range(noRegions):
            cellName = "{}{}".format('C', i+2)
            start = sheet[cellName].value
            cellName = "{}{}".format('D', i+2)
            end = sheet[cellName].value
            regionPositions.append([start, end])
        return regionPositions

def getTsRrVEC(workbook):
    rrVec=[]
    tsVec = []
    sheets = getSheetsInSequence(workbook,'LT Heart Beats')
    for sheet in sheets:
        tsSheetVec, rrSheetVec = loadTsRrVec(sheet)
        tsVec  = tsVec + tsSheetVec
        rrVec  = rrVec + rrSheetVec
    return tsVec, rrVec

def getTsEstAfVEC(workbook):
    estAfVec=[]
    tsVec = []
    sheets = getSheetsInSequence(workbook,'EstAfProb')
    for sheet in sheets:
        tsSheetVec, estAfSheetVec = loadTsEstAfVec(sheet)
        tsVec  = tsVec + tsSheetVec
        estAfVec  = estAfVec + estAfSheetVec
    return tsVec, estAfVec
    
def putRegion(workbook, table, sheetName):
    sheet = getSheet(workbook, sheetName)
    if sheet is not None:
        workbook.remove_sheet(sheet)
    sheet =  workbook.create_sheet(sheetName)
    sheet['A1'] = 'No. of Regions'
    sheet['A2'] = table.rowCount()
    sheet['B1'] = 'Region type'
    sheet['C1'] = 'Region start'
    sheet['D1'] = 'Region end'
    for i in range(table.rowCount()):
        cellName = "{}{}".format('B', i+2)
        sheet[cellName].value = 'AF region'
        cellName = "{}{}".format('C', i+2)
        sheet[cellName].value = table.item(i, 1).text()
        cellName = "{}{}".format('D', i+2)
        sheet[cellName].value = table.item(i, 2).text()
        
def checkRR(workbook):
    sheet = getRrSheet(workbook)
    row = 102
    column = "C"
    cell_name = "{}{}".format(column, row)
    try:
        int(sheet[cell_name].value)
        return True
    except Exception:
        return False

def checkEstAfP(workbook):
    sheet = getSheet(workbook, 'EstAfProb')
    row = 2
    column = "B"
    cell_name = "{}{}".format(column, row)
    try:
        float(sheet[cell_name].value)
        return True
    except Exception:
        return False

def loadTimestamp(sheet):
    timestampVec = []
    for row in range(3, sheet.max_row+1):
        for column in "B":
            cell_name = "{}{}".format(column, row)
            timestamp = datetime.strptime(sheet[cell_name].value,
                                          '%Y-%m-%d %H:%M:%S.%f')
            timestampVec.append(timestamp.timestamp())
    return timestampVec

def getSheet(workbook, name):
    for sheet in workbook.worksheets:
        if sheet.title.startswith(name):
            return workbook[sheet.title]
        
def getSheetsInSequence(workbook, name):
    sheets = []
    for sheet in workbook.worksheets:
        if sheet.title.startswith(name):
            sheets.append(workbook[sheet.title])
    return sheets

def getRrSheet(workbook):
    for sheet in workbook.worksheets:
        if sheet.title.startswith('LT Heart Beats'):
            return workbook[sheet.title]






