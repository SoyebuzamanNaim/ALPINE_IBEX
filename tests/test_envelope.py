"""Automated tests for Phase 07 Experimental Envelope Guard."""
import pytest
from src.envelope.guard import EnvelopeGuard


def test_in_domain_standard_condition():
    guard = EnvelopeGuard()
    res = guard.check(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA")
    assert res["in_training_range"] is True
    assert res["status"] in ["in_domain", "boundary"]
    assert res["out_of_range_reasons"] == []
    assert len(res["nearest_experiments"]) == 3
    assert res["explanation"] is None


def test_boundary_condition():
    guard = EnvelopeGuard()
    # 16.5% O2 on PMMA is the physical near-extinction boundary
    res = guard.check(oxygen_pct=16.5, pressure_kpa=101.3, flow_cm_s=3.0, material="PMMA")
    assert res["in_training_range"] is True
    assert res["status"] == "boundary"
    assert "boundary" in (res["warning_message"] or "").lower()


def test_global_out_of_range_refusal():
    guard = EnvelopeGuard()
    # 40% O2 exceeds the maximum published training envelope
    res = guard.check(oxygen_pct=40.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA")
    assert res["in_training_range"] is False
    assert res["status"] == "extrapolation"
    assert len(res["out_of_range_reasons"]) > 0
    assert res["out_of_range_reasons"][0]["feature"] == "oxygen_pct"
    assert "train_min" in res["out_of_range_reasons"][0]
    assert "train_max" in res["out_of_range_reasons"][0]
    # Nearest experiments MUST still be returned per Challenge Brief §4
    assert len(res["nearest_experiments"]) == 3
    assert "Requested conditions are outside" in res["explanation"]


def test_unsupported_material_refusal():
    guard = EnvelopeGuard()
    res = guard.check(oxygen_pct=21.0, pressure_kpa=101.3, flow_cm_s=5.0, material="Kapton")
    assert res["in_training_range"] is False
    assert res["status"] == "unsupported_category"
    assert any(r["feature"] == "material" for r in res["out_of_range_reasons"])
    assert len(res["nearest_experiments"]) == 3


def test_per_material_out_of_range():
    guard = EnvelopeGuard()
    # Nomex was only tested between 20.8% and 34.0% O2; 17% O2 is out of range for Nomex
    res = guard.check(oxygen_pct=17.0, pressure_kpa=101.3, flow_cm_s=5.0, material="Nomex")
    assert res["in_training_range"] is False
    assert res["status"] == "extrapolation"
    assert any("Nomex" in r["reason"] for r in res["out_of_range_reasons"])


def test_sparse_region_detection():
    guard = EnvelopeGuard()
    # Valid bounding box for PMMA [0.0, 35.0], but high flow + elevated O2 at low pressure is sparse
    res = guard.check(oxygen_pct=32.0, pressure_kpa=60.0, flow_cm_s=34.0, material="PMMA")
    assert "knn_mean_distance" in res
    assert isinstance(res["sparse_region_warning"], bool)
