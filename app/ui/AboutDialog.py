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

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("Contact us")
        self.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
        self.setFixedWidth(700)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        title = QLabel("Contact us")
        font = QFont("Arial", 18, QFont.Bold)
        title.setFont(font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        fontn = QFont("Arial", 10)

        developer_label = QLabel("Developed by: Jukgarin Eisiri, Email: jkeisiri@kkumail.com")
        developer_label.setFont(fontn)
        developer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(developer_label)

        correspondence_label = QLabel("Correspondence: Kiatichai Faksri, Email: kiatichai@kku.ac.th")
        correspondence_label.setFont(fontn)
        correspondence_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(correspondence_label)


        separator = QLabel("─────────────────────────")
        separator.setAlignment(Qt.AlignCenter)
        layout.addWidget(separator)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
