#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is dual-licensed under the GNU General Public License,
# version 2 (GPL-2.0), or the GNU General Public License, version 3 (GPL-3.0).
# 
# You may choose to redistribute it and/or modify it under either of these licenses:
# 
# 1. GNU General Public License, version 2, as published by the Free Software Foundation.
#    See <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html> for details.
#
# 2. GNU General Public License, version 3, as published by the Free Software Foundation.
#    See <https://www.gnu.org/licenses/gpl-3.0.html> for details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import sqlite3
from pathlib import Path
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

class DeleteDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteDialog, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon('icon/RCEID.png'))
        self.setWindowTitle("Delete Patient Information")
        self.setFixedWidth(450)
        self.setFixedHeight(120)

        self.QBtn = QPushButton()
        self.QBtn.setText("  Delete")
        self.QBtn.setFixedSize(200, 50)
        self.QBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxCritical')))
        self.QBtn.setStyleSheet(Path('css/buttonv2.css').read_text())
        self.QBtn.clicked.connect(self.deletestudent)

        self.layout = QFormLayout()
        self.layout2 = QVBoxLayout()

        self.deleteinput = QLineEdit()
        self.deleteinput.setStyleSheet(Path('css/button.css').read_text())
        self.deleteinput.setPlaceholderText("Individual ID")

        self.layout.addRow(QLabel("Individual ID:"),self.deleteinput)

        self.layout2.addLayout(self.layout)
        self.layout2.addWidget(self.QBtn ,alignment=QtCore.Qt.AlignRight)
        self.setLayout(self.layout2)

    def deletestudent(self):
        try:
            delrol = ""
            delrol = self.deleteinput.text()
            if delrol == "":
                raise Exception("Please insert individual ID")

            self.conn = sqlite3.connect("database/individualDB.db")
            self.c = self.conn.cursor()

            query_check = "SELECT 1 FROM individualDB WHERE Individual = ?"
            self.c.execute(query_check, (delrol,))
            result = self.c.fetchone()

            if result is None:
                raise Exception("No data found for the given Individual")

            query_delete = "DELETE FROM individualDB WHERE Individual = ?"
            self.c.execute(query_delete, (delrol,))
            self.conn.commit()
            self.c.close()
            self.conn.close()

            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Information)
            msg.setText(" Deleted From individual successfully \n[ Please proceed to Tools -> Refresh ]")
            msg.setWindowTitle("Successfully")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.close()


        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Error : {e}")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

