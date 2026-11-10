// Shared client/core fixture: execute the actual frontend wire builder in Node.
import { readFileSync } from 'node:fs';
import { createArguments, fieldValue, mappedValue, fieldUpdate, fieldAction, manualSource } from '../../apps/memory_graph/src/fieldModel.js';

const catalog = JSON.parse(readFileSync(0, 'utf8'));
const create = createArguments(catalog, { id: 'client-person', type: 'person', name: 'Synthetic Client Person', note: 'Synthetic client fixture only.' });
const legacy = { value: { property: 'last-contacted', calendar_period: '2026-05', precision: 'month', source_annotation: 'Month only.' } };
const date = catalog.fields['date.last_contacted'];
const value = fieldValue(date, legacy);
const update = fieldUpdate(catalog, 'date.last_contacted', { state: 'known', end: 'unknown', start: '', context: {} });
const payload = mappedValue(date, value, legacy, 'month');
const source = 'client-extra-source';
const unknown = fieldUpdate(catalog, 'contact.email', { state: 'unknown', end: 'unknown', start: '', context: {} });
const additional = { catalog_digest: catalog.digest_sha256, request_id: 'client-additional', actions: [
  manualSource(source, 'Synthetic source establishes an unknown email and reported month.'),
  fieldAction(catalog, 'date.last_contacted', payload, update, { id: 'client-date', subject: 'client-person', source }),
  fieldAction(catalog, 'contact.email', mappedValue(catalog.fields['contact.email'], null), unknown,
    { id: 'client-unknown', subject: 'client-person', source }),
] };
console.log(JSON.stringify({ create, additional, legacyValue: value, payload, update }));
