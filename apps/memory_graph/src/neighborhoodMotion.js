import { displayName } from './format.js';

export function mapLabelLines(node) {
  const label = displayName(node), words = label.split(' ');
  return label.length > (node.hop === 0 ? 11 : 17) && words.length > 1
    ? [words.slice(0, Math.ceil(words.length / 2)).join(' '), words.slice(Math.ceil(words.length / 2)).join(' ')] : [label];
}

export function motionLayout(model) {
  return { ...model, nodes: model.nodes.map(node => ({ ...node,
    radius: node.hop === 0 ? 54 : node.hop === 1 ? 25 : 14,
    labelY: node.hop === 0 ? mapLabelLines(node).length > 1 ? -5 : 7 : node.hop === 1 ? 48 : 37,
    opacity: 1, exiting: false })), edges: model.edges.map(edge => ({ ...edge, opacity: 1, exiting: false })) };
}

// Interpolate geometry only. Membership and relationship direction come from accepted graphs.
export function motionPlan(from, to, allowExits = true) {
  const old = new Map(from.nodes.map(n => [n.id, n])), next = new Map(to.nodes.map(n => [n.id, n]));
  const center = to.nodes.find(n => n.hop === 0);
  const nodePlans = to.nodes.map(node => {
    const neighbor = to.edges.flatMap(e => e.subject === node.id ? [e.object] : e.object === node.id ? [e.subject] : []).find(id => old.has(id));
    const anchor = old.get(neighbor) || old.get(center?.id) || center || node;
    return { from: old.get(node.id) || { ...node, x: anchor.x, y: anchor.y, radius: 0, opacity: 0 }, to: node };
  });
  if (allowExits) for (const node of from.nodes) if (!next.has(node.id)) nodePlans.push({ from: node, to: { ...node, opacity: 0, exiting: true } });
  const oldEdges = new Map(from.edges.map(e => [e.id, e])), nextEdges = new Set(to.edges.map(e => e.id));
  const edgePlans = to.edges.map(edge => ({ from: oldEdges.get(edge.id) || { ...edge, opacity: 0 }, to: edge }));
  if (allowExits) for (const edge of from.edges) if (!nextEdges.has(edge.id)) edgePlans.push({ from: edge, to: { ...edge, opacity: 0, exiting: true } });
  return progress => {
    if (progress >= 1) return to;
    const t = Math.max(0, progress), eased = t * t * (3 - 2 * t), mix = (a, b) => a + (b - a) * eased;
    const nodes = nodePlans.map(({ from: a, to: b }) => ({ ...b,
      x: mix(a.x, b.x), y: mix(a.y, b.y), radius: mix(a.radius, b.radius),
      labelY: mix(a.labelY, b.labelY), opacity: mix(a.opacity, b.opacity) }));
    const ids = new Set(nodes.map(n => n.id));
    const edges = edgePlans.filter(({ to: e }) => ids.has(e.subject) && ids.has(e.object)).map(({ from: a, to: b }) => ({ ...b, opacity: mix(a.opacity, b.opacity) }));
    return { ...to, nodes, edges };
  };
}
