"""
background.py - Powder & Thin-Film XRD Baseline Stripping Engines.
Implements Asymmetric Least Squares (AsLS), SNIP (LLS), Linear, and Minimum-Constant baselines.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Tuple
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


def compute_asls_background(
    y: np.ndarray,
    lam: float = 1e5,
    p: float = 0.005,
    niter: int = 12,
) -> np.ndarray:
    """
    Asymmetric Least Squares (Eilers & Boelens, 2005) baseline estimation.
    Ideal for removing amorphous glass humps, air scatter, and capillary backgrounds
    under sharp Bragg reflections without distorting peak tails.
    """
    y_arr = np.asarray(y, dtype=float)
    L = len(y_arr)
    if L < 5:
        return np.zeros_like(y_arr)

    # Sparse second-order difference matrix D
    D = sparse.diags([1.0, -2.0, 1.0], [0, -1, -2], shape=(L, L - 2), format="csc")
    D_term = float(lam) * D.dot(D.T)
    w = np.ones(L, dtype=float)
    z = np.copy(y_arr)

    for _ in range(max(3, int(niter))):
        W = sparse.spdiags(w, 0, L, L, format="csc")
        Z = W + D_term
        z = spsolve(Z, w * y_arr)
        w = p * (y_arr > z) + (1.0 - p) * (y_arr < z)

    return np.minimum(z, y_arr)


def compute_snip_background(
    y: np.ndarray,
    max_half_window: int = 35,
    decreasing: bool = True,
) -> np.ndarray:
    """
    Statistics-sensitive Non-linear Iterative Peak-clipping (SNIP) with LLS transform.
    Standard crystallographic background estimator used in powder diffraction refinement.
    """
    y_arr = np.maximum(np.asarray(y, dtype=float), 0.0)
    n = len(y_arr)
    if n < 10:
        return np.zeros_like(y_arr)

    # Log-Log-Sqrt (LLS) compression stabilizes dynamic range across strong/weak peaks
    v = np.log(np.log(np.sqrt(y_arr + 1.0) + 1.0) + 1.0)
    max_hw = int(max(2, min(max_half_window, n // 4)))
    widths = range(max_hw, 0, -1) if decreasing else range(1, max_hw + 1)

    for w in widths:
        v_left = np.roll(v, w)
        v_right = np.roll(v, -w)
        avg = 0.5 * (v_left + v_right)
        # Keep edge regions untouched by roll wraparound
        avg[:w] = v[:w]
        avg[-w:] = v[-w:]
        v = np.minimum(v, avg)

    bg = (np.exp(np.exp(v) - 1.0) - 1.0) ** 2 - 1.0
    return np.clip(bg, 0.0, y_arr)


def compute_linear_background(x: np.ndarray, y: np.ndarray, edge_pts: int = 8) -> np.ndarray:
    """Computes a straight-line baseline anchored by pattern endpoints."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    n = len(y_arr)
    if n < 4:
        return np.zeros_like(y_arr)

    k = max(1, min(edge_pts, n // 6))
    x1, y1 = float(np.mean(x_arr[:k])), float(np.mean(y_arr[:k]))
    x2, y2 = float(np.mean(x_arr[-k:])), float(np.mean(y_arr[-k:]))
    if abs(x2 - x1) < 1e-12:
        return np.full_like(y_arr, min(y1, y2))

    slope = (y2 - y1) / (x2 - x1)
    bg = y1 + slope * (x_arr - x1)
    return np.minimum(bg, y_arr)


def extract_net_pattern(
    two_theta: np.ndarray,
    intensity: np.ndarray,
    method: str = "AsLS (Asymmetric Least Squares)",
    asls_lam: float = 1e5,
    asls_p: float = 0.005,
    snip_window: int = 35,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Subtracts crystallographic background from an XRD pattern.
    Returns (net_intensity, background_curve).
    """
    x = np.asarray(two_theta, dtype=float)
    y = np.asarray(intensity, dtype=float)
    m = method.lower()

    if "asls" in m:
        bg = compute_asls_background(y, lam=asls_lam, p=asls_p, niter=12)
    elif "snip" in m:
        bg = compute_snip_background(y, max_half_window=snip_window, decreasing=True)
    elif "linear" in m:
        bg = compute_linear_background(x, y)
    elif "const" in m or "min" in m:
        bg = np.full_like(y, float(np.nanmin(y)))
    else:
        bg = np.zeros_like(y)

    y_net = np.maximum(y - bg, 0.0)
    return y_net, bg
