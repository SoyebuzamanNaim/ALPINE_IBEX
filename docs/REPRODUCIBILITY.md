# Reproducibility Guide (Phase 15)

> **Document Status:** Complete step-by-step instructions to independently reproduce the data ingestion, cross-validation, model artifacts, and test suite for FLARE-X.

---

## 1. Prerequisites & Environment Setup

- **Operating System:** Linux (Ubuntu 22.04+ or Debian-based), macOS, or Windows WSL2.
- **Python Version:** Python 3.12 (or 3.10+).

```bash
# Clone or navigate to the repository
cd flare-x-prototype

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install exact dependencies
pip install -r requirements.txt
```

---

## 2. Data Ingestion & Hash Verification

To extract the 145 discrete microgravity spaceflight observations from raw NASA PSI/NTRS reports into canonical Parquet and CSV tables:

```bash
# Execute full extraction pipeline
python -c "from src.ingestion.extract import build_all; build_all()"

# Verify SHA-256 dataset checksum
sha256sum cache/experiments.parquet
# Expected: d5a06d2d0cce4e2fe2207bd490df4ec1213ca6eeabc1436243eb8d49dafd0be0
```

---

## 3. Model Training & Cross-Validation

To train the Gradient Boosting model, evaluate honest 5-fold grouped cross-validation, and write `models/model_meta.json` and `models/metrics.json`:

```bash
python src/compute/model.py
```

Expected Output:
```text
Loaded 145 microgravity experiments.
Report-grouped 5-fold CV (report_id):
  honest grouped CV accuracy: 79.31%
  balanced accuracy:          72.41%
  macro F1:                   0.7315
  majority class baseline:    51.72%
  optimistic plain CV:        80.69%
Model saved to: models/flame_spread_gb.joblib
Metadata saved to: models/model_meta.json
Metrics saved to: models/metrics.json
```

---

## 4. Running the Complete Automated Test Suite

To run all 68 unit, integration, and red-team tests:

```bash
pytest tests/ -v
```

Expected: **68 passed in ~7.0s**.

---

## 5. Launching the Local Application

Execute the single-command runner script:

```bash
./scripts/run_local.sh
```

- **Mission Control Web App:** [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
