"""Client-led work and review over the ordinary immutable memory journal.

No model, network client, second database, or authority from supplied metadata.
"""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser

from . import knowledge
from .store import AuthorizationError, ConflictError, ValidationError, canonical

MANAGED = {'rm:task-state', 'rm:comment', 'rm:review', 'rm:derived-memory'}
PROFILE = 'refactoredmemory.workspace:v1'
MISSING = object()


def captured_text(text):
    """Remove only known import envelopes; retain the unchanged source record."""
    original, details = text, {}
    decoder = json.JSONDecoder()
    try:
        value, end = decoder.raw_decode(text.lstrip())
        if (isinstance(value, dict) and {'part', 'parts', 'source_identity', 'version_sha256'} <= value.keys()
                and set(value) <= {'part', 'parts', 'source_identity', 'version_sha256'}):
            text = text.lstrip()[end:].lstrip()
            value, end = decoder.raw_decode(text)
        if (isinstance(value, dict) and value.get('untrusted_source_content') is True
                and value.get('fidelity') == 'source text' and 'source_identity' in value):
            details = dict(value.get('metadata') or {}, title=value.get('title'))
            return text.lstrip()[end:].lstrip(), details
    except (ValueError, TypeError):
        pass
    return original, details


def readable(text):
    text, _ = captured_text(text)
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            if isinstance(value.get('body'), dict) and isinstance(value['body'].get('content'), str):
                text = value['body']['content']
            elif isinstance(value.get('content'), str):
                text = value['content']
    except (ValueError, TypeError):
        pass
    if any(tag in text.lower() for tag in ('<html', '<div', '<p>', '<table', '<body')):
        class Plain(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.parts, self.hidden = [], 0
            def handle_starttag(self, tag, attrs):
                if tag in ('script', 'style'):
                    self.hidden += 1
                elif tag in ('p', 'div', 'br', 'tr'):
                    self.parts.append('\n')
            def handle_endtag(self, tag):
                if tag in ('script', 'style') and self.hidden:
                    self.hidden -= 1
            def handle_data(self, data):
                if not self.hidden:
                    self.parts.append(data)
        parser = Plain()
        parser.feed(text)
        text = ''.join(parser.parts)
    # Display protection only; originals and source hashes are untouched.
    import re
    text = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----', '[private key withheld]', text, flags=re.S)
    text = re.sub(r'(?im)^\s*(authorization|access_token|refresh_token|client_secret|password|api[_ -]?key)\s*[:=].*$', '[credential assignment withheld]', text)
    return text.strip()


def annotation(layer='workspace'):
    return {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'fact',
            'qualifiers': {'layer': layer}, 'evidence_status':
            'Attributed contribution; admission is not human verification.'}}


def fact(rid, subject, predicate, value, sources, **fields):
    return dict(type='assertion', id=rid, subject=subject, predicate=predicate,
                value=value, source_ids=sorted(set(sources)), time_precision='unknown',
                provenance=annotation(), **fields)


def contribution(actor, reported=None):
    return {'schema': PROFILE, 'connection': {'id': actor['id'], 'kind': actor['kind'],
            'basis': 'authenticated grant'}, 'reported': reported or {},
            'reported_basis': 'client supplied; not independently verified'}


class Workspace:
    def __init__(self, store, actor, authorize=None):
        self.store, self.actor = store, actor
        self.argument_digest = None
        self.authorize = authorize

    def prepare(self, method, arguments):
        self.argument_digest = hashlib.sha256(canonical(arguments).encode()).hexdigest()
        rid = self.identity(method, arguments['request_id'])
        with self.store._lock:
            old = self.store.db.execute('SELECT operation_id FROM requests WHERE actor=? AND id=?',
                (self.actor['id'], 'workspace:' + rid)).fetchone()
            if old is None:
                return None
            source = self.store.read('source', rid + '-request')
            if not source or source['metadata']['argument_digest'] != self.argument_digest:
                raise ConflictError('Request ID reused with different arguments')
            row = self.store.db.execute('SELECT body,position FROM operations WHERE id=?', (old[0],)).fetchone()
            body = json.loads(row['body'])
            result = {'operation_id': old[0], 'known_position': row['position'],
                      'action_ids': [a['id'] for a in body['actions']], 'duplicate': True}
            if method.startswith('task:'):
                result['job_id'] = next(a['subject'] for a in body['actions'] if a.get('predicate') == 'rm:task-state')
            return result

    def identity(self, method, request_id):
        return 'rm-' + hashlib.sha256(canonical([self.actor['id'], method, request_id]).encode()).hexdigest()[:40]

    def interaction(self, rid, text):
        return {'type': 'source', 'id': rid + '-source', 'uri': 'urn:refactoredmemory:interaction:' + rid,
                'content': text, 'metadata': {'source_kind': 'workspace interaction', 'schema': PROFILE,
                'meaning': 'Evidence of this action, not independent evidence of a world claim.'}}

    def submit(self, method, request_id, actions, conditions=(), reported=None):
        rid = self.identity(method, request_id)
        actions = [{'type': 'source', 'id': rid + '-request',
                    'uri': 'urn:refactoredmemory:request:' + rid, 'content': 'Workspace request: ' + method,
                    'metadata': {'argument_digest': self.argument_digest, 'schema': PROFILE}}] + actions
        for action in actions:
            if action['type'] == 'assertion':
                action.setdefault('provenance', annotation())['contribution'] = contribution(self.actor, reported)
        return self.store.submit(actions, actor=self.actor,
            request_id='workspace:' + self.identity(method, request_id), expected_heads=conditions, authorize=self.authorize)

    def heads(self, subject, predicate):
        result = self.store.query(subject=subject, predicate=predicate, limit=1000)
        if not result['coverage']['complete']:
            raise ConflictError('Too many heads for a safe edit')
        return result['assertions']

    def guard(self, subject, predicate, rows):
        return {'subject': subject, 'predicate': predicate, 'ids': [r['id'] for r in rows]}

    def locate(self, rid):
        claim = self.store.read('assertion', rid)
        if claim:
            rows = self.store.query(subject=claim['subject'], predicate=claim['predicate'], limit=1000)
            current = next((x for x in rows['assertions'] if x['id'] == rid), None)
            if current is None:
                raise ConflictError('Claim is unavailable or no longer active')
            return claim['subject'], current
        entity = self.store.get_entity(rid)
        if entity is None:
            raise ValidationError('Unknown target')
        return rid, None

    def inputs(self, refs):
        """Pin actual source/assertion bytes and reject stale/deleted inputs."""
        pinned, sources, conditions = [], set(), []
        for ref in refs:
            if ref['kind'] == 'source':
                row = self.store.get_source(ref['id'])
                if row is None:
                    raise ValidationError('Input source unavailable')
                sources.add(ref['id'])
            else:
                _, row = self.locate(ref['id'])
                if row is None:
                    raise ValidationError('Input must be an assertion')
                sources.update(row['source_ids'])
                conditions.append(self.guard(row['subject'], row['predicate'], self.heads(row['subject'], row['predicate'])))
                row = self.store.read('assertion', ref['id'])
            digest = hashlib.sha256(canonical(row).encode()).hexdigest()
            if ref.get('sha256') is not None and ref['sha256'] != digest:
                raise ConflictError('Input revision changed')
            pinned.append({'kind': ref['kind'], 'id': ref['id'], 'sha256': digest})
            if ref['kind'] == 'source':
                conditions.append({'kind': 'source', 'id': ref['id'], 'sha256': digest})
        if len(sources) > 90:
            raise ValidationError('Narrow the input set to at most 90 evidence sources')
        return pinned, sorted(sources), conditions

    def freshness(self, refs):
        try:
            self.inputs(refs)
            return {'state': 'current', 'basis': 'Inputs still available, unchanged and active; not a truth assessment.'}
        except (ValidationError, ConflictError):
            return {'state': 'stale', 'basis': 'An input is unavailable, corrected or changed; regenerate from current evidence.'}

    def comment(self, target_id, text, request_id, reported=None):
        subject, claim = self.locate(target_id)
        rid = self.identity('comment', request_id)
        source = self.interaction(rid, text)
        action = fact(rid, subject, 'rm:comment', {'target_id': target_id,
                      'target_kind': 'assertion' if claim else 'entity', 'text': text}, [source['id']])
        return self.submit('comment', request_id, [source, action], reported=reported)

    def review(self, target_id, disposition, note, request_id, expected_reviews, reported=None):
        if self.actor['kind'] != 'owner':
            raise AuthorizationError('An authenticated owner action is required for owner review')
        subject, claim = self.locate(target_id)
        if claim is None:
            raise ValidationError('Review a specific assertion revision')
        rows = self.heads(subject, 'rm:review')
        target_rows = [r for r in rows if r['value'].get('target_id') == target_id]
        if sorted(expected_reviews) != sorted(r['id'] for r in target_rows):
            raise ConflictError('Review changed; reload')
        rid = self.identity('review', request_id)
        source = self.interaction(rid, note)
        fields = dict(kind='correct', predecessors=[r['id'] for r in target_rows], reason=note) if target_rows else {}
        action = fact(rid, subject, 'rm:review', {'target_id': target_id,
                      'disposition': disposition, 'note': note}, [source['id']], **fields)
        return self.submit('review', request_id, [source, action],
                           [self.guard(subject, 'rm:review', rows)], reported)

    def review_state(self, claim, frontier=None):
        result = self.store.query(subject=claim['subject'], predicate='rm:review', frontier=frontier, limit=1000)
        rows = [r for r in result['assertions'] if isinstance(r.get('value'), dict)
                and r['value'].get('target_id') == claim['id'] and r['actor']['kind'] == 'owner'
                and r['value'].get('disposition') in ('confirmed', 'disputed', 'needs-review')]
        states = {r['value']['disposition'] for r in rows}
        return {'state': next(iter(states)) if len(states) == 1 else 'conflicting' if states else 'unreviewed',
                'human_verified': states == {'confirmed'} and result['coverage']['complete'], 'review_ids': [r['id'] for r in rows],
                'meaning': 'Applies only to this assertion revision.'}

    def correct(self, target_id, expected_heads, reason, request_id, value=MISSING, object=MISSING, reported=None, operation='correct', predicate=None):
        subject, claim = self.locate(target_id)
        if claim is None or claim['predicate'] in MANAGED:
            raise ValidationError('Use the corresponding workspace operation for managed records')
        if operation == 'retract':
            value, object = (claim['value'], MISSING) if 'value' in claim else (MISSING, claim['object'])
        if (value is MISSING) == (object is MISSING):
            raise ValidationError('Supply one corrected value or relationship target')
        if object is not MISSING and 'object' not in claim or value is not MISSING and 'value' not in claim:
            raise ValidationError('Corrections preserve the assertion shape')
        rows = self.heads(subject, claim['predicate'])
        if target_id not in expected_heads or not set(expected_heads) <= {r['id'] for r in rows}:
            raise ConflictError('Correction predecessors are not current heads')
        rid = self.identity('correct', request_id)
        source = self.interaction(rid, reason)
        action = {k: claim[k] for k in ('subject', 'predicate', 'valid_from', 'valid_to', 'time_precision', 'uncertainty') if k in claim}
        action.update(type='assertion', id=rid, kind='retract' if operation in ('retract', 'reclassify') else 'correct', predecessors=expected_heads, reason=reason,
                      source_ids=sorted(set(claim['source_ids'] + [source['id']])), provenance=claim.get('provenance', {}))
        action.update({'object': object} if object is not MISSING else {'value': value})
        actions = [source, action]
        if operation == 'reclassify':
            if not predicate or predicate == claim['predicate'] or predicate in MANAGED:
                raise ValidationError('Select a different supported predicate')
            new = {k: v for k, v in action.items() if k not in ('kind', 'predecessors', 'reason', 'provenance')}
            new.update(id=rid + '-replacement', predicate=predicate)
            profile = {'schema': knowledge.PROFILE, 'kind': 'relationship' if 'object' in new else 'fact',
                       'qualifiers': {'reclassified_from': target_id}}
            if 'object' in new and predicate in knowledge.PREDICATES:
                profile['category'] = knowledge.PREDICATES[predicate]['category']
            new['provenance'] = {'knowledge': profile}
            actions.append(new)
            # Withdrawal names the old meaning; replacement carries the new one.
            action.pop('object', None)
            action.pop('value', None)
            action.update({'object': claim['object']} if 'object' in claim else {'value': claim['value']})
        elif predicate is not None:
            raise ValidationError('Changing a predicate requires explicit reclassification')
        return self.submit('correct', request_id, actions,
                           [self.guard(subject, claim['predicate'], rows)], reported)

    def derive(self, subject, title, text, inputs, input_frontier, request_id, predecessor=None, reported=None):
        self.locate(subject)
        self.store._view(frontier=input_frontier)
        if any(not self.store._reference_visible(r['kind'], r['id'], input_frontier) for r in inputs):
            raise ValidationError('Input does not exist at the declared input frontier')
        pinned, sources, conditions = self.inputs(inputs)
        conditions += self.output_conditions(reported, inputs=inputs)
        rid = self.identity('derive', request_id)
        rows = self.heads(subject, 'rm:derived-memory')
        old = next((r for r in rows if r['id'] == predecessor), None)
        if predecessor and old is None:
            raise ConflictError('Derived artifact changed; reload')
        fields = dict(kind='correct', predecessors=[predecessor], reason='Regenerate from pinned inputs') if predecessor else {}
        action = fact(rid, subject, 'rm:derived-memory', {'title': title, 'text': text,
                      'inputs': pinned, 'input_frontier': input_frontier,
                      'artifact_id': old['value']['artifact_id'] if old else rid}, sources, **fields)
        conditions.append(self.guard(subject, 'rm:derived-memory', rows))
        return self.submit('derive', request_id, [action], conditions, reported)

    def output_conditions(self, reported, inputs=None, sources=None):
        if not reported or not reported.get('task_id'):
            return []
        job = reported['task_id']
        rows = self.heads(job, 'rm:task-state')
        if len(rows) != 1 or rows[0]['value']['status'] != 'running' or rows[0]['value']['assignee'] != self.actor['id']:
            raise AuthorizationError('Output task is not assigned to this connection')
        task = rows[0]['value']
        _, allowed_sources, guards = self.inputs(task['inputs'])
        if inputs and not {(r['kind'], r['id']) for r in inputs} <= {(r['kind'], r['id']) for r in task['inputs']}:
            raise AuthorizationError('Output uses inputs outside the task')
        if sources and not set(sources) <= set(allowed_sources):
            raise AuthorizationError('Output cites evidence outside the task')
        return [self.guard(job, 'rm:task-state', rows)] + guards

    def artifacts(self, subject):
        return [{**r, 'freshness': self.freshness(r['value']['inputs'])}
                for r in self.heads(subject, 'rm:derived-memory')]

    def task(self, action, request_id, job_id=None, subject=None, title=None, inputs=None,
             expected_revisions=None, checkpoint=None, output_ids=None, reported=None):
        rid = self.identity('task:' + action, request_id)
        if action == 'create':
            self.locate(subject)
            pinned, sources, conditions = self.inputs(inputs)
            job_id = self.identity('task:create', request_id) + '-job'
            rows = []
            state = {'status': 'open', 'title': title, 'subject': subject, 'inputs': pinned,
                     'requester': {'id': self.actor['id'], 'kind': self.actor['kind']},
                     'assignee': None, 'checkpoint': {}, 'output_ids': []}
        else:
            rows = self.heads(job_id, 'rm:task-state')
            if not rows or sorted(expected_revisions or []) != sorted(r['id'] for r in rows):
                raise ConflictError('Task changed or conflicted; reload its heads')
            if len(rows) != 1 and (action != 'resolve' or self.actor['kind'] != 'owner'):
                raise ConflictError('Concurrent task claims require owner resolution')
            input_conditions = []
            if action == 'resolve':
                if self.actor['kind'] != 'owner':
                    raise AuthorizationError('Owner resolution required')
                state = dict(rows[0]['value'], status='open', assignee=None, checkpoint={}, output_ids=[])
            else:
                state = dict(rows[0]['value'])
                if action == 'claim':
                    if state['status'] not in ('open', 'failed'):
                        raise ConflictError('Task is already assigned or completed')
                    state.update(status='running', assignee=self.actor['id'])
                    _, _, input_conditions = self.inputs(state['inputs'])
                else:
                    if state['status'] != 'running' or (state['assignee'] != self.actor['id'] and self.actor['kind'] != 'owner'):
                        raise AuthorizationError('Task is not assigned to this connection')
                    if action in ('complete', 'checkpoint'):
                        _, _, input_conditions = self.inputs(state['inputs'])
                    if action == 'checkpoint':
                        state['checkpoint'] = checkpoint or {}
                    elif action == 'complete':
                        if not output_ids:
                            raise ValidationError('Completed work requires at least one attributed output record')
                        for output_id in output_ids or []:
                            _, output = self.locate(output_id)
                            if (not output or output['actor']['id'] != self.actor['id'] or
                                    output.get('provenance', {}).get('contribution', {}).get('reported', {}).get('task_id') != job_id):
                                raise ValidationError('Output must be this connection\'s attributed contribution to this task')
                        state.update(status='completed', output_ids=output_ids or [])
                    elif action == 'fail':
                        state.update(status='failed', checkpoint=checkpoint or state['checkpoint'])
                    elif action == 'release':
                        state.update(status='open', assignee=None)
                    else:
                        raise ValidationError('Unknown task action')
            # Previous state revisions retain their own interaction evidence.
            # Do not grow each checkpoint's source list without bound.
            sources = [sid for sid in rows[0]['source_ids'] if not
                (self.store.get_source(sid) or {}).get('uri', '').startswith('urn:refactoredmemory:interaction:')]
            conditions = [self.guard(job_id, 'rm:task-state', rows)] + input_conditions
        source = self.interaction(rid, title or 'Client-led task ' + action)
        actions = [source]
        if action == 'create':
            actions += [{'type': 'entity', 'id': job_id, 'entity_type': 'occurrence', 'label': title},
                fact(rid + '-type', job_id, knowledge.TYPE_PREDICATE, 'occurrence', [source['id']])]
        fields = dict(kind='correct', predecessors=[r['id'] for r in rows], reason='Client-led task ' + action) if rows else {}
        actions.append(fact(rid, job_id, 'rm:task-state', state, sources + [source['id']], **fields))
        receipt = self.submit('task:' + action, request_id, actions, conditions, reported)
        return {**receipt, 'job_id': job_id}

    def tasks(self, status=None, limit=30, offset=0):
        result = self.store.query(predicate='rm:task-state', limit=limit, offset=offset)
        rows = result['assertions']
        if status:
            # Filtering after a bounded read is explicit, never advertised complete.
            rows = [r for r in rows if r['value']['status'] == status]
        return {**result, 'assertions': rows, 'status_filter_after_page': bool(status),
                'execution': 'External connected clients only; RM does not run a model.'}

    def reviews(self, offset=0, limit=30):
        items, more = [], False
        for predicate in ('rm:enrichment-review', 'rm:review-flag', 'rm:review'):
            page = self.store.query(predicate=predicate, offset=offset, limit=limit)
            more |= page['coverage']['has_more']
            for row in page['assertions']:
                value = row.get('value', {})
                if isinstance(value, dict) and (str(value.get('status', '')).startswith('resolved') or
                    predicate == 'rm:review' and value.get('disposition') == 'confirmed'):
                    continue
                entity = self.store.get_entity(row['subject'])
                items.append({**row, 'label': entity['label'] if entity else 'Unresolved identity'})
        return {'items': items, 'has_more': more, 'next_offset': offset + limit,
                'coverage': 'Bounded pages of current review records; not a count of distinct people or the historical audit queue.'}

    def inspect(self, target_id):
        subject, claim = self.locate(target_id)
        claims = self.store.query(subject=subject, limit=100, excerpt_chars=1200)
        selected = [claim] if claim else claims['assertions']
        claims['assertions'] = [{**r, 'review': self.review_state(r)} for r in selected]
        notes = self.heads(subject, 'rm:comment')
        return {'entity': self.store.get_entity(subject), 'claims': claims,
                'comments': [r for r in notes if r['value']['target_id'] == target_id],
                'artifacts': self.artifacts(subject), 'permissions': {'owner_review': self.actor['kind'] == 'owner',
                'write': 'write' in self.actor.get('scopes', []), 'correct': 'correct' in self.actor.get('scopes', [])}}

    def context(self, subject, budget_chars=12000, limit=40):
        page = self.store.query(subject=subject, limit=limit, excerpt_chars=600)
        result, used = [], 0
        for row in page['assertions']:
            if row['predicate'] in MANAGED or row['predicate'] == knowledge.TYPE_PREDICATE:
                continue
            value = row.get('excerpt', row.get('value'))
            preview = canonical(value) if value is not None else None
            item = {k: row[k] for k in ('id', 'subject', 'predicate', 'object', 'source_ids', 'valid_from', 'valid_to', 'time_precision', 'actor', 'human_verified') if k in row}
            if preview is not None:
                item['preview'] = preview[:600]
                item['preview_truncated'] = len(preview) > 600
            amount = len(canonical(item))
            if used + amount > budget_chars:
                break
            result.append(item)
            used += amount
        return {'context': result, 'used_characters': used, 'budget_characters': budget_chars,
                'frontier': page['frontier'], 'known_position': page['known_position'],
                'coverage': {'complete': page['coverage']['complete'] and len(result) == len(page['assertions']),
                             'meaning': 'Bounded deterministic selection, not exhaustive relevance or independent verification.'}}

    def evidence(self, target_id, source_id, offset=0, chars=1200):
        _, claim = self.locate(target_id)
        if claim is None or source_id not in claim['source_ids']:
            raise ValidationError('Select a source attached to this claim revision')
        classes = self.store.query(predicate='rm:source-classification', limit=1000)
        if not classes['coverage']['complete']:
            return {'source_id': source_id, 'withheld': True,
                    'reason': 'Source classification coverage is incomplete; evidence display is withheld.'}
        for classification in classes['assertions']:
            value = classification.get('value', {})
            if source_id in classification['source_ids'] and isinstance(value, dict):
                if value.get('restricted') or value.get('classification') in ('software-or-test-fixture', 'execution-or-analysis-artifact', 'synthetic-or-code-artifact', 'structured-execution-artifact'):
                    return {'source_id': source_id, 'withheld': True, 'reason': 'Historical control/test content is withheld from this evidence view.'}
        source = self.store.get_source(source_id)
        if source is None:
            raise ValidationError('Source is unavailable')
        captured, details = captured_text(source['content'])
        text = readable(captured)
        title = next((v[:256] for v in (details.get('title'), source.get('metadata', {}).get('title')) if isinstance(v, str)), None)
        date = next((v[:128] for v in (details.get('receivedDateTime'), details.get('date'), source.get('metadata', {}).get('date')) if isinstance(v, str)), None)
        return {'source_id': source_id, 'uri': source['uri'], 'excerpt': text[offset:offset + chars],
                'title': title, 'date': date, 'offset': offset,
                'total_characters': len(text), 'has_more': len(text) > offset + chars,
                'next_offset': offset + chars, 'withheld': False,
                'meaning': 'Captured source record text; unresolved original evidence remains unresolved.'}

    def graph(self, start, depth=1, limit=60, include_mentions=False):
        self.locate(start)
        frontier = self.store.status()['frontier']
        entities, edges, queue, visited = {}, {}, [start], set()
        complete = True
        for _ in range(depth):
            following = []
            for node in queue:
                if node in visited:
                    continue
                visited.add(node)
                entity = self.store.get_entity(node)
                if entity:
                    entities[node] = entity
                candidates = self.store.query(subject=node, frontier=frontier, limit=200)
                complete &= candidates['coverage']['complete']
                selected = list(candidates['assertions'])
                incoming = list(self.store.db.execute("SELECT subject,predicate FROM records WHERE kind='assertion' AND object=? AND (? OR predicate!='mentions') LIMIT 201", (node, int(include_mentions))))
                complete &= len(incoming) <= 200
                for key in sorted({(r['subject'], r['predicate']) for r in incoming[:200]}):
                    page = self.store.query(subject=key[0], predicate=key[1], frontier=frontier, limit=200)
                    complete &= page['coverage']['complete']
                    selected += [r for r in page['assertions'] if r.get('object') == node]
                for row in selected:
                    if not row.get('object') or row['predicate'] in ('has-type', 'about'):
                        continue
                    if row['predicate'] == 'mentions' and not include_mentions:
                        continue
                    if len(edges) >= limit or len(entities) >= limit:
                        complete = False
                        continue
                    for eid in (row['subject'], row['object']):
                        entity = self.store.get_entity(eid)
                        if entity:
                            entities[eid] = entity
                            if eid not in visited:
                                following.append(eid)
                    if row['subject'] not in entities or row['object'] not in entities:
                        continue
                    keys = ('id', 'subject', 'predicate', 'object', 'source_ids', 'actor', 'status', 'preferred', 'conflicts', 'known_position')
                    edges[row['id']] = {k: row[k] for k in keys if k in row}
                    edges[row['id']]['review'] = self.review_state(row)
            queue = list(dict.fromkeys(following))
        return {'entities': list(entities.values()), 'edges': list(edges.values()), 'start': start,
                'coverage': {'complete': bool(complete), 'depth': depth, 'limit': limit},
                'frontier': frontier, 'known_position': self.store.status()['known_position'],
                'meaning': 'Connections are sourced claims, not automatic confirmation.'}

    def activity(self, connection_id=None, subject=None, since=0, limit=50):
        deleted = self.store._deleted()
        sql = "SELECT id,body,position,applied_at FROM operations WHERE position>? AND position IS NOT NULL"
        args = [since]
        sql += ' ORDER BY position LIMIT ?'
        args.append(limit + 1)
        rows = list(self.store.db.execute(sql, args))
        items, cursor, processed = [], since, 0
        for row in rows[:limit]:
            body = json.loads(row['body'])
            if items and len(items) + len(body['actions']) > 500:
                break
            cursor, processed = row['position'], processed + 1
            if connection_id and body['actor']['id'] != connection_id:
                continue
            for a in body['actions']:
                if a['type'] != 'assertion' or a['subject'] in deleted or a.get('object') in deleted:
                    continue
                if subject and subject not in (a['subject'], a.get('object')):
                    continue
                items.append({'id': a['id'], 'subject': a['subject'], 'predicate': a['predicate'],
                    'action': a.get('kind', 'assert'), 'connection': body['actor'],
                    'reported_processor': a.get('provenance', {}).get('contribution', {}).get('reported', {}),
                    'operation_id': body['id'], 'origin': body['origin'], 'known_position': row['position'],
                    'applied_at': row['applied_at'], 'source_ids': a['source_ids'],
                    'outcome': 'admitted on this peer', 'replication': 'Inspect peer frontiers; local admission is not remote receipt.'})
        return {'items': items, 'next_since': cursor, 'has_more': len(rows) > processed,
                'filter': 'Bounded operation page; connection and subject filters are applied within the page.'}
