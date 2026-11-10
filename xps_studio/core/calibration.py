"""
calibration.py - Core Charge Referencing & Energy Calibration Engine
Aligns experimental XPS binding energy scale to recognized physical standards:
- Adventitious C 1s (sp3 / aliphatic C-C): 284.80 eV
- Aromatic C 1s (graphitic / graphene / sp2): 284.50 eV
- Gold Au 4f7/2: 84.00 eV
- Silver Ag 3d5/2: 368.27 eV
- Copper Cu 2p3/2: 932.67 eV
- Fermi edge cut-off: 0.00 eV
"""

from typing import Tuple, Optional
import numpy as np


CALIBRATION_STANDARDS = {
    'Adventitious C 1s (Aliphatic 284.8 eV)': {'expected': 284.80, 'search_window': (282.5, 287.0)},
    'Graphitic C 1s (sp² / Carbon 284.5 eV)': {'expected': 284.50, 'search_window': (282.5, 286.5)},
    'Gold Au 4f₇/₂ (84.00 eV)': {'expected': 84.00, 'search_window': (82.0, 86.0)},
    'Silver Ag 3d₅/₂ (368.27 eV)': {'expected': 368.27, 'search_window': (366.0, 370.5)},
    'Copper Cu 2p₃/₂ (932.67 eV)': {'expected': 932.67, 'search_window': (930.5, 935.0)},
    'Manual Custom Shift': {'expected': 0.00, 'search_window': None}
}


def apply_charge_calibration(
    binding_energy: np.ndarray,
    intensity: np.ndarray,
    method: str = 'Adventitious C 1s (Aliphatic 284.8 eV)',
    manual_shift_eV: float = 0.0
) -> Tuple[np.ndarray, float, str]:
    """
    Applies electrostatic charge compensation shift to the binding energy array.
    Returns:
        (calibrated_binding_energy, applied_shift_eV, status_message)
    """
    if method == 'Manual Custom Shift':
        calibrated_be = binding_energy + manual_shift_eV
        msg = f"Applied manual charge offset of {manual_shift_eV:+.3f} eV."
        return calibrated_be, manual_shift_eV, msg

    std = CALIBRATION_STANDARDS.get(method)
    if not std or not std['search_window']:
        return binding_energy, 0.0, "No calibration applied."

    w_min, w_max = std['search_window']
    mask = (binding_energy >= w_min) & (binding_energy <= w_max)
    
    if not np.any(mask) or np.sum(mask) < 3:
        # Fallback to manual shift if reference peak is out of the scan window
        if manual_shift_eV != 0.0:
            return binding_energy + manual_shift_eV, manual_shift_eV, f"Reference peak outside scan window. Applied manual shift {manual_shift_eV:+.3f} eV."
        return binding_energy, 0.0, f"Notice: Reference region [{w_min:.1f} - {w_max:.1f} eV] not in spectrum. Unshifted."

    # Identify maximum intensity in reference window
    sub_be = binding_energy[mask]
    sub_counts = intensity[mask]
    measured_peak_pos = sub_be[np.argmax(sub_counts)]
    
    expected_pos = std['expected']
    shift = expected_pos - measured_peak_pos
    
    calibrated_be = binding_energy + shift
    status = (
        f"Calibrated via {method}: Measured peak at {measured_peak_pos:.2f} eV "
        f"aligned to {expected_pos:.2f} eV (Charge shift ΔE = {shift:+.3f} eV)."
    )
    return calibrated_be, float(shift), status
