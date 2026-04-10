# 🧪 TB-SERS Analyzer

**This Python-based tool is designed for blood plasma analysis, enabling rapid and cost-effective testing using Raman spectroscopy (RS) and Surface-enhanced Raman spectroscopy (SERS). It specifically analyzes RS/SERS spectra and has demonstrated a high level of agreement with results obtained from the interferon gamma release assay (IGRA). By integrating RS/SERS techniques with machine learning (ML) and a convolutional neural network (CNN), the software provides quick analysis—with an average processing time of less than ten seconds. Coupled with its reporting module, this makes it a potentially valuable diagnostic tool for tuberculosis (TB) screening.**

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
pyinstaller TB-SERS-Analyzer.spec
```

This will generate the standalone executable in the `dist/` folder.

---

### 5. Result
After the build process is complete, you will find the executable in the `dist/` folder. You can now run the application without needing Python installed on the system.

---

## 📂 Project File Structure

```
TB-SERS-Analyzer/
├── TB-SERS-Analyzer.py          # Main application script
├── MultipleDialog.py            # Script for displaying the "Multiple-Sample" dialog in the application
├── SingleDialog.py              # Script for displaying the "Single-Sample" dialog in the application
├── AboutDialog.py               # Script for displaying the "About" dialog in the application
├── DeleteDialog.py              # Script for displaying the "Delete" dialog in the application
├── EditDialog.py                # Script for displaying the "Edit" dialog in the application
├── InsertDialog.py              # Script for displaying the "Insert" dialog in the application
├── ui_open_screen.py            # Script for initializing and opening the main user interface screen
├── database/
│   └── CNN_TB_Model.h5          # Trained 1D-CNN model file
│   └── scaler.pkl               # Used for scaling data to match the training data
│   └── wavenumber.txt           # Used for comparing wave or Raman shift values
│   └── Database_Averaged.csv    # Database for comparing with reference data and new blind samples (intensity)
├── css/                         # CSS files for styling
├── icon/                        # Icons used in the application
├── generate/                    # Templates or files for report generation
├── requirements.txt             # Python dependencies
├── dist/                        # Executable files (after building with PyInstaller)
├── build/                       # Temporary build files
└── TB-SERS-Analyzer.spec        # PyInstaller spec file
├── blind sample/
│   └── Blinded #1 on SERS.txt   # Blind samples #1 for testing
│   └── Blinded #2 on SERS.txt   # Blind samples #2 for testing
│   └── Blinded #3 on SERS.txt   # Blind samples #3 for testing
│   └── Blinded #4 on SERS.txt   # Blind samples #4 for testing
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

