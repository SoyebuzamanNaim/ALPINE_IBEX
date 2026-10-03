"""Structured nearest-neighbor search over verified microgravity experiments."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "cache" / "experiments.parquet"


class NearestExperimentRetriever:
    def __init__(self, data_path: Path = DATA_FILE):
        if not data_path.exists():
            raise FileNotFoundError(f"Missing experiments dataset: {data_path}")
        self.df = pd.read_parquet(data_path)
        
        # Calculate feature ranges for normalization
        self.o2_range = float(self.df["oxygen_pct"].max() - self.df["oxygen_pct"].min()) or 1.0
        self.p_range = float(self.df["pressure_kpa"].max() - self.df["pressure_kpa"].min()) or 1.0
        self.flow_range = float(self.df["flow_cm_s"].max() - self.df["flow_cm_s"].min()) or 1.0

    def find_nearest(
        self,
        oxygen_pct: float,
        pressure_kpa: float,
        flow_cm_s: float,
        material: str,
        k: int = 3,
        material_penalty: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Find the k nearest real NASA experiments by normalized feature distance.
        
        A material mismatch receives a large penalty (default 10.0) per Challenge Brief §7.
        """
        # Normalized deltas
        delta_o2 = np.abs(self.df["oxygen_pct"].values - oxygen_pct) / self.o2_range
        delta_p = np.abs(self.df["pressure_kpa"].values - pressure_kpa) / self.p_range
        delta_flow = np.abs(self.df["flow_cm_s"].values - flow_cm_s) / self.flow_range

        # Material penalty
        mat_mismatch = (self.df["material"].values != material).astype(float) * material_penalty

        # Euclidean distance
        distances = np.sqrt(delta_o2**2 + delta_p**2 + delta_flow**2) + mat_mismatch

        # Top k indices
        top_k_indices = np.argsort(distances)[:k]

        results = []
        for idx in top_k_indices:
            row = self.df.iloc[idx]
            dist = float(distances[idx])

            # Matched and mismatched analysis
            matched = []
            mismatched = []

            if abs(row["oxygen_pct"] - oxygen_pct) <= 1.0:
                matched.append(f"oxygen_pct ({row['oxygen_pct']}%)")
            else:
                mismatched.append(f"oxygen_pct (observed {row['oxygen_pct']}%, requested {oxygen_pct}%)")

            if abs(row["pressure_kpa"] - pressure_kpa) <= 5.0:
                matched.append(f"pressure_kpa ({row['pressure_kpa']} kPa)")
            else:
                mismatched.append(f"pressure_kpa (observed {row['pressure_kpa']} kPa, requested {pressure_kpa} kPa)")

            if abs(row["flow_cm_s"] - flow_cm_s) <= 2.0:
                matched.append(f"flow_cm_s ({row['flow_cm_s']} cm/s)")
            else:
                mismatched.append(f"flow_cm_s (observed {row['flow_cm_s']} cm/s, requested {flow_cm_s} cm/s)")

            if row["material"] == material:
                matched.append(f"material ({material})")
            else:
                mismatched.append(f"material (observed {row['material']}, requested {material})")

            # Format strictly matching the Challenge Brief §7 API contract
            results.append({
                "experiment_id": str(row["experiment_id"]),
                "investigation": str(row["investigation"]),
                "material": str(row["material"]),
                "oxygen_pct": float(row["oxygen_pct"]),
                "pressure_kpa": float(row["pressure_kpa"]),
                "flow_cm_s": float(row["flow_cm_s"]),
                "outcome": str(row["outcome"]),
                "distance": round(dist, 4),
                "report_id": str(row["report_id"]),
                "source_url": str(row["source_url"]),
                "source_page": int(row["source_page"]) if pd.notnull(row.get("source_page")) else None,
                "source_table": str(row["source_table"]) if pd.notnull(row.get("source_table")) else None,
                "matched_variables": matched,
                "mismatched_variables": mismatched,
                "similarity_explanation": f"Observed {row['outcome']} in {row['investigation']} at {row['oxygen_pct']}% O2, {row['flow_cm_s']} cm/s flow."
            })

        return results
