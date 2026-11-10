"""Disposable, explicitly synthetic records for the selected brief interface."""
from refactoredmemory import knowledge
from refactoredmemory.service import Service


def seed(store):
    people = [('avery', 'Avery Rivera'), ('jordan', 'Jordan Lee'), ('morgan', 'Morgan Ellis')]
    sources = [
        ('meeting', 'Meeting note', '2026-10-28', 'Synthetic example: Avery reviewed the fundraising round. No commitment or completed investment was established.'),
        ('reply', 'Email reply', '2026-11-04', 'Synthetic example: Avery wrote, "Happy to discuss the round next week." This is not a commitment.'),
        ('deck', 'Materials request', '2026-10-30', 'Synthetic example: Jordan requested the deck before a follow-up.'),
        ('intro', 'Introduction note', '2026-10-26', 'Synthetic example: Morgan introduced Avery to the Forgence fundraising discussion. Avery is an investor contact at Riverbend Ventures in Example City; no investment commitment is recorded. Example contact card: +1 202-555-0104, https://example.org/avery; preferred channel is email.')]
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
    for rid, value in [('avery', 'Investor contact at Riverbend Ventures. Introduced by Morgan; fundraising discussion recorded, with no commitment established.'),
                       ('project', 'Synthetic organization record used to review fundraising connections.')]:
        actions.append({'type': 'assertion', 'id': rid + '-description', 'subject': rid,
                        'predicate': 'description', 'value': value, 'source_ids': ['meeting', 'intro']})
    for key, value in [('role', 'Investor contact'), ('location', 'Example City'), ('relationship-origin', 'Introduced by Morgan during the fundraising discussion'), ('preferred-channel', 'Email')]:
        actions.append({'type': 'assertion', 'id': 'avery-profile-' + key, 'subject': 'avery',
                        'predicate': 'rm:profile-property', 'value': {'property': key, 'reported_value': value}, 'source_ids': ['intro']})
    actions += [
        {'type': 'assertion', 'id': 'avery-phone', 'subject': 'avery', 'predicate': 'rm:contact-point',
         'value': {'kind': 'phone', 'address': '+1 202-555-0104'}, 'source_ids': ['intro']},
        {'type': 'assertion', 'id': 'avery-url', 'subject': 'avery', 'predicate': 'rm:contact-point',
         'value': {'kind': 'url', 'address': 'https://example.org/avery'}, 'source_ids': ['intro']},
        {'type': 'assertion', 'id': 'avery-last-contact', 'subject': 'avery', 'predicate': 'rm:reported-date',
         'value': {'property': 'last-contacted', 'date': '2026-11-04', 'precision': 'day'}, 'source_ids': ['reply']}]
    store.submit(actions, request_id='synthetic-brief-seed')
    # Context is real synthetic graph data, separate from the prepared answer.
    context = [('riverbend', 'Riverbend Ventures', 'organization'), ('robin', 'Robin Chen', 'person'),
               ('forum', 'Founders Forum', 'project'), ('taylor', 'Taylor Brooks', 'person'),
               ('studio', 'Northline Studio', 'organization'), ('sam', 'Sam Patel', 'person'),
               ('place', 'Harbor House', 'location')]
    context_actions = [{'type': 'source', 'id': 'network-context', 'uri': 'synthetic://brief/network',
                        'content': 'Synthetic context: Avery works at Riverbend and knows Robin; Jordan participates in Founders Forum and knows Taylor; Morgan works at Northline and knows Sam. Riverbend is based at Harbor House, a meeting venue in the Harbor district of Example City; street address and access instructions are not recorded.',
                        'metadata': {'synthetic': True, 'title': 'Example network context'}}]
    for rid, label, kind in context:
        context_actions += [{'type': 'entity', 'id': rid, 'label': label, 'entity_type': kind},
                            {'type': 'assertion', 'id': rid + '-name', 'subject': rid, 'predicate': 'name',
                             'value': label, 'source_ids': ['network-context']},
                            {'type': 'assertion', 'id': rid + '-type', 'subject': rid, 'predicate': knowledge.TYPE_PREDICATE,
                             'value': kind, 'source_ids': ['network-context']}]
    for rid, subject, predicate, target in [('avery-employer', 'avery', 'employed-by', 'riverbend'),
            ('avery-robin', 'avery', 'knows', 'robin'), ('jordan-forum', 'jordan', 'participant-in', 'forum'),
            ('jordan-taylor', 'jordan', 'knows', 'taylor'), ('morgan-employer', 'morgan', 'employed-by', 'studio'),
            ('morgan-sam', 'morgan', 'knows', 'sam')]:
        context_actions.append({'type': 'assertion', 'id': rid, 'subject': subject, 'predicate': predicate,
                                'object': target, 'source_ids': ['network-context']})
    context_actions += [
        {'type': 'assertion', 'id': 'riverbend-place', 'subject': 'riverbend', 'predicate': 'based-in', 'object': 'place', 'source_ids': ['network-context']},
        {'type': 'assertion', 'id': 'place-description', 'subject': 'place', 'predicate': 'description',
         'value': 'Synthetic meeting venue connected to Riverbend Ventures. Access instructions and street address are not recorded.', 'source_ids': ['network-context']},
        {'type': 'assertion', 'id': 'place-location', 'subject': 'place', 'predicate': 'rm:profile-property',
         'value': {'property': 'location', 'reported_value': 'Harbor district, Example City'}, 'source_ids': ['network-context']}]
    store.submit(context_actions, request_id='synthetic-map-context')
    service = Service(store)
    token = store.create_grant('synthetic external brief processor', ['read', 'write'])
    ids = ['avery-round', 'jordan-round', 'morgan-round', 'avery-intro']
    result = service.call('memory_derive', {
        'subject': 'project', 'title': 'Fundraising connections',
        'text': 'Two discussions and an introduction.',
        'inputs': [{'kind': 'assertion', 'id': rid} for rid in ids],
        'input_frontier': store.status()['frontier'], 'request_id': 'synthetic-brief',
        'reported': {'application': 'Synthetic external client', 'method': 'source-grounded example selection'},
        'view': {'schema': 'refactoredmemory.relationship-brief:v1', 'groups': [
            {'title': 'Direct discussions', 'items': [
                {'entity_id': 'avery', 'claim_ids': ['avery-round', 'morgan-round', 'avery-intro'],
                 'why': 'Reviewed the round and replied. No commitment recorded.'},
                {'entity_id': 'jordan', 'claim_ids': ['jordan-round'],
                 'why': 'Requested the deck before a follow-up.'}]},
            {'title': 'Introduction recorded', 'items': [{'entity_id': 'morgan', 'claim_ids': ['morgan-round'],
                 'why': 'Introduced Avery to the round.'}]}]}}, token)
    return next(rid for rid in result['action_ids'] if store.read('assertion', rid))
