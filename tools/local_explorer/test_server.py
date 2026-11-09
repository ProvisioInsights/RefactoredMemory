import contextlib
import http.client
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from server import Explorer,Handler,connection,readable


class ExplorerSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        db=self.root/'store.sqlite3'
        with sqlite3.connect(db) as c:c.execute('CREATE TABLE test(value TEXT)');c.execute("INSERT INTO test VALUES ('original')")
        self.db=db
    def tearDown(self):self.tmp.cleanup()
    def test_connections_cannot_modify_the_database(self):
        with contextlib.closing(connection(self.db)) as c:
            self.assertEqual(c.execute('SELECT value FROM test').fetchone()[0],'original')
            with self.assertRaises(sqlite3.OperationalError):c.execute("UPDATE test SET value='changed'")
        with sqlite3.connect(self.db) as c:self.assertEqual(c.execute('SELECT value FROM test').fetchone()[0],'original')
    def test_html_is_plain_text_and_script_and_style_are_removed(self):
        value=readable('<html><style>secret-style</style><p>Hello &amp; welcome</p><script>fetch("https://example.test/leak")</script></html>')
        self.assertIn('Hello & welcome',value);self.assertNotIn('fetch',value);self.assertNotIn('<script',value);self.assertNotIn('secret-style',value)
    def test_credential_assignments_are_withheld_from_display(self):
        self.assertNotIn('synthetic-private-value',readable('Authorization: synthetic-private-value\nOrdinary source text'))
    def test_unknown_source_id_cannot_select_a_local_file(self):
        index=self.root/'index.sqlite3'
        with sqlite3.connect(index) as c:c.execute('CREATE TABLE documents(id TEXT)')
        app=object.__new__(Explorer);app.index=index
        with self.assertRaises(KeyError):app.source('/etc/passwd')


class HttpBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);(root/'index.html').write_text('<html>Private explorer</html>')
        class App:
            def state(self):return {'read_only':True}
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.cookie='synthetic-session';self.server.assets=root;self.server.app=App()
        self.server.access_key='synthetic-private-access-key'
        self.server.cookie_created=time.monotonic()
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
    def tearDown(self):self.server.shutdown();self.server.server_close();self.worker.join();self.tmp.cleanup()
    def request(self,path,headers=None,method='GET',body=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        try:
            c.request(method,path,body=body,headers=headers or {});r=c.getresponse();return r.status,dict(r.getheaders()),r.read()
        finally:c.close()
    def test_api_needs_same_origin_session_and_cookie_is_protected(self):
        self.assertEqual(self.request('/api/state')[0],403)
        status,headers,body=self.request('/')
        self.assertEqual(status,200);self.assertNotIn('Set-Cookie',headers)
        status,login_headers,_=self.request('/api/session',method='POST',headers={'Content-Type':'application/json'},body=json.dumps({'key':'synthetic-private-access-key'}))
        self.assertEqual(status,200);self.assertIn('HttpOnly',login_headers['Set-Cookie']);self.assertIn('SameSite=Strict',login_headers['Set-Cookie'])
        self.assertEqual(headers['Cache-Control'],'no-store');self.assertIn("connect-src 'self'",headers['Content-Security-Policy'])
        self.assertEqual(self.request('/api/state',{'Cookie':'rm_explorer=synthetic-session'})[0],200)
    def test_wrong_or_cross_origin_unlock_never_grants_a_session(self):
        self.assertEqual(self.request('/api/session',method='POST',body=json.dumps({'key':'wrong'}))[0],403)
        self.assertEqual(self.request('/api/session',method='POST',headers={'Origin':'https://attacker.example'},body=json.dumps({'key':'synthetic-private-access-key'}))[0],403)
    def test_expired_session_needs_unlock_again(self):
        self.server.cookie_created=time.monotonic()-28801
        self.assertEqual(self.request('/api/state',{'Cookie':'rm_explorer=synthetic-session'})[0],403)
    def test_dns_rebinding_cross_origin_and_cross_site_are_denied(self):
        auth={'Cookie':'rm_explorer=synthetic-session'}
        for extra in ({'Host':'attacker.example'},{'Origin':'https://attacker.example'},{'Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.request('/api/state',{**auth,**extra})[0],403)
    def test_write_methods_and_asset_traversal_are_denied(self):
        for method in ('POST','PUT','DELETE','PATCH'):self.assertEqual(self.request('/api/state',method=method)[0],405)
        auth={'Cookie':'rm_explorer=synthetic-session'}
        self.assertEqual(self.request('/assets/../index.html',auth)[0],404)


if __name__=='__main__':unittest.main()
