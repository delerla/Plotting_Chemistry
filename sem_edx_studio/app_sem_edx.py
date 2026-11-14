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

try:
    from sem_edx_studio.modules.counter_module import (
        render_sidebar_counter,
        render_studio_navigation_bar,
        render_unified_studio_footer,
    )
except ImportError:
    try:
        from modules.counter_module import (
            render_sidebar_counter,
            render_studio_navigation_bar,
            render_unified_studio_footer,
        )
    except ImportError:
        try:
            from counter_module import (
                render_sidebar_counter,
                render_studio_navigation_bar,
                render_unified_studio_footer,
            )
        except ImportError:
            def render_sidebar_counter(domain_key: str):
                pass
            def render_studio_navigation_bar(active_domain_key: str):
                st.markdown('<a href="https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/" target="_blank" style="display:inline-flex; align-items:center; padding: 4px 11px; background: #ffffff; color: #0f172a !important; border: 1px solid #94a3b8; border-radius: 4px; text-decoration: none !important; font-weight: 600; font-size: 0.76rem;">← Master Hub</a>', unsafe_allow_html=True)
            def render_unified_studio_footer(active_domain_key: str, studio_title: str, studio_subtitle: str):
                st.markdown(f'<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.78rem;"><strong>{studio_title}</strong> — {studio_subtitle}<br/>© 2026 Dr. Deler Langenberg • MIT Open-Source License</div>', unsafe_allow_html=True)

# Page Configuration
st.set_page_config(
    page_title="SEM-EDX Microstructural Studio",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Standardized Institutional Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .studio-masthead {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0f172a;
        border-radius: 6px;
        padding: 1rem 1.35rem;
        margin-bottom: 1.15rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
    }
    .studio-eyebrow {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0284c7;
        margin-bottom: 2px;
    }
    .studio-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .studio-subtitle {
        font-size: 0.84rem;
        color: #475569;
        margin-top: 3px;
    }
    .sidebar-brand {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #0f172a;
        border-radius: 5px;
        padding: 10px 12px;
        margin-bottom: 1rem;
    }
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        padding: 11px 15px;
        border-radius: 6px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 9px 13px;
        border-radius: 6px;
        color: #92400e;
        margin-top: 8px;
        font-size: 0.88rem;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-right: 4px;
    }
    .badge-dark { background: #0f172a; color: #f8fafc; }
    .badge-blue { background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd; }
    .badge-green { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR: DOMAIN, DATA SOURCES & STYLE
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #0284c7; font-weight: 700;">Characterization Module</div>
        <div style="font-size: 1.02rem; font-weight: 700; color: #0f172a; margin-top: 2px;">SEM-EDX Microstructural Studio</div>
        <div style="font-size: 0.76rem; color: #64748b; margin-top: 3px; line-height: 1.35;">
            Watershed Particle Segmentation, Size Distributions &amp; EDX Stoichiometry
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 1. Material Domain & Reference")
    domain_names = list(SEM_EDX_DOMAINS.keys())
    selected_domain = st.selectbox("Reference Benchmark / Domain:", domain_names, index=0)
    domain_meta = SEM_EDX_DOMAINS[selected_domain]

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 5px; padding: 9px 11px; margin-bottom: 0.85rem; font-size: 0.80rem; color: #334155; line-height: 1.45;">
        <strong>Class:</strong> {domain_meta['material_class']}<br/>
        <strong>Morphology:</strong> {domain_meta['morphology']}<br/>
        <strong>Standard:</strong> {domain_meta['reference']}
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Saudi Alliance Reference Databank", expanded=False):
        sq = st.text_input("Filter Materials / Literature:", placeholder="UiO-66, Perovskite, PAN, TiO2...", key="sem_saudi_sq")
        inst_choice = st.selectbox(
            "Institution Focus:",
            ["All Saudi Alliance Partners", "KAUST", "KFUPM", "KACST", "IAU (iau.edu.sa)"],
            key="sem_saudi_inst"
        )
        sub_code = inst_choice.split()[0] if "All" not in inst_choice else ""
        try:
            from knowledge_base.saudi_research_databank import search_saudi_databank
            bms = search_saudi_databank(query=sq, institution=sub_code)
            if bms:
                bm_titles = [f"{b['material_name']} ({'/'.join(b['institutions'])})" for b in bms]
                sel_idx = st.selectbox("Institutional References:", range(len(bm_titles)), format_func=lambda i: bm_titles[i], key="sem_saudi_bm_select")
                active_saudi_bm = bms[sel_idx]
                st.markdown(f"**Pillar:** *{active_saudi_bm['pillar']}*")
                st.markdown(f"**Partners:** {', '.join(active_saudi_bm['institutions'])}")
                st.caption(f"**Citation:** {active_saudi_bm['primary_citation']}")
            else:
                st.caption("No matching benchmarks found.")
        except Exception:
            st.caption("Reference databank available on Master Hub.")

    st.markdown("##### 2. Micrograph & EDX Data Sources")
    up_img = st.file_uploader(
        "Upload SEM Micrograph (PNG, JPG, TIFF):",
        type=["png", "jpg", "jpeg", "tif", "tiff"],
        key="sem_img_uploader"
    )
    if up_img is not None:
        file_bytes = np.asarray(bytearray(up_img.read()), dtype=np.uint8)
        sem_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        st.success(f"Loaded Micrograph: {up_img.name} ({sem_img.shape[1]}×{sem_img.shape[0]} px)")
    else:
        if "Perovskite" in selected_domain:
            sem_img = generate_perovskite_grains_micrograph()
        else:
            sem_img = generate_uio66_micrograph()
        st.caption(f"Reference micrograph loaded ({sem_img.shape[1]}×{sem_img.shape[0]} px)")

    up_edx = st.file_uploader(
        "Upload EDX Spectrum (CSV, DAT, TXT, Excel):",
        type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "dpt"],
        key="sem_edx_uploader"
    )
    if up_edx is not None:
        raw_b = up_edx.getvalue()
        df_edx, _ = load_smart_file(raw_b, up_edx.name)
        st.success(f"Loaded EDX: {up_edx.name} ({df_edx.shape[0]} channels)")
    else:
        if "Perovskite" in selected_domain:
            df_edx = generate_mapbi3_edx_spectrum()
        else:
            df_edx = generate_uio66_edx_spectrum()
        st.caption(f"Reference EDX spectrum loaded ({df_edx.shape[0]} channels)")

    st.markdown("---")
    st.markdown("##### 3. Publication Typography & Style")
    selected_theme = st.selectbox("Journal Color Palette:", list(PUBLICATION_PALETTES.keys()), index=2)

    # Real-Time Domain Visitor Counter
    render_sidebar_counter("sem_edx_studio")


# ==============================================================================
# MAIN WORKSPACE HEADER & UNIFIED ECOSYSTEM NAVIGATION
# ==============================================================================
render_studio_navigation_bar("sem_edx_studio")

st.markdown(f"""
<div class="studio-masthead">
    <div>
        <div class="studio-eyebrow">ELECTRON MICROSCOPY &amp; ELEMENTAL MICROANALYSIS</div>
        <div class="studio-title">SEM-EDX Microstructural Studio</div>
        <div class="studio-subtitle">Distance-watershed particle segmentation, Log-Normal/Weibull statistical sizing, and EDX stoichiometric quantification.</div>
    </div>
    <div style="display: flex; gap: 4px; flex-wrap: wrap; align-items: center;">
        <span class="badge badge-dark">{selected_domain}</span>
        <span class="badge badge-blue">{domain_meta['material_class']}</span>
        <span class="badge badge-green">OriginLab &amp; LabPlot Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top-Level Analytical Workflow Tabs (Standardized with XRD, FTIR, XPS)
tab_seg, tab_dist, tab_edx = st.tabs([
    "🔬 SEM Micrograph Segmentation & Particle Sizing",
    "📊 Particle Size Statistical Distribution (Log-Normal & Weibull)",
    "⚡ EDX Elemental Microanalysis & Stoichiometry"
])

# Shared Segmentation & Typography Controls
with st.expander("⚙️ Spatial Calibration, Thresholding, EDX Sensitivity & Figure Style", expanded=False):
    c_cfg1, c_cfg2, c_cfg3 = st.columns(3)
    with c_cfg1:
        scale_val = st.number_input("Spatial Scale (nm per pixel):", min_value=0.01, max_value=500.0, value=12.5, step=0.5)
        seg_method = st.selectbox("Segmentation Algorithm:", ["Otsu", "Adaptive"], index=0)
        use_watershed = st.checkbox("Apply Distance Watershed Separation", value=True)
    with c_cfg2:
        min_px = st.slider("Min Particle Area Filter (px):", min_value=5, max_value=200, value=25)
        edx_prom = st.slider("EDX Peak Prominence (Counts):", min_value=20.0, max_value=500.0, value=75.0, step=5.0)
    with c_cfg3:
        selected_font_size = st.slider("Typography Font Size (pt):", min_value=9, max_value=18, value=12)
        fig_width = st.slider("Figure Width (in):", min_value=8.0, max_value=16.0, value=11.0, step=0.5)
        fig_height = st.slider("Figure Height (in):", min_value=4.0, max_value=8.0, value=5.2, step=0.5)

seg_res = segment_micrograph(
    image=sem_img,
    scale_nm_per_px=scale_val,
    method=seg_method,
    min_area_px=min_px,
    apply_watershed=use_watershed
)
df_particles = seg_res["df_particles"]

# ==============================================================================
# TAB 1: SEM MICROGRAPH SEGMENTATION & PARTICLE SIZING
# ==============================================================================
with tab_seg:
    fig_seg, _ = render_micrograph_overlay_plot(
        raw_img=sem_img,
        overlay_rgb=seg_res["overlay_rgb"],
        scale_nm_per_px=scale_val,
        font_size=selected_font_size,
        fig_size=(fig_width, fig_height)
    )
    st.pyplot(fig_seg)

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    s_col1.metric("Particles Segmented", seg_res["n_particles"])
    if not df_particles.empty:
        mean_d = df_particles["Diameter_nm"].mean()
        mean_asp = df_particles["Aspect_Ratio"].mean()
        mean_sph = df_particles["Sphericity"].mean()
        s_col2.metric("Mean Equivalent Diameter", f"{mean_d:.1f} nm")
        s_col3.metric("Mean Aspect Ratio", f"{mean_asp:.2f}")
        s_col4.metric("Mean Sphericity", f"{mean_sph:.2f}")

        st.markdown(f"""
        <div class="insight-card">
            <strong>✓ Morphological Diagnostic:</strong> Segmented <b>{seg_res['n_particles']}</b> discrete grains/crystallites at a spatial calibration of <code>{scale_val:.2f} nm/px</code> using {seg_method} thresholding{' with Euclidean distance-watershed separation' if use_watershed else ''}. Mean equivalent diameter = <b>{mean_d:.1f} nm</b> (aspect ratio = {mean_asp:.2f}, sphericity = {mean_sph:.2f}).
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📊 Tabulated Morphological Particle Metrics", expanded=True):
            st.dataframe(df_particles, use_container_width=True)

    st.markdown("#### 📥 Publication Export Center")
    clean_slug = selected_domain.split("(")[0].strip().replace(" ", "_").replace("/", "_")
    zip_seg = build_analysis_bundle_zip(
        fig=fig_seg,
        base_name=f"SEM_Segmentation_{clean_slug}",
        labplot_df=df_particles,
        summary_data={"domain": selected_domain, "particles": seg_res["n_particles"]},
        title=f"SEM Segmentation: {selected_domain}"
    )
    st.download_button(
        "📦 Download Complete SEM Segmentation Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
        data=zip_seg,
        file_name=f"SEM_{clean_slug}_Segmentation_Package.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
        key="dl_sem_seg_zip"
    )
    c_l1, c_r1 = st.columns(2)
    with c_l1:
        st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
        st.download_button("📊 Export OriginLab Matrix (.dat)", data=get_originlab_ascii_bytes(df_particles, title="SEM Particle Sizing Matrix"), file_name=f"SEM_{clean_slug}_OriginLab.dat", mime="text/plain", use_container_width=True, key="sem_seg_dat")
        st.download_button("📗 Export OriginLab Workbook (.xlsx)", data=get_originlab_excel_bytes(df_particles, title="SEM Particle Sizing Matrix"), file_name=f"SEM_{clean_slug}_OriginLab.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="sem_seg_xlsx")
        st.download_button("📈 Export LabPlot Matrix (.dat)", data=get_labplot_ascii_bytes(df_particles, title="SEM Particle Sizing Matrix"), file_name=f"SEM_{clean_slug}_LabPlot.dat", mime="text/plain", use_container_width=True, key="sem_seg_lab")
    with c_r1:
        st.markdown("**🖼️ Publication Graphics:**")
        st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_seg, "png", dpi=600), file_name=f"SEM_{clean_slug}_600DPI.png", mime="image/png", use_container_width=True, key="sem_seg_png")
        st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_seg, "svg"), file_name=f"SEM_{clean_slug}.svg", mime="image/svg+xml", use_container_width=True, key="sem_seg_svg")
        st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_seg, "pdf"), file_name=f"SEM_{clean_slug}.pdf", mime="application/pdf", use_container_width=True, key="sem_seg_pdf")
    plt.close(fig_seg)


# ==============================================================================
# TAB 2: PARTICLE SIZE STATISTICAL DISTRIBUTION
# ==============================================================================
with tab_dist:
    if not df_particles.empty:
        d_vals = df_particles["Diameter_nm"].to_numpy()
        dist_stats = fit_size_distributions(d_vals)

        fig_dist, _ = render_size_distribution_plot(
            diameters_nm=d_vals,
            dist_stats=dist_stats,
            theme=selected_theme,
            font_size=selected_font_size,
            fig_size=(fig_width, fig_height)
        )
        st.pyplot(fig_dist)

        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("Median Diameter (d50)", f"{dist_stats['d50_nm']:.1f} nm", f"d10–d90: {dist_stats['d10_nm']:.0f}–{dist_stats['d90_nm']:.0f} nm")
        d_col2.metric("Mean ± Std Dev", f"{dist_stats['mean_nm']:.1f} ± {dist_stats['std_nm']:.1f} nm")
        d_col3.metric("Polydispersity (PDI)", f"{dist_stats['pdi']:.3f}", "Monodisperse" if dist_stats['pdi'] < 0.1 else ("Narrow" if dist_stats['pdi'] < 0.3 else "Polydisperse"))
        lit_d = domain_meta.get("expected_diameter_nm", np.nan)
        d_col4.metric("Reference Benchmark", f"{lit_d:.0f} nm" if not np.isnan(lit_d) else "N/A")

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

        with st.expander("📊 Particle Size Distribution Statistical Summary", expanded=True):
            st.dataframe(summary_df, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        zip_dist = build_analysis_bundle_zip(
            fig=fig_dist,
            base_name=f"SEM_Distribution_{clean_slug}",
            labplot_df=df_particles,
            summary_data=summary_df,
            title=f"Particle Size Distribution: {selected_domain}"
        )
        st.download_button(
            "📦 Download Complete Size Distribution Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
            data=zip_dist,
            file_name=f"SEM_{clean_slug}_Distribution_Package.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="dl_sem_dist_zip"
        )
        c_l2, c_r2 = st.columns(2)
        with c_l2:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button("📊 Export OriginLab Matrix (.dat)", data=get_originlab_ascii_bytes(df_particles, title="Particle Size Distribution Matrix"), file_name=f"SEM_Dist_{clean_slug}_OriginLab.dat", mime="text/plain", use_container_width=True, key="sem_dist_dat")
            st.download_button("📗 Export OriginLab Workbook (.xlsx)", data=get_originlab_excel_bytes(df_particles, title="Particle Size Distribution Matrix"), file_name=f"SEM_Dist_{clean_slug}_OriginLab.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="sem_dist_xlsx")
            st.download_button("📈 Export LabPlot Matrix (.dat)", data=get_labplot_ascii_bytes(df_particles, title="Particle Size Distribution Matrix"), file_name=f"SEM_Dist_{clean_slug}_LabPlot.dat", mime="text/plain", use_container_width=True, key="sem_dist_lab")
        with c_r2:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_dist, "png", dpi=600), file_name=f"SEM_Dist_{clean_slug}_600DPI.png", mime="image/png", use_container_width=True, key="sem_dist_png")
            st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_dist, "svg"), file_name=f"SEM_Dist_{clean_slug}.svg", mime="image/svg+xml", use_container_width=True, key="sem_dist_svg")
            st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_dist, "pdf"), file_name=f"SEM_Dist_{clean_slug}.pdf", mime="application/pdf", use_container_width=True, key="sem_dist_pdf")
        plt.close(fig_dist)
    else:
        st.warning("No particles segmented. Adjust thresholding or minimum area filter in the configuration bar above.")


# ==============================================================================
# TAB 3: EDX ELEMENTAL MICROANALYSIS & STOICHIOMETRY
# ==============================================================================
with tab_edx:
    edx_res = analyze_edx_spectrum(
        df_edx=df_edx,
        peak_prominence=edx_prom
    )

    fig_edx, _ = render_edx_publication_plot(
        edx_results=edx_res,
        theme=selected_theme,
        font_size=selected_font_size,
        fig_size=(fig_width, fig_height)
    )
    st.pyplot(fig_edx)

    df_quant = edx_res["df_quant"]
    stoich = edx_res["stoichiometry"]

    if not df_quant.empty:
        e_cols = st.columns(min(len(df_quant), 4))
        for i, row in df_quant.iterrows():
            if i < len(e_cols):
                e_cols[i].metric(f"{row['Element']} Content", f"{row['Atomic_pct']:.1f} at%", f"{row['Weight_pct']:.1f} wt%")

        if stoich:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            for k, v in stoich.items():
                st.markdown(f"**✓ Stoichiometric Atomic Ratio ({k}):** `{v}`")
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("📊 Quantified Elemental Composition Table", expanded=True):
            st.dataframe(df_quant, use_container_width=True)

        st.markdown("#### 📥 Publication Export Center")
        zip_edx = build_analysis_bundle_zip(
            fig=fig_edx,
            base_name=f"EDX_{clean_slug}",
            labplot_df=df_quant,
            summary_data=df_quant,
            title=f"EDX Microanalysis: {selected_domain}"
        )
        st.download_button(
            "📦 Download Complete EDX Microanalysis Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
            data=zip_edx,
            file_name=f"EDX_{clean_slug}_Package.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="dl_edx_zip"
        )
        c_l3, c_r3 = st.columns(2)
        with c_l3:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button("📊 Export OriginLab Matrix (.dat)", data=get_originlab_ascii_bytes(df_quant, title="EDX Elemental Composition Matrix"), file_name=f"EDX_{clean_slug}_OriginLab.dat", mime="text/plain", use_container_width=True, key="edx_dat")
            st.download_button("📗 Export OriginLab Workbook (.xlsx)", data=get_originlab_excel_bytes(df_quant, title="EDX Elemental Composition Matrix"), file_name=f"EDX_{clean_slug}_OriginLab.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="edx_xlsx")
            st.download_button("📈 Export LabPlot Matrix (.dat)", data=get_labplot_ascii_bytes(df_quant, title="EDX Elemental Composition Matrix"), file_name=f"EDX_{clean_slug}_LabPlot.dat", mime="text/plain", use_container_width=True, key="edx_lab")
        with c_r3:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_edx, "png", dpi=600), file_name=f"EDX_{clean_slug}_600DPI.png", mime="image/png", use_container_width=True, key="edx_png")
            st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_edx, "svg"), file_name=f"EDX_{clean_slug}.svg", mime="image/svg+xml", use_container_width=True, key="edx_svg")
            st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_edx, "pdf"), file_name=f"EDX_{clean_slug}.pdf", mime="application/pdf", use_container_width=True, key="edx_pdf")
        plt.close(fig_edx)
    else:
        st.warning("No characteristic X-ray lines resolved above threshold. Lower the peak prominence threshold above.")

# ==============================================================================
# UNIFIED INSTITUTIONAL FOOTER & MASTER GATEWAY REVIEW LINK
# ==============================================================================
render_unified_studio_footer(
    active_domain_key="sem_edx_studio",
    studio_title="SEM-EDX Microstructural Studio",
    studio_subtitle="Microstructural Watershed Segmentation, Sizing Statistics & EDX Stoichiometry"
)
