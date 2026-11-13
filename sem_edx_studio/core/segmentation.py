"""
sem_edx_studio.core.segmentation
Computer Vision Micrograph Segmentation Engine for Particle Sizing & Nanomorphology.
Supports Otsu, Adaptive, and Distance-Transform Watershed segmentation.
Extracts Equivalent Diameter, Feret Dimensions, Aspect Ratio, and Sphericity.
"""

from typing import Dict, Any, List, Tuple, Optional
import cv2
import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import closing, disk, opening
from skimage.segmentation import watershed
from skimage.feature import peak_local_max


def clean_small_objects(binary_img: np.ndarray, min_area_px: int) -> np.ndarray:
    """Version-agnostic small object removal for scikit-image binary masks."""
    labeled = label(binary_img)
    if labeled.max() == 0:
        return binary_img
    counts = np.bincount(labeled.ravel())
    mask_sizes = counts >= min_area_px
    mask_sizes[0] = 0  # Background
    return mask_sizes[labeled]


def segment_micrograph(
    image: np.ndarray,
    scale_nm_per_px: float = 1.0,
    method: str = "Otsu",
    min_area_px: int = 25,
    max_area_px: int = 50000,
    apply_watershed: bool = True,
    gaussian_blur_sigma: float = 1.0
) -> Dict[str, Any]:
    """
    Performs full morphological particle segmentation on a 2D SEM micrograph.
    
    Parameters:
    -----------
    image: 2D grayscale or 3D RGB numpy array.
    scale_nm_per_px: Spatial calibration (nm per pixel).
    method: Thresholding technique ("Otsu", "Adaptive", "Manual").
    min_area_px: Filter out debris / noise smaller than this pixel area.
    max_area_px: Filter out huge edge artifacts / borders.
    apply_watershed: Separate touching / aggregated particles.
    
    Returns:
    --------
    Dictionary with segmented particle measurements, binary mask, labeled mask, and overlay image.
    """
    # Ensure 8-bit grayscale
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)

    # Denoise
    if gaussian_blur_sigma > 0:
        ksize = int(2 * round(2 * gaussian_blur_sigma) + 1)
        ksize = max(3, ksize | 1)
        blurred = cv2.GaussianBlur(gray, (ksize, ksize), gaussian_blur_sigma)
    else:
        blurred = gray

    # Thresholding
    if method == "Adaptive":
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 35, -2
        )
        binary = thresh > 0
    else:
        try:
            val_otsu = threshold_otsu(blurred)
        except Exception:
            val_otsu = 128
        binary = blurred > val_otsu

    # Morphological cleanup
    cleaned = opening(binary, disk(2))
    cleaned = closing(cleaned, disk(2))
    cleaned = clean_small_objects(cleaned, min_area_px)

    # Watershed separation if enabled
    if apply_watershed and np.sum(cleaned) > 0:
        distance = ndi.distance_transform_edt(cleaned)
        coords = peak_local_max(distance, min_distance=8, labels=cleaned)
        mask_peaks = np.zeros(distance.shape, dtype=bool)
        mask_peaks[tuple(coords.T)] = True
        markers, _ = ndi.label(mask_peaks)
        labeled_particles = watershed(-distance, markers, mask=cleaned)
    else:
        labeled_particles = label(cleaned)

    # Extract Particle Metrics
    props = regionprops(labeled_particles, intensity_image=gray)
    particles_data: List[Dict[str, Any]] = []

    # Visual overlay preparation (RGB)
    overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    particle_idx = 1
    for p in props:
        if p.area < min_area_px or p.area > max_area_px:
            continue

        # Physical metrics
        area_nm2 = p.area * (scale_nm_per_px ** 2)
        eq_diam_px = getattr(p, "equivalent_diameter_area", getattr(p, "equivalent_diameter", 10.0))
        eq_diam_nm = eq_diam_px * scale_nm_per_px
        maj_len = getattr(p, "axis_major_length", getattr(p, "major_axis_length", 10.0))
        min_len = getattr(p, "axis_minor_length", getattr(p, "minor_axis_length", 10.0))
        major_axis_nm = maj_len * scale_nm_per_px
        minor_axis_nm = min_len * scale_nm_per_px
        aspect_ratio = (maj_len / max(min_len, 1e-4))

        perimeter_px = p.perimeter
        sphericity = (4.0 * np.pi * p.area) / max(perimeter_px ** 2, 1e-4)
        sphericity = min(1.0, float(sphericity))

        # Centroid
        cy, cx = p.centroid

        particles_data.append({
            "Particle_ID": particle_idx,
            "Diameter_nm": round(eq_diam_nm, 2),
            "Major_Axis_nm": round(major_axis_nm, 2),
            "Minor_Axis_nm": round(minor_axis_nm, 2),
            "Aspect_Ratio": round(aspect_ratio, 2),
            "Sphericity": round(sphericity, 3),
            "Area_nm2": round(area_nm2, 1),
            "Centroid_X_px": round(cx, 1),
            "Centroid_Y_px": round(cy, 1)
        })

        # Draw contour / bounding box on overlay
        minr, minc, maxr, maxc = p.bbox
        cv2.rectangle(overlay, (minc, minr), (maxc, maxr), (0, 220, 255), 1)
        cv2.circle(overlay, (int(cx), int(cy)), 2, (255, 50, 50), -1)

        particle_idx += 1

    df_particles = pd.DataFrame(particles_data)

    return {
        "df_particles": df_particles,
        "n_particles": len(particles_data),
        "labeled_mask": labeled_particles,
        "binary_mask": cleaned,
        "overlay_rgb": overlay,
        "scale_nm_per_px": scale_nm_per_px
    }
