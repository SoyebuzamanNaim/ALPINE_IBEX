"""A corrupt optional model must not take the evidence application offline."""
import os
from pathlib import Path
import shutil
import subprocess
import sys


def test_evidence_service_starts_with_an_unusable_model(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(root / "cache", tmp_path / "cache")
    (tmp_path / "models").mkdir()
    shutil.copy2(root / "models/model_meta.json", tmp_path / "models/model_meta.json")
    (tmp_path / "models/flame_spread_gb.joblib").write_bytes(b"invalid optional artifact")
    script = """
from fastapi.testclient import TestClient
from src.api.main import app
with TestClient(app) as client:
    scenario = dict(oxygen_pct=19, pressure_kpa=101.3, flow_cm_s=5, material='PMMA')
    assert client.get('/health').json()['evidence_ready'] is True
    assert client.post('/evidence', json=scenario).status_code == 200
    assert client.post('/predict', json=scenario).status_code == 503
    assert client.get('/reports/search', params={'query': 'PMMA'}).json()['reports']
"""
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path,
                            env={**os.environ, "PYTHONPATH": str(tmp_path)}, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
