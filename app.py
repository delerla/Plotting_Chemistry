"""
app.py - Automated Materials Characterization & Spectroscopic Analysis Hub
Interactive Desktop GUI powered by Streamlit, SciPy, lmfit, OpenCV, Matplotlib, and OpenPyXL.
Equipped with Universal Multi-Format Ingestion (Excel, OriginLab, CSV, TXT, DAT, ASC, DPT, PRN, Images)
and Physics-Based Technique Auto-Detection & Header Cleaning.
"""

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.export_utils import get_figure_bytes, get_labplot_ascii_bytes
from modules.file_parser import load_smart_file, detect_technique
from modules.ftir_module import process_and_plot_ftir, generate_benchmark_ftir_data
from modules.xrd_module import process_and_plot_xrd, generate_benchmark_xrd_data
from modules.uv_vis_module import process_and_plot_uv_vis, generate_benchmark_uv_vis_data
from modules.xps_module import deconvolve_xps, generate_benchmark_xps_data
from modules.sem_edx_module import (
    analyze_sem_micrograph,
    analyze_edx_spectrum,
    generate_benchmark_sem_image,
    generate_benchmark_edx_data
)

# Page configuration
st.set_page_config(
    page_title="Materials Characterization Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for scientific styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e3d59;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #555555;
        margin-bottom: 1.2rem;
    }
    .smart-card {
        background: linear-gradient(135deg, #f0f7ff 0%, #e6f0fa 100%);
        border: 1px solid #b8daff;
        border-left: 5px solid #0066cc;
        padding: 0.9rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1.2rem;
    }
    .stDownloadButton button {
        width: 100%;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# List of supported file extensions
ALL_SUPPORTED_EXTS = ["csv", "xlsx", "xls", "txt", "dat", "tsv", "ascii", "asc", "dpt", "prn", "xy", "png", "jpg", "tif", "tiff"]

TECHNIQUES = [
    "1. FTIR Spectroscopy",
    "2. XRD Crystallography",
    "3. UV-Vis & Dye Kinetics",
    "4. XPS Core Deconvolution",
    "5. SEM & EDX Microanalysis"
]

if "current_technique" not in st.session_state:
    st.session_state.current_technique = TECHNIQUES[0]

# ==============================================================================
# GLOBAL SMART DROPZONE (AUTO-DETECT & HEADER CLEANER)
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚡ Universal Smart Ingestion")
    st.caption("Drop any file (Excel, OriginLab export, CSV, DAT, TXT, ASC, DPT, Micrograph):")
    smart_uploaded = st.file_uploader(
        "Auto-Classify & Clean Any File",
        type=ALL_SUPPORTED_EXTS,
        key="smart_global_uploader",
        help="Uploads Excel (.xlsx/.xls), OriginLab worksheets, or ASCII files. Cleans multi-line headers, handles comma decimals, and detects technique automatically."
    )
    
    if smart_uploaded is not None:
        file_bytes = smart_uploaded.read()
        smart_df, smart_img, meta = load_smart_file(file_bytes, filename=smart_uploaded.name)
        
        if meta.get('detected_technique'):
            target_tech = meta['detected_technique']
            # Match with standard dropdown item
            matched_tech = next((t for t in TECHNIQUES if t[:2] == target_tech[:2]), target_tech)
            st.session_state["smart_data"] = {
                'df': smart_df,
                'img': smart_img,
                'meta': meta,
                'matched_tech': matched_tech
            }
            if st.button(f"🎯 Switch to {matched_tech[:6]}", key="btn_switch_tech"):
                st.session_state.current_technique = matched_tech
                st.rerun()

    st.markdown("---")
    st.markdown("### 🔬 Technique Selection")
    selected_tech = st.radio(
        "Active Technique:",
        TECHNIQUES,
        index=TECHNIQUES.index(st.session_state.current_technique) if st.session_state.current_technique in TECHNIQUES else 0,
        key="radio_technique"
    )
    st.session_state.current_technique = selected_tech

    st.markdown("---")
    st.markdown("### 📁 Interoperability")
    st.caption("Publication raster (600 DPI PNG), vectors (SVG, PDF), and LabPlot ASCII matrices (.dat) exported across all modules.")

# Display Smart Banner if a file was recently analyzed via smart uploader
if "smart_data" in st.session_state:
    s_info = st.session_state["smart_data"]
    s_meta = s_info['meta']
    st.markdown(f"""
    <div class="smart-card">
        <strong>📂 Smart Ingestion Summary:</strong> <code>{s_meta['filename']}</code> ({s_meta['format']})<br>
        <strong>🔬 Detected Technique:</strong> <b>{s_meta['detected_technique']}</b> &nbsp;•&nbsp; 
        <strong>Confidence:</strong> <code>{s_meta['confidence']*100:.0f}%</code><br>
        <small style="color: #444444;">{s_meta['reason']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 View Cleaned Header & Numerical Table", expanded=False):
        if s_info['df'] is not None:
            st.write(f"Cleaned {s_meta['rows']} rows and {len(s_meta['columns'])} columns:")
            st.dataframe(s_info['df'].head(8), use_container_width=True)
        elif s_info['img'] is not None:
            st.write(f"Micrograph Image Shape: {s_info['img'].shape}")

technique = st.session_state.current_technique

# ==============================================================================
# 1. FTIR MODULE
# ==============================================================================
if technique.startswith("1"):
    st.markdown('<div class="main-header">Fourier-Transform Infrared (FTIR) Spectroscopy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-sample spectral stacking, Savitzky-Golay filtering, and automatic vibrational band detection.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Parameters")
        data_source = st.radio("Source:", ["Use Benchmark Data", "Upload File (Excel / Origin / CSV / DAT)"], key="ftir_src")
        
        if data_source != "Use Benchmark Data":
            up_file = st.file_uploader(
                "Upload File (Col 1: Wavenumber, Subsequent: %T)",
                type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "dpt"],
                key="ftir_up"
            )
            if up_file is not None:
                parsed_df, _, meta_up = load_smart_file(up_file.read(), filename=up_file.name)
                if parsed_df is not None and not parsed_df.empty:
                    df_ftir = parsed_df
                    st.success(f"Cleaned {meta_up['rows']} rows from {meta_up['format']}")
                else:
                    st.error("Could not parse numeric columns. Falling back to benchmark.")
                    df_ftir = generate_benchmark_ftir_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("1"):
                df_ftir = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting file upload. Showing benchmark.")
                df_ftir = generate_benchmark_ftir_data()
        else:
            default_path = BASE_DIR / "data" / "ftir" / "ftir_data.csv"
            df_ftir = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_ftir_data()

        step_offset = st.slider("Vertical Stacking Offset (%)", min_value=10.0, max_value=80.0, value=35.0, step=5.0)
        sg_window = st.slider("Savitzky-Golay Window", min_value=5, max_value=35, value=11, step=2)
        sg_poly = st.slider("Polynomial Order", min_value=1, max_value=4, value=2, step=1)
        prominence = st.slider("Peak Detection Prominence", min_value=1.0, max_value=15.0, value=4.0, step=0.5)

    with col_view:
        fig_ftir, ax_ftir, peaks_dict, labplot_ftir_df = process_and_plot_ftir(
            df_ftir,
            step_offset=step_offset,
            sg_window=sg_window,
            sg_poly=sg_poly,
            prominence=prominence
        )
        st.pyplot(fig_ftir)

        with st.expander("📊 Detected Vibrational Absorption Bands", expanded=True):
            peak_rows = []
            for smp, p_list in peaks_dict.items():
                peak_rows.append({"Sample": smp, "Detected Bands (cm⁻¹)": ", ".join(map(str, p_list)) if p_list else "None detected"})
            st.dataframe(pd.DataFrame(peak_rows), use_container_width=True)

        st.markdown("#### 📥 Publication & LabPlot Export")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button(
                "Export 600 DPI PNG",
                data=get_figure_bytes(fig_ftir, 'png', dpi=600),
                file_name="FTIR_Stacked_600DPI.png",
                mime="image/png"
            )
        with c2:
            st.download_button(
                "Export Vector SVG",
                data=get_figure_bytes(fig_ftir, 'svg'),
                file_name="FTIR_Stacked.svg",
                mime="image/svg+xml"
            )
        with c3:
            st.download_button(
                "Export Vector PDF",
                data=get_figure_bytes(fig_ftir, 'pdf'),
                file_name="FTIR_Stacked.pdf",
                mime="application/pdf"
            )
        with c4:
            units = {'Wavenumber': 'cm^-1'}
            for col in labplot_ftir_df.columns[1:]:
                units[col] = '%' if 'Raw' in col or 'Smoothed' in col else 'offset a.u.'
            ascii_bytes = get_labplot_ascii_bytes(
                labplot_ftir_df,
                title="FTIR Stacked Spectra with Savitzky-Golay Filtering",
                units=units
            )
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=ascii_bytes,
                file_name="FTIR_Stacked_LabPlot.dat",
                mime="text/plain"
            )
        plt.close(fig_ftir)

# ==============================================================================
# 2. XRD MODULE
# ==============================================================================
elif technique.startswith("2"):
    st.markdown('<div class="main-header">X-Ray Diffraction (XRD) & Scherrer Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cu Kα (λ = 1.5406 Å) diffraction stacking, Lorentzian deconvolution, and crystallite size determination.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Parameters")
        data_source = st.radio("Source:", ["Use Benchmark Data", "Upload File (Excel / Origin / CSV / DAT / XY / PRN)"], key="xrd_src")
        
        if data_source != "Use Benchmark Data":
            up_file = st.file_uploader(
                "Upload File (Col 1: 2θ, Subsequent: Intensity)",
                type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "xy", "prn", "asc"],
                key="xrd_up"
            )
            if up_file is not None:
                parsed_df, _, meta_up = load_smart_file(up_file.read(), filename=up_file.name)
                if parsed_df is not None and not parsed_df.empty:
                    df_xrd = parsed_df
                    st.success(f"Cleaned {meta_up['rows']} rows from {meta_up['format']}")
                else:
                    st.error("Could not parse numeric columns. Falling back to benchmark.")
                    df_xrd = generate_benchmark_xrd_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("2"):
                df_xrd = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting file upload. Showing benchmark.")
                df_xrd = generate_benchmark_xrd_data()
        else:
            default_path = BASE_DIR / "data" / "xrd" / "xrd_data.csv"
            df_xrd = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_xrd_data()

        offset_step = st.slider("Stacking Offset (a.u.)", min_value=100.0, max_value=1200.0, value=500.0, step=50.0)
        fit_min = st.number_input("Fit Window 2θ Min (deg)", value=41.5, step=0.5)
        fit_max = st.number_input("Fit Window 2θ Max (deg)", value=45.0, step=0.5)
        wavelength = st.number_input("X-Ray Wavelength λ (nm)", value=0.15406, format="%.5f")
        k_factor = st.number_input("Scherrer Constant K", value=0.9, format="%.2f")

    with col_view:
        fig_xrd, ax_xrd, fit_results, labplot_xrd_df = process_and_plot_xrd(
            df_xrd,
            offset_step=offset_step,
            fit_range=(fit_min, fit_max),
            wavelength_nm=wavelength,
            k_factor=k_factor
        )
        st.pyplot(fig_xrd)

        with st.expander("📊 Scherrer Crystallite Sizing Metrics", expanded=True):
            fit_rows = []
            for smp, res in fit_results.items():
                if 'Error' not in res:
                    fit_rows.append({
                        "Pattern": smp,
                        "Peak 2θ (°)": res['Peak_2Theta_deg'],
                        "FWHM (°)": res['FWHM_deg'],
                        "Crystallite Size D (nm)": res['Crystallite_Size_nm']
                    })
                else:
                    fit_rows.append({"Pattern": smp, "Status": res['Error']})
            st.dataframe(pd.DataFrame(fit_rows), use_container_width=True)

        st.markdown("#### 📥 Publication & LabPlot Export")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button(
                "Export 600 DPI PNG",
                data=get_figure_bytes(fig_xrd, 'png', dpi=600),
                file_name="XRD_Stacked_600DPI.png",
                mime="image/png"
            )
        with c2:
            st.download_button(
                "Export Vector SVG",
                data=get_figure_bytes(fig_xrd, 'svg'),
                file_name="XRD_Stacked.svg",
                mime="image/svg+xml"
            )
        with c3:
            st.download_button(
                "Export Vector PDF",
                data=get_figure_bytes(fig_xrd, 'pdf'),
                file_name="XRD_Stacked.pdf",
                mime="application/pdf"
            )
        with c4:
            units = {'TwoTheta_deg': 'degrees'}
            for col in labplot_xrd_df.columns[1:]:
                units[col] = 'Counts'
            ascii_bytes = get_labplot_ascii_bytes(
                labplot_xrd_df,
                title="XRD Diffraction Stacked Patterns with Scherrer Analysis",
                units=units
            )
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=ascii_bytes,
                file_name="XRD_Stacked_LabPlot.dat",
                mime="text/plain"
            )
        plt.close(fig_xrd)

# ==============================================================================
# 3. UV-VIS & DYE KINETICS MODULE
# ==============================================================================
elif technique.startswith("3"):
    st.markdown('<div class="main-header">UV-Vis Spectroscopy & Photodegradation Kinetics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Spectral evolution monitoring, pseudo-first-order (ln(C₀/C_t) = k_app·t) & pseudo-second-order fitting.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Parameters")
        data_source = st.radio("Source:", ["Use Benchmark Data", "Upload File (Excel / Origin / CSV / DAT)"], key="uv_src")
        
        if data_source != "Use Benchmark Data":
            up_file = st.file_uploader(
                "Upload File (Col 1: Wavelength, Subsequent: Time Traces)",
                type=["csv", "xlsx", "xls", "txt", "dat", "tsv"],
                key="uv_up"
            )
            if up_file is not None:
                parsed_df, _, meta_up = load_smart_file(up_file.read(), filename=up_file.name)
                if parsed_df is not None and not parsed_df.empty:
                    df_uv = parsed_df
                    st.success(f"Cleaned {meta_up['rows']} rows from {meta_up['format']}")
                else:
                    st.error("Could not parse numeric columns. Falling back to benchmark.")
                    df_uv, _ = generate_benchmark_uv_vis_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("3"):
                df_uv = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting file upload. Showing benchmark.")
                df_uv, _ = generate_benchmark_uv_vis_data()
        else:
            default_path = BASE_DIR / "data" / "uv_vis" / "uv_vis_spectra.csv"
            df_uv = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_uv_vis_data()[0]

        target_lambda = st.number_input("Target Peak Wavelength λ_max (nm)", value=554.0, step=1.0)
        c0_initial = st.number_input("Initial Dye Concentration C₀ (mg/L)", value=10.0, step=1.0)

    with col_view:
        fig_uv, axes_uv, uv_metrics, labplot_spectra, labplot_kinetics = process_and_plot_uv_vis(
            df_uv,
            lambda_target=target_lambda,
            initial_conc=c0_initial
        )
        st.pyplot(fig_uv)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("λ_max Monitored", f"{uv_metrics['lambda_max_nm']} nm")
        m2.metric("k_app (PFO)", f"{uv_metrics['k_pseudo_first_order_min-1']:.4f} min⁻¹", f"R² = {uv_metrics['R2_pseudo_first_order']:.4f}")
        m3.metric("k₂ (PSO)", f"{uv_metrics['k_pseudo_second_order']:.5f}", f"R² = {uv_metrics['R2_pseudo_second_order']:.4f}")
        m4.metric("Degradation Efficiency", f"{uv_metrics['final_degradation_pct']:.1f}%")

        with st.expander("📊 Detailed Degradation Kinetics Table", expanded=False):
            st.dataframe(labplot_kinetics, use_container_width=True)

        st.markdown("#### 📥 Publication & LabPlot Export")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button(
                "Export 600 DPI PNG",
                data=get_figure_bytes(fig_uv, 'png', dpi=600),
                file_name="UV_Vis_Kinetics_600DPI.png",
                mime="image/png"
            )
        with c2:
            st.download_button(
                "Export Vector SVG",
                data=get_figure_bytes(fig_uv, 'svg'),
                file_name="UV_Vis_Kinetics.svg",
                mime="image/svg+xml"
            )
        with c3:
            st.download_button(
                "Export Vector PDF",
                data=get_figure_bytes(fig_uv, 'pdf'),
                file_name="UV_Vis_Kinetics.pdf",
                mime="application/pdf"
            )
        with c4:
            units_k = {
                'Time_min': 'min', 'Absorbance_lambda_max': 'a.u.', 'Ct_over_C0': 'dimensionless',
                'Concentration_mg_L': 'mg/L', 'Degradation_Efficiency_pct': '%', 'ln_C0_Ct': 'dimensionless',
                'Pseudo_First_Order_Fit': 'dimensionless', 'Inv_Ct_minus_Inv_C0': 'L/mg', 'Pseudo_Second_Order_Fit': 'L/mg'
            }
            ascii_bytes = get_labplot_ascii_bytes(
                labplot_kinetics,
                title="Dye Photodegradation Kinetics Data and Fits",
                units=units_k
            )
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=ascii_bytes,
                file_name="Photodegradation_Kinetics_LabPlot.dat",
                mime="text/plain"
            )
        plt.close(fig_uv)

# ==============================================================================
# 4. XPS DECONVOLUTION MODULE
# ==============================================================================
elif technique.startswith("4"):
    st.markdown('<div class="main-header">X-Ray Photoelectron Spectroscopy (XPS) Deconvolution</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Iterative Shirley baseline subtraction, C 1s charge referencing (284.8 eV), and non-linear multi-peak Voigt profile fitting via lmfit.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Fitting Settings")
        data_source = st.radio("Source:", ["Use Benchmark Data", "Upload File (Excel / Origin / CSV / DAT)"], key="xps_src")
        
        if data_source != "Use Benchmark Data":
            up_file = st.file_uploader(
                "Upload File (Col 1: Binding Energy eV, Col 2: Counts/s)",
                type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc"],
                key="xps_up"
            )
            if up_file is not None:
                parsed_df, _, meta_up = load_smart_file(up_file.read(), filename=up_file.name)
                if parsed_df is not None and not parsed_df.empty:
                    df_xps = parsed_df
                    st.success(f"Cleaned {meta_up['rows']} rows from {meta_up['format']}")
                else:
                    st.error("Could not parse numeric columns. Falling back to benchmark.")
                    df_xps = generate_benchmark_xps_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("4"):
                df_xps = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting file upload. Showing benchmark.")
                df_xps = generate_benchmark_xps_data()
        else:
            default_path = BASE_DIR / "data" / "xps" / "c1s_high_res.csv"
            df_xps = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_xps_data()

        apply_c1s = st.checkbox("Auto-Calibrate C 1s Charge Shift", value=True)
        ref_be = st.number_input("C 1s Reference Position (eV)", value=284.8, step=0.1)

    with col_view:
        fig_xps, summary_xps, labplot_xps_df = deconvolve_xps(
            df_xps,
            c1s_calibration=apply_c1s,
            expected_ref_be=ref_be
        )
        st.pyplot(fig_xps)

        m1, m2, m3 = st.columns(3)
        m1.metric("BE Shift Applied", f"{summary_xps['be_shift_applied_eV']:+.3f} eV")
        m2.metric("Fit R²", f"{summary_xps['r_squared']:.4f}")
        m3.metric("Reduced χ²", f"{summary_xps['redchi']:.1f}")

        with st.expander("📊 Chemical State Quantification Table (at%)", expanded=True):
            st.dataframe(pd.DataFrame(summary_xps['quantification_table']), use_container_width=True)

        st.markdown("#### 📥 Publication & LabPlot Export")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button(
                "Export 600 DPI PNG",
                data=get_figure_bytes(fig_xps, 'png', dpi=600),
                file_name="XPS_Deconvolution_600DPI.png",
                mime="image/png"
            )
        with c2:
            st.download_button(
                "Export Vector SVG",
                data=get_figure_bytes(fig_xps, 'svg'),
                file_name="XPS_Deconvolution.svg",
                mime="image/svg+xml"
            )
        with c3:
            st.download_button(
                "Export Vector PDF",
                data=get_figure_bytes(fig_xps, 'pdf'),
                file_name="XPS_Deconvolution.pdf",
                mime="application/pdf"
            )
        with c4:
            units = {'Binding_Energy_eV': 'eV'}
            for col in labplot_xps_df.columns[1:]:
                units[col] = 'Counts/s'
            ascii_bytes = get_labplot_ascii_bytes(
                labplot_xps_df,
                title="XPS Core-Level Shirley Deconvolution Matrix",
                units=units
            )
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=ascii_bytes,
                file_name="XPS_Deconvolution_LabPlot.dat",
                mime="text/plain"
            )
        plt.close(fig_xps)

# ==============================================================================
# 5. SEM & EDX MICROANALYSIS MODULE
# ==============================================================================
elif technique.startswith("5"):
    st.markdown('<div class="main-header">SEM Micrograph & EDX Elemental Microanalysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Particle segmentation, Otsu thresholding, diameter distributions, and EDX characteristic line elemental quantification.</div>', unsafe_allow_html=True)

    tab_sem, tab_edx = st.tabs(["📷 SEM Particle Sizing", "⚡ EDX Spectroscopy"])

    with tab_sem:
        col_ctrl, col_view = st.columns([1, 2.5])
        with col_ctrl:
            st.subheader("SEM Settings")
            sem_source = st.radio("Image Source:", ["Benchmark Micrograph", "Upload Image (PNG/TIFF/JPG/BMP)"], key="sem_src")
            if sem_source != "Benchmark Micrograph":
                uploaded_img = st.file_uploader(
                    "Upload SEM Image",
                    type=["png", "jpg", "jpeg", "tif", "tiff", "bmp"],
                    key="sem_up"
                )
                if uploaded_img is not None:
                    _, parsed_img, _ = load_smart_file(uploaded_img.read(), filename=uploaded_img.name)
                    sem_img = parsed_img if parsed_img is not None else generate_benchmark_sem_image()
                elif "smart_data" in st.session_state and st.session_state["smart_data"]['img'] is not None:
                    sem_img = st.session_state["smart_data"]['img']
                else:
                    st.info("Awaiting image upload. Showing benchmark.")
                    sem_img = generate_benchmark_sem_image()
            else:
                default_path = BASE_DIR / "data" / "sem_edx" / "sem_micrograph.png"
                sem_img = cv2.imread(str(default_path), cv2.IMREAD_GRAYSCALE) if default_path.exists() else generate_benchmark_sem_image()

            nm_per_px = st.number_input("Scale (nm / pixel)", value=2.5, min_value=0.1, step=0.5)
            min_area = st.slider("Min Particle Area (pixels)", min_value=5, max_value=100, value=25, step=5)

        with col_view:
            fig_sem, stats_sem, df_particles = analyze_sem_micrograph(
                sem_img,
                scale_nm_per_pixel=nm_per_px,
                min_area_px=min_area
            )
            st.pyplot(fig_sem)

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Particles Counted", f"{stats_sem['Total_Count']}")
            s2.metric("Mean Diameter", f"{stats_sem['Mean_Diameter_nm']} nm", f"± {stats_sem['Std_Diameter_nm']} nm")
            s3.metric("Median (D50)", f"{stats_sem['Median_Diameter_nm']} nm")
            s4.metric("D10 / D90 Span", f"{stats_sem['D10_nm']} / {stats_sem['D90_nm']} nm")

            st.markdown("#### 📥 SEM Publication & LabPlot Export")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.download_button(
                    "Export 600 DPI PNG",
                    data=get_figure_bytes(fig_sem, 'png', dpi=600),
                    file_name="SEM_Particle_Sizing_600DPI.png",
                    mime="image/png"
                )
            with c2:
                st.download_button(
                    "Export Vector SVG",
                    data=get_figure_bytes(fig_sem, 'svg'),
                    file_name="SEM_Particle_Sizing.svg",
                    mime="image/svg+xml"
                )
            with c3:
                st.download_button(
                    "Export Vector PDF",
                    data=get_figure_bytes(fig_sem, 'pdf'),
                    file_name="SEM_Particle_Sizing.pdf",
                    mime="application/pdf"
                )
            with c4:
                units = {'Particle_ID': '#', 'Area_px': 'px^2', 'Diameter_nm': 'nm', 'Circularity': 'dimensionless', 'Centroid_Y': 'px', 'Centroid_X': 'px'}
                ascii_bytes = get_labplot_ascii_bytes(
                    df_particles,
                    title="SEM Particle Morphological Sizing and Area Distribution",
                    units=units
                )
                st.download_button(
                    "LabPlot ASCII Matrix (.dat)",
                    data=ascii_bytes,
                    file_name="SEM_Particle_Sizing_LabPlot.dat",
                    mime="text/plain"
                )
            plt.close(fig_sem)

    with tab_edx:
        col_ctrl2, col_view2 = st.columns([1, 2.5])
        with col_ctrl2:
            st.subheader("EDX Settings")
            edx_source = st.radio("Data Source:", ["Benchmark EDX", "Upload File (Excel / Origin / CSV / DAT)"], key="edx_src")
            if edx_source != "Benchmark EDX":
                up_edx = st.file_uploader(
                    "Upload File (Col 1: Energy keV, Col 2: Counts)",
                    type=["csv", "xlsx", "xls", "txt", "dat", "tsv"],
                    key="edx_up"
                )
                if up_edx is not None:
                    parsed_df, _, meta_up = load_smart_file(up_edx.read(), filename=up_edx.name)
                    if parsed_df is not None and not parsed_df.empty:
                        df_edx = parsed_df
                        st.success(f"Cleaned {meta_up['rows']} rows from {meta_up['format']}")
                    else:
                        st.error("Could not parse numeric columns. Falling back to benchmark.")
                        df_edx = generate_benchmark_edx_data()
                elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("5"):
                    df_edx = st.session_state["smart_data"]['df']
                else:
                    st.info("Awaiting EDX upload. Showing benchmark.")
                    df_edx = generate_benchmark_edx_data()
            else:
                default_path = BASE_DIR / "data" / "sem_edx" / "edx_spectrum.csv"
                df_edx = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_edx_data()

            prominence_edx = st.slider("Peak Detection Prominence", min_value=20.0, max_value=300.0, value=80.0, step=10.0)
            tol_edx = st.slider("Line Match Tolerance (keV)", min_value=0.05, max_value=0.30, value=0.16, step=0.01)

        with col_view2:
            fig_edx, res_edx, labplot_edx = analyze_edx_spectrum(
                df_edx,
                prominence=prominence_edx,
                peak_tolerance_keV=tol_edx
            )
            st.pyplot(fig_edx)

            with st.expander("📊 Elemental Quantification (wt% and at%)", expanded=True):
                st.dataframe(pd.DataFrame(res_edx['quantification']), use_container_width=True)

            st.markdown("#### 📥 EDX Publication & LabPlot Export")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.download_button(
                    "Export 600 DPI PNG",
                    data=get_figure_bytes(fig_edx, 'png', dpi=600),
                    file_name="EDX_Spectrum_600DPI.png",
                    mime="image/png",
                    key="edx_png"
                )
            with c2:
                st.download_button(
                    "Export Vector SVG",
                    data=get_figure_bytes(fig_edx, 'svg'),
                    file_name="EDX_Spectrum.svg",
                    mime="image/svg+xml",
                    key="edx_svg"
                )
            with c3:
                st.download_button(
                    "Export Vector PDF",
                    data=get_figure_bytes(fig_edx, 'pdf'),
                    file_name="EDX_Spectrum.pdf",
                    mime="application/pdf",
                    key="edx_pdf"
                )
            with c4:
                ascii_bytes = get_labplot_ascii_bytes(
                    labplot_edx,
                    title="Energy-Dispersive X-Ray Spectroscopy (EDX) Spectrum",
                    units={'Energy_keV': 'keV', 'Counts': 'Counts'}
                )
                st.download_button(
                    "LabPlot ASCII Matrix (.dat)",
                    data=ascii_bytes,
                    file_name="EDX_Spectrum_LabPlot.dat",
                    mime="text/plain",
                    key="edx_dat"
                )
            plt.close(fig_edx)
