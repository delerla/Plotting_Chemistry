"""
app.py - Automated Materials Characterization & Spectroscopic Analysis Hub
Professional Scientific GUI powered by Streamlit, SciPy, lmfit, OpenCV, Matplotlib, and OpenPyXL.
Equipped with:
- Universal Ingestion (Excel, OriginLab, CSV, DAT, TXT, ASC, DPT, PRN, Images)
- Physics-Based Technique Auto-Detection & Multi-Line Header Cleaning
- Publication Journal Themes (Nature, Science, ACS, RSC, Monochrome)
- 1-Click Complete Publication Package (.ZIP) Exporter
- High-Precision Deconvolution & Crystallite Sizing Engine
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

from modules.export_utils import (
    PUBLICATION_PALETTES,
    build_analysis_bundle_zip,
    get_figure_bytes,
    get_labplot_ascii_bytes
)
from modules.file_parser import load_smart_file
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

# Professional CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f2b48;
        margin-bottom: 0.15rem;
        letter-spacing: -0.02em;
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
        padding: 0.85rem 1.1rem;
        border-radius: 6px;
        margin-bottom: 1.2rem;
    }
    .stDownloadButton button {
        width: 100%;
        border-radius: 4px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton button:hover {
        border-color: #0066cc;
        color: #0066cc;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0f2b48;
    }
</style>
""", unsafe_allow_html=True)

TECHNIQUES = [
    "1. FTIR Spectroscopy",
    "2. XRD Crystallography",
    "3. UV-Vis & Dye Kinetics",
    "4. XPS Core Deconvolution",
    "5. SEM & EDX Microanalysis"
]

ALL_SUPPORTED_EXTS = ["csv", "xlsx", "xls", "txt", "dat", "tsv", "ascii", "asc", "dpt", "prn", "xy", "png", "jpg", "tif", "tiff"]

if "current_technique" not in st.session_state:
    st.session_state.current_technique = TECHNIQUES[0]

# ==============================================================================
# SIDEBAR CONTROLS & UNIVERSAL SMART INGESTION
# ==============================================================================
with st.sidebar:
    st.markdown("### 🔬 Materials Characterization")
    st.caption("Commercial-grade open-source alternative to OriginLab.")
    
    selected_theme = st.selectbox(
        "🎨 Publication Color Palette:",
        list(PUBLICATION_PALETTES.keys()),
        index=2,
        help="Applies standard editorial color palettes matching top scientific journals."
    )

    st.markdown("---")
    st.markdown("### ⚡ Smart File Dropzone")
    st.caption("Upload any file (Excel, OriginLab export, CSV, DAT, ASC, DPT, Micrograph):")
    smart_uploaded = st.file_uploader(
        "Drop Any File for Auto-Detection",
        type=ALL_SUPPORTED_EXTS,
        key="smart_global_uploader",
        help="Cleans multi-line headers, handles comma decimals, and detects technique automatically."
    )
    
    if smart_uploaded is not None:
        file_bytes = smart_uploaded.read()
        smart_df, smart_img, meta = load_smart_file(file_bytes, filename=smart_uploaded.name)
        
        if meta.get('detected_technique'):
            target_tech = meta['detected_technique']
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
    st.markdown("### 📑 Module Navigation")
    selected_tech = st.radio(
        "Select Technique:",
        TECHNIQUES,
        index=TECHNIQUES.index(st.session_state.current_technique) if st.session_state.current_technique in TECHNIQUES else 0,
        key="radio_technique"
    )
    st.session_state.current_technique = selected_tech

    st.markdown("---")
    st.caption("LabPlot ASCII (.dat), 600 DPI PNG, Vector SVG & PDF exports enabled.")

# Smart Ingestion Notification Banner
if "smart_data" in st.session_state:
    s_info = st.session_state["smart_data"]
    s_meta = s_info['meta']
    st.markdown(f"""
    <div class="smart-card">
        <strong>📂 Ingested File:</strong> <code>{s_meta['filename']}</code> ({s_meta['format']}) &nbsp;•&nbsp; 
        <strong>Detected Technique:</strong> <b>{s_meta['detected_technique']}</b> (<code>{s_meta['confidence']*100:.0f}% confidence</code>)<br>
        <small style="color: #444444;">{s_meta['reason']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Inspect Cleaned Header & Numerical Table", expanded=False):
        if s_info['df'] is not None:
            st.write(f"Cleaned {s_meta['rows']} rows and {len(s_meta['columns'])} columns:")
            st.dataframe(s_info['df'].head(8), use_container_width=True)
        elif s_info['img'] is not None:
            st.write(f"Micrograph Dimensions: {s_info['img'].shape}")

technique = st.session_state.current_technique

# ==============================================================================
# 1. FTIR SPECTROSCOPY MODULE
# ==============================================================================
if technique.startswith("1"):
    st.markdown('<div class="main-header">Fourier-Transform Infrared (FTIR) Spectroscopy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-sample spectral stacking, Savitzky-Golay filtering, normalization, and vibrational band deconvolution.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Parameters")
        data_source = st.radio("Data Source:", ["Benchmark Spectra", "Upload File (Excel / Origin / CSV / DAT)"], key="ftir_src")
        
        if data_source != "Benchmark Spectra":
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
                    st.error("Parsing failed. Using benchmark.")
                    df_ftir = generate_benchmark_ftir_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("1"):
                df_ftir = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting upload. Showing benchmark.")
                df_ftir = generate_benchmark_ftir_data()
        else:
            default_path = BASE_DIR / "data" / "ftir" / "ftir_data.csv"
            df_ftir = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_ftir_data()

        if df_ftir is not None and not df_ftir.empty and df_ftir.shape[1] > 1:
            all_ftir_cols = list(df_ftir.columns)
            def_idx = 0
            for i, c in enumerate(all_ftir_cols):
                if any(k in str(c).lower() for k in ['wavenumber', 'cm-1', 'cm^-1']):
                    def_idx = i
                    break
            col_x_ftir = st.selectbox("Wavenumber (X-Axis):", all_ftir_cols, index=def_idx, key="ftir_col_x")
            avail_ftir = [c for c in all_ftir_cols if c != col_x_ftir]
            sel_ftir = st.multiselect("Spectra to Display:", avail_ftir, default=avail_ftir, key="ftir_col_y")
            if sel_ftir:
                df_ftir = df_ftir[[col_x_ftir] + sel_ftir]

        ftir_mode = st.selectbox("Display Mode:", ["Transmittance (%T)", "Absorbance (A = -log10 T)"])
        norm_mode = st.selectbox("Normalization:", ["None", "Min-Max (0 to 1)", "Zero Baseline"])
        step_offset = st.slider("Stacking Offset", min_value=0.0, max_value=80.0, value=35.0, step=5.0)
        sg_window = st.slider("Savitzky-Golay Window", min_value=5, max_value=35, value=11, step=2)
        sg_poly = st.slider("Polynomial Order", min_value=1, max_value=4, value=2, step=1)
        prominence = st.slider("Peak Detection Prominence", min_value=1.0, max_value=15.0, value=4.0, step=0.5)

    with col_view:
        fig_ftir, ax_ftir, peaks_dict, labplot_ftir_df = process_and_plot_ftir(
            df_ftir,
            step_offset=step_offset,
            sg_window=sg_window,
            sg_poly=sg_poly,
            prominence=prominence,
            mode=ftir_mode,
            normalization=norm_mode,
            theme=selected_theme
        )
        st.pyplot(fig_ftir)

        with st.expander("📊 Detected Vibrational Absorption Bands", expanded=True):
            peak_rows = []
            for smp, p_list in peaks_dict.items():
                peak_rows.append({"Sample": smp, "Detected Bands (cm⁻¹)": ", ".join(map(str, p_list)) if p_list else "None detected"})
            summary_df = pd.DataFrame(peak_rows)
            st.dataframe(summary_df, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        # 1-Click Complete ZIP Package
        zip_bytes = build_analysis_bundle_zip(
            fig_ftir,
            base_name="FTIR_Stacked_Analysis",
            labplot_df=labplot_ftir_df,
            summary_data=summary_df,
            title="FTIR Stacked Spectra with Savitzky-Golay Filtering",
            units={'Wavenumber_cm-1': 'cm^-1'}
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
            data=zip_bytes,
            file_name="FTIR_Publication_Package.zip",
            mime="application/zip"
        )
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_ftir, 'png', dpi=600), file_name="FTIR_600DPI.png", mime="image/png")
        with c2:
            st.download_button("Export Vector SVG", data=get_figure_bytes(fig_ftir, 'svg'), file_name="FTIR.svg", mime="image/svg+xml")
        with c3:
            st.download_button("Export Vector PDF", data=get_figure_bytes(fig_ftir, 'pdf'), file_name="FTIR.pdf", mime="application/pdf")
        with c4:
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_ftir_df, title="FTIR Matrix", units={'Wavenumber_cm-1': 'cm^-1'}),
                file_name="FTIR_LabPlot.dat",
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
        data_source = st.radio("Data Source:", ["Benchmark Patterns", "Upload File (Excel / Origin / CSV / DAT / XY)"], key="xrd_src")
        
        if data_source != "Benchmark Patterns":
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
                    st.error("Parsing failed. Using benchmark.")
                    df_xrd = generate_benchmark_xrd_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("2"):
                df_xrd = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting upload. Showing benchmark.")
                df_xrd = generate_benchmark_xrd_data()
        else:
            default_path = BASE_DIR / "data" / "xrd" / "xrd_data.csv"
            df_xrd = pd.read_csv(default_path) if default_path.exists() else generate_benchmark_xrd_data()

        if df_xrd is not None and not df_xrd.empty and df_xrd.shape[1] > 1:
            all_xrd_cols = list(df_xrd.columns)
            def_idx = 0
            for i, c in enumerate(all_xrd_cols):
                if any(k in str(c).lower() for k in ['2θ', '2theta', 'theta', 'degree', 'angle', 'two_theta', 'two theta']):
                    def_idx = i
                    break
            col_x_xrd = st.selectbox("2θ Angle (X-Axis):", all_xrd_cols, index=def_idx, key="xrd_col_x")
            avail_xrd = [c for c in all_xrd_cols if c != col_x_xrd]
            sel_xrd = st.multiselect("Active Samples to Display:", avail_xrd, default=avail_xrd, key="xrd_col_y")
            if sel_xrd:
                df_xrd = df_xrd[[col_x_xrd] + sel_xrd]

        norm_max = st.checkbox("Normalize Intensity to Max Reflection (0 to 100%)", value=False)
        offset_step = st.slider("Stacking Offset (a.u.)", min_value=50.0, max_value=1200.0, value=500.0, step=50.0)
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
            k_factor=k_factor,
            normalize_max=norm_max,
            theme=selected_theme
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
            summary_xrd_df = pd.DataFrame(fit_rows)
            st.dataframe(summary_xrd_df, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        zip_bytes_xrd = build_analysis_bundle_zip(
            fig_xrd,
            base_name="XRD_Stacked_Analysis",
            labplot_df=labplot_xrd_df,
            summary_data=summary_xrd_df,
            title="XRD Diffraction Stacked Patterns with Scherrer Analysis",
            units={'TwoTheta_deg': 'degrees'}
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
            data=zip_bytes_xrd,
            file_name="XRD_Publication_Package.zip",
            mime="application/zip"
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_xrd, 'png', dpi=600), file_name="XRD_600DPI.png", mime="image/png")
        with c2:
            st.download_button("Export Vector SVG", data=get_figure_bytes(fig_xrd, 'svg'), file_name="XRD.svg", mime="image/svg+xml")
        with c3:
            st.download_button("Export Vector PDF", data=get_figure_bytes(fig_xrd, 'pdf'), file_name="XRD.pdf", mime="application/pdf")
        with c4:
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_xrd_df, title="XRD Matrix", units={'TwoTheta_deg': 'degrees'}),
                file_name="XRD_LabPlot.dat",
                mime="text/plain"
            )
        plt.close(fig_xrd)

# ==============================================================================
# 3. UV-VIS & DYE KINETICS MODULE
# ==============================================================================
elif technique.startswith("3"):
    st.markdown('<div class="main-header">UV-Vis Spectroscopy & Photodegradation Kinetics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Spectral evolution monitoring, multi-order kinetic regression (0th, 1st, 2nd order), and rate constant determination.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.5])
    
    with col_ctrl:
        st.subheader("Data & Parameters")
        data_source = st.radio("Data Source:", ["Benchmark Spectra", "Upload File (Excel / Origin / CSV / DAT)"], key="uv_src")
        
        if data_source != "Benchmark Spectra":
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
                    st.error("Parsing failed. Using benchmark.")
                    df_uv, _ = generate_benchmark_uv_vis_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("3"):
                df_uv = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting upload. Showing benchmark.")
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
            initial_conc=c0_initial,
            theme=selected_theme
        )
        st.pyplot(fig_uv)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("λ_max Monitored", f"{uv_metrics['lambda_max_nm']} nm")
        m2.metric("Best Fit Model", f"{uv_metrics['best_kinetic_model']}")
        m3.metric("k_app (PFO)", f"{uv_metrics['k_pseudo_first_order_min-1']:.4f} min⁻¹", f"R² = {uv_metrics['R2_pseudo_first_order']:.4f}")
        m4.metric("Degradation Efficiency", f"{uv_metrics['final_degradation_pct']:.1f}%")

        with st.expander("📊 Multi-Order Kinetics Table (0th, 1st, 2nd Order)", expanded=False):
            st.dataframe(labplot_kinetics, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        zip_bytes_uv = build_analysis_bundle_zip(
            fig_uv,
            base_name="UV_Vis_Photodegradation_Kinetics",
            labplot_df=labplot_kinetics,
            summary_data=uv_metrics,
            title="Photodegradation Kinetics Data and Fits"
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
            data=zip_bytes_uv,
            file_name="UV_Vis_Kinetics_Package.zip",
            mime="application/zip"
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_uv, 'png', dpi=600), file_name="UV_Vis_600DPI.png", mime="image/png")
        with c2:
            st.download_button("Export Vector SVG", data=get_figure_bytes(fig_uv, 'svg'), file_name="UV_Vis.svg", mime="image/svg+xml")
        with c3:
            st.download_button("Export Vector PDF", data=get_figure_bytes(fig_uv, 'pdf'), file_name="UV_Vis.pdf", mime="application/pdf")
        with c4:
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_kinetics, title="Kinetics Matrix"),
                file_name="Kinetics_LabPlot.dat",
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
        data_source = st.radio("Data Source:", ["Benchmark C 1s Core", "Upload File (Excel / Origin / CSV / DAT)"], key="xps_src")
        
        if data_source != "Benchmark C 1s Core":
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
                    st.error("Parsing failed. Using benchmark.")
                    df_xps = generate_benchmark_xps_data()
            elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("4"):
                df_xps = st.session_state["smart_data"]['df']
            else:
                st.info("Awaiting upload. Showing benchmark.")
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
            expected_ref_be=ref_be,
            theme=selected_theme
        )
        st.pyplot(fig_xps)

        m1, m2, m3 = st.columns(3)
        m1.metric("BE Shift Applied", f"{summary_xps['be_shift_applied_eV']:+.3f} eV")
        m2.metric("Fit R²", f"{summary_xps['r_squared']:.4f}")
        m3.metric("Reduced χ²", f"{summary_xps['redchi']:.1f}")

        quant_df = pd.DataFrame(summary_xps['quantification_table'])
        with st.expander("📊 Chemical State Quantification Table (at%)", expanded=True):
            st.dataframe(quant_df, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        zip_bytes_xps = build_analysis_bundle_zip(
            fig_xps,
            base_name="XPS_Core_Deconvolution",
            labplot_df=labplot_xps_df,
            summary_data=quant_df,
            title="XPS Core-Level Shirley Deconvolution Matrix",
            units={'Binding_Energy_eV': 'eV'}
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
            data=zip_bytes_xps,
            file_name="XPS_Publication_Package.zip",
            mime="application/zip"
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_xps, 'png', dpi=600), file_name="XPS_600DPI.png", mime="image/png")
        with c2:
            st.download_button("Export Vector SVG", data=get_figure_bytes(fig_xps, 'svg'), file_name="XPS.svg", mime="image/svg+xml")
        with c3:
            st.download_button("Export Vector PDF", data=get_figure_bytes(fig_xps, 'pdf'), file_name="XPS.pdf", mime="application/pdf")
        with c4:
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_xps_df, title="XPS Matrix", units={'Binding_Energy_eV': 'eV'}),
                file_name="XPS_LabPlot.dat",
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
            min_circ = st.slider("Min Circularity Threshold", min_value=0.1, max_value=0.9, value=0.2, step=0.05)

        with col_view:
            fig_sem, stats_sem, df_particles = analyze_sem_micrograph(
                sem_img,
                scale_nm_per_pixel=nm_per_px,
                min_area_px=min_area,
                min_circularity=min_circ,
                theme=selected_theme
            )
            st.pyplot(fig_sem)

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Particles Counted", f"{stats_sem['Total_Count']}")
            s2.metric("Mean Diameter", f"{stats_sem['Mean_Diameter_nm']} nm", f"± {stats_sem['Std_Diameter_nm']} nm")
            s3.metric("Median (D50)", f"{stats_sem['Median_Diameter_nm']} nm")
            s4.metric("D10 / D90 Span", f"{stats_sem['D10_nm']} / {stats_sem['D90_nm']} nm")

            st.markdown("#### 📥 Publication Export Center")
            zip_bytes_sem = build_analysis_bundle_zip(
                fig_sem,
                base_name="SEM_Particle_Sizing",
                labplot_df=df_particles,
                summary_data=df_particles,
                title="SEM Particle Morphological Sizing and Area Distribution"
            )
            st.download_button(
                "📦 Download Complete SEM Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Particle Data)",
                data=zip_bytes_sem,
                file_name="SEM_Publication_Package.zip",
                mime="application/zip"
            )

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_sem, 'png', dpi=600), file_name="SEM_600DPI.png", mime="image/png")
            with c2:
                st.download_button("Export Vector SVG", data=get_figure_bytes(fig_sem, 'svg'), file_name="SEM.svg", mime="image/svg+xml")
            with c3:
                st.download_button("Export Vector PDF", data=get_figure_bytes(fig_sem, 'pdf'), file_name="SEM.pdf", mime="application/pdf")
            with c4:
                st.download_button(
                    "LabPlot ASCII Matrix (.dat)",
                    data=get_labplot_ascii_bytes(df_particles, title="SEM Matrix"),
                    file_name="SEM_LabPlot.dat",
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
                        st.error("Parsing failed. Using benchmark.")
                        df_edx = generate_benchmark_edx_data()
                elif "smart_data" in st.session_state and st.session_state["smart_data"]['df'] is not None and st.session_state["smart_data"]['matched_tech'].startswith("5"):
                    df_edx = st.session_state["smart_data"]['df']
                else:
                    st.info("Awaiting upload. Showing benchmark.")
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
                peak_tolerance_keV=tol_edx,
                theme=selected_theme
            )
            st.pyplot(fig_edx)

            quant_edx_df = pd.DataFrame(res_edx['quantification'])
            with st.expander("📊 Elemental Quantification (wt% and at%)", expanded=True):
                st.dataframe(quant_edx_df, use_container_width=True)

            st.markdown("#### 📥 Publication Export Center")
            zip_bytes_edx = build_analysis_bundle_zip(
                fig_edx,
                base_name="EDX_Elemental_Quantification",
                labplot_df=labplot_edx,
                summary_data=quant_edx_df,
                title="EDX Spectrum and Composition Table"
            )
            st.download_button(
                "📦 Download Complete EDX Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
                data=zip_bytes_edx,
                file_name="EDX_Publication_Package.zip",
                mime="application/zip",
                key="edx_zip"
            )

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_edx, 'png', dpi=600), file_name="EDX_600DPI.png", mime="image/png", key="edx_png")
            with c2:
                st.download_button("Export Vector SVG", data=get_figure_bytes(fig_edx, 'svg'), file_name="EDX.svg", mime="image/svg+xml", key="edx_svg")
            with c3:
                st.download_button("Export Vector PDF", data=get_figure_bytes(fig_edx, 'pdf'), file_name="EDX.pdf", mime="application/pdf", key="edx_pdf")
            with c4:
                st.download_button(
                    "LabPlot ASCII Matrix (.dat)",
                    data=get_labplot_ascii_bytes(labplot_edx, title="EDX Matrix"),
                    file_name="EDX_LabPlot.dat",
                    mime="text/plain",
                    key="edx_dat"
                )
            plt.close(fig_edx)
