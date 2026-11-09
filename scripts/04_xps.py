"""
04_xps.py - Automated XPS High-Resolution Shirley Deconvolution and LabPlot ASCII Engine
"""

import sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import matplotlib.pyplot as plt

from modules.export_utils import save_publication_figure, export_labplot_ascii
from modules.file_parser import load_smart_file
from modules.xps_module import deconvolve_xps, generate_benchmark_xps_data
DEFAULT_DATA_FILE = BASE_DIR / "data" / "xps" / "c1s_high_res.csv"
OUTPUT_DIR = BASE_DIR / "output" / "xps"


def main():
    print("=" * 70)
    print(" [4/5] Running XPS High-Resolution Core-Level Protocol")
    print("=" * 70)
    
    target_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    
    if target_file.exists():
        print(f"[INFO] Ingesting file via Smart Parser: {target_file}")
        df, _, meta = load_smart_file(target_file)
        if df is None or df.empty:
            print("[WARN] Parsing produced empty dataframe. Generating benchmark C 1s spectrum...")
            df = generate_benchmark_xps_data()
        else:
            print(f"[INFO] Successfully cleaned {meta['rows']} rows from {meta['format']}. Identified: {meta['detected_technique']}")
    else:
        print("[WARN] Data file missing. Generating benchmark C 1s spectrum...")
        df = generate_benchmark_xps_data()
        DEFAULT_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DEFAULT_DATA_FILE, index=False)

    fig, summary, labplot_df = deconvolve_xps(
        df,
        c1s_calibration=True,
        expected_ref_be=284.8
    )

    print(f"\n[ANALYSIS] Fit Diagnostics:")
    print(f"  * Binding Energy Shift Applied: {summary['be_shift_applied_eV']:+.3f} eV")
    print(f"  * Chi-square (chi^2): {summary['chi_square']}")
    print(f"  * Reduced Chi-square (redchi): {summary['redchi']}")
    print(f"  * Coefficient of Determination (R^2): {summary['r_squared']}")

    print("\n[QUANTIFICATION] Chemical Species Atomic Concentrations (at%):")
    for row in summary['quantification_table']:
        print(f"  * {row['Component']:<12}: Peak = {row['Binding_Energy_eV']} eV | FWHM = {row['FWHM_eV']} eV | Area = {row['Integrated_Area']:<9} | {row['Atomic_Concentration_pct']}%")

    # Export publication graphics (600 DPI PNG, SVG, PDF)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / "XPS_C1s_Deconvolution_Publication"
    save_publication_figure(fig, out_base, dpi=600, formats=('png', 'svg', 'pdf'))

    # Export LabPlot ASCII matrix
    ascii_out = OUTPUT_DIR / "XPS_C1s_Deconvolution_Matrix.dat"
    units = {
        'Binding_Energy_eV': 'eV',
        'Experimental_CPS': 'Counts/s',
        'Shirley_Baseline': 'Counts/s',
        'Envelope_Fit': 'Counts/s',
        'Residuals': 'Counts/s'
    }
    for col in labplot_df.columns:
        if col.startswith('Voigt_'):
            units[col] = 'Counts/s'
            
    export_labplot_ascii(
        labplot_df,
        filepath=ascii_out,
        title="High-Resolution C 1s XPS Spectrum Shirley Deconvolution",
        units=units,
        comments=[
            f"Referenced to C 1s sp3 at 284.8 eV (BE shift: {summary['be_shift_applied_eV']} eV)",
            f"Voigt model deconvolution via lmfit (R2 = {summary['r_squared']})"
        ]
    )

    plt.close(fig)
    print("\n[COMPLETED] XPS deconvolution analysis finished successfully.\n")


if __name__ == '__main__':
    main()
