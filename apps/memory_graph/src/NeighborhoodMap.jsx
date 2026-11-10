import React, { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { displayName } from './format.js';
import { relationshipLabel } from './briefModel.js';
import { checkedContext, pathTo, topology, travelTrace } from './neighborhoodModel.js';
import MapInspector from './MapInspector.jsx';
import useNeighborhoodMotion from './useNeighborhoodMotion.js';
import { mapLabelLines } from './neighborhoodMotion.js';

export default function NeighborhoodMap({ graph, call, available, pending, canNavigate, onOpen, onFocus, onStale, schema, preparedContext }) {
  const [depth, setDepth] = useState(2), [data, setData] = useState(null), [shownDepth, setShownDepth] = useState(2);
  const [loading, setLoading] = useState(false), [error, setError] = useState(''), [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState(null), [hovered, setHovered] = useState(null);
  const [trail, setTrail] = useState([]), [moving, setMoving] = useState(false);
  const triggerRef = useRef(null), clickTimer = useRef(null), moveRef = useRef(null), expectedRoot = useRef(null), priorGraph = useRef(graph);
  const arrow = useId();
  useEffect(() => {
    if (expectedRoot.current === graph?.start) return;
    moveRef.current = null; setTrail([]); setMoving(false);
  }, [graph?.start]);
  useEffect(() => () => clearTimeout(clickTimer.current), [graph, depth, pending]);
  useLayoutEffect(() => {
    let cancelled = false;
    const changed = graph !== priorGraph.current; priorGraph.current = graph;
    const accept = fresh => {
      setData(fresh); setShownDepth(depth); setHovered(null);
      setSelected(selection => !selection ? null : (selection.kind === 'node' ? fresh.entities : fresh.edges).some(item => item.id === selection.id) ? selection : { kind: 'node', id: fresh.start });
    };
    setError('');
    if (!graph) { setData(null); setSelected(null); setLoading(false); return; }
    if (pending) { setLoading(false); return; }
    if (!available) { accept(graph); setLoading(false); return; }
    // Navigation already obtained and checked this exact neighborhood before committing the root.
    if (changed && preparedContext?.graph === graph && preparedContext.depth === depth) {
      accept(checkedContext(null, graph, graph.start).data); setLoading(false); return;
    }
    setLoading(true);
    Promise.all([
      graph.brief ? call('memory_graph', { start: graph.start, brief_id: graph.brief.id }) : Promise.resolve(null),
      call('memory_graph', { start: graph.start, depth, limit: 16 })
    ]).then(([brief, context]) => {
      if (cancelled) return;
      const checked = checkedContext(brief, context, graph.start, graph.brief?.id);
      if (checked.stale) { onStale(checked.stale); return; }
      accept(checked.data);
    }).catch(e => { if (!cancelled) setError(e.message + (data ? ' The previous accepted view is retained.' : '')); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [graph, depth, available, pending, call, retry, onStale, preparedContext]);
  const targetModel = useMemo(() => topology(data, shownDepth), [data, shownDepth]);
  const { model, animating } = useNeighborhoodMotion(targetModel, data?.frontier, !!data?.coverage?.administrative_suppression);
  const blocked = pending || moving || loading || animating;
  const byId = new Map(model.nodes.map(n => [n.id, n]));
  const activeSelection = hovered || selected;
  const activeEdge = activeSelection?.kind === 'edge' && model.edges.find(e => e.id === activeSelection.id);
  const active = byId.get(activeEdge ? (byId.get(activeEdge.subject).hop >= byId.get(activeEdge.object).hop ? activeEdge.subject : activeEdge.object) : activeSelection?.id);
  const path = active ? pathTo(model, active.id) : { nodes: [], edges: [] };
  if (activeEdge) {
    if (!path.edges.includes(activeEdge.id)) path.edges.push(activeEdge.id);
    for (const id of [activeEdge.subject, activeEdge.object]) if (!path.nodes.includes(id)) path.nodes.push(id);
  }
  const root = byId.get(data?.start) || graph?.entities.find(n => n.id === graph.start);
  const trace = travelTrace(data, trail), previous = trace.previous;
  const linkLabel = edge => relationshipLabel(edge) === 'invests in' ? 'investment record · terms in details' : relationshipLabel(edge);
  const linkText = edge => `${displayName(byId.get(edge.subject))} → ${linkLabel(edge)} → ${displayName(byId.get(edge.object))}`;
  const choose = (id, kind = 'node', trigger) => { if (!blocked && canNavigate()) { if (trigger) triggerRef.current = trigger; setSelected({ id, kind }); } };
  const focus = async (id, trailIndex = null) => {
    clearTimeout(clickTimer.current);
    if (!available || blocked || moveRef.current || !canNavigate()) return;
    if (id === graph.start) { if (trailIndex !== null) setTrail(t => t.slice(0, trailIndex)); return; }
    const request = {}; moveRef.current = request; expectedRoot.current = id; setMoving(true);
    const next = trailIndex !== null ? trail.slice(0, trailIndex) : [...trail, { id: graph.start, label: displayName(root) }].slice(-16);
    try {
      const accepted = await onFocus(id, depth);
      if (moveRef.current === request) { if (accepted) setTrail(next); else expectedRoot.current = graph.start; }
    } finally {
      if (moveRef.current === request) { moveRef.current = null; setMoving(false); }
    }
  };
  const clickNode = (event, id) => {
    clearTimeout(clickTimer.current);
    if (event.detail > 1) return;
    const trigger = event.currentTarget;
    if (!event.detail) choose(id, 'node', trigger);
    else clickTimer.current = setTimeout(() => choose(id, 'node', trigger), 450);
  };
  const clear = () => { clearTimeout(clickTimer.current); if (canNavigate()) { setSelected(null); setHovered(null); triggerRef.current?.focus({ preventScroll: true }); } };
  return <section className={'neighborhood-map' + (selected ? ' has-inspector' : '')} aria-label="Tiered connection map"><div className="map-surface">
    <div className="map-controls"><button className="map-back" style={{ visibility: trail.length ? 'visible' : 'hidden' }} disabled={blocked || !trail.length} onClick={() => focus(trail.at(-1).id, trail.length - 1)} aria-label={trail.length ? `Back to ${trail.at(-1).label}` : 'Back'}>← Back</button><label>Outward<select aria-label="Connection tiers" value={depth} disabled={blocked} onChange={e => { if (canNavigate()) setDepth(Number(e.target.value)); }}><option value={1}>1 tier</option><option value={2}>2 tiers</option></select></label><span>Faded = indirect</span>{!available ? <small>Supplied snapshot</small> : data?.coverage.complete === false && <small>Bounded view</small>}</div>
    <nav className="map-breadcrumbs" aria-label="Exploration path">{trail.map((node, i) => <React.Fragment key={i + node.id}><button disabled={blocked} onClick={() => focus(node.id, i)}>{node.label}</button><span aria-hidden="true">›</span></React.Fragment>)}<strong aria-current="location">{displayName(root)}</strong></nav>
    <p className="map-gesture-hint" role={moving || loading || animating ? 'status' : undefined}>{moving || loading ? 'Updating connections…' : animating ? 'Moving into place…' : available ? 'Click to inspect · double-click a node to explore' : 'Select a record to inspect the supplied snapshot'}</p>
    {error && <p role="alert">{error} <button disabled={pending} onClick={() => { if (canNavigate()) setRetry(n => n + 1); }}>Retry</button></p>}
    {!!model.nodes.length && <svg viewBox="0 0 900 720" role="group" aria-label="Recorded connections by distance" aria-busy={blocked}>
      <defs><marker id={arrow} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10Z" fill="context-stroke"/></marker></defs>
      {[145, ...(shownDepth > 1 ? [285] : [])].map(r => <circle key={r} className="distance-ring" cx="450" cy="345" r={r}/>)}
      {model.edges.map(edge => {
        const a = byId.get(edge.subject), b = byId.get(edge.object), dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy) || 1;
        const radius = n => n.radius;
        const points = { x1: a.x + dx * radius(a) / length, y1: a.y + dy * radius(a) / length, x2: b.x - dx * radius(b) / length, y2: b.y - dy * radius(b) / length };
        return <g key={edge.id} className="map-edge" style={{ opacity: edge.opacity, pointerEvents: edge.exiting ? 'none' : undefined }} aria-hidden={edge.exiting || undefined} role="button" tabIndex={blocked || edge.exiting ? -1 : 0} aria-disabled={blocked || edge.exiting} aria-label={linkText(edge)} onPointerEnter={() => setHovered({ kind: 'edge', id: edge.id })} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered({ kind: 'edge', id: edge.id })} onBlur={() => setHovered(null)} onClick={e => choose(edge.id, 'edge', e.currentTarget)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(edge.id, 'edge', e.currentTarget); } }}>
          <title>{linkText(edge)}</title><line className="map-edge-hit" {...points}/><line className={'map-link' + (Math.max(a.hop, b.hop) > 1 ? ' indirect' : '') + (path.edges.includes(edge.id) ? ' active' : '') + (trace.edges.has(edge.id) ? ' traversed' : '')} {...points} markerEnd={`url(#${arrow})`}/>
        </g>;
      })}
      {model.nodes.map(node => {
        const label = displayName(node), labels = mapLabelLines(node);
        const highlighted = path.nodes.includes(node.id), isActive = active?.id === node.id;
        return <g key={node.id} className={'map-node hop-' + node.hop + (highlighted ? ' path-active' : '') + (isActive ? ' active' : '') + (node.id === previous ? ' arrived-from' : '')} transform={`translate(${node.x} ${node.y})`} style={{ opacity: node.opacity, pointerEvents: node.exiting ? 'none' : undefined }} aria-hidden={node.exiting || undefined} role="button" tabIndex={blocked || node.exiting ? -1 : 0} aria-disabled={blocked || node.exiting} aria-keyshortcuts="Enter Shift+Enter" aria-label={`${label}, ${node.hop === 0 ? 'focus' : node.hop + (node.hop === 1 ? ' step' : ' steps') + ' from ' + displayName(root)}${node.id === previous ? ', previous focus' : ''}`} onPointerEnter={() => setHovered({ kind: 'node', id: node.id })} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered({ kind: 'node', id: node.id })} onBlur={() => setHovered(null)} onClick={e => clickNode(e, node.id)} onDoubleClick={e => { e.preventDefault(); focus(node.id); }} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); clearTimeout(clickTimer.current); if (e.shiftKey && e.key === 'Enter') focus(node.id); else choose(node.id, 'node', e.currentTarget); } }}>
          <title>{label}{node.id === previous ? ' · previous focus' : ''}</title>{node.id === previous && <circle className="map-trace-mark" r={node.radius + 8}/>}<circle className="map-hit" r="46"/><circle className="map-mark" r={node.radius}/>
          <text className="map-node-label" textAnchor="middle">{labels.map((line, i) => <tspan key={i} x="0" dy={i ? 23 : node.labelY}>{line.length > 23 ? line.slice(0, 22) + '…' : line}</tspan>)}</text>
        </g>;
      })}
    </svg>}
    {!!targetModel.nodes.length && <details className="map-records"><summary>Nearby records ({targetModel.nodes.length - 1})</summary>{targetModel.nodes.filter(n => n.hop > 0).map(n => <button key={n.id} disabled={blocked} onClick={e => choose(n.id, 'node', e.currentTarget)}>{displayName(n)}<small>{n.hop} {n.hop === 1 ? 'step' : 'steps'}</small></button>)}</details>}
  </div>{selected && <MapInspector key={selected.kind + selected.id + JSON.stringify(Object.entries(data?.frontier || {}).sort())} selection={selected} graph={data} schema={schema} call={call} available={available} pending={blocked} onSelect={id => choose(id)} onClose={clear} onFocus={focus} onEdit={onOpen}/>}</section>;
}
