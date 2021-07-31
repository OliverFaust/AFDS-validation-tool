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
from PyQt5.QtWidgets import QMessageBox
import openpyxl
import excelProcessing


class LoadExcel(QRunnable):
    def __init__(self, main, sourceFileName):
        QRunnable.__init__(self)
        self.main = main
        self.__sourceFileName = sourceFileName

    def run(self):
        self.main.loadFilePath.setText(self.__sourceFileName)
        try:
            workbook = openpyxl.load_workbook(self.__sourceFileName)
        except Exception as msg:
            QMessageBox.information(self.main, "Error", str(msg))
            QMetaObject.invokeMethod(
                self.main, "setData", Qt.QueuedConnection, Q_ARG(
                    openpyxl.workbook.workbook.Workbook, workbook))
            return
        if not excelProcessing.checkSheet(workbook):
            QMessageBox.information(self.main, "Error","Excel sheet with RR intervals was not found")
            QMetaObject.invokeMethod(
                self.main, "setData", Qt.QueuedConnection, Q_ARG(
                    openpyxl.workbook.workbook.Workbook, workbook))
            return
        if not excelProcessing.checkRR(workbook):
            QMessageBox.information(
                self.main, "Error", "No RR intervals found")
            QMetaObject.invokeMethod(
                self.main, "setData", Qt.QueuedConnection, Q_ARG(
                    openpyxl.workbook.workbook.Workbook, workbook))
            return
        self.main.processButton.setEnabled(True)
        if not excelProcessing.checkEstAfP(workbook):
            QMetaObject.invokeMethod(
                self.main, "setData", Qt.QueuedConnection, Q_ARG(
                    openpyxl.workbook.workbook.Workbook, workbook))
            return
        self.main.plotButton.setEnabled(True)
        self.main.saveButton.setEnabled(True)
        QMetaObject.invokeMethod(self.main, "setData",
                                 Qt.QueuedConnection,
                                 Q_ARG(openpyxl.workbook.workbook.Workbook,
                                       workbook))
