"""Local owner administration and MCP/peer process entry points."""
from __future__ import annotations

import argparse
import contextlib
import ipaddress
import json
import os
from pathlib import Path
import ssl
import signal
import sys
import threading
from http.server import ThreadingHTTPServer
from socketserver import TCPServer
from urllib.parse import urlsplit

from .store import Store, MemoryError, AuthorizationError, ValidationError, CapacityError, canonical
from .service import Service
from .mcp import make_handler, run_stdio, decode_message
from .sync import MAX_BODY_BYTES, SyncError, decode_body, exchange, sync_once


def server_handler(service, *, allowed_origins=(), allowed_hosts=(), sync_only=False):
    base = make_handler(service, allowed_origins=allowed_origins, allowed_hosts=allowed_hosts)
    slots = threading.BoundedSemaphore(8)

    class Handler(base):
        def do_POST(self):
            if self.path != "/sync":
                if sync_only:
                    self._reply(404)
                    return
                return super().do_POST()
            self.connection.settimeout(15)
            # Reuse Host/Origin/TLS/duplicate-header protections on the peer endpoint.
            if not self._valid_endpoint("/sync"):
                return
            if not slots.acquire(blocking=False):
                self._reply(429, {"error": "busy"})
                return
            try:
                self._sync()
            except (TimeoutError, ConnectionError, OSError):
                self.close_connection = True
            finally:
                slots.release()

        def _sync(self):
            authorization = self.headers.get("Authorization", "")
            try:
                if not authorization.startswith("Bearer "):
                    raise AuthorizationError("Peer credential required")
                actor = service.store.authenticate(authorization[7:], "sync")
                if actor["kind"] != "peer" or not actor.get("peer_id"):
                    raise AuthorizationError("Peer credential required")
            except AuthorizationError:
                self._reply(401, {"error": "access_denied"})
                return
            length = self.headers.get("Content-Length", "")
            if self.headers.get("Transfer-Encoding") or not length.isascii() or not length.isdecimal() or len(length) > 10:
                self._reply(400, {"error": "invalid_length"})
                return
            if not 0 < int(length) <= MAX_BODY_BYTES:
                self._reply(413, {"error": "body_limit"})
                return
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                self._reply(415, {"error": "content_type"})
                return
            try:
                raw = self.rfile.read(int(length))
                if len(raw) != int(length):
                    raise ValidationError("Truncated request")
                result = exchange(service.store, decode_body(raw), actor["peer_id"])
                if len(canonical(result).encode()) > MAX_BODY_BYTES:
                    raise ValidationError("Response too large")
                self._reply(200, result)
            except AuthorizationError:
                self._reply(403, {"error": "origin_denied"})
            except CapacityError as exc:
                self._reply(503, {"error": exc.code, "reason": exc.reason,
                                  "retry_after_seconds": exc.retry_after_seconds},
                            response_headers={"Retry-After": str(exc.retry_after_seconds)})
            except (MemoryError, SyncError, ValueError):
                self._reply(400, {"error": "invalid_exchange"})
            except Exception:
                self._reply(500, {"error": "exchange_failed"})

        def do_GET(self):
            if not sync_only:
                return super().do_GET()
            if self._valid_endpoint("/sync"):
                self._reply(405)

        def _not_allowed(self):
            if not sync_only:
                return super()._not_allowed()
            if self._valid_endpoint("/sync"):
                self._reply(405)

        do_DELETE = _not_allowed
        do_OPTIONS = _not_allowed
        do_PUT = _not_allowed
        do_PATCH = _not_allowed
        do_HEAD = _not_allowed
    return Handler


class PeerHTTPServer(ThreadingHTTPServer):
    """Bound accepted connections before TLS/header parsing, not just tool calls."""
    daemon_threads = True

    def __init__(self, address, handler, tls_context=None):
        self.tls_context = tls_context
        self.connection_slots = threading.BoundedSemaphore(32)
        super().__init__(address, handler)

    def server_bind(self):
        # HTTPServer's default reverse DNS lookup can stall startup on a host
        # without working reverse resolution. Host policy uses explicit values.
        TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(15)
        if self.tls_context:
            try:
                connection = self.tls_context.wrap_socket(connection, server_side=True,
                                                           do_handshake_on_connect=False)
            except BaseException:
                connection.close()
                raise
        return connection, address

    def process_request(self, request, client_address):
        if not self.connection_slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.connection_slots.release()

    def handle_error(self, request, client_address):
        # No request data, bearer credentials or remote stack traces in logs.
        pass


@contextlib.contextmanager
def stop_signals(stop_event):
    """Signals only set an event; shutdown and database closure stay ordered."""
    previous = {}
    if threading.current_thread() is threading.main_thread():
        for number in (signal.SIGINT, signal.SIGTERM):
            previous[number] = signal.signal(number, lambda *_args: stop_event.set())
    try:
        yield
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


def _tls_context(cert_file, key_file):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    try:
        context.load_cert_chain(cert_file, key_file)
    except (OSError, ValueError):
        raise ValidationError("TLS certificate or private key is unavailable or invalid") from None
    return context


def _validate_audit_destination(path, protected_paths):
    """Do not append to or rotate a database, credential or trust file."""
    destination = Path(path)
    for candidate in (destination, destination.with_name(destination.name + ".1")):
        for protected in protected_paths:
            if candidate.resolve() == Path(protected).resolve():
                raise ValidationError("Audit destination conflicts with a protected runtime file")
            try:
                if candidate.samefile(protected):
                    raise ValidationError("Audit destination conflicts with a protected runtime file")
            except FileNotFoundError:
                pass


def serve_nas(store, args, *, stop_event=None):
    """A public OAuth resource and private sync listener sharing one Store."""
    from .oauth import OAuthAuthenticator
    from .audit import AuditLog
    event = stop_event or threading.Event()
    for port in (args.mcp_port, args.sync_port):
        if not 0 <= port <= 65535:
            raise ValidationError("Listener port must be 0–65535")
    if args.mcp_port and (args.mcp_host, args.mcp_port) == (args.sync_host, args.sync_port):
        raise ValidationError("MCP and sync require distinct listeners")
    store.configure_capacity(min_free_bytes=args.min_free_bytes, max_store_bytes=args.max_store_bytes)
    oauth = OAuthAuthenticator(store, args.oauth_config)
    contexts = [_tls_context(args.mcp_cert_file, args.mcp_key_file),
                _tls_context(args.sync_cert_file, args.sync_key_file)]
    # The resource authority was explicitly pinned in trusted local config.
    mcp_hosts = set(args.allow_host) | {urlsplit(oauth.resource).netloc}
    if args.audit_log:
        protected = [store.path + suffix for suffix in ("", "-wal", "-shm", "-journal")]
        protected += [args.mcp_cert_file, args.mcp_key_file, args.sync_cert_file, args.sync_key_file]
        protected += list(oauth.local_files)
        _validate_audit_destination(args.audit_log, protected)
    audit = AuditLog(args.audit_log) if args.audit_log else None
    servers, threads = [], []
    try:
        handlers = [
            make_handler(Service(store, authenticate=oauth), allowed_origins=args.allow_origin,
                         allowed_hosts=mcp_hosts, oauth=oauth,
                         allow_legacy_http=args.allow_legacy_http, audit=audit),
            server_handler(Service(store), allowed_origins=args.allow_origin,
                           allowed_hosts=args.allow_host, sync_only=True),
        ]
        for address, handler, context in zip(
                [(args.mcp_host, args.mcp_port), (args.sync_host, args.sync_port)], handlers, contexts):
            server = PeerHTTPServer(address, handler, context)
            # server_close must join accepted requests before the Store closes.
            server.daemon_threads = False
            servers.append(server)
        with stop_signals(event):
            for server in servers:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                threads.append(thread)
            print(canonical({"profile": "nas", "tls": True,
                             "mcp": {"listening": servers[0].server_address,
                                     "endpoints": ["/mcp", oauth.metadata_path]},
                             "sync": {"listening": servers[1].server_address,
                                      "endpoints": ["/sync"]}}), file=sys.stderr, flush=True)
            while not event.wait(0.5):
                if any(not thread.is_alive() for thread in threads):
                    raise ValidationError("A NAS listener stopped unexpectedly")
    finally:
        for server, thread in zip(servers, threads):
            if thread.is_alive():
                server.shutdown()
        for server in servers:
            server.server_close()
        for thread in threads:
            thread.join()
        if audit is not None:
            audit.close()


def load_json(value):
    raw = Path(value[1:]).read_bytes() if value.startswith("@") else value.encode()
    if len(raw) > 4 * 1024 * 1024:
        raise ValidationError("Input exceeds limit")
    try:
        return decode_message(raw)
    except (ValueError, UnicodeError):
        raise ValidationError("Invalid JSON input")


def token_value(args):
    token = Path(args.token_file).read_text().strip() if getattr(args, "token_file", None) else os.environ.get("REFACTOREDMEMORY_TOKEN", "")
    if not token:
        raise AuthorizationError("Use --token-file or REFACTOREDMEMORY_TOKEN")
    return token


def secret_file(path, value):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(value + "\n")
    return {"written": str(destination)}


def parser():
    p = argparse.ArgumentParser(description="Personal sourced temporal memory; local owner administration")
    p.add_argument("--db", default="memory.sqlite3", help="Local SQLite database; keep outside source control")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--store-id")
    init.add_argument("--peer-id")
    sub.add_parser("status")
    identity = sub.add_parser("identity", help="Export private pairing material into a new local file")
    identity.add_argument("--output", required=True)
    admit = sub.add_parser("peer-admit")
    admit.add_argument("--identity-file", required=True)
    revoke = sub.add_parser("peer-revoke")
    revoke.add_argument("peer_id")
    recovery = sub.add_parser("recovery-admit", help="Allow a paired restored peer to forward one original signed origin")
    recovery.add_argument("--sender", required=True)
    recovery.add_argument("--identity-file", required=True)
    grant = sub.add_parser("grant")
    grant.add_argument("--label", required=True)
    grant.add_argument("--scopes", required=True, help="Comma-separated read,write,correct,admin or peer-only sync")
    grant.add_argument("--kind", choices=["agent", "owner", "peer"], default="agent")
    grant.add_argument("--peer-id")
    grant.add_argument("--output", required=True, help="New private token file; token is never printed")
    rev = sub.add_parser("revoke")
    rev.add_argument("--token-file", required=True)
    call = sub.add_parser("call")
    call.add_argument("tool")
    call.add_argument("--args", default="{}", help="JSON or @file")
    call.add_argument("--token-file")
    submit = sub.add_parser("owner-submit", help="Explicit local owner assertions/corrections/admin actions")
    submit.add_argument("--actions", required=True, help="JSON action array or @file")
    submit.add_argument("--request-id")
    submit.add_argument("--min-free-bytes", type=int, default=536870912)
    submit.add_argument("--max-store-bytes", type=int)
    query = sub.add_parser("query")
    query.add_argument("--args", default="{}")
    hist = sub.add_parser("history")
    hist.add_argument("--args", default="{}")
    stdio = sub.add_parser("serve-stdio")
    stdio.add_argument("--token-file")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--cert-file")
    serve.add_argument("--key-file")
    serve.add_argument("--allow-origin", action="append", default=[])
    serve.add_argument("--allow-host", action="append", default=[])
    nas = sub.add_parser("serve-nas", help="Separate TLS OAuth MCP and private peer-sync listeners")
    nas.add_argument("--mcp-host", default="0.0.0.0")
    nas.add_argument("--mcp-port", type=int, default=8765)
    nas.add_argument("--mcp-cert-file", required=True)
    nas.add_argument("--mcp-key-file", required=True)
    nas.add_argument("--oauth-config", required=True)
    nas.add_argument("--sync-host", default="127.0.0.1")
    nas.add_argument("--sync-port", type=int, default=8766)
    nas.add_argument("--sync-cert-file", required=True)
    nas.add_argument("--sync-key-file", required=True)
    nas.add_argument("--allow-origin", action="append", default=[])
    nas.add_argument("--allow-host", action="append", default=[])
    nas.add_argument("--min-free-bytes", type=int, default=536870912)
    nas.add_argument("--max-store-bytes", type=int)
    nas.add_argument("--allow-legacy-http", action="store_true")
    nas.add_argument("--audit-log", help="Private bounded audit file; defaults to disabled")
    sync = sub.add_parser("sync")
    sync.add_argument("--url", required=True)
    sync.add_argument("--token-file")
    sync.add_argument("--expected-peer", required=True)
    sync.add_argument("--batch-size", type=int, default=100)
    watch = sub.add_parser("sync-watch", help="Run bounded, resumable synchronization until stopped")
    watch.add_argument("--config", required=True, help="Private local JSON scheduler configuration")
    backup = sub.add_parser("backup")
    backup.add_argument("destination")
    restore = sub.add_parser("restore")
    restore.add_argument("snapshot")
    restore.add_argument("destination")
    restore.add_argument("--peer-id")
    sub.add_parser("rebuild")
    imp = sub.add_parser("import", help="Read-only plan by default; only use approved source sets")
    imp.add_argument("path")
    imp.add_argument("--root", required=True)
    imp.add_argument("--namespace", default="personal-import")
    imp.add_argument("--apply", action="store_true")
    imp.add_argument("--backup")
    imp.add_argument("--min-free-bytes", type=int, default=536870912)
    imp.add_argument("--max-store-bytes", type=int)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "restore":
            with Store.restore(args.snapshot, args.destination, peer_id=args.peer_id) as restored:
                result = restored.status()
        else:
            # Planning an import must not create/change a destination database.
            if args.command == "import" and not args.apply:
                from .importers import plan_import
                plan = plan_import(args.path, approved_root=args.root, namespace=args.namespace)
                result = plan.summary()
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            with Store(args.db, store_id=getattr(args, "store_id", None), peer_id=getattr(args, "peer_id", None) if args.command == "init" else None) as store:
                service = Service(store)
                if args.command in {"init", "status"}:
                    result = store.status()
                elif args.command == "identity":
                    result = secret_file(args.output, canonical(store.identity()))
                elif args.command in {"peer-admit", "recovery-admit"}:
                    identity = load_json("@" + args.identity_file)
                    if identity["store_id"] != store.store_id:
                        raise ValidationError("Pairing material belongs to another store")
                    if args.command == "peer-admit":
                        store.admit_peer(identity["peer_id"], identity["key_hex"])
                    else:
                        store.admit_recovery_origin(args.sender, identity["peer_id"], identity["key_hex"])
                    result = {"admitted": identity["peer_id"]}
                elif args.command == "peer-revoke":
                    store.revoke_peer(args.peer_id)
                    result = {"revoked": args.peer_id}
                elif args.command == "grant":
                    if Path(args.output).exists():
                        raise ValidationError("Token output must be a new file")
                    token = store.create_grant(args.label, args.scopes.split(","), kind=args.kind, peer_id=args.peer_id)
                    try:
                        result = secret_file(args.output, token)
                    except BaseException:
                        store.revoke_grant(token)
                        raise
                elif args.command == "revoke":
                    store.revoke_grant(token_value(args))
                    result = {"revoked": True}
                elif args.command == "call":
                    result = service.call(args.tool, load_json(args.args), token_value(args))
                elif args.command == "owner-submit":
                    store.configure_capacity(min_free_bytes=args.min_free_bytes, max_store_bytes=args.max_store_bytes)
                    result = store.submit(load_json(args.actions), request_id=args.request_id)
                elif args.command == "query":
                    result = store.query(**load_json(args.args))
                elif args.command == "history":
                    result = store.history(**load_json(args.args))
                elif args.command == "serve-stdio":
                    run_stdio(service, token_value(args))
                    return 0
                elif args.command == "serve-nas":
                    serve_nas(store, args)
                    return 0
                elif args.command == "sync-watch":
                    from .sync import SyncRunner
                    stopped = threading.Event()
                    with stop_signals(stopped):
                        result = SyncRunner(store, args.config, stop_event=stopped).run()
                elif args.command == "serve":
                    try:
                        loopback = ipaddress.ip_address(args.host).is_loopback
                    except ValueError:
                        loopback = args.host == "localhost"
                    if not loopback and not (args.cert_file and args.key_file):
                        raise ValidationError("Non-loopback listeners require TLS certificate and key")
                    if bool(args.cert_file) != bool(args.key_file):
                        raise ValidationError("TLS certificate and key must be supplied together")
                    context = None
                    if args.cert_file:
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                        context.minimum_version = ssl.TLSVersion.TLSv1_2
                        context.load_cert_chain(args.cert_file, args.key_file)
                    server = PeerHTTPServer((args.host, args.port), server_handler(service, allowed_origins=args.allow_origin, allowed_hosts=args.allow_host), context)
                    print(canonical({"listening": server.server_address, "tls": bool(args.cert_file), "endpoints": ["/mcp", "/sync"]}), file=sys.stderr)
                    try:
                        server.serve_forever()
                    finally:
                        server.server_close()
                    return 0
                elif args.command == "sync":
                    result = sync_once(store, args.url, token_value(args), batch_size=args.batch_size, expected_peer=args.expected_peer)
                elif args.command == "backup":
                    result = store.backup(args.destination)
                elif args.command == "rebuild":
                    result = store.rebuild()
                elif args.command == "import":
                    if not args.backup:
                        raise ValidationError("Applying an import requires --backup to a new path")
                    store.configure_capacity(min_free_bytes=args.min_free_bytes, max_store_bytes=args.max_store_bytes)
                    from .importers import import_path
                    result = import_path(store, args.path, approved_root=args.root, namespace=args.namespace, dry_run=False, backup_path=args.backup)
                else:
                    raise ValidationError("Unknown command")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "import" and result.get("status") in {"failed", "partial"}:
            return 2
        return 0
    except (MemoryError, SyncError, ValueError, OSError, KeyError) as exc:
        print(f"RefactoredMemory: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
