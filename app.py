"""
app.py - Materials Characterization & Computational Spectroscopic Analytics Hub
Executive Master Gateway: Universal File & Data Analysis, Literature Reference Databank,
and Direct Launchpad to Specialized Deep-Intelligence Studios.
Platform Owner & Lead: Dr. Deler Langenberg
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

# Page configuration
st.set_page_config(
    page_title="Materials Characterization Hub - Master Gateway",
    page_icon="🔬",
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
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.025em;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        color: #475569;
        margin-bottom: 1.4rem;
        line-height: 1.5;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 1.2rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-right: 4px;
    }
    .badge-blue { background: #e0f2fe; color: #0284c7; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-purple { background: #f3e8ff; color: #7e22ce; }
    .badge-amber { background: #fef3c7; color: #b45309; }
    .badge-dark { background: #334155; color: #f8fafc; }
    .studio-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 1.1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .studio-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .ext-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        width: 100%;
        padding: 9px 16px;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.92rem;
        border-radius: 6px;
        text-decoration: none !important;
        border: none;
        box-shadow: 0 2px 4px rgba(2, 132, 199, 0.25);
    }
    .ext-btn:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Default Cloud URLs for Dedicated Studios
STUDIO_URLS = {
    "UV-Vis": {
        "name": "UV-Vis & Photokinetics Studio",
        "icon": "☀️",
        "url": "https://delerla-uv-vis-studio.streamlit.app/",
        "local_page": "pages/4_UV_Vis_Studio.py",
        "local_port": 8505,
        "class": "Photocatalysts · Solar Perovskites · Plasmonic Nanomaterials",
        "desc": "Tauc plot optical bandgap extrapolation (Direct/Indirect Eg), Urbach defect tail energy (Eu), multi-order reaction kinetics (0th, PFO, PSO, Weber-Morris) & AIC/BIC ranking.",
        "engine": "SciPy / Inflection Tangent Extrapolation"
    },
    "XPS": {
        "name": "XPS Deep-Intelligence Studio",
        "icon": "⚡",
        "url": "https://delerla-xps-studio.streamlit.app/",
        "local_page": "pages/1_XPS_Studio.py",
        "local_port": 8502,
        "class": "MOFs (UiO-66, ZIF-8) · Halide Perovskites · Carbon Nanofibers",
        "desc": "Non-linear Voigt & Shirley baseline deconvolution, automated C 1s charge referencing (@ 284.8 eV), Pb⁰ metallic defect photolysis, and linker vacancy quantitation.",
        "engine": "lmfit Voigt / Shirley Non-Linear Least Squares"
    },
    "XRD": {
        "name": "XRD Crystallography Studio",
        "icon": "💎",
        "url": "https://delerla-xrd-studio.streamlit.app/",
        "local_page": "pages/2_XRD_Studio.py",
        "local_port": 8503,
        "class": "Nanomaterials · Thin Films · Polymorph Mixtures",
        "desc": "Cu Kα2 stripping, pseudo-Voigt profile deconvolution, Scherrer crystallite sizing (D), Williamson–Hall microstrain separation (ε), and Spurr–Myers polymorph quantification.",
        "engine": "SciPy / lmfit Multi-Peak Profiling"
    },
    "FTIR": {
        "name": "FTIR Spectroscopy Studio",
        "icon": "🧪",
        "url": "https://delerla-ftir-studio.streamlit.app/",
        "local_page": "pages/3_FTIR_Studio.py",
        "local_port": 8504,
        "class": "Polymers · MOFs · Catalysts · Biomaterials",
        "desc": "Attenuated Total Reflectance (ATR) crystal correction, AsLS / Rubberband baseline subtraction, 2nd-derivative shoulder peak discovery, and PAN stabilization cyclization index (Es).",
        "engine": "SciPy / AsLS Baseline / Lorentz Band Deconvolution"
    },
    "SEM-EDX": {
        "name": "SEM-EDX Microstructural Studio",
        "icon": "🔬",
        "url": "https://delerla-sem-edx-studio.streamlit.app/",
        "local_page": "pages/5_SEM_EDX_Studio.py",
        "local_port": 8506,
        "class": "Nanoparticles · Grains · Nanofibers · Microstructures",
        "desc": "Computer vision distance-watershed particle segmentation, Log-Normal / Weibull particle size distributions (d10, d50, d90, PDI), and EDX characteristic line elemental stoichiometry.",
        "engine": "OpenCV / scikit-image / Peak Microanalysis"
    }
}

ALL_SUPPORTED_EXTS = ["csv", "xlsx", "xls", "txt", "dat", "tsv", "ascii", "asc", "dpt", "prn", "xy", "png", "jpg", "tif", "tiff"]


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="font-size: 1.5rem;">🔬</div>
            <div>
                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Platform Owner & Lead</div>
                <div style="font-size: 1.22rem; font-weight: 800; color: #38bdf8; line-height: 1.2;">Dr. Deler Langenberg</div>
            </div>
        </div>
        <div style="font-size: 0.81rem; color: #cbd5e1; margin-top: 8px; line-height: 1.35;">
            Materials Chemistry & Computational Spectroscopic Analytics Hub
        </div>
        <div style="display: flex; gap: 6px; margin-top: 10px;">
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="text-decoration: none; background: #334155; color: #f8fafc; padding: 4px 10px; border-radius: 4px; font-size: 0.74rem; font-weight: 600;">
                ⭐ GitHub
            </a>
            <a href="mailto:delerla@yahoo.de" style="text-decoration: none; background: #0284c7; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 0.74rem; font-weight: 600;">
                ✉️ Email
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Dedicated Studio Directory")
    st.caption("1-Click launch to external standalone intelligence studios:")
    for key, studio in STUDIO_URLS.items():
        st.markdown(
            f'<a href="{studio["url"]}" target="_blank" style="display: flex; align-items: center; gap: 8px; padding: 7px 10px; margin: 3px 0; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; text-decoration: none; color: #1e293b; font-size: 0.86rem; font-weight: 600;">'
            f'{studio["icon"]} {studio["name"]}'
            f'</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    with st.expander("🇸🇦 Saudi Research Alliance", expanded=False):
        st.markdown("""
        **Cross-Institutional Reference Databank**  
        Audited benchmarks spanning **KAUST**, **KFUPM**, **KACST**, and **IAU** (`iau.edu.sa`).
        """)
        render_sidebar_saudi_quick_search()

    with st.expander("📖 Citation & Software Attribution", expanded=False):
        st.markdown("""
        If you utilize this hub in academic publications, theses, or research reports, please cite:
        ```text
        Langenberg, D. Materials Characterization & Computational 
        Spectroscopic Analytics Hub: Automated Multi-Technique 
        Deconvolution, Kinetics & Crystallite Sizing (2026).
        Repository: https://github.com/delerla/Plotting_Chemistry
        ```
        """)


# ==============================================================================
# MAIN PAGE: EXECUTIVE MASTER GATEWAY
# ==============================================================================
st.markdown('<div class="hero-title">Materials Characterization & Computational Analytics Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Executive Scientific Gateway: Universal Experimental File Triage, Comprehensive Data Analysis, Cross-Institutional Benchmarking, and Dedicated Domain Studios.</div>', unsafe_allow_html=True)

# Executive Mission Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2b48 100%); color: #f8fafc; border-radius: 10px; padding: 22px 26px; margin-bottom: 1.8rem; border: 1px solid #334155; box-shadow: 0 4px 14px rgba(0,0,0,0.15);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
        <div>
            <span class="badge" style="background:#0284c7; color:#ffffff;">MASTER SCIENTIFIC GATEWAY</span>
            <span class="badge" style="background:#16a34a; color:#ffffff;">ORIGINLAB & LABPLOT CERTIFIED</span>
            <span class="badge" style="background:#7c3aed; color:#ffffff;">SAUDI RESEARCH ALLIANCE</span>
            <h2 style="color: #38bdf8; margin: 10px 0 6px 0; font-size: 1.55rem; font-weight: 800;">
                High-Throughput Spectroscopic & Microstructural Intelligence
            </h2>
            <p style="color: #cbd5e1; font-size: 0.93rem; margin: 0; max-width: 860px; line-height: 1.5;">
                This platform serves as the central master repository for materials characterization data analysis. 
                Upload and inspect any raw experimental file below for physics auto-detection, browse cross-institutional 
                literature standards (KAUST · KFUPM · KACST · IAU), and launch dedicated domain-specific studios operating 
                in independent cloud containers with dedicated memory and machine learning models.
            </p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.06); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
            <div style="font-size: 0.70rem; text-transform: uppercase; color: #94a3b8; font-weight: 700;">Platform Owner & Lead</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #f8fafc;">Dr. Deler Langenberg</div>
            <div style="font-size: 0.78rem; color: #38bdf8; margin-top: 2px;">Computational Chemistry Specialist</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# SECTION 1: DEDICATED DOMAIN INTELLIGENCE STUDIOS (EXTERNAL LAUNCHPAD)
# ==============================================================================
st.markdown("### 🚀 Specialized Domain Intelligence Studios")
st.markdown("Each technique operates in its own **independent cloud container** with isolated high-throughput compute, dedicated machine learning models, and zero memory cross-contamination. Click **Launch Dedicated Studio** to open the external platform:")

c_row1_1, c_row1_2 = st.columns(2)

with c_row1_1:
    # Card 1: UV-Vis
    u_info = STUDIO_URLS["UV-Vis"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{u_info['icon']} {u_info['name']}</div>
            <span class="badge badge-amber">Photokinetics & Bandgap</span>
        </div>
        <div style="font-size: 0.81rem; color: #0369a1; font-weight: 600; margin-bottom: 6px;">{u_info['class']}</div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 12px;">{u_info['desc']}</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 12px;"><strong>Engine:</strong> {u_info['engine']}</div>
        <a href="{u_info['url']}" target="_blank" class="ext-btn">
            🚀 Launch Dedicated UV-Vis Studio
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Card 2: XPS
    xp_info = STUDIO_URLS["XPS"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{xp_info['icon']} {xp_info['name']}</div>
            <span class="badge badge-purple">Core-Level Voigt Deconvolution</span>
        </div>
        <div style="font-size: 0.81rem; color: #7e22ce; font-weight: 600; margin-bottom: 6px;">{xp_info['class']}</div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 12px;">{xp_info['desc']}</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 12px;"><strong>Engine:</strong> {xp_info['engine']}</div>
        <a href="{xp_info['url']}" target="_blank" class="ext-btn">
            🚀 Launch Dedicated XPS Studio
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Card 3: SEM-EDX
    s_info = STUDIO_URLS["SEM-EDX"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{s_info['icon']} {s_info['name']}</div>
            <span class="badge badge-green">Computer Vision & Sizing</span>
        </div>
        <div style="font-size: 0.81rem; color: #15803d; font-weight: 600; margin-bottom: 6px;">{s_info['class']}</div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 12px;">{s_info['desc']}</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 12px;"><strong>Engine:</strong> {s_info['engine']}</div>
        <a href="{s_info['url']}" target="_blank" class="ext-btn">
            🚀 Launch Dedicated SEM-EDX Studio
        </a>
    </div>
    """, unsafe_allow_html=True)

with c_row1_2:
    # Card 4: XRD
    x_info = STUDIO_URLS["XRD"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{x_info['icon']} {x_info['name']}</div>
            <span class="badge badge-blue">Crystallography & Microstrain</span>
        </div>
        <div style="font-size: 0.81rem; color: #0284c7; font-weight: 600; margin-bottom: 6px;">{x_info['class']}</div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 12px;">{x_info['desc']}</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 12px;"><strong>Engine:</strong> {x_info['engine']}</div>
        <a href="{x_info['url']}" target="_blank" class="ext-btn">
            🚀 Launch Dedicated XRD Studio
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Card 5: FTIR
    f_info = STUDIO_URLS["FTIR"]
    st.markdown(f"""
    <div class="studio-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">{f_info['icon']} {f_info['name']}</div>
            <span class="badge badge-dark">Vibrational Intelligence</span>
        </div>
        <div style="font-size: 0.81rem; color: #475569; font-weight: 600; margin-bottom: 6px;">{f_info['class']}</div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 12px;">{f_info['desc']}</div>
        <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 12px;"><strong>Engine:</strong> {f_info['engine']}</div>
        <a href="{f_info['url']}" target="_blank" class="ext-btn">
            🚀 Launch Dedicated FTIR Studio
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Card 6: Saudi Alliance Databank Card
    st.markdown("""
    <div class="studio-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-left: 5px solid #16a34a;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">
            🇸🇦 Saudi Research Alliance & Reference Databank
        </div>
        <div style="font-size: 0.81rem; color: #16a34a; font-weight: 600; margin-bottom: 6px;">
            KAUST · KFUPM · KACST · IAU Reference Benchmarks
        </div>
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 14px;">
            Cross-institutional data repository containing verified, publication-audited standards for MOFs (UiO-66, ZIF-8), 
            photovoltaic perovskites, and high-performance electrocatalysts with DOI citations.
        </div>
        <a href="#literature-benchmarks" class="ext-btn" style="background: #16a34a;">
            🔍 Browse Databank Below
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ==============================================================================
# SECTION 2: SMART UNIVERSAL FILE & DATA ANALYSIS STATION
# ==============================================================================
st.markdown("### 📂 Smart Universal File & Data Analysis Station")
st.markdown("""
Upload **any experimental raw data file** below. The analytical engine cleans multi-line instrument headers, 
evaluates numerical health and statistical distributions, and automatically determines the characterization 
technique using physics-based coordinate profiling.
""")

col_up, col_stat = st.columns([1.5, 1])

with col_up:
    uploaded_file = st.file_uploader(
        "Drop Experimental File (Excel, OriginLab, CSV, DAT, TXT, ASC, DPT, PRN, Images):",
        type=ALL_SUPPORTED_EXTS,
        key="master_file_uploader"
    )

with col_stat:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; font-size: 0.83rem; line-height: 1.45;">
        <strong>Supported Coordinate Profiling:</strong><br/>
        • <strong>FTIR:</strong> Wavenumbers (4000 – 400 cm⁻¹)<br/>
        • <strong>XRD:</strong> Diffraction angles 2θ (10° – 90°)<br/>
        • <strong>UV-Vis:</strong> Wavelengths (200 – 900 nm)<br/>
        • <strong>XPS:</strong> Binding energy (1200 – 0 eV)<br/>
        • <strong>SEM:</strong> Pixel micrographs & EDX spectra
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    parsed_df, parsed_img, meta = load_smart_file(raw_bytes, filename=uploaded_file.name)
    
    tech_detected = meta.get("detected_technique", "Unknown")
    confidence = meta.get("confidence", 0.0) * 100
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 14px 18px; border-radius: 8px; margin: 1rem 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #166534;">
            ✅ Auto-Detected Technique: {tech_detected} ({confidence:.0f}% confidence)
        </div>
        <div style="font-size: 0.88rem; color: #14532d; margin-top: 4px;">
            <strong>Reasoning:</strong> {meta.get('reason', 'Coordinate spectrum matched standard physics domain.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Studio Redirection Action Card
    matched_studio = None
    for k, v in STUDIO_URLS.items():
        if k.lower() in tech_detected.lower():
            matched_studio = v
            break

    if matched_studio:
        st.markdown(f"""
        <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 14px 18px; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <strong>🚀 Recommended Dedicated Studio:</strong> {matched_studio['name']}<br/>
                <span style="font-size: 0.83rem; color: #0369a1;">Deep domain models, baseline deconvolution, and specialized machine learning ready.</span>
            </div>
            <div>
                <a href="{matched_studio['url']}" target="_blank" style="display: inline-block; padding: 8px 18px; background: #0284c7; color: #ffffff !important; border-radius: 6px; text-decoration: none !important; font-weight: 700; font-size: 0.9rem;">
                    Open in {matched_studio['name']} ➔
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Inspection Tabs
    tab_data, tab_summary, tab_export = st.tabs(["📊 Cleaned Data Table", "📈 Statistical Profiling", "📦 OriginLab & LabPlot Direct Export"])

    with tab_data:
        if parsed_df is not None:
            st.markdown(f"**Cleaned Structure:** `{meta.get('rows', 0)}` rows × `{len(meta.get('columns', []))}` columns | **Format:** `{meta.get('format', 'ASCII')}`")
            st.dataframe(parsed_df, use_container_width=True)
        elif parsed_img is not None:
            st.markdown(f"**Micrograph Resolution:** `{parsed_img.shape[1]}` × `{parsed_img.shape[0]}` pixels")
            st.image(parsed_img, caption="Loaded Micrograph Preview", use_column_width=True)

    with tab_summary:
        if parsed_df is not None:
            st.markdown("##### Numerical Descriptive Statistics")
            st.dataframe(parsed_df.describe().T, use_container_width=True)
            
            st.markdown("##### Column Coordinate Health")
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
            st.markdown("##### Direct OriginLab & LabPlot Universal Exporter")
            st.caption("Convert this ingested data table directly into OriginLab-certified matrices or LabPlot files:")
            
            exp_c1, exp_c2, exp_c3 = st.columns(3)
            with exp_c1:
                dat_bytes = get_originlab_ascii_bytes(parsed_df, title=f"{tech_detected} Ingested Matrix")
                st.download_button(
                    "📊 Export OriginLab Matrix (.dat)",
                    data=dat_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_OriginLab.dat",
                    mime="text/plain",
                    use_container_width=True
                )
            with exp_c2:
                xlsx_bytes = get_originlab_excel_bytes(parsed_df, title=f"{tech_detected} Ingested Workbook")
                st.download_button(
                    "📗 Export OriginLab Workbook (.xlsx)",
                    data=xlsx_bytes,
                    file_name=f"{uploaded_file.name.split('.')[0]}_OriginLab.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with exp_c3:
                labplot_bytes = get_labplot_ascii_bytes(parsed_df, title=f"{tech_detected} LabPlot Matrix")
                st.download_button(
                    "📉 Export LabPlot Matrix (.dat)",
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
st.markdown("### 📚 Saudi Research Alliance & Global Literature Databank")
st.markdown("""
Cross-institutional audited reference benchmarks spanning **KAUST**, **KFUPM**, **KACST**, and **IAU**. 
Search benchmark literature standards, crystal structures, reaction kinetics, and stoichiometry below:
""")

render_saudi_alliance_explorer()

st.markdown("---")
st.caption("Materials Characterization & Computational Spectroscopic Analytics Hub • Lead: Dr. Deler Langenberg • Open-Source MIT License")
