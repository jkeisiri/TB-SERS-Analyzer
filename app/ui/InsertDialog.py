#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TB-SERS Analyzer
# Version: 1.0.0
# A machine learning– and deep learning–based platform for predicting
# latent tuberculosis infection (LTBI) using SERS data.
#
# Author:
#   Jukgarin Eisiri
#   M.Sc. Biomedical Science, Khon Kaen University
#   E-mail: jkeisiri@kkumail.com
# © 2026
#

import os
import sys

import sqlite3
from pathlib import Path
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog

# ----------------------------
# Resource path (PyInstaller safe)
# ----------------------------
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class InsertDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(InsertDialog, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
        self.setFixedSize(550,450)
        self.setWindowTitle("Insert Patient Information")

        self.layout = QFormLayout()

        self.QBsubmit = QPushButton()
        self.QBsubmit.setText(" Insert Information")
        self.QBsubmit.setFixedSize(180, 50)
        self.QBsubmit.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogNewFolder')))
        self.QBsubmit.setStyleSheet(Path(resource_path("app/resources/css/buttonv2.css")).read_text())
        self.QBsubmit.clicked.connect(self.addIndividual)

        self.Individual = QLineEdit()
        self.Individual.setPlaceholderText("Individual ID")
        self.Individual.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

        self.HN = QLineEdit()
        self.HN.setPlaceholderText("HN")
        self.HN.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

        self.Sample = QComboBox()
        self.Sample.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Sample.addItem("Blood")

        self.Choosefile = QPushButton()
        self.Choosefile.setText("Choose file ...")
        self.Choosefile.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Choosefile.clicked.connect(self.addfile)

        self.Gender = QComboBox()
        self.Gender.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Gender.addItem("Male")
        self.Gender.addItem("Male")
        self.Gender.addItem("Unknown")

        self.Age = QLineEdit()
        self.Age.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Age.setPlaceholderText("Age")

        self.Province = QLineEdit()
        self.Province.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Province.setPlaceholderText("Province")

        self.Address = QLineEdit()
        self.Address.setPlaceholderText("Address")
        self.Address.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

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
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Please select a file",
                "",
                "Spectral files (*.txt)"
            )

            if not file_path:
                raise Exception("No file selected")

            # NOTE: Currently stored in Address field
            self.Address.setText(file_path)

            msg = QMessageBox(self)
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Information)
            msg.setText("File selected successfully")
            msg.setWindowTitle("Success")
            msg.exec_()

        except Exception:
            msg = QMessageBox(self)
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a valid file")
            msg.setWindowTitle("Error")
            msg.exec_()

    def addIndividual(self):

        nIndividual = self.Individual.text().strip()
        nHN = self.HN.text().strip()
        nSample = self.Sample.currentText()
        nGender = self.Gender.currentText()
        nAge = self.Age.text().strip()
        nProvince = self.Province.text().strip()
        nAddress = self.Address.text().strip()

        try:
            # Required fields (Age optional)
            if not all([nIndividual, nHN, nSample, nGender, nProvince, nAddress]):
                raise Exception("Please complete all required fields (Age is optional)")

            # Age validation
            if nAge not in ("", "-") and not nAge.isdigit():
                raise Exception("Age must be a number, '-' or empty")

            age_value = nAge if nAge else "-"

            db_path = resource_path("app/database/individualDB.db")

            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()

                c.execute(
                    "SELECT 1 FROM individualDB WHERE Individual = ?",
                    (nIndividual,)
                )
                if c.fetchone():
                    raise Exception("Individual ID already exists")

                c.execute(
                    """
                    INSERT INTO individualDB
                    (Individual, HN, Sample, Gender, Age, Province, Address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nIndividual,
                        nHN,
                        nSample,
                        nGender,
                        age_value,
                        nProvince,
                        nAddress
                    )
                )

            msg = QMessageBox(self)
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(
                "Clinical data added successfully\n"
                "[ Please proceed to Tools → Refresh ]"
            )
            msg.exec_()

            self.close()

        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.exec_()
