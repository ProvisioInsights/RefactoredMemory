import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { displayName } from './format.js';
import { relationshipLabel } from './briefModel.js';
import { checkedContext, pathTo, topology } from './neighborhoodModel.js';

export default function NeighborhoodMap({ graph, call, available, pending, canNavigate, onOpen, onFocus, onStale }) {
  const [depth, setDepth] = useState(2), [data, setData] = useState(null);
  const [loading, setLoading] = useState(false), [error, setError] = useState(''), [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState(null), [hovered, setHovered] = useState(null);
  const selectionRef = useRef(null);
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
  const active = byId.get(hovered || selected), pinned = byId.get(selected);
  const path = active ? pathTo(model, active.id) : { nodes: [], edges: [] };
  const root = byId.get(data?.start);
  const lastEdge = pinned && model.edges.find(e => e.id === pathTo(model, pinned.id).edges.at(-1));
  const linkLabel = edge => relationshipLabel(edge) === 'invests in' ? 'investment record · terms in details' : relationshipLabel(edge);
  const linkText = edge => `${displayName(byId.get(edge.subject))} → ${linkLabel(edge)} → ${displayName(byId.get(edge.object))}`;
  useEffect(() => { if (selected) selectionRef.current?.scrollIntoView({ block: 'nearest' }); }, [selected]);
  const choose = id => { if (!pending && canNavigate()) setSelected(id); };
  return <section className="neighborhood-map" aria-label="Tiered connection map">
    <div className="map-controls"><label>Outward<select aria-label="Connection tiers" value={depth} disabled={pending || loading} onChange={e => { if (canNavigate()) setDepth(Number(e.target.value)); }}><option value={1}>1 tier</option><option value={2}>2 tiers</option></select></label><span>Faded = indirect</span>{!available ? <small>Supplied snapshot</small> : data?.coverage.complete === false && <small>Bounded view</small>}</div>
    {loading && <p role="status">Loading nearby connections…</p>}
    {error && <p role="alert">{error} <button disabled={pending} onClick={() => { if (canNavigate()) setRetry(n => n + 1); }}>Retry</button></p>}
    {!!model.nodes.length && <svg viewBox="0 0 900 720" role="group" aria-label="Recorded connections by distance">
      <defs><marker id={arrow} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10Z" fill="context-stroke"/></marker></defs>
      {[145, ...(depth > 1 ? [285] : [])].map(r => <circle key={r} className="distance-ring" cx="450" cy="345" r={r}/>)}
      {model.edges.map(edge => {
        const a = byId.get(edge.subject), b = byId.get(edge.object), dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy) || 1;
        const radius = n => n.hop === 0 ? 54 : n.hop === 1 ? 25 : 14;
        return <line key={edge.id} className={'map-link' + (Math.max(a.hop, b.hop) > 1 ? ' indirect' : '') + (path.edges.includes(edge.id) ? ' active' : '')} x1={a.x + dx * radius(a) / length} y1={a.y + dy * radius(a) / length} x2={b.x - dx * radius(b) / length} y2={b.y - dy * radius(b) / length} markerEnd={`url(#${arrow})`}><title>{linkText(edge)}</title></line>;
      })}
      {model.nodes.map(node => {
        const label = displayName(node), words = label.split(' '), labels = label.length > 17 ? [words.slice(0, Math.ceil(words.length / 2)).join(' '), words.slice(Math.ceil(words.length / 2)).join(' ')] : [label];
        const highlighted = path.nodes.includes(node.id), isActive = active?.id === node.id;
        return <g key={node.id} className={'map-node hop-' + node.hop + (highlighted ? ' path-active' : '') + (isActive ? ' active' : '')} transform={`translate(${node.x} ${node.y})`} role="button" tabIndex={pending ? -1 : 0} aria-disabled={pending} aria-label={`${label}, ${node.hop === 0 ? 'focus' : node.hop + (node.hop === 1 ? ' step' : ' steps') + ' from ' + displayName(root)}`} onPointerEnter={() => setHovered(node.id)} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered(node.id)} onBlur={() => setHovered(null)} onClick={() => choose(node.id)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(node.id); } }}>
          <title>{label}</title><circle className="map-hit" r="46"/><circle className="map-mark" r={node.hop === 0 ? 54 : node.hop === 1 ? 25 : 14}/>
          <text className="map-node-label" textAnchor="middle">{labels.map((line, i) => <tspan key={i} x="0" dy={i ? 23 : node.hop === 0 ? labels.length === 1 ? 7 : -5 : node.hop === 1 ? 48 : 37}>{line.length > 23 ? line.slice(0, 22) + '…' : line}</tspan>)}</text>
        </g>;
      })}
    </svg>}
    {pinned && <div className="map-selection" ref={selectionRef}><div role="status"><strong>{displayName(pinned)}</strong><p>{lastEdge ? linkText(lastEdge) : 'Current focus'}</p></div><button disabled={pending || !available || pinned.id === data.start} onClick={() => { if (canNavigate()) onFocus(pinned.id); }}>Focus here</button><button disabled={pending || !available} onClick={() => { if (canNavigate()) onOpen(pinned.id); }}>Details</button><button aria-label="Clear map selection" disabled={pending} onClick={() => { if (canNavigate()) setSelected(null); }}>Clear</button></div>}
    {!!model.nodes.length && <details className="map-records"><summary>Nearby records ({model.nodes.length - 1})</summary>{model.nodes.filter(n => n.hop > 0).map(n => <button key={n.id} disabled={pending} onClick={() => choose(n.id)}>{displayName(n)}<small>{n.hop} {n.hop === 1 ? 'step' : 'steps'}</small></button>)}</details>}
  </section>;
}
