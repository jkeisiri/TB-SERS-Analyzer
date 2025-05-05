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
from tkinter import filedialog
from tkinter import Tk
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


Tk().withdraw()


class InsertDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(InsertDialog, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon('icon/RCEID.png'))
        self.setFixedSize(550,450)
        self.setWindowTitle("Insert Patient Information")

        self.layout = QFormLayout()

        self.QBsubmit = QPushButton()
        self.QBsubmit.setText(" Insert Information")
        self.QBsubmit.setFixedSize(180, 50)
        self.QBsubmit.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogNewFolder')))
        self.QBsubmit.setStyleSheet(Path('css/buttonv2.css').read_text())
        self.QBsubmit.clicked.connect(self.addIndividual)

        self.Individual = QLineEdit()
        self.Individual.setPlaceholderText("Individual ID")
        self.Individual.setStyleSheet(Path('css/button.css').read_text())

        self.HN = QLineEdit()
        self.HN.setPlaceholderText("HN")
        self.HN.setStyleSheet(Path('css/button.css').read_text())

        self.Sample = QComboBox()
        self.Sample.setStyleSheet(Path('css/button.css').read_text())
        self.Sample.addItem("Blood")
        #self.branchinput.addItem("Urine") Coming in the future
        #self.branchinput.addItem("Saliva") Coming in the future

        self.Choosefile = QPushButton()
        self.Choosefile.setText("Choose file ...")
        self.Choosefile.setStyleSheet(Path('css/button.css').read_text())
        self.Choosefile.clicked.connect(self.addfile)

        self.Gender = QComboBox()
        self.Gender.setStyleSheet(Path('css/button.css').read_text())
        self.Gender.addItem("Male")
        self.Gender.addItem("Female")
        self.Gender.addItem("Other")

        self.Age = QLineEdit()
        self.Age.setStyleSheet(Path('css/button.css').read_text())
        self.Age.setPlaceholderText("Age")

        self.Province = QLineEdit()
        self.Province.setStyleSheet(Path('css/button.css').read_text())
        self.Province.setPlaceholderText("Province")

        self.Address = QLineEdit()
        self.Address.setPlaceholderText("Address")
        self.Address.setStyleSheet(Path('css/button.css').read_text())

        self.label = QLabel("Patient Information:", self)
        self.label.setFont(QFont("Arial", 11, QFont.Bold))

        self.layout2 = QVBoxLayout()

        self.layout.addRow(self.label)
        self.layout.addRow(QLabel(""))
        self.layout.addRow(QLabel("Individual ID:"), self.Individual)
        self.layout.addRow(QLabel("HN:"), self.HN)
        self.layout.addRow(QLabel("Sample:"), self.Sample)
        self.layout.addRow(QLabel("File:"), self.Choosefile)
        self.layout.addRow(QLabel("Gender:"), self.Gender)
        self.layout.addRow(QLabel("Age:"), self.Age)
        self.layout.addRow(QLabel("Province:"), self.Province)
        self.layout.addRow(QLabel("Address:"), self.Address)

        self.layout2.addLayout(self.layout)
        self.layout2.addWidget(self.QBsubmit,alignment=QtCore.Qt.AlignRight)
        self.setLayout(self.layout2)

    def addfile(self):
        try:
                files = filedialog.askopenfilename(title = "Please select a file",filetypes = (('txt files', '*.txt'),('wdf files', '*.wdf')))

                if(files==''):
                    raise Exception("Please select a file")
                else:
                    self.Address.setText(files)

                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Information)
                msg.setText("File selected successfully")
                msg.setWindowTitle("Successfully")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        except Exception:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Please select a file")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def addIndividual(self):

        nIndividual = nHN = nSample = nAddress = nGender = nProvince = nAge = ""

        nIndividual = self.Individual.text()
        nHN  = self.HN.text()
        nSample = self.Sample.itemText(self.Sample.currentIndex())
        nGender = self.Gender.itemText(self.Gender.currentIndex())
        nAge = self.Age.text()
        nProvince = self.Province.text()
        nAddress = self.Address.text()

        try:
            if nIndividual == "" or nHN == "" or nSample == "" or nAddress == "" or nGender == "" or nProvince == "" or nAge == "":
                raise Exception("Please insert clinical data")

            self.conn = sqlite3.connect("database/individualDB.db")
            self.c = self.conn.cursor()
            query_check = "SELECT 1 FROM individualDB WHERE Individual = ?"
            self.c.execute(query_check, (nIndividual,))
            result = self.c.fetchone()

            if result is not None:
                raise ValueError("The Individual ID already exists in the database")

            self.c.execute(
                "INSERT INTO individualDB(Individual, HN , Sample, Gender, Age, Province, Address) VALUES (?,?,?,?,?,?,?)",
                (nIndividual, nHN , nSample, nGender, nAge, nProvince, nAddress))
            self.conn.commit()
            self.c.close()
            self.conn.close()

            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Information)
            msg.setText("Clinical data is added successfully to the database \n        [ Please proceed to Tools -> Refresh ]")
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
