"""Empirical joint support for oxygen, pressure, and forced flow."""

from __future__ import annotations

import numpy as np
from scipy.spatial import ConvexHull, QhullError


class JointDomain:
    """Convex support in the affine subspace spanned by one material's tests."""

    def __init__(self, points: np.ndarray):
        values = np.unique(np.asarray(points, dtype=float), axis=0)
        if values.ndim != 2 or values.shape[1] != 3 or not len(values):
            raise ValueError("Joint domain requires oxygen, pressure, and flow observations")
        self.origin = values.mean(axis=0)
        self.scale = np.ptp(values, axis=0)
        self.scale[self.scale == 0] = 1.0
        centered = (values - self.origin) / self.scale
        _, singular, vh = np.linalg.svd(centered, full_matrices=False)
        tolerance = max(centered.shape) * np.finfo(float).eps * singular[0] if len(singular) else 0.0
        self.rank = int(np.sum(singular > tolerance)) if tolerance else 0
        self.basis = vh[: self.rank].T
        self.projected = centered @ self.basis
        self.hull = None
        if self.rank >= 2:
            try:
                self.hull = ConvexHull(self.projected)
            except QhullError:
                # A malformed or nearly degenerate hull must not silently admit queries.
                self.hull = None

    def contains(self, point: list[float] | np.ndarray) -> bool:
        query = np.asarray(point, dtype=float)
        if query.shape != (3,) or not np.isfinite(query).all():
            return False
        centered = (query - self.origin) / self.scale
        if self.rank == 0:
            return bool(np.linalg.norm(centered) <= 1e-8)
        projection = centered @ self.basis
        residual = centered - projection @ self.basis.T
        if np.linalg.norm(residual) > 1e-8:
            return False
        if self.rank == 1:
            return bool(
                self.projected.min() - 1e-8 <= projection[0]
                <= self.projected.max() + 1e-8
            )
        if self.hull is None:
            return False
        distance = self.hull.equations[:, :-1] @ projection + self.hull.equations[:, -1]
        return bool(np.all(distance <= 1e-8))
