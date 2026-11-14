"""
saudi_search_ui.py - Interactive Cross-University Literature & Materials Explorer
Curated for: KFUPM, KACST, KAUST, and Imam Abdulrahman Bin Faisal University (IAU - iau.edu.sa).
"""

from typing import Optional
import streamlit as st
import pandas as pd

from knowledge_base.saudi_research_databank import (
    SAUDI_INSTITUTIONS,
    RESEARCH_PILLARS,
    SAUDI_RESEARCH_BENCHMARKS,
    search_saudi_databank,
    get_benchmark_by_id,
)

INSTITUTION_COLORS = {
    "KAUST": {"bg": "#f1f5f9", "text": "#0f172a", "border": "#94a3b8"},
    "KFUPM": {"bg": "#f0fdf4", "text": "#166534", "border": "#86efac"},
    "KACST": {"bg": "#f0f9ff", "text": "#0369a1", "border": "#7dd3fc"},
    "IAU": {"bg": "#fffbeb", "text": "#92400e", "border": "#fcd34d"},
}


def render_saudi_alliance_explorer(active_technique: Optional[str] = None):
    """
    Renders the Cross-University Reference & Literature Explorer.
    Can be embedded inside Plotting_Chemistry app.py or specialized studios.
    """
    st.markdown("""
    <div style="background: #f8fafc; padding: 1.1rem 1.35rem; border-radius: 6px; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; margin-bottom: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 0.70rem; letter-spacing: 0.08em; text-transform: uppercase; color: #0284c7; font-weight: 700;">
                    CROSS-INSTITUTIONAL REFERENCE DATABANK
                </div>
                <div style="margin: 2px 0 4px 0; font-size: 1.25rem; font-weight: 700; color: #0f172a;">
                    Saudi Research Alliance — Literature &amp; Spectroscopic Standards
                </div>
                <div style="font-size: 0.84rem; color: #475569; max-width: 880px; line-height: 1.45;">
                    Audited experimental reference benchmarks spanning <b>KAUST</b>, <b>KFUPM</b>, <b>KACST</b>, and <b>IAU (iau.edu.sa)</b> across reticular MOFs, halide perovskites, heterogeneous catalysts, and desalination membranes.
                </div>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; color: #334155; padding: 3px 9px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">KAUST</span>
                <span style="background: #ffffff; border: 1px solid #cbd5e1; color: #334155; padding: 3px 9px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">KFUPM</span>
                <span style="background: #ffffff; border: 1px solid #cbd5e1; color: #334155; padding: 3px 9px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">KACST</span>
                <span style="background: #ffffff; border: 1px solid #cbd5e1; color: #334155; padding: 3px 9px; border-radius: 4px; font-size: 0.73rem; font-weight: 600;">IAU</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search & Filter Controls
    c_search, c_inst, c_tech, c_pillar = st.columns([2.2, 1.2, 1.1, 1.5])
    
    with c_search:
        query = st.text_input(
            "Search Reference Databank:",
            placeholder="e.g. UiO-66, Perovskite, TiO2, ZIF-8, PAN, MXene, Carboxylate...",
            key="saudi_search_query",
            help="Searches material names, chemical formulas, research centers, binding energies, Bragg angles, and vibrational modes."
        )

    with c_inst:
        inst_options = ["All Universities", "KAUST", "KFUPM", "KACST", "IAU"]
        sel_inst = st.selectbox("Institution:", inst_options, index=0, key="saudi_filter_inst")

    with c_tech:
        tech_options = ["All Techniques", "XPS (Photoelectron)", "XRD (Diffraction)", "FTIR (Infrared)"]
        default_t_idx = 0
        if active_technique:
            for idx, opt in enumerate(tech_options):
                if active_technique.upper() in opt.upper():
                    default_t_idx = idx
                    break
        sel_tech = st.selectbox("Technique:", tech_options, index=default_t_idx, key="saudi_filter_tech")

    with c_pillar:
        sel_pillar = st.selectbox("Research Pillar:", RESEARCH_PILLARS, index=0, key="saudi_filter_pillar")

    # Perform Search
    matched_benchmarks = search_saudi_databank(
        query=query,
        institution=sel_inst,
        technique=sel_tech,
        pillar=sel_pillar,
    )

    st.caption(f"Showing {len(matched_benchmarks)} cross-referenced material standards:")

    if not matched_benchmarks:
        st.info("No matching material benchmark found. Clear active filters or search for `UiO-66`, `Perovskite`, `TiO2`, `PAN`, `MXene`, `Cu2O`, or `ZIF-8`.")
        return

    # Render each benchmark card
    for bm in matched_benchmarks:
        bm_id = bm["id"]
        with st.expander(f"{bm['material_name']} — {bm['chemical_formula']}", expanded=(len(matched_benchmarks) <= 2)):
            badges_html = " ".join([
                f'<span style="background:{INSTITUTION_COLORS.get(inst, {}).get("bg", "#f1f5f9")}; '
                f'color:{INSTITUTION_COLORS.get(inst, {}).get("text", "#334155")}; '
                f'border: 1px solid {INSTITUTION_COLORS.get(inst, {}).get("border", "#cbd5e1")}; '
                f'font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-right: 4px;">'
                f'{inst}'
                f'</span>'
                for inst in bm.get("institutions", [])
            ])
            st.markdown(
                f'<div style="margin-bottom: 0.6rem; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">'
                f'<span style="font-size: 0.74rem; font-weight: 600; color: #0284c7; background: #f0f9ff; border: 1px solid #bae6fd; padding: 2px 8px; border-radius: 4px;">{bm["pillar"]}</span>'
                f'{badges_html}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(f"**Primary Reference:** {bm.get('primary_citation', '')}")

            with st.expander("Institutional Literature Cross-References & Research Centers", expanded=False):
                for ref in bm.get("literature_references", []):
                    st.markdown(f"- {ref}")

            tab_xps, tab_xrd, tab_ftir, tab_bib = st.tabs([
                "XPS Core Levels",
                "XRD Reflections",
                "FTIR Vibrational Modes",
                "BibTeX Citation"
            ])

            with tab_xps:
                if "xps_benchmarks" in bm:
                    xps = bm["xps_benchmarks"]
                    st.markdown(f"**Core Levels:** `{xps.get('core_level', 'N/A')}`")
                    df_xps = pd.DataFrame([
                        {"Chemical State / Peak": k, "Reference Binding Energy (eV)": v}
                        for k, v in xps.get("binding_energies", {}).items()
                    ])
                    st.dataframe(df_xps, hide_index=True, use_container_width=True)
                    st.caption(f"**Diagnostic Note:** {xps.get('ratio_diagnostic', '')}")
                else:
                    st.caption("No XPS benchmark registered for this entry.")

            with tab_xrd:
                if "xrd_benchmarks" in bm:
                    xrd = bm["xrd_benchmarks"]
                    wl = float(xrd.get("wavelength_A", 1.54060))
                    st.markdown(f"**Wavelength:** λ = {wl:.5f} Å (Cu Kα, 1.54060 Å)")
                    df_xrd = pd.DataFrame(xrd.get("reflections", []))
                    if not df_xrd.empty:
                        df_xrd.rename(columns={
                            "hkl": "Facet (hkl)",
                            "two_theta": "Bragg Angle (2θ°)",
                            "d_A": "d-Spacing (Å)",
                            "note": "Crystallographic Role"
                        }, inplace=True)
                        st.dataframe(df_xrd, hide_index=True, use_container_width=True)
                    st.caption(f"**Diagnostic Note:** {xrd.get('diagnostic', '')}")
                else:
                    st.caption("No XRD benchmark registered for this entry.")

            with tab_ftir:
                if "ftir_benchmarks" in bm:
                    ftir = bm["ftir_benchmarks"]
                    df_ftir = pd.DataFrame(ftir.get("bands", []))
                    if not df_ftir.empty:
                        df_ftir.rename(columns={
                            "wavenumber": "Wavenumber (cm⁻¹)",
                            "mode": "Vibrational Mode",
                            "diagnostic": "Structural Interpretation"
                        }, inplace=True)
                        st.dataframe(df_ftir, hide_index=True, use_container_width=True)
                    st.caption(f"**Diagnostic Note:** {ftir.get('diagnostic', '')}")
                else:
                    st.caption("No FTIR benchmark registered for this entry.")

            with tab_bib:
                st.code(f"""@article{{saudi_alliance_{bm_id}_2026,
  title = {{{bm['material_name']}: Spectroscopic Benchmarks and Cross-Audited Standards}},
  author = {{{', '.join(bm['institutions'])} Materials Research Consortium}},
  institution = {{{', '.join([SAUDI_INSTITUTIONS[i]['name'] for i in bm['institutions'] if i in SAUDI_INSTITUTIONS])}}},
  year = {{2026}},
  note = {{Cross-Institutional Reference Databank: {bm['pillar']}}}
}}""", language="bibtex")


def render_sidebar_saudi_quick_search():
    """Renders a lightweight search widget for the sidebar."""
    q = st.text_input("Search Material / Literature:", placeholder="UiO-66, Perovskite, TiO2...", key="sb_saudi_q")
    if q:
        results = search_saudi_databank(query=q)
        st.caption(f"Found {len(results)} matches:")
        for r in results[:4]:
            st.markdown(f"**{r['material_name']}**")
            st.caption(f"{', '.join(r['institutions'])} • {r['chemical_formula']}")
            st.markdown("---")
    else:
        st.caption("Filter across KAUST, KFUPM, KACST, and IAU reference standards.")
