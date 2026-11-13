"""Unfitted input transforms with a stable import path for serialized experiments."""
import numpy as np


def physical_terms(values):
    """Derive quantities without a published boundary fitted to evaluation outcomes."""
    values = np.asarray(values, dtype=float)
    oxygen, pressure, flow = values.T
    return np.column_stack((values, oxygen * pressure / 100, np.log1p(flow),
                            oxygen * np.log1p(flow), oxygen / (1 + flow)))
