"""A restore must stream a journal larger than its process address-space cap."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from refactoredmemory.store import Store


class RestoreMemoryTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith('linux'),'Linux address-space-limit restore regression')
    def test_restore_streams_journal_larger_than_256_mib(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.sqlite3';destination=Path(tmp)/'restored.sqlite3'
            with Store(source) as store:
                for group in range(310):
                    store.submit([{'type':'source','id':f'synthetic-{group}-{part}',
                                   'uri':f'synthetic://{group}/{part}','content':'x'*60000}
                                  for part in range(15)])
                self.assertGreater(store.db.execute('SELECT sum(length(body)) FROM operations').fetchone()[0],256*1024**2)
            root=Path(__file__).resolve().parents[1]
            code="import runpy;runpy.run_path('tests/test_restore_memory.py',run_name='__main__')"
            result=subprocess.run([sys.executable,'-c',code,'--restore-probe',str(source),str(destination)],
                                  cwd=root,capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout),{'sources':4650,'fresh_identity':True})


if __name__=='__main__':
    if '--restore-probe' in sys.argv:
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
        source,destination=sys.argv[-2:]
        restored=Store.restore(source,destination)
        try:
            result={'sources':restored.status()['counts']['source'],
                    'fresh_identity':restored.peer_id!=restored.status()['restored_from']['peer_id']}
            print(json.dumps(result))
        finally:restored.close()
    else:unittest.main()
