"""Disposable synthetic MCP Apps SDK host, never a personal-store host.

Build with `npm run build:reference` in apps/memory_graph, then run this
module from the repository root. No credentials, personal paths or models.
The host proxies the official SDK AppBridge to real Service tool calls.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

from examples.client_led_demo import seed
from refactoredmemory.mcp import decode_message
from refactoredmemory.service import Service
from refactoredmemory.store import Store


def main():
    assets = Path(__file__).resolve().parents[1] / 'apps/memory_graph/.reference-host/index.html'
    host = assets.read_bytes()
    with Store(':memory:') as store:
        seed(store)
        service = Service(store)
        token = store.create_grant('synthetic MCP App host', ['read', 'write', 'correct'], kind='owner')
        app = service.resource('ui://refactoredmemory/graph.html', token)['contents'][0]['text'].encode()

        class Handler(BaseHTTPRequestHandler):
            def setup(self):
                super().setup()
                self.connection.settimeout(10)

            def log_message(self, *_):
                pass

            def reply(self, code, data, page=False):
                body = data if page else json.dumps(data).encode()
                self.send_response(code)
                self.send_header('Content-Type', 'text/html; charset=utf-8' if page else 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; frame-src 'self'; connect-src 'self'; frame-ancestors 'self'")
                self.end_headers()
                self.wfile.write(body)

            def boundary(self):
                origin = 'http://127.0.0.1:59262'
                return (self.headers.get_all('Host') == ['127.0.0.1:59262']
                    and len(self.headers.get_all('Origin', [])) <= 1
                    and self.headers.get('Origin') in (None, origin)
                    and self.headers.get('Sec-Fetch-Site') in (None, 'same-origin', 'none'))

            def do_GET(self):
                if not self.boundary():
                    return self.reply(403, {'error': 'Local synthetic host only'})
                if self.path in ('/', '/?display'):
                    return self.reply(200, host, True)
                if self.path == '/app':
                    return self.reply(200, app, True)
                self.reply(404, {'error': 'Not found'})

            def do_POST(self):
                if not self.boundary():
                    return self.reply(403, {'error': 'Local synthetic host only'})
                size = self.headers.get('Content-Length', '')
                if (self.path != '/rpc' or len(self.headers.get_all('Content-Length', [])) != 1
                    or not size.isdecimal() or len(size) > 7 or not 0 < int(size) < 262144
                    or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Type') != 'application/json'):
                    return self.reply(400, {'error': 'Bounded JSON required'})
                try:
                    data = decode_message(self.rfile.read(int(size)))
                    if not isinstance(data, dict) or data.get('name') in ('memory_submit',):
                        raise ValueError('Narrow synthetic workspace tools only')
                    self.reply(200, service.call(data['name'], data.get('arguments', {}), token))
                except (ValueError, TypeError, KeyError, PermissionError):
                    self.reply(400, {'error': 'Synthetic tool request rejected'})

        server = ThreadingHTTPServer(('127.0.0.1', 59262), Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
