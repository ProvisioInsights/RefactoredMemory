"""Bounded, authenticated direct-peer operation exchange.

Authentication of the HTTP caller belongs to the endpoint: a bearer credential
must resolve to an admitted peer ID before ``exchange`` is invoked. Operation
origin authentication, causal admission and durable acknowledgement belong to
the Store. This module never copies a database or treats wall clocks as order.
"""

from __future__ import annotations

import ipaddress
import gzip
import os
import zlib
import http.client
import socket
import threading
import json
import math
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

    def __init__(self, code: str, message: str, *, retry_after_seconds: float | None = None,
                 reason: str | None = None, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.retry_after_seconds = retry_after_seconds
        self.reason = reason
        self.http_status = http_status


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


# Resolver code is fixed: only a host and numeric port enter the child. The
# isolated child receives no peer credential, operation body, or proxy secret.
_RESOLVER_CODE = """import json,socket,sys
try:
    rows=socket.getaddrinfo(sys.argv[1],int(sys.argv[2]),socket.AF_UNSPEC,socket.SOCK_STREAM,socket.IPPROTO_TCP)
    print(json.dumps([[int(a),int(t),int(p),list(s)] for a,t,p,c,s in rows[:64]]))
except OSError:
    print('[]')
    sys.exit(2)
"""


class _AttemptDeadline:
    """Abort active sockets on a wall deadline; no background request worker."""

    def __init__(self, timeout, stop_event=None):
        self.end = time.monotonic() + timeout
        self.stop_event = stop_event
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.sockets = set()
        self.thread = threading.Thread(target=self._watch, name="refactoredmemory-sync-deadline", daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def check(self):
        if self.stop_event is not None and self.stop_event.is_set():
            raise SyncError("cancelled", "Synchronization cancelled")
        remaining = self.end - time.monotonic()
        if remaining <= 0:
            raise SyncError("transport_timeout", "Peer exchange exceeded its time budget")
        return remaining

    @staticmethod
    def _shutdown(sock):
        try:
            # Bypass SSLSocket.shutdown's SSL state mutation while another
            # thread may be inside a handshake/read. OS shutdown wakes the I/O.
            socket.socket.shutdown(sock, socket.SHUT_RDWR)
        except OSError:
            pass

    @classmethod
    def _close(cls, sock):
        cls._shutdown(sock)
        try:
            sock.close()
        except OSError:
            pass

    def _shutdown_all(self):
        with self.lock:
            sockets = list(self.sockets)
        for sock in sockets:
            self._shutdown(sock)

    def add(self, sock):
        with self.lock:
            self.sockets.add(sock)
        try:
            sock.settimeout(self.check())
        except BaseException:
            self._close(sock)
            raise

    def _close_all(self):
        with self.lock:
            sockets = list(self.sockets)
            self.sockets.clear()
        for sock in sockets:
            self._close(sock)

    def _watch(self):
        while not self.done.is_set():
            try:
                remaining = self.check()
            except SyncError:
                # Only interrupt OS I/O here. Closing an SSLSocket would clear
                # SSL state concurrently with the caller's handshake or read.
                self._shutdown_all()
                return
            self.done.wait(min(remaining, 0.025))

    def __exit__(self, *exc):
        self.done.set()
        self._shutdown_all()
        self.thread.join()
        # The request has unwound and the watchdog has exited; the caller owns
        # all final close operations, including SSLSocket's SSL-object cleanup.
        self._close_all()

    def resolve(self, host, port):
        """Bound libc name resolution in a terminated-and-reaped subprocess."""
        import os
        import subprocess
        import sys
        self.check()
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None:
            family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
            sockaddr = (str(address), port, 0, 0) if address.version == 6 else (str(address), port)
            return [(family, socket.SOCK_STREAM, socket.IPPROTO_TCP, sockaddr)]
        if not isinstance(host, str) or not host or len(host) > 1024 or type(port) is not int or not 1 <= port <= 65535:
            raise SyncError("invalid_url", "Invalid connection address")
        process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-c", _RESOLVER_CODE, host, str(port)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"PATH": os.defpath},
        )
        try:
            while True:
                try:
                    raw, _ = process.communicate(timeout=min(self.check(), 0.025))
                    break
                except subprocess.TimeoutExpired:
                    continue
            self.check()
            if process.returncode != 0 or len(raw) > 65536:
                raise SyncError("transport_error", "Peer address resolution failed")
            try:
                rows = json.loads(raw)
            except (UnicodeError, ValueError) as exc:
                raise SyncError("transport_error", "Peer address resolution failed") from exc
            if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
                raise SyncError("transport_error", "Peer address resolution failed")
            result = []
            for row in rows:
                if not isinstance(row, list) or len(row) != 4:
                    raise SyncError("transport_error", "Invalid resolved address")
                family, socktype, protocol, sockaddr = row
                if family not in {socket.AF_INET, socket.AF_INET6} or socktype != socket.SOCK_STREAM or protocol != socket.IPPROTO_TCP:
                    raise SyncError("transport_error", "Invalid resolved address")
                if (not isinstance(sockaddr, list) or len(sockaddr) != (4 if family == socket.AF_INET6 else 2)
                        or sockaddr[1] != port):
                    raise SyncError("transport_error", "Invalid resolved address")
                try:
                    ip = ipaddress.ip_address(sockaddr[0])
                except ValueError as exc:
                    raise SyncError("transport_error", "Invalid resolved address") from exc
                if ip.version != (6 if family == socket.AF_INET6 else 4):
                    raise SyncError("transport_error", "Invalid resolved address")
                if family == socket.AF_INET6 and any(type(x) is not int or not 0 <= x <= 2**32 - 1 for x in sockaddr[2:]):
                    raise SyncError("transport_error", "Invalid resolved address")
                result.append((family, socktype, protocol, tuple(sockaddr)))
            return result
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=0.25)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            if process.stdout is not None:
                process.stdout.close()

    def connect(self, address, timeout=None, source_address=None):
        host, port = address
        for family, socktype, protocol, sockaddr in self.resolve(host, port):
            self.check()
            sock = socket.socket(family, socktype, protocol)
            self.add(sock)
            try:
                if source_address:
                    sock.bind(source_address)
                sock.connect(sockaddr)
                self.check()
                return sock
            except OSError:
                self._close(sock)
                self.check()
        raise OSError("Peer connection failed")


class _DeadlineConnection:
    def __init__(self, *args, deadline, **kwargs):
        super().__init__(*args, **kwargs)
        self.deadline = deadline
        self._create_connection = deadline.connect


class _DeadlineHTTPConnection(_DeadlineConnection, http.client.HTTPConnection):
    pass


class _DeadlineHTTPSConnection(_DeadlineConnection, http.client.HTTPSConnection):
    def connect(self):
        # Keep stdlib CONNECT handling and the original hostname for SNI and
        # certificate verification. Register TLS before starting its handshake.
        http.client.HTTPConnection.connect(self)
        server_hostname = self._tunnel_host or self.host
        self.sock = self._context.wrap_socket(self.sock, server_hostname=server_hostname,
                                               do_handshake_on_connect=False)
        self.deadline.add(self.sock)
        self.sock.do_handshake()
        self.deadline.check()


class _DeadlineHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, deadline):
        super().__init__()
        self.deadline = deadline

    def http_open(self, req):
        return self.do_open(lambda *args, **kwargs: _DeadlineHTTPConnection(*args, deadline=self.deadline, **kwargs), req)


class _DeadlineHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, deadline):
        super().__init__()
        self.deadline = deadline

    def https_open(self, req):
        return self.do_open(lambda *args, **kwargs: _DeadlineHTTPSConnection(*args, deadline=self.deadline, **kwargs),
                            req, context=self._context)


def decode_peer_request(data: bytes, encoding: str = "identity") -> dict[str, Any]:
    """Bound both wire bytes and expanded bytes before parsing authenticated input."""
    if len(data) > MAX_BODY_BYTES:
        raise SyncError("too_large", "Peer request exceeds the bounded body size")
    if encoding == "identity":
        return decode_body(data)
    if encoding != "gzip":
        raise SyncError("invalid_encoding", "Unsupported peer request encoding")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        raw = decoder.decompress(data, MAX_BODY_BYTES + 1)
        if len(raw) > MAX_BODY_BYTES or decoder.unconsumed_tail:
            raise SyncError("too_large", "Expanded peer request exceeds the bounded body size")
        if not decoder.eof or decoder.unused_data:
            raise SyncError("invalid_encoding", "Truncated or trailing compressed peer data")
    except zlib.error as exc:
        raise SyncError("invalid_encoding", "Invalid compressed peer request") from exc
    return decode_body(raw)


def _post(url: str, token: str, payload: dict[str, Any], timeout: float,
          retries: int, stop_event=None) -> dict[str, Any]:
    data = _encode(payload)
    encoding = os.environ.get("REFMEM_SYNC_REQUEST_ENCODING", "identity")
    if encoding not in {"identity", "gzip"}:
        raise SyncError("invalid_encoding", "Unknown configured peer request encoding")
    # Opt-in only after the destination has been upgraded; old peers remain valid.
    if encoding == "gzip":
        data = gzip.compress(data, compresslevel=6, mtime=0)
    for attempt in range(retries + 1):
        retry = False
        with _AttemptDeadline(timeout, stop_event) as deadline:
            handlers: list[Any] = [_NoRedirect(), _DeadlineHTTPHandler(deadline), _DeadlineHTTPSHandler(deadline)]
            if urllib.parse.urlsplit(url).scheme == "http":
                handlers.append(urllib.request.ProxyHandler({}))
            opener = urllib.request.build_opener(*handlers)
            request = urllib.request.Request(url, data=data, method="POST", headers={
                "Authorization": "Bearer " + token, "Content-Type": "application/json",
                "Accept": "application/json", "Connection": "close", "Content-Encoding": encoding,
            })
            try:
                with opener.open(request, timeout=deadline.check()) as response:
                    deadline.check()
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
                    deadline.check()
                    return decode_body(raw)
            except urllib.error.HTTPError as exc:
                deadline.check()
                code = exc.code
                retry_after = _retry_after(exc.headers.get("Retry-After"))
                error_code = reason = None
                try:
                    error = decode_body(exc.read(4097))
                    deadline.check()
                    if code in {429, 503} and error.get("error") in {"capacity_paused", "budget_pause"}:
                        error_code = error["error"]
                    if error.get("reason") in {"low_disk", "store_limit", "budget_exhausted"}:
                        reason = error["reason"]
                except (SyncError, OSError, http.client.HTTPException):
                    try:
                        deadline.check()
                    except SyncError as interrupted:
                        if interrupted.code != "cancelled" and (code == 429 or retry_after is not None):
                            raise SyncError("rate_limited" if code == 429 else "http_error",
                                            f"Peer exchange returned HTTP {code}",
                                            retry_after_seconds=retry_after, http_status=code) from None
                        raise
                finally:
                    exc.close()
                if error_code or code == 429 or retry_after is not None:
                    raise SyncError(error_code or ("rate_limited" if code == 429 else "http_error"),
                                    f"Peer exchange returned HTTP {code}", retry_after_seconds=retry_after,
                                    reason=reason, http_status=code) from None
                if code in {500, 502, 503, 504} and attempt < retries:
                    retry = True
                else:
                    raise SyncError("http_error", f"Peer exchange returned HTTP {code}", http_status=code) from None
            except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
                deadline.check()
                if attempt < retries:
                    retry = True
                else:
                    raise SyncError("transport_error", "Peer exchange could not complete") from None
        # Socket watchdog and DNS subprocess are joined/reaped before another
        # attempt can begin. No sleeping sender can overlap a retry.
        if retry:
            delay = 0.05 * 2**attempt
            if stop_event is not None:
                if stop_event.wait(delay):
                    raise SyncError("cancelled", "Synchronization cancelled")
            else:
                time.sleep(delay)
    raise AssertionError("unreachable")


def _retry_after(value: str | None) -> float | None:
    """Return a nonnegative server delay without treating malformed text as zero."""
    if not value or len(value) > 128:
        return None
    value = value.strip()
    if value.isascii() and value.isdecimal() and len(value) <= 12:
        return float(value)
    try:
        from email.utils import parsedate_to_datetime
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            return None
        return max(0.0, date.timestamp() - time.time())
    except (ValueError, TypeError, OverflowError):
        return None


def sync_once(store: Any, url: str, token: str, batch_size: int = 100, *,
              timeout: float = 10, max_rounds: int = 1000, retries: int = 2,
              expected_peer: str | None = None, stop_event=None, disk_guard=None) -> dict[str, Any]:
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
        if stop_event is not None and stop_event.is_set():
            raise SyncError("cancelled", "Synchronization cancelled")
        if disk_guard is not None:
            disk_guard()
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
        response = _post(endpoint, token, payload, timeout, retries, stop_event=stop_event)
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
        if stop_event is not None and stop_event.is_set():
            raise SyncError("cancelled", "Synchronization cancelled")
        if disk_guard is not None:
            disk_guard()
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


class SyncRunner:
    """One private, resumable scheduler for a persistent personal peer.

    Status is an observation and retry deadline, never a replication checkpoint.
    The Store's durable frontier is the only source of synchronization progress.
    A hard failure pauses this runner; explicitly restarting it permits one new
    attempt after the persisted deadline, for example after fixing a credential.
    """

    def __init__(self, store, config, *, stop_event=None, clock=None):
        import hashlib
        import pathlib
        import threading
        self.store = store
        self.clock = clock or time.time
        self.stop_event = stop_event or threading.Event()
        self._lock_fd = None
        self._paused = False
        if str(store.path) == ":memory:":
            raise SyncError("invalid_config", "Automatic sync requires a persistent store")
        base = pathlib.Path.cwd()
        config_path = None
        if isinstance(config, (str, pathlib.Path)):
            import os
            import stat
            path = pathlib.Path(config).resolve()
            config_path = path
            base = path.parent
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise SyncError("invalid_config", "Sync configuration must be a regular file")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    raw = stream.read(65537)
            finally:
                os.close(fd)
            if len(raw) > 65536:
                raise SyncError("invalid_config", "Sync configuration exceeds size limit")
            config = decode_body(raw)
        if not isinstance(config, dict):
            raise SyncError("invalid_config", "Sync configuration must be an object")
        allowed = {"version", "url", "expected_peer", "token_file", "status_file",
                   "interval_seconds", "max_backoff_seconds", "batch_size", "max_rounds",
                   "timeout_seconds", "min_free_bytes", "max_store_bytes"}
        if set(config) - allowed or type(config.get("version", 1)) is not int or config.get("version", 1) != 1:
            raise SyncError("invalid_config", "Unsupported sync configuration field or version")
        self.config = {"version": 1, "interval_seconds": 30, "max_backoff_seconds": 900,
                       "batch_size": 100, "max_rounds": 10, "timeout_seconds": 10,
                       "min_free_bytes": 512 * 1024 * 1024, "max_store_bytes": None, **config}
        self.config["url"] = _endpoint(self.config.get("url"))
        peer = self.config.get("expected_peer")
        if not isinstance(peer, str) or not peer or len(peer) > 256:
            raise SyncError("invalid_config", "An expected peer identity is required")
        for key in ("token_file", "status_file"):
            value = self.config.get(key)
            if not isinstance(value, str) or not value:
                raise SyncError("invalid_config", f"{key} is required")
            path = pathlib.Path(value).expanduser()
            self.config[key] = str(path if path.is_absolute() else base / path)
        status_path = pathlib.Path(self.config["status_file"]).resolve()
        db_path = pathlib.Path(store.path).resolve()
        protected = [db_path, pathlib.Path(str(db_path) + "-wal"), pathlib.Path(str(db_path) + "-shm"),
                     pathlib.Path(str(db_path) + ".sync.lock"), pathlib.Path(self.config["token_file"]).resolve()]
        if config_path is not None:
            protected.append(config_path)
        if any(status_path == path or status_path.exists() and path.exists() and status_path.samefile(path)
               for path in protected):
            raise SyncError("invalid_config", "Status file must be separate from the database, credentials and configuration")
        for key, low, high in (("interval_seconds", 5, 86400),
                               ("max_backoff_seconds", 5, 86400),
                               ("batch_size", 1, MAX_BATCH), ("max_rounds", 1, 1000),
                               ("timeout_seconds", 1, 60), ("min_free_bytes", 0, 2**63 - 1)):
            _integer(self.config[key], key, low, high)
        if self.config["max_backoff_seconds"] < self.config["interval_seconds"]:
            raise SyncError("invalid_config", "Maximum backoff must cover the normal interval")
        maximum = self.config["max_store_bytes"]
        if maximum is not None:
            _integer(maximum, "max_store_bytes", 1, 2**63 - 1)
        self.store.configure_capacity(min_free_bytes=self.config["min_free_bytes"],
                                      max_store_bytes=maximum)
        local = store.status()
        if peer == local["peer_id"]:
            raise SyncError("invalid_config", "The expected peer cannot be the local peer")
        identity = [local["store_id"], local["peer_id"], self.config["url"], peer]
        self.identity = hashlib.sha256(_encode(identity)).hexdigest()
        self.status = self._new_status()

    def _new_status(self):
        return {"version": 1, "identity": self.identity, "state": "waiting",
                "next_attempt_at": 0.0, "failures": 0, "last_attempt_at": None,
                "last_success_at": None, "last_error": None, "last_reason": None,
                "last_http_status": None, "last_result": None,
                "frontier": self.store.status()["frontier"]}

    @staticmethod
    def _private_bytes(path, maximum):
        import os
        import stat
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        try:
            fd = os.open(path, flags)
        except OSError as exc:
            raise SyncError("private_file_error", "Cannot open configured private file") from exc
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_size > maximum
                    or info.st_uid != os.geteuid()):
                raise SyncError("private_file_error", "Configured file must be private, regular and bounded")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                raw = stream.read(maximum + 1)
            if len(raw) > maximum:
                raise SyncError("private_file_error", "Configured private file exceeds size limit")
            return raw
        finally:
            os.close(fd)

    def _load_status(self):
        import pathlib
        path = pathlib.Path(self.config["status_file"])
        if not path.exists() and not path.is_symlink():
            self.status = self._new_status()
            return
        status = decode_body(self._private_bytes(path, 65536))
        if status.get("version") != 1 or status.get("identity") != self.identity:
            raise SyncError("status_identity_mismatch", "Sync status belongs to a different configuration")
        deadline = status.get("next_attempt_at")
        if (isinstance(deadline, bool) or not isinstance(deadline, (int, float))
                or not math.isfinite(deadline) or deadline < 0):
            raise SyncError("invalid_status", "Sync status has an invalid retry deadline")
        _integer(status.get("failures"), "failures", 0, 1000000)
        # Do not trust persisted frontier as authority; every resume reads Store.
        self.status = status
        self.status["frontier"] = self.store.status()["frontier"]

    def _write_status(self):
        import errno
        import os
        import pathlib
        import tempfile
        path = pathlib.Path(self.config["status_file"])
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            raise SyncError("private_file_error", "Sync status may not be a symbolic link")
        self.status["frontier"] = self.store.status()["frontier"]
        raw = _encode(self.status)
        fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
            directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                try:
                    os.fsync(directory)
                except OSError as exc:
                    if exc.errno not in {errno.EINVAL, errno.ENOTSUP}:
                        raise
            finally:
                os.close(directory)
        finally:
            pathlib.Path(name).unlink(missing_ok=True)

    def _acquire(self):
        import fcntl
        import os
        import stat
        if self._lock_fd is not None:
            return False
        fd = os.open(str(self.store.path) + ".sync.lock",
                     os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise SyncError("private_file_error", "Scheduler lock must be a regular file")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(fd)
            raise SyncError("runner_busy", "Another sync runner holds this store") from exc
        except BaseException:
            os.close(fd)
            raise
        self._lock_fd = fd
        return True

    def _release(self):
        import fcntl
        import os
        if self._lock_fd is not None:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            os.close(self._lock_fd)
            self._lock_fd = None

    def _disk_guard(self):
        import pathlib
        import shutil
        if shutil.disk_usage(pathlib.Path(self.store.path).parent).free < self.config["min_free_bytes"]:
            raise SyncError("capacity_paused", "Synchronization paused for local capacity",
                            retry_after_seconds=300, reason="low_disk")

    def _backoff(self, hint=None):
        failures = self.status["failures"]
        delay = min(self.config["max_backoff_seconds"],
                    self.config["interval_seconds"] * 2 ** min(max(0, failures - 1), 20))
        if isinstance(hint, (int, float)) and not isinstance(hint, bool) and math.isfinite(hint):
            delay = max(delay, hint)
        return delay

    def step(self):
        """Run at most one due, bounded cycle; early calls never bypass a deadline."""
        acquired = self._acquire()
        try:
            self._load_status()
            if self.stop_event.is_set():
                self.status["state"] = "stopped"
                self._write_status()
                return dict(self.status)
            # A clean stop belongs to the previous process. Resume its saved
            # retry deadline without treating that stop as a persistent pause.
            if self.status["state"] == "stopped":
                self.status["state"] = "backoff"
            if self._paused:
                return dict(self.status)
            if self.clock() < self.status["next_attempt_at"]:
                if self.status["state"] == "paused":
                    self.status["state"] = "backoff"
                return dict(self.status)
            now = self.clock()
            self.status.update(state="running", last_attempt_at=now,
                               next_attempt_at=now + self.config["interval_seconds"])
            # Reserve a minimum restart delay before sending any request. A
            # process death cannot turn a supervisor restart into a tight loop.
            self._write_status()
            try:
                raw = self._private_bytes(self.config["token_file"], 4096)
                try:
                    token = raw.decode("ascii").strip()
                except UnicodeError as exc:
                    raise SyncError("private_file_error", "Peer credential must be ASCII") from exc
                self._disk_guard()
                result = sync_once(self.store, self.config["url"], token,
                                   self.config["batch_size"], timeout=self.config["timeout_seconds"],
                                   max_rounds=self.config["max_rounds"], retries=0,
                                   expected_peer=self.config["expected_peer"],
                                   stop_event=self.stop_event, disk_guard=self._disk_guard)
                self.status["last_result"] = result
                self.status["last_error"] = None
                self.status["last_reason"] = None
                self.status["last_http_status"] = None
                if result["reason"] == "semantic_rejection":
                    self._paused = True
                    self.status.update(state="paused", last_error="semantic_rejection",
                                       failures=min(self.status["failures"] + 1, 1000000))
                elif result["complete"]:
                    self.status.update(state="waiting", failures=0, last_success_at=self.clock())
                else:
                    self.status.update(state="waiting", failures=0)
                self.status["next_attempt_at"] = self.clock() + self.config["interval_seconds"]
            except Exception as exc:
                code = getattr(exc, "code", "internal_error")
                if code == "cancelled":
                    self.status.update(state="stopped", last_error=None)
                else:
                    transient = (code in {"transport_error", "transport_timeout", "rate_limited", "capacity_paused", "budget_pause"}
                                 or code == "http_error" and getattr(exc, "http_status", None) in {429, 500, 502, 503, 504})
                    self._paused = not transient
                    self.status["failures"] = min(self.status["failures"] + 1, 1000000)
                    safe_code = code if code in {"transport_error", "transport_timeout", "rate_limited", "capacity_paused", "budget_pause",
                                                "http_error", "private_file_error", "invalid_token", "wrong_store",
                                                "wrong_peer", "unsupported_protocol", "invalid_response", "too_large"} else "internal_error"
                    self.status.update(state="backoff" if transient else "paused", last_error=safe_code,
                                       next_attempt_at=self.clock() + self._backoff(getattr(exc, "retry_after_seconds", None)))
                    reason = getattr(exc, "reason", None)
                    self.status["last_reason"] = reason if reason in {"low_disk", "store_limit", "budget_exhausted"} else None
                    http_status = getattr(exc, "http_status", None)
                    self.status["last_http_status"] = http_status if type(http_status) is int and 100 <= http_status <= 599 else None
            self._write_status()
            return dict(self.status)
        finally:
            if acquired:
                self._release()

    def run(self):
        """Run until cancelled or a hard error pauses it; waits are interruptible."""
        self._acquire()
        try:
            self._load_status()
            while not self.stop_event.is_set():
                status = self.step()
                if status["state"] in {"paused", "stopped"}:
                    return status
                delay = max(0.0, status["next_attempt_at"] - self.clock())
                self.stop_event.wait(min(delay, 60.0))
            self.status["state"] = "stopped"
            self._write_status()
            return dict(self.status)
        finally:
            self._release()
