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

import os
import peakutils
from fpdf import FPDF
from fpdf.fonts import FontFace
from tensorflow.keras.models import load_model
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import shutil
import sqlite3
from pathlib import Path
from tkinter import Tk, filedialog
from tkinter.filedialog import asksaveasfilename
import math
from sklearn.metrics import r2_score
from sklearn.covariance import MinCovDet
import joblib
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
import time

Tk().withdraw()

class SingleDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SingleDialog, self).__init__(*args, **kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowIcon(QIcon('icon/RCEID.png'))
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
        self.QBSearch.setStyleSheet(Path('css/button.css').read_text())
        self.QBSearch.clicked.connect(self.searchsIndividual)

        self.IndividualID = QLineEdit()
        self.IndividualID.setStyleSheet(Path('css/button.css').read_text())
        self.IndividualID.setPlaceholderText("Individual ID")

        self.layout.addRow(QLabel("Search Individual:"), self.IndividualID)
        self.layout.addRow(QLabel(" "), self.QBSearch)
        self.layout.addRow(QLabel(" "))

    def setup_patient_info_section(self):
        self.labelIn = QLabel("Patient Information:", self)
        self.labelIn.setFont(QFont("Arial", 11, QFont.Bold))

        self.Individual = QLineEdit()
        self.Individual.setPlaceholderText("Individual ID")
        self.Individual.setStyleSheet(Path('css/button.css').read_text())

        self.HN = QLineEdit()
        self.HN.setPlaceholderText("HN")
        self.HN.setStyleSheet(Path('css/button.css').read_text())

        self.Sample = QLineEdit()
        self.Sample.setStyleSheet(Path('css/button.css').read_text())
        self.Sample.setPlaceholderText("Sample")

        self.QBaddfile = QPushButton()
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
        self.nspectra.setStyleSheet(Path('css/button.css').read_text())
        self.nspectra.setPlaceholderText("Number of Spectra")

        self.title = QLineEdit()
        self.title.setStyleSheet(Path('css/button.css').read_text())
        self.title.setPlaceholderText("Title Report")

        self.QBtnlogo = QPushButton()
        self.QBtnlogo.setText("Choose file ...")
        self.QBtnlogo.setStyleSheet(Path('css/button.css').read_text())
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
        self.QBReport.setStyleSheet(Path('css/buttonv2.css').read_text())
        self.QBReport.clicked.connect(self.ReportData)


    def addfile(self):
        try:
            files = filedialog.askopenfilename(title="Please select a file",
                                   filetypes=[('Text files', '*.txt')])

            if (files == ''):
                raise Exception("Please select a file")
            else:
                self.Address.setText(files)

            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Information)
            msg.setText("File selected successfully✅")
            msg.setWindowTitle("Successfully")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning: Please select a file❌")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def addLogo(self):
        try:
            from PIL import Image

            files = filedialog.askopenfilename(title="Please select a file",filetypes=(('jpeg files', '*.jpg'), ('png files', '*.png')))
            current_dir = os.path.dirname(os.path.abspath(__file__))
            destination_file = current_dir + '\icon\RCEIDlogo.png'

            new_size = (350, 270)
            image = Image.open(files)
            resized_image = image.resize(new_size)
            resized_image.save(destination_file)

            self.addresslogo.setText("Logo has been set successfully!!")

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
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
            msg.setText(f"Error : {e}")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def ReportData(self):
        start_time = time.time()

        individual = self.Individual.text()
        hn = self.HN.text()
        sample = self.Sample.text()
        gender = self.Gender.text()
        age = self.Age.text()
        province = self.Province.text()
        files = self.Address.text()
        nspec= self.nspectra.text()

        def modified_z_score(ys):
            ysb = np.diff(ys)  # Differentiated intensity values
            median_y = np.median(ysb)  # Median of the intensity values
            median_absolute_deviation_y = np.median(
                [np.abs(y - median_y) for y in ysb])  #median_absolute_deviation of the differentiated intensity values
            modified_z_scores = [0.6745 * (y - median_y) / median_absolute_deviation_y for y in ysb]  # median_absolute_deviationmodified z scores
            return modified_z_scores

        def fixer(y):
            threshold = 8
            desired_ratio = 1.15
            spikes = abs(np.array(modified_z_score(y))) > threshold
            y_out = y.copy()

            for i in np.arange(len(spikes)):
                if spikes[i] != 0:
                    y_out[i] = y[i] / desired_ratio
  
            return y_out
        
        def check_correlation(corr):
            if corr >= 0.9:
                return "Excellent ✅"
            elif 0.8 <= corr < 0.9:
                return "Good 👍"
            elif 0.7 <= corr < 0.8:
                return "Moderate ⚠️"
            else:
                return "Weak ❌"
            
        def compute_r2_score(listIntensity, future):
            dfch = pd.DataFrame(listIntensity, columns=np.flip(future))
            X = dfch.to_numpy()
            list_r2, sum = [], 0

            for i in range(len(X)):
                for j in range(len(X)):
                    if (i != j):
                        x1 = np.array(dfch.loc[i:i])
                        y1 = np.array(dfch.loc[j:j])
                        x1_norm = (x1 - np.min(x1)) / (np.max(x1) - np.min(x1))
                        y1_norm = (y1 - np.min(y1)) / (np.max(y1) - np.min(y1))

                        R2 = r2_score(x1_norm[0], y1_norm[0])
                        R2 = math.fabs(R2)
                        if (R2 > 1):
                            R2 = 1
                        sum += R2
                        list_r2.append(R2)

            return sum / len(list_r2)
        
        ###################################################################

        inputsp = np.genfromtxt(files, skip_header=1, skip_footer=0)

        ################### Cosmic Ray Removal ########################
        
        if(nspec == ""):
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please enter N spectra")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        else:
            num_row, num_column = inputsp.shape
            peaks = num_row // int(nspec)

        j, listIntensity, listPosition, dataIn, dataPo  = 0, [], [], [], []

        for i in range(len(inputsp)):
            dataIn.append(inputsp[:, 3][i])
            dataPo.append(inputsp[:, 2][i])
            j += 1
            if (j % peaks == 0):
                listIntensity.append(np.flip(dataIn[0:peaks]))
                listPosition.append(np.flip(dataPo[0:peaks]))
                dataIn.clear()
                dataPo.clear()

        features = []
        for i in range(peaks):
            features.append(listPosition[0][i])

        ################### R2_Score before ########################
        R2_Score=compute_r2_score(listIntensity,features)

        despiked_spectrum2 = []

        for i in range(int(nspec)):
            despiked_spectrum = fixer(listIntensity[i])
            despiked_spectrum2.append(despiked_spectrum)

        df = pd.DataFrame(despiked_spectrum2, columns=features)

        x = df.loc[:, features].values

        x = StandardScaler().fit_transform(x)

        pca = PCA(n_components=2)
        f_pca = pca.fit_transform(x)

        robust_cov = MinCovDet().fit(f_pca[:, :2])  # fit a Minimum Covariance Determinant (MCD) robust estimator to data
        m = robust_cov.mahalanobis(f_pca[:, :2])
        zscore = stats.zscore(m)

        Z_score,Xdel = [], []

        for i in range(len(zscore)):
            if abs(zscore[i]) < 1.645:  # check z score for a 90% confidence interval
                Z_score.append(abs(zscore[i]))
            else:
                Xdel.append(i)

        df.drop(Xdel, inplace=True)

        ################### R2_Score After ########################
        dfAfter_array = df.to_numpy()
        R2_Score2=compute_r2_score(dfAfter_array,features)

        ################### Average & Baseline ########################
        dfBaseline= df[np.array(df.columns)]
        Baseline  = peakutils.baseline(dfBaseline.mean(),deg=3) #Baseline subtraction
        datafinal = dfBaseline.mean() - Baseline 
        xData = np.array(datafinal.tolist())

        ################### Check QC ########################
        df = pd.read_csv('database/Database_Averaged.csv')
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
            dlg.setWindowTitle("Quality Control of Raman Shift and Intensity")
            dlg.setIcon(QMessageBox.Warning) 
            dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
            text = ("<b>Warning:</b> Spearman's correlation coefficient of the model<br>"
                "<b>Matching Points:</b> <span style='color:black;'>" +"Model : "+str(Xcol.shape[1])+" Blind : "+str(future.shape[1])+ "</span><br>"
                "<b>Raman shift:</b> <span style='color:black;'>" + f"{match_percentage:.4f}" +" : "+check_correlation(match_percentage)+ "</span><br>"
                "<b>Intensity:</b> <span style='color:black;'>" + f"{abs((corr+corr2)/2):.4f}" +" : "+check_correlation((corr+corr2)/2)+"</span><br><br>"
                "<b style='color:red;'>Would you like to continue with the diagnostic process?</b>")
            
            dlg.setText(text)
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()

            if button != QMessageBox.Yes:
                return

        else:
            target_size = 1011

            #Check Point
            if abs(Xcol.shape[1] - future.shape[1]) <= 3:
                xData = xData[:target_size]
                
            else:
                df_filtered = datafinal.reset_index()
                df_filtered = df_filtered[(df_filtered["index"] >= 615) & (df_filtered["index"] <= 1725)]
                
                if(df_filtered.shape[0]< target_size):
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Quality Control of Raman Shift and Intensity")
                    dlg.setIcon(QMessageBox.Warning) 
                    dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
                    text = ("<b>Warning:</b> Spearman's correlation coefficient of the model<br>"
                        "<b>Matching Points:</b> <span style='color:black;'>" +"Model : "+str(Xcol.shape[1])+" Blind : "+str(future.shape[1])+ "</span><br>"
                        "<b>Number of points after filtering:</b> <span style='color:black;'>" + str(df_filtered.shape[0]) + "</span><br><br>"
                        "<b style='color:red;'>Cannot continue the diagnostic process❌. Please wait for the next version!</b>")
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

            Ncolumn=np.array(features[:target_size])

            corr_feture = np.isclose(Mcolumn, Ncolumn, atol=3)
            match_percentage = np.sum(corr_feture) / len(Ncolumn)

            #Check intensity
            corr, pval = spearmanr(xIGN.mean(), xData)
            corr2, pval2 = spearmanr(xIGP.mean(), xData)
        
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Quality Control of Raman Shift and Intensity")
            dlg.setIcon(QMessageBox.Warning) 
            dlg.setStyleSheet("QLabel{font-size: 15px; color: style='color:black;';} QPushButton{font-size: 13px;}")
            text = ("<b>Warning:</b> Spearman's correlation coefficient of the model<br>"
                "<b>Matching Points:</b> <span style='color:black;'>" +"Model : "+str(Xcol.shape[1])+" Blind : "+str(future.shape[1])+ "</span><br>"
                "<b>Raman shift:</b> <span style='color:black;'>" + f"{match_percentage:.4f}" +" : "+check_correlation(match_percentage)+ "</span><br>"
                "<b>Intensity:</b> <span style='color:black;'>" + f"{abs((corr+corr2)/2):.4f}" +" : "+check_correlation((corr+corr2)/2)+"</span><br><br>"
                "<b style='color:red;'>Would you like to continue with the diagnostic process?</b>")
            
            dlg.setText(text)
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()

            if button != QMessageBox.Yes:
                return
        
        try:
            Xcol = Xmodel.columns.to_numpy()
            threshold = 0.5146

            dfTest = pd.DataFrame([xData], columns=Xcol)
            X_test2 = dfTest.to_numpy()  #convert to NumPy Array

            #load Scaler
            scaler = joblib.load('database/scaler.pkl')

            yhatcnn, y_predcnn = 0, 0

            #Check if the Shape matches the Trained Model.
            if X_test2.shape[1] != scaler.n_features_in_:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Warning: The number of features of X_test does not match the model!")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            
            else:
                X_testCnn = scaler.transform(X_test2)  #Transform data

                #Convert to a format suitable for CNN
                X_testCnn = np.expand_dims(X_testCnn, axis=-1)
                X_testCnn = np.array(X_testCnn, dtype=np.float32)

                #load model CNN
                modelCNN = load_model('database/CNN_TB_Model.h5')

                try:
                    y_new_pred = modelCNN.predict(X_testCnn, verbose=0)

                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("TensorFlow Error")
                    msg.setText(f"Prediction failed:\n{str(e)}")
                    msg.exec_()
                    return

                if y_new_pred.size > 0:
                    y_new_pred_label = (y_new_pred > threshold).astype(int).flatten()[0]
                    yhatcnn = y_new_pred_label
                    y_predcnn = y_new_pred.flatten()[0]

                
            y_pred2=y_predcnn
            yhat = yhatcnn

        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
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
                prob = round((1-y_pred2) * 100, 2)
                file_pic = "tblogo50.png"
                prob = prob/100

                if prob  <= 0.365:
                    Conf = round((prob / 0.365) * 0.99, 2)
                    Confcolor = "orange"

                elif prob  <= 0.631:
                    Conf = round(1 + (((prob - 0.365) / (0.631 - 0.365)) * 0.99), 2)
                    Confcolor = "yellow"

                else:
                    Conf = round(2 + ((prob - 0.8012) / 0.199), 2)
                    Confcolor = "green"

            else:
                prob = round((y_pred2) * 100, 2)
                file_pic = "tblogo100.png"
                prob = prob/100

                if prob  <= 0.365:
                    Conf = round((prob / 0.365) * 0.99, 2)
                    Confcolor = "orange"

                elif prob  <= 0.631:
                    Conf = round(1 + (((prob - 0.365) / (0.631 - 0.365)) * 0.99), 2)
                    Confcolor = "yellow"

                else:
                    Conf = round(2 + ((prob - 0.8012) / 0.199), 2)
                    Confcolor = "green"


            h = str(round((1 - y_pred2) * 100, 2))
            h2 = str(round((y_pred2) * 100, 2))

            result = ''
            if (yhat  == 1):
                result = 'IGRA-positive'
            else:
                result = 'IGRA-negative'

            data2 = [[ "Model", "Positive(%)", "Final interp.","Confidence value"],['1D-CNN', h2 + ' %',result,str(Conf)]]

            TITLE1 = self.title.text()

            if(TITLE1==""):
                TITLE1 ="Tuberculosis Diagnostic Report"
            TITLE = [TITLE1]

            pdf.add_page()

            create_letterhead(pdf, WIDTH)
            pdf.ln(8)
            create_title(TITLE, pdf)

            pdf.image('icon/RCEIDlogo.png', x=10, y=5, w=55, h=0, type='', link='')
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

            pdf.image('icon/' + file_pic, x=160, y=110, w=40, h=0, type='', link='')
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)
            pdf.ln(6)

            write_to_pdf2(pdf, "Diagnostic Conclusion :")
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
                                row.cell(datum, style=style3)
                            elif str(datum) == str(Conf) and Confcolor == 'yellow':
                                row.cell(datum, style=style4)
                            elif str(datum) == str(Conf) and Confcolor == 'green':
                                row.cell(datum, style=style5)
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
                 "* Note : 1D-CNN model applied for LTBI prediction based on IGRA results.")


            pdf.add_page()
            create_letterhead(pdf, WIDTH)
            pdf.image('icon/RCEIDlogo.png', x=10, y=5, w=60, h=0, type='', link='')
            pdf.ln(40)
            write_to_pdf2(pdf, "Quality Control of Raman Spectra: ")
            pdf.ln(5)
            data3 = [["Comparison", "Number of Features", "Number of Spectra", "R-squared"],
                    ['Before', str(peaks), nspec, str(round((R2_Score) * 100, 2))+" %"],
                    ['After', "1011", str(int(nspec)-len(Xdel)), str(round((R2_Score2) * 100, 2))+" %"]]
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

            write_to_pdf2(pdf, "Meaning of confidence value: ")
            pdf.ln(5)
            pdf.set_font('Arial', '', 11)
            data3 = [["Range", "Interpretation", "Meaning", "Color"],
                 ['2.00 - 3.00', "High Confidence",
                  "A high confidence level indicates that the model demonstrates strong certainty in its diagnostic prediction", "green"],
                 ['1.00 - 1.99', "Medium Confidence", "A medium confidence level indicates that the model possesses a moderate degree of certainty in its diagnostic prediction", "yellow"],
                 ['0.00 - 0.99', "Low Confidence", "A low confidence level indicates that the model has limited certainty in its diagnostic prediction", "orange"]]
        
            green = (59, 188, 65)
            yellow = (255, 255, 0)
            orange = (255, 165, 0)

            style = FontFace(fill_color=green)
            style2 = FontFace(fill_color=yellow)
            style3 = FontFace(fill_color=orange)
            with pdf.table(text_align="CENTER", col_widths=(15, 25, 50, 10),headings_style=headings_style) as table:
                for data_row in data3:
                    row = table.row()
                    for datum in data_row:
                        if str(datum) == 'High Confidence':
                            row.cell(datum, style=style)
                        elif str(datum) == 'Medium Confidence':
                            row.cell(datum, style=style2)
                        elif str(datum) == 'Low Confidence':
                            row.cell(datum, style=style3)
                        else:
                            row.cell(datum)

            pdf.output('generate/ReportSingleData.pdf', 'F')

        except Exception as e:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
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
            filename = asksaveasfilename(filetypes=(("File PDF", "*.pdf"), ("All Files", "*.*")),
                                         defaultextension='.pdf', title="Save file")
            
            source = "generate/ReportSingleData.pdf"
            shutil.copyfile(source, filename)

            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
            msg.setIcon(QMessageBox.Information)
            msg.setText("Diagnostic Report PDF has been successfully generated✅")
            msg.setWindowTitle("Successfully")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon('icon/RCEID.png'))
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
    pdf.image("icon/head.jpg", 0, 0, WIDTH)


def create_title(title, pdf):
    pdf.set_font('Arial', 'b', 30)
    pdf.ln(30)
    pdf.write(5, title[0])
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(r=128, g=128, b=128)
    import time
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



