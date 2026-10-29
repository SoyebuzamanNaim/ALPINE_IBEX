"""Automated tests for Phase 07 Experimental Envelope Guard."""
import pytest
from src.envelope.guard import EnvelopeGuard


def test_in_domain_standard_condition():
    guard = EnvelopeGuard()
    # 21% O2 on PMMA was in range only because of the 49 unsupported rows; the
    # BASS-II extraction this pipeline still uses tops out at 20.8% O2. Addendum 7.
    res = guard.check(oxygen_pct=19.0, pressure_kpa=101.3, flow_cm_s=5.0, material="PMMA")
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


def test_joint_domain_refuses_sparse_rectangle_corner():
    guard = EnvelopeGuard()
    # Every coordinate is individually in range, but this combination is outside
    # the convex hull of Cellulose experiments.
    res = guard.check(oxygen_pct=22.0, pressure_kpa=70.0, flow_cm_s=20.0, material="Cellulose")
    assert res["in_training_range"] is False
    assert res["status"] == "joint_extrapolation"
    assert any(r["feature"] == "joint_domain" for r in res["out_of_range_reasons"])
    assert len(res["nearest_experiments"]) == 3


def test_low_rank_material_joint_domain_rejects_off_line_point():
    guard = EnvelopeGuard()
    assert guard.joint_domains["Mylar"].contains([16.5, 70.3, 30.0])
    assert not guard.joint_domains["Mylar"].contains([16.5, 70.3, 29.0])


@pytest.mark.parametrize(
    "oxygen, pressure, flow, material, expected_ids",
    [
        (17.1, 101.3, 5.0, "Cotton-Fiberglass", {"BASS2_T11_5", "BASS2_T22_5"}),
        (17.3, 101.3, 10.0, "PMMA", {"BASS2_B19_10", "BASS2_T7_10"}),
        (18.0, 101.3, 3.0, "PMMA", {"BASS2_O3a_3", "BASS2_O3b_3"}),
        (22.0, 100.0, 20.0, "PMMA", {"SAF_II_8", "SAF_IV_2"}),
    ],
)
def test_identical_inputs_with_conflicting_outcomes_abstain(
    oxygen, pressure, flow, material, expected_ids
):
    result = EnvelopeGuard().check(oxygen, pressure, flow, material)
    assert result["in_training_range"] is True
    assert result["status"] == "conflicting_evidence"
    assert result["requires_abstention"] is True
    assert result["out_of_range_reasons"] == []
    assert expected_ids <= {item["experiment_id"] for item in result["nearest_experiments"]}
    assert "opposite" in result["explanation"].lower() or "conflict" in result["explanation"].lower()
