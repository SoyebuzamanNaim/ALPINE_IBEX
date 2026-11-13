"""Model training, evaluation, and serialization entry point for FLARE-X.

Authoritative path: src/compute/model.py.

Trains:
1. Naive Majority-Class Baseline (DummyClassifier)
2. Logistic Regression Baseline
3. Random Forest Classifier
4. Gradient Boosting Classifier (previous serving baseline)
5. Linear SVM (serving research model)

Evaluates using:
- Report-grouped CV: LeaveOneGroupOut(group=report_id)
- Secondary, stricter: LeaveOneGroupOut(group=investigation)
- Optimistic CV: StratifiedKFold, capped by the least-supported class
Outputs:
- models/flame_spread_gb.joblib
- models/model_meta.json
- models/metrics.json
- reports/BASELINE_RESULTS.md
- docs/MODEL_CARDS.md
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "cache" / "experiments.parquet"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

RANDOM_SEED = 42
SERVING_MODEL = "linear_svm"
FEATURE_COLS_NUM = ["oxygen_pct", "pressure_kpa", "flow_cm_s"]
FEATURE_COLS_CAT = ["material"]
TARGET_COL = "outcome"
GROUP_COL = "investigation"


def load_dataset() -> tuple[pd.DataFrame, str]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Run src.ingestion.build_table first.")
    df = pd.read_parquet(DATA_FILE)
    sha256 = hashlib.sha256(DATA_FILE.read_bytes()).hexdigest()
    return df, sha256


def get_preprocessor() -> ColumnTransformer:
    """Construct zero-leakage preprocessor.
    
    OneHotEncoder does not receive precomputed global categories from full df.
    It fits dynamically on training splits during CV and gracefully handles
    unseen categories via handle_unknown='ignore'.
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURE_COLS_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), FEATURE_COLS_CAT),
        ],
        remainder="drop",
    )


def make_serving_model(seed: int = RANDOM_SEED) -> Pipeline:
    """The frozen four-input experiment winner; probabilities remain exploratory."""
    return Pipeline([
        ("prep", get_preprocessor()),
        ("clf", SVC(kernel="linear", C=1.0, probability=True, random_state=seed)),
    ])


def compute_cv_metrics(
    model_factory,
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series | None,
    cv_splitter,
    classes: list[str],
) -> dict[str, Any]:
    """Evaluate a model using cross-validation and compute out-of-fold metrics."""
    oof_preds = []
    oof_trues = []
    fold_accuracies = []
    fold_sizes = []

    splits = cv_splitter.split(X, y, groups=groups) if groups is not None else cv_splitter.split(X, y)

    for train_idx, val_idx in splits:
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = model_factory()
        model.fit(X_train, y_train)
        val_pred = model.predict(X_val)

        oof_preds.extend(val_pred)
        oof_trues.extend(y_val)
        fold_accuracies.append(accuracy_score(y_val, val_pred))
        fold_sizes.append(int(len(val_idx)))

    oof_preds_arr = np.array(oof_preds)
    oof_trues_arr = np.array(oof_trues)

    acc = accuracy_score(oof_trues_arr, oof_preds_arr)
    bal_acc = balanced_accuracy_score(oof_trues_arr, oof_preds_arr)
    macro_f1 = f1_score(oof_trues_arr, oof_preds_arr, average="macro", zero_division=0)
    cm = confusion_matrix(oof_trues_arr, oof_preds_arr, labels=classes).tolist()

    report_dict = classification_report(
        oof_trues_arr, oof_preds_arr, labels=classes, output_dict=True, zero_division=0
    )

    per_class_recall = {cls: report_dict[cls]["recall"] for cls in classes}

    return {
        "accuracy": round(float(acc), 4),
        "balanced_accuracy": round(float(bal_acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "fold_accuracies": [round(float(a), 4) for a in fold_accuracies],
        "fold_sizes": fold_sizes,
        "n_groups": int(groups.nunique()) if groups is not None else None,
        "std_accuracy": round(float(np.std(fold_accuracies)), 4),
        "confusion_matrix": cm,
        "per_class_recall": per_class_recall,
    }


def train_and_evaluate_all() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    df, dataset_sha256 = load_dataset()
    classes = ["no_spread", "marginal_spread", "spread"]
    materials = sorted(df["material"].unique().tolist())

    X = df[FEATURE_COLS_NUM + FEATURE_COLS_CAT]
    y = df[TARGET_COL]
    groups = df[GROUP_COL]
    report_groups = df["report_id"]

    # Pre-calculate training range for the range guard
    training_range = {
        "oxygen_pct": {"min": float(df["oxygen_pct"].min()), "max": float(df["oxygen_pct"].max())},
        "pressure_kpa": {"min": float(df["pressure_kpa"].min()), "max": float(df["pressure_kpa"].max())},
        "flow_cm_s": {"min": float(df["flow_cm_s"].min()), "max": float(df["flow_cm_s"].max())},
        "allowed_materials": materials,
        "per_material": {},
    }
    for m in materials:
        m_df = df[df["material"] == m]
        training_range["per_material"][m] = {
            "n_samples": len(m_df),
            "oxygen_pct": {"min": float(m_df["oxygen_pct"].min()), "max": float(m_df["oxygen_pct"].max())},
            "pressure_kpa": {"min": float(m_df["pressure_kpa"].min()), "max": float(m_df["pressure_kpa"].max())},
            "flow_cm_s": {"min": float(m_df["flow_cm_s"].min()), "max": float(m_df["flow_cm_s"].max())},
        }

    # Define model factories with zero-leakage preprocessors
    def make_dummy():
        return DummyClassifier(strategy="most_frequent")

    def make_lr():
        return Pipeline([
            ("prep", get_preprocessor()),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
        ])

    def make_rf():
        return Pipeline([
            ("prep", get_preprocessor()),
            ("clf", RandomForestClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_SEED)),
        ])

    def make_gb(seed: int = RANDOM_SEED):
        return Pipeline([
            ("prep", get_preprocessor()),
            ("clf", GradientBoostingClassifier(
                n_estimators=85,
                max_depth=3,
                learning_rate=0.05,
                min_samples_leaf=3,
                subsample=0.85,
                random_state=seed,
            )),
        ])

    models_to_eval = [
        ("majority_baseline", make_dummy),
        ("logistic_regression", make_lr),
        ("random_forest", make_rf),
        ("gradient_boosting", make_gb),
        (SERVING_MODEL, make_serving_model),
    ]

    # With only two marginal_spread rows, stratified group folds cannot preserve every
    # class in each fold. Leave out complete investigations/reports instead.
    group_kfold = LeaveOneGroupOut()
    report_kfold = LeaveOneGroupOut()
    plain_kfold = StratifiedKFold(
        n_splits=min(5, int(y.value_counts().min())),
        shuffle=True,
        random_state=RANDOM_SEED,
    )

    results: dict[str, Any] = {
        "dataset_sha256": dataset_sha256,
        "n_train": len(df),
        "serving_model": SERVING_MODEL,
        "classes": classes,
        "plain_cv_scheme": f"StratifiedKFold(k={plain_kfold.n_splits})",
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "models": {},
    }

    print("Evaluating models with leave-one-investigation/report-out CV and optimistic CV...")
    for model_name, factory in models_to_eval:
        print(f" -> {model_name}...")
        # 1. Investigation-grouped CV
        grouped_metrics = compute_cv_metrics(factory, X, y, groups, group_kfold, classes)
        # 2. Plain Stratified CV (optimistic)
        plain_metrics = compute_cv_metrics(factory, X, y, None, plain_kfold, classes)
        # 3. Report-Grouped CV
        report_metrics = compute_cv_metrics(factory, X, y, report_groups, report_kfold, classes)

        results["models"][model_name] = {
            "grouped_cv": grouped_metrics,
            "report_grouped_cv": report_metrics,
            "plain_cv": plain_metrics,
        }

    # Print summary
    print("\n--- RESULTS SUMMARY ---")
    gb_report = results["models"][SERVING_MODEL]["report_grouped_cv"]
    gb_grouped = results["models"][SERVING_MODEL]["grouped_cv"]
    gb_plain = results["models"][SERVING_MODEL]["plain_cv"]
    majority_acc = results["models"]["majority_baseline"]["report_grouped_cv"]["accuracy"]

    print(f"Majority Baseline Accuracy:        {majority_acc:.4f}")
    print(f"Logistic Regression Grouped:       {results['models']['logistic_regression']['grouped_cv']['accuracy']:.4f}")
    print(f"Random Forest Grouped:             {results['models']['random_forest']['grouped_cv']['accuracy']:.4f}")
    print(f"Linear SVM report_id Grouped: {gb_report['accuracy']:.4f} (Headline, Brief S6)")
    print(f"Linear SVM investigation Grouped: {gb_grouped['accuracy']:.4f} (Secondary, stricter)")
    print(f"Linear SVM Plain CV:        {gb_plain['accuracy']:.4f} (Optimistic)")
    print(f"Confusion Matrix (serving model):     {gb_grouped['confusion_matrix']}")

    # Linear SVM class decisions are deterministic; probability calibration uses the fixed seed.
    import numpy as _np
    loro_acc, loro_bal, loro_f1 = [], [], []
    for seed in [RANDOM_SEED]:
        preds, trues = [], []
        for tr_idx, va_idx in LeaveOneGroupOut().split(X, y, groups=report_groups):
            mdl = make_serving_model(seed)
            mdl.fit(X.iloc[tr_idx], y.iloc[tr_idx])
            preds.extend(mdl.predict(X.iloc[va_idx])); trues.extend(y.iloc[va_idx])
        loro_acc.append(accuracy_score(trues, preds))
        loro_bal.append(balanced_accuracy_score(trues, preds))
        loro_f1.append(f1_score(trues, preds, average="macro", zero_division=0))
    results["loro"] = {
        "scheme": "LeaveOneGroupOut(group=report_id), fixed linear SVM seed; no seed selection",
        "n_groups": int(report_groups.nunique()),
        "accuracy_mean": round(float(_np.mean(loro_acc)), 4),
        "accuracy_std": round(float(_np.std(loro_acc)), 4),
        "balanced_accuracy_mean": round(float(_np.mean(loro_bal)), 4),
        "macro_f1_mean": round(float(_np.mean(loro_f1)), 4),
    }
    print(f"LORO (fixed seed): acc {_np.mean(loro_acc):.4f} +/- {_np.std(loro_acc):.4f}  "
          f"bal {_np.mean(loro_bal):.4f}  macroF1 {_np.mean(loro_f1):.4f}")

    # Fit final headline model on full dataset
    final_model = make_serving_model()
    final_model.fit(X, y)

    # Save model artifact
    artifact_path = MODELS_DIR / "flame_spread_gb.joblib"
    joblib.dump(final_model, artifact_path)
    model_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    print(f"\nSaved model artifact to: {artifact_path}")

    # Build the model metadata consumed by the API and model card.
    model_meta = {
        "type": SERVING_MODEL,
        "release_mode": "research",
        "validation_status": "exploratory_model_selection",
        "probability_calibration": "Internal SVM calibration; not validated across reports",
        "hyperparameters": {"kernel": "linear", "C": 1.0, "random_state": RANDOM_SEED},
        "research_warning": "Exploratory model estimates only. The grouped score was used for model selection; probabilities are not validated across reports. No flight certification or safety clearance.",
        "n_train": len(df),
        "cv_accuracy": gb_report["accuracy"],
        "cv_balanced_accuracy": gb_report["balanced_accuracy"],
        "cv_macro_f1": gb_report["macro_f1"],
        "cv_scheme": "LeaveOneGroupOut(group=report_id)",
        "secondary_cv": {
            "scheme": "LeaveOneGroupOut(group=investigation)",
            "accuracy": gb_grouped["accuracy"],
            "balanced_accuracy": gb_grouped["balanced_accuracy"],
            "rationale": "Coarser grouping: isolates whole flight campaigns.",
        },
        "cv_fold_accuracies": gb_report["fold_accuracies"],
        "cv_fold_sizes": gb_report["fold_sizes"],
        "cv_caveat": (
            f"There are {report_groups.nunique()} report groups with row counts "
            f"{report_groups.value_counts().sort_values(ascending=False).tolist()}; "
            "pooled metrics are row-weighted and dominated by the largest report. "
            "Only two marginal_spread records exist, so class-specific performance for "
            "that label is not statistically reliable. Treat scores as exploratory, not "
            "as evidence for operational or safety use."
        ),
        "optimistic_cv_accuracy": gb_plain["accuracy"],
        "majority_baseline_accuracy": majority_acc,
        "features": FEATURE_COLS_NUM + FEATURE_COLS_CAT,
        "classes": classes,
        "confusion_matrix": gb_report["confusion_matrix"],
        "per_class_recall": gb_report["per_class_recall"],
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset_sha256": dataset_sha256,
        "model_sha256": model_sha256,
        "training_range": training_range,
        "loro": results.get("loro"),
    }

    # Preserve the search procedure's evaluation separately from this fixed model's score.
    evidence_root = REPORTS_DIR / "accuracy_experiments"
    manifest = evidence_root / "latest.json"
    evidence_path = (ROOT / json.loads(manifest.read_text())["results"]
                     if manifest.exists() else evidence_root / "results.json")
    if evidence_path.exists():
        evidence = json.loads(evidence_path.read_text())
        if evidence["dataset_sha256"] == dataset_sha256:
            model_meta["selection_evidence"] = str(evidence_path.relative_to(ROOT))
            model_meta["selection_evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
            model_meta["nested_search"] = {
                "scheme": "Nested leave-one-report-out selection across the complete candidate pool",
                "accuracy": evidence["nested"]["base"]["metrics"]["accuracy"],
                "balanced_accuracy": evidence["nested"]["base"]["metrics"]["balanced_accuracy"],
                "candidate_count": evidence["candidate_count"],
                "caveat": "Evaluates the full search procedure, not the fixed SVM alone. No independent external validation.",
            }

    meta_path = MODELS_DIR / "model_meta.json"
    meta_path.write_text(json.dumps(model_meta, indent=2), encoding="utf-8")
    print(f"Saved model metadata to: {meta_path}")

    # Save metrics JSON
    metrics_path = MODELS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved full metrics to: {metrics_path}")

    # Generate BASELINE_RESULTS.md report
    generate_baseline_report(results, model_meta)

    # Generate docs/MODEL_CARDS.md
    generate_model_card(model_meta)


def generate_baseline_report(results: dict[str, Any], meta: dict[str, Any]) -> None:
    rows = []
    for name, evaluations in results["models"].items():
        score = evaluations["report_grouped_cv"]
        label = name + (" (serving model)" if name == SERVING_MODEL else "")
        rows.append(f"| {label} | {score['accuracy']:.4f} | {score['balanced_accuracy']:.4f} | {score['macro_f1']:.4f} |")
    content = f"""# Baseline Models & Evaluation Report

Serving model: **linear SVM**, C=1.0, four inputs; trained on {meta['n_train']} observations.
Its {meta['cv_accuracy']:.1%} report-grouped score is exploratory: this model was selected
using this dataset. All three classes and every report remain included.

| Model | Report-grouped accuracy | Balanced accuracy | Macro-F1 |
|---|---:|---:|---:|
{chr(10).join(rows)}

Validation: {meta['cv_scheme']}, {meta['loro']['n_groups']} report folds.
Confusion matrix (true rows / predicted columns: no_spread, marginal_spread, spread):
`{meta['confusion_matrix']}`.

Full search procedure nested accuracy: {meta.get('nested_search', {}).get('accuracy', 'unavailable')}.
This describes model selection across the search, not the fixed SVM alone.

{meta['cv_caveat']}

{meta['research_warning']}
"""
    (REPORTS_DIR / "BASELINE_RESULTS.md").write_text(content, encoding="utf-8")


def generate_model_card(meta: dict[str, Any]) -> None:
    content = f"""# Model Card: FLARE-X Flame-Spread Classifier

- Serving model: linear SVM, C=1.0, StandardScaler and training-fold OneHotEncoder.
- Mode: research estimates; not an operational safety model.
- Dataset: {meta['n_train']} observations; SHA-256 `{meta['dataset_sha256']}`.
- Artifact SHA-256: `{meta['model_sha256']}`.
- Trained: {meta['trained_at']}.
- Inputs: {', '.join(meta['features'])}.
- Classes: {', '.join(meta['classes'])}.
- Exploratory grouped selection score: {meta['cv_accuracy']:.1%}.
- Majority baseline: {meta['majority_baseline_accuracy']:.1%}.
- Balanced accuracy: {meta['cv_balanced_accuracy']:.1%}.
- Macro-F1: {meta['cv_macro_f1']:.4f}.
- Full search procedure nested accuracy: {meta.get('nested_search', {}).get('accuracy', 'unavailable')}.
- Probability calibration: {meta['probability_calibration']}.

{meta['cv_caveat']}

The legacy `flame_spread_gb.joblib` filename is retained for loader compatibility;
`type=linear_svm` identifies its contents. Retraining uses the same fixed SVM configuration.

Public research estimates require dataset/artifact hashes to match and a grouped score above
the majority baseline. Individual predictions still abstain outside the material's joint
experimental domain, at conflicting conditions, or with insufficient material evidence.
Neither a no_spread prediction nor a model transition establishes safety. Geometry, flow
direction and ignition history are omitted by this four-input model. No independent external
validation or certification is claimed. The original gradient booster remains a comparison
in metrics.json; the experiment evidence records selection separately.

{meta['research_warning']}
"""
    (DOCS_DIR / "MODEL_CARDS.md").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    train_and_evaluate_all()
