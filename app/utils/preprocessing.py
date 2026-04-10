#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =========================================================
# Spectral preprocessing utilities for TB-SERS Analyzer
# =========================================================

import numpy as np
import pandas as pd
import scipy.stats as stats

from sklearn.decomposition import PCA
from sklearn.covariance import MinCovDet
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

from pybaselines import Baseline 

# ========================
# Parameters
# ========================
COSMIC_THRESHOLD = 8
PCA_COMPONENTS = 5
OUTLIER_CONFIDENCE = 0.90
POLY_ORDER = 3


# =========================================================
# 1. Cosmic Ray Removal
# =========================================================

def modified_z_score(y):
    median_y = np.median(y)
    mad = np.median(np.abs(y - median_y))

    if mad == 0:
        return np.zeros_like(y)

    return 0.6745 * (y - median_y) / mad


def remove_cosmic_rays(y, threshold=COSMIC_THRESHOLD):
    mz = modified_z_score(y)
    spikes = np.abs(mz) > threshold
    y_out = y.copy()

    for i in range(len(spikes)):
        if spikes[i]:
            if 0 < i < len(y) - 1:
                y_out[i] = np.median([y[i - 1], y[i + 1]])
            elif i == 0:
                y_out[i] = y[i + 1]
            else:
                y_out[i] = y[i - 1]

    return y_out


# =========================================================
# 2. R2 Score (Spectral similarity)
# =========================================================

def compute_r2_score(list_intensity, features):

    df = pd.DataFrame(list_intensity, columns=np.flip(features))
    X = df.to_numpy()

    r2_list = []

    for i in range(len(X)):
        for j in range(len(X)):
            if i == j:
                continue

            x1 = X[i]
            x2 = X[j]

            # Min-max normalization
            x1_norm = (x1 - np.min(x1)) / (np.max(x1) - np.min(x1) + 1e-8)
            x2_norm = (x2 - np.min(x2)) / (np.max(x2) - np.min(x2) + 1e-8)

            r2 = abs(r2_score(x1_norm, x2_norm))
            r2 = min(r2, 1.0)

            r2_list.append(r2)

    return np.mean(r2_list) if len(r2_list) > 0 else 0.0


# =========================================================
# 3. QC Filtering (PCA + Mahalanobis)
# =========================================================

def qc_filter_zscore(df):
    """
    Returns:
        filtered_df
        removed_indices
    """

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df)

    pca = PCA(n_components=PCA_COMPONENTS)
    scores = pca.fit_transform(scaled)

    robust_cov = MinCovDet().fit(scores)
    mahal = robust_cov.mahalanobis(scores)

    cutoff = stats.chi2.ppf(OUTLIER_CONFIDENCE, df=PCA_COMPONENTS)
    mask = mahal < cutoff

    filtered_df = df[mask]
    removed_idx = np.where(~mask)[0]

    print("After outlier removal:", len(filtered_df))

    if len(filtered_df) == 0:
        raise ValueError("All spectra removed during QC filtering")

    return filtered_df, removed_idx


# =========================================================
# 4. Baseline Correction + SNV + Averaging
# =========================================================

def baseline_correct_average(df, poly_order=POLY_ORDER):

    processed = []

    for spec in df.to_numpy():

        # Baseline correction
        baseline = Baseline().poly(spec, poly_order=poly_order)[0]
        corrected = spec - baseline

        # Shift to positive
        corrected = corrected - np.min(corrected)

        processed.append(corrected)

    processed = np.array(processed)

    # ========================
    # SNV normalization
    # ========================
    mean_val = np.mean(processed, axis=1, keepdims=True)
    std_val = np.std(processed, axis=1, keepdims=True)

    std_val[std_val == 0] = 1

    processed = (processed - mean_val) / std_val

    # ========================
    # Averaging
    # ========================
    final_average = np.mean(processed, axis=0)

    return final_average