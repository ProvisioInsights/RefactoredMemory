import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { displayName } from './format.js';
import { relationshipLabel } from './briefModel.js';
import { checkedContext, pathTo, topology } from './neighborhoodModel.js';
import MapInspector from './MapInspector.jsx';

export default function NeighborhoodMap({ graph, call, available, pending, canNavigate, onOpen, onFocus, onStale, schema }) {
  const [depth, setDepth] = useState(2), [data, setData] = useState(null);
  const [loading, setLoading] = useState(false), [error, setError] = useState(''), [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState(null), [hovered, setHovered] = useState(null);
  const triggerRef = useRef(null);
  const arrow = useId();
  useEffect(() => {
    let cancelled = false;
    setData(null); setSelected(null); setHovered(null); setError('');
    if (!graph || pending) { setLoading(false); return; }
    if (!available) { setData(graph); setLoading(false); return; }
    setLoading(true);
    Promise.all([
      graph.brief ? call('memory_graph', { start: graph.start, brief_id: graph.brief.id }) : Promise.resolve(null),
      call('memory_graph', { start: graph.start, depth, limit: 16 })
    ]).then(([brief, context]) => {
      if (cancelled) return;
      const checked = checkedContext(brief, context, graph.start, graph.brief?.id);
      if (checked.stale) { onStale(checked.stale); return; }
      setData(checked.data);
    }).catch(e => { if (!cancelled) setError(e.message); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [graph, depth, available, pending, call, retry, onStale]);
  const model = useMemo(() => topology(data, depth), [data, depth]);
  const byId = new Map(model.nodes.map(n => [n.id, n]));
  const activeSelection = hovered || selected;
  const activeEdge = activeSelection?.kind === 'edge' && model.edges.find(e => e.id === activeSelection.id);
  const active = byId.get(activeEdge ? (byId.get(activeEdge.subject).hop >= byId.get(activeEdge.object).hop ? activeEdge.subject : activeEdge.object) : activeSelection?.id);
  const path = active ? pathTo(model, active.id) : { nodes: [], edges: [] };
  if (activeEdge) {
    if (!path.edges.includes(activeEdge.id)) path.edges.push(activeEdge.id);
    for (const id of [activeEdge.subject, activeEdge.object]) if (!path.nodes.includes(id)) path.nodes.push(id);
  }
  const root = byId.get(data?.start);
  const linkLabel = edge => relationshipLabel(edge) === 'invests in' ? 'investment record · terms in details' : relationshipLabel(edge);
  const linkText = edge => `${displayName(byId.get(edge.subject))} → ${linkLabel(edge)} → ${displayName(byId.get(edge.object))}`;
  const choose = (id, kind = 'node', trigger) => { if (!pending && canNavigate()) { if (trigger) triggerRef.current = trigger; setSelected({ id, kind }); } };
  const clear = () => { if (canNavigate()) { setSelected(null); setHovered(null); triggerRef.current?.focus({ preventScroll: true }); } };
  return <section className={'neighborhood-map' + (selected ? ' has-inspector' : '')} aria-label="Tiered connection map"><div className="map-surface">
    <div className="map-controls"><label>Outward<select aria-label="Connection tiers" value={depth} disabled={pending || loading} onChange={e => { if (canNavigate()) setDepth(Number(e.target.value)); }}><option value={1}>1 tier</option><option value={2}>2 tiers</option></select></label><span>Faded = indirect</span>{!available ? <small>Supplied snapshot</small> : data?.coverage.complete === false && <small>Bounded view</small>}</div>
    {loading && <p role="status">Loading nearby connections…</p>}
    {error && <p role="alert">{error} <button disabled={pending} onClick={() => { if (canNavigate()) setRetry(n => n + 1); }}>Retry</button></p>}
    {!!model.nodes.length && <svg viewBox="0 0 900 720" role="group" aria-label="Recorded connections by distance">
      <defs><marker id={arrow} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10Z" fill="context-stroke"/></marker></defs>
      {[145, ...(depth > 1 ? [285] : [])].map(r => <circle key={r} className="distance-ring" cx="450" cy="345" r={r}/>)}
      {model.edges.map(edge => {
        const a = byId.get(edge.subject), b = byId.get(edge.object), dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy) || 1;
        const radius = n => n.hop === 0 ? 54 : n.hop === 1 ? 25 : 14;
        const points = { x1: a.x + dx * radius(a) / length, y1: a.y + dy * radius(a) / length, x2: b.x - dx * radius(b) / length, y2: b.y - dy * radius(b) / length };
        return <g key={edge.id} className="map-edge" role="button" tabIndex={pending ? -1 : 0} aria-disabled={pending} aria-label={linkText(edge)} onPointerEnter={() => setHovered({ kind: 'edge', id: edge.id })} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered({ kind: 'edge', id: edge.id })} onBlur={() => setHovered(null)} onClick={e => choose(edge.id, 'edge', e.currentTarget)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(edge.id, 'edge', e.currentTarget); } }}>
          <title>{linkText(edge)}</title><line className="map-edge-hit" {...points}/><line className={'map-link' + (Math.max(a.hop, b.hop) > 1 ? ' indirect' : '') + (path.edges.includes(edge.id) ? ' active' : '')} {...points} markerEnd={`url(#${arrow})`}/>
        </g>;
      })}
      {model.nodes.map(node => {
        const label = displayName(node), words = label.split(' '), labels = label.length > 17 ? [words.slice(0, Math.ceil(words.length / 2)).join(' '), words.slice(Math.ceil(words.length / 2)).join(' ')] : [label];
        const highlighted = path.nodes.includes(node.id), isActive = active?.id === node.id;
        return <g key={node.id} className={'map-node hop-' + node.hop + (highlighted ? ' path-active' : '') + (isActive ? ' active' : '')} transform={`translate(${node.x} ${node.y})`} role="button" tabIndex={pending ? -1 : 0} aria-disabled={pending} aria-label={`${label}, ${node.hop === 0 ? 'focus' : node.hop + (node.hop === 1 ? ' step' : ' steps') + ' from ' + displayName(root)}`} onPointerEnter={() => setHovered({ kind: 'node', id: node.id })} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered({ kind: 'node', id: node.id })} onBlur={() => setHovered(null)} onClick={e => choose(node.id, 'node', e.currentTarget)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(node.id, 'node', e.currentTarget); } }}>
          <title>{label}</title><circle className="map-hit" r="46"/><circle className="map-mark" r={node.hop === 0 ? 54 : node.hop === 1 ? 25 : 14}/>
          <text className="map-node-label" textAnchor="middle">{labels.map((line, i) => <tspan key={i} x="0" dy={i ? 23 : node.hop === 0 ? labels.length === 1 ? 7 : -5 : node.hop === 1 ? 48 : 37}>{line.length > 23 ? line.slice(0, 22) + '…' : line}</tspan>)}</text>
        </g>;
      })}
    </svg>}
    {!!model.nodes.length && <details className="map-records"><summary>Nearby records ({model.nodes.length - 1})</summary>{model.nodes.filter(n => n.hop > 0).map(n => <button key={n.id} disabled={pending} onClick={e => choose(n.id, 'node', e.currentTarget)}>{displayName(n)}<small>{n.hop} {n.hop === 1 ? 'step' : 'steps'}</small></button>)}</details>}
  </div>{selected && <MapInspector key={selected.kind + selected.id} selection={selected} graph={data} schema={schema} call={call} available={available} pending={pending} onSelect={id => choose(id)} onClose={clear} onFocus={onFocus} onEdit={onOpen}/>}</section>;
}
