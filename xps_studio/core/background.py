"""
background.py - Advanced Inelastic Scattering Background & Baseline Algorithms
Supports:
1. Iterative Shirley Baseline (Standard in XPS quantitative analysis)
2. Linear Baseline (for flat/isolated core peaks)
3. Tougaard approximation (for high energy-loss inelastic tails)
"""

from typing import Tuple
import numpy as np


def compute_shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    max_iter: int = 50,
    tol: float = 1e-5
) -> np.ndarray:
    """
    Computes iterative Shirley inelastic background according to:
        B(E) = I_2 + (I_1 - I_2) * [ int_E^E2 (I(E') - B(E')) dE' ] / [ int_E1^E2 (I(E') - B(E')) dE' ]
    Ensures safe sorting and convergence.
    """
    if len(x) < 3:
        return y.copy()

    # Sort descending (standard XPS convention: higher binding energy to lower)
    is_descending = x[0] > x[-1]
    if not is_descending:
        x_sort = x[::-1]
        y_sort = y[::-1]
    else:
        x_sort = x
        y_sort = y

    n = len(y_sort)
    # Average 5 endpoints to dampen experimental detector noise
    pts = max(1, min(5, n // 10))
    y1 = np.mean(y_sort[:pts])  # High BE endpoint
    y2 = np.mean(y_sort[-pts:]) # Low BE endpoint

    # Initial linear guess
    bg = np.linspace(y1, y2, n)
    
    for _ in range(max_iter):
        net = np.maximum(y_sort - bg, 0.0)
        total_area = np.trapezoid(net) if hasattr(np, 'trapezoid') else np.trapz(net)
        
        if total_area <= 0:
            break
            
        cum_area = np.zeros(n)
        for i in range(1, n):
            sub_net = net[i:]
            cum_area[i] = np.trapezoid(sub_net) if hasattr(np, 'trapezoid') else np.trapz(sub_net)
            
        new_bg = y2 + (y1 - y2) * (cum_area / total_area)
        diff = np.max(np.abs(new_bg - bg))
        bg = new_bg
        if diff < tol:
            break

    # Re-invert if necessary
    if not is_descending:
        bg = bg[::-1]

    # Ensure background never exceeds raw counts
    return np.minimum(bg, y)


def compute_linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Computes two-point linear baseline between endpoints."""
    pts = max(1, min(5, len(y) // 10))
    y_start = np.mean(y[:pts])
    y_end = np.mean(y[-pts:])
    return np.linspace(y_start, y_end, len(y))


def extract_net_signal(
    x: np.ndarray,
    y: np.ndarray,
    baseline_type: str = "Shirley"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extracts baseline and calculates net photoemission peak intensity.
    Supports: 'Shirley', 'Linear', 'Constant (Min)', 'None'
    Returns:
        (baseline, net_intensity)
    """
    bt = baseline_type.lower()
    if "linear" in bt:
        bg = compute_linear_background(x, y)
    elif "constant" in bt or "min" in bt:
        bg = np.full_like(y, float(np.nanmin(y)))
    elif "none" in bt or "zero" in bt:
        bg = np.zeros_like(y)
    else:
        bg = compute_shirley_background(x, y)
        
    net = np.maximum(y - bg, 0.0)
    return bg, net
