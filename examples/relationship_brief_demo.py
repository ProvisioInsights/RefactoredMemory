"""Disposable, explicitly synthetic records for the selected brief interface."""
from refactoredmemory import knowledge
from refactoredmemory.service import Service


def seed(store):
    people = [('avery', 'Avery Rivera'), ('jordan', 'Jordan Lee'), ('morgan', 'Morgan Ellis')]
    sources = [
        ('meeting', 'Meeting note', '2026-10-28', 'Synthetic example: Avery reviewed the fundraising round. No commitment or completed investment was established.'),
        ('reply', 'Email reply', '2026-11-04', 'Synthetic example: Avery wrote, "Happy to discuss the round next week." This is not a commitment.'),
        ('deck', 'Materials request', '2026-10-30', 'Synthetic example: Jordan requested the deck before a follow-up.'),
        ('intro', 'Introduction note', '2026-10-26', 'Synthetic example: Morgan introduced Avery to the Forgence fundraising discussion.')]
    actions = [{'type': 'source', 'id': rid, 'uri': 'synthetic://brief/' + rid, 'content': content,
                'metadata': {'synthetic': True, 'title': title, 'date': date}} for rid, title, date, content in sources]
    for rid, label, kind in [('project', 'Forgence', 'organization')] + [(rid, label, 'person') for rid, label in people]:
        actions += [{'type': 'entity', 'id': rid, 'entity_type': kind, 'label': label},
                    {'type': 'assertion', 'id': rid + '-type', 'subject': rid, 'predicate': knowledge.TYPE_PREDICATE,
                     'value': kind, 'source_ids': ['meeting']},
                    {'type': 'assertion', 'id': rid + '-name', 'subject': rid, 'predicate': 'name', 'value': label,
                     'source_ids': ['meeting']}]
    actions += [{'type': 'assertion', 'id': 'avery-round', 'subject': 'avery', 'predicate': 'invests-in', 'object': 'project',
                 'source_ids': ['meeting', 'reply'], 'valid_from': '2026-11-04', 'time_precision': 'day',
                 'provenance': {'knowledge': {'schema': knowledge.PROFILE, 'kind': 'relationship', 'category': 'capital',
                                            'qualifiers': {'investment_status': 'discussed', 'amount': None}}}},
                {'type': 'assertion', 'id': 'jordan-round', 'subject': 'jordan', 'predicate': 'participant-in', 'object': 'project',
                 'source_ids': ['deck'], 'valid_from': '2026-10-30', 'time_precision': 'day'},
                {'type': 'assertion', 'id': 'morgan-round', 'subject': 'morgan', 'predicate': 'participant-in', 'object': 'project',
                 'source_ids': ['intro'], 'valid_from': '2026-10-26', 'time_precision': 'day'},
                {'type': 'assertion', 'id': 'avery-intro', 'subject': 'avery', 'predicate': 'introduced-by', 'object': 'morgan',
                 'source_ids': ['intro'], 'valid_from': '2026-10-26', 'time_precision': 'day'},
                {'type': 'assertion', 'id': 'avery-email', 'subject': 'avery', 'predicate': 'rm:contact-point',
                 'value': {'kind': 'email', 'address': 'avery@example.org'}, 'source_ids': ['reply']}]
    store.submit(actions, request_id='synthetic-brief-seed')
    service = Service(store)
    token = store.create_grant('synthetic external brief processor', ['read', 'write'])
    ids = ['avery-round', 'jordan-round', 'morgan-round', 'avery-intro']
    result = service.call('memory_derive', {
        'subject': 'project', 'title': 'People connected to the raise',
        'text': 'Two conversations to review, plus one potential introduction.',
        'inputs': [{'kind': 'assertion', 'id': rid} for rid in ids],
        'input_frontier': store.status()['frontier'], 'request_id': 'synthetic-brief',
        'reported': {'application': 'Synthetic external client', 'method': 'source-grounded example selection'},
        'view': {'schema': 'refactoredmemory.relationship-brief:v1', 'groups': [
            {'title': 'Direct discussions', 'items': [
                {'entity_id': 'avery', 'claim_ids': ['avery-round', 'morgan-round', 'avery-intro'],
                 'why': 'Reviewed the round and replied to a follow-up. No commitment is established.'},
                {'entity_id': 'jordan', 'claim_ids': ['jordan-round'],
                 'why': 'Requested materials before a follow-up; funding is not established.'}]},
            {'title': 'Introduction recorded', 'items': [{'entity_id': 'morgan', 'claim_ids': ['morgan-round'],
                 'why': 'Connected Avery with the discussion. A connector is not automatically an investor.'}]}]}}, token)
    return next(rid for rid in result['action_ids'] if store.read('assertion', rid))
