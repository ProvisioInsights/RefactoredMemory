"""Synthetic HTTP interoperability and public resource-boundary tests."""
import asyncio
import importlib.util
import io
import json
import os
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from refactoredmemory.mcp import LEGACY_VERSION, META_PREFIX, PROTOCOL_VERSION, make_handler, run_stdio
from refactoredmemory.oauth import OAuthAuthenticationError, OAuthScopeError
from refactoredmemory.service import Service
from refactoredmemory.store import Store


def modern(method="tools/list", params=None, request_id=1):
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {
        **(params or {}), "_meta": {META_PREFIX + "protocolVersion": PROTOCOL_VERSION,
                                  META_PREFIX + "clientCapabilities": {}}}}


def initialize(version=LEGACY_VERSION):
    return {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": version, "capabilities": {},
        "clientInfo": {"name": "synthetic-client", "version": "1"}}}


class Metadata:
    metadata_path = "/.well-known/oauth-protected-resource/mcp"

    def resource_metadata(self):
        return {"resource": "https://memory.example/mcp",
                "authorization_servers": ["https://identity.example/realms/memory"],
                "bearer_methods_supported": ["header"],
                "scopes_supported": ["memory:read", "memory:write", "memory:correct"]}

    def www_authenticate(self, error=None, scope=None):
        result = 'Bearer resource_metadata="https://memory.example' + self.metadata_path + '"'
        if error:
            result += ', error="' + error + '"'
        if scope:
            result += ', scope="' + scope + '"'
        return result


@contextmanager
def running(service, **options):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service, **options))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def send(port, token, message=None, *, method="POST", path="/mcp", headers=None):
    base = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if token is not None:
        base["Authorization"] = "Bearer " + token
    if headers:
        base.update(headers)
    body = None if message is None else json.dumps(message)
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path, body, base)
        response = connection.getresponse()
        data = response.read()
        return response.status, dict(response.getheaders()), json.loads(data) if data else None
    finally:
        connection.close()


def modern_headers(method="tools/list", name=None):
    result = {"MCP-Protocol-Version": PROTOCOL_VERSION, "Mcp-Method": method}
    if name is not None:
        result["Mcp-Name"] = name
    return result


class HTTPProfileTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.token = self.store.create_grant("synthetic-writer", ["read", "write", "correct"])
        self.service = Service(self.store)

    def tearDown(self):
        self.store.close()

    def test_legacy_is_explicit_and_does_not_create_shared_session_state(self):
        with running(self.service) as port:
            self.assertEqual(send(port, self.token, initialize())[0], 400)
            self.assertEqual(send(port, self.token, modern(), headers=modern_headers())[0], 200)
        with running(self.service, allow_legacy_http=True) as port:
            status, headers, response = send(port, self.token, initialize())
            self.assertEqual(status, 200)
            self.assertEqual(response["result"]["protocolVersion"], LEGACY_VERSION)
            self.assertEqual(headers["MCP-Protocol-Version"], LEGACY_VERSION)
            self.assertNotIn("Mcp-Session-Id", headers)
            call = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            status, _, response = send(port, self.token, call, headers={"MCP-Protocol-Version": LEGACY_VERSION})
            self.assertEqual(status, 200)
            self.assertNotIn("resultType", response["result"])
            self.assertIn("memory_submit", [tool["name"] for tool in response["result"]["tools"]])
            self.assertEqual(send(port, self.token, call)[0], 400)
            # Compatibility does not become a connection/session default.
            status, _, response = send(port, self.token, modern(), headers=modern_headers())
            self.assertEqual(status, 200)
            self.assertEqual(response["result"]["resultType"], "complete")

    def test_no_downgrade_of_modern_metadata_and_version_or_header_mismatches(self):
        with running(self.service, allow_legacy_http=True) as port:
            self.assertEqual(send(port, self.token, initialize("2025-03-26"))[0], 400)
            self.assertEqual(send(port, self.token, modern(), headers={"MCP-Protocol-Version": LEGACY_VERSION})[0], 400)
            self.assertEqual(send(port, self.token, modern(), headers={**modern_headers(), "Mcp-Method": "tools/call"})[0], 400)
            call = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            self.assertEqual(send(port, self.token, call, headers={"MCP-Protocol-Version": "2000-01-01"})[0], 400)
            self.assertEqual(send(port, self.token, call, headers={"MCP-Protocol-Version": LEGACY_VERSION, "Mcp-Method": "tools/call"})[0], 400)
            for meta in (None, [], {META_PREFIX + "clientCapabilities": {}}):
                malformed = {**call, "params": {"_meta": meta}}
                self.assertEqual(send(port, self.token, malformed, headers={"MCP-Protocol-Version": LEGACY_VERSION})[0], 400)

    def test_notifications_and_malformed_methods_never_write(self):
        events = []
        with running(self.service, allow_legacy_http=True, audit=events.append) as port:
            message = {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "memory_submit", "arguments": {"actions": [{"type": "entity", "id": "forged", "entity_type": "project", "label": "Never write"}]}}}
            self.assertEqual(send(port, self.token, message, headers={"MCP-Protocol-Version": LEGACY_VERSION})[0], 202)
            self.assertIsNone(self.store.get_entity("forged"))
            for method in ({"bad": "method"}, ["tools/list"], None):
                message = {"jsonrpc": "2.0", "id": 1, "method": method}
                self.assertEqual(send(port, self.token, message, headers={"MCP-Protocol-Version": LEGACY_VERSION})[0], 400)
        self.assertEqual(len(events), 4)

    def test_metadata_is_public_exact_path_and_respects_host_and_origin(self):
        metadata = Metadata()
        with running(self.service, oauth=metadata) as port:
            status, headers, body = send(port, None, method="GET", path=metadata.metadata_path)
            self.assertEqual(status, 200)
            self.assertEqual(body, metadata.resource_metadata())
            self.assertEqual(headers["Cache-Control"], "no-store")
            status, headers, _ = send(port, None, modern(), headers=modern_headers())
            self.assertEqual(status, 401)
            self.assertIn('resource_metadata="https://memory.example/.well-known/oauth-protected-resource/mcp"', headers["WWW-Authenticate"])
            for path in ("/sync", "/admin", "/mcp?token=do-not-reflect", metadata.metadata_path + "?extra=1", "/.well-known/oauth-protected-resource"):
                self.assertEqual(send(port, self.token, method="GET", path=path)[0], 404)
                self.assertEqual(send(port, self.token, modern(), path=path)[0], 404)
            self.assertEqual(send(port, None, method="GET", path=metadata.metadata_path, headers={"Host": "attacker.example"})[0], 403)
            self.assertEqual(send(port, None, method="GET", path=metadata.metadata_path, headers={"Origin": "https://attacker.example"})[0], 403)
            self.assertEqual(send(port, None, modern(), path=metadata.metadata_path)[0], 404)
            status, headers, _ = send(port, None, method="DELETE", path=metadata.metadata_path)
            self.assertEqual(status, 405)
            self.assertEqual(headers["Allow"], "GET")

    def test_oauth_errors_become_resource_challenges_and_local_denials_remain_tool_errors(self):
        def auth(token, scope=None):
            if token != "synthetic-valid-access":
                raise OAuthAuthenticationError()
            if scope == "write":
                raise OAuthScopeError("memory:write")
            return self.store.authenticate(self.token, scope)

        service = Service(self.store, authenticate=auth)
        call = modern("tools/call", {"name": "memory_submit", "arguments": {"actions": [{"type": "entity", "id": "e", "entity_type": "project", "label": "Synthetic"}]}})
        with running(service, oauth=Metadata()) as port:
            status, headers, _ = send(port, "synthetic-invalid", modern(), headers=modern_headers())
            self.assertEqual(status, 401)
            self.assertIn('error="invalid_token"', headers["WWW-Authenticate"])
            status, headers, _ = send(port, "synthetic-valid-access", call, headers=modern_headers("tools/call", "memory_submit"))
            self.assertEqual(status, 403)
            self.assertIn('error="insufficient_scope"', headers["WWW-Authenticate"])
            self.assertIn('scope="memory:write"', headers["WWW-Authenticate"])
            self.assertIsNone(self.store.get_entity("e"))
        reader = self.store.create_grant("synthetic-reader", ["read"])
        with running(self.service) as port:
            status, headers, response = send(port, reader, call, headers=modern_headers("tools/call", "memory_submit"))
            self.assertEqual(status, 200)
            self.assertTrue(response["result"]["isError"])
            self.assertNotIn("WWW-Authenticate", headers)

    def test_audit_is_bounded_to_known_labels_and_never_records_input_or_token(self):
        events = []
        with running(self.service, audit=events.append) as port:
            send(port, self.token, modern(), headers=modern_headers())
            send(port, self.token, modern("private-method"), headers=modern_headers("private-method"))
            send(port, self.token, modern("tools/call", {"name": "private-tool", "arguments": {"secret": "private-body"}}), headers=modern_headers("tools/call", "private-tool"))
            send(port, self.token, method="GET", path="/mcp?token=private-query")
        self.assertEqual(len(events), 4)
        self.assertEqual(len({event["request_id"] for event in events}), 4)
        self.assertEqual(events[0]["grant_id"], self.store.authenticate(self.token)["id"])
        self.assertEqual(events[1]["method"], "unknown")
        self.assertEqual(events[2]["tool"], "unknown")
        self.assertEqual(events[3]["route"], "unknown")
        self.assertEqual(set(events[0]), {"event", "request_id", "route", "method", "tool", "grant_id", "status"})
        encoded = json.dumps(events)
        for secret in (self.token, "private-method", "private-tool", "private-body", "private-query"):
            self.assertNotIn(secret, encoded)

    def test_http_capacity_refusal_preserves_reads_and_allows_same_request_retry(self):
        arguments = {"request_id": "capacity-retry", "actions": [
            {"type": "entity", "id": "pending", "entity_type": "note", "label": "Synthetic pending note"}]}
        self.store.configure_capacity(max_store_bytes=1)
        with running(self.service) as port:
            status, headers, response = send(port, self.token, modern("tools/call", {
                "name": "memory_submit", "arguments": arguments}),
                headers=modern_headers("tools/call", "memory_submit"))
            self.assertEqual(status, 200)
            self.assertEqual(headers["Retry-After"], "300")
            self.assertTrue(response["result"]["isError"])
            self.assertEqual(response["result"]["structuredContent"], {
                "error": "capacity_paused", "reason": "store_limit", "retry_after_seconds": 300})
            self.assertIsNone(self.store.get_entity("pending"))
            self.assertEqual(self.store.status()["known_position"], 0)
            status, headers, response = send(port, self.token, modern("tools/call", {
                "name": "memory_status", "arguments": {}}),
                headers=modern_headers("tools/call", "memory_status"))
            self.assertEqual(status, 200)
            self.assertNotIn("Retry-After", headers)
            self.assertFalse(response["result"]["isError"])
            self.store.configure_capacity()
            status, _, response = send(port, self.token, modern("tools/call", {
                "name": "memory_submit", "arguments": arguments}),
                headers=modern_headers("tools/call", "memory_submit"))
            self.assertEqual(status, 200)
            self.assertFalse(response["result"]["isError"])
            self.assertIsNotNone(self.store.get_entity("pending"))

    def test_stdio_low_disk_refusal_is_a_structured_tool_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with Store(os.path.join(directory, "synthetic.sqlite")) as store:
                token = store.create_grant("capacity-test", ["read", "write"])
                store.configure_capacity(min_free_bytes=2 ** 62)
                request = modern("tools/call", {"name": "memory_submit", "arguments": {
                    "request_id": "low-disk-retry", "actions": [
                        {"type": "entity", "id": "pending", "entity_type": "note", "label": "Synthetic pending note"}]}})
                output = io.StringIO()
                run_stdio(Service(store), token,
                          input_stream=io.BytesIO((json.dumps(request) + "\n").encode()),
                          output_stream=output)
                response = json.loads(output.getvalue())
                self.assertTrue(response["result"]["isError"])
                self.assertEqual(response["result"]["structuredContent"], {
                    "error": "capacity_paused", "reason": "low_disk", "retry_after_seconds": 300})
                self.assertEqual(store.status()["known_position"], 0)

    @unittest.skipUnless(importlib.util.find_spec("mcp"), "Optional independent MCP SDK is not installed")
    def test_installed_sdk_streamable_http_capture_retry_query_and_evidence(self):
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with running(self.service, allow_legacy_http=True) as port:
            async def exercise():
                async with httpx.AsyncClient(headers={"Authorization": "Bearer " + self.token}) as client:
                    async with streamable_http_client(f"http://127.0.0.1:{port}/mcp", http_client=client) as (read, write, _):
                        async with ClientSession(read, write) as session:
                            result = await session.initialize()
                            self.assertEqual(result.protocolVersion, LEGACY_VERSION)
                            catalog = await session.list_tools()
                            self.assertIn("memory_submit", [tool.name for tool in catalog.tools])
                            arguments = {"request_id": "synthetic-http-capture", "actions": [
                                {"type": "entity", "id": "project", "entity_type": "project", "label": "Synthetic Northstar"},
                                {"type": "source", "id": "source", "uri": "synthetic:notes", "content": "Portable storage supports offline work."},
                                {"type": "assertion", "id": "decision", "subject": "project", "predicate": "decision", "value": "portable storage", "source_ids": ["source"], "valid_from": "2026-10-01"},
                            ]}
                            accepted = await session.call_tool("memory_submit", arguments)
                            self.assertFalse(accepted.isError)
                            retried = await session.call_tool("memory_submit", arguments)
                            self.assertTrue(retried.structuredContent["duplicate"])
                            queried = await session.call_tool("memory_query", {"subject": "project", "valid_at": "2026-10-03"})
                            self.assertEqual(queried.structuredContent["assertions"][0]["source_ids"], ["source"])
                            evidence = await session.call_tool("memory_source", {"source_id": "source"})
                            self.assertEqual(evidence.structuredContent["source"]["uri"], "synthetic:notes")
                            self.store.configure_capacity(max_store_bytes=1)
                            paused = await session.call_tool("memory_submit", {
                                "request_id": "capacity-sdk", "actions": [{"type": "entity", "id": "pending", "entity_type": "note", "label": "Pending"}]})
                            self.assertTrue(paused.isError)
                            self.assertEqual(paused.structuredContent, {
                                "error": "capacity_paused", "reason": "store_limit", "retry_after_seconds": 300})
                            self.assertIsNone(self.store.get_entity("pending"))
            asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
