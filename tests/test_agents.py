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
    assert meta["n_train"] == 145
    assert meta["cv_accuracy"] > 0.70

    res = router.predict(21.0, 101.3, 5.0, "PMMA")
    assert res["prediction"] in ["spread", "marginal_spread", "no_spread"]
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=1e-3)


def test_auditor_numerical_rejection(auditor):
    pred_obj = {
        "inputs": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
        "in_training_range": True,
        "prediction": "spread",
        "probabilities": {"spread": 0.977, "marginal_spread": 0.015, "no_spread": 0.008},
        "model": {"n_train": 145, "cv_accuracy": 0.7931},
        "nearest_experiments": [
            {"report_id": "NASA/TM-2016-219077", "experiment_id": "EXP_BASS_001", "oxygen_pct": 21.0, "distance": 0.02}
        ]
    }

    # Grounded text should pass
    valid_text = (
        "Under microgravity conditions, PMMA at 21.0% O2, 101.3 kPa, and 5.0 cm/s exhibits spread "
        "with probability 97.7%. Supported by NASA/TM-2016-219077."
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
            {"report_id": "NASA/TM-2016-219077", "experiment_id": "EXP_BASS_001"}
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
        "model": {"n_train": 145, "cv_accuracy": 0.7931},
        "nearest_experiments": [
            {"report_id": "NASA/TM-2016-219077", "outcome": "spread", "oxygen_pct": 21.0}
        ]
    }
    # LLM gave an invalid explanation containing fabricated numbers
    bad_llm_text = "The spread velocity is 88.5 cm/s with 99.9% certainty according to NASA/TM-2099-999999."
    comp_res = composer.compose(prediction_obj=pred_obj, candidate_text=bad_llm_text)
    assert comp_res["source"] == "deterministic_fallback_audit_failed"
    # Fallback explanation must cite authorized experiment
    assert "NASA/TM-2016-219077" in comp_res["explanation"]


def test_orchestrator_in_domain_run(orchestrator):
    res = orchestrator.run({
        "oxygen_pct": 21.0,
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
