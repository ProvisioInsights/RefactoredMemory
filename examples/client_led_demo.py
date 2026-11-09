"""Synthetic graph/workflow fixture. Never opens a personal memory store."""
from __future__ import annotations

import tempfile
from pathlib import Path

from refactoredmemory import knowledge
from refactoredmemory.service import Service
from refactoredmemory.store import Store


def seed(store):
    people = [('alex', 'Alex Morgan'), ('jamie', 'Jamie Chen'), ('riley', 'Riley Park')]
    entities = [('project', 'Example Project', 'project'), ('northstar', 'Northstar', 'organization'),
                ('pinebridge', 'Pinebridge', 'organization')] + [(i, n, 'person') for i, n in people]
    actions = [{'type': 'source', 'id': 'meeting', 'uri': 'synthetic://meeting-2026-11-07',
                'content': 'Alex asked for the project overview and said they would review it next week. '
                'Jamie and Riley participate in Example Project. Alex was introduced by Jamie. '
                'Alex works at Northstar and Jamie works at Pinebridge. These are synthetic examples, not real people.',
                'metadata': {'synthetic': True, 'date': '2026-11-07'}}]
    for rid, name, kind in entities:
        actions += [{'type': 'entity', 'id': rid, 'entity_type': kind, 'label': name},
                    {'type': 'assertion', 'id': rid + '-type', 'subject': rid, 'predicate': knowledge.TYPE_PREDICATE,
                     'value': kind, 'source_ids': ['meeting'], 'provenance': {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'fact'}}}]
    for rid, a, predicate, b in [('alex-project', 'alex', 'participant-in', 'project'),
        ('jamie-project', 'jamie', 'participant-in', 'project'), ('riley-project', 'riley', 'participant-in', 'project'),
        ('intro', 'alex', 'introduced-by', 'jamie'), ('alex-job', 'alex', 'employed-by', 'northstar'),
        ('jamie-job', 'jamie', 'employed-by', 'pinebridge')]:
        qualifiers = {'role': 'expressed interest'} if rid == 'alex-project' else {}
        actions.append({'type': 'assertion', 'id': rid, 'subject': a, 'predicate': predicate, 'object': b,
                        'source_ids': ['meeting'], 'valid_from': '2026-11-07', 'time_precision': 'day',
                        'provenance': {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'relationship',
                        'category': knowledge.PREDICATES[predicate]['category'], 'qualifiers': qualifiers}}})
    actions += [{'type': 'assertion', 'id': 'project-note', 'subject': 'project', 'predicate': 'rm:project-note',
                 'value': 'Synthetic project overview for graph and processing qualification.', 'source_ids': ['meeting'],
                 'provenance': {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'fact'}}},
                {'type': 'assertion', 'id': 'review-example', 'subject': 'alex', 'predicate': 'rm:enrichment-review',
                 'value': {'status': 'needs-review', 'reason': 'Interest is not evidence of a completed investment.'},
                 'source_ids': ['meeting'], 'provenance': {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'fact'}}}]
    store.submit(actions, request_id='synthetic-graph-seed')
    store.enable_knowledge_profile()
    return 'project'


def main():
    with tempfile.TemporaryDirectory(prefix='rm-client-led-demo-') as directory, Store(Path(directory) / 'synthetic.sqlite3') as store:
        seed(store)
        token = store.create_grant('synthetic external processor', ['read', 'write', 'correct'])
        service = Service(store)
        job = service.call('memory_task', {'action': 'create', 'subject': 'project', 'title': 'Summarize the synthetic meeting',
            'inputs': [{'kind': 'source', 'id': 'meeting'}], 'request_id': 'job'}, token)['job_id']
        revisions = lambda: [r['id'] for r in store.query(subject=job, predicate='rm:task-state')['assertions']]
        service.call('memory_task', {'action': 'claim', 'job_id': job, 'expected_revisions': revisions(), 'request_id': 'claim'}, token)
        result = service.call('memory_derive', {'subject': 'project', 'title': 'Synthetic meeting brief',
            'text': 'Alex requested an overview. Interest is recorded; investment is not confirmed.',
            'inputs': [{'kind': 'source', 'id': 'meeting'}], 'input_frontier': store.status()['frontier'],
            'reported': {'application': 'Synthetic external runner', 'model': 'synthetic reported model', 'task_id': job}, 'request_id': 'brief'}, token)
        outputs = [rid for rid in result['action_ids'] if store.read('assertion', rid)]
        service.call('memory_task', {'action': 'complete', 'job_id': job, 'expected_revisions': revisions(), 'output_ids': outputs, 'request_id': 'complete'}, token)
        if service.call('memory_artifacts', {'subject': 'project'}, token)[0]['freshness']['state'] != 'current':
            raise RuntimeError('Synthetic brief inputs unexpectedly became stale')
        print('PASS: synthetic external-client work, attributed brief, pinned inputs and completion; no internal model call.')


if __name__ == '__main__':
    main()
