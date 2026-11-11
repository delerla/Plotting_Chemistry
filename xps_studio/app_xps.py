"""
app.py - XPS Studio: Standalone Materials-Specific XPS Intelligence Platform
Authored & Maintained by Dr. Deler Langenberg (2026)
Dedicated for: MOFs & Frameworks, Solar Perovskites, PAN Nanofibers, and Catalysis.
"""

import sys
from pathlib import Path

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

try:
    from knowledge_base import ALL_DOMAINS
    from knowledge_base.benchmark_data import (
        generate_benchmark_mof_c1s,
        generate_benchmark_solar_pb4f,
        generate_benchmark_pan_n1s,
    )
    from core.calibration import apply_charge_calibration, CALIBRATION_STANDARDS
    from core.background import extract_net_signal
    from core.deconvolution import fit_xps_components
    from core.interpretation import interpret_xps_chemistry
    from visualizer.plot_core_level import render_core_level_plot
except ImportError:
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
        font-size: 1.90rem;
        font-weight: 800;
        color: #0f2b48;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 1.1rem;
        border: 1px solid #334155;
    }
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 10px;
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

DEFAULT_PEAK_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd',
    '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#7f7f7f', '#d62728'
]

# ==============================================================================
# SIDEBAR: DOMAIN SELECTION & CORE CONFIGURATION
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
    st.markdown("### 🎨 Journal Color Theme")
    selected_theme = st.selectbox(
        "Editorial Palette:",
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
            Interactive multi-peak deconvolution, physics constraints, editable publication typography & automated chemical reasoning.
        </div>
    </div>
    <div style="display: flex; gap: 4px; align-items: center;">
        <span class="badge badge-dark">Lead: Dr. Deler Langenberg</span>
        <span class="badge badge-blue">Pro Edition</span>
        <span class="badge badge-green">MIT License</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA INGESTION, ROI TRIMMING & FITTING CONTROLS
# ==============================================================================
col_ctrl, col_main = st.columns([1.05, 2.35])

with col_ctrl:
    st.subheader("1. Data & Physics Setup")
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
        st.success(f"Benchmark: **{selected_preset_name}**")
    else:
        uploaded_file = st.file_uploader(
            "Upload XPS Spectrum (CSV, XLSX, TXT, DAT):",
            type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "prn"],
            key="xps_file_up"
        )
        if uploaded_file is not None:
            parsed_df, _, meta = load_smart_file(uploaded_file.read(), filename=uploaded_file.name)
            if parsed_df is not None and not parsed_df.empty:
                raw_df = parsed_df
                st.success(f"Parsed {meta['rows']} pts from `{uploaded_file.name}`")
            else:
                st.error("Parsing failed. Using benchmark.")
                raw_df = generate_benchmark_mof_c1s()
        else:
            st.info("Awaiting upload. Showing benchmark.")
            raw_df = generate_benchmark_mof_c1s()

    clean_df = sanitize_spectral_dataframe(raw_df)
    if clean_df.shape[1] > 2:
        be_col = st.selectbox("Binding Energy Column (X):", clean_df.columns, index=0)
        cps_col = st.selectbox("Intensity / Counts Column (Y):", [c for c in clean_df.columns if c != be_col], index=0)
        df_xps = clean_df[[be_col, cps_col]]
    else:
        df_xps = clean_df

    x_full = df_xps.iloc[:, 0].to_numpy().astype(float)
    y_full = df_xps.iloc[:, 1].to_numpy().astype(float)

    # Energy Calibration
    with st.expander("⚖️ Charge Calibration", expanded=True):
        calib_mode = st.selectbox("Calibration Standard:", list(CALIBRATION_STANDARDS.keys()), index=0)
        manual_offset = st.number_input("Manual ΔE Shift (eV):", value=0.00, step=0.05, format="%.2f")
        x_calib_full, shift_applied, calib_status = apply_charge_calibration(
            x_full, y_full, method=calib_mode, manual_shift_eV=manual_offset
        )
        st.caption(f"⚡ {calib_status}")

    # Region of Interest (ROI) Trimming
    be_scan_min = float(np.nanmin(x_calib_full))
    be_scan_max = float(np.nanmax(x_calib_full))
    with st.expander("✂️ Energy Range (ROI Trim)", expanded=False):
        roi_range = st.slider(
            "Fit Window BE (eV):",
            min_value=round(be_scan_min, 2),
            max_value=round(be_scan_max, 2),
            value=(round(be_scan_min, 2), round(be_scan_max, 2)),
            step=0.1,
            help="Crop noisy tails before Shirley baseline subtraction."
        )

    roi_mask = (x_calib_full >= roi_range[0]) & (x_calib_full <= roi_range[1])
    x_calib = x_calib_full[roi_mask]
    y_raw = y_full[roi_mask]
    if len(x_calib) < 5:
        x_calib = x_calib_full
        y_raw = y_full

    # Baseline & Line Shape Physics
    with st.expander("📉 Baseline & Line Shape Model", expanded=True):
        baseline_method = st.selectbox(
            "Inelastic Background:",
            ["Shirley (Iterative)", "Linear", "Constant (Min)", "None (Zero)"],
            index=0
        )
        bg_curve, y_net = extract_net_signal(x_calib, y_raw, baseline_type=baseline_method)

        line_shape_model = st.selectbox(
            "Peak Profile Function:",
            ["Voigt", "Pseudo-Voigt (GL)", "Gaussian", "Lorentzian"],
            index=0,
            help="Voigt = true Gaussian⊗Lorentzian convolution; Pseudo-Voigt = GL(x) blend used in CasaXPS."
        )
        gl_mix = 0.30
        if "Pseudo" in line_shape_model:
            gl_pct = st.slider("Gaussian/Lorentzian Mix GL(%):", min_value=0, max_value=100, value=30, step=5)
            gl_mix = gl_pct / 100.0

        c_fw1, c_fw2 = st.columns(2)
        with c_fw1:
            fwhm_min = st.number_input("Min FWHM (eV):", min_value=0.1, max_value=2.0, value=0.40, step=0.05)
        with c_fw2:
            fwhm_max = st.number_input("Max FWHM (eV):", min_value=0.5, max_value=8.0, value=3.00, step=0.10)

        lock_fwhm_equal = st.checkbox("Constrain Equal FWHM Across Peaks", value=False)
        use_doublet_coupling = st.checkbox(
            "Enforce Spin-Orbit Doublet Constraints",
            value=bool(active_preset.get('is_doublet', False)),
            disabled=not bool(active_preset.get('is_doublet', False)),
            help="Locks spin-orbit splitting ΔE and theoretical branching ratios (2:1, 3:2, 4:3)."
        )
        n_fev = st.slider("Max Fit Iterations:", min_value=1000, max_value=8000, value=4000, step=500)


# ==============================================================================
# PEAK EDITOR, VISUALIZATION & TYPOGRAPHY CUSTOMIZER
# ==============================================================================
with col_main:
    # --------------------------------------------------------------------------
    # INTERACTIVE PEAK CONFIGURATION TABLE
    # --------------------------------------------------------------------------
    if "active_preset_tracker" not in st.session_state or st.session_state["active_preset_tracker"] != selected_preset_name:
        st.session_state["active_preset_tracker"] = selected_preset_name
        st.session_state["peak_editor_seed"] = 0
        st.session_state["preset_peaks_base"] = [
            {
                "Peak Name": c['name'],
                "Center (eV)": float(c['center']),
                "Tol ± (eV)": float(c.get('center_tol', 0.35)),
                "Fix Center": False,
                "Init Sigma": float(c.get('sigma', 0.55)),
                "Color": c.get('color', DEFAULT_PEAK_COLORS[i % len(DEFAULT_PEAK_COLORS)]),
                "Assignment": c.get('meaning', ''),
                "_prefix": c['prefix'],
                "_gamma": float(c.get('gamma', 0.25)),
            }
            for i, c in enumerate(active_preset.get('components', []))
        ]
        st.session_state["num_peaks_val"] = len(st.session_state["preset_peaks_base"])

    with st.expander("⛰️ Peak Fitting Setup (Number of Peaks, Centers, Constraints & Labels)", expanded=True):
        pk_top1, pk_top2, pk_top3 = st.columns([1.2, 1.2, 1.6])
        with pk_top1:
            num_peaks = st.number_input(
                "Number of Peaks to Fit:",
                min_value=1, max_value=10,
                value=int(st.session_state.get("num_peaks_val", 4)),
                step=1,
                key="num_peaks_input"
            )
            st.session_state["num_peaks_val"] = num_peaks
        with pk_top2:
            st.write("")
            if st.button("🔄 Reset Peaks to Preset", use_container_width=True):
                st.session_state["active_preset_tracker"] = None
                st.rerun()
        with pk_top3:
            st.caption("Edit peak names, centers (eV), tolerances, fix locks, colors, or assignments directly below:")

        # Dynamically resize peak rows cleanly
        base_rows = list(st.session_state["preset_peaks_base"])
        while len(base_rows) < num_peaks:
            idx_new = len(base_rows) + 1
            mid_be = float(np.mean(x_calib)) if len(x_calib) > 0 else 285.0
            offset_be = (idx_new - 1) * 1.1 - 1.5
            guess_be = round(float(np.clip(mid_be + offset_be, be_scan_min + 0.2, be_scan_max - 0.2)), 2)
            base_rows.append({
                "Peak Name": f"Peak {idx_new}",
                "Center (eV)": guess_be,
                "Tol ± (eV)": 0.50,
                "Fix Center": False,
                "Init Sigma": 0.55,
                "Color": DEFAULT_PEAK_COLORS[(idx_new - 1) % len(DEFAULT_PEAK_COLORS)],
                "Assignment": "User-defined component",
                "_prefix": f"custom_p{idx_new}_",
                "_gamma": 0.25,
            })
        base_rows = base_rows[:num_peaks]
        st.session_state["preset_peaks_base"] = base_rows

        editor_df_input = pd.DataFrame(base_rows)[[
            "Peak Name", "Center (eV)", "Tol ± (eV)", "Fix Center", "Init Sigma", "Color", "Assignment"
        ]]
        edited_peaks_df = st.data_editor(
            editor_df_input,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Peak Name": st.column_config.TextColumn("Peak Label / Name", required=True),
                "Center (eV)": st.column_config.NumberColumn("Initial Center (eV)", format="%.2f", step=0.1),
                "Tol ± (eV)": st.column_config.NumberColumn("Window ± (eV)", min_value=0.0, max_value=5.0, format="%.2f", step=0.05),
                "Fix Center": st.column_config.CheckboxColumn("Lock Center"),
                "Init Sigma": st.column_config.NumberColumn("Width σ", min_value=0.1, max_value=3.0, format="%.2f", step=0.05),
                "Color": st.column_config.TextColumn("Hex Color"),
                "Assignment": st.column_config.TextColumn("Chemical Assignment"),
            },
            key=f"pk_table_{selected_preset_name}_{num_peaks}_{st.session_state.get('peak_editor_seed', 0)}"
        )

    # Convert edited table rows back into deconvolution config dictionaries
    components_cfg = []
    for i, row in edited_peaks_df.iterrows():
        orig = base_rows[i]
        components_cfg.append({
            'prefix': orig.get('_prefix', f'p{i}_'),
            'name': str(row['Peak Name']),
            'center': float(row['Center (eV)']),
            'center_tol': float(row['Tol ± (eV)']),
            'fix_center': bool(row['Fix Center']),
            'sigma': float(row['Init Sigma']),
            'gamma': float(orig.get('_gamma', 0.25)),
            'color': str(row['Color']).strip(),
            'meaning': str(row['Assignment']),
        })

    # --------------------------------------------------------------------------
    # EDITABLE TYPOGRAPHY, LEGEND & ANNOTATION STUDIO
    # --------------------------------------------------------------------------
    with st.expander("🎨 Publication Figure Studio (Editable Titles, Axes, Legend & On-Plot Peak Labels)", expanded=False):
        tab_txt, tab_leg, tab_ann, tab_lay = st.tabs([
            "📝 Titles & Axes", "🏷️ Legend Controls", "📍 On-Plot Peak Labels", "📐 Layout & Style"
        ])

        with tab_txt:
            tc1, tc2 = st.columns(2)
            with tc1:
                edit_title = st.text_input("Plot Title (leave blank for none):", value=f"{active_preset.get('core_level', 'XPS')} High-Resolution Deconvolution")
                edit_xlabel = st.text_input("X-Axis Label:", value="Binding Energy (eV)")
                edit_ylabel = st.text_input("Y-Axis Label:", value="Intensity (Counts / s)")
            with tc2:
                edit_res_ylabel = st.text_input("Residual Panel Y-Label:", value="ΔI")
                fs_title = st.slider("Title Font Size:", 9, 20, 13)
                fs_axes = st.slider("Axis Label Font Size:", 9, 18, 12)
                fs_ticks = st.slider("Tick Font Size:", 7, 15, 10)
                bold_fonts = st.checkbox("Bold Titles & Axis Labels", value=True)

        with tab_leg:
            lc1, lc2 = st.columns(2)
            with lc1:
                show_legend = st.checkbox("Show Legend on Plot", value=True)
                legend_title = st.text_input("Legend Header Title:", value="Chemical States")
                legend_loc = st.selectbox(
                    "Legend Position:",
                    ["upper left", "upper right", "lower left", "lower right", "best", "outside right"],
                    index=0
                )
                legend_fs = st.slider("Legend Font Size:", 6.5, 13.0, 8.8, step=0.2)
            with lc2:
                legend_raw_lbl = st.text_input("Raw Data Legend Label:", value="Experimental Data")
                legend_bg_lbl = st.text_input("Baseline Legend Label:", value="Shirley Baseline" if "Shirley" in baseline_method else f"{baseline_method} Baseline")
                legend_env_lbl = st.text_input("Envelope Fit Legend Label:", value="Envelope Fit")
                legend_stats = st.checkbox("Include BE & Area% inside Legend", value=True)

        with tab_ann:
            ac1, ac2 = st.columns(2)
            with ac1:
                peak_lbl_mode = st.selectbox(
                    "On-Plot Peak Label Format:",
                    ["None", "Name Only", "Binding Energy (eV)", "Name + BE", "Name + BE + Area%"],
                    index=3,
                    help="Annotates fitted chemical states directly above each peak apex."
                )
                peak_lbl_rot = st.radio("Annotation Orientation:", [0, 90], format_func=lambda x: "Horizontal (0°)" if x == 0 else "Vertical (90°)", horizontal=True)
                show_drop_lines = st.checkbox("Show Leader / Drop-Lines to Peak Apex", value=True)
            with ac2:
                peak_lbl_fs = st.slider("Peak Annotation Font Size:", 6.5, 13.0, 8.5, step=0.2)
                peak_lbl_offset = st.slider("Vertical Label Offset (% of span):", 1.0, 20.0, 5.0, step=0.5)

        with tab_lay:
            yc1, yc2 = st.columns(2)
            with yc1:
                show_residuals = st.checkbox("Show Upper Residuals Panel (ΔI)", value=True)
                show_stats_box = st.checkbox("Show Scientific Fit Quality Box (R², χ²ν, ΔE)", value=True)
                invert_x = st.checkbox("Invert X-Axis (Standard XPS: High -> Low BE)", value=True)
                raw_style = st.selectbox("Experimental Data Style:", ["Open Circles", "Solid Dots", "Thin Line", "Dots + Line"], index=0)
            with yc2:
                show_yticks = st.checkbox("Show Y-Axis Tick Numbers", value=True)
                show_grid = st.checkbox("Show Subtle Gridlines", value=False)
                fig_w = st.slider("Figure Width (inches):", 5.0, 14.0, 8.5, step=0.5)
                fig_h = st.slider("Figure Height (inches):", 4.0, 11.0, 7.5, step=0.5)

    # --------------------------------------------------------------------------
    # EXECUTE DECONVOLUTION & RENDER FIGURE
    # --------------------------------------------------------------------------
    doublet_info = {
        'is_doublet': bool(use_doublet_coupling and active_preset.get('is_doublet', False)),
        'doublet_delta_eV': active_preset.get('doublet_delta_eV', 0.0),
        'branching_ratio': active_preset.get('branching_ratio', 1.0)
    }

    try:
        fit_result, comp_curves, comp_summary, r2 = fit_xps_components(
            x_calib, y_net, components_cfg,
            doublet_info=doublet_info,
            line_shape=line_shape_model,
            fwhm_bounds=(fwhm_min, fwhm_max),
            lock_fwhm_equal=lock_fwhm_equal,
            gl_fraction=gl_mix,
            max_nfev=n_fev
        )

        plot_cfg = {
            'title': edit_title,
            'xlabel': edit_xlabel,
            'ylabel': edit_ylabel,
            'res_ylabel': edit_res_ylabel,
            'title_fontsize': fs_title,
            'label_fontsize': fs_axes,
            'tick_fontsize': fs_ticks,
            'font_bold': bold_fonts,
            'show_legend': show_legend,
            'legend_title': legend_title,
            'legend_loc': legend_loc,
            'legend_fontsize': legend_fs,
            'legend_raw_label': legend_raw_lbl,
            'legend_bg_label': legend_bg_lbl,
            'legend_env_label': legend_env_lbl,
            'legend_include_stats': legend_stats,
            'peak_label_mode': peak_lbl_mode,
            'peak_label_rotation': peak_lbl_rot,
            'peak_label_fontsize': peak_lbl_fs,
            'peak_label_offset_pct': peak_lbl_offset,
            'show_drop_lines': show_drop_lines,
            'show_residuals': show_residuals,
            'show_stats_box': show_stats_box,
            'stats_extras': {
                'r2': r2,
                'redchi': float(fit_result.redchi) if hasattr(fit_result, 'redchi') else None,
                'calib_shift': shift_applied
            },
            'invert_xaxis': invert_x,
            'show_yticks': show_yticks,
            'show_grid': show_grid,
            'raw_style': raw_style,
            'fig_width': fig_w,
            'fig_height': fig_h
        }

        fig_xps, labplot_df = render_core_level_plot(
            x_calib, y_raw, bg_curve, fit_result, comp_curves, comp_summary,
            core_label=active_preset.get('core_level', 'XPS'),
            theme=selected_theme,
            plot_config=plot_cfg
        )
        st.pyplot(fig_xps)

        # Fit Statistics Strip
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Fit R²", f"{r2:.5f}")
        s2.metric("Reduced χ²", f"{fit_result.redchi:.2f}")
        s3.metric("Active Peaks", f"{len(comp_summary)}")
        s4.metric("Calib Shift ΔE", f"{shift_applied:+.2f} eV")

        # ----------------------------------------------------------------------
        # AUTOMATED SCIENTIFIC INTERPRETATION & DEFECT REPORT
        # ----------------------------------------------------------------------
        interp_results = interpret_xps_chemistry(
            comp_summary, preset_dict=active_preset, core_level=active_preset.get('core_level', 'C 1s')
        )

        st.markdown("### 🧠 Automated Chemical Reasoning & Defect Report")
        if interp_results['metrics']:
            m_cols = st.columns(len(interp_results['metrics']))
            for idx, (m_key, m_val) in enumerate(interp_results['metrics'].items()):
                with m_cols[idx]:
                    st.metric(
                        label=m_val['name'],
                        value=f"{m_val['value']:.2f} {m_val['unit']}".strip()
                    )

        if interp_results['insights']:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            for ins in interp_results['insights']:
                st.markdown(f"**✓ Insight:** {ins}")
            st.markdown('</div>', unsafe_allow_html=True)

        if interp_results['warnings']:
            for w in interp_results['warnings']:
                st.markdown(f'<div class="warning-box">⚠️ <b>Defect Notice:</b> {w}</div>', unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # QUANTIFICATION TABLE
        # ----------------------------------------------------------------------
        with st.expander("📊 Quantified Deconvolution Metrics & Component Properties", expanded=True):
            table_rows = []
            for name, d in comp_summary.items():
                table_rows.append({
                    "Chemical State": name,
                    "Line Shape": d.get('Line_Shape', line_shape_model),
                    "Binding Energy (eV)": d['Binding_Energy_eV'],
                    "FWHM (eV)": d['FWHM_eV'],
                    "Area (Counts·eV)": d['Area_cps_eV'],
                    "Area Fraction (%)": f"{d['Area_Percent']:.2f}%",
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
            title=edit_title or f"XPS Analysis: {selected_preset_name}",
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
