"""Absolute inbound I/O budgets resist synthetic slow-drip connections."""
from __future__ import annotations

import contextlib
from http.client import HTTPConnection, HTTPSConnection
import json
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest

from refactoredmemory.cli import PeerHTTPServer, server_handler
from refactoredmemory.service import Service
from refactoredmemory.store import Store, ValidationError


VERSION = "2026-07-28"
PREFIX = "io.modelcontextprotocol/"


class RequestDeadlineTests(unittest.TestCase):
    @contextlib.contextmanager
    def listener(self, *, tls_context=None, budget=0.4, max_connections=1):
        store = Store(":memory:")
        token = store.create_grant("Synthetic deadline reader", ["read"])
        handler = server_handler(Service(store))
        entered = threading.Event()
        original_setup = handler.setup

        def observed_setup(instance):
            entered.set()
            original_setup(instance)

        handler.setup = observed_setup
        server = PeerHTTPServer(("127.0.0.1", 0), handler, tls_context=tls_context,
                                request_deadline_seconds=budget, max_connections=max_connections)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
        thread.start()
        try:
            yield SimpleNamespace(server=server, port=server.server_port, token=token, entered=entered,
                                  thread=thread, store=store)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertFalse(server._deadline_thread.is_alive())
            self.assertFalse(server._request_deadlines)
            store.close()

    def healthy(self, listener, *, context=None):
        self.assertTrue(listener.server.connection_slots.acquire(timeout=1), "Connection slot was not released")
        listener.server.connection_slots.release()
        connection = (HTTPSConnection("127.0.0.1", listener.port, timeout=2, context=context)
                      if context is not None else HTTPConnection("127.0.0.1", listener.port, timeout=2))
        message = {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {
            "_meta": {PREFIX + "protocolVersion": VERSION, PREFIX + "clientCapabilities": {}}}}
        connection.request("POST", "/mcp", json.dumps(message), {
            "Authorization": "Bearer " + listener.token,
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": VERSION, "Mcp-Method": "server/discover"})
        response = connection.getresponse()
        body = response.read()
        connection.close()
        self.assertEqual(response.status, 200, body)
        self.assertTrue(listener.server.connection_slots.acquire(timeout=1), "Healthy request did not release its slot")
        listener.server.connection_slots.release()

    @contextlib.contextmanager
    def dripping(self, listener, initial, remainder=b"x" * 4096):
        sock = socket.create_connection(("127.0.0.1", listener.port), timeout=2)
        sock.sendall(initial)
        self.assertTrue(listener.entered.wait(1), "The request worker did not start")
        stop = threading.Event()

        def feed():
            for byte in remainder:
                if stop.wait(0.02):
                    return
                try:
                    sock.sendall(bytes([byte]))
                except OSError:
                    return

        thread = threading.Thread(target=feed, daemon=True)
        thread.start()
        try:
            yield sock
        finally:
            stop.set()
            sock.close()
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())

    def assert_closed_promptly(self, sock):
        started = time.monotonic()
        try:
            data = sock.recv(8192)
        except (ConnectionError, OSError) as error:
            self.assertNotIsInstance(error, TimeoutError)
            data = b""
        self.assertEqual(data, b"")
        self.assertLess(time.monotonic() - started, 1.3)

    def test_slow_headers_expire_despite_regular_byte_arrivals(self):
        with self.listener() as listener:
            with self.dripping(listener, b"POST /mcp HTTP/1.1\r\nX-Drip: ") as sock:
                self.assert_closed_promptly(sock)
            self.healthy(listener)
            self.assertEqual(listener.server.connection_slots._value, 1)

    def test_slow_body_expires_and_next_client_can_use_the_released_slot(self):
        with self.listener() as listener:
            headers = (f"POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{listener.port}\r\n"
                       f"Authorization: Bearer {listener.token}\r\n"
                       "Content-Type: application/json\r\nContent-Length: 4096\r\n"
                       "Accept: application/json, text/event-stream\r\n"
                       f"MCP-Protocol-Version: {VERSION}\r\nMcp-Method: server/discover\r\n\r\n")
            with self.dripping(listener, headers.encode(), remainder=b" " * 4096) as sock:
                self.assert_closed_promptly(sock)
            self.healthy(listener)

    def test_independent_listener_pools_and_shutdown_join_are_bounded(self):
        with self.listener(budget=0.8) as public, self.listener() as private:
            with self.dripping(public, b"POST /mcp HTTP/1.1\r\nX-Drip: "):
                # Filling a public slot cannot consume a different listener's
                # pool. No shared semaphore exists between MCP and private sync.
                self.assertEqual(public.server.connection_slots._value, 0)
                self.healthy(private)
                started = time.monotonic()
                public.server.shutdown()
                public.server.server_close()
                self.assertLess(time.monotonic() - started, 1.5)
                self.assertFalse(public.server._deadline_thread.is_alive())
                self.assertFalse(public.server._request_deadlines)
                self.assertEqual(public.server.connection_slots._value, 1)

    def test_invalid_resource_budgets_fail_before_opening_a_listener(self):
        for kwargs in ({"request_deadline_seconds": 0}, {"request_deadline_seconds": float("nan")},
                       {"request_deadline_seconds": True}, {"max_connections": 0}, {"max_connections": True}):
            with self.assertRaises(ValidationError):
                PeerHTTPServer(("127.0.0.1", 0), object, **kwargs)

    @unittest.skipUnless(shutil.which("openssl"), "OpenSSL generates a synthetic TLS certificate")
    def test_slow_tls_handshake_expires_before_a_healthy_tls_connection(self):
        with tempfile.TemporaryDirectory(prefix="refactoredmemory-deadline-tls-") as directory:
            cert, key = Path(directory) / "cert.pem", Path(directory) / "key.pem"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                            "-keyout", str(key), "-out", str(cert), "-days", "1", "-subj", "/CN=localhost",
                            "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=15)
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            server_context.load_cert_chain(cert, key)
            client_context = ssl.create_default_context(cafile=str(cert))
            incoming, outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
            client = client_context.wrap_bio(incoming, outgoing, server_hostname="localhost")
            with self.assertRaises(ssl.SSLWantReadError):
                client.do_handshake()
            hello = outgoing.read()
            self.assertGreater(len(hello), 100)
            with self.listener(tls_context=server_context) as listener:
                # Send a valid record header followed by one ClientHello byte
                # every 20ms. An idle timeout would be continually refreshed.
                with self.dripping(listener, hello[:6], remainder=hello[6:]) as sock:
                    self.assert_closed_promptly(sock)
                self.healthy(listener, context=client_context)


if __name__ == "__main__":
    unittest.main()
