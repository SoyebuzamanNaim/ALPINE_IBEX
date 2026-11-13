"""Reproducible, nested report-holdout experiments; never changes production artifacts.

Run: .venv/bin/python -m src.compute.experiments --jobs 6
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import tempfile
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from joblib import Parallel, delayed, parallel_config
from sklearn.compose import ColumnTransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (ExtraTreesClassifier, GradientBoostingClassifier,
                              HistGradientBoostingClassifier, RandomForestClassifier)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (FunctionTransformer, OneHotEncoder,
                                   PolynomialFeatures, StandardScaler)
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from src.compute.model import FEATURE_COLS_CAT, FEATURE_COLS_NUM, load_dataset
from src.features.experiment_terms import physical_terms

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports" / "accuracy_experiments"
CLASSES = ["no_spread", "marginal_spread", "spread"]
BASE_FEATURES = FEATURE_COLS_NUM + FEATURE_COLS_CAT
CONTEXT_NUM = ["sample_thickness_mm"]
CONTEXT_CAT = ["sample_geometry", "flow_direction"]
SEED = 42


def candidate_grid():
    specs = [{"pool": "base", "kind": "majority", "variant": "raw", "params": {}}]
    weights = [None, {"no_spread": 0.5, "marginal_spread": 1.0, "spread": 1.0}, "balanced"]
    for variant, c, weight in itertools.product(["raw", "physical", "quadratic"],
                                               [0.01, 0.1, 1.0, 10.0], weights):
        specs.append(dict(pool="base", kind="logistic", variant=variant,
                          params=dict(C=c, class_weight=weight)))
    for variant, c, gamma, weight in itertools.product(["raw", "physical"],
                                                      [0.1, 1.0, 10.0],
                                                      ["scale", 0.1], [None, "balanced"]):
        specs.append(dict(pool="base", kind="svm", variant=variant,
                          params=dict(C=c, gamma=gamma, class_weight=weight)))
    for c, weight in itertools.product([0.01, 0.1, 1.0], [None, "balanced"]):
        specs.append(dict(pool="base", kind="svm", variant="raw",
                          params=dict(kernel="linear", C=c, class_weight=weight)))
    for kind, depth, leaf, weight in itertools.product(["forest", "extra_trees"],
                                                      [2, 5, None], [1, 4], [None, "balanced"]):
        specs.append(dict(pool="base", kind=kind, variant="raw",
                          params=dict(max_depth=depth, min_samples_leaf=leaf, class_weight=weight)))
    for depth, leaf in itertools.product([1, 2, 3], [3, 8]):
        specs.append(dict(pool="base", kind="boosting", variant="raw",
                          params=dict(max_depth=depth, min_samples_leaf=leaf)))
    for leaves, l2 in itertools.product([3, 7], [1.0, 10.0]):
        specs.append(dict(pool="base", kind="hist_boosting", variant="raw",
                          params=dict(max_leaf_nodes=leaves, l2_regularization=l2)))
    for k, weight in itertools.product([3, 7, 15], ["uniform", "distance"]):
        specs.append(dict(pool="base", kind="knn", variant="raw",
                          params=dict(n_neighbors=k, weights=weight)))
    for shrink in [0.1, 0.5, 0.9]:
        specs.append(dict(pool="base", kind="lda", variant="raw", params=dict(shrinkage=shrink)))
    for smooth in [1e-6, 0.01, 0.1]:
        specs.append(dict(pool="base", kind="gaussian_nb", variant="raw",
                          params=dict(var_smoothing=smooth)))
    specs.append(dict(pool="base", kind="production", variant="raw", params={}))
    for c, weight in itertools.product([0.01, 0.1, 1.0], [None, "balanced"]):
        specs.append(dict(pool="context", kind="logistic", variant="raw",
                          params=dict(C=c, class_weight=weight)))
    for kind, depth, leaf in itertools.product(["forest", "extra_trees"], [3, None], [1, 4]):
        specs.append(dict(pool="context", kind=kind, variant="raw",
                          params=dict(max_depth=depth, min_samples_leaf=leaf)))
    for depth in [1, 2, 3]:
        specs.append(dict(pool="context", kind="boosting", variant="raw", params=dict(max_depth=depth)))
    for c in [0.1, 1.0, 10.0]:
        specs.append(dict(pool="context", kind="svm", variant="raw", params=dict(C=c)))
    # The context pool receives the same majority control.
    specs.append(dict(pool="context", kind="majority", variant="raw", params={}))
    for index, spec in enumerate(specs):
        spec["id"] = f"exp_{index:03d}"
    return specs


def make_model(spec):
    variant = spec["variant"]
    numeric = []
    if variant == "physical":
        numeric.append(("derive", FunctionTransformer(physical_terms)))
    elif variant == "quadratic":
        numeric.append(("derive", PolynomialFeatures(2, include_bias=False)))
    numeric.append(("scale", StandardScaler()))
    transforms = [("num", Pipeline(numeric), FEATURE_COLS_NUM),
                  ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), FEATURE_COLS_CAT)]
    if spec["pool"] == "context":
        transforms.extend([
            ("context_num", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True,
                                                               keep_empty_features=True)),
                                      ("scale", StandardScaler())]), CONTEXT_NUM),
            ("context_cat", Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="unknown")),
                                      ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]),
             CONTEXT_CAT),
        ])
    kind, params = spec["kind"], spec["params"]
    if kind == "majority":
        classifier = DummyClassifier(strategy="most_frequent")
    elif kind == "logistic":
        classifier = LogisticRegression(max_iter=3000, random_state=SEED, **params)
    elif kind == "svm":
        classifier = SVC(probability=True, random_state=SEED, **params)
    elif kind in ("forest", "extra_trees"):
        cls = RandomForestClassifier if kind == "forest" else ExtraTreesClassifier
        classifier = cls(n_estimators=100, random_state=SEED, n_jobs=1, **params)
    elif kind == "boosting":
        classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05,
                                                 random_state=SEED, **params)
    elif kind == "production":
        classifier = GradientBoostingClassifier(n_estimators=85, max_depth=3, learning_rate=0.05,
                                                 min_samples_leaf=3, subsample=0.85, random_state=SEED)
    elif kind == "hist_boosting":
        classifier = HistGradientBoostingClassifier(max_iter=100, min_samples_leaf=5,
                                                     early_stopping=False, random_state=SEED, **params)
    elif kind == "knn":
        classifier = KNeighborsClassifier(**params)
    elif kind == "lda":
        classifier = LinearDiscriminantAnalysis(solver="lsqr", **params)
    elif kind == "gaussian_nb":
        classifier = GaussianNB(**params)
    else:
        raise ValueError(kind)
    return Pipeline([("prep", ColumnTransformer(transforms, remainder="drop")), ("clf", classifier)])


def metrics(y, predicted, groups):
    cm = confusion_matrix(y, predicted, labels=CLASSES)
    support = cm.sum(axis=1)
    recalls = np.divide(cm.diagonal(), support, out=np.zeros(3), where=support != 0)
    # Average recall only over classes present in this scoring subset.
    balanced = float(recalls[support > 0].mean())
    safe_calls = int(cm[:, 0].sum())
    return dict(accuracy=float(accuracy_score(y, predicted)), balanced_accuracy=balanced,
                macro_f1=float(f1_score(y, predicted, labels=CLASSES, average="macro", zero_division=0)),
                confusion_matrix=cm.tolist(), per_class_recall=dict(zip(CLASSES, recalls.tolist())),
                no_spread_precision=float(cm[0, 0] / safe_calls) if safe_calls else None,
                no_spread_calls=safe_calls, false_safe_calls=int(cm[1:, 0].sum()),
                report_macro_accuracy=float(np.mean([accuracy_score(y[groups == g], predicted[groups == g])
                                                       for g in np.unique(groups)])))


def evaluate_candidate(spec, X, y, groups, purge=False):
    """Cache single/pair report exclusions; each pair serves two nested inner folds."""
    reports = np.unique(groups)
    predictions = {}
    warning_messages = set()
    for size in (1, 2):
        for excluded in itertools.combinations(reports, size):
            test = np.isin(groups, excluded)
            train = ~test
            if purge:
                keys = pd.MultiIndex.from_frame(X[BASE_FEATURES])
                train &= ~keys.isin(keys[test])
            assert set(groups[train]).isdisjoint(groups[test])
            assert not np.any(train & test) and train.any()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model = make_model(spec).fit(X.loc[train], y[train])
                prediction = model.predict(X.loc[test])
            warning_messages.update(str(w.message) for w in caught)
            full = np.full(len(y), "", dtype=object)
            full[test] = prediction
            predictions[excluded] = full
    return dict(id=spec["id"], predictions=predictions, warnings=sorted(warning_messages))


def selection_key(score):
    return score["accuracy"], score["balanced_accuracy"], score["macro_f1"]


def select_for_outer(indices, results, y, groups, outer, eligible=None):
    train = groups != outer if eligible is None else eligible
    inner = []
    for index in indices:
        prediction = np.full(len(y), "", dtype=object)
        for inner_report in np.unique(groups[train]):
            held = tuple(sorted((outer, inner_report)))
            mask = (groups == inner_report) & train
            prediction[mask] = results[index]["predictions"][held][mask]
        assert np.all(prediction[train] != "")
        inner.append(metrics(y[train], prediction[train], groups[train]))
    winner = max(range(len(indices)), key=lambda i: selection_key(inner[i]))
    return indices[winner], inner[winner]


def nested_result(specs, results, y, groups, pool, condition_keys=None):
    indices = [i for i, spec in enumerate(specs) if spec["pool"] == pool]
    predicted = np.full(len(y), "", dtype=object)
    folds = []
    for outer in np.unique(groups):
        test = groups == outer
        train = ~test
        if condition_keys is not None:
            train &= ~condition_keys.isin(condition_keys[test])
        winner, score = select_for_outer(indices, results, y, groups, outer, train)
        predicted[test] = results[winner]["predictions"][(outer,)][test]
        folds.append(dict(report_id=str(outer), n_train=int(train.sum()), n_test=int(test.sum()),
                          selected_id=specs[winner]["id"], inner_metrics=score,
                          outer_metrics=metrics(y[test], predicted[test], groups[test])))
    assert np.all(predicted != "")
    return dict(metrics=metrics(y, predicted, groups), folds=folds), predicted


def bootstrap_reports(y, predicted, control, groups):
    rng = np.random.default_rng(SEED)
    reports = np.unique(groups)
    indices = [np.flatnonzero(groups == group) for group in reports]
    acc, delta = [], []
    for _ in range(5000):
        sample = np.concatenate([indices[i] for i in rng.integers(0, len(reports), len(reports))])
        a = np.mean(y[sample] == predicted[sample])
        acc.append(a)
        delta.append(a - np.mean(y[sample] == control[sample]))
    return dict(accuracy_95_percentile=np.quantile(acc, [0.025, 0.975]).tolist(),
                improvement_over_majority_95_percentile=np.quantile(delta, [0.025, 0.975]).tolist(),
                caveat="Descriptive report bootstrap; only seven reports; not independent external validation.")


def write_report(payload, specs, output=OUTPUT):
    """Keep the human-readable conclusions tied to the saved machine-readable scores."""
    candidates = payload["candidates"]
    base, context = payload["nested"]["base"], payload["nested"]["context"]
    selected = base["full_data_selection_metrics_tuning_only"]
    majority = payload["controls"]["majority"]
    production = payload["controls"]["production"]
    n_groups = len(base["folds"])
    supports = np.asarray(selected["confusion_matrix"]).sum(axis=1)
    fit_count = len(specs) * (n_groups + n_groups * (n_groups - 1) // 2) * 2
    rows = []
    for label, score in [("Previous gradient-boosting reference (fixed)", production),
                         ("Training-fold majority", majority),
                         ("Best four-input candidate (selection score only)", selected),
                         ("Nested selection, four inputs", base["metrics"]),
                         ("Nested selection, seven inputs", context["metrics"])]:
        precision = score["no_spread_precision"]
        precision_text = "N/A" if precision is None else f"{precision:.1%}"
        rows.append(f"| {label} | {score['accuracy']:.1%} | {score['balanced_accuracy']:.1%} | "
                    f"{score['macro_f1']:.4f} | {precision_text} | {score['false_safe_calls']} |")
    family_rows = []
    for pool, kind in sorted({(s["pool"], s["kind"]) for s in specs}):
        winner = max((s for s in candidates if s["pool"] == pool and s["kind"] == kind), key=selection_key)
        family_rows.append(f"| {pool} | {kind} | {winner['id']} | {winner['accuracy']:.1%} | "
                           f"{winner['balanced_accuracy']:.1%} |")
    fold_rows = []
    for fold in base["folds"]:
        spec = next(s for s in specs if s["id"] == fold["selected_id"])
        fold_rows.append(f"| {fold['report_id']} | {fold['n_train']} | {fold['n_test']} | "
                         f"{fold['selected_id']} ({spec['kind']}) | {fold['inner_metrics']['accuracy']:.1%} | "
                         f"{fold['outer_metrics']['accuracy']:.1%} |")
    report = f"""# Accuracy experiments — {payload['run_at'][:10]} (UTC)

Ran **{len(specs)} frozen configurations** on the unchanged **{payload['n_rows']}-row,
three-class dataset**, with {n_groups} report groups. Each candidate has {n_groups} outer fits and
{n_groups * (n_groups - 1) // 2} reusable pair-exclusion fits for nested selection. Repeating the complete procedure
with exact-condition purging gives **{fit_count:,} validation fits** in total.

The highest ordinary report-grouped accuracy is **{selected['accuracy']:.1%}**, versus
**{production['accuracy']:.1%}** for the previous gradient-boosting reference and **{majority['accuracy']:.1%}** for the majority
control. It is a **selection score**, chosen from the grid; it is not an independent estimate
of the selected model's accuracy. The nested procedure's accuracy is **{base['metrics']['accuracy']:.1%}**.
**This experiment runner does not promote models or change the serving release.**

## Results

| Procedure | Accuracy | Balanced accuracy (3 classes) | Macro-F1 | no_spread precision | False-safe calls |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

All {payload['n_rows']} rows, including {supports[1]} marginal_spread examples, count in these scores. The three-class
majority balanced-accuracy floor is 33.3%. Older binary evaluations in
REBUILT_MODEL_EVALUATION.md dropped the marginal class and cannot be compared directly.
"False-safe" counts true spread or marginal_spread observations predicted as no_spread.

## Best candidate and why it is still experimental

The four-input candidate is **{selected['id']}**, a `{selected['kind']}` with
`{selected['params']}` and fold-fitted scaling/category encoding. Its ordinary grouped
confusion matrix, rows=true and columns=predicted in order no_spread, marginal_spread, spread:

```text
{json.dumps(selected['confusion_matrix'])}
```

It detects only {selected['confusion_matrix'][0][0]}/{supports[0]} no_spread cases and
{selected['confusion_matrix'][1][1]}/{supports[1]} marginal cases. Its no_spread precision rests on
{selected['no_spread_calls']} predictions. Probabilities have not been validated or calibrated
across reports. The seven-input candidate requires sample thickness, geometry and flow
direction, which the current API does not collect.

## Nested evaluation exposes a transfer failure

Every outer report is excluded from both tuning and fitting. Inner selection ranks candidates
by pooled accuracy, then balanced accuracy, then macro-F1. Each outer fold uses its own selected
candidate. This evaluates the entire selection procedure, rather than quoting its best score.

| Excluded report | Train rows | Test rows | Inner-selected candidate | Inner accuracy | Outer accuracy |
|---|---:|---:|---|---:|---:|
{chr(10).join(fold_rows)}

BASS-II supplies 158/200 rows. Excluding it leaves only 42 training rows from six different
reports. The inner-selected model transfers poorly to BASS-II; its failure remains included
in the headline nested result. Choosing another model after seeing that failure would use
outer evaluation results for tuning. The frozen search was not changed to repair this score.

The descriptive report-bootstrap 95% interval for nested four-input accuracy is
[{base['uncertainty']['accuracy_95_percentile'][0]:.1%},
{base['uncertainty']['accuracy_95_percentile'][1]:.1%}]. With only seven highly unequal reports,
this is not strong uncertainty quantification or evidence of operational safety.

## Leakage checks and sensitivity

- Outcomes, observation text, failure mode, burn duration/rate, IDs, report identity and
  citations are excluded from model features. All classes and observations are retained.
- Preprocessing fits inside every training fold. Whole reports, including sibling sweep
  observations, stay together. The two-report exclusion cache is equivalent to the nested
  inner folds and never fits on the outer report.
- There is one cross-report exact four-input condition overlap (Saffire II/IV). Purging such
  conditions from training and rerunning the entire nested search yields
  **{payload['purged_nested']['base']['metrics']['accuracy']:.1%}** for four inputs and
  **{payload['purged_nested']['context']['metrics']['accuracy']:.1%}** for seven inputs.
  It does not repair the transfer failure.
- No synthetic rows, relabeling, class merging, favorable row splits, seed selection, fitted
  NASA boundary features, or exclusion of bad folds was used. All random seeds are 42.
- The dataset was already inspected in previous work. Nested CV does not erase that exposure.
  An independent report with source-supported outcomes is required to confirm an improvement.

## Best ordinary grouped score per family (tuning evidence only)

| Input pool | Family | Candidate | Accuracy | Balanced accuracy |
|---|---|---|---:|---:|
{chr(10).join(family_rows)}

## Artifacts and reproduction

```bash
.venv/bin/python -m src.compute.experiments --jobs 6
.venv/bin/pytest -q tests/test_accuracy_experiments.py tests/test_models.py tests/test_model_governance.py
.venv/bin/python scripts/verify_artifacts.py
```

`grid.json` records every configuration; `candidate_scores.csv` includes unsuccessful models;
`outer_predictions.csv` records all outer answers, including the selected candidates' ordinary
grouped predictions; `results.json` includes nested choices, confusion matrices, warnings,
versions and hashes. `PROTOCOL.md` was written before the experiment.

Saved research models: `{base['artifact']}` and
`{context['artifact']}`, with separate metadata files in the same immutable bundle.
The complete bundle is published only after every phase succeeds; `latest.json` points to
the latest completed run. Interrupted reruns leave previous completed runs untouched.
Serving promotion is separate from experiments. The base candidate uses four fields;
the context candidate needs seven. No global optimum or independently validated gain is claimed.

Method reference: [scikit-learn nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

Dataset SHA-256: `{payload['dataset_sha256']}`.
"""
    (output / "SUMMARY.md").write_text(report)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    df, dataset_hash = load_dataset()
    runs = OUTPUT / "runs"
    runs.mkdir(exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = runs / run_id
    with tempfile.TemporaryDirectory(prefix=".pending-", dir=runs) as temporary:
        output = Path(temporary) / "bundle"
        output.mkdir()
        (output / "PROTOCOL.md").write_bytes((OUTPUT / "PROTOCOL.md").read_bytes())
        run_experiments(df, dataset_hash, args.jobs, output, destination)
        output.rename(destination)
    manifest = OUTPUT / f".latest-{run_id}.json"
    manifest.write_text(json.dumps({"run": str(destination.relative_to(ROOT)),
                                    "results": str((destination / "results.json").relative_to(ROOT))}, indent=2) + "\n")
    manifest.replace(OUTPUT / "latest.json")
    print(f"Published complete run: {destination}", flush=True)


def run_experiments(df, dataset_hash, jobs, output, destination):
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    feature_hash = hashlib.sha256((ROOT / "src/features/experiment_terms.py").read_bytes()).hexdigest()
    X = df[BASE_FEATURES + CONTEXT_NUM + CONTEXT_CAT].copy()
    X[CONTEXT_CAT] = X[CONTEXT_CAT].fillna(np.nan)
    y, groups = df.outcome.to_numpy(), df.report_id.astype(str).to_numpy()
    specs = candidate_grid()
    grid_text = json.dumps(specs, indent=2, sort_keys=True)
    (output / "grid.json").write_text(grid_text + "\n")
    print(f"Frozen grid: {len(specs)} candidates, {len(np.unique(groups))} reports, {len(y)} rows", flush=True)
    with parallel_config(backend="loky", inner_max_num_threads=1), threadpool_limits(limits=1):
        results = Parallel(n_jobs=jobs, verbose=10)(
            delayed(evaluate_candidate)(spec, X, y, groups) for spec in specs)
    table, full_predictions = [], []
    for spec, result in zip(specs, results):
        predicted = np.full(len(y), "", dtype=object)
        for group in np.unique(groups):
            mask = groups == group
            predicted[mask] = result["predictions"][(group,)][mask]
        full_predictions.append(predicted)
        table.append(dict(id=spec["id"], pool=spec["pool"], kind=spec["kind"], variant=spec["variant"],
                          params=json.dumps(spec["params"], sort_keys=True),
                          **metrics(y, predicted, groups), warnings=result["warnings"]))
    table_frame = pd.DataFrame(table)
    table_frame.to_csv(output / "candidate_scores.csv", index=False)
    payload = dict(dataset_sha256=dataset_hash, n_rows=len(y), classes=CLASSES,
                   source_sha256=source_hash,
                   feature_source_sha256=feature_hash,
                   grid_sha256=hashlib.sha256(grid_text.encode()).hexdigest(),
                   protocol_sha256=hashlib.sha256((output / "PROTOCOL.md").read_bytes()).hexdigest(),
                   run_at=datetime.now(timezone.utc).isoformat(), seed=SEED,
                   versions=dict(python=platform.python_version(), sklearn=sklearn.__version__,
                                 numpy=np.__version__, pandas=pd.__version__),
                   candidate_count=len(specs), nested={}, candidates=table)
    majority_index = next(i for i,s in enumerate(specs) if s["pool"] == "base" and s["kind"] == "majority")
    production_index = next(i for i,s in enumerate(specs) if s["kind"] == "production")
    payload["controls"] = {"majority": table[majority_index], "production": table[production_index]}
    output_predictions = df[["experiment_id", "report_id", "outcome"]].copy()
    output_predictions["majority"] = full_predictions[majority_index]
    output_predictions["production"] = full_predictions[production_index]
    for pool in ("base", "context"):
        summary, predicted = nested_result(specs, results, y, groups, pool)
        summary["uncertainty"] = bootstrap_reports(y, predicted, full_predictions[majority_index], groups)
        output_predictions[f"nested_{pool}"] = predicted
        indices = [i for i,s in enumerate(specs) if s["pool"] == pool]
        winner = max(indices, key=lambda i: selection_key(table[i]))
        summary["full_data_selected_id"] = specs[winner]["id"]
        summary["full_data_selection_metrics_tuning_only"] = table[winner]
        output_predictions[f"selected_{pool}_ordinary_grouped"] = full_predictions[winner]
        # Research artifacts have separate names and never open the public inference gate.
        with threadpool_limits(limits=1):
            fitted = make_model(specs[winner]).fit(X, y)
        artifact = output / f"accuracy_candidate_{pool}.joblib"
        joblib.dump(fitted, artifact)
        summary["artifact"] = str((destination / artifact.name).relative_to(ROOT))
        summary["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        summary["required_features"] = BASE_FEATURES + (CONTEXT_NUM + CONTEXT_CAT if pool == "context" else [])
        summary["public_inference_approved"] = False
        payload["nested"][pool] = summary
        print(f"Nested {pool}: {summary['metrics']}; final selection {specs[winner]['id']}", flush=True)
    # Freeze and rerun the entire same selection procedure with overlap purging.
    print("Running exact-condition purge sensitivity check...", flush=True)
    with parallel_config(backend="loky", inner_max_num_threads=1), threadpool_limits(limits=1):
        purged = Parallel(n_jobs=jobs, verbose=10)(
            delayed(evaluate_candidate)(spec, X, y, groups, True) for spec in specs)
    payload["purged_nested"] = {}
    for pool in ("base", "context"):
        summary, predicted = nested_result(specs, purged, y, groups, pool,
                                           pd.MultiIndex.from_frame(X[BASE_FEATURES]))
        payload["purged_nested"][pool] = summary
        output_predictions[f"purged_nested_{pool}"] = predicted
        print(f"Purged nested {pool}: {summary['metrics']}", flush=True)
    output_predictions.to_csv(output / "outer_predictions.csv", index=False)
    (output / "results.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    for pool, summary in payload["nested"].items():
        metadata = dict(dataset_sha256=dataset_hash, selection_protocol="nested leave-one-report-out",
                        validation_status="research_only; no validated improvement", **summary)
        (output / f"accuracy_candidate_{pool}_meta.json").write_text(
            json.dumps(metadata, indent=2, allow_nan=False) + "\n")
    write_report(payload, specs, output)
    if (source_hash != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or feature_hash != hashlib.sha256((ROOT / "src/features/experiment_terms.py").read_bytes()).hexdigest()):
        raise RuntimeError("Source changed during the experiment; the previous complete bundle is preserved.")


if __name__ == "__main__":
    main()
