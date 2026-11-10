# Automated Materials Characterization & Spectroscopic Analysis Hub

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg)](https://python.org)
[![LabPlot Compatible](https://img.shields.io/badge/LabPlot-Compatible-orange.svg)](https://labplot.kde.org)

An open-source, local-first scientific analysis and visualization engine designed to replace proprietary suites (e.g., OriginLab) with Python 3.12, SciPy, lmfit, OpenCV, Matplotlib, and Streamlit.

🔗 **Live Cloud Application:** [https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/](https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/)

Equipped with **Universal Multi-Format Ingestion** (Excel, OriginLab exports, CSV, TSV, DAT, TXT, ASC, DPT, PRN, XY, and Micrographs), **Physics-Based Technique Auto-Detection & Header Cleaning**, and **Zero-Setup Portability**.

---

## ⚡ 1-Click Portability: Copy-Paste to Any Computer

The entire repository uses **relative paths** and isolated environment scripts. You can copy-paste the entire `Plotting_Chemistry` folder to any drive (`C:`, `D:`, USB drive, etc.) or computer (Windows 10/11, PowerShell 5.1/7):

| 1-Click Launcher | Description |
|---|---|
| **`run_gui.bat`** | **Double-click to start.** Auto-checks dependencies, activates `.venv` (or creates/installs if missing), and opens the interactive multi-technique GUI in your browser. |
| **`run_xps_studio.bat`** | **Dedicated XPS Intelligence Studio.** Launches the specialized XPS platform with domain models for MOFs, Solar Perovskites, and PAN Nanofibers. |
| **`setup_environment.bat`** | Optional: sets up an isolated Python virtual environment (`.venv`) and installs all scientific packages cleanly. |
| **`run_all_scripts.bat`** | Double-click to execute all 5 analytical modules headlessly and generate all publication graphics and LabPlot matrices. |
| **`sync_github.bat`** / **`.ps1`** | Synchronize local modifications with your GitHub repository in 1 click. |

---

## 🔄 Synchronizing with GitHub

You can connect and push this repository to GitHub at any time:

### Quick Method (Automated Assistant)
1. Double-click **`sync_github.bat`** (or run `.\sync_github.ps1` in PowerShell).
2. If running for the first time, paste your GitHub repository URL (e.g., `https://github.com/username/Plotting_Chemistry.git`).
3. The script automatically stages changes, commits with timestamped metadata, and syncs to `main`.

### Manual Git Commands
```powershell
# 1. Link your remote repository (first time only)
git remote add origin https://github.com/<your-username>/Plotting_Chemistry.git
git branch -M main

# 2. Stage and commit
git add -A
git commit -m "Update materials characterization models and data"

# 3. Push to GitHub
git push -u origin main
```

> **Note on `.gitignore`:** The repository is configured to exclude large raw analytical binary dumps (`.raw`, `.spc`, `.dm3`, `.bcf`) and heavy generated outputs (`*.png`, `*.pdf`, `*.svg`, `*.dat`), while keeping the output folder structure intact via `.gitkeep`.

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
Plotting_Chemistry/
├── run_gui.bat                # 1-Click desktop launcher (auto-installs if needed)
├── run_all_scripts.bat        # 1-Click batch processor for all scripts
├── setup_environment.bat      # 1-Click isolated venv setup
├── sync_github.bat            # 1-Click GitHub sync assistant (Windows Batch)
├── sync_github.ps1            # 1-Click GitHub sync assistant (PowerShell)
├── app.py                     # Streamlit Interactive Desktop GUI Hub
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

---

## 👤 Author & Ownership

- **Lead Developer & Maintainer:** **Dr. Deler Langenberg**
- **GitHub:** [@delerla](https://github.com/delerla)
- **Repository:** [https://github.com/delerla/Plotting_Chemistry](https://github.com/delerla/Plotting_Chemistry)
- **Live Web Hub:** [https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/](https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/)
- **Contact:** [delerla@yahoo.de](mailto:delerla@yahoo.de)

### 📖 Citation

If you use this software in your research, thesis, or academic publications, please cite:

```bibtex
@software{langenberg_plotting_chemistry_2026,
  author = {Dr. Deler Langenberg},
  title = {Automated Materials Characterization & Spectroscopic Analysis Hub},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/delerla/Plotting_Chemistry}
}
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details (Copyright © 2026 Dr. Deler Langenberg).
All publication exports (PNG, SVG, PDF, ASCII .DAT) generated by this platform are entirely royalty-free for academic and commercial research.
