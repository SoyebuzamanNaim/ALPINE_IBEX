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
    """A drop-tower row must name the table it was read out of.

    This used to check DROP_EXT_07, one of 49 rows attributed to five NASA reports that
    no source check could support; it also credited CR-182264 to Olson when 19890014267
    is Ferkul. It now checks a row taken off the rendered table itself, which is the
    extinction at 17% O2 and 0.81 cm/s in the last column of TABLE I.
    """
    service = ProvenanceService()
    record = service.get_provenance("FERKUL_T1_08")
    assert record is not None
    assert "19890014267" in record["report_id"]
    assert "TABLE I" in record["exact_source_citation"]
    assert record["verification_tier"] == "HAND_TRANSCRIBED_FROM_SOURCE"
    assert record["outcome"] == "no_spread"
    assert record["oxygen_pct"] == 17.0
    assert record["flow_cm_s"] == 0.81


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
