"""
interpretation.py - Automated Scientific Chemical Reasoning & Defect Quantification Engine
Translates deconvolution peak areas into material-specific chemical physics insights:
- Stoichiometric coordination ratios
- Missing-linker defect densities in MOFs
- Metallic Pb0 photolysis in solar cells
- Cyclization indices in PAN nanofibers
- Oxygen vacancy concentrations
"""

from typing import Dict, List, Any, Optional
import numpy as np
try:
    from knowledge_base.scofield_rsf import get_rsf
except ImportError:
    from ..knowledge_base.scofield_rsf import get_rsf


def interpret_xps_chemistry(
    fit_metrics: Dict[str, Dict[str, Any]],
    preset_dict: Optional[Dict[str, Any]] = None,
    core_level: str = "C 1s"
) -> Dict[str, Any]:
    """
    Performs automated domain-specific interpretation and defect analysis.
    Returns:
        dictionary with metrics, scientific insights, and warnings.
    """
    results = {
        'core_level': core_level,
        'rsf': get_rsf(core_level),
        'metrics': {},
        'insights': [],
        'warnings': []
    }

    # Extract component areas mapping
    pfx_to_area = {}
    name_to_area = {}
    for name, m in fit_metrics.items():
        pfx = m.get('prefix', '')
        pfx_to_area[pfx] = m.get('Area_cps_eV', 0.0)
        name_to_area[name] = m.get('Area_cps_eV', 0.0)

    # 1. Apply preset domain rules if available
    if preset_dict and 'interpretation_rules' in preset_dict:
        rules = preset_dict['interpretation_rules']
        for r in rules:
            metric_key = r['metric']
            num_pfx = r['numerator']
            den_pfx = r['denominator']
            
            num_val = pfx_to_area.get(num_pfx, 0.0)
            if isinstance(den_pfx, list):
                den_val = sum(pfx_to_area.get(p, 0.0) for p in den_pfx)
            else:
                den_val = pfx_to_area.get(den_pfx, 0.0)
                
            if den_val > 0:
                val = (num_val / den_val) * 100.0 if r.get('unit') == '%' else (num_val / den_val)
                results['metrics'][metric_key] = {
                    'name': r['description'],
                    'value': round(val, 2),
                    'unit': r.get('unit', ''),
                    'description': r['description']
                }
                
                # Check against expected stoichiometry
                if 'expected' in r:
                    exp = r['expected']
                    diff_pct = abs(val - exp) / exp * 100.0
                    if diff_pct > 25.0:
                        results['warnings'].append(
                            f"Deviation in {r['description']}: Measured {val:.3f} differs from ideal {exp:.3f} by {diff_pct:.1f}%."
                        )

    # 2. Heuristic domain intelligence
    cl_lower = core_level.lower()
    
    # Perovskite Pb 4f intelligence
    if 'pb 4f' in cl_lower:
        pb0_area = sum(a for k, a in name_to_area.items() if 'pb⁰' in k.lower() or 'zero' in k.lower())
        pb2_area = sum(a for k, a in name_to_area.items() if 'pb²⁺' in k.lower() or '2plus' in k.lower())
        if pb2_area > 0 and pb0_area > 0:
            deg_pct = (pb0_area / (pb0_area + pb2_area)) * 100.0
            results['metrics']['metallic_pb0_fraction'] = {
                'name': 'Metallic Pb⁰ Defect Fraction',
                'value': round(deg_pct, 2),
                'unit': '%',
                'description': 'Fraction of lead reduced to metallic Pb0 non-radiative recombination centers'
            }
            if deg_pct > 5.0:
                results['warnings'].append(
                    f"Significant photodecomposition: {deg_pct:.1f}% of lead exists as metallic Pb⁰ clusters, reducing solar cell open-circuit voltage (Voc)."
                )
            else:
                results['insights'].append(
                    f"High perovskite lattice purity: Metallic Pb⁰ defects remain low ({deg_pct:.1f}%)."
                )

    # MOF C 1s intelligence
    elif 'c 1s' in cl_lower and any(('carboxylate' in k.lower() or 'o-c=o' in k.lower()) for k in name_to_area):
        carb_area = sum(a for k, a in name_to_area.items() if 'carboxylate' in k.lower() or 'o-c=o' in k.lower())
        arom_area = sum(a for k, a in name_to_area.items() if 'aromatic' in k.lower() or 'c-c' in k.lower())
        if arom_area > 0:
            ratio = carb_area / arom_area
            results['insights'].append(
                f"Framework Linker Integrity: Carboxylate-to-aromatic carbon ratio = {ratio:.2f}."
            )

    # PAN N 1s intelligence
    elif 'n 1s' in cl_lower and any('nitrile' in k.lower() for k in name_to_area):
        nitrile_area = sum(a for k, a in name_to_area.items() if 'nitrile' in k.lower())
        imine_area = sum(a for k, a in name_to_area.items() if 'cyclized' in k.lower() or 'imine' in k.lower() or 'pyridine' in k.lower())
        if (nitrile_area + imine_area) > 0:
            cyc_index = (imine_area / (nitrile_area + imine_area)) * 100.0
            results['metrics']['pan_cyclization_index'] = {
                'name': 'Thermal Cyclization Index',
                'value': round(cyc_index, 2),
                'unit': '%',
                'description': 'Conversion of linear nitrile groups into aromatic ladder rings'
            }
            results['insights'].append(
                f"PAN Stabilization Degree: {cyc_index:.1f}% cyclized into ladder structure."
            )

    return results
