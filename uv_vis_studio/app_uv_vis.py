"""
uv_vis_studio.app_uv_vis
Flagship Dedicated Streamlit Application for UV-Vis Spectroscopy,
Photodegradation Reaction Kinetics, Tauc Plot Bandgap & Urbach Energy Defect Analysis.
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

import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from uv_vis_studio.knowledge_base.benchmarks import (
    UV_VIS_DOMAINS,
    generate_rhb_kinetics,
    generate_methylene_blue_kinetics,
    generate_mapbi3_tauc_spectrum,
    generate_tio2_tauc_spectrum,
    generate_gold_nanorods_spectrum,
)
from uv_vis_studio.core.kinetics import fit_all_kinetic_models
from uv_vis_studio.core.tauc_analysis import (
    compute_tauc_series,
    fit_tauc_bandgap,
    fit_urbach_energy,
    TRANSITION_MODES
)
from uv_vis_studio.core.deconvolution import fit_uv_vis_peaks
from uv_vis_studio.visualizer.plot_kinetics import render_kinetics_publication_plot
from uv_vis_studio.visualizer.plot_tauc import render_tauc_publication_plot
from uv_vis_studio.modules.export_utils import (
    PUBLICATION_PALETTES,
    get_figure_bytes,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
    get_labplot_ascii_bytes,
    build_analysis_bundle_zip
)
from uv_vis_studio.modules.file_parser import load_smart_file, sanitize_spectral_dataframe

try:
    from uv_vis_studio.modules.counter_module import (
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
    page_title="UV-Vis & Photokinetics Studio",
    page_icon="☀️",
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
    .insight-card {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        color: #14532d;
    }
    .warning-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        color: #92400e;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #0284c7; font-weight: 700;">Characterization Module</div>
        <div style="font-size: 1.02rem; font-weight: 700; color: #0f172a; margin-top: 2px;">UV-Vis &amp; Photokinetics Studio</div>
        <div style="font-size: 0.76rem; color: #64748b; margin-top: 3px; line-height: 1.35;">
            Optical Bandgap (Tauc), Urbach Disorder &amp; Multi-Order Kinetic Regression
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 1. Material Domain & Reference")
    domain_names = list(UV_VIS_DOMAINS.keys())
    selected_domain = st.selectbox("Reference Benchmark / Domain:", domain_names, index=0)
    domain_meta = UV_VIS_DOMAINS[selected_domain]

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 5px; padding: 9px 11px; margin-bottom: 0.85rem; font-size: 0.80rem; color: #334155; line-height: 1.45;">
        <strong>Class:</strong> {domain_meta['material_class']}<br/>
        <strong>System:</strong> {domain_meta['target_analyte']}<br/>
        <strong>Standard:</strong> {domain_meta['reference']}
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Saudi Alliance Reference Databank", expanded=False):
        sq = st.text_input("Filter Materials / Literature:", placeholder="Perovskite, TiO2, UiO-66...", key="uv_saudi_sq")
        inst_choice = st.selectbox(
            "Institution Focus:",
            ["All Saudi Alliance Partners", "KAUST", "KFUPM", "KACST", "IAU (iau.edu.sa)"],
            key="uv_saudi_inst"
        )
        sub_code = inst_choice.split()[0] if "All" not in inst_choice else ""
        try:
            from knowledge_base.saudi_research_databank import search_saudi_databank
            bms = search_saudi_databank(query=sq, institution=sub_code)
            if bms:
                bm_titles = [f"{b['material_name']} ({'/'.join(b['institutions'])})" for b in bms]
                sel_idx = st.selectbox("Institutional References:", range(len(bm_titles)), format_func=lambda i: bm_titles[i], key="uv_saudi_bm_select")
                active_saudi_bm = bms[sel_idx]
                st.markdown(f"**Pillar:** *{active_saudi_bm['pillar']}*")
                st.markdown(f"**Partners:** {', '.join(active_saudi_bm['institutions'])}")
                st.caption(f"**Citation:** {active_saudi_bm['primary_citation']}")
            else:
                st.caption("No matching benchmarks found.")
        except Exception:
            st.caption("Reference databank available on Master Hub.")

    st.markdown("---")
    st.markdown("##### 2. Spectrum Data Source")
    up_file = st.file_uploader(
        "Upload Spectral Series or Tauc Spectrum (.csv, .xlsx, .txt, .dat)",
        type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "dpt"],
        help="Auto-detects wavelength (nm) and multi-column absorbance / kinetic series."
    )

    st.markdown("---")
    st.markdown("##### 3. Publication Typography & Style")
    selected_theme = st.selectbox("Journal Color Palette:", list(PUBLICATION_PALETTES.keys()), index=2)

    # Real-Time Domain Visitor Counter
    render_sidebar_counter("uv_vis_studio")


# ==============================================================================
# MAIN WORKSPACE HEADER & UNIFIED ECOSYSTEM NAVIGATION
# ==============================================================================
render_studio_navigation_bar("uv_vis_studio")

st.markdown(f"""
<div class="studio-masthead">
    <div>
        <div class="studio-eyebrow">OPTICAL ABSORPTION &amp; REACTION KINETICS</div>
        <div class="studio-title">UV-Vis &amp; Photokinetics Studio</div>
        <div class="studio-subtitle">Tauc optical bandgap extrapolation, Urbach defect tail analysis, and multi-order kinetic regression.</div>
    </div>
    <div style="display: flex; gap: 4px; flex-wrap: wrap; align-items: center;">
        <span class="badge badge-dark">{selected_domain}</span>
        <span class="badge badge-blue">{domain_meta['material_class']}</span>
        <span class="badge badge-green">OriginLab &amp; LabPlot Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# DATA INGESTION
# ==============================================================================
if up_file is not None:
    raw_bytes = up_file.getvalue()
    df_spectra, meta = load_smart_file(raw_bytes, up_file.name)
    df_spectra = sanitize_spectral_dataframe(df_spectra)
    df_kinetics = pd.DataFrame()
    source_status_msg = f"Parsed {up_file.name} ({df_spectra.shape[0]} points, {df_spectra.shape[1]-1} traces)"
else:
    if "Rhodamine B" in selected_domain:
        df_spectra, df_kinetics = generate_rhb_kinetics()
    elif "Methylene Blue" in selected_domain:
        df_spectra, df_kinetics = generate_methylene_blue_kinetics()
    elif "MAPbI3" in selected_domain:
        df_spectra = generate_mapbi3_tauc_spectrum()
        df_kinetics = pd.DataFrame()
    elif "TiO2" in selected_domain:
        df_spectra = generate_tio2_tauc_spectrum()
        df_kinetics = pd.DataFrame()
    elif "Gold Nanorods" in selected_domain:
        df_spectra = generate_gold_nanorods_spectrum()
        df_kinetics = pd.DataFrame()
    else:
        df_spectra, df_kinetics = generate_rhb_kinetics()
    source_status_msg = f"Curated Benchmark ({selected_domain}, {df_spectra.shape[0]} points)"

with st.expander("⚙️ Optical Physics, Kinetic Parameters, Tauc Transition & Figure Style", expanded=False):
    p_c1, p_c2, p_c3, p_c4 = st.columns(4)
    wavelengths_all = df_spectra.iloc[:, 0].to_numpy().astype(float)
    with p_c1:
        target_lambda = st.number_input(
            "Tracking λ_max (nm):",
            min_value=float(np.nanmin(wavelengths_all)),
            max_value=float(np.nanmax(wavelengths_all)),
            value=float(np.clip(domain_meta.get("lambda_max", 554.0), np.nanmin(wavelengths_all), np.nanmax(wavelengths_all))),
            step=1.0
        )
        initial_c0 = st.number_input("Initial Conc. C₀ (mg/L):", min_value=0.1, max_value=500.0, value=10.0, step=1.0)
    with p_c2:
        transition_sel = st.selectbox(
            "Tauc Electronic Transition:",
            list(TRANSITION_MODES.keys()),
            index=0 if "Direct" in domain_meta.get("tauc_transition", "Direct") else 1
        )
        thickness_nm = st.number_input("Film Thickness d (nm):", min_value=10.0, max_value=5000.0, value=300.0, step=50.0)
    with p_c3:
        auto_fit = st.checkbox("Auto-Detect Tauc Inflection", value=True)
        num_peaks = st.slider("Deconvolution Peaks:", min_value=1, max_value=4, value=2)
    with p_c4:
        selected_font_size = st.slider("Typography Font Size (pt):", min_value=9, max_value=18, value=12)
        fig_width = st.slider("Figure Width (in):", min_value=8.0, max_value=16.0, value=12.0, step=0.5)
        fig_height = st.slider("Figure Height (in):", min_value=4.0, max_value=8.0, value=5.2, step=0.4)

    e_min_manual, e_max_manual = None, None
    if not auto_fit:
        em1, em2 = st.columns(2)
        e_min_manual = em1.number_input("Tauc Fit Energy Min (eV):", value=1.45, step=0.05)
        e_max_manual = em2.number_input("Tauc Fit Energy Max (eV):", value=1.70, step=0.05)


# ==============================================================================
# WORKFLOW EXECUTION (FULL-WIDTH STANDARDIZED TABS)
# ==============================================================================
tab_kin, tab_tauc, tab_deconv = st.tabs([
    "⏱️ Photodegradation Reaction Kinetics",
    "🔬 Tauc Optical Bandgap (Eg) & Urbach Tail (Eu)",
    "📊 Multi-Component Peak Deconvolution"
])

with tab_kin:
    wavelengths = df_spectra.iloc[:, 0].to_numpy().astype(float)
    time_cols = list(df_spectra.columns[1:])
    extracted_times = []
    for idx_c, c in enumerate(time_cols):
        digits = ''.join(ch for ch in c if ch.isdigit() or ch == '.')
        extracted_times.append(float(digits) if digits else float(idx_c * 15.0))

    idx_lambda = int(np.argmin(np.abs(wavelengths - target_lambda)))
    a_series = np.array([float(df_spectra[c].iloc[idx_lambda]) for c in time_cols])

    kinetics_res = fit_all_kinetic_models(
        time_points=np.array(extracted_times),
        absorbance_or_conc=a_series,
        is_concentration=False,
        c0_initial=initial_c0
    )

    fig_kin, _ = render_kinetics_publication_plot(
        df_spectra=df_spectra,
        kinetics_result=kinetics_res,
        lambda_target=target_lambda,
        time_points=extracted_times,
        theme=selected_theme,
        font_size=selected_font_size,
        fig_size=(fig_width, fig_height)
    )

    pfo = kinetics_res["pfo"]
    pso = kinetics_res["pso"]
    deg_eff = kinetics_res["degradation_efficiency"][-1]

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Optimal Mechanism", kinetics_res["best_model"].split('(')[0].strip())
    m_col2.metric("PFO Rate Constant k", f"{pfo['k']:.4f} min⁻¹", f"R² = {pfo['r2']:.4f}")
    m_col3.metric("Reaction Half-Life (t½)", f"{pfo['t_half']:.1f} min" if not np.isnan(pfo['t_half']) else "N/A")
    m_col4.metric("Degradation Efficiency", f"{deg_eff:.1f} %", "Complete Conversion" if deg_eff > 90 else "")

    st.markdown(f"""
    <div class="insight-card">
        <b>Photokinetic Diagnostic Summary:</b> Source: <code>{source_status_msg}</code> &nbsp;|&nbsp;
        <b>Tracked Band:</b> λ = {target_lambda:.1f} nm &nbsp;|&nbsp;
        <b>Best Kinetic Model:</b> {kinetics_res['best_model']} (<i>k</i><sub>PFO</sub> = {pfo['k']:.4f} min⁻¹, R² = {pfo['r2']:.4f}).
    </div>
    """, unsafe_allow_html=True)

    st.pyplot(fig_kin, use_container_width=True)

    with st.expander("📋 Tabulated Kinetic Regression & Model Comparison", expanded=False):
        st.dataframe(kinetics_res["table"], use_container_width=True)

with tab_tauc:
    wl = df_spectra.iloc[:, 0].to_numpy().astype(float)
    abs_col = df_spectra.columns[1]
    abs_vals = df_spectra[abs_col].to_numpy().astype(float)

    df_tauc = compute_tauc_series(
        wavelength_nm=wl,
        absorbance=abs_vals,
        transition_mode=transition_sel,
        film_thickness_nm=thickness_nm
    )

    fit_range = (e_min_manual, e_max_manual) if not auto_fit else None
    tauc_fit = fit_tauc_bandgap(
        energy_ev=df_tauc["Photon_Energy_eV"].to_numpy(),
        tauc_y=df_tauc["Tauc_Y"].to_numpy(),
        alpha_or_abs=abs_vals,
        fit_energy_range=fit_range
    )

    eg_val = tauc_fit.get("bandgap_ev", np.nan)
    urbach_fit = fit_urbach_energy(
        energy_ev=df_tauc["Photon_Energy_eV"].to_numpy(),
        alpha_cm_inv=df_tauc["Alpha_cm_inv"].to_numpy(),
        bandgap_ev=eg_val
    )

    fig_tauc, _ = render_tauc_publication_plot(
        df_tauc=df_tauc,
        tauc_fit=tauc_fit,
        urbach_fit=urbach_fit,
        transition_label=transition_sel,
        theme=selected_theme,
        font_size=selected_font_size,
        fig_size=(fig_width, fig_height)
    )

    eu_val = urbach_fit.get("urbach_energy_mev", np.nan)
    lit_eg = domain_meta.get("literature_bandgap_eV", np.nan)

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    t_col1.metric("Optical Bandgap (Eg)", f"{eg_val:.3f} eV" if not np.isnan(eg_val) else "N/A", f"R² = {tauc_fit['r2']:.4f}")
    t_col2.metric("Absorption Onset (λ_onset)", f"{tauc_fit.get('lambda_onset_nm', np.nan):.1f} nm")
    t_col3.metric("Urbach Energy (Eu)", f"{eu_val:.1f} meV" if not np.isnan(eu_val) else "N/A", "Defect Disorder Metric")
    t_col4.metric("Literature Benchmark", f"{lit_eg:.2f} eV" if not np.isnan(lit_eg) else "N/A", "Literature Value")

    st.markdown(f"""
    <div class="insight-card">
        <b>Optical Bandgap &amp; Sub-Bandgap Tail Summary:</b> Transition: <b>{transition_sel}</b> &nbsp;|&nbsp;
        <b>Extrapolated E<sub>g</sub>:</b> {eg_val:.3f} eV (R² = {tauc_fit['r2']:.4f}) &nbsp;|&nbsp;
        <b>Urbach Tail Energy (E<sub>u</sub>):</b> {eu_val:.1f} meV.
    </div>
    """, unsafe_allow_html=True)

    st.pyplot(fig_tauc, use_container_width=True)

    with st.expander("📋 Tabulated Tauc & Optical Absorbance Data", expanded=False):
        st.dataframe(df_tauc, use_container_width=True)

with tab_deconv:
    wl = df_spectra.iloc[:, 0].to_numpy().astype(float)
    abs_col = df_spectra.columns[1]
    abs_vals = df_spectra[abs_col].to_numpy().astype(float)

    g_cols = st.columns(num_peaks)
    guesses = []
    for i in range(num_peaks):
        default_cen = 520.0 + i * 40.0
        g = g_cols[i].number_input(f"Peak {i+1} Center Guess (nm):", value=default_cen, step=5.0, key=f"uv_pk_guess_{i}")
        guesses.append(g)

    deconv_res = fit_uv_vis_peaks(
        wavelength_nm=wl,
        absorbance=abs_vals,
        initial_peak_centers=guesses
    )

    fig_deconv, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    ax.plot(deconv_res["wavelength"], deconv_res["experimental"], color="black", lw=2.0, label="Experimental")
    ax.plot(deconv_res["wavelength"], deconv_res["cumulative_fit"], color="crimson", lw=2.2, ls="--", label=f"Cumulative Fit (R²={deconv_res['r2']:.4f})")
    ax.plot(deconv_res["wavelength"], deconv_res["baseline"], color="gray", ls=":", lw=1.2, label="Baseline")

    palette = PUBLICATION_PALETTES.get(selected_theme, PUBLICATION_PALETTES["ACS"])
    for idx, curve in enumerate(deconv_res["individual_curves"]):
        c = palette[idx % len(palette)]
        pk = deconv_res["peaks"][idx]
        ax.plot(deconv_res["wavelength"], curve + deconv_res["baseline"], color=c, lw=1.8, label=f"Peak {idx+1} ({pk['center_nm']} nm, {pk['area_pct']}%)")
        ax.fill_between(deconv_res["wavelength"], deconv_res["baseline"], curve + deconv_res["baseline"], color=c, alpha=0.18)

    ax.set_xlabel(r"$\mathbf{Wavelength\ (nm)}$", fontsize=selected_font_size)
    ax.set_ylabel(r"$\mathbf{Absorbance\ (O.D.)}$", fontsize=selected_font_size)
    ax.minorticks_on()
    ax.legend(loc="upper right", framealpha=0.92, fontsize=selected_font_size - 1)
    fig_deconv.tight_layout()
    st.pyplot(fig_deconv, use_container_width=True)

    st.markdown("##### Deconvolved Component Breakdown")
    df_peaks = pd.DataFrame(deconv_res["peaks"])
    st.dataframe(df_peaks, use_container_width=True)

# Select default active export based on domain default mode
if domain_meta.get("mode") == "tauc":
    fig = fig_tauc
    active_export_df = df_tauc
else:
    fig = fig_kin
    active_export_df = kinetics_res["table"]

# ==============================================================================
# ZERO-BARRIER EXPORT CENTER (ORIGINLAB, LABPLOT & PUBLICATION BUNDLE)
# ==============================================================================
st.markdown("---")
st.markdown("#### 📥 Publication Export Center (OriginLab, LabPlot & 600 DPI Vectors)")

zip_bytes = build_analysis_bundle_zip(
    fig=fig,
    base_name="UV_Vis_Analysis",
    labplot_df=active_export_df,
    summary_data={"domain": selected_domain, "mode": domain_meta.get("mode", "kinetics")},
    title=f"UV-Vis Analysis: {selected_domain}"
)
st.download_button(
    "📦 Download Complete UV-Vis Publication Package (.ZIP — 600 DPI PNG, PDF, SVG + OriginLab/LabPlot Matrices)",
    data=zip_bytes,
    file_name="UV_Vis_Publication_Package.zip",
    mime="application/zip",
    use_container_width=True,
    type="primary"
)

exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    st.markdown("##### 📊 OriginLab & LabPlot Data Matrices")
    o1, o2, o3 = st.columns(3)
    dat_bytes = get_originlab_ascii_bytes(active_export_df, title="UV-Vis Matrix")
    o1.download_button(
        "📊 Origin (.dat)",
        data=dat_bytes,
        file_name="uv_vis_originlab_matrix.dat",
        mime="text/plain",
        use_container_width=True
    )

    xlsx_bytes = get_originlab_excel_bytes(active_export_df, title="UV-Vis Matrix")
    o2.download_button(
        "📗 Excel (.xlsx)",
        data=xlsx_bytes,
        file_name="uv_vis_originlab_workbook.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    labplot_bytes = get_labplot_ascii_bytes(active_export_df, title="UV-Vis Matrix")
    o3.download_button(
        "📉 LabPlot (.dat)",
        data=labplot_bytes,
        file_name="uv_vis_labplot_matrix.dat",
        mime="text/plain",
        use_container_width=True
    )

with exp_col2:
    st.markdown("##### 🖼️ High-Resolution Vector & Raster Graphics")
    png_bytes = get_figure_bytes(fig, "png", dpi=600)
    svg_bytes = get_figure_bytes(fig, "svg")
    pdf_bytes = get_figure_bytes(fig, "pdf")

    g_btn1, g_btn2, g_btn3 = st.columns(3)
    g_btn1.download_button("🖼️ 600 DPI PNG", data=png_bytes, file_name="uv_vis_figure_600dpi.png", mime="image/png", use_container_width=True)
    g_btn2.download_button("📐 Vector SVG", data=svg_bytes, file_name="uv_vis_figure.svg", mime="image/svg+xml", use_container_width=True)
    g_btn3.download_button("📄 Vector PDF", data=pdf_bytes, file_name="uv_vis_figure.pdf", mime="application/pdf", use_container_width=True)

# ==============================================================================
# UNIFIED INSTITUTIONAL FOOTER & MASTER GATEWAY REVIEW LINK
# ==============================================================================
render_unified_studio_footer(
    active_domain_key="uv_vis_studio",
    studio_title="UV-Vis & Photokinetics Studio",
    studio_subtitle="Tauc Optical Bandgap, Urbach Defect Tail & Kinetic Modeling Intelligence"
)
