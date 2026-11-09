"""Synthetic private graph-host boundary and authorization tests."""
import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import time
import unittest
from unittest.mock import patch

from examples.client_led_demo import seed
from refactoredmemory.review import handler
from refactoredmemory.service import Service
from refactoredmemory.store import Store


class ReviewHostTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(':memory:')
        seed(self.store)
        self.service = Service(self.store)
        self.owner = self.store.create_grant('synthetic owner', ['read', 'write', 'correct'], kind='owner')
        self.reader = self.store.create_grant('synthetic reader', ['read'])
        self.start(self.owner)

    def start(self, token):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(self.service, token, 'synthetic-local-key', start='project'))
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join()

    def tearDown(self):
        self.stop()
        self.store.close()

    def request(self, path, body=None, headers=None, method=None):
        client = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            payload = json.dumps(body) if body is not None else None
            client.request(method or ('POST' if body is not None else 'GET'), path, payload,
                {'Content-Type': 'application/json', **(headers or {})})
            response = client.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            client.close()

    def unlock(self):
        status, headers, _ = self.request('/api/session', {'key': 'synthetic-local-key'})
        self.assertEqual(status, 200)
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Strict', headers['Set-Cookie'])
        return {'Cookie': headers['Set-Cookie'].split(';')[0]}

    def test_html_has_no_credentials_or_automatic_session(self):
        status, headers, body = self.request('/')
        self.assertEqual(status, 200)
        self.assertNotIn('Set-Cookie', headers)
        self.assertNotIn(b'synthetic-local-key', body)
        self.assertNotIn(self.owner.encode(), body)
        self.assertIn(b'data-rm-mode="local"', body)
        self.assertIn("script-src 'sha256-", headers['Content-Security-Policy'])
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        state = json.loads(self.request('/api/state')[2])
        self.assertFalse(state['authenticated'])
        self.assertIsNone(state['start'])

    def test_private_unlock_then_real_comment_and_readback(self):
        args = {'name': 'memory_comment', 'arguments': {'target_id': 'alex-project', 'text': 'Synthetic UI comment', 'request_id': 'ui-note'}}
        self.assertEqual(self.request('/api/tool', args)[0], 403)
        auth = self.unlock()
        self.assertEqual(self.request('/api/tool', args, auth)[0], 200)
        status, _, body = self.request('/api/tool', {'name': 'memory_inspect', 'arguments': {'target_id': 'alex-project'}}, auth)
        self.assertEqual(status, 200)
        view = json.loads(body)
        self.assertEqual(view['comments'][0]['value']['text'], 'Synthetic UI comment')
        self.assertFalse(view['claims']['assertions'][0]['human_verified'])

    def test_cross_site_wrong_origin_wrong_host_and_wrong_key_are_denied(self):
        for header in ({'Host': 'attacker.example'}, {'Origin': 'https://attacker.example'}, {'Sec-Fetch-Site': 'cross-site'}):
            self.assertEqual(self.request('/api/session', {'key': 'synthetic-local-key'}, header)[0], 403)
        self.assertEqual(self.request('/api/session', {'key': 'wrong'})[0], 403)

    def test_expired_session_and_revoked_grant_cannot_read_or_write(self):
        auth = self.unlock()
        args = {'name': 'memory_inspect', 'arguments': {'target_id': 'alex-project'}}
        with patch('refactoredmemory.review.time.monotonic', return_value=time.monotonic() + 28801):
            self.assertEqual(self.request('/api/tool', args, auth)[0], 403)
        self.store.revoke_grant(self.owner)
        self.assertEqual(self.request('/api/tool', args, auth)[0], 403)

    def test_read_only_grant_and_generic_capture_stay_restricted(self):
        auth = self.unlock()
        self.assertEqual(self.request('/api/tool', {'name': 'memory_submit', 'arguments': {'actions': []}}, auth)[0], 403)
        self.stop()
        self.start(self.reader)
        auth = self.unlock()
        status, _, body = self.request('/api/tool', {'name': 'memory_inspect', 'arguments': {'target_id': 'alex-project'}}, auth)
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(body)['permissions']['write'])
        self.assertEqual(self.request('/api/tool', {'name': 'memory_comment', 'arguments': {'target_id': 'alex-project', 'text': 'Denied', 'request_id': 'deny'}}, auth)[0], 403)

    def test_unknown_routes_malformed_shapes_and_write_methods_fail_closed(self):
        auth = self.unlock()
        for path in ('/../memory.sqlite3', '/sync', '/admin', '/api/unknown'):
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('/api/tool', {'name': []}, auth)[0], 400)
        self.assertEqual(self.request('/api/tool', {'name': 'memory_status', 'arguments': []}, auth)[0], 400)
        for method in ('PUT', 'PATCH', 'DELETE'):
            self.assertEqual(self.request('/api/tool', {}, auth, method)[0], 405)
        self.assertEqual(self.request('/api/session', {}, {'Content-Length': '9999999999999'})[0], 400)


if __name__ == '__main__':
    unittest.main()
