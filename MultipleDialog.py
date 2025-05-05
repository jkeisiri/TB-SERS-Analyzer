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

import peakutils
from tensorflow.keras.models import load_model
from scipy.stats import spearmanr
import joblib
from sklearn.decomposition import PCA
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import shutil
import sqlite3
import math
from sklearn.metrics import r2_score
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
from fpdf import FPDF

from sklearn.covariance import MinCovDet
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import *
from fpdf.fonts import FontFace

Tk().withdraw()

class MultipleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MultipleDialog, self).__init__(parent)
        self.setFixedSize(1050, 580)
        self.setWindowTitle("Multiple Data")
        self.setWindowIcon(QIcon('icon/RCEID.png'))

        self.tableWidget = QTableWidget()

        self.QBtn = QPushButton()
        self.QBtn.setText("Select .. file")
        self.QBtn.setStyleSheet(Path('css/button.css').read_text())

        self.QBtn2 = QPushButton()
        self.QBtn2.setText(" Generate Report")
        self.QBtn2.setFixedSize(180, 50)
        self.QBtn2.setIcon(self.style().standardIcon(getattr(QStyle,'SP_ArrowDown')))
        self.QBtn2.setStyleSheet(Path('css/buttonv2.css').read_text())
        self.QBtn2.clicked.connect(self.reportData)

        self.layout = QVBoxLayout()
        self.h_layout = QFormLayout()

        self.title12 = QLineEdit()
        self.title12.setStyleSheet(Path('css/button.css').read_text())
        self.title12.setPlaceholderText("Title Report")


        self.QBtnlogo = QPushButton()
        self.QBtnlogo.setText("Choose file ...")
        self.QBtnlogo.setStyleSheet(Path('css/button.css').read_text())



        self.labelIn22 = QLabel("Setting Report:", self)
        self.labelIn22.setFont(QFont("Arial", 11, QFont.Bold))

        self.nspectra = QLineEdit()
        self.nspectra.setStyleSheet(Path('css/button.css').read_text())
        self.nspectra.setPlaceholderText("Number of Spectra")

        self.h_layout.addRow(QLabel(" "))
        self.h_layout.addRow(self.labelIn22)
        self.h_layout.addRow(QLabel("Number of Spectra :"), self.nspectra)
        self.h_layout.addRow(QLabel("Title:"), self.title12)

        self.layout.addWidget(self.tableWidget)
        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.QBtn2,alignment=QtCore.Qt.AlignRight)
        self.setLayout(self.layout)

        self.conn = sqlite3.connect("database/individualDB.db")
        self.c = self.conn.cursor()
        result = self.c.execute("SELECT * from individualDB")
        row1 = result.fetchall()

        self.conn.commit()
        self.c.close()
        self.conn.close()

        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(len(row1))
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 120)
        self.tableWidget.setColumnWidth(4, 80)
        self.tableWidget.setColumnWidth(5, 120)
        self.tableWidget.setColumnWidth(6, 300)
        self.tableWidget.setColumnWidth(7, 60)


        for k in range(len(row1)):
            self.tableWidget.setHorizontalHeaderLabels(
                ("Individual ID", "HN", "Sample", "Gender", "Age", "Province", "Input file", "Select"))

            data=row1[k]
            self.checkBox_c =  QTableWidgetItem()
            self.checkBox_c.setCheckState(Qt.CheckState.Checked)
            self.checkBox_c.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.verticalHeader().setVisible(False)

            self.tableWidget.setItem(k, 0,QTableWidgetItem(str(data[1])))
            self.tableWidget.setItem(k, 1, QTableWidgetItem(str(data[2])))
            self.tableWidget.setItem(k, 2, QTableWidgetItem(str(data[3])))
            self.tableWidget.setItem(k, 3, QTableWidgetItem(str(data[4])))
            self.tableWidget.setItem(k, 4, QTableWidgetItem(str(data[5])))
            self.tableWidget.setItem(k, 5, QTableWidgetItem(str(data[6])))
            self.tableWidget.setItem(k, 6, QTableWidgetItem(str(data[7])))
            self.tableWidget.setItem(k, 7, QTableWidgetItem(self.checkBox_c))

        self.tableWidget.horizontalHeader().setStretchLastSection(True)


    def reportData(self):

        def modified_z_score(ys):
            ysb = np.diff(ys)  # Differentiated intensity values
            median_y = np.median(ysb)  # Median of the intensity values
            median_absolute_deviation_y = np.median(
                [np.abs(y - median_y) for y in ysb])  # median_absolute_deviation of the differentiated intensity values
            modified_z_scores = [0.6745 * (y - median_y) / median_absolute_deviation_y for y in
                                 ysb]  # median_absolute_deviationmodified z scores
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
        

        data11 = [['Individual ID', 'HN', 'Sample', 'Age', 'Gender', 'Province']]
        data22 = [["Individual ID","Sample", "Probability(%)", "Final interp.", "Confidence value"]]
        data33 = [["Model", "Negative(%)", "Positive(%)", "Final interp.", "Confidence value"]]

        checked_list, file_list, datapatien, Conflist, Confcolorlist, listhn, listinten, listposit, R2before, R2ater, npeak, nspecbefore, nspecafter = [], [], [], [], [], [], [], [], [], [], [], [], []

        for i in range(self.tableWidget.rowCount()):
            if(self.tableWidget.item(i, 7).checkState()== Qt.CheckState.Checked):
                datafile=self.tableWidget.item(i, 6).text()
                data1=self.tableWidget.item(i, 0).text()
                data2 = self.tableWidget.item(i, 1).text()
                data3 = self.tableWidget.item(i, 2).text()
                data4 = self.tableWidget.item(i, 3).text()
                data5 = self.tableWidget.item(i, 4).text()
                data6 = self.tableWidget.item(i, 5).text()

                dataone = [data1, data2, data3, data4, data5, data6]

                listhn.append(data1)
                datapatien.append(data1)
                data11.append(dataone)
                file_list.append(datafile)
                checked_list.append([i, 7])

            else:
                pass

        for k in range(len(file_list)):
            inputsp = np.genfromtxt(file_list[k], skip_header=1, skip_footer=0)
            nspec = self.nspectra.text()
            
            if (nspec == ""):
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Warning: Please enter the number of spectra❌")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            else:
                if (len(file_list)>10):
                    msg = QMessageBox()
                    msg.setWindowIcon(QIcon('icon/RCEID.png'))
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("Warning: Please select no more than 10 files❌")
                    msg.setWindowTitle("Warning")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    return
                
                else:
                    num_row, num_column = inputsp.shape
                    peaks = num_row // int(nspec)
                    npeak.append(peaks)
                    nspecbefore.append(int(nspec))


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
            R2before.append(R2_Score)

            ################### cosmic ray remove ########################
            despiked_spectrum2 = []
            for i in range(int(nspec)):
                despiked_spectrum = fixer(listIntensity[i])
                despiked_spectrum2.append(despiked_spectrum)


            df = pd.DataFrame(despiked_spectrum2, columns=features)

            ################### outlier remove ########################
            x = df.loc[:, features].values

            x = StandardScaler().fit_transform(x)

            pca = PCA(n_components=2)
            f_pca = pca.fit_transform(x)

            robust_cov = MinCovDet().fit(f_pca[:, :2])  # fit a Minimum Covariance Determinant (MCD) robust estimator to data
            m = robust_cov.mahalanobis(f_pca[:, :2]) 
            zscore = stats.zscore(m)

            x = []
            Xdel = []
            for i in range(len(zscore)):
                if abs(zscore[i]) < 1.645:  # check z score for a 90% confidence interval
                    x.append(abs(zscore[i]))
                else:
                    Xdel.append(i)

            df.drop(Xdel, inplace=True)
            nspecafter.append(int(nspec)-len(Xdel))

            ################### R2_Score After ########################
            dfAfter_array = df.to_numpy()
            R2_Score2=compute_r2_score(dfAfter_array,features)
            R2ater.append(R2_Score2)

            ################### Average & Baseline ########################
            dfBaseline= df[np.array(df.columns)]
            Baseline  = peakutils.baseline(dfBaseline.mean(),deg=3) #Baseline subtraction
            datafinal = dfBaseline.mean() - Baseline 
            xData = np.array(datafinal.tolist())

            listinten.append(datafinal.tolist())
            listposit.append(features)

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
                    "Warning: There is an issue in the model prediction process❌\n\n"
                    f"Error details: {str(e)}")
                msg.setText(error_text)
                msg.setWindowTitle("Warning:")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            file_pic = ""
            Conf = 0.0
            Confcolor = ""

            try:
                if yhat == 0:
                    prob = round((1-y_pred2) * 100, 2)
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

                result=''
                prob=0.0

                if(yhat == 1):
                    result = 'IGRA-positive'
                    prob=h2
                else:
                    result = 'IGRA-negative'
                    prob=h

                dataone = [datapatien[k], data11[k+1][2], prob, result, str(Conf)]
                datatwo = ['1D-CNN', h, h2, result, str(Conf)]
                data33.append(datatwo)
                data22.append(dataone)
                Conflist.append(Conf)
                Confcolorlist.append(Confcolor)

            except Exception as e:
                msg = QMessageBox()
                msg.setWindowIcon(QIcon('icon/RCEID.png'))
                msg.setIcon(QMessageBox.Warning)
                error_text = (
                    "Warning: There is an issue in the confidence value calculation process❌\n\n"
                    f"Error details: {str(e)}")
                msg.setText(error_text)
                msg.setWindowTitle("Warning:")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        ############################## Generate Report ################################
        try:
            WIDTH = 210

            pdf = PDF()

            TITLE1 = self.title12.text()

            if (TITLE1 == ""):
                TITLE1 = "Tuberculosis Diagnostic Report"
            TITLE = [TITLE1]

            pdf.add_page()
            create_letterhead(pdf, WIDTH)
            pdf.ln(8)
            create_title2(TITLE, pdf)
            pdf.image('icon/RCEIDlogo.png', x=10, y=5, w=55, h=0, type='', link='')
            pdf.ln(5)

            write_to_pdf2(pdf, "Diagnostic Conclusion :")
            pdf.ln(5)
            pdf.set_font('Arial', '', 12)

            green = (59, 188, 65)
            green2 = (0, 170, 0)
            red = (255, 0, 0)
            yellow = (255, 255, 0)
            orange = (255, 165, 0)
            grey = (234, 237, 237)

            style = FontFace(color=green2)
            style2 = FontFace(color=red)

            style3 = FontFace(fill_color=orange,emphasis="UNDERLINE")
            style4 = FontFace(fill_color=yellow,emphasis="UNDERLINE")
            style5 = FontFace(fill_color=green,emphasis="UNDERLINE")

            headings_style = FontFace(fill_color=grey, emphasis="BOLD")

            with pdf.table(text_align="CENTER",headings_style=headings_style) as table:
                for row_index, data_row in enumerate(data22):
                    row = table.row()
                    for datum in data_row:
                        if str(datum) == 'IGRA-positive':
                            row.cell(datum, style=style2)
                        elif str(datum) == 'IGRA-negative':
                            row.cell(datum, style=style)
                        else:
                            if str(datum) == str(Conflist[row_index-1]) and Confcolorlist[row_index-1] == 'orange':
                                row.cell(datum, style=style3)
                            elif str(datum) == str(Conflist[row_index-1]) and Confcolorlist[row_index-1] == 'yellow':
                                row.cell(datum, style=style4)
                            elif str(datum) == str(Conflist[row_index-1]) and Confcolorlist[row_index-1] == 'green':
                                row.cell(datum, style=style5)
                            else:
                                row.cell(datum)
  
            pdf.ln(15)
            write_to_pdf2(pdf, "Meaning of confidence value: ")
            pdf.ln(5)
            pdf.set_font('Arial', '', 11)
            data3 = [["Range", "Interpretation", "Meaning", "Color"],
                 ['2.00 - 3.00', "High Confidence",
                  "A high confidence level indicates that the model demonstrates strong certainty in its diagnostic prediction",
                  "green"],
                 ['1.00 - 1.99', "Medium Confidence",
                  "A medium confidence level indicates that the model possesses a moderate degree of certainty in its diagnostic prediction",
                  "yellow"],
                 ['0.00 - 0.99', "Low Confidence",
                  "A low confidence level indicates that the model has limited certainty in its diagnostic prediction",
                  "orange"]]
        
            green = (59, 188, 65)
            yellow = (255, 255, 0)
            orange = (255, 165, 0)

            style = FontFace(fill_color=green)
            style2 = FontFace(fill_color=yellow)
            style3 = FontFace(fill_color=orange)

            with pdf.table(text_align="CENTER", col_widths=(15, 25, 50, 10), headings_style=headings_style) as table:
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

            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 10,"* Note : This preliminary report is intended for research purposes only. Caution is advised when applying it to clinical diagnosis.")
            
            for i in range(len(data11)-1):

                data = [['Individual ID', 'HN', 'Sample', 'Age', 'Gender', 'Province'],
                data11[i+1]]
            
                data2 = [[ "Model", "Positive(%)", "Final interp.","Confidence value"],
                     [data33[i+1][0],data33[i+1][2],data33[i+1][3],data33[i+1][4]]]
            
                Confcolor=Confcolorlist[i]
                Conf=Conflist[i]

                if (data33[i+1][3]  == 'IGRA-positive'):
                    file_pic = "tblogo100.png"
                else:
                    file_pic = "tblogo50.png"  
           
                pdf.add_page()
                create_letterhead(pdf, WIDTH)
                pdf.ln(5)
                create_title2(["Individual Case Report"], pdf)
                pdf.image('icon/RCEIDlogo.png', x=10, y=5, w=55, h=0, type='', link='')
                pdf.ln(10)

                write_to_pdf2(pdf, 'Patient Information :')
                pdf.ln(5)

                pdf.set_font('Arial', '', 12)
                grey = (234, 237, 237)
                headings_style = FontFace(fill_color=grey, emphasis="BOLD")

                with pdf.table(text_align="CENTER", headings_style=headings_style) as table:
                    for data_row in data:
                        row = table.row()
                        for datum in data_row:
                            row.cell(datum)
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

                re1 = ""
                reh = 0.0

                if (data33[i+1][3]  == 'IGRA-positive'):
                    re1 = " Positive."
                    reh = data33[i+1][2]
                else:
                    re1 = " Negative."
                    reh = data33[i+1][1]

                pdf.cell(0, 10, "The diagnostic outcome shows a likelihood of" + re1, ln=1)
                pdf.set_font('Arial', 'b', 12)
                pdf.cell(0, -10, "                                                                                         Probability = " + reh + " %", ln=1)
            
                pdf.ln(75)
                write_to_pdf2(pdf, "Quality Control of Raman Spectra: ")
                pdf.ln(5)

   
                data3 = [["Comparison", "Number of Features", "Number of Spectra", "R-squared"],
                 ['Before', str(npeak[i]), str(nspecbefore[i]) , str(round((R2before[i]) * 100, 2)) + " %"],
                 ['After', "1011", str(nspecafter[i]),str(round((R2ater[i]) * 100, 2)) + " %"]]
            
                pdf.set_font('Arial', '', 12)
                with pdf.table(text_align="CENTER", headings_style=headings_style) as table:
                    for data_row in data3:
                        row = table.row()
                        for datum in data_row:
                            row.cell(datum)

                pdf.set_font('Arial', '', 9)
                pdf.cell(0, 10,
                 "* Note: 'Before' represents the original data, whereas 'After' denotes the data after preprocessing.")  
            

            pdf.output('generate/ReportMultipleData.pdf', 'F')

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

            source = "generate/ReportMultipleData.pdf"

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
        pdf = FPDF(format='letter', unit='in')
        self.alias_nb_pages()

    def header(self):
        self.set_font('Arial', '', 12)


    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)    
        self.cell(0, 8, 'Research Use Only', 0, 0, 'L')
        self.cell(0, 8, f'Page {self.page_no()} of ' + '{nb}', 0, 0, 'R')


def create_letterhead(pdf, WIDTH):
    pdf.image("icon/head.jpg", 0, 0, WIDTH)


def create_title2(title, pdf):
    import time

    pdf.set_font('Arial', 'b', 30)
    pdf.ln(30)
    pdf.write(5, title[0])
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(r=128, g=128, b=128)
    
    timeis = time.localtime()
    a = time.strftime('%d %B %Y, %H:%M:%S', timeis)
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