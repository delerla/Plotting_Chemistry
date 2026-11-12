"""
baseline.py - FTIR Vibrational Baseline Correction Engines.
Implements Asymmetric Least Squares (AsLS), Concave Rubberband (Convex Hull), Linear, and Min-Zero.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Tuple
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.spatial import ConvexHull


def compute_asls_baseline(
    y: np.ndarray,
    lam: float = 1e6,
    p: float = 0.004,
    niter: int = 12,
) -> np.ndarray:
    """Asymmetric Least Squares sparse solver (Eilers & Boelens) for FTIR absorbance spectra."""
    y_arr = np.asarray(y, dtype=float)
    L = len(y_arr)
    if L < 5:
        return np.zeros_like(y_arr)

    D = sparse.diags([1.0, -2.0, 1.0], [0, -1, -2], shape=(L, L - 2), format="csc")
    D_term = float(lam) * D.dot(D.T)
    w = np.ones(L, dtype=float)
    z = np.copy(y_arr)

    for _ in range(max(3, int(niter))):
        W = sparse.spdiags(w, 0, L, L, format="csc")
        z = spsolve(W + D_term, w * y_arr)
        w = p * (y_arr > z) + (1.0 - p) * (y_arr < z)

    return np.minimum(z, y_arr)


def compute_rubberband_baseline(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Computes the lower convex-hull 'Rubberband' baseline standard in Bruker OPUS / Thermo OMNIC.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    n = len(x_arr)
    if n < 5:
        return np.full_like(y_arr, float(np.nanmin(y_arr)))

    order = np.argsort(x_arr)
    xs = x_arr[order]
    ys = y_arr[order]

    # Normalize coordinates for numerical ConvexHull stability
    x_span = max(float(xs[-1] - xs[0]), 1.0)
    y_span = max(float(np.ptp(ys)), 1e-6)
    pts = np.column_stack(((xs - xs[0]) / x_span, (ys - np.min(ys)) / y_span))

    try:
        hull = ConvexHull(pts)
        # Vertices running monotonically from index 0 to n-1 along lower rim
        v = hull.vertices
        # Roll so index 0 starts first
        idx0 = int(np.argmin(v))
        v = np.roll(v, -idx0)
        idx_end = int(np.argmax(v))
        lower_v = v[: idx_end + 1]
        if len(lower_v) < 2:
            lower_v = np.array([0, n - 1])
        bg_sorted = np.interp(xs, xs[lower_v], ys[lower_v])
    except Exception:
        bg_sorted = np.linspace(ys[0], ys[-1], n)

    bg = np.empty_like(bg_sorted)
    bg[order] = np.minimum(bg_sorted, ys)
    return bg


def compute_linear_baseline(x: np.ndarray, y: np.ndarray, edge_pts: int = 8) -> np.ndarray:
    """Linear baseline anchored across ROI/spectrum edges."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    n = len(y_arr)
    if n < 4:
        return np.zeros_like(y_arr)

    k = max(1, min(edge_pts, n // 8))
    order = np.argsort(x_arr)
    xs, ys = x_arr[order], y_arr[order]
    x1, y1 = float(np.mean(xs[:k])), float(np.mean(ys[:k]))
    x2, y2 = float(np.mean(xs[-k:])), float(np.mean(ys[-k:]))
    slope = (y2 - y1) / max(x2 - x1, 1e-9)
    bg_s = y1 + slope * (xs - x1)

    bg = np.empty_like(bg_s)
    bg[order] = np.minimum(bg_s, ys)
    return bg


def extract_net_absorbance(
    wavenumber: np.ndarray,
    absorbance: np.ndarray,
    method: str = "AsLS (Asymmetric Least Squares)",
    asls_lam: float = 1e6,
    asls_p: float = 0.004,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Strips baseline drift from FTIR absorbance spectra.
    Returns (net_absorbance, baseline_curve).
    """
    x = np.asarray(wavenumber, dtype=float)
    y = np.asarray(absorbance, dtype=float)
    m = method.lower()

    if "asls" in m:
        bg = compute_asls_baseline(y, lam=asls_lam, p=asls_p, niter=12)
    elif "rubber" in m or "hull" in m:
        bg = compute_rubberband_baseline(x, y)
    elif "linear" in m:
        bg = compute_linear_baseline(x, y)
    elif "min" in m:
        bg = np.full_like(y, float(np.nanmin(y)))
    else:
        bg = np.zeros_like(y)

    y_net = np.maximum(y - bg, 0.0)
    return y_net, bg
