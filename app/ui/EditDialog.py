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

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QFormLayout,
    QVBoxLayout, QMessageBox, QFileDialog, QStyle
)
from PyQt5 import QtCore


# ----------------------------
# Resource path (PyInstaller safe)
# ----------------------------
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ----------------------------
# Edit Dialog
# ----------------------------
class EditDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(EditDialog, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
        self.setWindowTitle("Edit Patient Information")
        self.setFixedSize(550, 530)

        self.db_path = resource_path("app/database/individualDB.db")

        # ---------------- Layout ----------------
        self.layout = QFormLayout()
        self.layout2 = QVBoxLayout()

        # ---------------- Widgets ----------------
        self.IndividualID = QLineEdit()
        self.IndividualID.setPlaceholderText("Individual ID (Search)")
        self.IndividualID.setStyleSheet(Path(
            resource_path("app/resources/css/button.css")
        ).read_text())

        self.QBSearch = QPushButton("Search")
        self.QBSearch.setStyleSheet(Path(
            resource_path("app/resources/css/button.css")
        ).read_text())
        self.QBSearch.clicked.connect(self.searchIndividual)

        self.labelIn = QLabel("Patient Information:")
        self.labelIn.setFont(QFont("Arial", 11, QFont.Bold))

        self.Individual = QLineEdit()
        self.HN = QLineEdit()
        self.Sample = QLineEdit()
        self.Gender = QLineEdit()
        self.Age = QLineEdit()
        self.Province = QLineEdit()
        self.Address = QLineEdit()

        for w in [
            self.Individual, self.HN, self.Sample,
            self.Gender, self.Age, self.Province, self.Address
        ]:
            w.setStyleSheet(Path(
                resource_path("app/resources/css/button.css")
            ).read_text())

        self.Individual.setPlaceholderText("Individual ID")
        self.HN.setPlaceholderText("HN")
        self.Sample.setPlaceholderText("Sample")
        self.Gender.setPlaceholderText("Gender")
        self.Age.setPlaceholderText("Age")
        self.Province.setPlaceholderText("Province")
        self.Address.setPlaceholderText("Address / File path")

        self.QBaddfile = QPushButton("Choose file ...")
        self.QBaddfile.setStyleSheet(Path(
            resource_path("app/resources/css/button.css")
        ).read_text())
        self.QBaddfile.clicked.connect(self.addFile)

        self.QBReport = QPushButton("Edit Information")
        self.QBReport.setFixedSize(180, 50)
        self.QBReport.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton)
        )
        self.QBReport.setStyleSheet(Path(
            resource_path("app/resources/css/buttonv2.css")
        ).read_text())
        self.QBReport.clicked.connect(self.editIndividual)

        # ---------------- Assemble layout ----------------
        self.layout.addRow(QLabel("Search Individual:"), self.IndividualID)
        self.layout.addRow(QLabel(" "), self.QBSearch)
        self.layout.addRow(QLabel(" "))

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

    # ----------------------------
    # Select file (PyQt only)
    # ----------------------------
    def addFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",
            "Data Files (*.txt)"
        )

        if file_path:
            self.Address.setText(file_path)
            QMessageBox.information(self, "Success", "File selected successfully")

    # ----------------------------
    # Search Individual
    # ----------------------------
    def searchIndividual(self):
        try:
            search_id = self.IndividualID.text().strip()
            if not search_id:
                raise ValueError("Please insert Individual ID")

            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT * FROM individualDB WHERE Individual = ?",
                    (search_id,)
                )
                row = c.fetchone()

            if row is None:
                raise ValueError("No data found for the given Individual")

            self.Individual.setText(row[1])
            self.HN.setText(row[2])
            self.Sample.setText(row[3])
            self.Gender.setText(row[4])
            self.Age.setText(str(row[5]))
            self.Province.setText(row[6])
            self.Address.setText(row[7])

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    # ----------------------------
    # Edit Individual
    # ----------------------------
    def editIndividual(self):
        try:
            nIndividual = self.Individual.text().strip()
            nHN = self.HN.text().strip()
            nSample = self.Sample.text().strip()
            nGender = self.Gender.text().strip()
            nAge = self.Age.text().strip()
            nProvince = self.Province.text().strip()
            nAddress = self.Address.text().strip()

            # Required fields (Age is optional)
            if not all([
                nIndividual, nHN, nSample,
                nGender, nProvince, nAddress
            ]):
                raise ValueError("Please insert required clinical data")

            # Validate Age
            if nAge not in ("", "-") and not nAge.isdigit():
                raise ValueError("Age must be a number, '-' or empty")

            # Validate Age
            if nAge not in ("", "-") and not nAge.isdigit():
                raise ValueError("Age must be a number, '-' or empty")

            # Save Age as-is
            age_value = nAge if nAge != "" else "-"

            
            reply = QMessageBox.question(
                self,
                "Confirm Edit",
                "Are you sure you want to update this patient information?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    """
                    UPDATE individualDB
                    SET HN = ?, Sample = ?, Gender = ?, Age = ?, Province = ?, Address = ?
                    WHERE Individual = ?
                    """,
                    (nHN, nSample, nGender, age_value, nProvince, nAddress, nIndividual)
                )

            QMessageBox.information(
                self,
                "Success",
                "Clinical data updated successfully\n[Please proceed to Tools → Refresh]"
            )
            self.close()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
