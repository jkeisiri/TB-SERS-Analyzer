# 🧪 TB-SERS Analyzer

**A desktop application for blood plasma analysis enables rapid and cost-effective testing using RS/SERS. It is designed to analyze RS/SERS spectra, demonstrating a high level of agreement with results obtained from IGRA. By integrating RS/SERS techniques with machine learning and convolutional neural network, along with its reporting module, it provides quick analysis with an average processing time of less than ten seconds. This makes it a potentially valuable diagnostic tool for TB screening.**

---

## 📦 Features

- 🧬 **Predict TB** from Raman/SERS spectral data
- 📊 **Patient data extraction**(`.txt`)
- 🛠️ **Data preparation** for model analysis
- 📑 **Diagnostic report generation** (`.pdf`)
- 🤖 **ML and CNN analysis** using trained model (`.h5`)

---

## 🖥️ Installation

```bash
git clone https://github.com/jkeisiri/TB-SERS-Analyzer.git
cd TB-SERS-Analyzer
pip install -r requirements.txt
python TB-SERS-Analyzer.py

---

## 🛠️ Creating Executable with PyInstaller

If you want to create an executable for the TB-SERS Analyzer project using PyInstaller, follow these steps:
```bash
pip install pyinstaller
