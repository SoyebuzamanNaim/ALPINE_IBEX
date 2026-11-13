"""Write explicit public API configuration; refuse an incomplete demo deployment."""
from __future__ import annotations

import ipaddress
import json
import os
from pathlib import Path
from urllib.parse import urlsplit


def public_api_url(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    try:
        public_host = ipaddress.ip_address(host).is_global
    except ValueError:
        public_host = "." in host and host != "localhost" and not host.endswith((".localhost", ".local", ".internal"))
    if (parsed.scheme != "https" or not public_host or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise ValueError("Set repository variable FLARE_API_BASE to the reachable public HTTPS FastAPI URL before deploying the demo.")
    # Force validation of malformed or out-of-range ports.
    parsed.port
    return value


def write_config(destination: Path, api_base: str) -> None:
    destination.write_text(f"window.FLARE_API_BASE = {json.dumps(public_api_url(api_base))};\n")


if __name__ == "__main__":
    write_config(Path("_site/app/config.js"), os.environ.get("FLARE_API_BASE", ""))
