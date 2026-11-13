"""Catalog caching must not preserve incomplete NASA PSI responses."""

import json

import pytest

from scripts import build_catalog


class _PSIResponse:
    def __init__(self, records):
        self.payload = json.dumps({
            "hits": {"hits": [{"_source": record} for record in records]}
        }).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.payload


def test_incomplete_psi_response_is_not_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(build_catalog, "DATA_RAW_PSI", tmp_path)
    monkeypatch.setattr(
        build_catalog.urllib.request, "urlopen",
        lambda request, timeout: _PSIResponse([{"Accession": "PSI-25", "Title": "BASS-II"}]),
    )

    with pytest.raises(ValueError, match="missing shortlisted investigations"):
        build_catalog.fetch_psi_data()

    assert not (tmp_path / "psi_investigations.json").exists()


def test_incomplete_existing_cache_is_refetched(tmp_path, monkeypatch):
    cache_file = tmp_path / "psi_investigations.json"
    cache_file.write_text(json.dumps({"PSI-25": {"Title": "BASS-II"}}))
    records = [
        {"Accession": psi_id, "Title": name}
        for psi_id, (name, _, _) in build_catalog.PRIORITY_SHORTLIST.items()
    ]
    monkeypatch.setattr(build_catalog, "DATA_RAW_PSI", tmp_path)
    monkeypatch.setattr(
        build_catalog.urllib.request, "urlopen",
        lambda request, timeout: _PSIResponse(records),
    )

    result = build_catalog.fetch_psi_data()

    assert set(result) == set(build_catalog.PRIORITY_SHORTLIST)
    assert set(json.loads(cache_file.read_text())) == set(build_catalog.PRIORITY_SHORTLIST)
