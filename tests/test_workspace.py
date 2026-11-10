"""Synthetic client-led memory, authority, concurrency and recovery qualification."""
import concurrent.futures
import tempfile
import threading
import unittest
from pathlib import Path

from refactoredmemory.service import Service
from refactoredmemory.store import Store, AuthorizationError, ConflictError, ValidationError
from refactoredmemory.workspace import Workspace


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'memory.sqlite3'
        self.store = Store(self.path)
        self.store.submit([
            {'type': 'entity', 'id': 'project', 'entity_type': 'project', 'label': 'Example Project'},
            {'type': 'entity', 'id': 'alex', 'entity_type': 'person', 'label': 'Alex Morgan'},
            {'type': 'source', 'id': 'evidence', 'uri': 'synthetic://meeting', 'content': 'Alex expressed interest; no investment was confirmed.'},
            {'type': 'source', 'id': 'other-evidence', 'uri': 'synthetic://other', 'content': 'A different synthetic source.'},
            {'type': 'assertion', 'id': 'claim', 'subject': 'alex', 'predicate': 'participant-in', 'object': 'project',
             'source_ids': ['evidence'], 'provenance': {'knowledge': {'schema': 'refactoredmemory.knowledge:v1',
             'kind': 'relationship', 'category': 'occurrence', 'qualifiers': {}}}}])
        self.store.enable_knowledge_profile()
        self.service = Service(self.store)
        self.agent = self.store.create_grant('processor-a', ['read', 'write', 'correct'])
        self.other = self.store.create_grant('processor-b', ['read', 'write', 'correct'])
        self.reader = self.store.create_grant('reader', ['read'])
        self.owner = self.store.create_grant('owner-review', ['read', 'write', 'correct'], kind='owner')

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def call(self, name, token=None, **args):
        return self.service.call(name, args, token or self.agent)

    def create_job(self):
        result = self.call('memory_task', action='create', subject='project', title='Summarize the meeting',
            inputs=[{'kind': 'assertion', 'id': 'claim'}], request_id='create-job')
        return result['job_id']

    def revision(self, job):
        return [a['id'] for a in self.store.query(subject=job, predicate='rm:task-state')['assertions']]

    def claim_job(self):
        job = self.create_job()
        self.call('memory_task', action='claim', job_id=job, expected_revisions=self.revision(job), request_id='claim-job')
        return job

    def derive(self, **extra):
        args = dict(subject='project', title='Meeting brief', text='Alex expressed interest; investment is unconfirmed.',
                    inputs=[{'kind': 'assertion', 'id': 'claim'}], input_frontier=self.store.status()['frontier'], request_id='derive')
        args.update(extra)
        return self.call('memory_derive', **args)

    def test_client_led_job_checkpoint_output_and_retry_without_internal_model(self):
        job = self.create_job()
        rev = self.revision(job)
        args = dict(action='claim', job_id=job, expected_revisions=rev, request_id='claim-job')
        self.call('memory_task', **args)
        self.assertTrue(self.call('memory_task', **args)['duplicate'])
        self.call('memory_task', action='checkpoint', job_id=job, expected_revisions=self.revision(job),
                  checkpoint={'next_part': 2, 'processed': ['claim']}, request_id='checkpoint')
        self.assertEqual(self.store.query(subject=job, predicate='rm:task-state')['assertions'][0]['value']['checkpoint']['next_part'], 2)
        receipt = self.derive(reported={'application': 'Synthetic client', 'model': 'reported-model', 'task_id': job})
        output = next(a for a in receipt['action_ids'] if self.store.read('assertion', a))
        self.call('memory_task', action='complete', job_id=job, expected_revisions=self.revision(job), output_ids=[output], request_id='complete')
        self.assertEqual(self.store.query(subject=job, predicate='rm:task-state')['assertions'][0]['value']['status'], 'completed')
        artifact = self.call('memory_artifacts', subject='project')[0]
        self.assertEqual(artifact['freshness']['state'], 'current')
        self.assertEqual(artifact['provenance']['contribution']['reported_basis'], 'client supplied; not independently verified')

    def test_permissions_and_managed_records_cannot_forge_owner_reviews(self):
        with self.assertRaises(AuthorizationError):
            self.call('memory_comment', token=self.reader, target_id='claim', text='No write permission', request_id='denied')
        with self.assertRaises(AuthorizationError):
            self.call('memory_review', target_id='claim', disposition='confirmed', note='I claim to be John', expected_reviews=[], request_id='spoof')
        for predicate in ('rm:review', 'rm:task-state', 'rm:comment', 'rm:derived-memory'):
            with self.assertRaises(AuthorizationError):
                self.call('memory_submit', actions=[{'type': 'assertion', 'id': 'spoof', 'subject': 'alex', 'predicate': predicate,
                    'value': {'confirmed': True}, 'source_ids': ['evidence']}])
        with self.assertRaises(AuthorizationError):
            self.call('memory_submit', actions=[{'type': 'entity', 'id': 'x', 'entity_type': 'person', 'label': 'X'}], request_id='workspace:reserved')
        self.assertFalse(self.store.query(subject='alex')['assertions'][0]['human_verified'])

    def test_owner_review_is_revision_and_knowledge_view_specific(self):
        before = self.store.status()['known_position']
        self.call('memory_review', token=self.owner, target_id='claim', disposition='confirmed', note='Synthetic owner review', expected_reviews=[], request_id='review')
        current = self.store.query(subject='alex', predicate='participant-in')['assertions'][0]
        self.assertTrue(current['human_verified'])
        self.assertFalse(self.store.query(subject='alex', predicate='participant-in', known_at=before)['assertions'][0]['human_verified'])
        self.call('memory_correct', target_id='claim', expected_heads=['claim'], reason='Synthetic corrected target', object='project', request_id='correction')
        corrected = self.store.query(subject='alex', predicate='participant-in')['assertions'][0]
        self.assertFalse(corrected['human_verified'])
        self.assertEqual(corrected['predecessors'], ['claim'])

    def test_comments_are_durable_and_not_verification(self):
        args = dict(target_id='claim', text='Please check the meaning of interest.', request_id='comment')
        self.call('memory_comment', **args)
        self.assertTrue(self.call('memory_comment', **args)['duplicate'])
        with self.assertRaises(ConflictError):
            self.call('memory_comment', **{**args, 'text': 'Different contents'})
        view = self.call('memory_inspect', target_id='claim')
        self.assertEqual(len(view['comments']), 1)
        self.assertFalse(view['claims']['assertions'][0]['review']['human_verified'])
        self.store.close()
        self.store = Store(self.path)
        self.service = Service(self.store)
        self.assertEqual(len(self.call('memory_inspect', target_id='claim')['comments']), 1)

    def test_input_correction_marks_summary_stale_and_blocks_old_task_output(self):
        job = self.claim_job()
        self.derive()
        self.call('memory_correct', target_id='claim', expected_heads=['claim'], reason='Correct old interpretation', object='project', request_id='correct-input')
        self.assertEqual(self.call('memory_artifacts', subject='project')[0]['freshness']['state'], 'stale')
        with self.assertRaises(ConflictError):
            self.call('memory_task', action='checkpoint', job_id=job, expected_revisions=self.revision(job), checkpoint={}, request_id='stale-checkpoint')
        with self.assertRaises(ConflictError):
            self.derive(request_id='stale-summary')

    def test_foreign_connection_and_out_of_task_evidence_are_rejected(self):
        job = self.claim_job()
        with self.assertRaises(AuthorizationError):
            self.call('memory_task', token=self.other, action='complete', job_id=job, expected_revisions=self.revision(job), request_id='foreign')
        with self.assertRaises(AuthorizationError):
            self.derive(inputs=[{'kind': 'source', 'id': 'other-evidence'}], reported={'task_id': job}, request_id='outside-input')
        with self.assertRaises(ValidationError):
            self.call('memory_task', action='complete', job_id=job, expected_revisions=self.revision(job), output_ids=['claim'], request_id='foreign-output')

    def test_two_connections_cannot_claim_same_local_revision(self):
        job = self.create_job()
        revisions = self.revision(job)
        second = Store(self.path)
        try:
            barrier = threading.Barrier(2)
            def claim(service, token, rq):
                barrier.wait()
                try:
                    service.call('memory_task', dict(action='claim', job_id=job, expected_revisions=revisions, request_id=rq), token)
                    return 'claimed'
                except ConflictError:
                    return 'conflict'
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(claim, self.service, self.agent, 'claim-a'), pool.submit(claim, Service(second), self.other, 'claim-b')]
                self.assertEqual(sorted(f.result() for f in futures), ['claimed', 'conflict'])
        finally:
            second.close()

    def test_guarded_edit_failure_leaves_no_partial_interaction_records(self):
        workspace = Workspace(self.store, self.store.authenticate(self.agent))
        guard = workspace.guard('alex', 'participant-in', workspace.heads('alex', 'participant-in'))
        self.call('memory_correct', target_id='claim', expected_heads=['claim'], reason='First change', object='project', request_id='first')
        with self.assertRaises(ConflictError):
            self.store.submit([{'type': 'source', 'id': 'must-not-exist', 'uri': 'synthetic://guard', 'content': 'Synthetic'}], expected_heads=[guard])
        self.assertIsNone(self.store.read('source', 'must-not-exist'))

    def test_graph_includes_incoming_edges_and_reports_bounds(self):
        graph = self.call('memory_graph', start='project')
        self.assertEqual({e['id'] for e in graph['entities']}, {'alex', 'project'})
        self.assertEqual(graph['edges'][0]['id'], 'claim')
        self.assertFalse(self.call('memory_graph', start='project', limit=1)['coverage']['complete'])

    def test_current_frontier_review_does_not_decode_entire_journal(self):
        import sqlite3
        frontier = self.store.status()['frontier']
        def guard(action, table, column, *_):
            if action == sqlite3.SQLITE_READ and table == 'operations' and column == 'body':
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        self.store.db.set_authorizer(guard)
        try:
            self.assertEqual(self.store._view(frontier=frontier)[1], frontier)
        finally:
            self.store.db.set_authorizer(None)

    def test_attribution_and_activity_keep_reported_model_separate(self):
        before = self.store.status()['known_position']
        self.call('memory_comment', target_id='claim', text='Synthetic note', request_id='attributed', reported={'application': 'Synthetic connector', 'model': 'reported-model'})
        actor = self.store.authenticate(self.agent)
        activity = self.call('memory_activity', since=before, connection_id=actor['id'])
        self.assertEqual(len(activity['items']), 1)
        self.assertEqual(activity['items'][0]['connection']['id'], actor['id'])
        self.assertEqual(activity['items'][0]['reported_processor']['model'], 'reported-model')
        self.assertNotIn('Synthetic note', str(activity))
        self.assertIn('not remote receipt', activity['items'][0]['replication'])

    def test_activity_action_budget_never_skips_an_operation(self):
        before = self.store.status()['known_position']
        expected = set()
        for batch in range(3):
            actions = []
            for number in range(200):
                rid = f'activity-{batch}-{number}'
                expected.add(rid)
                actions.append({'type': 'assertion', 'id': rid, 'subject': 'project',
                    'predicate': 'rm:comment', 'value': {'text': rid, 'target_id': 'project'},
                    'source_ids': ['evidence'], 'provenance': {'knowledge': {
                        'schema': 'refactoredmemory.knowledge:v1', 'kind': 'fact', 'qualifiers': {}}}})
            self.store.submit(actions)
        seen, cursor = set(), before
        while True:
            page = self.call('memory_activity', since=cursor, limit=50)
            self.assertLessEqual(len(page['items']), 500)
            seen.update(row['id'] for row in page['items'])
            self.assertGreater(page['next_since'], cursor)
            cursor = page['next_since']
            if not page['has_more']:
                break
        self.assertEqual(seen, expected)

    def test_graph_resource_is_fixed_authenticated_and_modern_legacy_compatible(self):
        from refactoredmemory.mcp import Dispatcher
        from tests.test_mcp import request
        dispatcher = Dispatcher(self.service, legacy_stdio=True)
        modern = dispatcher.dispatch(request('resources/list'), self.reader)['result']
        uri = modern['resources'][0]['uri']
        self.assertEqual(uri, 'ui://refactoredmemory/graph.html')
        loaded = dispatcher.dispatch(request('resources/read', {'uri': uri}), self.reader)['result']
        self.assertIn('profile=mcp-app', loaded['contents'][0]['mimeType'])
        self.assertIn('RefactoredMemory', loaded['contents'][0]['text'])
        self.assertNotIn(self.owner, loaded['contents'][0]['text'])
        initialized = dispatcher.dispatch({'jsonrpc': '2.0', 'id': 40, 'method': 'initialize',
            'params': {'protocolVersion': '2025-11-25', 'capabilities': {},
                       'clientInfo': {'name': 'synthetic independent host', 'version': '1'}}}, self.reader)
        self.assertIn('resources', initialized['result']['capabilities'])
        legacy = dispatcher.dispatch({'jsonrpc': '2.0', 'id': 41, 'method': 'resources/read',
            'params': {'uri': uri}}, self.reader)
        self.assertEqual(legacy['result']['contents'][0]['text'], loaded['contents'][0]['text'])
        unknown = dispatcher.dispatch(request('resources/read', {'uri': 'file:///private/store'}), self.reader)
        self.assertEqual(unknown['error']['code'], -32602)
        self.store.revoke_grant(self.reader)
        self.assertEqual(dispatcher.dispatch(request('resources/read', {'uri': uri}), self.reader)['error']['code'], 403)

    def test_fresh_identity_restore_preserves_work_and_revokes_old_grants(self):
        self.claim_job()
        self.derive()
        snapshot = Path(self.temp.name) / 'snapshot.sqlite3'
        self.store.backup(snapshot)
        restored = Store.restore(snapshot, Path(self.temp.name) / 'restored.sqlite3')
        try:
            with self.assertRaises(AuthorizationError):
                restored.authenticate(self.agent)
            self.assertEqual(len(restored.query(predicate='rm:derived-memory')['assertions']), 1)
            self.assertEqual(len(restored.query(predicate='rm:task-state')['assertions']), 1)
        finally:
            restored.close()

    def test_reclassify_and_retract_preserve_original_meaning_and_history(self):
        result = self.call('memory_correct', target_id='claim', expected_heads=['claim'], reason='Synthetic relationship correction',
            operation='reclassify', predicate='introduced-by', object='alex', request_id='reclassify')
        original = self.store.query(subject='alex', predicate='participant-in', include_inactive=True)['assertions']
        self.assertEqual({r['object'] for r in original}, {'project'})
        self.assertEqual({r['status'] for r in original}, {'superseded', 'retracted'})
        new = self.store.query(subject='alex', predicate='introduced-by')['assertions'][0]
        self.assertEqual(new['object'], 'alex')
        self.call('memory_correct', target_id=new['id'], expected_heads=[new['id']], reason='Synthetic withdrawal', operation='retract', request_id='withdraw')
        self.assertEqual(self.store.query(subject='alex', predicate='introduced-by')['assertions'], [])
        self.assertTrue(result['operation_id'])

    def test_many_checkpoints_do_not_grow_the_source_list_unboundedly(self):
        job = self.claim_job()
        for n in range(110):
            self.call('memory_task', action='checkpoint', job_id=job, expected_revisions=self.revision(job), checkpoint={'next': n}, request_id='checkpoint-' + str(n))
        row = self.store.query(subject=job, predicate='rm:task-state')['assertions'][0]
        self.assertLessEqual(len(row['source_ids']), 3)
        self.assertEqual(row['value']['checkpoint']['next'], 109)

    def test_revocation_inside_admission_is_atomic(self):
        actor = self.store.authenticate(self.agent)
        self.store.revoke_grant(self.agent)
        with self.assertRaises(AuthorizationError):
            self.store.submit([{'type': 'source', 'id': 'denied-source', 'uri': 'synthetic://revoked', 'content': 'Synthetic'}],
                actor=actor, authorize=lambda: self.store.authenticate(self.agent, 'write'))
        self.assertIsNone(self.store.read('source', 'denied-source'))

    def test_evidence_is_bounded_inert_text_and_known_controls_are_withheld(self):
        from refactoredmemory.workspace import readable
        self.assertEqual(readable('<html><script>never execute</script><p>Safe text</p></html>'), 'Safe text')
        self.assertNotIn('synthetic-secret', readable('Authorization: synthetic-secret\nSource text'))

        result = self.call('memory_evidence', target_id='claim', source_id='evidence', chars=100)
        self.assertIn('Alex expressed interest', result['excerpt'])
        with self.assertRaises(ValidationError):
            self.call('memory_evidence', target_id='claim', source_id='other-evidence')
        self.store.submit([{'type': 'assertion', 'id': 'control-class', 'subject': 'alex', 'predicate': 'rm:source-classification',
            'value': {'restricted': True, 'classification': 'restricted-control-record'}, 'source_ids': ['evidence'],
            'provenance': {'knowledge': {'schema': 'refactoredmemory.knowledge:v1', 'kind': 'fact'}}}])
        self.assertTrue(self.call('memory_evidence', target_id='claim', source_id='evidence')['withheld'])

    def test_import_envelopes_display_body_without_altering_original(self):
        import json
        from refactoredmemory.workspace import readable
        header = {'part': 0, 'parts': 1, 'source_identity': 'synthetic-mail', 'version_sha256': 'a' * 64}
        envelope = {'untrusted_source_content': True, 'fidelity': 'source text',
            'source_identity': 'synthetic-mail', 'title': 'Synthetic meeting',
            'metadata': {'receivedDateTime': '2026-11-07T12:00:00Z'}}
        original = json.dumps(header) + '\n\n' + json.dumps(envelope) + '\n\nActual synthetic message body.'
        self.store.submit([{'type': 'source', 'id': 'wrapped-evidence', 'uri': 'synthetic://wrapped', 'content': original},
            {'type':'assertion','id':'wrapped-claim','subject':'alex','predicate':'participant-in','object':'project',
             'source_ids':['wrapped-evidence'],'provenance':{'knowledge':{'schema':'refactoredmemory.knowledge:v1','kind':'relationship','category':'occurrence','qualifiers':{}}}}])
        shown = self.call('memory_evidence', target_id='wrapped-claim', source_id='wrapped-evidence')
        self.assertEqual(shown['title'], 'Synthetic meeting')
        self.assertEqual(shown['date'], '2026-11-07T12:00:00Z')
        self.assertEqual(shown['excerpt'], 'Actual synthetic message body.')
        # Parser behavior is display-only and does not rewrite immutable capture.
        self.assertEqual(readable(original), 'Actual synthetic message body.')
        self.assertEqual(self.store.get_source('wrapped-evidence')['content'], original)
        self.assertEqual(readable('{"domain":"record"}\n\nUnrelated source content.'), '{"domain":"record"}\n\nUnrelated source content.')

    def test_offline_competing_claims_converge_and_owner_resolution_can_be_claimed(self):
        job = self.create_job()
        second = Store(Path(self.temp.name) / 'peer.sqlite3', store_id=self.store.store_id)
        left, right = self.store.identity(), second.identity()
        self.store.admit_peer(right['peer_id'], right['key_hex'])
        second.admit_peer(left['peer_id'], left['key_hex'])
        def transfer(a, b):
            while True:
                batch = a.export_operations(b.status()['frontier'], limit=100)
                if not batch['operations']:
                    break
                self.assertEqual(b.receive(batch['operations'], a.peer_id)['rejected'], 0)
        try:
            transfer(self.store, second)
            second.enable_knowledge_profile()
            token = second.create_grant('offline second client', ['read', 'write', 'correct'])
            revisions = self.revision(job)
            self.call('memory_task', action='claim', job_id=job, expected_revisions=revisions, request_id='offline-a')
            Service(second).call('memory_task', dict(action='claim', job_id=job, expected_revisions=revisions, request_id='offline-b'), token)
            transfer(self.store, second)
            transfer(second, self.store)
            self.assertEqual(len(self.revision(job)), 2)
            with self.assertRaises(ConflictError):
                self.call('memory_task', action='complete', job_id=job, expected_revisions=self.revision(job), output_ids=['claim'], request_id='conflicted-complete')
            self.call('memory_task', token=self.owner, action='resolve', job_id=job, expected_revisions=self.revision(job), request_id='owner-resolve')
            self.call('memory_task', action='claim', job_id=job, expected_revisions=self.revision(job), request_id='claim-resolved')
            self.assertEqual(len(self.revision(job)), 1)
            self.assertEqual(self.store.query(subject=job, predicate='rm:task-state')['assertions'][0]['value']['status'], 'running')
            transfer(self.store, second)
            frontier = self.store.status()['frontier']
            self.assertEqual(self.store.query(subject=job, frontier=frontier)['assertions'], second.query(subject=job, frontier=frontier)['assertions'])
        finally:
            second.close()


if __name__ == '__main__':
    unittest.main()
