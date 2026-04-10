# 🧪 TB-SERS Analyzer

**This Python-based tool is designed for blood plasma analysis, enabling rapid and cost-effective testing using Raman spectroscopy (RS) and Surface-enhanced Raman spectroscopy (SERS). It specifically analyzes RS/SERS spectra and has demonstrated a high level of agreement with results obtained from the interferon gamma release assay (IGRA). By integrating RS/SERS techniques with machine learning (ML) and a convolutional neural network (CNN), the software provides quick analysis with an average processing time of less than ten seconds. Coupled with its reporting module, this makes it a potentially valuable diagnostic tool for tuberculosis (TB) screening.**

---

## 📦 Features

- 🧬 **Predict TB** from Raman/SERS spectral data
- 📊 **Spectral data extraction**(`.txt`)
- 🛠️ **Data preparation** for model analysis
- 📑 **Diagnostic report generation** (`.pdf`)
- 🤖 **ML and CNN prediction** using trained model (`.h5`)

---

## 🖥️ Installation

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/jkeisiri/TB-SERS-Analyzer.git
cd TB-SERS-Analyzer
```

### 2. Install Dependencies

Install all necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

After installing dependencies, run the application:

```bash
python TB-SERS-Analyzer.py
```

---

## 🛠️ Creating Executable with PyInstaller

If you want to create a standalone executable for **TB-SERS Analyzer** using **PyInstaller**, follow the steps below.

### 1. Install PyInstaller

First, install **PyInstaller** if you haven’t already:

```bash
pip install pyinstaller
```

### 2. Create `.spec` File with PyInstaller

Once **PyInstaller** is installed, you can generate the `.spec` file by running:

```bash
pyinstaller --onefile --windowed TB-SERS-Analyzer.py
```

Explanation of flags:

- `--onefile` creates a single executable file
- `--windowed` suppresses the terminal window when running the app (ideal for GUI apps)

This will create a `.spec` file in the project directory.

### 3. Customize `.spec` File

If you need to bundle additional files (e.g., the trained model file `.h5`), open the generated `.spec` file and modify the `datas` section. For example:

```python
datas=[('app/database', 'app/database'),('app/resources', 'app/resources')]
```

This will ensure that the necessary files are included in the generated executable.

### 4. Build the Executable

Now, use the `.spec` file to build the executable:

```bash
pyinstaller main.spec
```

This will generate the standalone executable in the `dist/` folder.

---

### 5. Result
After the build process is complete, you will find the executable in the `dist/` folder. You can now run the application without needing Python installed on the system.

---

## 📂 Project File Structure

```
TB-SERS-Analyzer/
├── analysis/                     # Analysis workflow & Code preprocessing pipeline
├── app/
│   ├── database/
│   │   ├── CNN_TB_Model.h5       # Trained 1D-CNN model file
│   │   └── Database_Averaged.csv  # Reference database for intensity comparison
│   ├── resources/
│   │   ├── css/                  # Style sheets for UI customization
│   │   └── icon/                 # Icons and graphic assets used in the app
│   ├── ui/
│   │   ├── init.py
│   │   ├── AboutDialog.py        # Script for the "About" dialog window
│   │   ├── DeleteDialog.py       # Script for the "Delete" confirmation dialog
│   │   ├── EditDialog.py         # Script for the "Edit" data dialog
│   │   ├── InsertDialog.py       # Script for the "Insert" new data dialog
│   │   ├── MultipleDialog.py     # Script for batch/multiple sample analysis
│   │   ├── SingleDialog.py       # Script for individual sample analysis
│   │   └── ui_open_screen.py     # Script for initializing the main UI screen
│   ├── utils/                    # Utility functions and helper modules
│   │   ├── init.py
│   │   └── processing.py         # Utility functions and helper modules for data processing
│   ├── init.py
│   └── main.py                   # Main application entry point script
├── reports/                      # Folder for storing exported final reports
├── samples/                      # Folder containing test files and blind samples
├── main.spec                     # PyInstaller configuration for building the executable
├── README.md                     # Project documentation and overview
└── requirements.txt              # List of required Python libraries and dependencies
```

---

## 📈 Requirements

- Python 3.8+
- PyQt5==5.15.11
- numpy==1.24.3
- pandas==2.3.3
- scikit-learn==1.7.2
- scipy==1.15.3
- tensorflow==2.13.0
- pybaselines==1.2.1
- matplotlib==3.10.8
- fpdf2==2.8.5

Check `requirements.txt` for the full list of dependencies.

---

## 📸 Screenshot
![App Screenshot](https://github.com/user-attachments/assets/689ab44d-eea9-4b1b-83b3-5ca05eab7fa7)

---

## 📘 User Manual
After building the project using `PyInstaller`, you can run the application directly from the executable file.

📥 **Download the user manual:**


Click [TB-SERS Analyzer Manual.pdf](https://github.com/user-attachments/files/22749221/TB-SERS.Analyzer.Manual.pdf) to download the latest user manual and executable file from the **Releases** section.

---

## 🧑‍💻 Author

Jukgarin Eisiri  
M.Sc. Biomedical Science, Khon Kaen University, E-mail : jkeisiri@kkumail.com

