"""
interpretation.py - Domain-Aware Crystallographic Reasoning & Phase Diagnostic Engine.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional
import numpy as np


def _find_peak_near(peak_summary: Dict[str, Dict[str, Any]], target_tt: float, tol_deg: float = 0.8) -> Optional[Dict[str, Any]]:
    """Returns the strongest fitted peak within +/- tol_deg of a reference 2-theta value."""
    candidates = []
    for name, p in peak_summary.items():
        diff = abs(float(p["TwoTheta_deg"]) - target_tt)
        if diff <= tol_deg:
            candidates.append((diff, -float(p["Area"]), name, p))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    _, _, best_name, best_p = candidates[0]
    out = dict(best_p)
    out["_matched_name"] = best_name
    return out


def interpret_xrd_diagnostics(
    peak_summary: Dict[str, Dict[str, Any]],
    wh_results: Optional[Dict[str, Any]],
    two_theta: np.ndarray,
    y_net: np.ndarray,
    bg_curve: np.ndarray,
    domain_key: str = "",
    preset_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Produces domain-specific scientific diagnostics, quantitative phase fractions,
    crystallinity index, and strain vs. size structural insights.
    """
    metrics: Dict[str, Dict[str, Any]] = {}
    insights: List[str] = []
    warnings: List[str] = []

    if not peak_summary:
        return {"metrics": metrics, "insights": insights, "warnings": warnings}

    fn_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")

    # 1. Apparent Crystallinity Index (CI): ratio of fitted crystalline Bragg area to total scattered signal above floor
    total_peak_area = sum(float(p.get("Area", 0.0)) for p in peak_summary.values())
    order = np.argsort(two_theta)
    x_s = np.asarray(two_theta[order], dtype=float)
    y_net_s = np.maximum(np.asarray(y_net[order], dtype=float), 0.0)
    bg_s = np.asarray(bg_curve[order], dtype=float)
    bg_above_floor = np.maximum(bg_s - float(np.nanmin(bg_s)), 0.0)
    total_area_above_floor = float(fn_trapz(y_net_s + bg_above_floor, x_s))

    if total_area_above_floor > 1e-6:
        ci_pct = float(np.clip(100.0 * total_peak_area / total_area_above_floor, 0.0, 100.0))
        metrics["Crystallinity Index"] = {"name": "Apparent Crystallinity", "value": ci_pct, "unit": "%"}

    # Mean Scherrer size weighted by peak area
    weighted_d = sum(float(p["Scherrer_D_nm"]) * float(p["Area"]) for p in peak_summary.values())
    mean_d_nm = weighted_d / total_peak_area if total_peak_area > 1e-6 else 0.0
    metrics["Mean Scherrer Size"] = {"name": "Area-Wtd Scherrer <D>", "value": mean_d_nm, "unit": "nm"}

    # 2. Williamson-Hall vs Scherrer synthesis
    if wh_results and wh_results.get("valid"):
        eps_pct = float(wh_results["microstrain_percent"])
        d_wh = float(wh_results["D_wh_nm"])
        metrics["W-H Microstrain"] = {"name": "W-H Microstrain (ε)", "value": eps_pct, "unit": "%"}
        if np.isfinite(d_wh) and d_wh < 2000.0:
            insights.append(
                f"Williamson–Hall separation across {wh_results['n_peaks']} Bragg peaks yields true crystallite size "
                f"D_WH = {d_wh:.1f} nm with lattice microstrain ε = {eps_pct:+.4f}% (R² = {wh_results['r2_wh']:.3f})."
            )
            if abs(eps_pct) > 0.25:
                warnings.append(
                    f"Substantial microstrain (|ε| = {abs(eps_pct):.2f}%) detected; single-peak Scherrer sizing may underestimate true domain size."
                )

    dom_low = domain_key.lower()

    # 3. Domain-Specific Physical Models
    if "perovskite" in dom_low:
        pk_pbi2 = _find_peak_near(peak_summary, 12.67, tol_deg=0.45)
        pk_110 = _find_peak_near(peak_summary, 14.15, tol_deg=0.55)
        pk_220 = _find_peak_near(peak_summary, 28.50, tol_deg=0.60)
        pk_delta = _find_peak_near(peak_summary, 11.82, tol_deg=0.45)

        if pk_110:
            pbi2_area = float(pk_pbi2["Area"]) if pk_pbi2 else 0.0
            perov_area = float(pk_110["Area"])
            deg_idx = 100.0 * pbi2_area / max(pbi2_area + perov_area, 1e-9)
            metrics["PbI2 Fraction"] = {"name": "PbI₂ Degradation Index", "value": deg_idx, "unit": "%"}
            if deg_idx > 15.0:
                warnings.append(
                    f"Pronounced PbI₂ (001) signature ({deg_idx:.1f}% vs. Perovskite (110)), pointing to thermal/moisture halide loss."
                )
            else:
                insights.append(
                    f"Strong black-phase Perovskite (110) domain (d = {pk_110['d_Spacing_A']:.3f} Å, D = {pk_110['Scherrer_D_nm']:.1f} nm) with low PbI₂ impurity ({deg_idx:.1f}%)."
                )
            if pk_220:
                tex = float(pk_110["Height_cts"]) / max(float(pk_220["Height_cts"]), 1e-6)
                insights.append(f"Grain orientation ratio I(110)/I(220) = {tex:.2f} (preferred uniaxial texturing indicator).")
        if pk_delta and float(pk_delta["Area_Percent"]) > 2.5:
            warnings.append(f"Photo-inactive yellow δ-phase reflection detected near {pk_delta['TwoTheta_deg']:.2f}° ({pk_delta['Area_Percent']:.1f}% area).")

    elif "catalyst" in dom_low or "oxide" in dom_low:
        pk_a101 = _find_peak_near(peak_summary, 25.28, tol_deg=0.60)
        pk_r110 = _find_peak_near(peak_summary, 27.45, tol_deg=0.60)
        if pk_a101 and pk_r110:
            ia = max(float(pk_a101["Height_cts"]), 0.0)
            ir = max(float(pk_r110["Height_cts"]), 0.0)
            # Spurr-Myers equation: W_R = 1 / (1 + 0.8 * (I_A / I_R))
            w_r = 100.0 / (1.0 + 0.8 * (ia / max(ir, 1e-6))) if ir > 0 else 0.0
            metrics["Spurr-Myers Rutile"] = {"name": "Rutile Fraction (Spurr–Myers)", "value": w_r, "unit": "wt%"}
            insights.append(
                f"Spurr–Myers phase quantification yields {100.0 - w_r:.1f} wt% Anatase ((101) D = {pk_a101['Scherrer_D_nm']:.1f} nm) "
                f"and {w_r:.1f} wt% Rutile ((110) D = {pk_r110['Scherrer_D_nm']:.1f} nm)."
            )
        else:
            # Check FCC Cu vs Cu2O
            pk_cu = _find_peak_near(peak_summary, 43.30, tol_deg=0.65)
            pk_cu2o = _find_peak_near(peak_summary, 36.42, tol_deg=0.65)
            if pk_cu:
                a_est = float(pk_cu["d_Spacing_A"]) * np.sqrt(3.0)  # FCC (111): a = d * sqrt(3)
                metrics["FCC Lattice a"] = {"name": "FCC Lattice Param a", "value": a_est, "unit": "Å"}
                insights.append(f"Metallic FCC (111) reflection at {pk_cu['TwoTheta_deg']:.3f}° implies cubic lattice parameter a ≈ {a_est:.4f} Å (bulk Cu = 3.615 Å).")
                if pk_cu2o and float(pk_cu2o["Area_Percent"]) > 5.0:
                    warnings.append(f"Surface oxidation detected: Cu₂O (111) reflection accounts for {pk_cu2o['Area_Percent']:.1f}% of integrated Bragg intensity.")

    elif "polymer" in dom_low or "carbon" in dom_low:
        pk_pan = _find_peak_near(peak_summary, 16.92, tol_deg=1.0)
        pk_002 = _find_peak_near(peak_summary, 25.60, tol_deg=1.6)
        if pk_002:
            d002 = float(pk_002["d_Spacing_A"])
            lc_nm = float(pk_002["Scherrer_D_nm"])
            n_layers = (lc_nm * 10.0) / max(d002, 1.0)
            metrics["Interlayer d002"] = {"name": "Graphitic d₀₀₂", "value": d002, "unit": "Å"}
            metrics["Stacking Lc"] = {"name": "Stacking Height Lc", "value": lc_nm, "unit": "nm"}
            insights.append(
                f"(002) π-stacking reflection yields d₀₀₂ = {d002:.3f} Å (graphite = 3.354 Å) with stacking height Lc = {lc_nm:.2f} nm (~{n_layers:.1f} graphene sheets)."
            )
        if pk_pan:
            insights.append(
                f"PAN (100) crystalline chain packing preserved at {pk_pan['TwoTheta_deg']:.2f}° (d = {pk_pan['d_Spacing_A']:.2f} Å, FWHM = {pk_pan['FWHM_obs_deg']:.2f}°)."
            )

    elif "mof" in dom_low:
        low_angle = [p for p in peak_summary.values() if float(p["TwoTheta_deg"]) < 13.0]
        if low_angle:
            sharpest = min(low_angle, key=lambda p: float(p["FWHM_obs_deg"]))
            insights.append(
                f"Intact low-angle reticular pore reflections below 13° 2θ (sharpest at {sharpest['TwoTheta_deg']:.2f}°, "
                f"d = {sharpest['d_Spacing_A']:.2f} Å, coherent domain D = {sharpest['Scherrer_D_nm']:.1f} nm)."
            )
        if "Crystallinity Index" in metrics and metrics["Crystallinity Index"]["value"] < 35.0:
            warnings.append("Reduced apparent crystallinity (<35%) may indicate partial framework collapse, residual solvent scattering, or ligand defects.")

    if preset_dict and preset_dict.get("key_diagnostic"):
        insights.append(f"Reference Guidance: {preset_dict['key_diagnostic']}")

    return {"metrics": metrics, "insights": insights, "warnings": warnings}
