# FILE: utils.py
"""
Utility functions for Pist01 Beat v3.4.

This module provides small, reusable tools used across all engines:
- safe division
- clamping values
- linear scaling
- normalization
- weighted averages
- basic validators

None of these functions contain basketball logic. They are pure utilities.
"""

import math


# ============================================================
# BASIC SAFETY UTILITIES
# ============================================================

def safe_divide(numerator, denominator, fallback=0.0):
    """
    Safely divide two numbers.
    If denominator is zero or near-zero, return fallback.
    """
    if abs(denominator) < 1e-9:
        return fallback
    return numerator / denominator


def clamp(value, min_value, max_value):
    """
    Clamp a value between a minimum and maximum.
    """
    return max(min_value, min(max_value, value))


def is_number(x):
    """
    Returns True if x is a valid number (includes ints and floats),
    False for None, NaN, or invalid types.
    """
    if x is None:
        return False
    if isinstance(x, (int, float)):
        return not math.isnan(x)
    return False


# ============================================================
# SCALING + NORMALIZATION UTILITIES
# ============================================================

def linear_scale(value, in_min, in_max, out_min, out_max):
    """
    Map value from one range to another using linear interpolation.
    Handles reversed ranges safely.
    """
    if in_max - in_min == 0:
        return out_min
    ratio = (value - in_min) / (in_max - in_min)
    return out_min + ratio * (out_max - out_min)


def normalize(value, mean, std_dev, fallback=0.0):
    """
    Basic z-score normalization.
    Returns fallback if std_dev is zero.
    """
    if std_dev == 0:
        return fallback
    return (value - mean) / std_dev


# ============================================================
# AGGREGATION UTILITIES
# ============================================================

def weighted_average(values, weights):
    """
    Compute the weighted average of a list of values.
    Returns None if lengths mismatch or if total weight is zero.
    """
    if len(values) != len(weights):
        return None
    total_weight = sum(weights)
    if total_weight == 0:
        return None
    return sum(v * w for v, w in zip(values, weights)) / total_weight


# ============================================================
# VALUE CLEANING / SANITY UTILITIES
# ============================================================

def safe_float(x, fallback=0.0):
    """
    Convert x to float if possible; otherwise return fallback.
    """
    try:
        return float(x)
    except (ValueError, TypeError):
        return fallback


def bounded_mean(values, min_value=None, max_value=None):
    """
    Compute mean of values, optionally forcing bounds on result.
    """
    if not values:
        return None
    mean_val = sum(values) / len(values)
    if min_value is not None:
        mean_val = max(min_value, mean_val)
    if max_value is not None:
        mean_val = min(max_value, mean_val)
    return mean_val


if __name__ == "__main__":
    print("utils.py loaded successfully.")
