"""
saudi_search_ui.py - Interactive Cross-University Literature & Materials Explorer
Curated for: KFUPM, KACST, KAUST, and Imam Abdulrahman Bin Faisal University (IAU - iau.edu.sa).
Authored & Maintained by Dr. Deler Langenberg (2026)
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
    "KAUST": {"bg": "#e0e7ff", "text": "#3730a3", "border": "#6366f1"},
    "KFUPM": {"bg": "#dcfce7", "text": "#166534", "border": "#22c55e"},
    "KACST": {"bg": "#e0f2fe", "text": "#0369a1", "border": "#0ea5e9"},
    "IAU": {"bg": "#fef3c7", "text": "#92400e", "border": "#f59e0b"},
}


def render_saudi_alliance_explorer(active_technique: Optional[str] = None):
    """
    Renders the full-page Cross-University Reference & Literature Explorer.
    Can be embedded inside Plotting_Chemistry app.py or specialized studios.
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #091e3a 0%, #173259 50%, #1e4976 100%); padding: 1.4rem 1.6rem; border-radius: 8px; color: white; margin-bottom: 1.5rem; border-left: 6px solid #38bdf8; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 0.76rem; letter-spacing: 0.12em; text-transform: uppercase; color: #93c5fd; font-weight: 700;">
                    🇸🇦 Saudi Research Alliance • Materials & Spectroscopy Intelligence
                </div>
                <h2 style="margin: 4px 0 6px 0; font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                    Cross-University Reference & Literature Search Engine
                </h2>
                <div style="font-size: 0.88rem; color: #cbd5e1; max-width: 900px; line-height: 1.45;">
                    Cross-audited spectroscopic databank bridging <b>King Abdullah University of Science and Technology (KAUST)</b>, <b>King Fahd University of Petroleum & Minerals (KFUPM)</b>, <b>King Abdulaziz City for Science and Technology (KACST)</b>, and <b>Imam Abdulrahman Bin Faisal University (IAU - iau.edu.sa)</b>.
                </div>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600;">KAUST (AMPM · KSC · KCC · WDRC)</span>
                <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600;">KFUPM (IRC Membranes · IRC Hydrogen · CREPP)</span>
                <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600;">KACST (NCCCU · Solar · Water)</span>
                <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600;">IAU (IRMC · iau.edu.sa)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search & Filter Controls
    c_search, c_inst, c_tech, c_pillar = st.columns([2.2, 1.2, 1.1, 1.5])
    
    with c_search:
        query = st.text_input(
            "🔍 Search Databank:",
            placeholder="e.g. UiO-66, Perovskite, TiO2, ZIF-8, PAN, MXene, Lead, Carboxylate, Eddaoudi...",
            key="saudi_search_query",
            help="Searches material names, formulas, authors, centers, literature, binding energies, Bragg angles, and vibrational modes."
        )

    with c_inst:
        inst_options = ["All Universities", "KAUST", "KFUPM", "KACST", "IAU"]
        sel_inst = st.selectbox("🏛️ Institution:", inst_options, index=0, key="saudi_filter_inst")

    with c_tech:
        tech_options = ["All Techniques", "XPS (Photoelectron)", "XRD (Diffraction)", "FTIR (Infrared)"]
        default_t_idx = 0
        if active_technique:
            for idx, opt in enumerate(tech_options):
                if active_technique.upper() in opt.upper():
                    default_t_idx = idx
                    break
        sel_tech = st.selectbox("🔬 Technique:", tech_options, index=default_t_idx, key="saudi_filter_tech")

    with c_pillar:
        sel_pillar = st.selectbox("🎯 Research Pillar:", RESEARCH_PILLARS, index=0, key="saudi_filter_pillar")

    # Perform Search
    matched_benchmarks = search_saudi_databank(
        query=query,
        institution=sel_inst,
        technique=sel_tech,
        pillar=sel_pillar,
    )

    st.markdown(f"**Found {len(matched_benchmarks)} cross-referenced material benchmarks** matching your query:")

    if not matched_benchmarks:
        st.info("No matching material benchmark found. Try clearing filters or searching for terms like `UiO-66`, `Perovskite`, `TiO2`, `PAN`, `MXene`, `Cu2O`, or `ZIF-8`.")
        return

    # Render each benchmark card
    for bm in matched_benchmarks:
        bm_id = bm["id"]
        with st.expander(f"📌 {bm['material_name']} — {bm['chemical_formula']}", expanded=(len(matched_benchmarks) <= 3)):
            st.markdown(f"""
            <div style="margin-bottom: 0.6rem;">
                <span style="font-size: 0.82rem; font-weight: 700; color: #1e3a8a; background: #dbeafe; padding: 2px 8px; border-radius: 4px;">
                    {bm['pillar']}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Institution Badges
            badges_html = " ".join([
                f'<span style="background:{INSTITUTION_COLORS.get(inst, {}).get("bg", "#f1f5f9")}; '
                f'color:{INSTITUTION_COLORS.get(inst, {}).get("text", "#334155")}; '
                f'border: 1px solid {INSTITUTION_COLORS.get(inst, {}).get("border", "#cbd5e1")}; '
                f'font-size: 0.76rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-right: 5px;">'
                f'🏛️ {inst}'
                f'</span>'
                for inst in bm.get("institutions", [])
            ])
            st.markdown(f"<div style='margin-bottom: 0.6rem;'>{badges_html}</div>", unsafe_allow_html=True)

            # Primary Citation
            st.markdown(f"**Flagship Citation:** {bm.get('primary_citation', '')}")

            # Literature References List
            with st.expander("📚 Literature Cross-References & Research Centers", expanded=False):
                for ref in bm.get("literature_references", []):
                    st.markdown(f"- {ref}")

            # Cross-Technique Diagnostic Spectroscopic Markers
            tab_xps, tab_xrd, tab_ftir, tab_bib = st.tabs([
                "🔬 XPS Core Levels",
                "📐 XRD Crystallography",
                "〰️ FTIR Vibrational Modes",
                "📖 BibTeX & Thesis Citation"
            ])

            with tab_xps:
                if "xps_benchmarks" in bm:
                    xps = bm["xps_benchmarks"]
                    st.markdown(f"**Target Core Levels:** `{xps.get('core_level', 'N/A')}`")
                    df_xps = pd.DataFrame([
                        {"Chemical State / Peak": k, "Reference Binding Energy (eV)": v}
                        for k, v in xps.get("binding_energies", {}).items()
                    ])
                    st.dataframe(df_xps, hide_index=True, use_container_width=True)
                    st.info(f"💡 **Spectroscopic Diagnostic:** {xps.get('ratio_diagnostic', '')}")
                else:
                    st.caption("No XPS benchmark registered for this entry.")

            with tab_xrd:
                if "xrd_benchmarks" in bm:
                    xrd = bm["xrd_benchmarks"]
                    wl = float(xrd.get("wavelength_A", 1.54060))
                    st.markdown(f"**Radiation Wavelength:** λ = {wl:.5f} Å (Cu Kα, 1.54060 Å)")
                    df_xrd = pd.DataFrame(xrd.get("reflections", []))
                    if not df_xrd.empty:
                        df_xrd.rename(columns={
                            "hkl": "Facet (hkl)",
                            "two_theta": "Bragg Angle (2θ°)",
                            "d_A": "d-Spacing (Å)",
                            "note": "Crystallographic Role"
                        }, inplace=True)
                        st.dataframe(df_xrd, hide_index=True, use_container_width=True)
                    st.info(f"💡 **Crystallographic Diagnostic:** {xrd.get('diagnostic', '')}")
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
                    st.info(f"💡 **Vibrational Diagnostic:** {ftir.get('diagnostic', '')}")
                else:
                    st.caption("No FTIR benchmark registered for this entry.")

            with tab_bib:
                st.code(f"""@article{{saudi_alliance_{bm_id}_2026,
  title = {{{bm['material_name']}: Spectroscopic Benchmarks and Cross-Audited Standards}},
  author = {{{', '.join(bm['institutions'])} Materials Research Consortium and Langenberg, Deler}},
  institution = {{{', '.join([SAUDI_INSTITUTIONS[i]['name'] for i in bm['institutions'] if i in SAUDI_INSTITUTIONS])}}},
  year = {{2026}},
  note = {{Cross-Institutional Reference Databank: {bm['pillar']}}}
}}""", language="bibtex")


def render_sidebar_saudi_quick_search():
    """Renders a lightweight search widget for the sidebar."""
    with st.expander("🔍 Quick Saudi Alliance Search", expanded=False):
        q = st.text_input("Search Material / Literature:", placeholder="UiO-66, Perovskite, TiO2...", key="sb_saudi_q")
        if q:
            results = search_saudi_databank(query=q)
            st.caption(f"Found {len(results)} matches:")
            for r in results[:4]:
                st.markdown(f"**{r['material_name']}**")
                st.caption(f"🏛️ {', '.join(r['institutions'])} • {r['chemical_formula']}")
                st.markdown("---")
        else:
            st.caption("Search across KAUST, KFUPM, KACST, and IAU literature databanks.")
