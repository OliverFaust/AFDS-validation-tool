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
# import hrClassification
import openpyxl


class EstimateAfProbability(QRunnable):
    def __init__(self, main, workbook):
        QRunnable.__init__(self)
        self.main = main
        self.__workbook = workbook

    def run(self):
        # Validate your own model
        #self.__workbook = hrClassification.processData(self.__workbook)
        QMetaObject.invokeMethod(self.main, "setProcessedWorkbook",
                                 Qt.QueuedConnection,
                                 Q_ARG(openpyxl.workbook.workbook.Workbook,
                                       self.__workbook))