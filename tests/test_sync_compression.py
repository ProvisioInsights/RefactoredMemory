"""Synthetic bounded private-sync compression tests."""
import gzip
import json
import unittest
from refactoredmemory.sync import decode_peer_request, SyncError, MAX_BODY_BYTES
class CompressionTests(unittest.TestCase):
 def test_identity_and_gzip_decode_the_same_exchange(self):
  value={"protocol":"refactoredmemory-sync/1","operations":[],"frontier":{}}
  raw=json.dumps(value).encode()
  self.assertEqual(decode_peer_request(raw),value)
  self.assertEqual(decode_peer_request(gzip.compress(raw),"gzip"),value)
 def test_expansion_bomb_is_bounded(self):
  with self.assertRaises(SyncError) as e:decode_peer_request(gzip.compress(b"x"*(MAX_BODY_BYTES+1)),"gzip")
  self.assertEqual(e.exception.code,"too_large")
 def test_invalid_truncated_concatenated_and_trailing_members_are_rejected(self):
  good=gzip.compress(b"{}")
  for value in [b"invalid",good[:-1],good+good,good+b"trailing"]:
   with self.subTest(size=len(value)),self.assertRaises(SyncError):decode_peer_request(value,"gzip")
 def test_unknown_encoding_and_oversized_wire_are_rejected(self):
  with self.assertRaises(SyncError):decode_peer_request(b"{}","br")
  with self.assertRaises(SyncError):decode_peer_request(b"x"*(MAX_BODY_BYTES+1),"gzip")

 def test_production_handler_accepts_compressed_signed_sync_after_authentication(self):
  import tempfile,threading,os
  from pathlib import Path
  from unittest.mock import patch
  from http.client import HTTPConnection
  from refactoredmemory.cli import server_handler,PeerHTTPServer
  from refactoredmemory.service import Service
  from refactoredmemory.store import Store
  from refactoredmemory.sync import sync_once
  with tempfile.TemporaryDirectory() as folder:
   with Store(Path(folder)/"local.sqlite",store_id="synthetic-gzip",peer_id="local") as local, Store(Path(folder)/"remote.sqlite",store_id="synthetic-gzip",peer_id="remote") as remote:
    local.admit_peer("remote",remote.identity()["key_hex"])
    remote.admit_peer("local",local.identity()["key_hex"])
    token=remote.create_grant("synthetic gzip",["sync"],kind="peer",peer_id="local")
    local.submit([{"type":"entity","id":"note","entity_type":"note","label":"Synthetic "*4000}])
    server=PeerHTTPServer(("127.0.0.1",0),server_handler(Service(remote),sync_only=True));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
     url="http://127.0.0.1:"+str(server.server_port)+"/sync"
     with patch.dict(os.environ,{"REFMEM_SYNC_REQUEST_ENCODING":"gzip"}):
      result=sync_once(local,url,token,expected_peer="remote")
     self.assertTrue(result["complete"])
     self.assertEqual(local.status()["frontier"],remote.status()["frontier"])
     connection=HTTPConnection("127.0.0.1",server.server_port,timeout=3)
     connection.request("POST","/sync",gzip.compress(b"x"*(MAX_BODY_BYTES+1)),headers={"Content-Type":"application/json","Content-Encoding":"gzip"})
     self.assertEqual(connection.getresponse().status,401);connection.close()
     connection=HTTPConnection("127.0.0.1",server.server_port,timeout=3)
     connection.putrequest("POST","/sync");connection.putheader("Authorization","Bearer "+token);connection.putheader("Content-Length","2");connection.putheader("Content-Type","application/json");connection.putheader("Content-Encoding","identity");connection.putheader("Content-Encoding","gzip");connection.endheaders(b"{}")
     self.assertEqual(connection.getresponse().status,400);connection.close()
    finally:server.shutdown();server.server_close();thread.join(timeout=3)
