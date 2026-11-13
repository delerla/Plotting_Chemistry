"""
sem_edx_studio.app_sem_edx
Flagship Dedicated Streamlit Application for Scanning Electron Microscopy (SEM) Particle Sizing,
Computer Vision Morphological Segmentation, and EDX Elemental Microanalysis.
Lead: Dr. Deler Langenberg
"""

import sys
from pathlib import Path

# Setup module path
ROOT_DIR = Path(__file__).resolve().parent.parent
STUDIO_DIR = Path(__file__).resolve().parent

for p in (str(STUDIO_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from sem_edx_studio.knowledge_base.benchmarks import (
    SEM_EDX_DOMAINS,
    generate_uio66_micrograph,
    generate_perovskite_grains_micrograph,
    generate_uio66_edx_spectrum,
    generate_mapbi3_edx_spectrum
)
from sem_edx_studio.core.segmentation import segment_micrograph
from sem_edx_studio.core.distribution import fit_size_distributions
from sem_edx_studio.core.edx_analysis import analyze_edx_spectrum
from sem_edx_studio.visualizer.plot_micrograph import render_micrograph_overlay_plot
from sem_edx_studio.visualizer.plot_distribution import render_size_distribution_plot
from sem_edx_studio.visualizer.plot_edx import render_edx_publication_plot
from sem_edx_studio.modules.export_utils import (
    PUBLICATION_PALETTES,
    get_figure_bytes,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
    get_labplot_ascii_bytes,
    build_analysis_bundle_zip
)
from sem_edx_studio.modules.file_parser import load_smart_file

# Page Configuration
st.set_page_config(
    page_title="SEM-EDX Studio - Dr. Deler Langenberg",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .sem-header {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 1.2rem;
        border: 1px solid #334155;
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
    .badge-dark { background: #334155; color: #f8fafc; }
    .badge-blue { background: #e0f2fe; color: #0284c7; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-amber { background: #fef3c7; color: #b45309; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="font-size: 1.5rem;">🔬</div>
            <div>
                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Dedicated Studio</div>
                <div style="font-size: 1.18rem; font-weight: 800; color: #38bdf8; line-height: 1.2;">Dr. Deler Langenberg</div>
            </div>
        </div>
        <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 8px; line-height: 1.35;">
            SEM Electron Microscopy & EDX Elemental Microanalysis Suite
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

    st.markdown("### 🎯 Investigation Domain")
    domain_names = list(SEM_EDX_DOMAINS.keys())
    selected_domain = st.selectbox("Scientific Benchmark / Domain:", domain_names, index=0)
    domain_meta = SEM_EDX_DOMAINS[selected_domain]

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin-bottom: 1rem; font-size: 0.83rem; line-height: 1.4;">
        <strong>Target Class:</strong> {domain_meta['material_class']}<br/>
        <strong>Morphology:</strong> {domain_meta['morphology']}<br/>
        <strong>Audited Reference:</strong> {domain_meta['reference']}
    </div>
    """, unsafe_allow_html=True)

    analysis_mode = st.radio(
        "Analysis Workflow:",
        ["1. SEM Micrograph Segmentation & Sizing", "2. Particle Size Statistical Distribution", "3. EDX Elemental Microanalysis & Stoichiometry"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🎨 Publication Typography & Style")
    selected_theme = st.selectbox("Journal Palette:", list(PUBLICATION_PALETTES.keys()), index=2)
    selected_font_size = st.slider("Typography Font Size (pt):", min_value=9, max_value=18, value=12)
    fig_width = st.slider("Figure Width (in):", min_value=8.0, max_value=16.0, value=12.0, step=0.5)
    fig_height = st.slider("Figure Height (in):", min_value=4.0, max_value=8.0, value=5.5, step=0.5)

    st.markdown("---")
    with st.expander("📖 Citation Attribution", expanded=False):
        st.markdown("""
        **Lead Author:** Dr. Deler Langenberg  
        **Contact:** [delerla@yahoo.de](mailto:delerla@yahoo.de)  
        **Repository:** [Plotting_Chemistry](https://github.com/delerla/Plotting_Chemistry)
        """)


# ==============================================================================
# MAIN WORKSPACE HEADER & RETURN LINK
# ==============================================================================
try:
    st.page_link("app.py", label="← Return to Materials Characterization Master Gateway", icon="🏠")
except Exception:
    st.markdown('<a href="https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding: 7px 16px; margin-bottom: 12px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #38bdf8 !important; border: 1px solid #334155; border-radius: 6px; text-decoration: none !important; font-weight: 600; font-size: 0.88rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏠 ⟵ Return to Master Materials Characterization Gateway</a>', unsafe_allow_html=True)

st.markdown('<div class="sem-header">🔬 SEM-EDX Studio: Microstructural & Elemental Intelligence</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom: 1.0rem;">
    <span class="badge badge-dark">{selected_domain}</span>
    <span class="badge badge-blue">{domain_meta['material_class']}</span>
    <span class="badge badge-green">Zero-Barrier Export • OriginLab Ready</span>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# DATA INGESTION & CONTROLS
# ==============================================================================
col_ctrl, col_view = st.columns([1, 2.6])

with col_ctrl:
    st.subheader("Data & Parameters")
    
    if analysis_mode.startswith("1") or analysis_mode.startswith("2"):
        data_source = st.radio("Micrograph Source:", ["Curated Benchmark Micrograph", "Upload Image (PNG, JPG, TIFF)"], key="sem_src")
        
        if data_source == "Curated Benchmark Micrograph":
            if "Perovskite" in selected_domain:
                sem_img = generate_perovskite_grains_micrograph()
            else:
                sem_img = generate_uio66_micrograph()
            st.success(f"Ingested benchmark image: {sem_img.shape[1]}x{sem_img.shape[0]} px.")
        else:
            up_img = st.file_uploader("Upload SEM Micrograph", type=["png", "jpg", "jpeg", "tif", "tiff"])
            if up_img is not None:
                file_bytes = np.asarray(bytearray(up_img.read()), dtype=np.uint8)
                sem_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                st.success(f"Loaded {up_img.name}: {sem_img.shape[1]}x{sem_img.shape[0]} px.")
            else:
                sem_img = generate_uio66_micrograph()
                st.info("No file uploaded yet. Showing default benchmark image.")

        st.markdown("#### 📏 Spatial Calibration")
        scale_val = st.number_input("Spatial Scale (nm per pixel):", min_value=0.01, max_value=500.0, value=12.5, step=0.5)
        seg_method = st.selectbox("Segmentation Algorithm:", ["Otsu", "Adaptive"], index=0)
        use_watershed = st.checkbox("Apply Distance Watershed Separation", value=True)
        min_px = st.slider("Min Particle Size (px):", min_value=5, max_value=200, value=25)

    else:
        edx_source = st.radio("EDX Data Source:", ["Curated Benchmark Spectrum", "Upload File (CSV, DAT, TXT, Excel)"], key="edx_src")
        if edx_source == "Curated Benchmark Spectrum":
            if "Perovskite" in selected_domain:
                df_edx = generate_mapbi3_edx_spectrum()
            else:
                df_edx = generate_uio66_edx_spectrum()
            st.success(f"Ingested benchmark EDX spectrum: {df_edx.shape[0]} energy channels.")
        else:
            up_edx = st.file_uploader("Upload EDX Spectrum", type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "dpt"])
            if up_edx is not None:
                raw_b = up_edx.getvalue()
                df_edx, _ = load_smart_file(raw_b, up_edx.name)
                st.success(f"Parsed {up_edx.name}: {df_edx.shape[0]} channels.")
            else:
                df_edx = generate_uio66_edx_spectrum()
                st.info("No file uploaded. Showing default benchmark EDX.")

        st.markdown("#### ⚡ Peak Sensitivity")
        edx_prom = st.slider("Peak Prominence (Counts):", min_value=20.0, max_value=500.0, value=75.0, step=5.0)

    st.markdown("---")


# ==============================================================================
# WORKFLOW EXECUTION
# ==============================================================================
with col_view:
    # -------------------------------------------------------------
    # WORKFLOW 1: MICROGRAPH SEGMENTATION OVERLAY
    # -------------------------------------------------------------
    if analysis_mode.startswith("1"):
        seg_res = segment_micrograph(
            image=sem_img,
            scale_nm_per_px=scale_val,
            method=seg_method,
            min_area_px=min_px,
            apply_watershed=use_watershed
        )

        fig, _ = render_micrograph_overlay_plot(
            raw_img=sem_img,
            overlay_rgb=seg_res["overlay_rgb"],
            scale_nm_per_px=scale_val,
            font_size=selected_font_size,
            fig_size=(fig_width, fig_height)
        )
        st.pyplot(fig)

        df_particles = seg_res["df_particles"]
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        s_col1.metric("Particles Detected", seg_res["n_particles"])
        if not df_particles.empty:
            mean_d = df_particles["Diameter_nm"].mean()
            mean_asp = df_particles["Aspect_Ratio"].mean()
            mean_sph = df_particles["Sphericity"].mean()
            s_col2.metric("Mean Diameter", f"{mean_d:.1f} nm")
            s_col3.metric("Mean Aspect Ratio", f"{mean_asp:.2f}")
            s_col4.metric("Mean Sphericity", f"{mean_sph:.2f}")

            with st.expander("📋 Morphological Particle Metrics Table", expanded=False):
                st.dataframe(df_particles, use_container_width=True)

        active_export_df = df_particles
        active_summary = f"""# SEM Micrograph Morphological Particle Sizing Report
Benchmark Domain: {selected_domain}
Material Class: {domain_meta['material_class']}
Particles Counted: {seg_res['n_particles']}
Spatial Scale: {scale_val:.2f} nm/px
Mean Diameter: {df_particles['Diameter_nm'].mean():.2f} nm
"""

    # -------------------------------------------------------------
    # WORKFLOW 2: PARTICLE SIZE DISTRIBUTION
    # -------------------------------------------------------------
    elif analysis_mode.startswith("2"):
        seg_res = segment_micrograph(
            image=sem_img,
            scale_nm_per_px=scale_val,
            method=seg_method,
            min_area_px=min_px,
            apply_watershed=use_watershed
        )
        df_particles = seg_res["df_particles"]

        if not df_particles.empty:
            d_vals = df_particles["Diameter_nm"].to_numpy()
            dist_stats = fit_size_distributions(d_vals)

            fig, _ = render_size_distribution_plot(
                diameters_nm=d_vals,
                dist_stats=dist_stats,
                theme=selected_theme,
                font_size=selected_font_size,
                fig_size=(fig_width * 0.75, fig_height)
            )
            st.pyplot(fig)

            d_col1, d_col2, d_col3, d_col4 = st.columns(4)
            d_col1.metric("Median d50", f"{dist_stats['d50_nm']:.1f} nm", f"Span: {dist_stats['d10_nm']:.0f} - {dist_stats['d90_nm']:.0f} nm")
            d_col2.metric("Mean Diameter", f"{dist_stats['mean_nm']:.1f} ± {dist_stats['std_nm']:.1f} nm")
            d_col3.metric("Polydispersity (PDI)", f"{dist_stats['pdi']:.3f}", "Narrow" if dist_stats['pdi'] < 0.3 else "Polydisperse")
            lit_d = domain_meta.get("expected_diameter_nm", np.nan)
            d_col4.metric("Benchmark Target", f"{lit_d:.0f} nm" if not np.isnan(lit_d) else "N/A")

            # Tabulate distribution summary
            summary_df = pd.DataFrame([{
                "Count": dist_stats["count"],
                "Mean_nm": dist_stats["mean_nm"],
                "Std_nm": dist_stats["std_nm"],
                "Median_d50_nm": dist_stats["d50_nm"],
                "d10_nm": dist_stats["d10_nm"],
                "d90_nm": dist_stats["d90_nm"],
                "PDI": dist_stats["pdi"],
                "Geo_Mean_nm": dist_stats["lognormal"].get("geometric_mean_nm", np.nan),
                "Geo_Std": dist_stats["lognormal"].get("geometric_std", np.nan)
            }])

            with st.expander("📋 Particle Size Statistical Summary", expanded=False):
                st.dataframe(summary_df, use_container_width=True)

            active_export_df = df_particles
            active_summary = f"""# Particle Size Distribution Report
Benchmark Domain: {selected_domain}
Total Particles: {dist_stats['count']}
Mean Diameter: {dist_stats['mean_nm']:.1f} ± {dist_stats['std_nm']:.1f} nm
Median d50: {dist_stats['d50_nm']:.1f} nm
Polydispersity Index (PDI): {dist_stats['pdi']:.3f}
"""
        else:
            st.warning("No particles segmented. Adjust thresholding or size filter.")
            fig, ax = plt.subplots()
            active_export_df = pd.DataFrame()
            active_summary = "No particles found."

    # -------------------------------------------------------------
    # WORKFLOW 3: EDX ELEMENTAL MICROANALYSIS
    # -------------------------------------------------------------
    else:
        edx_res = analyze_edx_spectrum(
            df_edx=df_edx,
            peak_prominence=edx_prom
        )

        fig, _ = render_edx_publication_plot(
            edx_results=edx_res,
            theme=selected_theme,
            font_size=selected_font_size,
            fig_size=(fig_width, fig_height)
        )
        st.pyplot(fig)

        df_quant = edx_res["df_quant"]
        stoich = edx_res["stoichiometry"]

        if not df_quant.empty:
            e_cols = st.columns(min(len(df_quant), 4))
            for i, row in df_quant.iterrows():
                if i < len(e_cols):
                    e_cols[i].metric(f"{row['Element']} Content", f"{row['Atomic_pct']:.1f} at%", f"{row['Weight_pct']:.1f} wt%")

            if stoich:
                st.markdown("##### 🔬 Stoichiometric Verification")
                for k, v in stoich.items():
                    st.info(f"**Quantified Atomic Ratio {k}:** `{v}`")

            with st.expander("📋 Quantified Elemental Composition Table", expanded=False):
                st.dataframe(df_quant, use_container_width=True)

            active_export_df = df_quant
            active_summary = f"""# EDX Elemental Microanalysis Report
Benchmark Domain: {selected_domain}
Material Class: {domain_meta['material_class']}
Identified Elements: {', '.join(df_quant['Element'].tolist())}
Stoichiometry: {stoich}
"""
        else:
            st.warning("No elemental peaks matched above threshold.")
            active_export_df = pd.DataFrame()
            active_summary = "No peaks resolved."

    # ==============================================================================
    # ZERO-BARRIER EXPORT CENTER (ORIGINLAB, LABPLOT & PUBLICATION BUNDLE)
    # ==============================================================================
    st.markdown("---")
    st.markdown("### 📦 Publication Export & Interoperability Center")
    st.caption("Direct zero-barrier downloads: OriginLab ASCII matrix with 4-tier headers, Excel workbooks, LabPlot matrices, and 600 DPI publication graphics.")

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("#### 📊 OriginLab & LabPlot Data Matrices")
        
        # OriginLab ASCII (.dat)
        dat_bytes = get_originlab_ascii_bytes(active_export_df, title="SEM-EDX Matrix")
        st.download_button(
            "📊 Export OriginLab Matrix (.dat)",
            data=dat_bytes,
            file_name="sem_edx_originlab_matrix.dat",
            mime="text/plain",
            use_container_width=True
        )

        # OriginLab Excel Workbook (.xlsx)
        xlsx_bytes = get_originlab_excel_bytes(active_export_df, title="SEM-EDX Matrix")
        st.download_button(
            "📗 Export OriginLab Workbook (.xlsx)",
            data=xlsx_bytes,
            file_name="sem_edx_originlab_workbook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # LabPlot ASCII (.dat)
        labplot_bytes = get_labplot_ascii_bytes(active_export_df, title="SEM-EDX Matrix")
        st.download_button(
            "📉 Export LabPlot Matrix (.dat)",
            data=labplot_bytes,
            file_name="sem_edx_labplot_matrix.dat",
            mime="text/plain",
            use_container_width=True
        )

    with exp_col2:
        st.markdown("#### 🖼️ Editorial Graphics & Complete ZIP")
        
        png_bytes = get_figure_bytes(fig, "png", dpi=600)
        svg_bytes = get_figure_bytes(fig, "svg")
        pdf_bytes = get_figure_bytes(fig, "pdf")

        g_btn1, g_btn2, g_btn3 = st.columns(3)
        g_btn1.download_button("🖼️ 600 DPI PNG", data=png_bytes, file_name="sem_edx_figure_600dpi.png", mime="image/png", use_container_width=True)
        g_btn2.download_button("📐 Vector SVG", data=svg_bytes, file_name="sem_edx_figure.svg", mime="image/svg+xml", use_container_width=True)
        g_btn3.download_button("📄 Vector PDF", data=pdf_bytes, file_name="sem_edx_figure.pdf", mime="application/pdf", use_container_width=True)

        zip_bytes = build_analysis_bundle_zip(
            fig=fig,
            base_name="SEM_EDX_Analysis",
            labplot_df=active_export_df,
            summary_data={"domain": selected_domain, "mode": analysis_mode},
            title=f"SEM-EDX Analysis: {selected_domain}"
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP)",
            data=zip_bytes,
            file_name="SEM_EDX_Publication_Package.zip",
            mime="application/zip",
            use_container_width=True
        )
