"""
app_xps.py - XPS Studio: Dedicated Materials-Specific XPS Intelligence Platform
Authored & Maintained by Dr. Deler Langenberg (2026)
Specialized for: MOFs, Solar Perovskites, PAN Nanofibers, and Catalysts.
"""

import sys
from pathlib import Path

# Add root project directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.export_utils import (
    PUBLICATION_PALETTES,
    build_analysis_bundle_zip,
    get_figure_bytes,
    get_labplot_ascii_bytes,
)
from modules.file_parser import sanitize_spectral_dataframe, load_smart_file
from xps_studio.knowledge_base import ALL_DOMAINS
from xps_studio.knowledge_base.benchmark_data import (
    generate_benchmark_mof_c1s,
    generate_benchmark_solar_pb4f,
    generate_benchmark_pan_n1s,
)
from xps_studio.core.calibration import apply_charge_calibration, CALIBRATION_STANDARDS
from xps_studio.core.background import extract_net_signal
from xps_studio.core.deconvolution import fit_xps_components
from xps_studio.core.interpretation import interpret_xps_chemistry
from xps_studio.visualizer.plot_core_level import render_core_level_plot

# Page Configuration
st.set_page_config(
    page_title="XPS Studio - Dr. Deler Langenberg",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .xps-header {
        font-size: 1.95rem;
        font-weight: 800;
        color: #0f2b48;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 1.2rem;
        border: 1px solid #334155;
    }
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 12px;
        margin-bottom: 12px;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 6px;
        color: #92400e;
        margin-top: 8px;
        font-size: 0.90rem;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.74rem;
        font-weight: 600;
    }
    .badge-dark { background: #1e293b; color: #f8fafc; }
    .badge-blue { background: #e0f2fe; color: #0284c7; }
    .badge-green { background: #dcfce7; color: #16a34a; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR: DOMAIN SELECTION & PARAMETERS
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Platform Owner & Lead</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #38bdf8;">Dr. Deler Langenberg</div>
        <div style="font-size: 0.81rem; color: #cbd5e1; margin-top: 4px;">
            XPS Intelligence Engine & Computational Spectroscopy
        </div>
        <div style="display: flex; gap: 6px; margin-top: 10px;">
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="text-decoration: none; background: #334155; color: #f8fafc; padding: 4px 10px; border-radius: 4px; font-size: 0.74rem; font-weight: 600;">⭐ GitHub</a>
            <a href="mailto:delerla@yahoo.de" style="text-decoration: none; background: #0284c7; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 0.74rem; font-weight: 600;">✉️ Email</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏛️ Target Materials Domain")
    selected_domain = st.selectbox(
        "Select Field of Study:",
        list(ALL_DOMAINS.keys()),
        index=0,
        help="Loads dedicated chemical knowledge, spin-orbit rules, and defect metrics for your target material."
    )

    domain_presets = ALL_DOMAINS[selected_domain]
    preset_names = list(domain_presets.keys())
    selected_preset_name = st.selectbox("Spectral Chemistry Preset:", preset_names)
    active_preset = domain_presets[selected_preset_name]

    st.markdown("---")
    st.markdown("### 🎨 Editorial Styling")
    selected_theme = st.selectbox(
        "Journal Color Palette:",
        list(PUBLICATION_PALETTES.keys()),
        index=2
    )

    st.markdown("---")
    with st.expander("📖 Citation & Attribution", expanded=False):
        st.markdown("""
        ```bibtex
        @software{langenberg_xps_studio_2026,
          author    = {Dr. Deler Langenberg},
          title     = {XPS Studio: Materials-Specific Spectroscopic Intelligence Hub},
          year      = {2026},
          publisher = {GitHub},
          url       = {https://github.com/delerla/Plotting_Chemistry}
        }
        ```
        **Lead Author:** Dr. Deler Langenberg  
        **Contact:** [delerla@yahoo.de](mailto:delerla@yahoo.de)  
        **License:** MIT Open-Source
        """)

# ==============================================================================
# MAIN PAGE HEADER & BRANDING
# ==============================================================================
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 10px;">
    <div>
        <div class="xps-header">⚡ XPS Studio: High-Resolution Core-Level Intelligence</div>
        <div style="font-size: 0.90rem; color: #475569;">
            Physics-constrained Voigt deconvolution, Shirley baseline, and automated chemical state reasoning.
        </div>
    </div>
    <div style="display: flex; gap: 4px; align-items: center;">
        <span class="badge badge-dark">Lead: Dr. Deler Langenberg</span>
        <span class="badge badge-blue">Domain-Trained Engine</span>
        <span class="badge badge-green">MIT License</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA INGESTION & CHARGE CALIBRATION CONTROLS
# ==============================================================================
col_ctrl, col_plot = st.columns([1, 2.3])

with col_ctrl:
    st.subheader("Data & Calibration")
    data_source = st.radio(
        "Data Source:",
        ["Load Domain Benchmark", "Upload Experimental Data (ASCII/CSV/Excel)"],
        key="xps_src"
    )

    if data_source == "Load Domain Benchmark":
        if "mof" in selected_preset_name.lower():
            raw_df = generate_benchmark_mof_c1s()
        elif "perovskite" in selected_preset_name.lower() or "pb" in selected_preset_name.lower():
            raw_df = generate_benchmark_solar_pb4f()
        elif "pan" in selected_preset_name.lower() or "nitrile" in selected_preset_name.lower():
            raw_df = generate_benchmark_pan_n1s()
        else:
            raw_df = generate_benchmark_mof_c1s()
        st.success(f"Loaded benchmark for: **{selected_preset_name}**")
    else:
        uploaded_file = st.file_uploader(
            "Upload XPS Spectrum (Col 1: Binding Energy, Col 2: Counts/s):",
            type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "prn"],
            key="xps_file_up"
        )
        if uploaded_file is not None:
            parsed_df, _, meta = load_smart_file(uploaded_file.read(), filename=uploaded_file.name)
            if parsed_df is not None and not parsed_df.empty:
                raw_df = parsed_df
                st.success(f"Parsed {meta['rows']} points from {uploaded_file.name}")
            else:
                st.error("Failed to parse file. Falling back to benchmark.")
                raw_df = generate_benchmark_mof_c1s()
        else:
            st.info("Awaiting upload. Showing domain benchmark.")
            raw_df = generate_benchmark_mof_c1s()

    # Column selector if multiple columns exist
    clean_df = sanitize_spectral_dataframe(raw_df)
    if clean_df.shape[1] > 2:
        be_col = st.selectbox("Binding Energy Column (X):", clean_df.columns, index=0)
        cps_col = st.selectbox("Intensity / Counts Column (Y):", [c for c in clean_df.columns if c != be_col], index=0)
        df_xps = clean_df[[be_col, cps_col]]
    else:
        df_xps = clean_df

    x_raw = df_xps.iloc[:, 0].to_numpy().astype(float)
    y_raw = df_xps.iloc[:, 1].to_numpy().astype(float)

    st.markdown("#### ⚖️ Charge Calibration")
    calib_mode = st.selectbox(
        "Calibration Standard:",
        list(CALIBRATION_STANDARDS.keys()),
        index=0
    )
    manual_offset = st.number_input("Manual ΔE Offset (eV):", value=0.00, step=0.05, format="%.2f")

    x_calib, shift_applied, calib_status = apply_charge_calibration(
        x_raw, y_raw, method=calib_mode, manual_shift_eV=manual_offset
    )
    st.caption(f"⚡ {calib_status}")

    st.markdown("#### 📉 Baseline Subtraction")
    baseline_method = st.selectbox("Inelastic Background Method:", ["Shirley (Iterative)", "Linear"], index=0)
    bg_curve, y_net = extract_net_signal(x_calib, y_raw, baseline_type="Linear" if "Linear" in baseline_method else "Shirley")

    st.markdown("#### 🔬 Deconvolution Parameters")
    n_fev = st.slider("Optimization Iteration Limit:", min_value=1000, max_value=8000, value=4000, step=500)

# ==============================================================================
# DECONVOLUTION EXECUTION & INTERPRETATION
# ==============================================================================
with col_plot:
    components_cfg = active_preset.get('components', [])
    doublet_info = {
        'is_doublet': active_preset.get('is_doublet', False),
        'doublet_delta_eV': active_preset.get('doublet_delta_eV', 0.0),
        'branching_ratio': active_preset.get('branching_ratio', 1.0)
    }

    try:
        fit_result, comp_curves, comp_summary, r2 = fit_xps_components(
            x_calib, y_net, components_cfg, doublet_info=doublet_info, max_nfev=n_fev
        )

        fig_xps, labplot_df = render_core_level_plot(
            x_calib, y_raw, bg_curve, fit_result, comp_curves, comp_summary,
            core_label=active_preset.get('core_level', 'XPS'),
            theme=selected_theme
        )
        st.pyplot(fig_xps)

        # ----------------------------------------------------------------------
        # AUTOMATED SCIENTIFIC INTERPRETATION & DEFECT ANALYSIS CARD
        # ----------------------------------------------------------------------
        interp_results = interpret_xps_chemistry(
            comp_summary, preset_dict=active_preset, core_level=active_preset.get('core_level', 'C 1s')
        )

        st.markdown("### 🧠 Automated Chemical Reasoning & Defect Report")
        
        # Display key computed metrics
        if interp_results['metrics']:
            metric_cols = st.columns(len(interp_results['metrics']))
            for idx, (m_key, m_val) in enumerate(interp_results['metrics'].items()):
                with metric_cols[idx]:
                    st.metric(
                        label=m_val['name'],
                        value=f"{m_val['value']:.2f} {m_val['unit']}".strip()
                    )

        # Insights narrative
        if interp_results['insights']:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            for ins in interp_results['insights']:
                st.markdown(f"**✓ Insight:** {ins}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Warnings / Defect flags
        if interp_results['warnings']:
            for w in interp_results['warnings']:
                st.markdown(f'<div class="warning-box">⚠️ <b>Defect Notice:</b> {w}</div>', unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # DECONVOLUTION NUMERICAL QUANTIFICATION TABLE
        # ----------------------------------------------------------------------
        with st.expander("📊 Detailed Voigt Component Metrics & Peak Properties", expanded=True):
            table_rows = []
            for name, d in comp_summary.items():
                table_rows.append({
                    "Chemical State": name,
                    "Binding Energy (eV)": d['Binding_Energy_eV'],
                    "FWHM (eV)": d['FWHM_eV'],
                    "Area (Counts·eV)": d['Area_cps_eV'],
                    "Area Fraction (%)": f"{d['Area_Percent']:.1f}%",
                    "Chemical Assignment": d['Meaning']
                })
            quant_df = pd.DataFrame(table_rows)
            st.dataframe(quant_df, use_container_width=True)

        # ----------------------------------------------------------------------
        # PUBLICATION EXPORT CENTER
        # ----------------------------------------------------------------------
        st.markdown("#### 📥 Publication Export Center (600 DPI & LabPlot Interoperable)")
        zip_bytes = build_analysis_bundle_zip(
            fig_xps,
            base_name=f"XPS_{selected_preset_name.replace(' ', '_').replace('/', '_')}",
            labplot_df=labplot_df,
            summary_data=quant_df,
            title=f"XPS Analysis: {selected_preset_name}",
            units={'Binding_Energy_eV': 'eV', 'Experimental_CPS': 'Counts/s'}
        )
        st.download_button(
            "📦 Download Complete XPS Publication Package (.ZIP: 600 DPI PNG, SVG, PDF, LabPlot .DAT, Report)",
            data=zip_bytes,
            file_name=f"XPS_{selected_preset_name.replace(' ', '_')}_Package.zip",
            mime="application/zip",
            key="dl_xps_zip"
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("Export 600 DPI PNG", data=get_figure_bytes(fig_xps, 'png', dpi=600), file_name="XPS_600DPI.png", mime="image/png", key="xps_png")
        with c2:
            st.download_button("Export Vector SVG", data=get_figure_bytes(fig_xps, 'svg'), file_name="XPS.svg", mime="image/svg+xml", key="xps_svg")
        with c3:
            st.download_button("Export Vector PDF", data=get_figure_bytes(fig_xps, 'pdf'), file_name="XPS.pdf", mime="application/pdf", key="xps_pdf")
        with c4:
            st.download_button(
                "LabPlot ASCII Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_df, title="XPS LabPlot Matrix"),
                file_name="XPS_LabPlot.dat",
                mime="text/plain",
                key="xps_dat"
            )

        plt.close(fig_xps)

    except Exception as e:
        st.error(f"Deconvolution Optimization Error: {e}")

# ==============================================================================
# INSTITUTIONAL FOOTER
# ==============================================================================
st.markdown("""
<div style="margin-top: 4.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.84rem; line-height: 1.65;">
    <strong>XPS Studio</strong> • High-Resolution Core-Level Photoelectron Spectroscopy Intelligence<br>
    Engineered & Maintained by <strong>Dr. Deler Langenberg</strong> • 
    <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 600;">GitHub Repository</a> • 
    <a href="mailto:delerla@yahoo.de" style="color: #0284c7; text-decoration: none; font-weight: 600;">Contact: delerla@yahoo.de</a><br>
    <small style="color: #94a3b8;">Calibrated for 600 DPI raster, vector formats, and LabPlot ASCII tables. © 2026 Dr. Deler Langenberg (MIT License).</small>
</div>
""", unsafe_allow_html=True)
