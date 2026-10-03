"""Fetch NTRS citation metadata and PDFs, preserving originals with SHA256 hashes.

Usage:
    python -m src.ingestion.ntrs_fetch 20210011385 20160000593 ...

Every file written to data/raw/ntrs/<id>/ is the unmodified server response.
A manifest row (id, url, sha256, bytes, fetched_at) is appended to
data/metadata/source_manifest.csv. Nothing is ever constructed: if NTRS does not
return a record, the id is reported as unresolved.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "ntrs"
MANIFEST = ROOT / "data" / "metadata" / "source_manifest.csv"
API = "https://ntrs.nasa.gov/api/citations/{id}"
BASE = "https://ntrs.nasa.gov"
UA = {"User-Agent": "FLARE-X-research-prototype/0.1 (+public NTRS API)"}

MANIFEST_FIELDS = ["source", "report_id", "kind", "url", "local_path", "sha256", "bytes", "fetched_at"]


def _get(url: str, retries: int = 3) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as exc:  # network errors are retried, then raised
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _append_manifest(row: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if MANIFEST.exists():
        with MANIFEST.open() as f:
            for r in csv.DictReader(f):
                existing.add((r["report_id"], r["kind"], r["sha256"]))
    if (row["report_id"], row["kind"], row["sha256"]) in existing:
        return
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def fetch(report_id: str, with_pdf: bool = True) -> dict:
    out = RAW / report_id
    out.mkdir(parents=True, exist_ok=True)
    meta_bytes = _get(API.format(id=report_id))
    meta = json.loads(meta_bytes)
    if str(meta.get("id")) != str(report_id):
        raise RuntimeError(f"NTRS returned mismatching id for {report_id}")
    (out / "citation.json").write_bytes(meta_bytes)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _append_manifest({
        "source": "NTRS", "report_id": report_id, "kind": "citation_json",
        "url": API.format(id=report_id), "local_path": str((out / "citation.json").relative_to(ROOT)),
        "sha256": sha256_bytes(meta_bytes), "bytes": len(meta_bytes), "fetched_at": now,
    })
    pdfs = []
    if with_pdf:
        for d in meta.get("downloads", []) or []:
            link = (d.get("links") or {}).get("pdf") or (d.get("links") or {}).get("original")
            if not link or not link.lower().split("?")[0].endswith(".pdf"):
                continue
            url = link if link.startswith("http") else BASE + link
            name = Path(link.split("?")[0]).name
            dest = out / name
            if not dest.exists():
                dest.write_bytes(_get(url))
            b = dest.read_bytes()
            _append_manifest({
                "source": "NTRS", "report_id": report_id, "kind": "pdf", "url": url,
                "local_path": str(dest.relative_to(ROOT)), "sha256": sha256_bytes(b),
                "bytes": len(b), "fetched_at": now,
            })
            pdfs.append(str(dest))
    return {"id": report_id, "title": meta.get("title"), "pdfs": pdfs}


if __name__ == "__main__":
    for rid in sys.argv[1:]:
        try:
            info = fetch(rid)
            print(f"OK  {rid}  {len(info['pdfs'])} pdf  {info['title'][:90]}")
        except Exception as exc:
            print(f"ERR {rid}  {exc}")
