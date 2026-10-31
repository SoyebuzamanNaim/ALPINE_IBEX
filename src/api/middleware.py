"""Small process-local request guards for the prototype API."""
from __future__ import annotations

import json
import threading
import time
from collections import OrderedDict
from typing import Any


class RequestGuardMiddleware:
    """Bound request bodies and burst rates before endpoint work begins.

    Rate limits are intentionally per-process and use the ASGI client's socket
    address. Deployments behind a proxy should add a trusted shared limiter at
    the edge rather than accepting an untrusted forwarded-for header here.
    """

    HEAVY_POST_PATHS = {
        "/predict",
        "/counterfactual",
        "/sweep",
        "/boundary",
        "/scenario/parse",
        "/api/conflict/compare-studies",
        "/api/conflict/compare-experiments",
    }

    def __init__(
        self,
        app: Any,
        *,
        max_body_bytes: int = 65_536,
        general_requests_per_minute: int = 600,
        heavy_requests_per_minute: int = 60,
        max_tracked_clients: int = 4096,
    ) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes
        self.general_limit = general_requests_per_minute
        self.heavy_limit = heavy_requests_per_minute
        self.max_tracked_clients = max_tracked_clients
        self._windows: OrderedDict[tuple[str, str], tuple[int, int]] = OrderedDict()
        self._lock = threading.Lock()
        self._checks = 0

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "")
        client = scope.get("client")
        client_key = str(client[0]) if client else "unknown"
        if not self._allow_request(client_key, path):
            await self._send_json(send, 429, {"detail": "Request rate limit exceeded; retry after one minute."}, [(b"retry-after", b"60")])
            return

        content_length = next((value for key, value in scope.get("headers", []) if key.lower() == b"content-length"), None)
        if method in {"POST", "PUT", "PATCH"} and content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    await self._send_too_large(send)
                    return
            except ValueError:
                await self._send_json(send, 400, {"detail": "Invalid Content-Length header."})
                return

        received_bytes = 0

        async def limited_receive() -> dict[str, Any]:
            nonlocal received_bytes
            message = await receive()
            if message.get("type") == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_body_bytes:
                    raise _RequestTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestTooLarge:
            await self._send_too_large(send)

    def _allow_request(self, client: str, path: str) -> bool:
        now = int(time.monotonic() // 60)
        key = (client, "heavy" if path in self.HEAVY_POST_PATHS else "general")
        limit = self.heavy_limit if key[1] == "heavy" else self.general_limit
        with self._lock:
            window, count = self._windows.get(key, (now, 0))
            if window != now:
                window, count = now, 0
            if count >= limit:
                return False
            self._windows[key] = (window, count + 1)
            self._windows.move_to_end(key)
            self._checks += 1
            if self._checks % 128 == 0:
                for old_key, (old_window, _) in list(self._windows.items()):
                    if old_window < now:
                        self._windows.pop(old_key, None)
            while len(self._windows) > self.max_tracked_clients:
                self._windows.popitem(last=False)
        return True

    async def _send_too_large(self, send: Any) -> None:
        await self._send_json(send, 413, {"detail": f"Request body exceeds the {self.max_body_bytes}-byte limit."})

    @staticmethod
    async def _send_json(send: Any, status: int, payload: dict[str, str], headers: list[tuple[bytes, bytes]] | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        response_headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode("ascii"))]
        response_headers.extend(headers or [])
        await send({"type": "http.response.start", "status": status, "headers": response_headers})
        await send({"type": "http.response.body", "body": body})


class _RequestTooLarge(Exception):
    pass
