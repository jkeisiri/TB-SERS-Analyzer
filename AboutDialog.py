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


from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("Contact us")
        self.setWindowIcon(QIcon('icon/RCEID.png'))
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
