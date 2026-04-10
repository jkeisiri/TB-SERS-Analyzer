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
from fpdf import FPDF
from fpdf.fonts import FontFace
from tensorflow.keras.models import load_model
from scipy.stats import spearmanr
import numpy as np
import pandas as pd
import shutil
import sqlite3
from pathlib import Path
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
from PIL import Image
import time

from app.utils.preprocessing import (
    remove_cosmic_rays,
    compute_r2_score,
    qc_filter_zscore,
    baseline_correct_average
)

# =============================
# CONFIGURATION CONSTANTS
# =============================
THRESHOLD_CNN = 0.581        # Decision threshold for TB classification
TARGET_FEATURES = 1011        # Expected number of Raman features
CONF_LOW = 0.2317              # Low Confidence thresholds
CONF_MED = 0.417              # Medium Confidence thresholds 


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SingleDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SingleDialog, self).__init__(*args, **kwargs)
        self.setup_ui()
        try:
            self.modelCNN = load_model(resource_path("app/database/tb_sers_cnn_model.h5"))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Model Load Error",
                f"Cannot load diagnostic model:\n{e}"
            )
            self.close()


        
    def setup_ui(self):
        self.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
        self.setWindowTitle("Single Data")
        self.setFixedSize(550, 720)

        self.layout = QFormLayout()
        self.layout2 = QVBoxLayout()

        # Setup all UI elements
        self.setup_search_section()
        self.setup_patient_info_section()
        self.setup_report_settings_section()
        self.setup_generate_button()

        self.layout2.addLayout(self.layout)
        self.layout2.addWidget(self.QBReport, alignment=QtCore.Qt.AlignRight)
        self.setLayout(self.layout2)

    def setup_search_section(self):
        self.QBSearch = QPushButton()
        self.QBSearch.setText("Search")
        self.QBSearch.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.QBSearch.clicked.connect(self.searchsIndividual)

        self.IndividualID = QLineEdit()
        self.IndividualID.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.IndividualID.setPlaceholderText("Individual ID")

        self.layout.addRow(QLabel("Search Individual:"), self.IndividualID)
        self.layout.addRow(QLabel(" "), self.QBSearch)
        self.layout.addRow(QLabel(" "))

    def setup_patient_info_section(self):
        self.labelIn = QLabel("Patient Information:", self)
        self.labelIn.setFont(QFont("Arial", 11, QFont.Bold))

        self.Individual = QLineEdit()
        self.Individual.setPlaceholderText("Individual ID")
        self.Individual.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

        self.HN = QLineEdit()
        self.HN.setPlaceholderText("HN")
        self.HN.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

        self.Sample = QLineEdit()
        self.Sample.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Sample.setPlaceholderText("Sample")

        self.QBaddfile = QPushButton()
        self.QBaddfile.setText("Choose file ...")
        self.QBaddfile.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.QBaddfile.clicked.connect(self.addfile)

        self.Gender = QLineEdit()
        self.Gender.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Gender.setPlaceholderText("Gender")

        self.Age = QLineEdit()
        self.Age.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Age.setPlaceholderText("Age")

        self.Province = QLineEdit()
        self.Province.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.Province.setPlaceholderText("Province")

        self.Address = QLineEdit()
        self.Address.setPlaceholderText("Address")
        self.Address.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())

        self.layout.addRow(self.labelIn)
        self.layout.addRow(QLabel("Individual ID:"), self.Individual)
        self.layout.addRow(QLabel("HN:"), self.HN)
        self.layout.addRow(QLabel("Sample:"), self.Sample)
        self.layout.addRow(QLabel("File:"), self.QBaddfile)
        self.layout.addRow(QLabel("Gender:"), self.Gender)
        self.layout.addRow(QLabel("Age:"), self.Age)
        self.layout.addRow(QLabel("Province:"), self.Province)
        self.layout.addRow(QLabel("Address:"), self.Address)
        self.layout.addRow(QLabel(" "))

    def setup_report_settings_section(self):
        self.labelIn2 = QLabel("Setting Report:", self)
        self.labelIn2.setFont(QFont("Arial", 11, QFont.Bold))

        self.labelIn3 = QLabel("Standard: W: 350px * H: 270px", self)
        self.labelIn3.setFont(QFont("Arial", 7))

        self.nspectra = QLineEdit()
        self.nspectra.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.nspectra.setPlaceholderText("Number of Spectra")

        self.title = QLineEdit()
        self.title.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.title.setPlaceholderText("Title Report")

        self.QBtnlogo = QPushButton()
        self.QBtnlogo.setText("Choose file ...")
        self.QBtnlogo.setStyleSheet(Path(resource_path("app/resources/css/button.css")).read_text())
        self.QBtnlogo.clicked.connect(self.addLogo)

        self.addresslogo = QLabel("")
        self.addresslogo.setFont(QFont("Arial", 8, QFont.Bold))
        self.addresslogo.setStyleSheet("color: red;")

        self.layout.addRow(self.labelIn2)
        self.layout.addRow(QLabel("Number of Spectra :"), self.nspectra)
        self.layout.addRow(QLabel("Title :"), self.title)
        self.layout.addRow(QLabel("Logo :"), self.QBtnlogo)
        self.layout.addRow(QLabel(""), self.labelIn3)
        self.layout.addRow(QLabel(" "), self.addresslogo)

    def setup_generate_button(self):
        self.QBReport = QPushButton()
        self.QBReport.setText(" Generate Report")
        self.QBReport.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowDown')))
        self.QBReport.setFixedSize(180, 50)
        self.QBReport.setStyleSheet(Path(resource_path("app/resources/css/buttonv2.css")).read_text())
        self.QBReport.clicked.connect(self.ReportData)


    def addfile(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Please select a file",
                "",
                "Spectral files (*.txt)"
            )

            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select a file")
                return
            
            self.Address.setText(file_path)

            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Information)
            msg.setText("File selected successfully✅")
            msg.setWindowTitle("Successfully")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning: Please select a file❌")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def addLogo(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select logo image",
                "",
                "Image files (*.png *.jpg)"
            )

            if not file_path:
                return

            destination_file = resource_path("app/resources/icon/RCEIDlogo.png")

            image = Image.open(file_path)
            resized_image = image.resize((350, 270))
            resized_image.save(destination_file)
            
            self.addresslogo.setText("Logo has been set successfully!!")

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning: Please select a file❌")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
    def searchsIndividual(self):
        try:
            searchrol = self.IndividualID.text()
            if searchrol == "" :
                raise Exception("Please insert individual ID")

            db_path = resource_path("app/database/individualDB.db")
            self.conn = sqlite3.connect(db_path)
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
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Error : {e}")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def ReportData(self):

        individual = self.Individual.text()
        hn = self.HN.text()
        sample = self.Sample.text()
        gender = self.Gender.text()
        age = self.Age.text()
        province = self.Province.text()
        files = self.Address.text()
        nspec= self.nspectra.text()

        if not files or not os.path.exists(files):
            QMessageBox.warning(self, "Error", "Spectral file not found")
            return

        if not nspec.isdigit():
            QMessageBox.warning(self, "Error", "Number of spectra must be numeric")
            return
        
        def check_correlation(corr):
            if corr == 1.0:
                return "Perfect ✅"
            elif corr >= 0.8:
                return "Very strong 💪"
            elif 0.6 <= corr < 0.8:
                return "Moderate 👍"
            else:
                return "Fair to poor ⚠️"
            
        ###################################################################

        inputsp = np.genfromtxt(files, skip_header=1, skip_footer=0)

        ################### Cosmic Ray Removal ########################
        
        if(nspec == ""):
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please enter N spectra")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        else:
            num_row, num_column = inputsp.shape
            peaks = num_row // int(nspec)

        # -----------------------------
        # แยก spectra จากไฟล์
        # -----------------------------
        j, listIntensity, listPosition, dataIn, dataPo = 0, [], [], [], []

        for i in range(len(inputsp)):
            dataIn.append(inputsp[i, 3])
            dataPo.append(inputsp[i, 2])
            j += 1
            if j % peaks == 0:
                listIntensity.append(np.flip(dataIn))
                listPosition.append(np.flip(dataPo))
                dataIn.clear()
                dataPo.clear()

        features = listPosition[0]

        # -----------------------------
        # R2 ก่อน QC
        # -----------------------------
        R2_before = compute_r2_score(listIntensity, features)

        # -----------------------------
        # Cosmic ray removal 
        # -----------------------------
        despiked = [remove_cosmic_rays(y) for y in listIntensity]
        df = pd.DataFrame(despiked, columns=features)

        # -----------------------------
        # QC filtering
        # -----------------------------
        df_filtered, removed_idx = qc_filter_zscore(df)

        # -----------------------------
        # R2 หลัง QC
        # -----------------------------
        R2_after = compute_r2_score(df_filtered.to_numpy(), features)

        # -----------------------------
        # Baseline + average
        # -----------------------------
        xData = baseline_correct_average(df_filtered)


        ################### Check QC ########################
        df = pd.read_csv(resource_path("app/database/Database_Averaged.csv"))
        Xmodel = df.drop(['Groups'], axis=1)
        Xcol = Xmodel.columns.to_numpy()

        future = np.array(features)

        Xcol = Xcol.reshape(1, -1)
        future = future.reshape(1, -1)

            
        if Xcol.shape[1] == future.shape[1]:
            
            #Check Raman shift
            xIGN = df[(df['Groups'] == 0)].drop(['Groups'], axis=1)
            xIGP = df[(df['Groups'] == 1)].drop(['Groups'], axis=1)
            
            Mcolumn=Xmodel.columns.to_numpy()
            Mcolumn = Mcolumn.astype(float)
            Ncolumn=np.array(features)

            corr_feture = np.isclose(Mcolumn, Ncolumn, atol=3)
            match_percentage = np.sum(corr_feture) / len(Ncolumn)

            #Check intensity
            corr, pval = spearmanr(xIGN.mean(), xData)
            corr2, pval2 = spearmanr(xIGP.mean(), xData)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Spectral Quality Control")
            dlg.setIcon(QMessageBox.Warning) 
            dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
            text = ("<b>Pre-analysis Quality Control:</b><br>"
                "<b>Aligned Spectral Points:</b> <span style='color:black;'>" +"Reference : "+str(Xcol.shape[1])+" Predicted : "+str(future.shape[1])+ "</span><br>"
                "<b>Peak position alignment:</b> <span style='color:black;'>" + f"({match_percentage:.2f})" +" : "+check_correlation(match_percentage)+ "</span><br>"
                "<b>Spectral pattern similarity:</b> <span style='color:black;'>" + f"({abs((corr+corr2)/2):.2f})" +" : "+check_correlation((corr+corr2)/2)+"</span><br><br>"
                "<b style='color:red;'>Would you like to continue with the screening process?</b>")
            
            dlg.setText(text)
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()

            if button != QMessageBox.Yes:
                return

        else:
            #Check Point
            if abs(Xcol.shape[1] - future.shape[1]) <= 3:
                xData = xData[:TARGET_FEATURES]
                
            else:
                mask = (features >= 615) & (features <= 1725)
                df_filtered = xData[mask]
        
                if(df_filtered.shape[0]< TARGET_FEATURES):
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Spectral Quality Control")
                    dlg.setIcon(QMessageBox.Warning) 
                    dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
                    text = ("<b>Pre-analysis Quality Control:</b><br>"
                        "<b>Aligned Spectral Points:</b> <span style='color:black;'>" +"Reference : "+str(Xcol.shape[1])+" Predicted : "+str(future.shape[1])+ "</span><br>"
                        "<b>Number of points after filtering:</b> <span style='color:black;'>" + str(df_filtered.shape[0]) + "</span><br><br>"
                        "<b style='color:red;'>Cannot continue the screening process❌. Please wait for the next version!</b>")
                    dlg.setText(text)
                    dlg.setIcon(QMessageBox.Question)
                    dlg.setStandardButtons(QMessageBox.Ok)
                    dlg.exec_()
                    return
                

            #Check Raman shift
            xIGN = df[(df['Groups'] == 0)].drop(['Groups'], axis=1)
            xIGP = df[(df['Groups'] == 1)].drop(['Groups'], axis=1)

            Mcolumn=Xmodel.columns.to_numpy()
            Mcolumn = Mcolumn.astype(float)

            Ncolumn=np.array(features[:TARGET_FEATURES])

            corr_feture = np.isclose(Mcolumn, Ncolumn, atol=3)
            match_percentage = np.sum(corr_feture) / len(Ncolumn)

            #Check intensity
            corr, pval = spearmanr(xIGN.mean(), xData)
            corr2, pval2 = spearmanr(xIGP.mean(), xData)
        
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Spectral Quality Control")
            dlg.setIcon(QMessageBox.Warning) 
            dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
            text = ("<b>Pre-analysis Quality Control:</b><br>"
                "<b>Aligned Spectral Points</b> <span style='color:black;'>" +"Reference : "+str(Xcol.shape[1])+" Predicted : "+str(future.shape[1])+ "</span><br>"
                "<b>Peak position alignment:</b> <span style='color:black;'>" + f"({match_percentage:.2f})" +" : "+check_correlation(match_percentage)+ "</span><br>"
                "<b>Spectral pattern similarity:</b> <span style='color:black;'>" + f"({abs((corr+corr2)/2):.2f})" +" : "+check_correlation((corr+corr2)/2)+"</span><br><br>"
                "<b style='color:red;'>Would you like to continue with the screening process?</b>")
            
            dlg.setText(text)
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()

            if button != QMessageBox.Yes:
                return
        
        try:
            Xcol = Xmodel.columns.to_numpy()

            dfTest = pd.DataFrame([xData], columns=Xcol)
            X_test2 = dfTest.to_numpy() 

            yhatcnn, y_predcnn = 0, 0

            if X_test2.shape[1] != TARGET_FEATURES:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Warning: The number of features of X_test does not match the model!")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            
            else:
                X_testCnn = np.expand_dims(X_test2, axis=-1)
                X_testCnn = np.array(X_testCnn, dtype=np.float32)

                try:
                    y_new_pred = self.modelCNN.predict(X_testCnn, verbose=0)

                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("TensorFlow Error")
                    msg.setText(f"Prediction failed:\n{str(e)}")
                    msg.exec_()
                    return

                if y_new_pred.size > 0:
                    y_new_pred_label = (y_new_pred > THRESHOLD_CNN).astype(int).flatten()[0]
                    yhatcnn = y_new_pred_label
                    y_predcnn = y_new_pred.flatten()[0]

                
            y_pred2=y_predcnn
            yhat = yhatcnn

        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            error_text = (
                "Range of Raman shift does not match the Model\n\n"
                f"Error details: {str(e)}")
            msg.setText(error_text)
            msg.setWindowTitle("Warning:")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        ################################# Generate Report PDF ##################################
        try: 
            WIDTH = 210

            pdf = PDF()
            pdf.set_font('Arial', '', 12)

            data = [['Individual ID', 'HN', 'Sample', 'Age', 'Gender', 'Province'],
                    [individual, hn, sample, age, gender, province]]

            file_pic = ""
            Conf=0.0
            Confcolor=""

            if yhat == 0:
                prob = round((1 - y_pred2), 4)   # 0–1
                file_pic = "tblogo50.png"

                margin = abs(prob - THRESHOLD_CNN)

                # LOW (0.00 – 0.99)
                if margin <= CONF_LOW:
                    Conf = (margin / CONF_LOW) * 0.99
                    Confcolor = "orange"

                # MEDIUM (1.00 – 1.99)
                elif margin <= CONF_MED:
                    Conf = 1.0 + ((margin - CONF_LOW) / (CONF_MED - CONF_LOW)) * 0.99
                    Confcolor = "yellow"

                # HIGH (2.00 – 3.00)
                else:
                    Conf = 2.0 + ((margin - CONF_MED) / (1 - CONF_MED)) * 1.0
                    Confcolor = "green"

                Conf = round(margin, 4)

            else:
                prob = round(y_pred2, 4)   # 0–1
                file_pic = "tblogo100.png"

                margin = abs(prob - THRESHOLD_CNN)

                # LOW (0.00 – 0.99)
                if margin <= CONF_LOW:
                    Conf = (margin / CONF_LOW) * 0.99
                    Confcolor = "orange"

                # MEDIUM (1.00 – 1.99)
                elif margin <= CONF_MED:
                    Conf = 1.0 + ((margin - CONF_LOW) / (CONF_MED - CONF_LOW)) * 0.99
                    Confcolor = "yellow"

                # HIGH (2.00 – 3.00)
                else:
                    Conf = 2.0 + ((margin - CONF_MED) / (1 - CONF_MED)) * 1.0
                    Confcolor = "green"

                Conf = round(margin, 4)


            h = str(round((1 - y_pred2) * 100, 2))
            h2 = str(round((y_pred2) * 100, 2))

            result = ''
            if (yhat  == 1):
                result = 'IGRA-positive'
            else:
                result = 'IGRA-negative'

            data2 = [[ "Model", "Positive(%)", "Final interp.","Prediction tier"],['1D-CNN', h2 + ' %',result,str(Conf)]]

            TITLE1 = self.title.text()

            if(TITLE1==""):
                TITLE1 ="Tuberculosis Screening Report"
            TITLE = [TITLE1]

            pdf.add_page()

            create_letterhead(pdf, WIDTH)
            pdf.ln(8)
            create_title(TITLE, pdf)

            pdf.image(resource_path("app/resources/icon/RCEIDlogo.png"), x=10, y=5, w=55, h=0, type='', link='')
            pdf.ln(10)
            write_to_pdf2(pdf, "Patient Information : " )
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)


            grey = (234, 237, 237)
            headings_style = FontFace(fill_color=grey,emphasis="BOLD")

            with pdf.table(text_align="CENTER",headings_style=headings_style) as table:
                for data_row in data:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)
        
            pdf.ln(6)
            Pathimg = resource_path("app/resources/icon/")
            pdf.image(Pathimg + file_pic, x=160, y=110, w=40, h=0, type='', link='')
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)
            pdf.ln(6)

            write_to_pdf2(pdf, "Screening Result :")
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)

            green = (59, 188, 65)
            green2 = (0, 170, 0)
            red = (255, 0, 0)
            yellow = (255, 255, 0)
            orange = (255, 165, 0)
            style = FontFace(color=green2)
            style2 = FontFace(color=red)

            style3 = FontFace(fill_color=orange,emphasis="UNDERLINE")
            style4 = FontFace(fill_color=yellow,emphasis="UNDERLINE")
            style5 = FontFace(fill_color=green,emphasis="UNDERLINE")

            with pdf.table(width=140, col_widths=(20, 25, 25, 30), align='LEFT', text_align="CENTER",headings_style=headings_style) as table:
                for data_row in data2:
                    row = table.row()
                    for datum in data_row:
                        if str(datum) == 'IGRA-positive':
                            row.cell(datum, style=style2)
                        elif str(datum) == 'IGRA-negative':
                            row.cell(datum, style=style)
                        else:
                            if str(datum) == str(Conf) and Confcolor == 'orange':
                                row.cell('Low', style=style3)
                            elif str(datum) == str(Conf) and Confcolor == 'yellow':
                                row.cell('Medium', style=style4)
                            elif str(datum) == str(Conf) and Confcolor == 'green':
                                row.cell('High', style=style5)
                            else:
                                row.cell(datum)

            pdf.ln(3)
            pdf.set_font('Arial', '', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 12)

            re1 = ""
            reh = 0.0
            if (yhat == 1):
                re1 = " Positive."
                reh = h2
            else:
                re1 = " Negative."
                reh = h

            pdf.cell(0, 10, "The diagnostic outcome shows a likelihood of" + re1, ln=1)
            pdf.set_font('Arial', 'b', 12)
            pdf.cell(0, -10, "                                                                                         Probability = " + reh + " %", ln=1)
            pdf.set_font('Arial', '', 12)
            pdf.ln(80)
            pdf.cell(0, 8,
                 "                                                                                          ___________________________")
            pdf.ln(10)
            pdf.cell(0, 8,
                 "                                                                                          (                                                    )")
            pdf.ln(20)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 10,
                 "* Note : This preliminary report is intended for research purposes only. Caution is advised when applying it to clinical diagnosis.")
            pdf.ln(5)
            pdf.cell(0, 10,
                 "* Note : Interferon-Gamma Release Assay (IGRA) - Used as a diagnostic test for latent tuberculosis infection (LTBI).")
            pdf.ln(5)
            pdf.cell(0, 10,
                 "* Note : 1D-CNN model for LTBI screening based on IGRA results.")


            pdf.add_page()
            create_letterhead(pdf, WIDTH)
            pdf.image(resource_path("app/resources/icon/RCEIDlogo.png"), x=10, y=5, w=60, h=0, type='', link='')
            pdf.ln(40)
            write_to_pdf2(pdf, "Quality Control of Raman Spectra: ")
            pdf.ln(5)
            data3 = [["Comparison", "Number of Features", "Number of Spectra", "R-squared"],  
                    ['Before', str(peaks), nspec, str(round((R2_before) * 100, 2))+" %"],
                    ['After', "1011", str(int(nspec)-len(removed_idx)), str(round((R2_after) * 100, 2))+" %"]]
            pdf.set_font('Arial', '', 11)

            with pdf.table(text_align="CENTER",headings_style=headings_style) as table:
                for data_row in data3:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)

            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 10,
                 "* Note: 'Before' represents the original data, whereas 'After' denotes the data after preprocessing.")
            pdf.ln(20)

            write_to_pdf2(pdf, "Meaning of prediction tier: ")
            pdf.ln(5)
            pdf.set_font('Arial', '', 11)
            data3 = [["Margin range", "Interpretation", "Meaning", "Color"],
                 ['0.4177 - 1.0000', "High Tier",
                  "A high prediction tier indicates that the model output is well separated from the decision boundary, reflecting strong model certainty", "green"],
                 ['0.2317 - 0.4176', "Medium Tier", "A medium prediction tier indicates that the model output is moderately separated from the decision boundary, reflecting intermediate model certainty", "yellow"],
                 ['0.0000 - 0.2316', "Low Tier", "A low prediction tier indicates that the model output is close to the decision boundary, reflecting limited model certainty and requiring cautious interpretation", "orange"]]
        
            green = (59, 188, 65)
            yellow = (255, 255, 0)
            orange = (255, 165, 0)

            style = FontFace(fill_color=green)
            style2 = FontFace(fill_color=yellow)
            style3 = FontFace(fill_color=orange)
            with pdf.table(text_align="CENTER", col_widths=(25, 15, 50, 10),headings_style=headings_style) as table:
                for data_row in data3:
                    row = table.row()
                    for datum in data_row:
                        if str(datum) == 'High Tier':
                            row.cell('High Tier', style=style)
                        elif str(datum) == 'Medium Tier':
                            row.cell('Medium Tier', style=style2)
                        elif str(datum) == 'Low Tier':
                            row.cell('Low Tier', style=style3)
                        else:
                            row.cell(datum)

            report_dir = resource_path("reports")
            os.makedirs(report_dir, exist_ok=True)
            pdf.output(os.path.join(report_dir, "ReportSingleData.pdf"))

        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            error_text = (
                "There is an issue with the report generation process\n\n"
                f"Error details: {str(e)}")
            msg.setText(error_text)
            msg.setWindowTitle("Warning:")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return  

        try:
            filename, _ = QFileDialog.getSaveFileName(
            self,
                "Save report",
                "",
                "PDF files (*.pdf)"
            )

            if not filename:
                return

            shutil.copyfile(
                resource_path("reports/ReportSingleData.pdf"),
                filename
            )

            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Information)
            msg.setText("Diagnostic Report PDF has been successfully generated✅")
            msg.setWindowTitle("Successfully")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(resource_path("app/resources/icon/RCEID.png")))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning: The report has not been saved!❌")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

class PDF(FPDF):
    def __init__(self):
        super().__init__()

    def header(self):
        self.set_font('Arial', '', 10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)    
        self.cell(0, 8, 'Research Use Only', 0, 0, 'L')
        self.cell(0, 8, f'Page {self.page_no()} of ' + '{nb}', 0, 0, 'R')


def create_letterhead(pdf, WIDTH):
    pdf.image(resource_path("app/resources/icon/head.jpg"), 0, 0, WIDTH)


def create_title(title, pdf):
    pdf.set_font('Arial', 'b', 30)
    pdf.ln(30)
    pdf.write(5, title[0])
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(r=128, g=128, b=128)
    timeis = time.localtime()
    a = time.strftime('%Y %B %d, %H:%M:%S', timeis)
    pdf.cell(0, 6,'Date : '+a)
    pdf.ln(10)

def write_to_pdf(pdf, words):
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 0, words)

def write_to_pdf2(pdf, words):
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font('Arial', 'b', 12)
    pdf.cell(0, 0, words)

