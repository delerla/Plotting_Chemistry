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

# Page Configuration
st.set_page_config(
    page_title="UV-Vis Studio - Dr. Deler Langenberg",
    page_icon="☀️",
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
    .uv-header {
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
            <div style="font-size: 1.5rem;">☀️</div>
            <div>
                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Dedicated Studio</div>
                <div style="font-size: 1.18rem; font-weight: 800; color: #38bdf8; line-height: 1.2;">Dr. Deler Langenberg</div>
            </div>
        </div>
        <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 8px; line-height: 1.35;">
            UV-Vis Spectroscopy, Photokinetics & Tauc Optical Bandgap Suite
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
    domain_names = list(UV_VIS_DOMAINS.keys())
    selected_domain = st.selectbox("Scientific Benchmark / Domain:", domain_names, index=0)
    domain_meta = UV_VIS_DOMAINS[selected_domain]

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin-bottom: 1rem; font-size: 0.83rem; line-height: 1.4;">
        <strong>Target Class:</strong> {domain_meta['material_class']}<br/>
        <strong>Analyte:</strong> {domain_meta['target_analyte']}<br/>
        <strong>Audited Reference:</strong> {domain_meta['reference']}
    </div>
    """, unsafe_allow_html=True)

    analysis_mode = st.radio(
        "Analysis Workflow:",
        ["1. Photodegradation Reaction Kinetics", "2. Tauc Optical Bandgap (Eg) & Urbach Tail (Eu)", "3. Multi-Component Peak Deconvolution"],
        index=0 if domain_meta.get("mode") == "kinetics" else (1 if domain_meta.get("mode") == "tauc" else 0)
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
    st.page_link("app.py", label="← Return to Materials Characterization Multi-Technique Hub", icon="🏠")
except Exception:
    st.markdown('<a href="/" target="_self" style="display:inline-block; padding: 6px 14px; margin-bottom: 8px; background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem;">🏠 ← Return to Materials Characterization Multi-Technique Hub</a>', unsafe_allow_html=True)

st.markdown('<div class="uv-header">☀️ UV-Vis Studio: Photokinetics & Optical Bandgap Intelligence</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom: 1.0rem;">
    <span class="badge badge-dark">{selected_domain}</span>
    <span class="badge badge-blue">{domain_meta['material_class']}</span>
    <span class="badge badge-green">Zero-Barrier Export • OriginLab Ready</span>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# DATA INGESTION
# ==============================================================================
col_ctrl, col_view = st.columns([1, 2.6])

with col_ctrl:
    st.subheader("Data & Parameters")
    data_source = st.radio("Data Source:", ["Curated Benchmark Series", "Upload File (Excel / Origin / CSV / DAT / TXT)"], key="uv_src")
    
    if data_source == "Curated Benchmark Series":
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
        st.success(f"Ingested benchmark dataset: {df_spectra.shape[0]} wavelength points, {df_spectra.shape[1]-1} time/absorbance series.")
    else:
        up_file = st.file_uploader("Upload Spectral Series or Tauc Spectrum", type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "dpt"])
        if up_file is not None:
            raw_bytes = up_file.getvalue()
            df_spectra, meta = load_smart_file(raw_bytes, up_file.name)
            df_spectra = sanitize_spectral_dataframe(df_spectra)
            st.success(f"Parsed {up_file.name}: {df_spectra.shape[0]} data points, {df_spectra.shape[1]-1} traces.")
        else:
            df_spectra, df_kinetics = generate_rhb_kinetics()
            st.info("No file uploaded yet. Displaying default Rhodamine B benchmark.")

    st.markdown("---")


# ==============================================================================
# WORKFLOW EXECUTION
# ==============================================================================
with col_view:
    # -------------------------------------------------------------
    # WORKFLOW 1: PHOTODEGRADATION REACTION KINETICS
    # -------------------------------------------------------------
    if analysis_mode.startswith("1"):
        wavelengths = df_spectra.iloc[:, 0].to_numpy().astype(float)
        time_cols = list(df_spectra.columns[1:])
        
        # User controls for Kinetics
        with col_ctrl:
            st.markdown("#### ⏱️ Kinetic Settings")
            target_lambda = st.number_input(
                "Tracking Wavelength λ_max (nm):",
                min_value=float(np.nanmin(wavelengths)),
                max_value=float(np.nanmax(wavelengths)),
                value=float(domain_meta.get("lambda_max", 554.0)),
                step=1.0
            )
            initial_c0 = st.number_input("Initial Concentration C0 (mg/L):", min_value=0.1, max_value=500.0, value=10.0, step=1.0)
            
            # Extract time points
            extracted_times = []
            for c in time_cols:
                digits = ''.join(ch for ch in c if ch.isdigit() or ch == '.')
                extracted_times.append(float(digits) if digits else 0.0)
            
            st.caption(f"Series points: {extracted_times} minutes")

        # Run multi-order kinetic fit
        idx_lambda = np.argmin(np.abs(wavelengths - target_lambda))
        a_series = np.array([float(df_spectra[c].iloc[idx_lambda]) for c in time_cols])
        
        kinetics_res = fit_all_kinetic_models(
            time_points=np.array(extracted_times),
            absorbance_or_conc=a_series,
            is_concentration=False,
            c0_initial=initial_c0
        )

        fig, _ = render_kinetics_publication_plot(
            df_spectra=df_spectra,
            kinetics_result=kinetics_res,
            lambda_target=target_lambda,
            time_points=extracted_times,
            theme=selected_theme,
            font_size=selected_font_size,
            fig_size=(fig_width, fig_height)
        )
        st.pyplot(fig)

        # Scientific Metrics Summary Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        pfo = kinetics_res["pfo"]
        pso = kinetics_res["pso"]
        deg_eff = kinetics_res["degradation_efficiency"][-1]

        m_col1.metric("Optimal Mechanism", kinetics_res["best_model"].split('(')[0].strip())
        m_col2.metric("PFO Rate Constant k", f"{pfo['k']:.4f} min⁻¹", f"R² = {pfo['r2']:.4f}")
        m_col3.metric("Reaction Half-Life (t½)", f"{pfo['t_half']:.1f} min" if not np.isnan(pfo['t_half']) else "N/A")
        m_col4.metric("Degradation Efficiency", f"{deg_eff:.1f} %", "Complete Conversion" if deg_eff > 90 else "")

        # Kinetics Table Preview
        with st.expander("📋 Tabulated Kinetic Regression & Model Comparison", expanded=False):
            st.dataframe(kinetics_res["table"], use_container_width=True)

        active_export_df = kinetics_res["table"]
        active_summary = f"""# UV-Vis Photodegradation Kinetics Report
Benchmark: {selected_domain}
Material Class: {domain_meta['material_class']}
Tracking Wavelength: {target_lambda:.1f} nm
Optimal Kinetic Mechanism: {kinetics_res['best_model']}
Pseudo-First-Order Rate Constant (k_app): {pfo['k']:.5f} min^-1 (R2 = {pfo['r2']:.4f})
Pseudo-Second-Order Rate Constant (k2): {pso['k']:.6f} g/(mg*min) (R2 = {pso['r2']:.4f})
Final Degradation Efficiency: {deg_eff:.2f}%
Half-Life (t1/2): {pfo['t_half']:.2f} min
"""

    # -------------------------------------------------------------
    # WORKFLOW 2: TAUC PLOT OPTICAL BANDGAP & URBACH TAIL
    # -------------------------------------------------------------
    elif analysis_mode.startswith("2"):
        with col_ctrl:
            st.markdown("#### 🔬 Tauc Plot Parameters")
            transition_sel = st.selectbox(
                "Electronic Transition Mode:",
                list(TRANSITION_MODES.keys()),
                index=0 if "Direct" in domain_meta.get("tauc_transition", "Direct") else 1
            )
            thickness_nm = st.number_input("Film Thickness d (nm):", min_value=10.0, max_value=5000.0, value=300.0, step=50.0)
            
            auto_fit = st.checkbox("Auto-Detect Linear Inflection Region", value=True)
            e_min_manual, e_max_manual = None, None
            if not auto_fit:
                e_min_manual = st.number_input("Fit Energy Min (eV):", value=1.45, step=0.05)
                e_max_manual = st.number_input("Fit Energy Max (eV):", value=1.70, step=0.05)

        # Compute Tauc Data
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

        fig, _ = render_tauc_publication_plot(
            df_tauc=df_tauc,
            tauc_fit=tauc_fit,
            urbach_fit=urbach_fit,
            transition_label=transition_sel,
            theme=selected_theme,
            font_size=selected_font_size,
            fig_size=(fig_width, fig_height)
        )
        st.pyplot(fig)

        # Metrics cards
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        t_col1.metric("Optical Bandgap (Eg)", f"{eg_val:.3f} eV" if not np.isnan(eg_val) else "N/A", f"R² = {tauc_fit['r2']:.4f}")
        t_col2.metric("Absorption Onset (λ_onset)", f"{tauc_fit.get('lambda_onset_nm', np.nan):.1f} nm")
        eu_val = urbach_fit.get("urbach_energy_mev", np.nan)
        t_col3.metric("Urbach Energy (Eu)", f"{eu_val:.1f} meV" if not np.isnan(eu_val) else "N/A", "Defect Disorder Metric")
        lit_eg = domain_meta.get("literature_bandgap_eV", np.nan)
        t_col4.metric("Literature Benchmark", f"{lit_eg:.2f} eV" if not np.isnan(lit_eg) else "N/A", "Literature Value")

        with st.expander("📋 Tabulated Tauc & Optical Absorbance Data", expanded=False):
            st.dataframe(df_tauc, use_container_width=True)

        active_export_df = df_tauc
        active_summary = f"""# UV-Vis Tauc Optical Bandgap & Urbach Defect Report
Benchmark Domain: {selected_domain}
Material Class: {domain_meta['material_class']}
Transition: {transition_sel}
Optical Bandgap (Eg): {eg_val:.3f} eV (R2 = {tauc_fit['r2']:.4f})
Absorption Onset (lambda_onset): {tauc_fit.get('lambda_onset_nm', np.nan):.1f} nm
Urbach Tail Energy (Eu): {eu_val:.2f} meV
Film Thickness: {thickness_nm:.1f} nm
"""

    # -------------------------------------------------------------
    # WORKFLOW 3: MULTI-COMPONENT PEAK DECONVOLUTION
    # -------------------------------------------------------------
    else:
        wl = df_spectra.iloc[:, 0].to_numpy().astype(float)
        abs_col = df_spectra.columns[1]
        abs_vals = df_spectra[abs_col].to_numpy().astype(float)

        with col_ctrl:
            st.markdown("#### 🔍 Deconvolution Guesses")
            num_peaks = st.slider("Number of Component Peaks:", min_value=1, max_value=4, value=2)
            guesses = []
            for i in range(num_peaks):
                default_cen = 520.0 + i * 40.0
                g = st.number_input(f"Peak {i+1} Guess (nm):", value=default_cen, step=5.0)
                guesses.append(g)

        deconv_res = fit_uv_vis_peaks(
            wavelength_nm=wl,
            absorbance=abs_vals,
            initial_peak_centers=guesses
        )

        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
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
        fig.tight_layout()
        st.pyplot(fig)

        st.markdown("##### Deconvolved Component Breakdown")
        df_peaks = pd.DataFrame(deconv_res["peaks"])
        st.dataframe(df_peaks, use_container_width=True)

        active_export_df = df_peaks
        active_summary = f"""# UV-Vis Multi-Peak Deconvolution Report
Benchmark: {selected_domain}
Deconvolution R2: {deconv_res['r2']:.4f}
Peaks Resolved: {len(deconv_res['peaks'])}
"""

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
        dat_bytes = get_originlab_ascii_bytes(active_export_df, title="UV-Vis Matrix")
        st.download_button(
            "📊 Export OriginLab Matrix (.dat)",
            data=dat_bytes,
            file_name="uv_vis_originlab_matrix.dat",
            mime="text/plain",
            use_container_width=True
        )

        # OriginLab Excel Workbook (.xlsx)
        xlsx_bytes = get_originlab_excel_bytes(active_export_df, title="UV-Vis Matrix")
        st.download_button(
            "📗 Export OriginLab Workbook (.xlsx)",
            data=xlsx_bytes,
            file_name="uv_vis_originlab_workbook.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # LabPlot ASCII (.dat)
        labplot_bytes = get_labplot_ascii_bytes(active_export_df, title="UV-Vis Matrix")
        st.download_button(
            "📉 Export LabPlot Matrix (.dat)",
            data=labplot_bytes,
            file_name="uv_vis_labplot_matrix.dat",
            mime="text/plain",
            use_container_width=True
        )

    with exp_col2:
        st.markdown("#### 🖼️ Editorial Graphics & Complete ZIP")
        
        png_bytes = get_figure_bytes(fig, "png", dpi=600)
        svg_bytes = get_figure_bytes(fig, "svg")
        pdf_bytes = get_figure_bytes(fig, "pdf")

        g_btn1, g_btn2, g_btn3 = st.columns(3)
        g_btn1.download_button("🖼️ 600 DPI PNG", data=png_bytes, file_name="uv_vis_figure_600dpi.png", mime="image/png", use_container_width=True)
        g_btn2.download_button("📐 Vector SVG", data=svg_bytes, file_name="uv_vis_figure.svg", mime="image/svg+xml", use_container_width=True)
        g_btn3.download_button("📄 Vector PDF", data=pdf_bytes, file_name="uv_vis_figure.pdf", mime="application/pdf", use_container_width=True)

        zip_bytes = build_analysis_bundle_zip(
            fig=fig,
            df_labplot=active_export_df,
            metrics={"domain": selected_domain, "mode": analysis_mode},
            technique="UV-Vis",
            summary_text=active_summary
        )
        st.download_button(
            "📦 Download Complete Publication Package (.ZIP)",
            data=zip_bytes,
            file_name="UV_Vis_Publication_Package.zip",
            mime="application/zip",
            use_container_width=True
        )
