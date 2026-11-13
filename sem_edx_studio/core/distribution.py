"""
sem_edx_studio.core.distribution
Particle Size Distribution Analysis & Statistical Modeling Engine.
Fits Log-Normal, Gaussian, and Weibull distributions.
Computes d10, d50 (median), d90, and Polydispersity Index (PDI).
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import lognorm, norm, weibull_min


def fit_size_distributions(diameters_nm: np.ndarray) -> Dict[str, Any]:
    """
    Fits continuous statistical distributions to an array of measured particle diameters.
    """
    d = np.asarray(diameters_nm, dtype=float)
    d = d[np.isfinite(d) & (d > 0)]

    if len(d) < 5:
        return {
            "mean_nm": np.nan, "std_nm": np.nan, "median_nm": np.nan,
            "d10_nm": np.nan, "d50_nm": np.nan, "d90_nm": np.nan,
            "pdi": np.nan, "lognormal": {}, "gaussian": {}
        }

    # Percentiles
    d10 = float(np.percentile(d, 10))
    d50 = float(np.percentile(d, 50))
    d90 = float(np.percentile(d, 90))
    pdi = float((d90 - d10) / max(d50, 1e-4))

    mean_d = float(np.mean(d))
    std_d = float(np.std(d))

    # 1. Log-Normal Fit: pdf(x) = 1/(x * s * sqrt(2*pi)) * exp(-(ln(x)-scale)^2 / (2*s^2))
    shape_ln, loc_ln, scale_ln = lognorm.fit(d, floc=0)
    geo_mean = scale_ln  # Median of lognormal is scale
    geo_std = np.exp(shape_ln)

    # 2. Gaussian Fit
    loc_gauss, scale_gauss = norm.fit(d)

    # 3. Weibull Fit
    c_weib, loc_weib, scale_weib = weibull_min.fit(d, floc=0)

    # Generate curves for plotting
    x_dense = np.linspace(max(0.1, np.min(d) * 0.7), np.max(d) * 1.3, 200)
    pdf_lognormal = lognorm.pdf(x_dense, shape_ln, loc_ln, scale_ln)
    pdf_gaussian = norm.pdf(x_dense, loc_gauss, scale_gauss)
    pdf_weibull = weibull_min.pdf(x_dense, c_weib, loc_weib, scale_weib)

    return {
        "count": len(d),
        "mean_nm": round(mean_d, 2),
        "std_nm": round(std_d, 2),
        "median_nm": round(d50, 2),
        "d10_nm": round(d10, 2),
        "d50_nm": round(d50, 2),
        "d90_nm": round(d90, 2),
        "pdi": round(pdi, 3),
        "lognormal": {
            "geometric_mean_nm": round(float(geo_mean), 2),
            "geometric_std": round(float(geo_std), 3),
            "shape": float(shape_ln)
        },
        "gaussian": {
            "mean_nm": round(float(loc_gauss), 2),
            "std_nm": round(float(scale_gauss), 2)
        },
        "weibull": {
            "shape_k": round(float(c_weib), 2),
            "scale_lambda": round(float(scale_weib), 2)
        },
        "x_dense": x_dense,
        "pdf_lognormal": pdf_lognormal,
        "pdf_gaussian": pdf_gaussian,
        "pdf_weibull": pdf_weibull
    }
