"""
interpretation.py - Domain-Aware Vibrational Chemistry Reasoning Engine.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional
import numpy as np


def _find_band_near(band_summary: Dict[str, Dict[str, Any]], target_wn: float, tol: float = 45.0) -> Optional[Dict[str, Any]]:
    """Finds strongest deconvolved IR band within +/- tol cm-1."""
    candidates = []
    for name, b in band_summary.items():
        diff = abs(float(b["Wavenumber_cm1"]) - target_wn)
        if diff <= tol:
            candidates.append((diff, -float(b["Integrated_Area"]), name, b))
    if not candidates:
        return None
    candidates.sort(key=lambda t: (t[0], t[1]))
    _, _, best_name, best_b = candidates[0]
    out = dict(best_b)
    out["_name"] = best_name
    return out


def interpret_ftir_chemistry(
    band_summary: Dict[str, Dict[str, Any]],
    domain_key: str = "",
    preset_dict: Optional[Dict[str, Any]] = None,
    wavenumber_full: Optional[np.ndarray] = None,
    absorbance_full: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Produces domain-specific vibrational chemistry metrics:
      - PAN: FT-IR Extent of Stabilization / Cyclization Index (E_s, f = 0.29)
      - MOFs: Deacon Carboxylate Splitting Delta_nu = nu_as - nu_s + Free H2BDC check
      - Perovskites: FA+ / MA+ cation indicator & Passivated C=O shift
      - Catalysts/Oxides: Surface Carbonate vs Siloxane / M-O network dominance
    """
    metrics: Dict[str, Dict[str, Any]] = {}
    insights: List[str] = []
    warnings: List[str] = []

    if not band_summary:
        return {"metrics": metrics, "insights": insights, "warnings": warnings}

    dom = domain_key.lower()

    # Check broad O-H hydration envelope (~3400 cm-1) if full range passed
    if wavenumber_full is not None and absorbance_full is not None:
        mask_oh = (wavenumber_full >= 3250.0) & (wavenumber_full <= 3550.0)
        if np.any(mask_oh):
            oh_max = float(np.nanmax(absorbance_full[mask_oh]))
            tot_max = max(float(np.nanmax(absorbance_full)), 1e-4)
            oh_ratio = 100.0 * oh_max / tot_max
            metrics["O-H Hydration Ratio"] = {"name": "O–H Stretch (~3400)", "value": oh_ratio, "unit": "% max"}
            if oh_ratio > 45.0:
                warnings.append(f"Strong O–H band (~3400 cm⁻¹, {oh_ratio:.1f}% of peak intensity): check surface moisture or adsorbed solvent.")

    # 1. Polymers / PAN Stabilization Extent (EOR / E_s)
    if "polymer" in dom or "pan" in dom:
        b_cn = _find_band_near(band_summary, 2243.0, tol=30.0)
        b_im = _find_band_near(band_summary, 1605.0, tol=45.0)
        if b_cn and b_im:
            i_cn = max(float(b_cn["Peak_Absorbance"]), 0.0)
            i_im = max(float(b_im["Peak_Absorbance"]), 0.0)
            # Literature molar extinction weighting f = 0.29 (Zhu et al. / Grassie)
            f_ext = 0.29
            e_s = 100.0 * (f_ext * i_im) / max(i_cn + f_ext * i_im, 1e-9)
            metrics["Cyclization Index"] = {"name": "PAN Stabilization (E_s)", "value": e_s, "unit": "%"}
            metrics["I(C=N)/I(C≡N)"] = {"name": "Ladder / Nitrile Ratio", "value": i_im / max(i_cn, 1e-6), "unit": ""}

            if e_s < 10.0:
                insights.append(f"Linear as-spun PAN retained: crisp ν(C≡N) nitrile at {b_cn['Wavenumber_cm1']:.1f} cm⁻¹ with minimal cyclization (E_s = {e_s:.1f}%).")
            elif e_s < 55.0:
                insights.append(f"Progressive ladder cyclization (E_s = {e_s:.1f}%): nitrile attenuation accompanied by ν(C=N/C=C) growth at {b_im['Wavenumber_cm1']:.1f} cm⁻¹.")
            else:
                insights.append(f"Highly stabilized conjugated ladder network achieved (E_s = {e_s:.1f}%), ready for high-yield carbonization.")
        elif b_im and not b_cn:
            insights.append(f"Complete nitrile consumption: no residual 2243 cm⁻¹ ν(C≡N) resolved against {b_im['Wavenumber_cm1']:.1f} cm⁻¹ ladder band.")

    # 2. MOFs: Carboxylate Deacon Splitting & Unwashed Acid Pore Check
    elif "mof" in dom:
        b_as = _find_band_near(band_summary, 1605.0, tol=55.0)
        b_sym = _find_band_near(band_summary, 1388.0, tol=40.0)
        b_acid = _find_band_near(band_summary, 1695.0, tol=25.0)
        if b_as and b_sym:
            delta_nu = float(b_as["Wavenumber_cm1"]) - float(b_sym["Wavenumber_cm1"])
            metrics["Deacon Splitting"] = {"name": "Deacon Δν(COO⁻)", "value": delta_nu, "unit": "cm⁻¹"}
            coord_mode = "bridging bidentate" if 130 <= delta_nu <= 210 else ("monodentate/asymmetric" if delta_nu > 210 else "chelating bidentate")
            insights.append(
                f"Deacon carboxylate splitting Δν = {delta_nu:.1f} cm⁻¹ (ν_as = {b_as['Wavenumber_cm1']:.1f}, ν_s = {b_sym['Wavenumber_cm1']:.1f} cm⁻¹) "
                f"confirms {coord_mode} metal-cluster coordination."
            )
        if b_acid and float(b_acid["Area_Percent"]) > 4.0:
            warnings.append(
                f"Residual uncoordinated -COOH carbonyl band detected at {b_acid['Wavenumber_cm1']:.1f} cm⁻¹ ({b_acid['Area_Percent']:.1f}% area) — consider DMF/MeOH solvent exchange."
            )

    # 3. Solar Perovskites: FA+ / MA+ & Lewis-Base Passivation
    elif "perovskite" in dom:
        b_fa = _find_band_near(band_summary, 1712.0, tol=16.0)
        b_pass = _find_band_near(band_summary, 1682.0, tol=20.0)
        b_free = _find_band_near(band_summary, 1738.0, tol=18.0)
        b_h2o = _find_band_near(band_summary, 1622.0, tol=22.0)

        if b_fa:
            insights.append(f"FA⁺ ν_as(C=N) marker localized at {b_fa['Wavenumber_cm1']:.1f} cm⁻¹ (FWHM = {b_fa['FWHM_cm1']:.1f} cm⁻¹).")
        if b_pass and b_free:
            shift = float(b_free["Wavenumber_cm1"]) - float(b_pass["Wavenumber_cm1"])
            bound_frac = 100.0 * float(b_pass["Integrated_Area"]) / max(float(b_pass["Integrated_Area"]) + float(b_free["Integrated_Area"]), 1e-9)
            metrics["C=O Passivation Shift"] = {"name": "Lewis-Base Δν(C=O)", "value": shift, "unit": "cm⁻¹"}
            metrics["Bound C=O Fraction"] = {"name": "Pb²⁺-Bound C=O", "value": bound_frac, "unit": "%"}
            insights.append(f"Additive ν(C=O) red-shift of Δν = {shift:.1f} cm⁻¹ confirms Lewis-base electron donation to undercoordinated Pb²⁺ ({bound_frac:.1f}% coordinated).")
        if b_h2o and float(b_h2o["Area_Percent"]) > 8.0:
            warnings.append(f"Elevated δ(H₂O) moisture bending near {b_h2o['Wavenumber_cm1']:.1f} cm⁻¹ ({b_h2o['Area_Percent']:.1f}% area).")

    # 4. Catalysts & Metal Oxides
    elif "catalyst" in dom or "oxide" in dom:
        b_sio = _find_band_near(band_summary, 1085.0, tol=50.0)
        b_carb = _find_band_near(band_summary, 1520.0, tol=40.0)
        b_mo = _find_band_near(band_summary, 545.0, tol=60.0)
        if b_sio:
            insights.append(f"Strong framework ν_as(Si–O–Si) bridge at {b_sio['Wavenumber_cm1']:.1f} cm⁻¹ ({b_sio['Area_Percent']:.1f}% ROI area).")
        if b_mo:
            insights.append(f"Distinct metal–oxygen lattice stretch at {b_mo['Wavenumber_cm1']:.1f} cm⁻¹.")
        if b_carb:
            metrics["Surface Carbonate"] = {"name": "Carbonate Band Area", "value": float(b_carb["Area_Percent"]), "unit": "%"}
            insights.append(f"Chemisorbed surface carbonate species at {b_carb['Wavenumber_cm1']:.1f} cm⁻¹ ({b_carb['Area_Percent']:.1f}% area).")

    if preset_dict and preset_dict.get("key_diagnostic"):
        insights.append(f"Reference Guidance: {preset_dict['key_diagnostic']}")

    return {"metrics": metrics, "insights": insights, "warnings": warnings}
