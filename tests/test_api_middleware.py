"""Regression tests for API request size and rate guards."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.api.middleware import RequestGuardMiddleware


def test_request_guard_limits_expensive_requests_per_client():
    app = FastAPI()
    app.add_middleware(
        RequestGuardMiddleware,
        heavy_requests_per_minute=1,
        general_requests_per_minute=2,
    )

    @app.post("/predict")
    async def predict(request: Request):
        return {"ok": True}

    @app.get("/status")
    async def status():
        return {"ok": True}

    with TestClient(app) as client:
        assert client.post("/predict").status_code == 200
        limited = client.post("/predict")
        assert limited.status_code == 429
        assert limited.headers["retry-after"] == "60"

        assert client.get("/status").status_code == 200
        assert client.get("/status").status_code == 200
        assert client.get("/status").status_code == 429
