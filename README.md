# Automated Materials Characterization & Spectroscopic Analysis Hub

An open-source, local-first scientific analysis and visualization engine designed to replace proprietary suites (e.g., OriginLab) with Python 3.12, SciPy, lmfit, OpenCV, Matplotlib, and Streamlit.

Equipped with **Universal Multi-Format Ingestion** (Excel, OriginLab exports, CSV, TSV, DAT, TXT, ASC, DPT, PRN, XY, and Micrographs) and **Physics-Based Technique Auto-Detection & Header Cleaning**.

---

## 🔬 Supported Characterization Techniques

1. **FTIR Spectroscopy (`scripts/01_ftir.py`)**
   - Transmittance (%T) vs Wavenumber (4000–400 cm⁻¹).
   - Savitzky-Golay filtering, peak-valley vibrational band detection, baseline stacking with discrete vertical offsets.
2. **XRD Crystallography (`scripts/02_xrd.py`)**
   - Cu Kα (λ = 1.5406 Å) diffraction stacking.
   - Non-linear Lorentzian deconvolution & Scherrer crystallite sizing:
     $$D = \frac{K \cdot \lambda}{\beta \cdot \cos\theta}$$
3. **UV-Vis & Photodegradation Kinetics (`scripts/03_uv_vis_kinetics.py`)**
   - Time-resolved absorbance monitoring (200–800 nm).
   - Automatic $\lambda_{\max}$ identification, $C_t / C_0 = A_t / A_0$.
   - Pseudo-First-Order ($\ln(C_0 / C_t) = k_{\mathrm{app}} \cdot t$) & Pseudo-Second-Order ($1/C_t - 1/C_0 = k_2 \cdot t$) kinetic regression modeling.
4. **XPS Core-Level Deconvolution (`scripts/04_xps.py`)**
   - Iterative Shirley inelastic scattering background subtraction.
   - Adventitious carbon C 1s charge calibration (284.8 eV).
   - Non-linear multi-component Voigt profile fitting via `lmfit` (C–C/C–H, C–O, C=O, O–C=O), residual diagnostics ($\chi^2$, redchi, $R^2$), and relative atomic concentration percentages (at%).
5. **SEM & EDX Microanalysis (`scripts/05_sem_edx.py`)**
   - **SEM:** Micrograph contrast enhancement, Otsu binarization, morphological filtering, automated particle segmentation, diameter distributions, and percentiles (D10, D50, D90).
   - **EDX:** Automated characteristic emission line identification (Kα/Lα lines), Bremsstrahlung consideration, and semi-quantitative elemental wt% and at% quantification.

---

## ⚡ Universal Smart Ingestion & Header Cleaning

The hub features an intelligent pre-processing engine (`modules/file_parser.py`) that handles real-world instrument outputs:

- **Broad File Format Support:**
  - Modern & Legacy Excel: `.xlsx`, `.xls`
  - OriginLab Worksheets & ASCII tables: `.dat`, `.txt`, `.csv`, `.tsv`, `.ascii`, `.asc`, `.dpt` (Bruker/PerkinElmer), `.prn`, `.xy`
  - Micrograph Images: `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`
- **Smart Multi-Line Header Cleaning:**
  - Detects and strips instrument metadata, comments, operator notes, and non-numeric leading lines.
  - Recognizes OriginLab table layouts with Short Names, Long Names, Units, and Comments, synthesizing clean, publication-ready column labels (e.g. `Two-Theta (Degree)`, `Wavenumber (cm-1)`).
  - Handles international decimal formats (commas vs dots, e.g. `35,42` -> `35.42`).
- **Physics-Based Technique Auto-Detection:**
  - Analyzes X-axis domains and physical signatures to automatically classify whether uploaded data corresponds to FTIR (cm⁻¹), XRD (2θ), UV-Vis (nm), XPS (eV), or EDX (keV), and automatically routes micrographs to SEM particle analysis.

---

## 📁 Repository Structure

```text
D:\Plotting_Chemistry\
├── app.py                     # Streamlit Interactive Desktop GUI Hub with Smart Ingestion
├── requirements.txt           # Python dependency specification
├── README.md                  # System overview and protocol documentation
├── docs\
│   └── METHODS.md             # Theoretical protocol specifications
├── data\                      # Benchmark and experimental datasets
│   ├── ftir\
│   ├── xrd\
│   ├── uv_vis\
│   ├── degradation\
│   ├── xps\
│   └── sem_edx\
├── modules\                   # Core analytical modules
│   ├── file_parser.py         # Smart file ingestion, header cleaning & classifier
│   ├── export_utils.py        # 600 DPI, SVG, PDF, and LabPlot ASCII matrix formatter
│   ├── ftir_module.py         # FTIR engine
│   ├── xrd_module.py          # XRD engine
│   ├── uv_vis_module.py       # UV-Vis & kinetics engine
│   ├── xps_module.py          # XPS Shirley & Voigt engine
│   └── sem_edx_module.py      # SEM particle sizing & EDX quantification
├── scripts\                   # Headless execution scripts
│   ├── 01_ftir.py
│   ├── 02_xrd.py
│   ├── 03_uv_vis_kinetics.py
│   ├── 04_xps.py
│   └── 05_sem_edx.py
└── output\                    # Exported publication figures & LabPlot matrices
    ├── ftir\
    ├── xrd\
    ├── uv_vis\
    ├── xps\
    └── sem_edx\
```

---

## 🚀 Quickstart & Usage

### 1. Launch Interactive Desktop GUI
```powershell
streamlit run app.py
```
Open `http://localhost:8501`. 
- **Global Dropzone:** Drag and drop any Excel file, Origin export, or instrument ASCII file in the sidebar. The system will inspect the headers, clean the table, classify the analytical technique, and offer a 1-click switch button to jump directly to the matched module with your data loaded.
- **Export Center:** Download 600 DPI PNG, SVG, PDF, or LabPlot ASCII matrices with 1 click.

### 2. Headless Script Execution
All scripts support default benchmark files or custom file inputs (including Excel and OriginLab exports):

```powershell
# Using default benchmark files:
python scripts\01_ftir.py
python scripts\02_xrd.py
python scripts\03_uv_vis_kinetics.py
python scripts\04_xps.py
python scripts\05_sem_edx.py

# Using custom files (CSV, Excel, Origin exports, DAT, TXT):
python scripts\01_ftir.py "path\to\my_ftir_origin.xlsx"
python scripts\02_xrd.py "path\to\experimental_xrd.dat"
```

---

## 📊 LabPlot Interoperability Standard

All scripts and GUI exports produce ASCII data tables (`.dat`) equipped with standardized metadata headers recognized by **LabPlot**, **OriginLab**, and **QtiPlot**:

```text
# ==============================================================================
# LabPlot ASCII Matrix / Data Table
# Hub: Automated Materials Characterization & Spectroscopic Analysis Hub
# Title: <Dataset Title>
# Export Date: YYYY-MM-DD HH:MM:SS
# ------------------------------------------------------------------------------
# Column Definitions:
# Column 1: <Name> [<Units>]
# Column 2: <Name> [<Units>]
# ==============================================================================
```
These matrices load directly into LabPlot worksheets via `File -> Import -> Import File...` without requiring manual column mapping.
