"""Synthetic core contract for the shared field editor, independent of its UI."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from refactoredmemory import field_contract
from refactoredmemory.service import Service
from refactoredmemory.store import Store, AuthorizationError, ConflictError, ValidationError


def field(field_id, value, rid, subject='person'):
    definition = field_contract.catalog()['fields'][field_id]
    return {'type': 'assertion', 'id': rid, 'subject': subject,
        'predicate': definition['storage']['predicate'], 'value': value,
        'source_ids': ['source'], 'valid_from': None, 'valid_to': None, 'time_precision': 'unknown',
        'provenance': {'knowledge': {'schema': 'refactoredmemory.knowledge:v1', 'kind': 'fact',
            'qualifiers': {'field_contract': {'schema': field_contract.SCHEMA, 'revision': 1,
                'field': field_id, 'state': 'known', 'validity_end': 'unknown'}}}}}


class FieldEditorTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(':memory:')
        self.store.submit([
            {'type': 'entity', 'id': 'person', 'entity_type': 'person', 'label': 'Avery Chen'},
            {'type': 'entity', 'id': 'org', 'entity_type': 'organization', 'label': 'Synthetic Company'},
            {'type': 'source', 'id': 'source', 'uri': 'synthetic://editor', 'content': 'Synthetic evidence only.'}])
        self.service = Service(self.store)
        self.writer = self.store.create_grant('synthetic editor', ['read', 'write', 'correct'])
        self.reader = self.store.create_grant('synthetic independent reader', ['read'])
        self.digest = field_contract.catalog()['digest_sha256']

    def tearDown(self):
        self.store.close()

    def call(self, name, **args):
        return self.service.call(name, args, self.writer)

    def update(self, field_id='contact.email', **overrides):
        result = {'field': field_id, 'catalog_digest': self.digest, 'state': 'known',
            'validity_end': 'unknown', 'valid_from': None, 'valid_to': None,
            'time_precision': 'unknown', 'context': {}}
        result.update(overrides)
        return result

    def correct(self, target='email', **overrides):
        args = {'target_id': target, 'expected_heads': [target], 'reason': 'Synthetic sourced correction',
            'request_id': 'correction', 'value': {'kind': 'email', 'address': 'new@example.org'},
            'field_update': self.update()}
        args.update(overrides)
        return self.call('memory_correct', **args)

    def seed_email(self):
        self.store.submit([field('contact.email', {'kind': 'email', 'address': 'old@example.org'}, 'email')])

    def test_independent_clients_discover_same_contract_and_read_projection(self):
        self.seed_email()
        a = self.call('memory_schema')
        b = self.service.call('memory_schema', {}, self.reader)
        self.assertEqual(a['field_catalog'], b['field_catalog'])
        self.assertEqual(a['field_editor']['correction'], 'memory_correct.field_update')
        view = self.call('memory_inspect', target_id='person')['field_view']
        self.assertEqual(view['claims']['email']['qualification'], 'explicit_v1')
        self.assertEqual(view['fields']['contact.phone']['empty_state'], 'not_recorded')
        selected = self.call('memory_inspect', target_id='email')['field_view']
        self.assertFalse(selected['coverage']['complete'])
        self.assertEqual(selected['fields']['contact.phone']['empty_state'], 'not_in_selection')

    def test_projection_preserves_legacy_and_unmapped_without_qualification(self):
        legacy = field('contact.email', {'kind': 'email', 'address': None}, 'legacy')
        legacy.pop('provenance')
        unmapped = dict(legacy, id='unmapped', predicate='legacy:unknown', value='Original text')
        self.store.submit([legacy, unmapped])
        view = self.call('memory_inspect', target_id='person')['field_view']
        self.assertEqual(view['claims']['legacy']['state'], 'legacy_unspecified')
        self.assertEqual(view['claims']['legacy']['qualification'], 'legacy_unqualified')
        self.assertIn('unmapped', view['unmapped_claim_ids'])
        self.assertNotIn('provenance', self.store.read('assertion', 'legacy'))

    def test_partial_projection_cannot_claim_global_absence(self):
        entity = self.store.get_entity('person')
        view = field_contract.project(entity, [], complete=False)
        self.assertFalse(view['coverage']['complete'])
        self.assertEqual(view['fields']['contact.email']['empty_state'], 'not_in_selection')

    def test_known_unknown_na_changes_are_sourced_and_history_retained(self):
        self.seed_email()
        receipt = self.correct(value={'kind': 'email', 'address': None}, field_update=self.update(state='unknown'))
        current = self.store.query(subject='person', predicate='rm:contact-point')['assertions'][0]
        self.assertEqual(field_contract.declaration(current)['state'], 'unknown')
        self.assertEqual(current['predecessors'], ['email'])
        self.assertEqual(len(current['source_ids']), 2)
        self.assertFalse(current['human_verified'])
        again = self.correct(value={'kind': 'email', 'address': None}, field_update=self.update(state='unknown'))
        self.assertEqual(receipt['operation_id'], again['operation_id'])
        self.assertTrue(again['duplicate'])
        self.correct(target=current['id'], expected_heads=[current['id']], request_id='na',
            value={'kind': 'email', 'address': None}, field_update=self.update(state='not_applicable'))
        self.assertEqual(self.store.read('assertion', 'email')['value']['address'], 'old@example.org')

    def test_correct_explicit_time_does_not_infer_ongoing(self):
        self.seed_email()
        update = self.update(valid_from='2026-05-02', time_precision='day', validity_end='ongoing')
        update.pop('valid_to')
        self.correct(field_update=update)
        row = self.store.query(subject='person', predicate='rm:contact-point')['assertions'][0]
        self.assertNotIn('valid_to', row)
        self.assertEqual(field_contract.declaration(row)['validity_end'], 'ongoing')
        self.assertIsNone(self.store.read('assertion', 'email')['valid_from'])

    def test_stale_catalog_wrong_field_and_context_fail_without_change(self):
        self.seed_email()
        before = self.store.status()['known_position']
        for update in (self.update(catalog_digest='0' * 64), self.update(field='contact.phone'),
                       self.update(context={'human_verified': True}), self.update(state='unknown')):
            with self.subTest(update=update):
                with self.assertRaises(ValidationError): self.correct(field_update=update)
                self.assertEqual(before, self.store.status()['known_position'])
                self.assertEqual(self.store.read('assertion', 'email')['value']['address'], 'old@example.org')

    def test_legacy_explicit_qualification_preserves_original_metadata(self):
        legacy = field('contact.email', {'kind': 'email', 'address': 'old@example.org'}, 'email')
        legacy['provenance'] = {'knowledge': None, 'method': 'legacy capture'}
        self.store.submit([legacy])
        self.correct()
        row = self.store.query(subject='person', predicate='rm:contact-point')['assertions'][0]
        self.assertEqual(field_contract.declaration(row)['field'], 'contact.email')
        self.assertEqual(row['provenance']['method'], 'legacy capture')
        self.assertIsNone(self.store.read('assertion', 'email')['provenance']['knowledge'])

    def test_updates_cannot_change_withdrawal_meaning_or_revive_wrong_type(self):
        self.seed_email()
        with self.assertRaises(ValidationError): self.correct(operation='retract')
        self.store.submit([field('identity.type', 'topic', 'new-type')])
        with self.assertRaises(ValidationError): self.correct()
        receipt = self.call('memory_correct', target_id='email', expected_heads=['email'],
            reason='Withdraw unchanged claim after reclassification', request_id='withdraw', operation='retract')
        self.assertTrue(receipt['operation_id'])
        self.assertEqual(self.store.query(subject='person', predicate='rm:contact-point')['assertions'], [])

    def test_permission_and_stale_heads_do_not_mutate(self):
        self.seed_email()
        args = dict(target_id='email', expected_heads=['email'], reason='Synthetic reason', request_id='denied',
                    value={'kind': 'email', 'address': 'a@example.org'}, field_update=self.update())
        with self.assertRaises(AuthorizationError): self.service.call('memory_correct', args, self.reader)
        self.correct()
        with self.assertRaises(ConflictError): self.correct(request_id='stale')
        self.store.revoke_grant(self.writer)
        with self.assertRaises(AuthorizationError): self.call('memory_correct', **args)

    def test_creation_digest_and_atomic_required_fields(self):
        entity = {'type': 'entity', 'id': 'new', 'entity_type': 'person', 'label': 'Avery Chen'}
        actions = [entity, field('identity.type', 'person', 'new-type', 'new'),
                   field('identity.name', 'Avery Chen', 'new-name', 'new')]
        with self.assertRaises(ValidationError): self.call('memory_submit', actions=actions, catalog_digest='0' * 64)
        with self.assertRaises(ValidationError): self.call('memory_submit', actions=actions[:-1], catalog_digest=self.digest)
        self.assertIsNone(self.store.get_entity('new'))
        result = self.call('memory_submit', actions=actions, catalog_digest=self.digest, request_id='create')
        self.assertTrue(self.call('memory_submit', actions=actions, catalog_digest=self.digest, request_id='create')['duplicate'])
        self.assertEqual(len(self.store.search_entities('Avery Chen')['entities']), 2)
        self.assertEqual(self.store.query(subject='new', predicate='rm:contact-point')['assertions'], [])
        self.assertTrue(result['operation_id'])

    def test_committed_capture_recovers_exact_receipt_after_catalog_change(self):
        actions = [field('identity.description', 'Synthetic note', 'description')]
        args = dict(actions=actions, catalog_digest=self.digest, request_id='committed')
        original = self.call('memory_submit', **args)
        changed = field_contract.catalog(); changed['digest_sha256'] = 'a' * 64
        with patch('refactoredmemory.field_contract.catalog', return_value=changed):
            retry = self.call('memory_submit', **args)
            self.assertTrue(retry['duplicate'])
            self.assertEqual(original['operation_id'], retry['operation_id'])
            with self.assertRaises(ConflictError): self.call('memory_submit', **dict(args, catalog_digest='a' * 64))
            with self.assertRaises(ValidationError): self.call('memory_submit', **dict(args, request_id='new-stale'))
            self.store.revoke_grant(self.writer)
            with self.assertRaises(AuthorizationError): self.call('memory_submit', **args)

    def test_suppression_and_malformed_historical_tags_are_conservative(self):
        entity = self.store.get_entity('person')
        view = field_contract.project(entity, [], complete=True, administrative_suppression=True)
        self.assertFalse(view['coverage']['complete'])
        self.assertEqual(view['fields']['relationship.employed-by']['empty_state'], 'not_in_selection')
        for bad in (None, {}, {'field': []}, {'schema': field_contract.SCHEMA, 'revision': 1,
                'field': 'contact.email', 'state': 'known', 'validity_end': {}}):
            row = field('contact.email', {'kind': 'email', 'address': 'a@example.org'}, 'historical')
            row['provenance']['knowledge']['qualifiers']['field_contract'] = bad
            result = field_contract.project(entity, [row], complete=True)
            self.assertIn('historical', result['unmapped_claim_ids'])

    def test_private_capture_rejects_padding_and_malformed_shapes(self):
        a = field('identity.description', 'Synthetic note', 'description')
        base = {'actions': [a], 'catalog_digest': self.digest}
        self.assertTrue(field_contract.is_typed_capture(base))
        for extra in ({'type': 'source', 'id': 'unrelated'},
                      {'type': 'entity', 'id': 'unrelated', 'entity_type': 'person'},
                      {'type': 'entity', 'id': 'person', 'entity_type': 'source-document'},
                      {'type': []}, None):
            self.assertFalse(field_contract.is_typed_capture(dict(base, actions=[a, extra])))
        bad = copy.deepcopy(a); bad['source_ids'] = None
        self.assertTrue(field_contract.is_typed_capture(dict(base, actions=[bad])))
        # Shape/reference checks still belong to the core, and commit nothing.
        with self.assertRaises(ValidationError): self.call('memory_submit', actions=[bad], catalog_digest=self.digest)

    @unittest.skipUnless(shutil.which('node'), 'Node is a frontend build/qualification dependency, not a production runtime dependency')
    def test_actual_javascript_client_payloads_reach_core_without_schema_copy(self):
        fixture = Path(__file__).parent / 'fixtures/field-editor-client.mjs'
        result = subprocess.run(['node', str(fixture)], input=json.dumps(field_contract.catalog()),
            text=True, capture_output=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['legacyValue'], '2026-05')
        self.assertNotIn('calendar_period', data['payload']['value'])
        self.call('memory_submit', **data['create'])
        self.assertTrue(self.call('memory_submit', **data['create'])['duplicate'])
        self.call('memory_submit', **data['additional'])
        row = self.store.read('assertion', 'client-date')
        self.assertEqual(row['value']['date'], '2026-05')
        self.assertEqual(row['value']['precision'], 'month')
        self.assertIsNone(row['valid_from'])
        self.assertEqual(field_contract.declaration(self.store.read('assertion', 'client-unknown'))['state'], 'unknown')

    def test_ending_relationship_and_reclassification_preserve_meaning(self):
        a = field('relationship.employed-by', None, 'employment')
        a.pop('value'); a['object'] = 'org'
        a['provenance']['knowledge']['kind'] = 'relationship'
        a['provenance']['knowledge']['category'] = field_contract.catalog()['fields']['relationship.employed-by']['category']
        a['valid_from'] = '2026-05-01'; a['time_precision'] = 'day'
        self.store.submit([a])
        self.call('memory_correct', target_id='employment', expected_heads=['employment'],
            operation='invalidate', valid_to='2026-06-01', reason='Synthetic supported employment end', request_id='end')
        current = self.store.query(subject='person', predicate='employed-by')['assertions'][0]
        self.assertEqual(current['object'], 'org')
        self.assertEqual(current['valid_from'], '2026-05-01')
        self.assertEqual(current['valid_to'], '2026-06-01')
        self.assertEqual(field_contract.declaration(current)['validity_end'], 'known')
        self.assertIsNone(self.store.read('assertion', 'employment')['valid_to'])
        update = self.update('relationship.invests-in', context={'investment_status': 'discussed', 'amount': None})
        self.call('memory_correct', target_id=current['id'], expected_heads=[current['id']],
            operation='reclassify', predicate='invests-in', object='org', field_update=update,
            reason='Synthetic different claim, not completed funding', request_id='reclassify')
        replacement = self.store.query(subject='person', predicate='invests-in')['assertions'][0]
        self.assertEqual(field_contract.declaration(replacement)['field'], 'relationship.invests-in')
        self.assertEqual(replacement['provenance']['knowledge']['qualifiers']['investment_status'], 'discussed')
        self.assertEqual(self.store.query(subject='person', predicate='employed-by')['assertions'], [])

    def test_two_offline_field_writers_restart_converge_and_restore_fresh_identity(self):
        with tempfile.TemporaryDirectory(prefix='rm-synthetic-field-lifecycle-') as directory:
            root = Path(directory)
            a = Store(root / 'a.sqlite3', store_id='synthetic-fields', peer_id='a')
            b = Store(root / 'b.sqlite3', store_id='synthetic-fields', peer_id='b')
            try:
                ia, ib = a.identity(), b.identity()
                a.admit_peer(ib['peer_id'], ib['key_hex']); b.admit_peer(ia['peer_id'], ia['key_hex'])
                a.submit([
                    {'type': 'entity', 'id': 'person', 'entity_type': 'person', 'label': 'Synthetic offline person'},
                    {'type': 'source', 'id': 'source', 'uri': 'synthetic://offline', 'content': 'Synthetic offline evidence.'},
                    field('identity.type', 'person', 'type'),
                    field('identity.name', 'Synthetic offline person', 'name'),
                    field('contact.email', {'kind': 'email', 'address': 'original@example.org'}, 'original')])
                b.receive(a.export_operations()['operations'], 'a')
                ta = a.create_grant('synthetic offline client A', ['read', 'write', 'correct'])
                tb = b.create_grant('synthetic offline client B', ['read', 'write', 'correct'])
                for store, token, state, value in ((a, ta, 'known', 'offline-a@example.org'), (b, tb, 'unknown', None)):
                    Service(store).call('memory_correct', {'target_id': 'original', 'expected_heads': ['original'],
                        'reason': 'Independent synthetic offline correction', 'request_id': 'offline-' + store.peer_id,
                        'value': {'kind': 'email', 'address': value},
                        'field_update': self.update(state=state)}, token)
                self.assertNotEqual(a.status()['frontier'], b.status()['frontier'])
                a.close(); b.close()

                a = Store(root / 'a.sqlite3'); b = Store(root / 'b.sqlite3')
                for _ in range(2):
                    a.receive(b.export_operations()['operations'], 'b')
                    b.receive(a.export_operations()['operations'], 'a')
                self.assertEqual(a.status()['frontier'], b.status()['frontier'])
                rows = a.query(subject='person', predicate='rm:contact-point')['assertions']
                self.assertEqual(len(rows), 2)
                self.assertEqual({field_contract.declaration(r)['state'] for r in rows}, {'known', 'unknown'})
                snapshot = root / 'consistent.sqlite3'; a.backup(snapshot)
                with Store.restore(snapshot, root / 'recovered.sqlite3') as recovered:
                    self.assertNotIn(recovered.peer_id, {'a', 'b'})
                    self.assertEqual(recovered.read('assertion', 'original')['value']['address'], 'original@example.org')
                    self.assertEqual({r['id'] for r in rows}, {r['id'] for r in recovered.query(subject='person', predicate='rm:contact-point')['assertions']})
                    with self.assertRaises(AuthorizationError): Service(recovered).call('memory_schema', {}, ta)
            finally:
                a.close(); b.close()

    def test_corrected_name_and_aliases_are_searchable_without_rewriting_identity(self):
        self.store.submit([field('identity.name', 'Avery Chen', 'name')])
        self.correct(target='name', expected_heads=['name'], value='Avery Rivera', field_update=self.update('identity.name'))
        entity = self.store.get_entity('person')
        self.assertEqual(entity['label'], 'Avery Chen')
        self.assertEqual(entity['display_label'], 'Avery Rivera')
        self.assertEqual(self.store.read('entity', 'person')['label'], 'Avery Chen')
        self.assertEqual(self.store.search_entities('Rivera')['entities'][0]['id'], 'person')
        self.assertEqual(self.store.search_entities('Avery Chen')['entities'][0]['id'], 'person')
        self.store.submit([field('identity.aliases', ['Synthetic Known Alias'], 'aliases')])
        self.assertEqual(self.store.search_entities('Known Alias')['entities'][0]['id'], 'person')
        self.store.submit([field('identity.name', 'Avery Different', 'competing-name')])
        ambiguous = self.store.get_entity('person')
        self.assertTrue(ambiguous['display_name']['conflicted'])
        self.assertEqual(ambiguous['display_label'], 'Avery Chen')
        self.assertEqual(self.store.search_entities('Avery Different')['entities'][0]['id'], 'person')

    def test_future_and_ended_names_do_not_replace_display_label(self):
        a = field('identity.name', 'Future Name', 'future')
        a.update(valid_from='2999-01-01', time_precision='day')
        self.store.submit([a])
        self.assertEqual(self.store.get_entity('person')['display_label'], 'Avery Chen')
        old = field('identity.name', 'Ended Name', 'ended')
        old.update(valid_from='2000-01-01', valid_to='2001-01-01', time_precision='day')
        old['provenance']['knowledge']['qualifiers']['field_contract']['validity_end'] = 'known'
        self.store.submit([old])
        self.assertEqual(self.store.get_entity('person')['display_label'], 'Avery Chen')
        self.assertEqual(self.store.search_entities('Future Name')['entities'], [])
        alias = field('identity.aliases', ['Past Alias'], 'past-alias')
        alias.update(valid_from='2000-01-01', valid_to='2001-01-01', time_precision='day')
        alias['provenance']['knowledge']['qualifiers']['field_contract']['validity_end'] = 'known'
        self.store.submit([alias])
        self.assertEqual(self.store.search_entities('Past Alias')['entities'], [])

    def test_historical_graph_does_not_leak_later_names_or_basis_ids(self):
        self.store.submit([field('identity.name', 'Earlier Name', 'earlier-name')])
        frontier = self.store.status()['frontier']
        self.correct(target='earlier-name', expected_heads=['earlier-name'], value='Later Name',
                     field_update=self.update('identity.name'))
        current = self.store.get_entity('person')
        self.assertEqual(current['display_label'], 'Later Name')
        old = self.store.traverse('person', frontier=frontier)['entities'][0]
        self.assertEqual(old['display_label'], 'Earlier Name')
        self.assertEqual(old['display_name']['assertion_ids'], ['earlier-name'])

    def test_preferred_unknown_name_does_not_promote_an_unpreferred_guess(self):
        self.store.submit([field('identity.name', 'Earlier Name', 'original-name')])
        owner = self.store.create_grant('synthetic owner correction', ['read', 'write', 'correct'], kind='owner')
        result = self.service.call('memory_correct', {'target_id': 'original-name', 'expected_heads': ['original-name'],
            'reason': 'Owner states the name is explicitly unknown', 'request_id': 'owner-unknown',
            'value': None, 'field_update': self.update('identity.name', state='unknown')}, owner)
        self.store.submit([field('identity.name', 'Unpreferred Agent Guess', 'guess')],
                          actor={'id': 'synthetic-other-agent', 'kind': 'agent'})
        entity = self.store.get_entity('person')
        self.assertEqual(entity['display_label'], 'Avery Chen')
        self.assertTrue(entity['display_name']['unresolved'])
        self.assertNotIn('guess', entity['display_name']['assertion_ids'])
        self.assertTrue(set(entity['display_name']['assertion_ids']) <= set(result['action_ids']))

if __name__ == '__main__':
    unittest.main()
