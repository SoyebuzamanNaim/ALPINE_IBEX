"""Agent Orchestrator for FLARE-X.

Executes a formal finite-state machine (FSM) coordinating the specialized agents:
ScenarioInterpreter -> EnvelopeGuard -> ModelRouter -> EvidenceRetriever ->
ExplanationComposer -> EvidenceAuditor.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from src.agents.auditor import EvidenceAuditor
from src.agents.composer import ExplanationComposer
from src.agents.interpreter import ScenarioInterpreter
from src.agents.model_router import ModelRouter
from src.agents.retriever import EvidenceRetrieverAgent
from src.envelope.guard import EnvelopeGuard

ROOT = Path(__file__).resolve().parents[2]


class OrchestratorState(str, Enum):
    INIT = "INIT"
    INTERPRETING = "INTERPRETING"
    ENVELOPE_CHECK = "ENVELOPE_CHECK"
    PREDICTING = "PREDICTING"
    RETRIEVING = "RETRIEVING"
    COMPOSING = "COMPOSING"
    AUDITING = "AUDITING"
    REFUSED = "REFUSED"
    FAILED_AMBIGUOUS = "FAILED_AMBIGUOUS"
    FINALIZED = "FINALIZED"


class AgentOrchestrator:
    """Finite-state machine orchestrating all specialized flammability agents."""

    def __init__(
        self,
        meta_path: Path = ROOT / "models" / "model_meta.json",
        data_path: Path = ROOT / "cache" / "experiments.parquet",
    ):
        self.interpreter = ScenarioInterpreter()
        self.guard = EnvelopeGuard(meta_path=meta_path, data_path=data_path)
        self.router = ModelRouter(meta_path=meta_path)
        self.retriever = EvidenceRetrieverAgent(data_path=data_path)
        self.auditor = EvidenceAuditor()
        self.composer = ExplanationComposer(auditor=self.auditor)

    def run(
        self,
        user_input: str | dict[str, Any],
        candidate_explanation: str | None = None,
    ) -> dict[str, Any]:
        """Execute the end-to-end multi-agent state machine."""
        state_history = [OrchestratorState.INIT]

        # 1. State: INTERPRETING
        state_history.append(OrchestratorState.INTERPRETING)
        interp_res = self.interpreter.parse(user_input)

        if not interp_res["is_valid"]:
            state_history.append(OrchestratorState.FAILED_AMBIGUOUS)
            return {
                "status": "failed_ambiguous",
                "state_history": [s.value for s in state_history],
                "ambiguities": interp_res["ambiguities"],
                "inputs": None,
                "prediction": None,
                "probabilities": None,
                "explanation": (
                    "Could not interpret operational scenario unambiguously: "
                    + "; ".join(interp_res["ambiguities"])
                ),
            }

        scenario = interp_res["parsed_scenario"]
        oxygen_pct = scenario["oxygen_pct"]
        pressure_kpa = scenario["pressure_kpa"]
        flow_cm_s = scenario["flow_cm_s"]
        material = scenario["material"]

        # 2. State: ENVELOPE_CHECK
        state_history.append(OrchestratorState.ENVELOPE_CHECK)
        env_res = self.guard.check(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
        )

        model_meta = self.router.get_model_metadata()

        # Handle Out of Envelope Refusal
        if not env_res["in_training_range"]:
            state_history.append(OrchestratorState.REFUSED)
            refusal_payload = {
                "inputs": scenario,
                "in_training_range": False,
                "status": env_res["status"],
                "out_of_range_reasons": env_res["out_of_range_reasons"],
                "prediction": None,
                "probabilities": None,
                "model": model_meta,
                "nearest_experiments": env_res["nearest_experiments"],
                "explanation": env_res["explanation"],
                "state_history": [s.value for s in state_history],
            }
            state_history.append(OrchestratorState.FINALIZED)
            refusal_payload["state_history"] = [s.value for s in state_history]
            return refusal_payload

        # 3. State: PREDICTING
        state_history.append(OrchestratorState.PREDICTING)
        pred_res = self.router.predict(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
        )

        # 4. State: RETRIEVING
        state_history.append(OrchestratorState.RETRIEVING)
        ret_res = self.retriever.retrieve(
            oxygen_pct=oxygen_pct,
            pressure_kpa=pressure_kpa,
            flow_cm_s=flow_cm_s,
            material=material,
            k=3,
        )

        # Assemble draft prediction payload
        prediction_payload = {
            "inputs": scenario,
            "in_training_range": True,
            "status": env_res["status"],
            "out_of_range_reasons": [],
            "prediction": pred_res["prediction"],
            "probabilities": pred_res["probabilities"],
            "model": model_meta,
            "nearest_experiments": ret_res["nearest_experiments"],
            "supporting_passages": ret_res.get("supporting_passages", []),
            "sparse_region_warning": env_res.get("sparse_region_warning", False),
            "knn_mean_distance": env_res.get("knn_mean_distance"),
            "warning_message": env_res.get("warning_message"),
        }

        # 5. State: COMPOSING
        state_history.append(OrchestratorState.COMPOSING)
        comp_res = self.composer.compose(
            prediction_obj=prediction_payload,
            candidate_text=candidate_explanation,
        )
        prediction_payload["explanation"] = comp_res["explanation"]
        prediction_payload["explanation_source"] = comp_res["source"]

        # 6. State: AUDITING
        state_history.append(OrchestratorState.AUDITING)
        audit_res = self.auditor.audit_prediction_payload(prediction_payload)
        prediction_payload["audit_passed"] = audit_res["passed"]
        if not audit_res["passed"]:
            prediction_payload["audit_errors"] = audit_res["errors"]

        state_history.append(OrchestratorState.FINALIZED)
        prediction_payload["state_history"] = [s.value for s in state_history]

        return prediction_payload
