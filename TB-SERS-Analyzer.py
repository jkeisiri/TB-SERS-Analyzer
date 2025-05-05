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
import sys
from tkinter import Tk
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import *


from ui_open_screen import Ui_SplashScreen
from DeleteDialog import DeleteDialog
from AboutDialog import AboutDialog
from EditDialog import EditDialog
from InsertDialog import InsertDialog
from SingleDialog import SingleDialog
from MultipleDialog import MultipleDialog

counter = 0

Tk().withdraw()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QIcon('icon/RCEID.png'))

        self.conn = sqlite3.connect("database/individualDB.db")
        self.c = self.conn.cursor()
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS individualDB(roll INTEGER PRIMARY KEY AUTOINCREMENT ,Individual TEXT,HN TEXT,Sample TEXT,Gender TEXT,Age INTEGER,Province TEXT,Address TEXT)")
        self.c.close()

        self.setWindowTitle("TB-SERS Analyzer")
        self.setMinimumSize(1600, 850)

        self.tableWidget = QTableWidget()
        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.setHorizontalHeaderLabels(
            ("Individual ID", "HN", "Sample", "Gender", "Age", "Province", "Input file"))

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(55, 50))
        self.addToolBar(toolbar)

        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        self.setStyleSheet("""
                    QToolBar {
                        background: #eee;
                        padding: 0px;
                        border: 0px;
                        spacing: 3px;

                    }
                    QMenuBar { 
                        font-size: 10pt; 
                    }
                   QToolBar QToolButton {
                        background: #eee;
                        margin: 0px;
                        padding: 5px;
                        border-radius: 5px;
                    }
                   QToolBar QToolButton:hover {
                        background: #bbb;
                    }
                   QMenu {
                        background: #eee;
                   }
                   QMenu::item {
                        background: transparent;
                        padding: 5px 10px;
                        margin: 0px;
                        
                   }
                    QMenu::item:selected {
                        background: #bbb;
                    }
                    """)

        file_menu = self.menuBar().addMenu("&File")
        tools_menu = self.menuBar().addMenu("&Tools")
        about_menu = self.menuBar().addMenu("&About")

        btn_ac_Single = QAction(QIcon("icon/m1.png"), "Single Data", self) # search icon
        btn_ac_Single.triggered.connect(self.reportone)
        btn_ac_Single.setStatusTip("Single Data")
        toolbar.addAction(btn_ac_Single)

        btn_ac_Multiple = QAction(QIcon("icon/m2.png"), "Multiple Data", self)
        btn_ac_Multiple.triggered.connect(self.reportall)
        btn_ac_Multiple.setStatusTip("Multiple Data")
        toolbar.addAction(btn_ac_Multiple)

        Single_action = QAction(QIcon("icon/m1.png"), "Single Data", self)
        Single_action.setShortcut('Ctrl+S')
        Single_action.setStatusTip("Single Data")
        Single_action.triggered.connect(self.reportone)
        file_menu.addAction(Single_action)

        Multiple_action = QAction(QIcon("icon/m2.png"), "Multiple Data", self)
        Multiple_action.setShortcut('Ctrl+M')
        Multiple_action.setStatusTip("Multiple Data")
        Multiple_action.triggered.connect(self.reportall)
        file_menu.addSeparator()
        file_menu.addAction(Multiple_action)

        add_action = QAction(QIcon("icon/add1.png"), "&Insert Data", self)
        add_action.setShortcut('Ctrl+I')
        add_action.setStatusTip("Insert Data")
        add_action.triggered.connect(self.insert)
        tools_menu.addAction(add_action)

        edit_action = QAction(QIcon("icon/s1.png"), "Edit Data", self)
        edit_action.setShortcut('Ctrl+E')
        edit_action.setStatusTip("Edit Data")

        edit_action.triggered.connect(self.edit)
        tools_menu.addAction(edit_action)

        tools_menu.addSeparator()
        Delete_action = QAction(QIcon("icon/d1.png"), "Delete Data", self)
        Delete_action.setShortcut('Ctrl+D')
        Delete_action.setStatusTip("Delete Data")
        Delete_action.triggered.connect(self.delete)
        tools_menu.addAction(Delete_action)
        tools_menu.addSeparator()

        btn_ac_refresh = QAction(QIcon("icon/r3.png"), "Refresh Database", self)  # refresh icon
        btn_ac_refresh.setShortcut('Ctrl+R')
        btn_ac_refresh.triggered.connect(self.loaddata)
        btn_ac_refresh.setStatusTip("Refresh Database")
        tools_menu.addAction(btn_ac_refresh)

        about_action = QAction(QIcon("icon/i1.png"), "Contact us", self)  # info icon
        about_action.triggered.connect(self.about)
        about_action.setStatusTip("Contact us")
        about_menu.addAction(about_action)


    def loaddata(self):
        listco = []
        self.connection = sqlite3.connect("database/individualDB.db")
        query = "SELECT * FROM individualDB"
        result = self.connection.execute(query)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if (column_number > 0):
                    self.tableWidget.setItem(row_number, column_number - 1, QTableWidgetItem(str(data)))
                else:
                    listco.append(data)
        self.connection.close()

    def handlePaintRequest(self, printer):
        document = QTextDocument()
        cursor = QTextCursor(document)
        model = self.table.model()
        table = cursor.insertTable(
            model.rowCount(), model.columnCount())
        for row in range(table.rows()):
            for column in range(table.columns()):
                cursor.insertText(model.item(row, column).text())
                cursor.movePosition(QTextCursor.NextCell)
        document.print_(printer)

    def insert(self):
        dlg = InsertDialog()
        dlg.exec_()

    def delete(self):
        dlg = DeleteDialog()
        dlg.exec_()

    def reportone(self):
        dlg = SingleDialog()
        dlg.exec_()

    def edit(self):
        dlg = EditDialog()
        dlg.exec_()

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def reportall(self):
        dlg = MultipleDialog()
        dlg.exec_()


class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up UI
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # REMOVE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        # QTIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)

        # Initialize counter
        self.counter = 0  # Make sure the counter is initialized
        self.timer.start(35)  # TIMER IN MILLISECONDS

        self.show()

    def progress(self):
        self.ui.progressBar.setValue(self.counter)

        if self.counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()
            self.main.loaddata()  # Assuming 'loaddata' is a method of MainWindow
            self.close()  # Close the splash screen

        self.counter += 1

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    login = SplashScreen()
    sys.exit(app.exec_())
