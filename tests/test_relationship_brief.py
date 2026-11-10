"""Actual-graph, authority and freshness regressions for client-prepared views."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from examples.client_led_demo import seed
from refactoredmemory.service import Service
from refactoredmemory.store import Store, AuthorizationError, ConflictError, ValidationError
from refactoredmemory.workspace import Workspace


class RelationshipBriefTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(':memory:')
        seed(self.store)
        self.service = Service(self.store)
        self.writer = self.store.create_grant('synthetic client', ['read', 'write', 'correct'])
        self.reader = self.store.create_grant('synthetic independent reader', ['read'])
        self.view = {'schema': 'refactoredmemory.relationship-brief:v1', 'groups': [
            {'title': 'Selected people', 'items': [{'entity_id': 'alex',
              'claim_ids': ['alex-project', 'jamie-project', 'intro'], 'why': 'A named participant with an introduction.'}]}]}
        self.args = {'subject': 'project', 'title': 'Who is connected?', 'text': 'A synthetic, client-written interpretation.',
                     'inputs': [{'kind': 'assertion', 'id': rid} for rid in ['alex-project', 'jamie-project', 'intro', 'project-note']],
                     'input_frontier': self.store.status()['frontier'], 'view': self.view, 'request_id': 'brief',
                     'reported': {'application': 'Synthetic client', 'model': 'client-reported-model'}}

    def tearDown(self):
        self.store.close()

    def call(self, name, **args):
        return self.service.call(name, args, self.writer)

    def save(self):
        result = self.call('memory_derive', **self.args)
        return next(rid for rid in result['action_ids'] if self.store.read('assertion', rid))

    def correct(self, target='alex-project'):
        return self.call('memory_correct', target_id=target, expected_heads=[target], reason='Synthetic updated evidence',
                         **({'value': 'Changed note'} if target == 'project-note' else {'object': 'project'}), request_id='correct-' + target)

    def test_discovery_and_independent_reader_preserve_actual_paths_and_attribution(self):
        a = self.call('memory_schema'); b = self.service.call('memory_schema', {}, self.reader)
        self.assertEqual(a['relationship_brief'], b['relationship_brief'])
        brief = self.save()
        result = self.service.call('memory_graph', {'start': 'project', 'brief_id': brief}, self.reader)
        self.assertEqual({e['id'] for e in result['entities']}, {'alex', 'jamie', 'project'})
        self.assertEqual({e['id'] for e in result['edges']}, {'alex-project', 'jamie-project', 'intro'})
        self.assertEqual(len(result['paths']['alex']['routes']), 2)
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual(result['brief']['contribution']['connection']['kind'], 'agent')
        self.assertEqual(result['brief']['contribution']['reported']['model'], 'client-reported-model')
        self.assertNotIn('source text', str(result))

    def test_invalid_paths_and_unpinned_support_fail_without_partial_writes(self):
        before = self.store.status()['known_position']
        for ids in [['alex-job'], ['alex-project', 'alex-job'], ['project-note']]:
            args = copy.deepcopy(self.args); args['view']['groups'][0]['items'][0]['claim_ids'] = ids
            args['inputs'].append({'kind': 'assertion', 'id': 'alex-job'})
            with self.assertRaises(ValidationError):self.call('memory_derive', **args)
            self.assertEqual(self.store.status()['known_position'], before)

    def test_duplicate_records_and_overall_item_budget_are_enforced(self):
        for count in [2, 7]:
            args = copy.deepcopy(self.args); args['view']['groups'][0]['items'] *= count
            with self.assertRaises(ValidationError):self.call('memory_derive', **args)
        args = copy.deepcopy(self.args)
        items = [{'entity_id': 'person-' + str(i), 'claim_ids': ['alex-project'], 'why': 'Synthetic over-budget view'} for i in range(7)]
        args['view']['groups'] = [{'title': 'First', 'items': items[:4]}, {'title': 'Second', 'items': items[4:]}]
        with self.assertRaises(ValidationError):self.call('memory_derive', **args)

    def test_path_without_a_direct_edge_is_supported_but_three_hops_are_rejected(self):
        self.args['view']['groups'][0]['items'][0]['claim_ids'] = ['jamie-project', 'intro']
        self.assertEqual(len(self.call('memory_graph', start='project', brief_id=self.save())['paths']['alex']['routes'][0]['claim_ids']), 2)
        self.store.submit([{'type': 'assertion', 'id': 'third-hop', 'subject': 'jamie', 'predicate': 'employed-by',
                           'object': 'northstar', 'source_ids': ['meeting'], 'provenance': {'knowledge': {
                               'schema': 'refactoredmemory.knowledge:v1', 'kind': 'relationship', 'category': 'employment'}}}])
        args = copy.deepcopy(self.args);args['request_id'] = 'three-hops';args['input_frontier'] = self.store.status()['frontier']
        args['inputs'] = [{'kind': 'assertion', 'id': rid} for rid in ['alex-project', 'alex-job', 'third-hop']]
        args['view']['groups'][0]['items'] = [{'entity_id': 'jamie', 'claim_ids': ['alex-project', 'alex-job', 'third-hop'], 'why': 'Invalid long path.'}]
        with self.assertRaises(ValidationError):self.call('memory_derive', **args)

    def test_deleted_identity_and_future_or_forged_input_frontier_cannot_be_presented(self):
        brief = self.save(); action = self.store.read('assertion', brief);action['id'] = 'false-frontier';action['value']['input_frontier'] = {}
        self.store.submit([action])
        with self.assertRaises(ValidationError):self.call('memory_graph', start='project', brief_id='false-frontier')
        self.store.submit([{'type': 'delete', 'id': 'suppress-alex', 'entity_id': 'alex', 'reason': 'Synthetic owner suppression'}])
        result = self.call('memory_graph', start='project', brief_id=brief)
        self.assertEqual(result['brief']['freshness']['state'], 'stale')
        self.assertNotIn('text', result['brief']);self.assertEqual(len(result['entities']), 1)

    def test_selected_view_cannot_expand_a_claimed_tasks_inputs(self):
        job = self.call('memory_task', action='create', subject='project', title='Synthetic bounded task',
                        inputs=[{'kind': 'assertion', 'id': 'project-note'}], request_id='job')['job_id']
        heads = [r['id'] for r in self.store.query(subject=job, predicate='rm:task-state')['assertions']]
        self.call('memory_task', action='claim', job_id=job, expected_revisions=heads, request_id='claim-job')
        args = copy.deepcopy(self.args);args['reported']['task_id'] = job
        with self.assertRaises(AuthorizationError):self.call('memory_derive', **args)

    def test_correction_suppresses_old_prose_and_paths(self):
        brief = self.save(); self.correct()
        result = self.call('memory_graph', start='project', brief_id=brief)
        self.assertEqual(result['brief']['freshness']['state'], 'stale')
        self.assertNotIn('text', result['brief']); self.assertNotIn('groups', result['brief'])
        self.assertEqual(result['edges'], [])

    def test_extra_pinned_input_race_cannot_return_stale_text_as_current(self):
        brief = self.save(); original = Workspace.freshness; changed = False
        def race(workspace, refs):
            nonlocal changed
            result = original(workspace, refs)
            if not changed:
                changed = True; self.correct('project-note')
            return result
        with patch.object(Workspace, 'freshness', race):
            with self.assertRaises(ConflictError):self.call('memory_graph', start='project', brief_id=brief)

    def test_unrelated_writes_do_not_make_unchanged_inputs_stale(self):
        brief = self.save()
        self.call('memory_comment', target_id='alex', text='An unrelated synthetic comment.', request_id='comment')
        self.assertEqual(self.call('memory_graph', start='project', brief_id=brief)['brief']['freshness']['state'], 'current')

    def test_historical_forged_contribution_does_not_become_an_owner_connection(self):
        brief = self.save(); action = self.store.read('assertion', brief)
        action['id'] = 'peer-style-artifact'; action['provenance']['contribution']['connection'] = {'id': 'forged-owner', 'kind': 'owner'}
        self.store.submit([action], actor={'id': 'admitted-agent', 'kind': 'agent'})
        result = self.call('memory_graph', start='project', brief_id=action['id'])
        self.assertEqual(result['brief']['contribution']['connection']['id'], 'admitted-agent')
        self.assertEqual(result['brief']['contribution']['connection']['kind'], 'agent')

    def test_malformed_peer_envelope_is_a_bounded_validation_error(self):
        brief = self.save()
        for key, value in [('inputs', None), ('input_frontier', []), ('text', None), ('view', {'schema': 'unexpected', 'groups': []})]:
            action = self.store.read('assertion', brief); action['id'] = 'malformed-' + key; action['value'][key] = value
            self.store.submit([action])
            with self.assertRaises(ValidationError):self.call('memory_graph', start='project', brief_id=action['id'])

    def test_read_only_revoked_and_wrong_subject_grants_are_not_bypassed(self):
        with self.assertRaises(AuthorizationError):self.service.call('memory_derive', self.args, self.reader)
        brief = self.save()
        with self.assertRaises(ValidationError):self.call('memory_graph', start='alex', brief_id=brief)
        self.store.revoke_grant(self.reader)
        with self.assertRaises(AuthorizationError):self.service.call('memory_graph', {'start': 'project', 'brief_id': brief}, self.reader)

    def test_exact_retry_restart_and_fresh_identity_restore_keep_the_view(self):
        brief = self.save(); self.assertTrue(self.call('memory_derive', **self.args)['duplicate'])
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / 'snapshot.sqlite3'; self.store.backup(snapshot)
            restored = Store.restore(snapshot, Path(directory) / 'restored.sqlite3')
            try:
                token = restored.create_grant('fresh reader', ['read'])
                result = Service(restored).call('memory_graph', {'start': 'project', 'brief_id': brief}, token)
                self.assertEqual(result['brief']['freshness']['state'], 'current')
            finally:restored.close()

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable for the actual client projection fixture')
    def test_neighborhood_motion_preserves_positions_membership_and_real_edges(self):
        from examples.relationship_brief_demo import seed as seed_brief
        with Store(':memory:') as store:
            seed_brief(store)
            token = store.create_grant('synthetic motion reader', ['read'])
            service = Service(store)
            payload = {key: service.call('memory_graph', {'start': target, 'depth': 2, 'limit': 16}, token)
                       for key, target in [('before', 'project'), ('after', 'avery'), ('third', 'riverbend')]}
            fixture = Path(__file__).parent / 'fixtures/neighborhood-motion-client.mjs'
            result = json.loads(subprocess.check_output(['node', str(fixture)], input=json.dumps(payload), text=True))
            self.assertEqual(result['result'], 'passed')

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable for the actual client projection fixture')
    def test_map_inspector_uses_actual_contracts_selection_and_record_types(self):
        from examples.relationship_brief_demo import seed as seed_brief
        with Store(':memory:') as store:
            seed_brief(store)
            token = store.create_grant('synthetic inspector reader', ['read'])
            service = Service(store)
            payload = {'schema': service.call('memory_schema', {}, token)}
            for key, target in [('node', 'avery'), ('location', 'place'), ('edge', 'avery-round'), ('legacy', 'avery-robin')]:
                payload[key] = service.call('memory_inspect', {'target_id': target}, token)
                self.assertFalse(payload[key]['permissions']['write'])
                self.assertFalse(payload[key]['permissions']['correct'])
            payload['history'] = service.call('memory_history', {'entity_id': 'avery', 'limit': 40}, token)
            fixture = Path(__file__).parent / 'fixtures/map-inspector-client.mjs'
            result = json.loads(subprocess.check_output(['node', str(fixture)], input=json.dumps(payload), text=True))
            self.assertEqual(result['result'], 'passed')

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable for the actual client projection fixture')
    def test_indirect_map_uses_actual_context_without_expanding_the_saved_answer(self):
        from examples.relationship_brief_demo import seed as seed_brief
        with Store(':memory:') as store:
            brief = seed_brief(store); token = store.create_grant('synthetic map read', ['read'])
            service = Service(store)
            graph = service.call('memory_graph', {'start': 'project', 'depth': 2, 'limit': 16}, token)
            answer = service.call('memory_graph', {'start': 'project', 'brief_id': brief}, token)
            self.assertNotIn('riverbend', {e['id'] for e in answer['entities']})
            fixture = Path(__file__).parent / 'fixtures/neighborhood-client.mjs'
            result = json.loads(subprocess.check_output(['node', str(fixture)], input=json.dumps(graph), text=True))
        self.assertEqual(set(result['direct']), {'project', 'avery', 'jordan', 'morgan'})
        self.assertEqual(result['hops']['riverbend'], 2)
        self.assertEqual(result['path'], {'nodes': ['project', 'avery', 'riverbend'], 'edges': ['avery-round', 'avery-employer']})
        self.assertEqual(result['tracedEdges'], ['avery-employer', 'avery-round'])
        self.assertEqual(result['previousFocus'], 'avery')
        self.assertTrue(result['noInventedTrailEdge'])
        self.assertTrue(result['emptyTrace'])
        self.assertEqual(result['retainedDirection']['subject'], 'avery')
        self.assertEqual(result['retainedDirection']['object'], 'project')
        self.assertTrue(all(result[key] for key in ['onlyRecordedEdges', 'equalFrontier', 'changedFrontier', 'bounded',
            'currentContext', 'staleWithheld', 'changedContextRejected', 'wrongBriefRejected', 'wrongRevisionRejected', 'wrongContextRejected', 'overBudgetRejected']))

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable for the actual client projection fixture')
    def test_actual_client_projection_preserves_references_and_missingness(self):
        from examples.relationship_brief_demo import seed as seed_brief
        with Store(':memory:') as store:
            brief = seed_brief(store); token = store.create_grant('synthetic client read', ['read'])
            graph = Service(store).call('memory_graph', {'start': 'project', 'brief_id': brief}, token)
            fixture = Path(__file__).parent / 'fixtures/relationship-brief-client.mjs'
            result = json.loads(subprocess.check_output(['node', str(fixture)], input=json.dumps(graph), text=True))
        self.assertEqual(result['names'], ['Avery Rivera', 'Jordan Lee', 'Morgan Ellis'])
        self.assertEqual(result['firstRelationship'], 'Funding discussed')
        self.assertIn('amount: Unknown', result['firstContext'])
        self.assertEqual(result['sourceCount'], 3)
        self.assertEqual(set(result['pathEntities']), {'project', 'avery', 'morgan'})
        self.assertEqual(result['staleRows'], 0);self.assertEqual(result['malformedSnapshotRows'], 0)
        self.assertEqual(result['nullGroupRows'], 0);self.assertEqual(result['nullItemRows'], 0)
        self.assertTrue(all(result[key] for key in ['validSnapshot', 'nullEntityRejected', 'nullEdgeRejected', 'objectTitleRejected',
                                                   'objectTypeRejected', 'objectAttributionRejected', 'missingSourcesRejected']))
        self.assertEqual(result['legacy'], 'invests in')
        self.assertEqual(result['discussed'], 'Funding discussed')
        self.assertEqual(result['completed'], 'Investment reported as completed')


if __name__ == '__main__':unittest.main()
