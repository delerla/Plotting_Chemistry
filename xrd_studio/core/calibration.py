"""
calibration.py - Rachinger K-alpha2 Stripping & Bragg 2-Theta Alignment Engine.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Tuple
import numpy as np


def apply_ka2_stripping(
    two_theta: np.ndarray,
    intensity: np.ndarray,
    lambda_a1: float = 1.540598,
    lambda_a2: float = 1.544426,
    ka_ratio: float = 0.5,
) -> np.ndarray:
    """
    Applies the Rachinger correction to strip K-alpha2 satellite doublets:
        I_a1(2theta) = I_total(2theta) - R * I_a1(2theta - delta_2theta)
    where sin(theta_2) = (lambda_a2 / lambda_a1) * sin(theta_1).
    Operates cleanly on non-uniform or uniform grids via linear interpolation.
    """
    x = np.asarray(two_theta, dtype=float)
    y = np.asarray(intensity, dtype=float)
    if len(x) < 10 or ka_ratio <= 0.0 or lambda_a2 <= lambda_a1:
        return np.copy(y)

    # Ensure strictly ascending 2theta for sequential Rachinger evaluation
    order = np.argsort(x)
    x_s = x[order]
    y_s = y[order]

    y_a1 = np.zeros_like(y_s)
    ratio_lam = lambda_a2 / lambda_a1

    # Estimate minimum value for baseline floor before Rachinger subtraction
    y_floor = float(np.nanmin(y_s))
    y_rel = np.maximum(y_s - y_floor, 0.0)

    # For each 2theta_i, compute the angle 2theta_source where K-alpha1 produces a peak
    # whose K-alpha2 counterpart falls at 2theta_i: sin(theta_source) = (lam1/lam2)*sin(theta_i)
    sin_theta_i = np.sin(np.radians(x_s / 2.0))
    sin_src = np.clip(sin_theta_i / ratio_lam, -1.0, 1.0)
    x_src = 2.0 * np.degrees(np.arcsin(sin_src))

    for i in range(len(x_s)):
        xs = x_src[i]
        if xs <= x_s[0]:
            y_a1[i] = y_rel[i]
        else:
            # Interpolate already-recovered K-alpha1 intensity strictly below current i
            val_prev = float(np.interp(xs, x_s[: max(i, 1)], y_a1[: max(i, 1)]))
            y_a1[i] = max(y_rel[i] - ka_ratio * val_prev, 0.0)

    res = y_a1 + y_floor
    out = np.empty_like(res)
    out[order] = res
    return out


def apply_two_theta_calibration(
    two_theta: np.ndarray,
    measured_peak_deg: float,
    target_peak_deg: float,
    mode: str = "Zero-Shift (Δ2θ)",
    manual_shift_deg: float = 0.0,
) -> Tuple[np.ndarray, float, str]:
    """
    Calibrates diffraction angle 2-theta using either:
      1. Constant Zero-Point Offset: 2theta_corr = 2theta + (target - measured)
      2. Specimen Displacement Error: delta(2theta) proportional to cos(theta)
      3. Direct Manual Offset
    Returns (calibrated_2theta, shift_applied_at_ref, status_text).
    """
    x = np.asarray(two_theta, dtype=float)
    m_low = mode.lower()

    if "manual" in m_low:
        shift = float(manual_shift_deg)
        return x + shift, shift, f"Manual 2θ zero-shift applied: {shift:+.4f}°"

    if measured_peak_deg is None or target_peak_deg is None or measured_peak_deg <= 0 or target_peak_deg <= 0:
        return x.copy(), 0.0, "No 2θ shift applied (Raw diffractogram angles preserved)"

    delta_ref = float(target_peak_deg) - float(measured_peak_deg)

    if "displacement" in m_low or "cos" in m_low:
        cos_ref = max(np.cos(np.radians(float(measured_peak_deg) / 2.0)), 0.1)
        shift_curve = delta_ref * (np.cos(np.radians(x / 2.0)) / cos_ref)
        return (
            x + shift_curve,
            delta_ref,
            f"Specimen displacement calibration: {delta_ref:+.4f}° at {target_peak_deg:.3f}° (∝ cos θ)",
        )

    return (
        x + delta_ref,
        delta_ref,
        f"Zero-point 2θ calibration: {delta_ref:+.4f}° aligned to {target_peak_deg:.3f}°",
    )
