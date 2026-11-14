"""
app.py - Materials Characterization & Computational Spectroscopic Analytics Hub
Master Gateway: Universal File & Data Triage, Literature Reference Databank,
and Direct Launchpad to Dedicated Domain Characterization Studios.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
import streamlit as st

from modules.export_utils import (
    PUBLICATION_PALETTES,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
    get_labplot_ascii_bytes,
)
from modules.file_parser import load_smart_file
from modules.saudi_search_ui import render_saudi_alliance_explorer, render_sidebar_saudi_quick_search
from modules.feedback_module import render_community_reviews
from modules.counter_module import (
    render_sidebar_counter,
    render_footer_counter,
    render_cross_domain_traffic_panel
)

# Page configuration
st.set_page_config(
    page_title="Materials Characterization Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Standardized Institutional Stylesheet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .inst-masthead {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #0f172a;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
    }
    .inst-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0284c7;
        margin-bottom: 0.25rem;
    }
    .inst-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
        line-height: 1.25;
        margin-bottom: 0.35rem;
    }
    .inst-subtitle {
        font-size: 0.90rem;
        color: #475569;
        line-height: 1.5;
        max-width: 920px;
        margin: 0;
    }
    .sidebar-brand {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #0f172a;
        border-radius: 5px;
        padding: 11px 13px;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.71rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #334155;
    }
    .studio-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #0f172a;
        border-radius: 6px;
        padding: 1.15rem 1.25rem;
        margin-bottom: 1rem;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .studio-card:hover {
        border-color: #94a3b8;
        border-top-color: #0284c7;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    .ext-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 7px 14px;
        background: #0f172a;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.82rem;
        border-radius: 4px;
        text-decoration: none !important;
        border: 1px solid #0f172a;
        transition: background 0.15s ease;
    }
    .ext-btn:hover {
        background: #0284c7;
        border-color: #0284c7;
        color: #ffffff !important;
    }
    .section-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.01em;
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Dedicated Cloud Studios Registry
STUDIO_URLS = {
    "UV-Vis": {
        "name": "UV-Vis & Photokinetics Studio",
        "tag": "Optical & Kinetic Modeling",
        "url": "https://delerla-uv-vis-studio.streamlit.app/",
        "local_page": "pages/4_UV_Vis_Studio.py",
        "local_port": 8505,
        "class": "Photocatalysts · Halide Perovskites · Plasmonic Systems",
        "desc": "Tauc optical bandgap extrapolation (Direct/Indirect Eg), Urbach defect tail energy (Eu), and multi-order reaction kinetics (0th, PFO, PSO, Weber-Morris) with AIC/BIC ranking.",
        "engine": "Inflection Tangent Extrapolation & Non-Linear Regression"
    },
    "XPS": {
        "name": "XPS Core-Level Studio",
        "tag": "Photoelectron Spectroscopy",
        "url": "https://delerla-xps-studio.streamlit.app/",
        "local_page": "pages/1_XPS_Studio.py",
        "local_port": 8502,
        "class": "Reticular MOFs (UiO-66, ZIF-8) · Perovskites · Carbon Nanofibers",
        "desc": "Iterative Shirley & Tougaard background subtraction, Voigt multiplet deconvolution, automated adventitious C 1s charge referencing (284.8 eV), and defect stoichiometry.",
        "engine": "Constrained Voigt & Iterative Shirley Solver"
    },
    "XRD": {
        "name": "XRD Crystallography Studio",
        "tag": "Powder Diffraction & Microstrain",
        "url": "https://delerla-xrd-studio.streamlit.app/",
        "local_page": "pages/2_XRD_Studio.py",
        "local_port": 8503,
        "class": "Crystalline Oxides · Thin Films · Polymorph Mixtures",
        "desc": "Cu Kα2 Rachinger stripping, pseudo-Voigt profile fitting, instrumental-corrected Scherrer crystallite sizing (D), Williamson–Hall microstrain (ε), and Spurr–Myers phase fraction.",
        "engine": "Pseudo-Voigt Profile & Williamson–Hall Regression"
    },
    "FTIR": {
        "name": "FTIR Spectroscopy Studio",
        "tag": "Vibrational Spectroscopy",
        "url": "https://delerla-ftir-studio.streamlit.app/",
        "local_page": "pages/3_FTIR_Studio.py",
        "local_port": 8504,
        "class": "Polymers (PAN) · Coordination Frameworks · Oxide Catalysts",
        "desc": "ATR penetration-depth correction, AsLS & convex-hull rubberband baselines, Savitzky–Golay 2nd-derivative hidden band discovery, and quantitative ROI band integration.",
        "engine": "AsLS Penalized Least Squares & Lorentzian/Gaussian Fitting"
    },
    "SEM-EDX": {
        "name": "SEM-EDX Microstructural Studio",
        "tag": "Electron Microscopy & EDX",
        "url": "https://delerla-sem-edx-studi.streamlit.app/",
        "local_page": "pages/5_SEM_EDX_Studio.py",
        "local_port": 8506,
        "class": "Nanoparticles · Polycrystalline Grains · Electrospun Fibers",
        "desc": "Distance-transform watershed micrograph segmentation, Log-Normal & Weibull size distributions (d10, d50, d90, PDI), and EDX characteristic X-ray line stoichiometry.",
        "engine": "Euclidean Distance Watershed & ZAF-Corrected Peak Ratios"
    }
}

ALL_SUPPORTED_EXTS = ["csv", "xlsx", "xls", "txt", "dat", "tsv", "ascii", "asc", "dpt", "prn", "xy", "png", "jpg", "tif", "tiff"]


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #0284c7; font-weight: 700;">Central Platform</div>
        <div style="font-size: 1.02rem; font-weight: 700; color: #0f172a; margin-top: 2px;">Materials Characterization Hub</div>
        <div style="font-size: 0.77rem; color: #64748b; margin-top: 4px; line-height: 1.35;">
            Multi-Technique Spectroscopic &amp; Microstructural Analytics Suite
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### Analytical Modules")
    for key, studio in STUDIO_URLS.items():
        st.markdown(
            f'<a href="{studio["url"]}" target="_blank" style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; margin: 3px 0; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; text-decoration: none; color: #1e293b; font-size: 0.80rem; font-weight: 600;">'
            f'<span>{studio["name"]}</span>'
            f'<span style="color: #64748b; font-size: 0.75rem;">↗</span>'
            f'</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    with st.expander("Saudi Research Alliance Databank", expanded=False):
        st.caption("Cross-institutional reference standards (KAUST, KFUPM, KACST, IAU).")
        render_sidebar_saudi_quick_search()

    with st.expander("Repository & Documentation", expanded=False):
        st.markdown("""
        - **Source Code:** [GitHub Repository](https://github.com/delerla/Plotting_Chemistry)
        - **Export Formats:** OriginLab (`.dat`, `.xlsx`), LabPlot (`.dat`), 600 DPI PNG/SVG/PDF
        - **License:** MIT Open-Source
        """)

    # Domain Telemetry Counter
    render_sidebar_counter("master_hub")


# ==============================================================================
# MAIN PAGE: INSTITUTIONAL MASTHEAD
# ==============================================================================
st.markdown("""
<div class="inst-masthead">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <div class="inst-eyebrow">COMPUTATIONAL MATERIALS CHARACTERIZATION SUITE</div>
            <div class="inst-title">Materials Characterization &amp; Spectroscopic Analytics Hub</div>
            <p class="inst-subtitle">
                Standardized analytical gateway for experimental file triage, physics-based coordinate validation, 
                cross-institutional literature benchmarking (KAUST · KFUPM · KACST · IAU), and dedicated characterization studios.
            </p>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
            <span class="badge">OriginLab &amp; LabPlot Ready</span>
            <span class="badge">600 DPI Vector Export</span>
            <span class="badge">Saudi Research Alliance</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# SECTION 1: DEDICATED CHARACTERIZATION STUDIOS
# ==============================================================================
st.markdown('<div class="section-heading">1. Dedicated Characterization Studios</div>', unsafe_allow_html=True)
st.caption("Each characterization technique operates in an isolated cloud environment with domain-specific baseline, deconvolution, and kinetic solvers.")

c_row1_1, c_row1_2 = st.columns(2)

with c_row1_1:
    # Module 1: UV-Vis
    u_info = STUDIO_URLS["UV-Vis"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{u_info['name']}</div>
            <span class="badge">{u_info['tag']}</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{u_info['class']}</div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">{u_info['desc']}</div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Solver:</strong> {u_info['engine']}</div>
        <a href="{u_info['url']}" target="_blank" class="ext-btn">
            Open UV-Vis Studio →
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Module 2: XPS
    xp_info = STUDIO_URLS["XPS"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{xp_info['name']}</div>
            <span class="badge">{xp_info['tag']}</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{xp_info['class']}</div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">{xp_info['desc']}</div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Solver:</strong> {xp_info['engine']}</div>
        <a href="{xp_info['url']}" target="_blank" class="ext-btn">
            Open XPS Studio →
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Module 3: SEM-EDX
    s_info = STUDIO_URLS["SEM-EDX"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{s_info['name']}</div>
            <span class="badge">{s_info['tag']}</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{s_info['class']}</div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">{s_info['desc']}</div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Solver:</strong> {s_info['engine']}</div>
        <a href="{s_info['url']}" target="_blank" class="ext-btn">
            Open SEM-EDX Studio →
        </a>
    </div>
    """, unsafe_allow_html=True)

with c_row1_2:
    # Module 4: XRD
    x_info = STUDIO_URLS["XRD"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{x_info['name']}</div>
            <span class="badge">{x_info['tag']}</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{x_info['class']}</div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">{x_info['desc']}</div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Solver:</strong> {x_info['engine']}</div>
        <a href="{x_info['url']}" target="_blank" class="ext-btn">
            Open XRD Studio →
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Module 5: FTIR
    f_info = STUDIO_URLS["FTIR"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{f_info['name']}</div>
            <span class="badge">{f_info['tag']}</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{f_info['class']}</div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">{f_info['desc']}</div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Solver:</strong> {f_info['engine']}</div>
        <a href="{f_info['url']}" target="_blank" class="ext-btn">
            Open FTIR Studio →
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Module 6: Saudi Alliance Reference Databank
    st.markdown("""
    <div class="studio-card" style="border-top-color: #0284c7; background: #f8fafc;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">Saudi Research Alliance Databank</div>
            <span class="badge">Reference Standards</span>
        </div>
        <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">
            KAUST · KFUPM · KACST · IAU (iau.edu.sa)
        </div>
        <div style="font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 10px;">
            Cross-institutional reference library containing audited peak positions, Bragg reflections, binding energies, and DOI citations across key national research pillars.
        </div>
        <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 12px;"><strong>Coverage:</strong> XPS Core Levels · XRD Reflections · FTIR Modes</div>
        <a href="#literature-benchmarks" class="ext-btn" style="background: #0284c7; border-color: #0284c7;">
            Browse Reference Databank ↓
        </a>
    </div>
    """, unsafe_allow_html=True)

# Cross-Domain Multi-Technique Traffic Analytics Panel
render_cross_domain_traffic_panel()

st.markdown("---")


# ==============================================================================
# SECTION 2: UNIVERSAL EXPERIMENTAL FILE TRIAGE & DATA VALIDATION
# ==============================================================================
st.markdown('<div class="section-heading">2. Universal Experimental File Triage &amp; Format Converter</div>', unsafe_allow_html=True)
st.caption("Upload raw instrument files to strip multi-line headers, evaluate numerical health, auto-detect the characterization domain, and convert directly into OriginLab or LabPlot matrices.")

col_up, col_stat = st.columns([1.5, 1])

with col_up:
    uploaded_file = st.file_uploader(
        "Select Experimental Data File (CSV, XLSX, DAT, TXT, ASC, DPT, PRN, XY, TIFF/PNG):",
        type=ALL_SUPPORTED_EXTS,
        key="master_file_uploader"
    )

with col_stat:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 14px; font-size: 0.80rem; color: #334155; line-height: 1.5;">
        <strong style="color: #0f172a;">Coordinate Auto-Detection Domains:</strong><br/>
        • <strong>FTIR:</strong> Wavenumber domain (4000 – 400 cm⁻¹)<br/>
        • <strong>XRD:</strong> Diffraction angle 2θ (5° – 90°)<br/>
        • <strong>UV-Vis:</strong> Optical wavelength (190 – 1100 nm)<br/>
        • <strong>XPS:</strong> Photoelectron binding energy (1200 – 0 eV)<br/>
        • <strong>SEM-EDX:</strong> Grayscale micrographs &amp; keV spectra
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    parsed_df, parsed_img, meta = load_smart_file(raw_bytes, filename=uploaded_file.name)
    
    tech_detected = meta.get("detected_technique", "Unknown")
    confidence = meta.get("confidence", 0.0) * 100
    
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #0284c7; padding: 12px 16px; border-radius: 6px; margin: 0.8rem 0;">
        <div style="font-size: 0.98rem; font-weight: 700; color: #0f172a;">
            Detected Technique: {tech_detected} ({confidence:.0f}% confidence)
        </div>
        <div style="font-size: 0.83rem; color: #475569; margin-top: 3px;">
            <strong>Diagnostic:</strong> {meta.get('reason', 'Coordinate domain matched standard physical bounds.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    matched_studio = None
    for k, v in STUDIO_URLS.items():
        if k.lower() in tech_detected.lower():
            matched_studio = v
            break

    if matched_studio:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <strong style="color: #0f172a; font-size: 0.88rem;">Recommended Analytical Module: {matched_studio['name']}</strong><br/>
                <span style="font-size: 0.80rem; color: #64748b;">Specialized baseline subtraction, peak deconvolution, and domain presets available.</span>
            </div>
            <div>
                <a href="{matched_studio['url']}" target="_blank" style="display: inline-block; padding: 6px 14px; background: #0f172a; color: #ffffff !important; border-radius: 4px; text-decoration: none !important; font-weight: 600; font-size: 0.82rem;">
                    Open {matched_studio['name']} →
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    tab_data, tab_summary, tab_export = st.tabs(["Cleaned Data Table", "Statistical Profiling", "OriginLab & LabPlot Export"])

    with tab_data:
        if parsed_df is not None:
            st.markdown(f"**Dimensions:** `{meta.get('rows', 0)}` rows × `{len(meta.get('columns', []))}` columns | **Source Format:** `{meta.get('format', 'ASCII')}`")
            st.dataframe(parsed_df, use_container_width=True)
        elif parsed_img is not None:
            st.markdown(f"**Micrograph Resolution:** `{parsed_img.shape[1]}` × `{parsed_img.shape[0]}` px")
            st.image(parsed_img, caption="Loaded Micrograph Preview", use_column_width=True)

    with tab_summary:
        if parsed_df is not None:
            st.markdown("##### Descriptive Statistics")
            st.dataframe(parsed_df.describe().T, use_container_width=True)
            
            st.markdown("##### Column Coordinate Integrity")
            health_rows = []
            for col in parsed_df.columns:
                series = pd.to_numeric(parsed_df[col], errors='coerce')
                health_rows.append({
                    "Column": col,
                    "Data Type": str(parsed_df[col].dtype),
                    "Finite Values": int(series.notna().sum()),
                    "Missing / NaN": int(series.isna().sum()),
                    "Min Value": float(series.min()) if series.notna().any() else np.nan,
                    "Max Value": float(series.max()) if series.notna().any() else np.nan,
                })
            st.dataframe(pd.DataFrame(health_rows), use_container_width=True)

    with tab_export:
        if parsed_df is not None:
            st.markdown("##### Direct OriginLab & LabPlot Matrix Converter")
            st.caption("Export the sanitized data table with 4-tier OriginLab headers or LabPlot metadata:")
            
            exp_c1, exp_c2, exp_c3 = st.columns(3)
            with exp_c1:
                dat_bytes = get_originlab_ascii_bytes(parsed_df, title=f"{tech_detected} Ingested Matrix")
                st.download_button(
                    "Export OriginLab Matrix (.dat)",
                    data=dat_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_OriginLab.dat",
                    mime="text/plain",
                    use_container_width=True
                )
            with exp_c2:
                xlsx_bytes = get_originlab_excel_bytes(parsed_df, title=f"{tech_detected} Ingested Workbook")
                st.download_button(
                    "Export OriginLab Workbook (.xlsx)",
                    data=xlsx_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_OriginLab.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with exp_c3:
                labplot_bytes = get_labplot_ascii_bytes(parsed_df, title=f"{tech_detected} LabPlot Matrix")
                st.download_button(
                    "Export LabPlot Matrix (.dat)",
                    data=labplot_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_LabPlot.dat",
                    mime="text/plain",
                    use_container_width=True
                )

st.markdown("---")


# ==============================================================================
# SECTION 3: SAUDI RESEARCH ALLIANCE & LITERATURE BENCHMARKS
# ==============================================================================
st.markdown('<div id="literature-benchmarks"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">3. Cross-Institutional Reference &amp; Literature Databank</div>', unsafe_allow_html=True)
st.caption("Search audited spectroscopic and crystallographic reference benchmarks across KAUST, KFUPM, KACST, and IAU.")

render_saudi_alliance_explorer()

# ==============================================================================
# SECTION 4: USER REVIEWS, COMMUNITY FEEDBACK & WISHLIST
# ==============================================================================
render_community_reviews("Materials Characterization Master Hub")

# ==============================================================================
# STANDARDIZED SINGLE ATTRIBUTION FOOTER
# ==============================================================================
st.markdown("---")
c_foot1, c_foot2 = st.columns([3, 1])
with c_foot1:
    st.caption("Materials Characterization & Spectroscopic Analytics Hub • © 2026 Dr. Deler Langenberg • MIT Open-Source License")
with c_foot2:
    render_footer_counter("master_hub")
