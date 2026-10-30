"""Automated tests for Phase 09 Agentic System."""
import pytest
from src.agents.auditor import EvidenceAuditor
from src.agents.composer import ExplanationComposer
from src.agents.interpreter import ScenarioInterpreter
from src.agents.model_router import ModelRouter
from src.agents.orchestrator import AgentOrchestrator, OrchestratorState
from src.agents.retriever import EvidenceRetrieverAgent


@pytest.fixture
def interpreter():
    return ScenarioInterpreter()


@pytest.fixture
def auditor():
    return EvidenceAuditor()


@pytest.fixture
def composer(auditor):
    return ExplanationComposer(auditor=auditor)


@pytest.fixture
def orchestrator():
    return AgentOrchestrator()


def test_scenario_interpreter_natural_language(interpreter):
    text = "Evaluate 21% O2 at sea level with 5.0 cm/s ventilation for acrylic fuel"
    res = interpreter.parse(text)
    assert res["is_valid"] is True
    assert res["parsed_scenario"]["material"] == "PMMA"
    assert res["parsed_scenario"]["oxygen_pct"] == 21.0
    assert res["parsed_scenario"]["pressure_kpa"] == 101.3
    assert res["parsed_scenario"]["flow_cm_s"] == 5.0


def test_scenario_interpreter_ambiguity(interpreter):
    text = "What happens if we burn something at 25% oxygen?"
    res = interpreter.parse(text)
    assert res["is_valid"] is False
    assert len(res["ambiguities"]) > 0
    assert any("material" in a.lower() for a in res["ambiguities"])
    assert any("pressure" in a.lower() for a in res["ambiguities"])


@pytest.mark.parametrize(
    "query, field",
    [
        ("PMMA and Nomex at 21% O2, 101.3 kPa, 5 cm/s", "material"),
        ("PMMA at 21% O2 or 34% O2, 101.3 kPa, 5 cm/s", "oxygen"),
        ("PMMA at 21% O2, 101.3 kPa or 56.5 kPa, 5 cm/s", "pressure"),
        ("PMMA at 21% O2, sea level or 56.5 kPa, 5 cm/s", "pressure"),
        ("PMMA at 21% O2, 101.3 kPa, 5 cm/s or 10 cm/s", "flow"),
        ("PMMA at 21% O2, 101.3 kPa, quiescent or 5 cm/s", "flow"),
    ],
)
def test_scenario_interpreter_rejects_conflicting_values(interpreter, query, field):
    result = interpreter.parse(query)
    assert result["is_valid"] is False
    assert result["parsed_scenario"] is None
    assert any(field in item.lower() for item in result["ambiguities"])


def test_scenario_interpreter_accepts_repeated_equivalent_values(interpreter):
    result = interpreter.parse("Acrylic PMMA at 21% O2 and 21% oxygen, sea level 101.3 kPa, 5 cm/s")
    assert result["is_valid"] is True
    assert result["parsed_scenario"]["material"] == "PMMA"


def test_scenario_interpreter_recognizes_current_composite_material(interpreter):
    result = interpreter.parse("Cotton-Fiberglass at 21% O2, 101.3 kPa, 5 cm/s")
    assert result["is_valid"] is True
    assert result["parsed_scenario"]["material"] == "Cotton-Fiberglass"


@pytest.mark.parametrize(
    "query, field",
    [
        ("PMMA at -5% O2, 101.3 kPa, 5 cm/s", "oxygen"),
        ("PMMA at 1e2% O2, 101.3 kPa, 5 cm/s", "oxygen"),
        ("PMMA at 21-25% O2, 101.3 kPa, 5 cm/s", "oxygen"),
        ("PMMA at 21% O2, -5 kPa, 5 cm/s", "pressure"),
        ("PMMA at 21% O2, 70-100 kPa, 5 cm/s", "pressure"),
        ("PMMA at 21% O2, 101.3 kPa, -5 cm/s", "flow"),
        ("PMMA at 21% O2, 101.3 kPa, 5 to 10 cm/s", "flow"),
        ("PMMA at 21% O2 or +34% O2, 101.3 kPa, 5 cm/s", "oxygen"),
        ("PMMA at 21% O2, 101.3 kPa, 5 cm/s or +10 cm/s", "flow"),
    ],
)
def test_scenario_interpreter_rejects_malformed_or_ranged_numbers(interpreter, query, field):
    result = interpreter.parse(query)
    assert result["is_valid"] is False
    assert result["parsed_scenario"] is None
    assert any(field in item.lower() for item in result["ambiguities"])


def test_scenario_interpreter_ignores_labeled_non_oxygen_percentage(interpreter):
    result = interpreter.parse("PMMA at 21% O2, 30% relative humidity, 101.3 kPa, 5 cm/s")
    assert result["is_valid"] is True
    assert result["parsed_scenario"]["oxygen_pct"] == 21.0


def test_evidence_retriever():
    agent = EvidenceRetrieverAgent()
    res = agent.retrieve(21.0, 101.3, 5.0, "PMMA", k=3)
    assert len(res["nearest_experiments"]) == 3
    for exp in res["nearest_experiments"]:
        assert "experiment_id" in exp
        assert "report_id" in exp
        assert "source_url" in exp


def test_model_router():
    router = ModelRouter()
    meta = router.get_model_metadata()
    assert meta["type"] == "gradient_boosting"
    assert meta["n_train"] == 200
    # Records what the honest data gives, and is not a target. Removing the 49
    # unsupported rows left four report groups, so report-grouped CV trains on 21
    # rows whenever BASS-II is the held-out fold. The requirement this used to
    # stand for lives in test_models.py::test_model_beats_majority_baseline, which
    # is a strict xfail because the model does not currently meet it. See reports/REBUILT_MODEL_EVALUATION.md Addendum 7.
    assert meta["cv_accuracy"] > 0.50

    res = router.predict(21.0, 101.3, 5.0, "PMMA")
    assert res["prediction"] in ["spread", "marginal_spread", "no_spread"]
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=1e-3)


def test_auditor_numerical_rejection(auditor):
    pred_obj = {
        "inputs": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
        "in_training_range": True,
        "prediction": "spread",
        "probabilities": {"spread": 0.977, "marginal_spread": 0.015, "no_spread": 0.008},
        "model": {"n_train": 200, "cv_accuracy": 0.7931},
        "nearest_experiments": [
            {"report_id": "20140011099", "experiment_id": "BASS_T1", "oxygen_pct": 21.0, "distance": 0.02}
        ]
    }

    # Grounded text should pass
    valid_text = (
        "Under microgravity conditions, PMMA at 21.0% O2, 101.3 kPa, and 5.0 cm/s exhibits spread "
        "with probability 97.7%. Supported by 20140011099."
    )
    res_valid = auditor.audit_explanation(valid_text, pred_obj)
    assert res_valid["is_valid"] is True
    assert len(res_valid["hallucinated_numbers"]) == 0

    # Text containing hallucinated numbers (e.g. 99.4% or 42.0 cm/s) must be rejected
    invalid_text = (
        "Under microgravity conditions, PMMA at 21.0% O2 burns with a 99.4% spread rate "
        "and creates flame heights of 42.0 cm/s."
    )
    res_invalid = auditor.audit_explanation(invalid_text, pred_obj)
    assert res_invalid["is_valid"] is False
    assert any("99.4" in n or "42" in n for n in res_invalid["hallucinated_numbers"])


def test_auditor_unauthorized_citation_rejection(auditor):
    pred_obj = {
        "inputs": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
        "nearest_experiments": [
            {"report_id": "20140011099", "experiment_id": "BASS_T1"}
        ]
    }
    # Citing a fabricated report ID
    hallucinated_cite = "According to NASA/TM-2099-999999, flames spread continuously."
    res = auditor.audit_explanation(hallucinated_cite, pred_obj)
    assert res["is_valid"] is False
    assert len(res["invalid_citations"]) > 0


def test_composer_fallback_on_audit_failure(composer):
    pred_obj = {
        "inputs": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
        "in_training_range": True,
        "prediction": "spread",
        "probabilities": {"spread": 0.977, "marginal_spread": 0.015, "no_spread": 0.008},
        "model": {"n_train": 200, "cv_accuracy": 0.7931},
        "nearest_experiments": [
            {"report_id": "20140011099", "outcome": "spread", "oxygen_pct": 21.0}
        ]
    }
    # LLM gave an invalid explanation containing fabricated numbers
    bad_llm_text = "The spread velocity is 88.5 cm/s with 99.9% certainty according to NASA/TM-2099-999999."
    comp_res = composer.compose(prediction_obj=pred_obj, candidate_text=bad_llm_text)
    assert comp_res["source"] == "deterministic_fallback_audit_failed"
    # Fallback explanation must cite authorized experiment
    assert "20140011099" in comp_res["explanation"]


def test_orchestrator_in_domain_run(orchestrator):
    res = orchestrator.run({
        "oxygen_pct": 19.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA"
    })
    assert res["in_training_range"] is True
    assert res["prediction"] == "spread"
    assert res["audit_passed"] is True
    assert len(res["nearest_experiments"]) == 3
    assert OrchestratorState.FINALIZED.value in res["state_history"]
    assert "explanation" in res


def test_orchestrator_refusal_run(orchestrator):
    # 45% O2 triggers refusal
    res = orchestrator.run({
        "oxygen_pct": 45.0,
        "pressure_kpa": 101.3,
        "flow_cm_s": 5.0,
        "material": "PMMA"
    })
    assert res["in_training_range"] is False
    assert res["prediction"] is None
    assert res["probabilities"] is None
    assert OrchestratorState.REFUSED.value in res["state_history"]
    assert len(res["nearest_experiments"]) == 3  # Preserved per Section 7
