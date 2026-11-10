import { validGraphSnapshot } from './briefModel.js';

// Graph distance is undirected; retained edges keep their actual direction.
export function topology(graph, depth = 2) {
  const entities = new Map((graph?.entities || []).map(n => [n.id, n]));
  const neighbors = new Map([...entities.keys()].map(id => [id, []]));
  for (const edge of graph?.edges || []) {
    if (!entities.has(edge.subject) || !entities.has(edge.object)) continue;
    neighbors.get(edge.subject).push({ id: edge.object, edge: edge.id });
    neighbors.get(edge.object).push({ id: edge.subject, edge: edge.id });
  }
  const hops = new Map(), parents = new Map(), queue = [];
  if (entities.has(graph?.start)) { hops.set(graph.start, 0); queue.push(graph.start); }
  for (let i = 0; i < queue.length; i++) {
    const id = queue[i];
    if (hops.get(id) >= depth) continue;
    for (const next of neighbors.get(id).sort((a, b) => a.id.localeCompare(b.id) || a.edge.localeCompare(b.edge))) {
      if (hops.has(next.id)) continue;
      hops.set(next.id, hops.get(id) + 1); parents.set(next.id, { id, edge: next.edge }); queue.push(next.id);
    }
  }
  const direct = queue.filter(id => hops.get(id) === 1);
  const branch = id => { while (parents.get(id)?.id !== graph.start && parents.has(id)) id = parents.get(id).id; return id; };
  const nodes = queue.map(id => {
    const hop = hops.get(id), rootBranch = branch(id), index = direct.indexOf(rootBranch);
    let angle = -Math.PI / 2 + index * Math.PI * 2 / Math.max(1, direct.length);
    if (hop > 1) {
      const siblings = queue.filter(other => hops.get(other) === hop && branch(other) === rootBranch);
      angle += ((siblings.indexOf(id) + .5) / siblings.length - .5) * Math.PI * 2 / Math.max(1, direct.length) * .72;
    }
    const radius = hop === 0 ? 0 : hop === 1 ? 145 : 285;
    return { ...entities.get(id), hop, x: 450 + Math.cos(angle) * radius, y: 345 + Math.sin(angle) * radius };
  });
  return { nodes, edges: (graph?.edges || []).filter(e => hops.has(e.subject) && hops.has(e.object)), parents };
}

export function pathTo(model, id) {
  const nodes = [id], edges = [];
  while (model.parents.has(id)) {
    const parent = model.parents.get(id); edges.push(parent.edge); nodes.push(parent.id); id = parent.id;
  }
  return { nodes: nodes.reverse(), edges: edges.reverse() };
}

export const sameFrontier = (a, b) => JSON.stringify(Object.entries(a || {}).sort()) === JSON.stringify(Object.entries(b || {}).sort());

export function checkedContext(brief, context, start, briefId) {
  const fail = () => { throw new Error('Memory changed while loading. Try again.'); };
  const frontier = value => value && typeof value === 'object' && !Array.isArray(value) && Object.values(value).every(n => Number.isSafeInteger(n) && n >= 0);
  if (briefId && (!validGraphSnapshot(brief) || !frontier(brief.frontier) || brief.start !== start || brief.brief?.id !== briefId)) fail();
  if (briefId && brief.brief?.freshness?.state === 'stale') return { stale: brief };
  if (briefId && brief.brief?.freshness?.state !== 'current') fail();
  if (!validGraphSnapshot(context) || context.entities.length > 16 || context.edges.length > 16 || context.start !== start || !frontier(context.frontier) || briefId && !sameFrontier(brief.frontier, context.frontier)) fail();
  return { data: context };
}
