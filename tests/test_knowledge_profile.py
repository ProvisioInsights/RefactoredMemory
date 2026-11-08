import tempfile
import unittest
from pathlib import Path

from refactoredmemory.store import Store, ValidationError
from refactoredmemory.knowledge import PROFILE, TYPE_PREDICATE, contract


def annotation(kind='relationship', category='affiliation', qualifiers=None):
    value = {'schema': PROFILE, 'kind': kind, 'qualifiers': qualifiers or {}}
    if category is not None:
        value['category'] = category
    return {'knowledge': value}


class KnowledgeProfileTests(unittest.TestCase):
    def test_contact_points_and_timeline_entries_coexist(self):
        for predicate in ['rm:contact-point','rm:communication-record','rm:profile-property','rm:reported-date','rm:legacy-reference']:
            self.store.submit([{'type':'assertion','id':predicate+suffix,'subject':'person','predicate':predicate,
                'value':value,'source_ids':['evidence'],'provenance':annotation(kind='fact',category=None)}
                for suffix,value in [('a',{'observed':'first'}),('b',{'observed':'second'})]])
            rows=self.store.query(subject='person',predicate=predicate)['assertions']
            self.assertEqual(len(rows),2)
            self.assertTrue(all(row['alternatives']==[] for row in rows))
            self.assertTrue(all(row['knowledge']['cardinality']=='multi-valued' for row in rows))

    def test_multivalued_fact_keeps_real_correction_conflicts(self):
        def point(id,**extra):return {'type':'assertion','id':id,'subject':'person','predicate':'rm:contact-point',
            'value':id,'source_ids':['evidence'],'provenance':annotation(kind='fact',category=None),**extra}
        self.store.submit([point('original')])
        self.store.submit([point('correction-a',kind='correct',predecessors=['original'],reason='Synthetic correction')])
        self.store.submit([point('correction-b',kind='correct',predecessors=['original'],reason='Synthetic competing correction')])
        rows=self.store.query(predicate='rm:contact-point')['assertions']
        self.assertEqual({r['id'] for r in rows},{'correction-a','correction-b'})
        self.assertTrue(all(r['conflicts'] for r in rows))
        self.assertTrue(all(r['alternatives']==[] for r in rows))

    def test_fact_cardinality_is_published_and_cannot_be_overridden(self):
        self.assertEqual(contract()['fact_predicates']['rm:contact-point']['cardinality'],'multi-valued')
        metadata=annotation(kind='fact',category=None);metadata['knowledge']['cardinality']='functional'
        with self.assertRaises(ValidationError):
            self.store.submit([{'type':'assertion','id':'bad-cardinality','subject':'person','predicate':'rm:contact-point',
                'value':'synthetic','source_ids':['evidence'],'provenance':metadata}])
        self.assertIsNone(self.store.read('assertion','bad-cardinality'))

    def setUp(self):
        self.store = Store(':memory:')
        self.store.submit([
            {'type':'entity','id':'person','entity_type':'person','label':'Example Person'},
            {'type':'entity','id':'org-a','entity_type':'organization','label':'Example Organization A'},
            {'type':'entity','id':'org-b','entity_type':'organization','label':'Example Organization B'},
            {'type':'entity','id':'legacy-project','entity_type':'other','label':'Example Project'},
            {'type':'source','id':'evidence','uri':'synthetic://evidence','content':'Synthetic fixture'}])

    def tearDown(self):
        self.store.close()

    def claim(self, id, **fields):
        return {'type':'assertion','id':id,'subject':'person','predicate':'member-of',
                'object':'org-a','source_ids':['evidence'], **fields}

    def test_multivalued_relationships_are_not_alternatives(self):
        self.store.submit([self.claim('a'), self.claim('b',object='org-b')])
        rows=self.store.query(subject='person')['assertions']
        self.assertEqual(len(rows),2)
        self.assertTrue(all(row['alternatives']==[] for row in rows))

    def test_functional_claims_keep_alternatives(self):
        self.store.submit([self.claim('a',predicate='based-in'),self.claim('b',predicate='based-in',object='org-b')])
        self.assertEqual(self.store.query(predicate='based-in')['assertions'][0]['alternatives'],['b'])

    def test_profile_preserves_qualifiers_without_human_authority(self):
        self.store.submit([self.claim('a',provenance=annotation(qualifiers={'role':'advisor'}))],actor={'kind':'agent','id':'extractor'})
        row=self.store.query(predicate='member-of')['assertions'][0]
        self.assertEqual(row['knowledge']['qualifiers']['role'],'advisor')
        self.assertFalse(row['human_verified'])
        self.assertEqual(row['actor']['kind'],'agent')

    def test_invalid_domain_fails_atomically(self):
        with self.assertRaises(ValidationError):
            self.store.submit([self.claim('bad',subject='org-a',object='person',provenance=annotation())])
        self.assertIsNone(self.store.read('assertion','bad'))

    def test_unknown_profile_predicate_and_category_are_rejected(self):
        for fields in ({'predicate':'typo'}, {'provenance':annotation(category='capital')}):
            args={'provenance':annotation(),**fields}
            with self.assertRaises(ValidationError): self.store.submit([self.claim('bad',**args)])

    def test_non_profile_legacy_records_remain_readable(self):
        self.store.submit([self.claim('old',predicate='legacy-open-label')])
        self.assertEqual(self.store.query(predicate='legacy-open-label')['assertions'][0]['knowledge']['profile'],'legacy-unannotated')

    def test_kind_shape_and_authority_fields_are_rejected(self):
        for metadata in (annotation(kind='fact'), {'knowledge':{'schema':PROFILE,'kind':'relationship','category':'affiliation','human_verified':True}}):
            with self.assertRaises(ValidationError): self.store.submit([self.claim('bad',provenance=metadata)])

    def test_type_recovery_preserves_original_identity(self):
        action={'type':'assertion','id':'type','subject':'legacy-project','predicate':TYPE_PREDICATE,
                'value':'project','source_ids':['evidence'],'provenance':annotation(kind='fact',category=None)}
        self.store.submit([action])
        entity=self.store.get_entity('legacy-project')
        self.assertEqual(entity['entity_type'],'other')
        self.assertEqual(entity['classification']['canonical_types'],['project'])
        self.assertEqual(self.store.read('entity','legacy-project')['entity_type'],'other')

    def test_ambiguous_types_fail_closed_for_new_profile_edge(self):
        for id,value in [('type-a','organization'),('type-b','project')]:
            self.store.submit([{'type':'assertion','id':id,'subject':'legacy-project','predicate':TYPE_PREDICATE,
                               'value':value,'source_ids':['evidence']}])
        self.assertTrue(self.store.get_entity('legacy-project')['classification']['ambiguous'])
        with self.assertRaises(ValidationError):
            self.store.submit([self.claim('bad',object='legacy-project',provenance=annotation())])

    def test_retraction_is_not_restored_by_profile(self):
        self.store.submit([self.claim('old')])
        self.store.submit([self.claim('retract',kind='retract',predecessors=['old'],reason='Synthetic error',provenance=annotation())])
        self.assertEqual(self.store.query(predicate='member-of')['assertions'],[])

    def test_filters_and_bounded_excerpt(self):
        text='Synthetic material. '*100+'Important matching phrase.'
        self.store.submit([self.claim('a',provenance=annotation()),
            {'type':'assertion','id':'document','subject':'person','predicate':'content','value':text,'source_ids':['evidence']}])
        self.assertEqual(len(self.store.query(knowledge_kind='relationship',category='affiliation')['assertions']),1)
        row=self.store.query(text='matching phrase',excerpt_chars=150)['assertions'][0]
        self.assertNotIn('value',row)
        self.assertLessEqual(len(row['excerpt']),150)
        self.assertIn('matching phrase',row['excerpt'])
        self.assertEqual(text[row['content_reference']['offset']:][:150],row['excerpt'])

    def test_unicode_excerpt_offset_uses_original_characters(self):
        text='ß'*200+' needle '+'x'*300
        self.store.submit([{'type':'assertion','id':'document','subject':'person','predicate':'content','value':text,'source_ids':['evidence']}])
        row=self.store.query(text='needle',excerpt_chars=100)['assertions'][0]
        self.assertIn('needle',row['excerpt'])
        self.assertEqual(text[row['content_reference']['offset']:][:100],row['excerpt'])

    def test_search_does_not_merge_matching_names(self):
        self.store.submit([{'type':'entity','id':'another','entity_type':'organization','label':'Example Person'}])
        result=self.store.search_entities('Example Person')
        self.assertEqual(result['matched'],2)
        self.assertEqual({e['id'] for e in result['entities']},{'person','another'})

    def test_backup_restore_keeps_profile_and_fresh_identity(self):
        self.store.submit([self.claim('a',provenance=annotation(qualifiers={'role':'advisor'}))])
        with tempfile.TemporaryDirectory() as tmp:
            self.store.backup(Path(tmp)/'backup.sqlite3')
            restored=Store.restore(Path(tmp)/'backup.sqlite3',Path(tmp)/'restored.sqlite3')
            try:
                self.assertNotEqual(self.store.peer_id,restored.peer_id)
                self.assertEqual(restored.query(predicate='member-of')['assertions'][0]['knowledge']['qualifiers'],{'role':'advisor'})
            finally: restored.close()

    def test_live_contract_defines_classification_and_cardinality(self):
        value=contract()
        self.assertEqual(value['predicates']['has-type']['category'],'taxonomy')
        self.assertEqual(value['predicates']['invests-in']['cardinality'],'multi-valued')

    def test_operator_enforcement_keeps_legacy_and_rejects_untyped_new_claim(self):
        self.store.submit([self.claim('legacy')])
        self.store.enable_knowledge_profile()
        self.assertEqual(len(self.store.query(predicate='member-of')['assertions']),1)
        with self.assertRaises(ValidationError): self.store.submit([self.claim('untyped')])
        with self.assertRaises(ValidationError):
            self.store.submit([{'type':'entity','id':'bad-type','entity_type':'typo','label':'Synthetic'}])
        self.store.submit([self.claim('typed',provenance=annotation())])

    def test_enforcement_allows_raw_observations_without_invented_semantics(self):
        self.store.enable_knowledge_profile()
        self.store.submit([{'type':'assertion','id':'raw','subject':'person','predicate':'content',
                           'value':'Untrusted source text','source_ids':['evidence']}])
        self.assertEqual(self.store.query(predicate='content')['assertions'][0]['knowledge']['kind'],'observation')

    def test_enforced_policy_survives_restore_without_rejecting_history(self):
        self.store.submit([self.claim('legacy')]);self.store.enable_knowledge_profile()
        with tempfile.TemporaryDirectory() as tmp:
            self.store.backup(Path(tmp)/'backup.sqlite3')
            restored=Store.restore(Path(tmp)/'backup.sqlite3',Path(tmp)/'restored.sqlite3')
            try:
                self.assertTrue(restored.knowledge_contract()['enforcement']['new_structured_writes'])
                with self.assertRaises(ValidationError):restored.submit([self.claim('untyped')])
                restored.submit([self.claim('typed',provenance=annotation())])
            finally:restored.close()

    def test_enforcement_blocks_already_open_legacy_writer_but_keeps_reads(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'policy.sqlite3'
            with Store(path) as current:
                current.submit([{'type':'entity','id':'person','entity_type':'person','label':'Synthetic'}])
                legacy=sqlite3.connect(path,isolation_level=None)
                try:
                    current.enable_knowledge_profile()
                    self.assertEqual(legacy.execute('SELECT count(*) FROM records').fetchone()[0],1)
                    before=legacy.execute('SELECT count(*) FROM operations').fetchone()[0]
                    with self.assertRaisesRegex(sqlite3.OperationalError,'no such function'):
                        legacy.execute("INSERT INTO operations SELECT 'stale-writer',origin,seq+1,body,signature,received_at,NULL,NULL,NULL FROM operations LIMIT 1")
                    self.assertEqual(legacy.execute('SELECT count(*) FROM operations').fetchone()[0],before)
                    current.submit([{'type':'entity','id':'project','entity_type':'project','label':'Synthetic Project'}])
                    self.assertEqual(legacy.execute('SELECT count(*) FROM records').fetchone()[0],2)
                finally:legacy.close()

    def test_restore_rejects_modified_writer_gate_without_executing_it(self):
        import sqlite3
        self.store.enable_knowledge_profile()
        with tempfile.TemporaryDirectory() as tmp:
            snapshot=Path(tmp)/'backup.sqlite3';destination=Path(tmp)/'restored.sqlite3'
            self.store.backup(snapshot)
            with sqlite3.connect(snapshot) as altered:
                altered.execute('DROP TRIGGER knowledge_writer_gate')
                altered.execute('CREATE TRIGGER knowledge_writer_gate BEFORE INSERT ON operations BEGIN SELECT 1; END')
            with self.assertRaisesRegex(ValidationError,'executable schema'):
                Store.restore(snapshot,destination)
            self.assertFalse(destination.exists())

    def test_deployment_guard_accepts_only_the_exact_policy_without_writes(self):
        import importlib.util,sqlite3
        from refactoredmemory.store import KNOWLEDGE_WRITER_GATE_SQL
        path=Path(__file__).resolve().parents[1]/'deploy/container_entrypoint.py'
        if not path.exists():self.skipTest('Standalone deployment guard is checked from the sealed source')
        spec=importlib.util.spec_from_file_location('synthetic_deployment_guard',path)
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
        self.assertEqual(guard.KNOWLEDGE_WRITER_GATE_SQL,KNOWLEDGE_WRITER_GATE_SQL)
        self.store.enable_knowledge_profile()
        with tempfile.TemporaryDirectory() as tmp:
            snapshot=Path(tmp)/'backup.sqlite3';self.store.backup(snapshot)
            before=snapshot.read_bytes();guard.validate_existing_database(snapshot)
            self.assertEqual(snapshot.read_bytes(),before)
            with sqlite3.connect(snapshot) as altered:
                altered.execute('DROP TRIGGER knowledge_writer_gate')
                altered.execute('CREATE TRIGGER knowledge_writer_gate BEFORE INSERT ON operations BEGIN SELECT 1; END')
            with self.assertRaises(ValueError):guard.validate_existing_database(snapshot)

    def test_endpoint_validation_does_not_rescan_the_journal_view(self):
        original=self.store._view
        def refuse(*args,**kwargs):raise AssertionError('Endpoint check rescanned the journal')
        self.store._view=refuse
        try:self.store.submit([self.claim('typed',provenance=annotation())])
        finally:self.store._view=original

    def test_type_resolution_respects_causal_frontier(self):
        self.store.submit([{'type':'assertion','id':'type-a','subject':'legacy-project','predicate':TYPE_PREDICATE,
                           'value':'project','source_ids':['evidence']}])
        frontier=self.store.status()['frontier']
        self.store.submit([{'type':'assertion','id':'type-b','subject':'legacy-project','predicate':TYPE_PREDICATE,
                           'value':'organization','source_ids':['evidence'],'kind':'correct','predecessors':['type-a'],'reason':'Synthetic correction'}])
        self.assertEqual(self.store._canonical_types('legacy-project',frontier),{'project'})
        self.assertEqual(self.store._canonical_types('legacy-project'),{'organization'})

    def test_document_mentions_are_capture_links_not_business_claims(self):
        self.store.submit([{'type':'entity','id':'document','entity_type':'source-document','label':'Synthetic captured message'}])
        self.store.enable_knowledge_profile()
        self.store.submit([self.claim('mention',subject='document',predicate='mentions',object='person',
                                    provenance=annotation(category='taxonomy',qualifiers={'layer':'capture','mention_kind':'header-reported-recipient'}))])
        row=self.store.query(predicate='mentions')['assertions'][0]
        self.assertEqual(self.store.get_entity('document')['entity_type'],'source-document')
        self.assertEqual(self.store.get_entity('document')['classification']['canonical_types'],['observation'])
        self.assertEqual(row['knowledge']['qualifiers']['layer'],'capture')
        self.assertFalse(row['human_verified'])
        self.assertEqual(self.store.query(predicate='invests-in')['assertions'],[])

    def test_business_entity_cannot_pose_as_document_mention_source(self):
        with self.assertRaises(ValidationError):
            self.store.submit([self.claim('invalid',predicate='mentions',object='org-a',provenance=annotation(category='taxonomy'))])


if __name__=='__main__': unittest.main()
