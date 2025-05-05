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


from PyQt5.QtCore import QCoreApplication, Qt, QMetaObject, QTimer, QRect
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QProgressBar, QVBoxLayout, QFrame, QGraphicsDropShadowEffect

class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        if SplashScreen.objectName():
            SplashScreen.setObjectName(u"SplashScreen")
        SplashScreen.resize(680, 440)
        self.centralwidget = QWidget(SplashScreen)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)

        self.dropShadowFrame = QFrame(self.centralwidget)
        self.dropShadowFrame.setObjectName(u"dropShadowFrame")
        self.dropShadowFrame.setStyleSheet(u"QFrame {"
                                           "background-color: rgb(56, 58, 89);"
                                           "color: rgb(220, 220, 220);"
                                           "border-radius: 10px;"
                                           "}")
        self.dropShadowFrame.setFrameShape(QFrame.StyledPanel)
        self.dropShadowFrame.setFrameShadow(QFrame.Raised)

        self.label1 = QLabel(self.dropShadowFrame)
        self.pixmap = QPixmap('icon/TB-SERS.png')  # Ensure this path is correct
        self.label1.setPixmap(self.pixmap)
        self.label1.setScaledContents(True)
        self.label1.setGeometry(QRect(0, 0, 661, 420))

        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(14)

        self.progressBar = QProgressBar(self.dropShadowFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(50, 380, 561, 23))
        self.progressBar.setStyleSheet(u"QProgressBar {"
                                       "background-color: rgb(98, 114, 164);"
                                       "color: rgb(200, 200, 200);"
                                       "border-style: none;"
                                       "border-radius: 10px;"
                                       "text-align: center;"
                                       "}"
                                       "QProgressBar::chunk {"
                                       "border-radius: 10px;"
                                       "background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(254, 121, 0, 255), stop:1 rgba(170, 85, 255, 255));"
                                       "}")
        self.progressBar.setValue(24)

        self.verticalLayout.addWidget(self.dropShadowFrame)
        SplashScreen.setCentralWidget(self.centralwidget)
        self.retranslateUi(SplashScreen)

        QMetaObject.connectSlotsByName(SplashScreen)

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QCoreApplication.translate("SplashScreen", u"MainWindow", None))



