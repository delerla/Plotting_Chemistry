"""
institutional_verifier.py - Cross-Auditing & Literature Verification Engine
Audits experimental spectra against peer-reviewed benchmarks from:
  - KAUST (King Abdullah University of Science and Technology)
  - KFUPM (King Fahd University of Petroleum and Minerals)
  - KACST (King Abdulaziz City for Science and Technology)
  - IAU (Imam Abdulrahman Bin Faisal University - iau.edu.sa)
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional
try:
    from knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        audit_spectral_match,
        get_benchmark_by_id,
    )
except ImportError:
    from ..knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        audit_spectral_match,
        get_benchmark_by_id,
    )


def match_benchmark_key(name_hint: str) -> Optional[str]:
    """Matches a user selection / material preset name to a databank benchmark key."""
    s = str(name_hint).lower()
    if "uio" in s or "zr" in s or "carboxylate" in s:
        return "uio66_zr_framework"
    if "zif" in s or "sodalite" in s or "imidazolate" in s:
        return "zif8_sodalite_framework"
    if "perovskite" in s or "fapbi" in s or "mapbi" in s or "lead" in s or "pb" in s:
        return "perovskite_fapbi3_solar"
    if "tio2" in s or "anatase" in s or "rutile" in s or "photocatal" in s:
        return "tio2_catalyst_photocatalysis"
    if "pan" in s or "nanofiber" in s or "cnf" in s or "cycliz" in s or "polymer" in s:
        return "pan_nanofibers_water_energy"
    return None


def verify_against_saudi_databank(
    technique: str,
    fitted_components: Dict[str, Dict[str, Any]],
    material_hint: str = "",
    benchmark_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verifies experimental peak deconvolution against the peer-reviewed Saudi research alliance databank.
    technique: 'XPS', 'XRD', or 'FTIR'
    fitted_components: summary dictionary of fitted peaks/bands
    material_hint: name of active preset or material
    """
    bm_key = benchmark_id or match_benchmark_key(material_hint)
    if not bm_key or bm_key not in SAUDI_RESEARCH_BENCHMARKS:
        # Fallback to first available if loosely related
        bm_key = "uio66_zr_framework" if "mof" in str(material_hint).lower() else "pan_nanofibers_water_energy"

    bm = SAUDI_RESEARCH_BENCHMARKS[bm_key]
    tech = technique.upper().strip()

    # Extract positions from fitted components
    exp_positions: List[float] = []
    tol = 0.40 if tech == "XPS" else (0.12 if tech == "XRD" else 8.0)

    for c_info in fitted_components.values():
        if tech == "XPS":
            pos = c_info.get("Binding_Energy_eV") or c_info.get("center")
        elif tech == "XRD":
            pos = c_info.get("TwoTheta_deg") or c_info.get("center")
        else:  # FTIR
            pos = c_info.get("Wavenumber_cm1") or c_info.get("center")
        if pos is not None and float(pos) > 0:
            exp_positions.append(float(pos))

    audit = audit_spectral_match(tech, exp_positions, bm_key, tolerance=tol)

    # Build academic explanation
    inst_str = ", ".join(bm["institutions"])
    match_pct = audit.get("match_percentage", 0.0)
    matched_count = len(audit.get("matches", []))
    total_ref = matched_count + len(audit.get("unmatched", []))

    if match_pct >= 75.0:
        verdict = "Excellent Alignment"
        verdict_color = "#16a34a"
        explanation = (
            f"Your experimental {tech} spectrum shows strong fidelity ({match_pct:.0f}% correlation) "
            f"with the peer-reviewed reference from {inst_str} ({bm['material_name']}). "
            f"Key spectral fingerprints align within ±{tol} {('eV' if tech=='XPS' else ('° 2θ' if tech=='XRD' else 'cm⁻¹'))}, "
            f"confirming target phase purity and coordination chemistry as reported by {bm['primary_citation']}."
        )
    elif match_pct >= 40.0:
        verdict = "Partial Match (Defect / Modified Phase)"
        verdict_color = "#f59e0b"
        explanation = (
            f"Your {tech} profile exhibits core features of {bm['material_name']} ({match_pct:.0f}% match with {inst_str} benchmarks), "
            f"but shows notable deviations or unassigned secondary reflections. In student/research workflows at {inst_str}, "
            f"such deviations typically indicate structural defects, incomplete activation/washing, or chemical transformation."
        )
    else:
        verdict = "Distinct / Deviating Phase"
        verdict_color = "#dc2626"
        explanation = (
            f"Low spectral correspondence ({match_pct:.0f}%) with the reference {bm['material_name']} ({inst_str}). "
            f"Your data may represent an unactivated precursor, significant degradation, or an alternative polymorph."
        )

    return {
        "matched": bool(match_pct >= 40.0),
        "benchmark_id": bm_key,
        "material_name": bm["material_name"],
        "pillar": bm["pillar"],
        "institutions": bm["institutions"],
        "primary_citation": bm["primary_citation"],
        "literature_references": bm["literature_references"],
        "verdict": verdict,
        "verdict_color": verdict_color,
        "match_percentage": match_pct,
        "matched_count": matched_count,
        "total_ref_count": total_ref,
        "matches": audit.get("matches", []),
        "unmatched": audit.get("unmatched", []),
        "explanation": explanation,
        "tolerance": tol,
    }
