"""Public Pages builds must explicitly configure a reachable API origin."""
import json

import pytest

from scripts.configure_pages import public_api_url, write_config


@pytest.mark.parametrize("value", ["", "http://example.com", "https://localhost", "https://127.0.0.1", "https://10.0.0.1", "https://user:secret@example.com", "https://example.com?key=x", "https://example.com/#x", "https://example.com:99999"])
def test_public_api_config_rejects_incomplete_or_private_urls(value):
    with pytest.raises(ValueError):
        public_api_url(value)


def test_pages_api_configuration_is_json_encoded(tmp_path):
    destination = tmp_path / "config.js"
    write_config(destination, " https://api.example.com/ ")
    assert destination.read_text() == f"window.FLARE_API_BASE = {json.dumps('https://api.example.com')};\n"
