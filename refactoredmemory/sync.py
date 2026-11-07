"""Bounded, authenticated direct-peer operation exchange.

Authentication of the HTTP caller belongs to the endpoint: a bearer credential
must resolve to an admitted peer ID before ``exchange`` is invoked. Operation
origin authentication, causal admission and durable acknowledgement belong to
the Store. This module never copies a database or treats wall clocks as order.
"""

from __future__ import annotations

import ipaddress
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

PROTOCOL = "refactoredmemory-sync/1"
MAX_BODY_BYTES = 4 * 1024 * 1024
MAX_BATCH = 1000
MAX_ORIGINS = 128


class SyncError(ValueError):
    """An exchange failed without declaring unsent/unknown progress complete."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _frontier(value: Any) -> dict[str, int]:
    if not isinstance(value, dict) or len(value) > MAX_ORIGINS:
        raise SyncError("invalid_frontier", "A bounded origin-to-sequence map is required")
    for origin, seq in value.items():
        if (not isinstance(origin, str) or not origin or len(origin) > 256
                or isinstance(seq, bool) or not isinstance(seq, int)
                or seq < 0 or seq > 2**63 - 1):
            raise SyncError("invalid_frontier", "Invalid origin or sequence")
    return {origin: seq for origin, seq in value.items() if seq}


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise SyncError("invalid_request", f"{name} must be an integer from {low} to {high}")
    return value


def _encode(value: Any) -> bytes:
    try:
        data = json.dumps(value, ensure_ascii=False, allow_nan=False,
                          separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise SyncError("invalid_json", "Exchange is not valid JSON") from exc
    if len(data) > MAX_BODY_BYTES:
        raise SyncError("too_large", "Exchange exceeds the bounded body size")
    return data


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SyncError("invalid_json", "Duplicate JSON object key")
        result[key] = value
    return result


def decode_body(data: bytes) -> dict[str, Any]:
    """Decode the endpoint's already-bounded body without ambiguous JSON values."""
    if len(data) > MAX_BODY_BYTES:
        raise SyncError("too_large", "Exchange exceeds the bounded body size")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               SyncError("invalid_json", "Non-finite JSON number")))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SyncError("invalid_json", "Malformed exchange JSON") from exc
    if not isinstance(value, dict):
        raise SyncError("invalid_request", "Exchange body must be an object")
    return value


def _operations(value: Any, limit: int = MAX_BATCH) -> list[dict[str, Any]]:
    if (not isinstance(value, list) or len(value) > limit
            or any(not isinstance(item, dict) for item in value)):
        raise SyncError("invalid_operations", "Operations must be a bounded list of objects")
    return value


def _fit_batch(envelope: dict[str, Any]) -> dict[str, Any]:
    """Reduce an operation batch to fit the wire bound; never split a group."""
    while True:
        try:
            _encode(envelope)
            return envelope
        except SyncError as exc:
            if exc.code != "too_large" or len(envelope["operations"]) <= 1:
                raise
            envelope["operations"] = envelope["operations"][:len(envelope["operations"]) // 2]
            if "more" in envelope:
                envelope["more"] = True


def exchange(store: Any, payload: dict[str, Any], peer_id: str) -> dict[str, Any]:
    """Handle one authenticated HTTP exchange, with durable receive before reply.

    ``peer_id`` MUST come from the server's credential mapping, never payload.
    The Store rejects non-admitted peers and invalid/conflicting operations.
    """
    if not isinstance(payload, dict):
        raise SyncError("invalid_request", "Exchange body must be an object")
    if set(payload) - {"protocol", "store_id", "frontier", "operations", "limit"}:
        raise SyncError("invalid_request", "Unknown exchange field")
    if payload.get("protocol") != PROTOCOL:
        raise SyncError("unsupported_protocol", "Unsupported peer protocol")
    status = store.status()
    if payload.get("store_id") != status["store_id"]:
        raise SyncError("wrong_store", "Peer belongs to a different knowledge store")
    frontier = _frontier(payload.get("frontier"))
    limit = _integer(payload.get("limit", 100), "limit", 1, MAX_BATCH)
    operations = _operations(payload.get("operations"))
    _encode(payload)
    receipt = store.receive(operations, peer_id=peer_id)
    exported = store.export_operations(frontier=frontier, limit=limit)
    response = {
        "protocol": PROTOCOL,
        "store_id": status["store_id"],
        "peer_id": status["peer_id"],
        "operations": _operations(exported["operations"], limit),
        "frontier": _frontier(exported["frontier"]),
        "more": bool(exported["more"]),
        "receipt": receipt,
    }
    return _fit_batch(response)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A bearer credential must never follow a server-directed destination.
        return None


def _endpoint(url: str) -> str:
    if not isinstance(url, str) or len(url) > 4096:
        raise SyncError("invalid_url", "A bounded peer URL is required")
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
        host = parsed.hostname
    except ValueError as exc:
        raise SyncError("invalid_url", "Invalid peer URL") from exc
    if (parsed.scheme not in {"http", "https"} or not host
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or any(c.isspace() for c in url)):
        raise SyncError("invalid_url", "Use an HTTP(S) URL without userinfo, query or fragment")
    if port is not None and port == 0:
        raise SyncError("invalid_url", "Invalid peer port")
    if parsed.scheme == "http":
        try:
            loopback = ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = False
        if not loopback:
            raise SyncError("tls_required", "Remote peer synchronization requires HTTPS")
    path = parsed.path.rstrip("/")
    if not path:
        path = "/sync"
    elif not path.endswith("/sync"):
        raise SyncError("invalid_url", "Peer endpoint must end in /sync")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _post(url: str, token: str, payload: dict[str, Any], timeout: float,
          retries: int) -> dict[str, Any]:
    data = _encode(payload)
    handlers: list[Any] = [_NoRedirect()]
    if urllib.parse.urlsplit(url).scheme == "http":
        # Validated numeric loopback traffic must stay local even if a machine's
        # proxy settings omit its NO_PROXY entry.
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, data=data, method="POST", headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "close",
        })
        try:
            with opener.open(request, timeout=timeout) as response:
                if response.headers.get_content_type() != "application/json":
                    raise SyncError("invalid_response", "Peer response must be JSON")
                if response.headers.get("Content-Encoding", "identity") != "identity":
                    raise SyncError("invalid_response", "Compressed peer responses are unsupported")
                raw_length = response.headers.get("Content-Length")
                if raw_length is not None:
                    try:
                        size = int(raw_length)
                    except ValueError as exc:
                        raise SyncError("invalid_response", "Invalid response length") from exc
                    if size < 0 or size > MAX_BODY_BYTES:
                        raise SyncError("too_large", "Peer response exceeds the bounded body size")
                raw = response.read(MAX_BODY_BYTES + 1)
                return decode_body(raw)
        except urllib.error.HTTPError as exc:
            code = exc.code
            exc.close()
            if code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(0.05 * 2**attempt)
                continue
            # Never echo response bodies, URLs or bearer values into logs/errors.
            raise SyncError("http_error", f"Peer exchange returned HTTP {code}") from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt < retries:
                time.sleep(0.05 * 2**attempt)
                continue
            raise SyncError("transport_error", "Peer exchange could not complete") from None
    raise AssertionError("unreachable")


def sync_once(store: Any, url: str, token: str, batch_size: int = 100, *,
              timeout: float = 10, max_rounds: int = 1000, retries: int = 2,
              expected_peer: str | None = None) -> dict[str, Any]:
    """Push and pull bounded operation groups until caught up or the round cap.

    No persistent transport cursor is advanced here. Each request derives its
    frontier from durable causally applied Store state, so retry after lost
    responses or a process restart is safe. A live writer may prevent reaching
    a shared frontier; return ``complete=False`` at the cap rather than invent
    convergence. Delivery counts include retries at the semantic-call level
    and do not claim new unique operations.
    """
    endpoint = _endpoint(url)
    _integer(batch_size, "batch_size", 1, MAX_BATCH)
    _integer(max_rounds, "max_rounds", 1, 10000)
    _integer(retries, "retries", 0, 5)
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not 0 < timeout <= 60):
        raise SyncError("invalid_request", "timeout must be between 0 and 60 seconds")
    if (not isinstance(token, str) or not token or len(token) > 4096
            or any(ord(c) < 33 or ord(c) > 126 for c in token)):
        raise SyncError("invalid_token", "A nonempty printable bearer credential is required")
    initial = store.status()
    own_peer = initial["peer_id"]
    store_id = initial["store_id"]
    remote_frontier: dict[str, int] = {}
    remote_peer = expected_peer
    sent = received = 0
    complete = False
    previous_progress = None
    reason = "round_limit"
    remote_pending = 0
    remote_rejected = 0
    for rounds in range(1, max_rounds + 1):
        status = store.status()
        # A metadata-only first round obtains the peer frontier without sending
        # every local operation merely because no transport cursor is cached.
        operations = [] if rounds == 1 else store.export_operations(
            frontier=remote_frontier, limit=batch_size)["operations"]
        payload = _fit_batch({
            "protocol": PROTOCOL, "store_id": store_id,
            "frontier": _frontier(status["frontier"]),
            "operations": _operations(operations, batch_size), "limit": batch_size,
        })
        response = _post(endpoint, token, payload, timeout, retries)
        if response.get("protocol") != PROTOCOL or response.get("store_id") != store_id:
            raise SyncError("wrong_store", "Peer protocol or knowledge-store identity mismatch")
        response_peer = response.get("peer_id")
        if (not isinstance(response_peer, str) or not response_peer or len(response_peer) > 256
                or response_peer == own_peer or (remote_peer and response_peer != remote_peer)):
            raise SyncError("wrong_peer", "Peer identity is unexpected or duplicates the local peer")
        remote_peer = response_peer
        remote_frontier = _frontier(response.get("frontier"))
        incoming = _operations(response.get("operations"), batch_size)
        if not isinstance(response.get("more"), bool):
            raise SyncError("invalid_response", "Peer response is missing its continuation state")
        receipt = response.get("receipt")
        if not isinstance(receipt, dict):
            raise SyncError("invalid_response", "Peer response is missing its durable receipt")
        remote_pending = _integer(receipt.get("pending"), "receipt.pending", 0, 2**63 - 1)
        remote_rejected = _integer(receipt.get("rejected", 0), "receipt.rejected", 0, 2**63 - 1)
        store.receive(incoming, peer_id=remote_peer)
        sent += len(payload["operations"])
        received += len(incoming)
        local = store.status()
        if local.get("rejected", 0) or remote_rejected:
            reason = "semantic_rejection"
            break
        remaining = store.export_operations(frontier=remote_frontier, limit=1)
        if (not response["more"] and not remaining["operations"]
                and _frontier(local["frontier"]) == remote_frontier
                and not local.get("pending", 0) and not remote_pending):
            complete = True
            reason = "shared_frontier"
            break
        progress = (_frontier(local["frontier"]), remote_frontier,
                    local.get("pending", 0), remote_pending)
        if progress == previous_progress:
            reason = "missing_dependencies"
            break
        previous_progress = progress
    final = store.status()
    return {"protocol": PROTOCOL, "peer_id": remote_peer, "rounds": rounds,
            "sent": sent, "received": received, "complete": complete,
            "frontier": final["frontier"], "remote_frontier": remote_frontier,
            "pending": final.get("pending", 0),
            "remote_pending": remote_pending, "rejected": final.get("rejected", 0),
            "remote_rejected": remote_rejected, "reason": reason}
