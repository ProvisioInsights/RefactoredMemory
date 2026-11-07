"""Synthetic protocol tests; optional installed SDK exercises a real client."""
import asyncio
import base64
import importlib.util
import io
import json
import os
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.client import HTTPConnection, HTTPSConnection
from http.server import ThreadingHTTPServer

from refactoredmemory.mcp import (
    Dispatcher, LEGACY_VERSION, META_PREFIX, PROTOCOL_VERSION,
    decode_message, make_handler, run_stdio, validate_http_headers,
)


def request(method="server/discover", params=None, request_id=1, version=PROTOCOL_VERSION):
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {
        **(params or {}), "_meta": {META_PREFIX + "protocolVersion": version,
                                  META_PREFIX + "clientCapabilities": {}}}}


class FakeService:
    """No real user data or credentials; graph semantics tested elsewhere."""
    def __init__(self):
        self.calls = []
        self.revoked = set()
        self.started, self.release = threading.Event(), threading.Event()

    def authenticate(self, token):
        if token not in ("synthetic-writer", "synthetic-reader") or token in self.revoked:
            raise PermissionError("private-token-must-not-leak")
        return {"kind": "agent", "id": token}

    def tools(self):
        return [{"name": "capture", "description": "Synthetic capture", "inputSchema": {
            "type": "object", "properties": {"value": {"type": "string"}},
            "required": ["value"], "additionalProperties": False}}]

    def call(self, name, arguments, token):
        self.authenticate(token)
        if token == "synthetic-reader":
            raise PermissionError("private-grant-detail")
        if set(arguments) != {"value"} or not isinstance(arguments["value"], str):
            raise ValueError("private-input-content")
        if arguments["value"] == "block":
            self.started.set()
            self.release.wait(3)
        self.calls.append(arguments)
        return {"saved": arguments["value"], "verified": False}


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.dispatcher = Dispatcher(self.service)

    def dispatch(self, message, token="synthetic-writer"):
        return self.dispatcher.dispatch(message, token)

    def test_modern_discovery_and_direct_call_without_handshake(self):
        result = self.dispatch(request())["result"]
        self.assertEqual(result["supportedVersions"], [PROTOCOL_VERSION])
        self.assertEqual(result["resultType"], "complete")
        self.assertEqual(result["cacheScope"], "private")
        self.assertEqual(result["ttlMs"], 0)
        self.assertEqual(result["capabilities"], {"tools": {}})
        self.assertIn(META_PREFIX + "serverInfo", result["_meta"])
        self.assertIn("Proactively", result["instructions"])
        called = self.dispatch(request("tools/call", {"name": "capture", "arguments": {"value": "a decision"}}))
        self.assertFalse(called["result"]["isError"])
        self.assertEqual(called["result"]["structuredContent"], {"saved": "a decision", "verified": False})

    def test_metadata_required_per_request_and_client_info_optional(self):
        self.dispatch(request())
        plain = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        self.assertEqual(self.dispatch(plain)["error"]["code"], -32602)
        missing_cap = request()
        missing_cap["params"]["_meta"].pop(META_PREFIX + "clientCapabilities")
        self.assertEqual(self.dispatch(missing_cap)["error"]["code"], -32602)
        self.assertIn("result", self.dispatch(request("tools/list")))

    def test_unsupported_version_and_method(self):
        error = self.dispatch(request(version="1900-01-01"))["error"]
        self.assertEqual(error["code"], -32022)
        self.assertEqual(error["data"]["supported"], [PROTOCOL_VERSION])
        self.assertEqual(self.dispatch(request("made/up"))["error"]["code"], -32601)
        self.assertEqual(self.dispatch(request("tools/list", {"cursor": "stale"}))["error"]["code"], -32602)

    def test_tools_errors_authority_and_revocation(self):
        invalid = self.dispatch(request("tools/call", {"name": "capture", "arguments": {}}))
        self.assertTrue(invalid["result"]["isError"])
        self.assertNotIn("private-input-content", json.dumps(invalid))
        denied = self.dispatch(request("tools/call", {"name": "capture", "arguments": {"value": "claim"}}), "synthetic-reader")
        self.assertTrue(denied["result"]["isError"])
        self.assertEqual(denied["result"]["structuredContent"]["error"], "access_denied")
        self.assertEqual(self.dispatch(request(), "bad")["error"]["code"], 403)
        self.service.revoked.add("synthetic-writer")
        self.assertEqual(self.dispatch(request("tools/list"))["error"]["code"], 403)

    def test_invalid_requests_and_notifications_have_no_side_effect(self):
        for message in [[], None, "x", {"jsonrpc": "2.0", "id": True, "method": "tools/list"},
                        {"jsonrpc": "2.0", "id": None, "method": "tools/list"},
                        {"jsonrpc": "2.0", "id": 1, "result": {}},
                        {"jsonrpc": "2.0", "id": 1.5, "method": "tools/list"}]:
            self.assertEqual(self.dispatch(message)["error"]["code"], -32600)
        notification = request("tools/call", {"name": "capture", "arguments": {"value": "no"}})
        notification.pop("id")
        self.assertIsNone(self.dispatch(notification))
        self.assertEqual(self.service.calls, [])

    def test_strict_json(self):
        for value in ['{"a":1,"a":2}', '{"v":NaN}', '{"v":Infinity}', '{']:
            with self.assertRaises(ValueError):
                decode_message(value)

    def test_legacy_stdio_is_explicit_and_does_not_weaken_modern_requests(self):
        dispatcher = Dispatcher(self.service, legacy_stdio=True)
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": LEGACY_VERSION, "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"}}}
        self.assertEqual(dispatcher.dispatch(init, "synthetic-writer")["result"]["protocolVersion"], LEGACY_VERSION)
        self.assertIn("tools", dispatcher.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, "synthetic-writer")["result"])
        self.assertEqual(dispatcher.dispatch(request(version="wrong"), "synthetic-writer")["error"]["code"], -32022)
        malformed_modern = request()
        malformed_modern["params"]["_meta"].pop(META_PREFIX + "protocolVersion")
        self.assertEqual(dispatcher.dispatch(malformed_modern, "synthetic-writer")["error"]["code"], -32602)
        self.assertEqual(self.dispatch(init)["error"]["code"], -32602)

    def test_http_header_mirror_and_base64(self):
        message = request("tools/call", {"name": "memory.知识", "arguments": {}})
        encoded = "=?base64?" + base64.b64encode("memory.知识".encode()).decode() + "?="
        headers = {"MCP-Protocol-Version": PROTOCOL_VERSION, "Mcp-Method": "tools/call", "Mcp-Name": encoded}
        validate_http_headers(message, headers)
        for field in headers:
            bad = {**headers, field: "mismatch"}
            with self.assertRaises(ValueError):
                validate_http_headers(message, bad)

    def test_stdio_framing_parse_failure_then_recovery(self):
        source = io.BytesIO(("not-json\n" + json.dumps(request()) + "\n").encode())
        output = io.StringIO()
        run_stdio(self.service, "synthetic-writer", input_stream=source, output_stream=output)
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(replies[0]["error"]["code"], -32700)
        self.assertEqual(replies[1]["result"]["supportedVersions"], [PROTOCOL_VERSION])

    def test_stdio_cancellation_suppresses_inflight_response(self):
        read_fd, write_fd = os.pipe()
        output = io.StringIO()
        with os.fdopen(read_fd, "rb") as source, os.fdopen(write_fd, "wb", buffering=0) as writer:
            thread = threading.Thread(target=run_stdio, args=(self.service, "synthetic-writer"),
                                      kwargs={"input_stream": source, "output_stream": output})
            thread.start()
            writer.write((json.dumps(request("tools/call", {"name": "capture", "arguments": {"value": "block"}}, 99)) + "\n").encode())
            self.assertTrue(self.service.started.wait(2))
            writer.write(b'{"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":99}}\n')
            # A following discovery establishes that the reader consumed cancel.
            writer.write((json.dumps(request(request_id=100)) + "\n").encode())
            deadline = time.monotonic() + 2
            while '"id":100' not in output.getvalue() and time.monotonic() < deadline:
                time.sleep(.01)
            self.service.release.set()
            writer.close()
            thread.join(3)
            self.assertFalse(thread.is_alive())
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["id"] for r in replies], [100])


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.service))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def send(self, message=None, headers=None, method="POST"):
        message = request() if message is None else message
        h = {"Authorization": "Bearer synthetic-writer", "Content-Type": "application/json",
             "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL_VERSION,
             "Mcp-Method": message.get("method", "") if isinstance(message, dict) else ""}
        if isinstance(message, dict) and message.get("method") == "tools/call":
            h["Mcp-Name"] = message.get("params", {}).get("name", "")
        h.update(headers or {})
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request(method, "/mcp", body=json.dumps(message), headers=h)
        response = connection.getresponse()
        body = response.read()
        result = (response.status, json.loads(body) if body else None)
        connection.close()
        return result

    def test_modern_http_end_to_end(self):
        status, body = self.send()
        self.assertEqual(status, 200)
        self.assertEqual(body["result"]["resultType"], "complete")
        status, body = self.send(request("tools/call", {"name": "capture", "arguments": {"value": "source-linked"}}))
        self.assertEqual(status, 200)
        self.assertEqual(body["result"]["structuredContent"]["saved"], "source-linked")

    def test_headers_origin_auth_and_obsolete_verbs(self):
        for headers, status in [({"Mcp-Method": "wrong"}, 400), ({"MCP-Protocol-Version": "wrong"}, 400),
                                ({"Origin": "https://attacker.invalid"}, 403), ({"Host": "attacker.invalid"}, 403),
                                ({"Authorization": "Bearer revoked"}, 401), ({"Accept": "application/json"}, 406),
                                ({"Accept": "application/json, text/event-stream;q=0"}, 406)]:
            observed, body = self.send(headers=headers)
            self.assertEqual(observed, status)
            self.assertNotIn("private-", json.dumps(body))
        for method in ("GET", "DELETE", "OPTIONS"):
            self.assertEqual(self.send(method=method)[0], 405)
        self.assertEqual(self.service.calls, [])

    def test_http_statuses_version_method_notification(self):
        status, body = self.send(request(version="wrong"), {"MCP-Protocol-Version": "wrong"})
        self.assertEqual((status, body["error"]["code"]), (400, -32022))
        status, body = self.send(request("unknown"))
        self.assertEqual((status, body["error"]["code"]), (404, -32601))
        notice = {"jsonrpc": "2.0", "method": "notifications/ignored"}
        self.assertEqual(self.send(notice), (202, None))
        self.assertEqual(self.send([])[1]["error"]["code"], -32600)
        missing = {"jsonrpc": "2.0", "id": 10, "method": "tools/list", "params": {}}
        self.assertEqual(self.send(missing)[1]["error"]["code"], -32602)


class RealStoreHTTPTests(unittest.TestCase):
    def test_modern_http_sourced_capture_query_matches_direct_store(self):
        from refactoredmemory.store import Store
        from refactoredmemory.service import Service

        with tempfile.TemporaryDirectory() as tmp, Store(os.path.join(tmp, "memory.sqlite")) as store:
            token = store.create_grant("synthetic HTTP writer", ["read", "write"])
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(Service(store)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                def call(name, arguments):
                    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                    message = request("tools/call", {"name": name, "arguments": arguments})
                    connection.request("POST", "/mcp", json.dumps(message), {
                        "Authorization": "Bearer " + token, "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL_VERSION,
                        "Mcp-Method": "tools/call", "Mcp-Name": name,
                    })
                    response = connection.getresponse()
                    result = json.loads(response.read())
                    connection.close()
                    self.assertEqual(response.status, 200)
                    self.assertFalse(result["result"]["isError"])
                    return result["result"]["structuredContent"]

                call("memory_submit", {"request_id": "modern-capture", "actions": [
                    {"type": "entity", "id": "person", "entity_type": "person", "label": "Synthetic Rae"},
                    {"type": "source", "id": "meeting", "uri": "synthetic:meeting", "content": "Met Rae at the project review."},
                    {"type": "assertion", "id": "context", "subject": "person", "predicate": "met_at",
                     "value": "project review", "source_ids": ["meeting"], "valid_from": "2026-10-01",
                     "provenance": {"mode": "inferred", "model": "synthetic"}},
                ]})
                result = call("memory_query", {"subject": "person", "valid_at": "2026-10-02"})
                direct = store.query(subject="person", valid_at="2026-10-02")
                self.assertEqual(result, direct)
                self.assertEqual(result["assertions"][0]["source_ids"], ["meeting"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


class ConnectionTimeoutTests(unittest.TestCase):
    def test_incomplete_headers_expire_before_do_post(self):
        from refactoredmemory.cli import PeerHTTPServer

        handler = make_handler(FakeService())
        handler.request_timeout = .15
        server = PeerHTTPServer(("127.0.0.1", 0), handler)
        errors = []
        server.handle_error = lambda *_: errors.append("unexpected handler failure")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as client:
                client.sendall(b"POST /mcp HTTP/1.1\r\nHost: ")
                self.assertEqual(client.recv(1024), b"")
            self.assertEqual(errors, [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


@unittest.skipUnless(shutil.which("openssl"), "OpenSSL is required only to generate synthetic TLS test certificates")
class TLSConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.cert = os.path.join(cls.temporary.name, "synthetic-cert.pem")
        cls.key = os.path.join(cls.temporary.name, "synthetic-key.pem")
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", cls.key, "-out", cls.cert, "-days", "1", "-subj", "/CN=localhost",
            "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=15)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def start_server(self, timeout=2):
        from refactoredmemory.cli import PeerHTTPServer

        handler = make_handler(FakeService())
        handler.request_timeout = timeout
        self.entered = threading.Event()
        original_setup = handler.setup

        def observed_setup(instance):
            self.entered.set()
            original_setup(instance)

        handler.setup = observed_setup
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(self.cert, self.key)
        self.server = PeerHTTPServer(("127.0.0.1", 0), handler, tls_context=context)
        self.errors = []
        self.server.handle_error = lambda *_: self.errors.append("unexpected handler failure")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        if hasattr(self, "server"):
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()

    def test_idle_tls_client_does_not_block_second_verified_tls_request(self):
        self.start_server(timeout=2)
        with socket.create_connection(self.server.server_address, timeout=3) as idle:
            self.assertTrue(self.entered.wait(1))
            # A listening-socket handshake would block this second request until
            # the idle client times out. The production server hands it off.
            context = ssl.create_default_context(cafile=self.cert)
            client = HTTPSConnection("127.0.0.1", self.server.server_port, timeout=1, context=context)
            client.request("POST", "/mcp", json.dumps(request()), {
                "Authorization": "Bearer synthetic-writer", "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL_VERSION,
                "Mcp-Method": "server/discover",
            })
            response = client.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["result"]["supportedVersions"], [PROTOCOL_VERSION])
            client.close()
            self.assertEqual(idle.recv(1024), b"")
        self.assertEqual(self.errors, [])

    def test_malformed_tls_is_closed_without_handler_traceback(self):
        self.start_server(timeout=.2)
        with socket.create_connection(self.server.server_address, timeout=2) as client:
            client.sendall(b"not a TLS handshake\n")
            try:
                self.assertEqual(client.recv(1024), b"")
            except ConnectionResetError:
                pass
        self.assertEqual(self.errors, [])


@unittest.skipUnless(importlib.util.find_spec("mcp"), "Independent MCP Python SDK is not installed")
class IndependentSDKTests(unittest.TestCase):
    def test_installed_client_initializes_lists_and_calls_stdio(self):
        # This is the actual independently maintained SDK, not our own wire client.
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        script = ("import sys; sys.path.insert(0, 'tests'); "
                  "from test_mcp import FakeService; "
                  "from refactoredmemory.mcp import run_stdio; "
                  "run_stdio(FakeService(), 'synthetic-writer')")

        async def exercise():
            params = StdioServerParameters(command=sys.executable, args=["-c", script], cwd=os.getcwd())
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    self.assertEqual(initialized.protocolVersion, LEGACY_VERSION)
                    listed = await session.list_tools()
                    self.assertEqual([t.name for t in listed.tools], ["capture"])
                    result = await session.call_tool("capture", {"value": "independent client"})
                    self.assertFalse(result.isError)
                    self.assertEqual(result.structuredContent["saved"], "independent client")
                    bad = await session.call_tool("capture", {"extra": "invalid"})
                    self.assertTrue(bad.isError)

        asyncio.run(exercise())

    def test_independent_sdk_real_store_capture_evidence_history_and_grants(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from refactoredmemory.store import Store

        script = (
            "import os; from refactoredmemory.store import Store; "
            "from refactoredmemory.service import Service; "
            "from refactoredmemory.mcp import run_stdio; "
            "store=Store(os.environ['MEMORY_TEST_DB']); "
            "run_stdio(Service(store), os.environ['MEMORY_TEST_TOKEN']); store.close()"
        )
        actions = [
            {"type": "entity", "id": "project", "entity_type": "project", "label": "Synthetic Northstar"},
            {"type": "source", "id": "notes", "uri": "synthetic:decision", "content": "Use portable storage to support offline work."},
            {"type": "assertion", "id": "decision", "subject": "project", "predicate": "decision",
             "value": "portable storage", "source_ids": ["notes"], "valid_from": "2026-10-01",
             "provenance": {"mode": "inferred", "model": "synthetic-model"}, "uncertainty": "inferred"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "memory.sqlite")
            with Store(path) as store:
                writer = store.create_grant("synthetic writer", ["read", "write", "correct"])
                reader = store.create_grant("synthetic reader", ["read"])
                owner = store.create_grant("synthetic owner", ["read", "write", "correct"], kind="owner")

                async def exercise():
                    def parameters(token):
                        return StdioServerParameters(command=sys.executable, args=["-c", script], cwd=os.getcwd(),
                                                     env={"MEMORY_TEST_DB": path, "MEMORY_TEST_TOKEN": token})
                    async with stdio_client(parameters(writer)) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            tools = await session.list_tools()
                            self.assertIn("memory_submit", [t.name for t in tools.tools])
                            submitted = await session.call_tool("memory_submit", {"actions": actions, "request_id": "sdk-capture"})
                            self.assertFalse(submitted.isError)
                            retry = await session.call_tool("memory_submit", {"actions": actions, "request_id": "sdk-capture"})
                            self.assertTrue(retry.structuredContent["duplicate"])
                            result = await session.call_tool("memory_query", {"subject": "project", "valid_at": "2026-10-10"})
                            self.assertFalse(result.isError)
                            self.assertEqual(result.structuredContent["assertions"][0]["source_ids"], ["notes"])
                            evidence = await session.call_tool("memory_source", {"source_id": "notes"})
                            self.assertEqual(evidence.structuredContent["source"]["uri"], "synthetic:decision")
                            history = await session.call_tool("memory_history", {"entity_id": "project", "since": 0})
                            self.assertFalse(history.isError)
                            forged = await session.call_tool("memory_submit", {"actions": [
                                {**actions[-1], "id": "forged", "actor": {"id": "owner", "kind": "owner"}}]})
                            self.assertTrue(forged.isError)
                            async with stdio_client(parameters(owner)) as (owner_read, owner_write):
                                async with ClientSession(owner_read, owner_write) as owner_session:
                                    await owner_session.initialize()
                                    corrected = await owner_session.call_tool("memory_submit", {"actions": [
                                        {**actions[-1], "id": "owner-fix", "kind": "correct",
                                         "predecessors": ["decision"], "reason": "Owner supplied correction",
                                         "value": "SQLite", "provenance": {"mode": "owner_statement"}}
                                    ], "request_id": "sdk-owner-correction"})
                                    self.assertFalse(corrected.isError)
                            later = await session.call_tool("memory_submit", {"actions": [
                                {**actions[-1], "id": "later-inference", "kind": "correct",
                                 "predecessors": ["owner-fix"], "reason": "New synthetic inferred evidence",
                                 "value": "another database"}
                            ], "request_id": "sdk-inferred-conflict"})
                            self.assertFalse(later.isError)
                            conflict = await session.call_tool("memory_query", {"subject": "project"})
                            rows = conflict.structuredContent["assertions"]
                            self.assertEqual({r["id"] for r in rows}, {"owner-fix", "later-inference"})
                            self.assertTrue(next(r for r in rows if r["id"] == "owner-fix")["preferred"])
                    async with stdio_client(parameters(reader)) as (read, write):
                        async with ClientSession(read, write) as session:
                            await session.initialize()
                            denied = await session.call_tool("memory_submit", {"actions": actions})
                            self.assertTrue(denied.isError)
                            query = await session.call_tool("memory_query", {"subject": "project"})
                            self.assertFalse(query.isError)
                            self.assertEqual(len(query.structuredContent["assertions"]), 2)

                asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
