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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DeleteDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(DeleteDialog, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
        self.setWindowTitle("Delete Patient Information")
        self.setFixedWidth(450)
        self.setFixedHeight(120)

        self.QBtn = QPushButton()
        self.QBtn.setText("  Delete")
        self.QBtn.setFixedSize(200, 50)
        self.QBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxCritical')))
        self.QBtn.setStyleSheet(Path(resource_path("app/resources/css/buttonv2.css")).read_text())
        self.QBtn.clicked.connect(self.delete_individual)

        self.layout = QFormLayout()
        self.layout2 = QVBoxLayout()

        self.deleteinput = QLineEdit()
        self.deleteinput.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.deleteinput.setPlaceholderText("Individual ID")

        self.layout.addRow(QLabel("Individual ID:"),self.deleteinput)

        self.layout2.addLayout(self.layout)
        self.layout2.addWidget(self.QBtn ,alignment=QtCore.Qt.AlignRight)
        self.setLayout(self.layout2)

    def delete_individual(self):
        try:
            delrol = self.deleteinput.text().strip()
            if not delrol:
                raise ValueError("Please insert Individual ID")

            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete Individual ID: {delrol}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            db_path = resource_path("app/database/individualDB.db")

            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT 1 FROM individualDB WHERE Individual = ?", (delrol,))
                if c.fetchone() is None:
                    raise ValueError("No data found for the given Individual")

                c.execute("DELETE FROM individualDB WHERE Individual = ?", (delrol,))

            QMessageBox.information(
                self,
                "Successfully",
                "Deleted from individual database successfully.\n"
                "Please proceed to Tools → Refresh."
            )
            self.close()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                str(e)
            )


