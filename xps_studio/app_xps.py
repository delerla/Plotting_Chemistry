"""
app.py - XPS Studio: Lightweight, Apply-Driven Materials-Specific XPS Intelligence Platform
Authored & Maintained by Dr. Deler Langenberg (2026)
Dedicated for: MOFs & Frameworks, Solar Perovskites, PAN Nanofibers, and Catalysis.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PKG_DIR = Path(__file__).resolve().parent
for _p in (str(PKG_DIR), str(BASE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.export_utils import (
    PUBLICATION_PALETTES,
    build_analysis_bundle_zip,
    get_figure_bytes,
    get_labplot_ascii_bytes,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
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
    from knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from modules.institutional_verifier import verify_against_saudi_databank
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
    from xps_studio.knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from xps_studio.modules.institutional_verifier import verify_against_saudi_databank

try:
    from xps_studio.modules.counter_module import (
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
                st.markdown('<a href="https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding: 5px 12px; background: #38bdf8; color: #0f172a !important; border-radius: 5px; text-decoration: none !important; font-weight: 700; font-size: 0.80rem;">🏠 ⟵ Master Characterization Hub</a>', unsafe_allow_html=True)
            def render_unified_studio_footer(active_domain_key: str, studio_title: str, studio_subtitle: str):
                st.markdown(f'<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.82rem;"><strong>{studio_title}</strong> • {studio_subtitle}<br/>Lead: Dr. Deler Langenberg (MIT License)</div>', unsafe_allow_html=True)

# Page Configuration
st.set_page_config(
    page_title="XPS Studio - Dr. Deler Langenberg",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lightweight System CSS (No blocking external font network requests)
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .xps-header {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f2b48;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 13px;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 11px 15px;
        border-radius: 6px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 9px 13px;
        border-radius: 6px;
        color: #92400e;
        margin-top: 8px;
        font-size: 0.89rem;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.73rem;
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


@st.cache_data(show_spinner=False)
def _cached_parse_file(raw_bytes: bytes, filename: str):
    return load_smart_file(raw_bytes, filename=filename)


@st.cache_data(show_spinner=False)
def _cached_benchmark_df(preset_name: str):
    low = preset_name.lower()
    if "perovskite" in low or "pb" in low:
        return generate_benchmark_solar_pb4f()
    elif "pan" in low or "nitrile" in low:
        return generate_benchmark_pan_n1s()
    else:
        return generate_benchmark_mof_c1s()


# ==============================================================================
# SIDEBAR: DOMAIN SELECTION & BRANDING
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Platform Owner & Lead</div>
        <div style="font-size: 1.2rem; font-weight: 800; color: #38bdf8;">Dr. Deler Langenberg</div>
        <div style="font-size: 0.79rem; color: #cbd5e1; margin-top: 3px;">
            XPS Intelligence Engine & Computational Spectroscopy
        </div>
        <div style="display: flex; gap: 6px; margin-top: 9px;">
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="text-decoration: none; background: #334155; color: #f8fafc; padding: 4px 10px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">⭐ GitHub</a>
            <a href="mailto:delerla@yahoo.de" style="text-decoration: none; background: #0284c7; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">✉️ Email</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Material Domain & Preset")
    selected_domain = st.selectbox(
        "Field of Study:",
        list(ALL_DOMAINS.keys()),
        index=0,
        help="Loads domain-specific chemistry, spin-orbit coupling rules, and defect models."
    )

    domain_presets = ALL_DOMAINS[selected_domain]
    preset_names = list(domain_presets.keys())
    selected_preset_name = st.selectbox("Spectral Chemistry Preset:", preset_names)
    active_preset = domain_presets[selected_preset_name]

    with st.expander("🇸🇦 Saudi Alliance Databank (KFUPM, KACST, KAUST, IAU)", expanded=False):
        sq = st.text_input("🔍 Filter Materials / Literature:", placeholder="UiO-66, Perovskite, TiO2, MXene...", key="xps_saudi_sq")
        inst_choice = st.selectbox(
            "Institution Focus:",
            ["All Saudi Alliance Partners", "KAUST", "KFUPM", "KACST", "IAU (iau.edu.sa)"],
            key="xps_saudi_inst"
        )
        sub_code = inst_choice.split()[0] if "All" not in inst_choice else ""
        from knowledge_base.saudi_research_databank import search_saudi_databank
        bms = search_saudi_databank(query=sq, institution=sub_code, technique="XPS")
        if bms:
            bm_titles = [f"{b['material_name']} ({'/'.join(b['institutions'])})" for b in bms]
            sel_idx = st.selectbox("Institutional References:", range(len(bm_titles)), format_func=lambda i: bm_titles[i], key="xps_saudi_bm_select")
            active_saudi_bm = bms[sel_idx]
            st.markdown(f"**Pillar:** *{active_saudi_bm['pillar']}*")
            st.markdown(f"**Partners:** {', '.join(active_saudi_bm['institutions'])}")
            st.caption(f"**Key Citation:** {active_saudi_bm['primary_citation']}")
            with st.expander("📖 Expected XPS Core Levels", expanded=False):
                if "xps_benchmarks" in active_saudi_bm:
                    for k, v in active_saudi_bm["xps_benchmarks"].get("binding_energies", {}).items():
                        st.markdown(f"- **{k}**: `{v:.1f} eV`")
                    st.caption(active_saudi_bm["xps_benchmarks"].get("ratio_diagnostic", ""))
        else:
            st.caption("No matching benchmarks found.")

    st.markdown("---")
    st.markdown("### 2. Publication Typography & Style")
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

    # Real-Time Domain Visitor Counter
    render_sidebar_counter("xps_studio")

# ==============================================================================
# MAIN PAGE HEADER & UNIFIED ECOSYSTEM NAVIGATION
# ==============================================================================
render_studio_navigation_bar("xps_studio")

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.65rem; margin-bottom: 1rem; flex-wrap: wrap; gap: 8px;">
    <div>
        <div class="xps-header">⚡ XPS Studio: High-Resolution Core-Level Intelligence</div>
        <div style="font-size: 0.88rem; color: #475569;">
            Lightweight, Apply-driven multi-peak deconvolution, editable typography & automated chemical reasoning.
        </div>
    </div>
    <div style="display: flex; gap: 4px; align-items: center;">
        <span class="badge badge-dark">Lead: Dr. Deler Langenberg</span>
        <span class="badge badge-blue">Fast Lightweight Mode</span>
        <span class="badge badge-green">MIT License</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA INGESTION
# ==============================================================================
col_ctrl, col_main = st.columns([1.05, 2.35])

with col_ctrl:
    st.subheader("1. Data Source")
    data_source = st.radio(
        "Input Source:",
        ["Load Domain Benchmark", "Upload Experimental Data (ASCII/CSV/Excel)"],
        key="xps_src"
    )

    file_sig = "benchmark"
    if data_source == "Load Domain Benchmark":
        raw_df = _cached_benchmark_df(selected_preset_name)
        st.success(f"Loaded: **{selected_preset_name}**")
    else:
        uploaded_file = st.file_uploader(
            "Upload XPS Spectrum (CSV, XLSX, TXT, DAT):",
            type=["csv", "xlsx", "xls", "txt", "dat", "tsv", "asc", "prn"],
            key="xps_file_up"
        )
        if uploaded_file is not None:
            f_bytes = uploaded_file.getvalue()
            file_sig = f"{uploaded_file.name}_{len(f_bytes)}"
            parsed_df, _, meta = _cached_parse_file(f_bytes, uploaded_file.name)
            if parsed_df is not None and not parsed_df.empty:
                raw_df = parsed_df
                st.success(f"Loaded {meta['rows']} pts (`{uploaded_file.name}`)")
            else:
                st.error("Parsing failed. Showing benchmark.")
                raw_df = _cached_benchmark_df(selected_preset_name)
        else:
            st.info("Awaiting upload. Showing benchmark.")
            raw_df = _cached_benchmark_df(selected_preset_name)

    clean_df = sanitize_spectral_dataframe(raw_df)
    if clean_df.shape[1] > 2:
        be_col = st.selectbox("Binding Energy Column (X):", clean_df.columns, index=0)
        cps_col = st.selectbox("Intensity / Counts Column (Y):", [c for c in clean_df.columns if c != be_col], index=0)
        df_xps = clean_df[[be_col, cps_col]]
    else:
        df_xps = clean_df

    x_full = df_xps.iloc[:, 0].to_numpy().astype(float)
    y_full = df_xps.iloc[:, 1].to_numpy().astype(float)
    be_scan_min = float(np.nanmin(x_full))
    be_scan_max = float(np.nanmax(x_full))

    # --------------------------------------------------------------------------
    # FORM 1: PHYSICS, CALIBRATION, ROI & BASELINE SETTINGS
    # --------------------------------------------------------------------------
    with st.form("physics_calibration_form"):
        st.subheader("2. Calibration & Physics")
        calib_mode = st.selectbox("Calibration Standard:", list(CALIBRATION_STANDARDS.keys()), index=0)
        manual_offset = st.number_input("Manual ΔE Shift (eV):", value=0.00, step=0.05, format="%.2f")

        roi_range = st.slider(
            "Fit Energy Window ROI (eV):",
            min_value=round(be_scan_min - 5.0, 1),
            max_value=round(be_scan_max + 5.0, 1),
            value=(round(be_scan_min, 1), round(be_scan_max, 1)),
            step=0.1,
            help="Trim noisy tails before background subtraction."
        )

        baseline_method = st.selectbox(
            "Inelastic Background:",
            ["Shirley (Iterative)", "Linear", "Constant (Min)", "None (Zero)"],
            index=0
        )

        line_shape_model = st.selectbox(
            "Peak Profile Model:",
            ["Voigt", "Pseudo-Voigt (GL)", "Gaussian", "Lorentzian"],
            index=0
        )
        gl_pct = st.slider("Pseudo-Voigt GL(%) Mix:", min_value=0, max_value=100, value=30, step=5)

        c_fw1, c_fw2 = st.columns(2)
        with c_fw1:
            fwhm_min = st.number_input("Min FWHM (eV):", min_value=0.1, max_value=2.0, value=0.40, step=0.05)
        with c_fw2:
            fwhm_max = st.number_input("Max FWHM (eV):", min_value=0.5, max_value=8.0, value=3.00, step=0.10)

        lock_fwhm_equal = st.checkbox("Constrain Equal FWHM Across Peaks", value=False)
        use_doublet_coupling = st.checkbox(
            "Couple Spin-Orbit Doublets",
            value=bool(active_preset.get('is_doublet', False)),
            disabled=not bool(active_preset.get('is_doublet', False))
        )
        n_fev = st.slider("Max Iterations:", min_value=1000, max_value=8000, value=3000, step=500)

        apply_physics_btn = st.form_submit_button("⚡ Apply Physics & Run Fit", type="primary", use_container_width=True)


# ==============================================================================
# PEAK STATE & TYPOGRAPHY DEFAULTS INITIALIZATION
# ==============================================================================
preset_sig = f"{selected_preset_name}__{file_sig}"

if st.session_state.get("active_preset_tracker") != selected_preset_name:
    st.session_state["active_preset_tracker"] = selected_preset_name
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
    st.session_state["xps_style_cfg"] = {
        'title': f"{active_preset.get('core_level', 'XPS')} High-Resolution Deconvolution",
        'xlabel': "Binding Energy (eV)",
        'ylabel': "Intensity (Counts / s)",
        'res_ylabel': "ΔI",
        'title_fontsize': 13,
        'label_fontsize': 12,
        'tick_fontsize': 10,
        'font_bold': True,
        'show_legend': True,
        'legend_title': "Chemical States",
        'legend_loc': "upper left",
        'legend_fontsize': 8.8,
        'legend_raw_label': "Experimental Data",
        'legend_bg_label': "Shirley Baseline",
        'legend_env_label': "Envelope Fit",
        'legend_include_stats': True,
        'peak_label_mode': "Name + BE",
        'peak_label_rotation': 0,
        'peak_label_fontsize': 8.5,
        'peak_label_offset_pct': 5.0,
        'show_drop_lines': True,
        'show_residuals': True,
        'show_stats_box': True,
        'invert_xaxis': True,
        'show_yticks': True,
        'show_grid': False,
        'raw_style': "Open Circles",
        'fig_width': 8.5,
        'fig_height': 7.5,
    }


# ==============================================================================
# RIGHT WORKSPACE: PEAK TABLE, APPLY BUTTONS, VISUALIZATION & EXPORTS
# ==============================================================================
with col_main:
    # --------------------------------------------------------------------------
    # 3. PEAK CONFIGURATION SECTION WITH EXPLICIT APPLY BUTTON
    # --------------------------------------------------------------------------
    with st.expander("⛰️ Peak Setup (Number of Peaks, Centers, Constraints & Labels)", expanded=False):
        pk_c1, pk_c2, pk_c3 = st.columns([1.1, 1.1, 1.8])
        with pk_c1:
            num_peaks = st.number_input(
                "Number of Peaks:",
                min_value=1, max_value=10,
                value=int(st.session_state.get("num_peaks_val", 4)),
                step=1,
                key="num_peaks_input"
            )
            st.session_state["num_peaks_val"] = num_peaks
        with pk_c2:
            st.write("")
            if st.button("🔄 Reset to Preset", use_container_width=True):
                st.session_state["active_preset_tracker"] = None
                st.session_state.pop("xps_fit_cache", None)
                st.rerun()
        with pk_c3:
            st.caption("Edit peak parameters below, then click **Apply Peak Setup & Run Fit**.")

        base_rows = list(st.session_state["preset_peaks_base"])
        while len(base_rows) < num_peaks:
            idx_new = len(base_rows) + 1
            mid_be = float(np.mean(x_full)) if len(x_full) > 0 else 285.0
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
                "Center (eV)": st.column_config.NumberColumn("Center (eV)", format="%.2f", step=0.1),
                "Tol ± (eV)": st.column_config.NumberColumn("Tol ± (eV)", min_value=0.0, max_value=5.0, format="%.2f", step=0.05),
                "Fix Center": st.column_config.CheckboxColumn("Lock"),
                "Init Sigma": st.column_config.NumberColumn("Width σ", min_value=0.1, max_value=3.0, format="%.2f", step=0.05),
                "Color": st.column_config.TextColumn("Hex Color"),
                "Assignment": st.column_config.TextColumn("Chemical Meaning"),
            },
            key=f"pk_table_{selected_preset_name}_{num_peaks}"
        )
        apply_peaks_btn = st.button("🚀 Apply Peak Setup & Run Fit", type="primary", use_container_width=True)

    # --------------------------------------------------------------------------
    # 4. TYPOGRAPHY & STYLE STUDIO (FORM WITH APPLY BUTTON -> ZERO LAG TYPING)
    # --------------------------------------------------------------------------
    with st.expander("🎨 Publication Figure Studio (Editable Texts, Legend & Annotations)", expanded=False):
        with st.form("typography_style_form"):
            cur_cfg = st.session_state["xps_style_cfg"]
            t_txt, t_leg, t_ann, t_lay = st.tabs([
                "📝 Titles & Axes", "🏷️ Legend Controls", "📍 On-Plot Peak Labels", "📐 Layout & Style"
            ])

            with t_txt:
                tc1, tc2 = st.columns(2)
                with tc1:
                    f_title = st.text_input("Plot Title (blank = none):", value=cur_cfg['title'])
                    f_xlabel = st.text_input("X-Axis Label:", value=cur_cfg['xlabel'])
                    f_ylabel = st.text_input("Y-Axis Label:", value=cur_cfg['ylabel'])
                with tc2:
                    f_res_ylabel = st.text_input("Residual Y-Label:", value=cur_cfg['res_ylabel'])
                    f_fs_title = st.slider("Title Font Size:", 9, 20, int(cur_cfg['title_fontsize']))
                    f_fs_axes = st.slider("Axis Label Font Size:", 9, 18, int(cur_cfg['label_fontsize']))
                    f_fs_ticks = st.slider("Tick Font Size:", 7, 15, int(cur_cfg['tick_fontsize']))
                    f_bold = st.checkbox("Bold Titles & Axis Labels", value=bool(cur_cfg['font_bold']))

            with t_leg:
                lc1, lc2 = st.columns(2)
                with lc1:
                    f_show_leg = st.checkbox("Show Legend", value=bool(cur_cfg['show_legend']))
                    f_leg_title = st.text_input("Legend Header Title:", value=cur_cfg['legend_title'])
                    loc_opts = ["upper left", "upper right", "lower left", "lower right", "best", "outside right"]
                    f_leg_loc = st.selectbox("Legend Position:", loc_opts, index=loc_opts.index(cur_cfg['legend_loc']))
                    f_leg_fs = st.slider("Legend Font Size:", 6.5, 13.0, float(cur_cfg['legend_fontsize']), step=0.2)
                with lc2:
                    f_leg_raw = st.text_input("Raw Data Label:", value=cur_cfg['legend_raw_label'])
                    f_leg_bg = st.text_input("Baseline Label:", value=cur_cfg['legend_bg_label'])
                    f_leg_env = st.text_input("Envelope Label:", value=cur_cfg['legend_env_label'])
                    f_leg_stats = st.checkbox("Show BE & Area% in Legend", value=bool(cur_cfg['legend_include_stats']))

            with t_ann:
                ac1, ac2 = st.columns(2)
                with ac1:
                    ann_opts = ["None", "Name Only", "Binding Energy (eV)", "Name + BE", "Name + BE + Area%"]
                    f_pk_mode = st.selectbox("Peak Label Format:", ann_opts, index=ann_opts.index(cur_cfg['peak_label_mode']))
                    f_pk_rot = st.radio("Orientation:", [0, 90], index=0 if cur_cfg['peak_label_rotation'] == 0 else 1, format_func=lambda x: "Horizontal (0°)" if x == 0 else "Vertical (90°)", horizontal=True)
                    f_drop = st.checkbox("Show Drop-Lines to Peak Apex", value=bool(cur_cfg['show_drop_lines']))
                with ac2:
                    f_pk_fs = st.slider("Peak Label Font Size:", 6.5, 13.0, float(cur_cfg['peak_label_fontsize']), step=0.2)
                    f_pk_off = st.slider("Vertical Offset (% span):", 1.0, 20.0, float(cur_cfg['peak_label_offset_pct']), step=0.5)

            with t_lay:
                yc1, yc2 = st.columns(2)
                with yc1:
                    f_show_res = st.checkbox("Show Upper Residuals Panel (ΔI)", value=bool(cur_cfg['show_residuals']))
                    f_show_box = st.checkbox("Show Fit Quality Box (R², χ²ν, ΔE)", value=bool(cur_cfg['show_stats_box']))
                    f_inv_x = st.checkbox("Invert X-Axis (High -> Low BE)", value=bool(cur_cfg['invert_xaxis']))
                    raw_opts = ["Open Circles", "Solid Dots", "Thin Line", "Dots + Line"]
                    f_raw_sty = st.selectbox("Raw Data Style:", raw_opts, index=raw_opts.index(cur_cfg['raw_style']))
                with yc2:
                    f_yticks = st.checkbox("Show Y-Axis Ticks", value=bool(cur_cfg['show_yticks']))
                    f_grid = st.checkbox("Show Gridlines", value=bool(cur_cfg['show_grid']))
                    f_fig_w = st.slider("Figure Width (in):", 5.0, 14.0, float(cur_cfg['fig_width']), step=0.5)
                    f_fig_h = st.slider("Figure Height (in):", 4.0, 11.0, float(cur_cfg['fig_height']), step=0.5)

            apply_style_btn = st.form_submit_button("🎨 Apply Figure Style & Typography", type="primary", use_container_width=True)

            if apply_style_btn:
                st.session_state["xps_style_cfg"] = {
                    'title': f_title,
                    'xlabel': f_xlabel,
                    'ylabel': f_ylabel,
                    'res_ylabel': f_res_ylabel,
                    'title_fontsize': f_fs_title,
                    'label_fontsize': f_fs_axes,
                    'tick_fontsize': f_fs_ticks,
                    'font_bold': f_bold,
                    'show_legend': f_show_leg,
                    'legend_title': f_leg_title,
                    'legend_loc': f_leg_loc,
                    'legend_fontsize': f_leg_fs,
                    'legend_raw_label': f_leg_raw,
                    'legend_bg_label': f_leg_bg,
                    'legend_env_label': f_leg_env,
                    'legend_include_stats': f_leg_stats,
                    'peak_label_mode': f_pk_mode,
                    'peak_label_rotation': f_pk_rot,
                    'peak_label_fontsize': f_pk_fs,
                    'peak_label_offset_pct': f_pk_off,
                    'show_drop_lines': f_drop,
                    'show_residuals': f_show_res,
                    'show_stats_box': f_show_box,
                    'invert_xaxis': f_inv_x,
                    'show_yticks': f_yticks,
                    'show_grid': f_grid,
                    'raw_style': f_raw_sty,
                    'fig_width': f_fig_w,
                    'fig_height': f_fig_h,
                }
                st.session_state.pop("xps_export_cache", None)

    # --------------------------------------------------------------------------
    # RUN FITTING ONLY ON INITIAL LOAD OR WHEN AN APPLY BUTTON IS CLICKED
    # --------------------------------------------------------------------------
    need_initial_fit = (
        "xps_fit_cache" not in st.session_state
        or st.session_state["xps_fit_cache"].get("sig") != preset_sig
    )

    if need_initial_fit or apply_physics_btn or apply_peaks_btn:
        # Build component configs from table
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

        with st.spinner("Running physics-constrained optimization..."):
            x_calib_full, shift_applied, calib_status = apply_charge_calibration(
                x_full, y_full, method=calib_mode, manual_shift_eV=manual_offset
            )
            roi_mask = (x_calib_full >= roi_range[0]) & (x_calib_full <= roi_range[1])
            x_calib = x_calib_full[roi_mask]
            y_raw = y_full[roi_mask]
            if len(x_calib) < 5:
                x_calib = x_calib_full
                y_raw = y_full

            bg_curve, y_net = extract_net_signal(x_calib, y_raw, baseline_type=baseline_method)
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
                    gl_fraction=gl_pct / 100.0,
                    max_nfev=n_fev
                )
                st.session_state["xps_fit_cache"] = {
                    'sig': preset_sig,
                    'x_calib': x_calib,
                    'y_raw': y_raw,
                    'bg_curve': bg_curve,
                    'fit_result': fit_result,
                    'comp_curves': comp_curves,
                    'comp_summary': comp_summary,
                    'r2': r2,
                    'shift_applied': shift_applied,
                    'calib_status': calib_status,
                    'line_shape_model': line_shape_model,
                    'active_preset': active_preset,
                    'preset_name': selected_preset_name
                }
                st.session_state.pop("xps_export_cache", None)
            except Exception as e:
                st.error(f"Deconvolution Error: {e}")

    # --------------------------------------------------------------------------
    # RENDER VISUALIZATION & REPORT FROM CACHED FIT (ULTRA FAST)
    # --------------------------------------------------------------------------
    if "xps_fit_cache" in st.session_state:
        fc = st.session_state["xps_fit_cache"]
        st.caption(f"⚡ {fc['calib_status']}")

        plot_cfg = dict(st.session_state["xps_style_cfg"])
        plot_cfg['screen_dpi'] = 130  # Crisp screen resolution, 4x faster rendering
        plot_cfg['stats_extras'] = {
            'r2': fc['r2'],
            'redchi': float(fc['fit_result'].redchi) if hasattr(fc['fit_result'], 'redchi') else None,
            'calib_shift': fc['shift_applied']
        }

        fig_xps, labplot_df = render_core_level_plot(
            fc['x_calib'], fc['y_raw'], fc['bg_curve'],
            fc['fit_result'], fc['comp_curves'], fc['comp_summary'],
            core_label=fc['active_preset'].get('core_level', 'XPS'),
            theme=selected_theme,
            plot_config=plot_cfg
        )
        st.pyplot(fig_xps)

        # Metrics Strip
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Fit R²", f"{fc['r2']:.5f}")
        s2.metric("Reduced χ²", f"{fc['fit_result'].redchi:.2f}")
        s3.metric("Active Peaks", f"{len(fc['comp_summary'])}")
        s4.metric("Calib Shift ΔE", f"{fc['shift_applied']:+.2f} eV")

        # Interpretation Engine
        interp_results = interpret_xps_chemistry(
            fc['comp_summary'],
            preset_dict=fc['active_preset'],
            core_level=fc['active_preset'].get('core_level', 'C 1s')
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

        # Summary Table
        with st.expander("📊 Quantified Deconvolution Metrics & Component Properties", expanded=True):
            table_rows = []
            for name, d in fc['comp_summary'].items():
                table_rows.append({
                    "Chemical State": name,
                    "Line Shape": d.get('Line_Shape', fc['line_shape_model']),
                    "Binding Energy (eV)": d['Binding_Energy_eV'],
                    "FWHM (eV)": d['FWHM_eV'],
                    "Area (Counts·eV)": d['Area_cps_eV'],
                    "Area Fraction (%)": f"{d['Area_Percent']:.2f}%",
                    "Chemical Assignment": d['Meaning']
                })
            quant_df = pd.DataFrame(table_rows)
            st.dataframe(quant_df, use_container_width=True)

        # Saudi Research Alliance Cross-Auditing & Literature Verification
        saudi_verif = verify_against_saudi_databank(
            technique="XPS",
            fitted_components=fc['comp_summary'],
            material_hint=selected_preset_name
        )
        with st.expander(f"🏛️ Saudi Alliance Literature Benchmark: {saudi_verif['material_name']} ({saudi_verif['match_percentage']:.0f}% Match)", expanded=True):
            st.markdown(f"""
            <div style="background: #f8fafc; border-left: 5px solid {saudi_verif['verdict_color']}; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;">
                <span style="font-weight: 700; color: {saudi_verif['verdict_color']}; font-size: 1.0rem;">Audit: {saudi_verif['verdict']}</span> 
                <span style="font-size: 0.85rem; color: #64748b;">({saudi_verif['matched_count']}/{saudi_verif['total_ref_count']} verified peaks, {saudi_verif['match_percentage']:.0f}% literature fidelity)</span><br>
                <span style="font-size: 0.88rem; color: #1e293b; line-height: 1.45;">{saudi_verif['explanation']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Research Centers:** {', '.join(saudi_verif['institutions'])} | **Pillar:** *{saudi_verif['pillar']}*")
            st.caption(f"**Primary Reference:** {saudi_verif['primary_citation']}")
            if saudi_verif['matches']:
                st.markdown("##### Correlated Literature Spectral States")
                m_df = pd.DataFrame(saudi_verif['matches'])
                m_df.columns = ["State Assignment", "Literature BE (eV)", "Measured BE (eV)", "Deviation |ΔBE| (eV)", "Audit Status"]
                st.dataframe(m_df, use_container_width=True)

        with st.expander("🔍 Search Full Saudi Alliance Literature & Peak Databank (KFUPM · KACST · KAUST · IAU)", expanded=False):
            from modules.saudi_search_ui import render_saudi_alliance_explorer
            render_saudi_alliance_explorer(active_technique="XPS")

        # ----------------------------------------------------------------------
        # PUBLICATION EXPORT CENTER
        # ----------------------------------------------------------------------
        st.markdown("#### 📥 Publication Export Center")
        clean_slug = fc['preset_name'].replace(' ', '_').replace('/', '_')
        zip_bytes = build_analysis_bundle_zip(
            fig_xps,
            base_name=f"XPS_{clean_slug}",
            labplot_df=labplot_df,
            summary_data=quant_df,
            title=plot_cfg['title'] or f"XPS Analysis: {fc['preset_name']}",
            units={'Binding_Energy_eV': 'eV', 'Experimental_CPS': 'Counts/s'}
        )
        st.download_button(
            "📦 Download Complete XPS Publication Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
            data=zip_bytes,
            file_name=f"XPS_{clean_slug}_Package.zip",
            mime="application/zip",
            key="dl_xps_zip",
            type="primary",
            use_container_width=True
        )

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button(
                "📊 Export OriginLab Matrix (.dat)",
                data=get_originlab_ascii_bytes(labplot_df, title="XPS OriginLab Matrix", units={'Binding_Energy_eV': 'eV', 'Experimental_CPS': 'Counts/s'}),
                file_name=f"XPS_{clean_slug}_OriginLab.dat",
                mime="text/plain",
                use_container_width=True,
                key="xps_origin_dat",
                help="OriginLab-compatible ASCII matrix with A(X), B(Y) column designations for direct drag & drop."
            )
            st.download_button(
                "📗 Export OriginLab Workbook (.xlsx)",
                data=get_originlab_excel_bytes(labplot_df, title="XPS OriginLab Matrix", units={'Binding_Energy_eV': 'eV', 'Experimental_CPS': 'Counts/s'}),
                file_name=f"XPS_{clean_slug}_OriginLab.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="xps_origin_xlsx",
                help="OriginLab-ready Excel workbook with 4-tier metadata header."
            )
            st.download_button(
                "📈 Export LabPlot Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_df, title="XPS LabPlot Matrix"),
                file_name=f"XPS_{clean_slug}_LabPlot.dat",
                mime="text/plain",
                use_container_width=True,
                key="xps_labplot_dat",
                help="LabPlot ASCII data table with metadata header."
            )
        with c_right:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_xps, 'png', dpi=600), file_name=f"XPS_{clean_slug}_600DPI.png", mime="image/png", use_container_width=True, key="xps_png")
            st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_xps, 'svg'), file_name=f"XPS_{clean_slug}.svg", mime="image/svg+xml", use_container_width=True, key="xps_svg")
            st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_xps, 'pdf'), file_name=f"XPS_{clean_slug}.pdf", mime="application/pdf", use_container_width=True, key="xps_pdf")

        plt.close(fig_xps)

# ==============================================================================
# UNIFIED INSTITUTIONAL FOOTER & MASTER GATEWAY REVIEW LINK
# ==============================================================================
render_unified_studio_footer(
    active_domain_key="xps_studio",
    studio_title="XPS Deep-Intelligence Studio",
    studio_subtitle="High-Resolution Core-Level Photoelectron Spectroscopy Intelligence"
)
