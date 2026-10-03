"""Automated tests for Phase 08 Counterfactual Engine."""
import pytest
from src.features.counterfactual import CounterfactualEngine


@pytest.fixture
def engine():
    return CounterfactualEngine()


def test_evaluate_scenario_in_domain(engine):
    res = engine.evaluate_scenario(
        oxygen_pct=21.0,
        pressure_kpa=101.3,
        flow_cm_s=5.0,
        material="PMMA",
    )
    assert res["in_training_range"] is True
    assert res["prediction"] in ["spread", "marginal_spread", "no_spread"]
    assert res["probabilities"] is not None
    assert set(res["probabilities"].keys()) == {"no_spread", "marginal_spread", "spread"}
    assert len(res["nearest_experiments"]) == 3
    assert res["confidence"] > 0.5


def test_evaluate_scenario_out_of_range(engine):
    res = engine.evaluate_scenario(
        oxygen_pct=45.0,
        pressure_kpa=101.3,
        flow_cm_s=5.0,
        material="PMMA",
    )
    assert res["in_training_range"] is False
    assert res["prediction"] is None
    assert res["probabilities"] is None
    assert res["status"] == "extrapolation"
    assert len(res["out_of_range_reasons"]) > 0
    assert len(res["nearest_experiments"]) == 3  # Evidence preserved per brief


def test_compute_perturbation_oxygen_drop(engine):
    baseline = {
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    # Perturb oxygen downwards to near extinction
    cf = engine.compute_perturbation(baseline, {"oxygen_pct": 16.5})

    assert cf["baseline"]["prediction"] == "spread"
    assert cf["counterfactual"]["prediction"] in ["no_spread", "marginal_spread"]
    assert cf["prediction_delta"]["changed"] is True
    assert cf["prediction_delta"]["from_regime"] == "spread"
    assert cf["prediction_delta"]["to_regime"] in ["no_spread", "marginal_spread"]

    # Probability of spread must drop
    assert cf["probability_deltas"]["spread"] < 0
    # Probability of extinction/no_spread or marginal must rise
    assert (
        cf["probability_deltas"]["no_spread"] > 0
        or cf["probability_deltas"]["marginal_spread"] > 0
    )

    # Variables delta check
    assert cf["changed_variables"]["oxygen_pct"]["delta"] == -4.5
    assert "scientific_disclaimer" in cf
    assert len(cf["evidence_delta"]["shared_experiment_ids"]) >= 0


def test_run_sweep_oxygen_boundary(engine):
    baseline = {
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    sweep = engine.run_sweep(
        baseline=baseline,
        param="oxygen_pct",
        start=21.0,
        end=16.0,
        steps=11,  # 0.5% increments
    )

    assert sweep["parameter"] == "oxygen_pct"
    assert len(sweep["points"]) == 11
    # Check that at least one transition occurred (e.g. spread -> marginal or no_spread)
    assert sweep["total_transitions"] >= 1

    first_transition = sweep["transitions"][0]
    assert first_transition["from_regime"] != first_transition["to_regime"]
    assert len(first_transition["evidence_before"]) > 0
    assert len(first_transition["evidence_after"]) > 0

    # Safety margin check
    margin = sweep["safety_margin"]
    assert margin is not None
    assert "boundary_midpoint" in margin
    assert margin["baseline_value"] == 21.0
    assert margin["delta_to_boundary"] > 0  # 21% is above the extinction limit


def test_sweep_invalid_parameter(engine):
    baseline = {
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    with pytest.raises(ValueError, match="Continuous sweep parameter 'material' not supported"):
        engine.run_sweep(baseline, "material", 0, 1)


def test_counterfactual_unsupported_material(engine):
    baseline = {
        "oxygen_pct": 21.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA",
    }
    cf = engine.compute_perturbation(baseline, {"material": "Teflon"})
    assert cf["counterfactual"]["in_training_range"] is False
    assert cf["counterfactual"]["status"] == "unsupported_category"
    assert cf["counterfactual"]["prediction"] is None
