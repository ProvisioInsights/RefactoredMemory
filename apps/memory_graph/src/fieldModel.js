// Wire construction follows the discovered core mappings; admission stays in RM.
export const EDITOR_SCHEMA = 'refactoredmemory.field-editor:v1';
export const clone = value => structuredClone(value);
export const tagOf = claim => claim?.provenance?.knowledge?.qualifiers?.field_contract;
export const qualifiersOf = claim => claim?.provenance?.knowledge?.qualifiers || {};
export function fieldValue(definition, claim) {
  if (!claim) return '';
  if (definition.value_type === 'entity_reference') return claim.object;
  const paths = definition.storage.read_paths || [definition.storage.value_path];
  for (const path of paths) {
    const value = path.reduce((v, key) => v?.[key], claim.value);
    if (value !== undefined) return value;
  }
  return undefined;
}
export function mappedValue(definition, value, claim, precision) {
  if (definition.value_type === 'entity_reference') return { object: value };
  const path = definition.storage.value_path;
  if (!path.length) return { value };
  const previous = claim?.value && typeof claim.value === 'object' && !Array.isArray(claim.value) ? claim.value : {};
  const raw = clone(definition.storage.match);
  for (const key of Object.keys(raw)) {
    if (previous[key] === raw[key] || key === 'property' && definition.legacy_properties.includes(previous[key])) raw[key] = previous[key];
  }
  const metadata = definition.value_type === 'calendar_date' ? ['reported_value', 'source_annotation']
    : definition.storage.predicate === 'rm:contact-point' ? ['label', 'country_code'] : [];
  for (const key of metadata) if (key in previous) raw[key] = clone(previous[key]);
  let target = raw;
  path.forEach((key, i) => { if (i === path.length - 1) target[key] = value; else target = target[key] ||= {}; });
  if (definition.value_type === 'calendar_date') raw.precision = value === null ? 'unknown' : precision;
  return { value: raw };
}
export function fieldUpdate(catalog, field, draft) {
  const update = { catalog_digest: catalog.digest_sha256, field, state: draft.state,
    validity_end: draft.end, valid_from: draft.start || null,
    time_precision: draft.start ? draft.timePrecision : 'unknown', context: draft.context || {} };
  if (draft.end !== 'ongoing') update.valid_to = draft.end === 'known' ? draft.until : null;
  return update;
}
export function fieldAction(catalog, field, payload, update, { id, subject, source }) {
  const definition = catalog.fields[field];
  const profile = { schema: 'refactoredmemory.knowledge:v1',
    kind: definition.value_type === 'entity_reference' ? 'relationship' : 'fact',
    qualifiers: { ...update.context, field_contract: { schema: catalog.schema, revision: catalog.revision,
      field, state: update.state, validity_end: update.validity_end } } };
  if (definition.category) profile.category = definition.category;
  return { type: 'assertion', id, subject, predicate: definition.storage.predicate, ...payload,
    source_ids: [source], valid_from: update.valid_from, time_precision: update.time_precision,
    ...('valid_to' in update ? { valid_to: update.valid_to } : {}), provenance: { knowledge: profile } };
}
export function manualSource(id, note) {
  return { type: 'source', id, uri: 'urn:refactoredmemory:manual-field:' + id, content: note,
    metadata: { source_kind: 'manual field statement', meaning: 'Attributed statement, not independent verification.' } };
}
export function createArguments(catalog, { id, type, name, note }) {
  const source = id + '-source';
  const draft = { state: 'known', end: 'unknown', start: '', context: {} };
  return { catalog_digest: catalog.digest_sha256, request_id: id,
    reported: { application: 'RM field editor' }, actions: [manualSource(source, note),
      { type: 'entity', id, entity_type: type, label: name },
      ...[['identity.type', type], ['identity.name', name]].map(([field, value], i) =>
        fieldAction(catalog, field, { value }, fieldUpdate(catalog, field, draft),
          { id: id + '-identity-' + i, subject: id, source }))] };
}
