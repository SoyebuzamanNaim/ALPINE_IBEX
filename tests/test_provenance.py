"""Unit and integration tests for Provenance and Citation Tracing."""
from fastapi.testclient import TestClient
from src.analysis.provenance_service import ProvenanceService
from src.api.main import app


def test_provenance_service_lookup():
    service = ProvenanceService()
    record = service.get_provenance("BASS2_B1")
    assert record is not None
    assert record["experiment_id"] == "BASS2_B1"
    assert "NASA/TM-20210011385" in record["exact_source_citation"]
    assert record["verification_tier"] == "VERIFIED_FLIGHT_TABLE"
    assert record["data_origin"] == "direct_measurement"


def test_drop_tower_provenance():
    service = ProvenanceService()
    record = service.get_provenance("DROP_EXT_07")
    assert record is not None
    assert "19890014267" in record["report_id"]
    assert "CR-182264" in record["exact_source_citation"]
    assert record["verification_tier"] == "VERIFIED_DROP_TOWER_TABLE"


def test_provenance_api():
    client = TestClient(app)
    # Single item
    r = client.get("/api/provenance/BASS2_B1")
    assert r.status_code == 200
    assert r.json()["experiment_id"] == "BASS2_B1"

    # Query
    r = client.get("/api/provenance?material=PMMA&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    assert len(data["records"]) <= 10
    for rec in data["records"]:
        assert rec["material"] == "PMMA"
