"""The static shell must not advertise an obsolete or unavailable model result."""

from pathlib import Path


APP_HTML = Path(__file__).resolve().parents[1] / "app" / "index.html"
APP_JS = Path(__file__).resolve().parents[1] / "app" / "app.js"


def test_static_shell_does_not_present_old_model_results():
    page = APP_HTML.read_text(encoding="utf-8")
    for obsolete in ("83.45%", "51.72%", "72.41%", "145", "Delrin"):
        assert obsolete not in page
    assert "model inference withheld" in page.lower()
    assert 'id="val-prob-spread">N/A<' in page


def test_static_shell_does_not_claim_unverified_coverage_or_guard_state():
    page = APP_HTML.read_text(encoding="utf-8")
    for unsupported in (
        "LOC min", "Near-Extinction LOC", "Near-LOC Quenching Boundary",
        "Zero-Extrapolation Guard Active", "75.0%", "428cec44",
        "SPACEFLIGHT OBS", "spaceflight observations", "flight observations",
    ):
        assert unsupported not in page


def test_runtime_copy_avoids_unproven_model_and_evidence_claims():
    source = APP_JS.read_text(encoding="utf-8")
    for unsupported in (
        "Zero NASA Flight Data in Regime", "Combustion will exhibit unsteady",
        "Grouped validation did not beat the majority baseline",
    ):
        assert unsupported not in source


def test_sweep_copy_does_not_call_model_transition_a_safety_limit():
    source = APP_JS.read_text(encoding="utf-8")
    for unsupported in (
        "Nominal Operating Margin", "Extinction / Quenched",
        "Critical Near-Boundary Margin", "16.5% O₂, 101.3 kPa, 4.0 cm/s",
        "(LOC Boundary)",
    ):
        assert unsupported not in source


def test_pitch_uses_evidence_and_labels_templates_and_dataset_scope():
    page = APP_HTML.read_text(encoding="utf-8")
    overview = (APP_HTML.parents[1] / "project-page" / "index.html").read_text(encoding="utf-8")
    assert 'id="chip-cv-acc"' not in page
    assert 'id="chip-base-acc"' not in page
    assert "84.0%" not in overview
    assert "similarity ranking" in page.lower()
    assert "template summary" in page.lower()
    assert "Team-Proposed Experiments" in page
    assert "current FLARE-X dataset" in page
    assert page.index('src="config.js"') < page.index('src="app.js"')
