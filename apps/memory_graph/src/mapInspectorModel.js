import { fieldValue, tagOf } from './fieldModel.js';
import { compact } from './format.js';

export function checkedInspection(data, selection) {
  const claims = data?.claims?.assertions;
  if (!data?.entity?.id || !Array.isArray(claims)) throw new Error('This record could not be verified. Select it again to retry.');
  if (selection.kind === 'node') {
    if (data.entity.id !== selection.id || data.field_view?.coverage?.selection_only) throw new Error('The returned record does not match this node.');
  } else if (claims.length !== 1 || claims[0].id !== selection.id || claims[0].subject !== data.entity.id || !claims[0].object || !data.field_view?.coverage?.selection_only) {
    throw new Error('The returned assertion does not match this relationship.');
  }
  return data;
}

export function contractRows(data, catalog, showEmpty = false) {
  const view = data?.field_view;
  if (catalog?.schema !== 'refactoredmemory.fields:v1' || catalog.revision !== 1 || view?.schema !== catalog.schema || view.revision !== catalog.revision || view.digest_sha256 !== catalog.digest_sha256) return null;
  const claims = new Map(data.claims.assertions.map(c => [c.id, c]));
  return Object.entries(view.fields).filter(([id, info]) => catalog.fields[id] && (info.claim_ids.length || !view.coverage.selection_only && (showEmpty || catalog.fields[id].required_for_create))).map(([id, info]) => ({
    id, definition: catalog.fields[id], empty: info.empty_state,
    values: info.claim_ids.map(cid => {
      const claim = claims.get(cid), mapping = view.claims[cid], tag = tagOf(claim);
      return { claim, mapping, text: !claim ? 'Value not loaded' : tag?.state === 'unknown' ? 'Explicitly unknown' : tag?.state === 'not_applicable' ? 'Not applicable' : mapping?.editable_value_loaded ? compact(fieldValue(catalog.fields[id], claim)) : claim.excerpt || 'Value not loaded' };
    })
  }));
}

export function validity(claim) {
  const tag = tagOf(claim);
  return {
    from: claim.valid_from ?? 'Not recorded',
    precision: claim.time_precision || 'Not recorded',
    until: tag?.validity_end === 'ongoing' ? 'Explicitly ongoing' : claim.valid_to === null || tag?.validity_end === 'unknown' ? 'Explicitly unknown' : claim.valid_to || 'Not recorded'
  };
}

// Presentation groups only; labels, applicability and value semantics stay in the catalog.
export function profileSections(rows, entity, { hidden = [], showIdentity = false } = {}) {
  const sections = new Map();
  for (const row of rows || []) {
    const important = !row.values.length && row.definition.required_for_create || row.values.some(v => ['unknown', 'not_applicable'].includes(tagOf(v.claim)?.state) || v.claim?.conflicts?.length || v.claim?.alternatives?.length) || row.id === 'identity.type' && entity?.classification?.ambiguous;
    if (!important && hidden.includes(row.id)) continue;
    const headerValue = row.id === 'identity.name' ? entity?.display_label || entity?.label : row.id === 'identity.type' ? entity?.classification?.canonical_types?.length === 1 ? entity.classification.canonical_types[0] : entity?.entity_type : null;
    if (!showIdentity && !important && headerValue && row.values.length === 1 && row.values[0].text === headerValue) continue;
    const section = row.id.startsWith('relationship.') ? 'Connections' : row.id.startsWith('date.') ? 'Dates' : row.id.startsWith('contact.') || row.id === 'profile.preferred_channel' ? 'Contact' : 'About';
    if (!sections.has(section)) sections.set(section, []);
    sections.get(section).push({ ...row, important });
  }
  return [...sections].sort((a, b) => ['About', 'Contact', 'Connections', 'Dates'].indexOf(a[0]) - ['About', 'Contact', 'Connections', 'Dates'].indexOf(b[0]));
}

export function selectedHistory(history, selection) {
  const operations = history?.operations || [];
  if (selection.kind === 'node') return operations.map(op => ({ ...op, actions: op.actions.filter(a => a.type === 'assertion' && a.subject === selection.id) })).filter(op => op.actions.length);
  const ancestors = new Set([selection.id]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const op of operations) for (const action of op.actions) {
      if (action.type === 'assertion' && ancestors.has(action.id)) for (const id of action.predecessors || []) if (!ancestors.has(id)) { ancestors.add(id); changed = true; }
    }
  }
  return operations.map(op => ({ ...op, actions: op.actions.filter(a => a.type === 'assertion' && ancestors.has(a.id)) })).filter(op => op.actions.length);
}
