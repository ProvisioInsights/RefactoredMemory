import { human, compact, displayName } from './format.js';

export const BRIEF_SCHEMA = 'refactoredmemory.relationship-brief:v1';
const groupNames = { capital: 'Capital relationships', employment: 'Work and organizations', network: 'People and introductions', structural: 'Related projects and records', occurrence: 'Participation and events' };
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const optionalText = value => value === undefined || value === null || typeof value === 'string';
const claimSnapshot = value => record(value) && ['id', 'subject', 'predicate'].every(key => typeof value[key] === 'string')
  && optionalText(value.object) && optionalText(value.valid_from)
  && Array.isArray(value.source_ids) && value.source_ids.every(id => typeof id === 'string');
export function validGraphSnapshot(graph) {
  const contribution = graph?.brief?.contribution;
  return record(graph) && typeof graph.start === 'string' && record(graph.coverage)
    && Array.isArray(graph.entities) && graph.entities.every(e => record(e) && typeof e.id === 'string' && typeof e.label === 'string'
      && optionalText(e.entity_type) && optionalText(e.display_label)
      && (!e.classification?.canonical_types || Array.isArray(e.classification.canonical_types) && e.classification.canonical_types.every(t => typeof t === 'string')))
    && Array.isArray(graph.edges) && graph.edges.every(e => claimSnapshot(e) && typeof e.object === 'string')
    && (graph.claims === undefined || Array.isArray(graph.claims) && graph.claims.every(claimSnapshot))
    && (!graph.brief || record(graph.brief) && ['id', 'title', 'text'].every(key => optionalText(graph.brief[key])))
    && (!contribution || record(contribution)
      && (!contribution.connection || record(contribution.connection) && optionalText(contribution.connection.id))
      && (!contribution.reported || record(contribution.reported) && ['application', 'model'].every(key => optionalText(contribution.reported[key]))));
}
export function relationshipLabel(claim) {
  if (claim?.predicate === 'invests-in') {
    const status = claim.knowledge?.qualifiers?.investment_status;
    const labels = { discussed: 'Funding discussed', proposed: 'Investment proposed', committed: 'Commitment reported', completed: 'Investment reported as completed', declined: 'Investment declined', withdrawn: 'Investment withdrawn', unknown: 'Investment status unknown' };
    if (labels[status]) return labels[status];
  }
  return human(claim?.predicate);
}
export function briefRows(graph) {
  if (!graph || !Array.isArray(graph.entities) || !Array.isArray(graph.edges) || graph.brief?.freshness?.state === 'stale') return [];
  const entities = new Map(graph.entities.filter(record).map(e => [e.id, e]));
  const claims = new Map((Array.isArray(graph.claims) ? graph.claims : graph.edges).filter(record).map(c => [c.id, c]));
  const row = item => {
    const supporting = item.claim_ids.map(id => claims.get(id)).filter(Boolean);
    const connection = supporting.find(c => c.object && (c.subject === item.entity_id || c.object === item.entity_id));
    const qualifiers = connection?.knowledge?.qualifiers || {};
    const context = Object.entries(qualifiers).filter(([key]) => key !== 'field_contract').map(([key, value]) => `${human(key.replaceAll('_', ' '))}: ${key === 'amount' && value === null ? 'Unknown' : compact(value)}`).join(' · ');
    return { ...item, entity: entities.get(item.entity_id), supporting, connection,
      sourceCount: new Set(supporting.flatMap(c => c.source_ids || [])).size,
      relationship: connection ? relationshipLabel(connection) : 'Supporting claim',
      date: connection?.valid_from || null, context };
  };
  if (graph.brief) return (Array.isArray(graph.brief.groups) ? graph.brief.groups : []).filter(g => record(g) && typeof g.title === 'string' && Array.isArray(g.items)).map(group => ({ title: group.title, items: group.items.filter(item => record(item) && typeof item.entity_id === 'string' && typeof item.why === 'string' && Array.isArray(item.claim_ids)).map(row).filter(r => r.entity) }));
  const grouped = new Map();
  for (const edge of graph.edges) {
    if (!record(edge)) continue;
    const id = edge.subject === graph.start ? edge.object : edge.object === graph.start ? edge.subject : null;
    if (!id || !entities.has(id)) continue;
    const title = groupNames[edge.knowledge?.category] || 'Recorded connections';
    if (!grouped.has(title)) grouped.set(title, new Map());
    const records = grouped.get(title), existing = records.get(id);
    if (existing) existing.claim_ids.push(edge.id);
    else records.set(id, { entity_id: id, claim_ids: [edge.id], why: `${displayName(entities.get(edge.subject))} → ${human(edge.predicate)} → ${displayName(entities.get(edge.object))}` });
  }
  return [...grouped].map(([title, items]) => ({ title, items: [...items.values()].map(row) }));
}

export function selectedPath(graph, row) {
  if (!graph || !row || graph.brief?.freshness?.state === 'stale') return null;
  const route = graph.paths?.[row.entity_id];
  const routes = Array.isArray(route?.routes) ? route.routes.filter(r => record(r) && Array.isArray(r.claim_ids)).slice(0, 2) : null;
  const ids = new Set(routes ? routes.flatMap(r => r.claim_ids) : row.claim_ids.filter(id => graph.edges.some(e => e?.id === id)));
  const edges = graph.edges.filter(e => e && ids.has(e.id));
  const nodes = new Set([graph.start, row.entity_id, ...edges.flatMap(e => [e.subject, e.object])]);
  return { ...graph, entities: graph.entities.filter(e => e && nodes.has(e.id)), edges };
}
