"""
03_uv_vis_kinetics.py - Automated UV-Vis Spectra & Photodegradation Kinetics Engine
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

from modules.export_utils import save_publication_figure, export_labplot_ascii, export_originlab_ascii
from modules.file_parser import load_smart_file
from modules.uv_vis_module import process_and_plot_uv_vis, generate_benchmark_uv_vis_data
DEFAULT_SPECTRA_FILE = BASE_DIR / "data" / "uv_vis" / "uv_vis_spectra.csv"
OUTPUT_DIR = BASE_DIR / "output" / "uv_vis"


def main():
    print("=" * 70)
    print(" [3/5] Running UV-Vis & Photodegradation Kinetics Protocol")
    print("=" * 70)
    
    target_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SPECTRA_FILE
    
    if target_file.exists():
        print(f"[INFO] Ingesting file via Smart Parser: {target_file}")
        df_spectra, _, meta = load_smart_file(target_file)
        if df_spectra is None or df_spectra.empty:
            print("[WARN] Parsing produced empty dataframe. Generating benchmark data...")
            df_spectra, _ = generate_benchmark_uv_vis_data()
        else:
            print(f"[INFO] Successfully cleaned {meta['rows']} rows from {meta['format']}. Identified: {meta['detected_technique']}")
    else:
        print("[WARN] Spectra file missing. Generating benchmark data...")
        df_spectra, _ = generate_benchmark_uv_vis_data()
        DEFAULT_SPECTRA_FILE.parent.mkdir(parents=True, exist_ok=True)
        df_spectra.to_csv(DEFAULT_SPECTRA_FILE, index=False)

    fig, axes, metrics, labplot_spectra, labplot_kinetics = process_and_plot_uv_vis(
        df_spectra,
        lambda_target=554.0,
        initial_conc=10.0
    )

    print("\n[ANALYSIS] Photodegradation Kinetics Summary:")
    print(f"  * Monitored Wavelength (lambda_max): {metrics['lambda_max_nm']} nm")
    print(f"  * Pseudo-First-Order Rate Constant (k_app): {metrics['k_pseudo_first_order_min-1']:.4f} min^-1 (R^2 = {metrics['R2_pseudo_first_order']:.4f})")
    print(f"  * Pseudo-Second-Order Rate Constant (k_2): {metrics['k_pseudo_second_order']:.5f} L/(mg*min) (R^2 = {metrics['R2_pseudo_second_order']:.4f})")
    print(f"  * Total Degradation Efficiency: {metrics['final_degradation_pct']:.2f}%")

    # Export publication graphics (600 DPI PNG, SVG, PDF)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / "UV_Vis_Kinetics_Publication"
    save_publication_figure(fig, out_base, dpi=600, formats=('png', 'svg', 'pdf'))

    # Export LabPlot ASCII matrices: both spectra series and kinetics table
    spectra_ascii_out = OUTPUT_DIR / "UV_Vis_Spectra_Matrix.dat"
    units_spectra = {'Wavelength_nm': 'nm'}
    for col in labplot_spectra.columns[1:]:
        units_spectra[col] = 'Absorbance a.u.'
    export_labplot_ascii(
        labplot_spectra,
        filepath=spectra_ascii_out,
        title="Time-Resolved UV-Vis Absorbance Spectra Series",
        units=units_spectra,
        comments=["Dye photodegradation time-series", f"Peak lambda = {metrics['lambda_max_nm']} nm"]
    )
    origin_spectra_out = OUTPUT_DIR / "Time_Resolved_UV_Vis_OriginLab.dat"
    export_originlab_ascii(
        labplot_spectra,
        filepath=origin_spectra_out,
        title="Time-Resolved UV-Vis Absorbance Spectra Series",
        units=units_spectra,
        comments=["Dye photodegradation time-series", f"Peak lambda = {metrics['lambda_max_nm']} nm"]
    )

    kinetics_ascii_out = OUTPUT_DIR / "Photodegradation_Kinetics_Matrix.dat"
    units_kinetics = {
        'Time_min': 'min',
        'Absorbance_lambda_max': 'a.u.',
        'Ct_over_C0': 'dimensionless',
        'Concentration_mg_L': 'mg/L',
        'Degradation_Efficiency_pct': '%',
        'ln_C0_Ct': 'dimensionless',
        'Pseudo_First_Order_Fit': 'dimensionless',
        'Inv_Ct_minus_Inv_C0': 'L/mg',
        'Pseudo_Second_Order_Fit': 'L/mg'
    }
    export_labplot_ascii(
        labplot_kinetics,
        filepath=kinetics_ascii_out,
        title="Dye Photodegradation Kinetics Data and Regression Fits",
        units=units_kinetics,
        comments=[
            f"k_app = {metrics['k_pseudo_first_order_min-1']} min^-1, R2 = {metrics['R2_pseudo_first_order']}",
            f"k2 = {metrics['k_pseudo_second_order']}, R2 = {metrics['R2_pseudo_second_order']}"
        ]
    )
    origin_kinetics_out = OUTPUT_DIR / "Photodegradation_Kinetics_OriginLab.dat"
    export_originlab_ascii(
        labplot_kinetics,
        filepath=origin_kinetics_out,
        title="Dye Photodegradation Kinetics Data and Regression Fits",
        units=units_kinetics,
        comments=[
            f"k_app = {metrics['k_pseudo_first_order_min-1']} min^-1, R2 = {metrics['R2_pseudo_first_order']}",
            f"k2 = {metrics['k_pseudo_second_order']}, R2 = {metrics['R2_pseudo_second_order']}"
        ]
    )

    plt.close(fig)
    print("\n[COMPLETED] UV-Vis & degradation kinetics analysis finished successfully.\n")


if __name__ == '__main__':
    main()
