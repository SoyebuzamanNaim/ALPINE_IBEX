"""Checks for leakage and honest scoring in the experiment runner."""
import numpy as np
import pandas as pd
import joblib

from src.compute.experiments import (
    BASE_FEATURES,
    candidate_grid,
    evaluate_candidate,
    make_model,
    metrics,
    select_for_outer,
)


def test_base_pipeline_ignores_outcome_text_and_context():
    spec = next(s for s in candidate_grid() if s["kind"] == "logistic")
    x = pd.DataFrame({
        "oxygen_pct": [14., 16., 20., 22.], "pressure_kpa": [100.] * 4,
        "flow_cm_s": [1., 2., 4., 8.], "material": ["PMMA"] * 4,
        "outcome_raw": ["failed", "failed", "burned", "burned"],
        "sample_thickness_mm": [1., 2., 3., 4.],
    })
    y = np.array(["no_spread", "no_spread", "spread", "spread"])
    model = make_model(spec).fit(x, y)
    before = model.predict_proba(x)
    x["outcome_raw"] = "leaked answer"
    x["sample_thickness_mm"] = 999.
    np.testing.assert_array_equal(before, model.predict_proba(x))
    selected = [column for name, _, columns in model["prep"].transformers_
                if name != "remainder" for column in columns]
    assert selected == BASE_FEATURES


def test_outer_selection_cannot_use_outer_labels():
    # Candidate 0 is perfect on inner reports, candidate 1 is wrong.
    # Changing the excluded report's answers must not change selection or its score.
    groups = np.array(["a", "a", "b", "b", "c", "c"])
    y = np.array(["spread", "no_spread"] * 3)
    results = []
    for good in (True, False):
        cache = {}
        for inner_report in ("b", "c"):
            prediction = np.full(6, "", dtype=object)
            mask = groups == inner_report
            prediction[mask] = y[mask] if good else y[mask][::-1]
            cache[("a", inner_report)] = prediction
        results.append({"predictions": cache})
    winner, score = select_for_outer([0, 1], results, y, groups, "a")
    y[groups == "a"] = "marginal_spread"
    other_winner, other_score = select_for_outer([0, 1], results, y, groups, "a")
    assert winner == other_winner == 0
    assert score == other_score
    assert score["accuracy"] == 1.


def test_outer_and_inner_fits_exclude_complete_reports(monkeypatch):
    # Repeated rows within each report stay together in all single/pair exclusions.
    groups = np.array(["a", "a", "b", "b", "c", "c"])
    x = pd.DataFrame({"oxygen_pct": [14., 15., 16., 17., 18., 19.],
                      "pressure_kpa": [100.] * 6, "flow_cm_s": [1.] * 6,
                      "material": ["PMMA"] * 6})
    y = np.array(["no_spread", "spread"] * 3)
    fits = []

    class Spy:
        def fit(self, train, labels):
            self.training_reports = set(groups[train.index])
            fits.append(self.training_reports)
            assert all(sum(groups[train.index] == g) == 2 for g in self.training_reports)
            return self

        def predict(self, test):
            assert self.training_reports.isdisjoint(groups[test.index])
            return np.full(len(test), "spread")

    monkeypatch.setattr("src.compute.experiments.make_model", lambda _: Spy())
    result = evaluate_candidate(candidate_grid()[0], x, y, groups)
    assert len(fits) == 6  # three outer exclusions and three distinct inner pairs
    assert len(result["predictions"]) == 6


def test_metrics_keep_rare_class_and_count_false_safe_calls():
    y = np.array(["no_spread", "marginal_spread", "spread", "spread"])
    predicted = np.array(["no_spread", "spread", "no_spread", "spread"])
    score = metrics(y, predicted, np.array(["a", "a", "b", "b"]))
    assert score["accuracy"] == 0.5
    assert score["balanced_accuracy"] == 0.5
    assert score["per_class_recall"]["marginal_spread"] == 0.
    assert score["false_safe_calls"] == 1
    assert score["no_spread_precision"] == 0.5


def test_purging_removes_overlapping_conditions_from_training(monkeypatch):
    groups = np.repeat(["a", "b", "c", "d"], 2)
    x = pd.DataFrame({"oxygen_pct": [14., 15., 14., 17., 18., 19., 20., 21.],
                      "pressure_kpa": [100.] * 8, "flow_cm_s": [1.] * 8,
                      "material": ["PMMA"] * 8})
    y = np.array(["no_spread", "spread"] * 4)
    sizes = []

    class Spy:
        def fit(self, train, labels):
            self.keys = set(pd.MultiIndex.from_frame(train[BASE_FEATURES]))
            sizes.append(len(train))
            return self

        def predict(self, test):
            assert self.keys.isdisjoint(pd.MultiIndex.from_frame(test[BASE_FEATURES]))
            return np.full(len(test), "spread")

    monkeypatch.setattr("src.compute.experiments.make_model", lambda _: Spy())
    evaluate_candidate(candidate_grid()[0], x, y, groups, purge=True)
    assert sizes[0] == 5  # excluding report a also purges the matching condition in b


def test_physical_pipeline_serializes_with_importable_transform(tmp_path):
    x = pd.DataFrame({"oxygen_pct": [14., 16., 20., 22.], "pressure_kpa": [100.] * 4,
                      "flow_cm_s": [0., 2., 4., 8.], "material": ["PMMA"] * 4})
    y = np.array(["no_spread", "no_spread", "spread", "spread"])
    spec = next(s for s in candidate_grid() if s["kind"] == "logistic" and s["variant"] == "physical")
    model = make_model(spec).fit(x, y)
    transform = model["prep"].named_transformers_["num"]["derive"].func
    assert transform.__module__ == "src.features.experiment_terms"
    path = tmp_path / "physical.joblib"
    joblib.dump(model, path)
    np.testing.assert_array_equal(model.predict(x), joblib.load(path).predict(x))


def test_purged_outer_selection_ignores_labels_of_removed_conditions():
    groups = np.array(["a", "a", "b", "b", "c", "c"])
    y = np.array(["spread", "spread", "no_spread", "spread", "spread", "spread"])
    eligible = np.array([False, False, False, True, True, True])
    results = []
    for good in (True, False):
        cache = {}
        for inner in ["b", "c"]:
            prediction = np.full(6, "", dtype=object)
            prediction[groups == inner] = "spread" if good else "no_spread"
            cache[("a", inner)] = prediction
        results.append({"predictions": cache})
    first = select_for_outer([0, 1], results, y, groups, "a", eligible)
    y[2] = "marginal_spread"  # this row was purged for matching outer report a
    second = select_for_outer([0, 1], results, y, groups, "a", eligible)
    assert first == second
    assert first[0] == 0 and first[1]["accuracy"] == 1.


def test_failed_experiment_does_not_replace_last_completed_bundle(tmp_path, monkeypatch):
    import sys
    import src.compute.experiments as experiments
    output = tmp_path / "experiments"
    output.mkdir()
    (output / "PROTOCOL.md").write_text("frozen")
    manifest = output / "latest.json"
    manifest.write_text('{"run": "previous-success"}')
    previous = manifest.read_bytes()

    def fail(df, sha, jobs, staging, destination):
        (staging / "accuracy_candidate_base.joblib").write_bytes(b"unfinished model")
        raise RuntimeError("purge failed")

    monkeypatch.setattr(experiments, "OUTPUT", output)
    monkeypatch.setattr(experiments, "load_dataset", lambda: (pd.DataFrame(), "hash"))
    monkeypatch.setattr(experiments, "run_experiments", fail)
    monkeypatch.setattr(sys, "argv", ["experiments"])
    import pytest
    with pytest.raises(RuntimeError, match="purge failed"):
        experiments.main()
    assert manifest.read_bytes() == previous
    assert list((output / "runs").iterdir()) == []
