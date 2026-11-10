"""Private loopback host for the same graph App and authorized memory tools.

Credentials stay in private files, never in the browser bundle. Explicit UI
actions use the supplied grant; there is no administrative or model proxy.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import stat
import threading
import time

from .mcp import decode_message
from .service import Service
from .store import Store, ConflictError


def private_text(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        mode = os.fstat(fd)
        if not stat.S_ISREG(mode.st_mode) or mode.st_uid != os.getuid() or mode.st_mode & 0o077:
            raise ValueError('Credential file must be private and owned by the current user')
        value = os.read(fd, 1025).decode().strip()
        if not value or len(value) > 1024:
            raise ValueError('Invalid credential file')
        return value
    finally:
        os.close(fd)


def handler(service, token, access_key, *, start=None):
    html = service.resource('ui://refactoredmemory/graph.html', token)['contents'][0]['text']
    html = html.replace('<html lang="en">', '<html lang="en" data-rm-mode="local">')
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.S | re.I)
    hashes = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'" for s in scripts)
    csp = "default-src 'none'; script-src " + hashes + "; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    allowed = {t['name'] for t in service.tools()}
    sessions, lock = {}, threading.RLock()

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def log_message(self, *_):
            pass

        def reply(self, status, value, *, cookie=None, page=False):
            payload = value.encode() if page else json.dumps(value, ensure_ascii=False).encode()
            if len(payload) > 4 * 1024 * 1024:
                return self.reply(413, {'error': 'Result is too large; narrow the selection.'})
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8' if page else 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Security-Policy', csp)
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            if cookie:
                self.send_header('Set-Cookie', 'rm_workspace=' + cookie + '; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
            self.end_headers()
            self.wfile.write(payload)

        def boundary(self):
            self.connection.settimeout(15)
            expected = '127.0.0.1:' + str(self.server.server_port)
            if (len(self.headers.get_all('Host', [])) != 1 or self.headers.get('Host') != expected
                or len(self.headers.get_all('Origin', [])) > 1 or len(self.headers.get_all('Cookie', [])) > 1
                or self.headers.get('Origin') not in (None, 'http://' + expected)
                or self.headers.get('Sec-Fetch-Site') not in (None, 'same-origin', 'none')
                or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Encoding')):
                self.reply(403, {'error': 'Only this private app origin is allowed.'})
                return False
            return True

        def authenticated(self):
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get('Cookie', ''))
                value = cookie.get('rm_workspace')
                with lock:
                    return value is not None and sessions.get(value.value, 0) > time.monotonic()
            except Exception:
                return False

        def do_GET(self):
            if not self.boundary():
                return
            if self.path == '/':
                return self.reply(200, html, page=True)
            if self.path == '/api/state':
                opened = self.authenticated()
                return self.reply(200, {'authenticated': opened, 'start': start if opened else None})
            self.reply(404, {'error': 'Not found'})

        def do_POST(self):
            if not self.boundary():
                return
            if self.path not in ('/api/session', '/api/tool'):
                return self.reply(404, {'error': 'Not found'})
            length = self.headers.get('Content-Length', '')
            if (len(self.headers.get_all('Content-Length', [])) != 1 or len(length) > 10 or not length.isascii() or not length.isdecimal()
                or not 0 < int(length) <= 256 * 1024 or self.headers.get('Content-Type', '').split(';')[0] != 'application/json'):
                return self.reply(400, {'error': 'A bounded JSON request is required.'})
            try:
                data = decode_message(self.rfile.read(int(length)))
                if not isinstance(data, dict):
                    raise ValueError('Object required')
            except (ValueError, UnicodeError):
                return self.reply(400, {'error': 'Invalid JSON request.'})
            if self.path == '/api/session':
                value = data.get('key')
                if not isinstance(value, str) or not hmac.compare_digest(value.encode(), access_key.encode()):
                    return self.reply(403, {'error': 'Private access key was not accepted.'})
                session = secrets.token_urlsafe(32)
                with lock:
                    expired = [key for key, expiry in sessions.items() if expiry <= time.monotonic()]
                    for key in expired:
                        del sessions[key]
                    if len(sessions) >= 32:
                        return self.reply(429, {'error': 'Too many active sessions.'})
                    sessions[session] = time.monotonic() + 28800
                return self.reply(200, {'opened': True}, cookie=session)
            if not self.authenticated():
                return self.reply(403, {'error': 'Open your private memory first.'})
            name, arguments = data.get('name'), data.get('arguments', {})
            if not isinstance(name, str) or name not in allowed or not isinstance(arguments, dict):
                return self.reply(400, {'error': 'Unknown memory operation.'})
            # New field forms use the ordinary core tool, with a narrow v1-only
            # capture boundary. Generic/legacy capture and administration remain
            # unavailable here; this never changes the underlying grant.
            if name == 'memory_submit':
                from .field_contract import is_typed_capture
                if not is_typed_capture(arguments):
                    return self.reply(403, {'error': 'This editor permits catalog-matched typed fields only; generic capture is unavailable.'})
            try:
                result = service.call(name, arguments, token)
                self.reply(200, result)
            except PermissionError:
                self.reply(403, {'error': 'This connection is not permitted to perform that action.'})
            except ConflictError:
                self.reply(409, {'error': 'This record changed. Reload it before saving again.'})
            except (ValueError, TypeError):
                self.reply(400, {'error': 'The change did not satisfy the memory contract. Check the target, relationship and current revision.'})
            except Exception:
                self.reply(503, {'error': 'Memory could not complete the operation. No completion is claimed; retry with the same request ID.'})

        def forbidden(self):
            self.reply(405, {'error': 'Method unavailable'})
        do_PUT = do_PATCH = do_DELETE = forbidden

    return Handler


def main():
    parser = argparse.ArgumentParser(description='Private loopback graph review host; no model processing.')
    parser.add_argument('--db', required=True)
    parser.add_argument('--token-file', required=True)
    parser.add_argument('--access-key-file', required=True)
    parser.add_argument('--port', type=int, default=59260)
    parser.add_argument('--start')
    args = parser.parse_args()
    if not Path(args.db).is_file():
        parser.error('Use an existing explicitly initialized memory store')
    token, key = private_text(args.token_file), private_text(args.access_key_file)
    with Store(args.db) as store:
        service = Service(store)
        actor = service.auth(token, 'read')
        if actor['kind'] == 'peer':
            parser.error('Peer credentials cannot host a consumer app')
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(service, token, key, start=args.start))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
