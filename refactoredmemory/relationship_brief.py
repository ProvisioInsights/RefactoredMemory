"""Bounded, client-selected views over existing pinned derived artifacts."""
from collections import deque
import re

from .store import ConflictError, ValidationError

SCHEMA = 'refactoredmemory.relationship-brief:v1'
ID = {'type': 'string', 'minLength': 1, 'maxLength': 256}
VIEW = {'type': 'object', 'additionalProperties': False,
        'required': ['schema', 'groups'], 'properties': {
    'schema': {'const': SCHEMA},
    'groups': {'type': 'array', 'minItems': 1, 'maxItems': 4, 'items': {
        'type': 'object', 'additionalProperties': False, 'required': ['title', 'items'], 'properties': {
            'title': {'type': 'string', 'minLength': 1, 'maxLength': 80},
            'items': {'type': 'array', 'minItems': 1, 'maxItems': 6, 'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['entity_id', 'claim_ids', 'why'], 'properties': {
                    'entity_id': ID,
                    'claim_ids': {'type': 'array', 'minItems': 1, 'maxItems': 8,
                                  'uniqueItems': True, 'items': ID},
                    'why': {'type': 'string', 'minLength': 1, 'maxLength': 500}}}}}}}}}


def validate_value(workspace, value):
    from .service import validate, INPUTS, FRONTIER
    validate(value, {'type': 'object', 'required': ['title', 'text', 'inputs', 'input_frontier', 'artifact_id', 'view'],
                     'properties': {'title': ID, 'text': {'type': 'string', 'minLength': 1, 'maxLength': 16384},
                                    'artifact_id': ID, 'inputs': INPUTS, 'input_frontier': FRONTIER, 'view': VIEW}})
    if any(not isinstance(ref.get('sha256'), str) or re.fullmatch('[a-f0-9]{64}', ref['sha256']) is None for ref in value['inputs']):
        raise ValidationError('Saved brief inputs must include actual pinned digests')
    workspace.store._view(frontier=value['input_frontier'])
    if any(not workspace.store._reference_visible(ref['kind'], ref['id'], value['input_frontier']) for ref in value['inputs']):
        raise ValidationError('Saved brief inputs must exist at its declared frontier')


def admitted_contribution(artifact):
    actor = artifact.get('actor') if isinstance(artifact.get('actor'), dict) else {}
    provenance = artifact.get('provenance') if isinstance(artifact.get('provenance'), dict) else {}
    supplied = provenance.get('contribution', {})
    reported = supplied.get('reported', {}) if isinstance(supplied, dict) else {}
    keys = ('application', 'connector', 'model', 'model_version', 'method', 'method_version', 'task_id')
    safe = {k: v for k, v in reported.items() if k in keys and isinstance(v, str) and len(v) <= 256} if isinstance(reported, dict) else {}
    return {'connection': {'id': actor.get('id'), 'kind': actor.get('kind'),
                           'basis': 'admitted operation actor; not current viewer'},
            'reported': safe, 'reported_basis': 'client supplied; not independently verified'}


def capability():
    return {'schema': SCHEMA, 'write': 'memory_derive.view', 'read': 'memory_graph.brief_id',
            'max_records': 6, 'max_claims': 24, 'max_path_hops': 2, 'max_path_identities': 13,
            'meaning': 'Client-selected interpretation over active pinned inputs; not exhaustive relevance or verification.'}


def project(workspace, start, view, inputs):
    # Historical/peer-supplied artifacts must pass the same shape checks as calls.
    from .service import validate
    validate(view, VIEW)
    store = workspace.store
    frontier = store.status()['frontier']
    items = [item for group in view['groups'] for item in group['items']]
    records = [item['entity_id'] for item in items]
    ids = list(dict.fromkeys(rid for item in items for rid in item['claim_ids']))
    if len(items) > 6 or len(ids) > 24 or len(set(records)) != len(records) or start in records:
        raise ValidationError('Select at most six distinct related records and 24 claims')
    allowed = {ref['id'] for ref in inputs if ref['kind'] == 'assertion'}
    if not set(ids) <= allowed:
        raise ValidationError('Every selected claim must be a pinned assertion input')
    claims = {}
    for rid in ids:
        _, claim = workspace.locate(rid)
        if claim is None:
            raise ValidationError('Selected evidence must be an active assertion')
        claims[rid] = claim
    entities, paths = {start: store.get_entity(start)}, {}
    if entities[start] is None:
        raise ValidationError('The brief subject must be an entity')
    for item in items:
        rows = [claims[rid] for rid in item['claim_ids']]
        adjacency = {}
        for row in rows:
            if row.get('object'):
                adjacency.setdefault(row['subject'], []).append((row['object'], row['id']))
                adjacency.setdefault(row['object'], []).append((row['subject'], row['id']))
        queue, found = deque([(start, [start], [])]), []
        while queue:
            node, nodes, links = queue.popleft()
            if node == item['entity_id']:
                found.append((nodes, links))
                continue
            if len(links) == 2:
                continue
            for other, claim_id in adjacency.get(node, []):
                if other not in nodes:
                    queue.append((other, nodes + [other], links + [claim_id]))
        if not found:
            raise ValidationError('Each selected record needs a named relationship path of at most two hops')
        nodes = list(dict.fromkeys(eid for path, _ in found for eid in path))
        links = list(dict.fromkeys(rid for _, path in found for rid in path))
        for row in rows:
            if row['subject'] not in nodes or row.get('object') and row['id'] not in links:
                raise ValidationError('Supporting claims must belong to the selected path')
        for eid in nodes:
            entity = store.get_entity(eid)
            if entity is None:
                raise ConflictError('A selected identity is no longer available')
            entities[eid] = entity
        paths[item['entity_id']] = {'entity_ids': nodes, 'claim_ids': links,
                                    'routes': [{'entity_ids': n, 'claim_ids': r} for n, r in found]}
    if len(entities) > 13:
        raise ValidationError('Narrow the selected paths to at most thirteen identities')
    edges, references = [], []
    for row in claims.values():
        keys = ('id', 'subject', 'predicate', 'object', 'source_ids', 'actor', 'status', 'preferred',
                'conflicts', 'known_position', 'valid_from', 'valid_to', 'time_precision', 'knowledge')
        reference = {**{k: row[k] for k in keys if k in row}, 'review': workspace.review_state(row)}
        references.append(reference)
        if row.get('object'):
            edges.append(reference)
    if store.status()['frontier'] != frontier:
        raise ConflictError('Memory changed while preparing the view; reload')
    return {'entities': list(entities.values()), 'edges': edges, 'claims': references, 'paths': paths, 'start': start,
            'frontier': frontier, 'known_position': store.status()['known_position'],
            'coverage': {'complete': False, 'depth': 2, 'limit': 6, 'selection_complete': True,
                         'meaning': 'Explicit client selection only; not all matching records or independent confirmation.'},
            'meaning': 'Actual sourced paths; the client explanation is separate interpretation.'}
