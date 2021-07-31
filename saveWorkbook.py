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

from PyQt5.QtCore import QRunnable, QMetaObject, Qt
import excelProcessing

class SaveWorkbook(QRunnable):
    def __init__(self, main, fileName):
        QRunnable.__init__(self)
        self.main = main
        self.fileName = fileName

    def run(self):
        if self.fileName:
            excelProcessing.putRegion(self.main.workbook, self.main.rrAfRegionTable, 'Estimated AF Regions')
            excelProcessing.putRegion(self.main.workbook, self.main.ecgAfRegionTable, 'Expert AF Regions')
            self.main.workbook.save(self.fileName)

        QMetaObject.invokeMethod(self.main, "setSaveWorkbook",
                                 Qt.QueuedConnection)
