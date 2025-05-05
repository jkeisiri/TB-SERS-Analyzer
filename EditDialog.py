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


from tkinter import filedialog
from tkinter import Tk
import sqlite3
from pathlib import Path
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

Tk().withdraw()

class EditDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(EditDialog, self).__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('icon/RCEID.png'))
        self.setWindowTitle("Edit Patient Information")
        self.setFixedSize(550, 530)

        self.layout = QFormLayout()

        self.QBSearch = QPushButton()
        self.QBSearch.setText("Search")
        self.QBSearch.setStyleSheet(Path('css/button.css').read_text())
        self.QBSearch.clicked.connect(self.searchsIndividual)

        self.Individual = QLineEdit()
        self.Individual.setPlaceholderText("Individual ID")
        self.Individual.setStyleSheet(Path('css/button.css').read_text())

        self.HN = QLineEdit()
        self.HN.setPlaceholderText("HN")
        self.HN.setStyleSheet(Path('css/button.css').read_text())

        self.Sample = QLineEdit()
        self.Sample.setStyleSheet(Path('css/button.css').read_text())
        self.Sample.setPlaceholderText("Sample")

        self.QBaddfile= QPushButton()
        self.QBaddfile.setText("Choose file ...")
        self.QBaddfile.setStyleSheet(Path('css/button.css').read_text())
        self.QBaddfile.clicked.connect(self.addfile)

        self.Gender = QLineEdit()
        self.Gender.setStyleSheet(Path('css/button.css').read_text())
        self.Gender.setPlaceholderText("Gender")

        self.Age = QLineEdit()
        self.Age.setStyleSheet(Path('css/button.css').read_text())
        self.Age.setPlaceholderText("Age")

        self.Province = QLineEdit()
        self.Province.setStyleSheet(Path('css/button.css').read_text())
        self.Province.setPlaceholderText("Province")

        self.Address = QLineEdit()
        self.Address.setPlaceholderText("Address")
        self.Address.setStyleSheet(Path('css/button.css').read_text())

        self.IndividualID = QLineEdit()
        self.IndividualID.setStyleSheet(Path('css/button.css').read_text())
        self.IndividualID.setPlaceholderText("Individual ID")

        self.title = QLineEdit()
        self.title.setStyleSheet(Path('css/button.css').read_text())
        self.title.setPlaceholderText("Title Report")

        self.QBtnlogo = QPushButton()
        self.QBtnlogo.setText("Choose file ...")
        self.QBtnlogo.setStyleSheet(Path('css/button.css').read_text())


        self.addresslogo = QLabel("")
        self.addresslogo.setFont(QFont("Arial", 8, QFont.Bold))
        self.addresslogo.setStyleSheet("color: red;")

        self.QBReport = QPushButton()
        self.QBReport.setText("Edit Information")
        self.QBReport.clicked.connect(self.editIndividual)
        self.QBReport.setFixedSize(180, 50)
        self.QBReport.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))
        self.QBReport.setStyleSheet(Path('css/buttonv2.css').read_text())


        self.layout.addRow(QLabel("Search Individual:"), self.IndividualID)
        self.layout.addRow(QLabel(" "), self.QBSearch)
        self.layout.addRow(QLabel(" "))

        self.labelIn = QLabel("Patient Information:", self)
        self.labelIn.setFont(QFont("Arial", 11, QFont.Bold))

        self.layout2 = QVBoxLayout()

        self.layout.addRow(self.labelIn)
        self.layout.addRow(QLabel("Individual ID:"), self.Individual)
        self.layout.addRow(QLabel("HN:"), self.HN)
        self.layout.addRow(QLabel("Sample:"), self.Sample)
        self.layout.addRow(QLabel("File:"), self.QBaddfile)
        self.layout.addRow(QLabel("Gender:"), self.Gender)
        self.layout.addRow(QLabel("Age:"), self.Age)
        self.layout.addRow(QLabel("Province:"), self.Province)
        self.layout.addRow(QLabel("Address:"), self.Address)

        self.layout2.addLayout(self.layout)
        self.layout2.addWidget(self.QBReport, alignment=QtCore.Qt.AlignRight)

        self.setLayout(self.layout2)

    def addfile(self):

        try:

            files = filedialog.askopenfilename(title="Please select a file",
                                               filetypes=(('txt files', '*.txt'), ('wdf files', '*.wdf')))

            if (files == ''):
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

    def searchsIndividual(self):

        try:
            searchrol = self.IndividualID.text()
            if searchrol == "" :
                raise Exception("Please insert individual ID")

            self.conn = sqlite3.connect("database/individualDB.db")
            self.c = self.conn.cursor()

            query_check = "SELECT 1 FROM individualDB WHERE Individual = ?"
            self.c.execute(query_check, (searchrol,))
            result = self.c.fetchone()

            if result is None:
                raise Exception("No data found for the given Individual")

            query = "SELECT * FROM individualDB WHERE Individual = ?"
            self.c.execute(query, (searchrol,))

            row = self.c.fetchone()

            self.Individual.setText(row[1])
            self.HN.setText(row[2])
            self.Sample.setText(row[3])
            self.Gender.setText(row[4])
            self.Age.setText(str(row[5]))
            self.Province.setText(str(row[6]))
            self.Address.setText(str(row[7]))

            self.conn.commit()
            self.c.close()
            self.conn.close()

        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Error: {e}")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def editIndividual(self):

            nIndividual = nHN = nSample = nAddress = nGender = nProvince = nAge = ""

            nIndividual = self.Individual.text()
            nHN = self.HN.text()
            nSample = self.Sample.text()
            nGender = self.Gender.text()
            nAge = self.Age.text()
            nProvince = self.Province.text()
            nAddress = self.Address.text()

            try:
                if nIndividual == "" or nHN == "" or nSample == "" or nAddress == "" or nGender == "" or nProvince == "" or nAge == "":
                    raise Exception("Please insert clinical data")

                self.conn = sqlite3.connect("database/individualDB.db")
                self.c = self.conn.cursor()

                self.c.execute(
                    "UPDATE individualDB SET HN = ?, Sample = ?, Gender = ?, Age = ?, Province = ?, Address = ? WHERE Individual = ?",
                    (nHN, nSample, nGender, nAge, nProvince, nAddress, nIndividual))

                self.conn.commit()
                self.c.close()
                self.conn.close()

                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    "Clinical data is Edited successfully to the database \n        [ Please proceed to Tools -> Refresh ]")
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