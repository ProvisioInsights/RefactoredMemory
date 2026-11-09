import React, { useMemo, useRef, useState } from 'react';
import { forceSimulation, forceLink, forceManyBody, forceX, forceY, forceCollide } from 'd3-force';
import { human } from './client';

const typeOf = node => node.classification?.canonical_types?.[0] || node.canonical_types?.[0] || node.entity_type;

function lines(label) {
  const words = label.split(' '); if (label.length < 19) return [label];
  const middle = Math.ceil(words.length / 2); return [words.slice(0, middle).join(' '), words.slice(middle).join(' ')];
}
export default function Graph({ data, selected, onSelect, fitSignal }) {
  const svg = useRef(null), drag = useRef(null);
  const [pan, setPan] = useState({ x: 0, y: 0, zoom: 1 });
  const [positions, setPositions] = useState({});
  const layout = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    const direct = [...new Set(data.edges.flatMap(e => e.subject === data.start ? [e.object] : e.object === data.start ? [e.subject] : []))];
    const anchors = [[220, 170], [680, 170], [450, 640], [150, 540], [750, 540]];
    let outer = 0;
    const nodes = data.entities.map((n, i) => {
      let anchor = n.id === data.start ? [450, 400] : direct.includes(n.id) && direct.length <= 5 ? anchors[direct.indexOf(n.id)] : null;
      if (!anchor && direct.length <= 3) anchor = [outer++ % 2 ? 760 : 140, 520];
      if (!anchor) anchor = [450 + Math.cos(i * 2.4) * 310, 370 + Math.sin(i * 2.4) * 270];
      return { ...n, label: n.display_label || n.label, x: anchor[0], y: anchor[1], ax: anchor[0], ay: anchor[1], ...(n.id === data.start ? { fx: 450, fy: 400 } : {}) };
    });
    const links = data.edges.map(e => ({ ...e, source: e.subject, target: e.object }));
    const simulation = forceSimulation(nodes).force('link', forceLink(links).id(n => n.id).distance(300).strength(.08))
      .force('charge', forceManyBody().strength(-300)).force('x', forceX(n => n.ax).strength(.9)).force('y', forceY(n => n.ay).strength(.9))
      .force('collide', forceCollide().radius(n => n.id === data.start || typeOf(n) === 'project' ? 136 : 80)).stop();
    for (let n = 0; n < 180; n++) simulation.tick();
    return { nodes, edges: links };
  }, [data]);
  const point = node => positions[data?.start + ':' + node.id] || node;
  React.useEffect(() => {
    if (!layout.nodes.length) return;
    const points = layout.nodes.map(point);
    const left = Math.min(...points.map(p => p.x)) - 125, right = Math.max(...points.map(p => p.x)) + 125;
    const top = Math.min(...points.map(p => p.y)) - 80, bottom = Math.max(...points.map(p => p.y)) + 80;
    const zoom = Math.min(1, 860 / (right - left), 690 / (bottom - top));
    setPan({x: zoom * (450 - (left + right) / 2), y: zoom * (365 - (top + bottom) / 2), zoom});
  }, [fitSignal, data]);
  const down = (event, node) => {
    if (event.button !== 0) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { node, x: event.clientX, y: event.clientY, pan, origin: node ? point(node) : null, moved: false };
  };
  const move = event => {
    if (!drag.current) return;
    const d = drag.current, box = svg.current.getBoundingClientRect(), ratio = 900 / box.width;
    const dx = (event.clientX - d.x) * ratio, dy = (event.clientY - d.y) * ratio;
    if (Math.abs(dx) + Math.abs(dy) > 5) d.moved = true;
    if (d.node) setPositions(old => ({ ...old, [data.start + ':' + d.node.id]: { x: d.origin.x + dx / pan.zoom, y: d.origin.y + dy / pan.zoom } }));
    else setPan({ ...d.pan, x: d.pan.x + dx, y: d.pan.y + dy });
  };
  return <div className="canvas-wrap">
    {!data && <div className="canvas-empty"><h2>Start with a person or project.</h2><p>Search above to explore their connections and evidence.</p></div>}
    <svg ref={svg} className={'graph ' + (layout.edges.length > 10 ? 'dense' : '')} viewBox="0 0 900 730" role="group" aria-label="Knowledge graph"
      onPointerDown={e => { if (e.target === svg.current) down(e, null); }} onPointerMove={move}
      onPointerUp={() => { drag.current = null; }} onPointerCancel={() => { drag.current = null; }}
      onWheel={e => setPan(p => ({ ...p, zoom: Math.max(.45, Math.min(2.5, p.zoom * (e.deltaY > 0 ? .9 : 1.1))) }))}>
      <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" /></marker></defs>
      <g transform={`translate(${pan.x} ${pan.y}) translate(450 365) scale(${pan.zoom}) translate(-450 -365)`}>
        {layout.edges.map(edge => {
          const a = point(edge.source), b = point(edge.target), dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy) || 1;
          const radius = node => typeOf(node) === 'project'
            ? Math.min(118 / Math.max(.001, Math.abs(dx)), 42 / Math.max(.001, Math.abs(dy))) : 63 / distance;
          const from = radius(edge.source), to = radius(edge.target);
          const center = layout.edges.length > 10 ? from + (1 - from - to) * (edge.target.id === data.start ? .25 : .75) : (from + 1 - to) / 2;
          const active = selected === edge.id, label = human(edge.predicate);
          return <g key={edge.id} className={'edge ' + (active ? 'selected' : '')} onClick={() => onSelect(edge.id)}>
            <line x1={a.x + dx * from} y1={a.y + dy * from} x2={b.x - dx * to} y2={b.y - dy * to}
              markerEnd="url(#arrow)" strokeDasharray={edge.review?.human_verified ? undefined : '4 5'} />
            <g role="button" tabIndex="0" aria-label={`${edge.source.label} ${label} ${edge.target.label}`}
              onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(edge.id); } }}>
              <rect x={a.x + dx * center - Math.min(130, label.length * 4.3 + 8)} y={a.y + dy * center - 14} width={Math.min(260, label.length * 8.6 + 16)} height="28" rx="5" />
              <text x={a.x + dx * center} y={a.y + dy * center + 5}>{label}</text>
            </g>
          </g>;
        })}
        {layout.nodes.map(node => {
          const p = point(node), type = typeOf(node);
          const project = type === 'project';
          return <g key={node.id} transform={`translate(${p.x},${p.y})`} className={`node ${type} ${selected === node.id ? 'selected' : ''}`}
            role="button" tabIndex="0" aria-label={`Explore ${node.label}`} onPointerDown={e => { e.stopPropagation(); down(e, node); }}
            onClick={() => { if (!drag.current?.moved) onSelect(node.id); }} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(node.id); } }}>
            {project ? <rect x="-118" y="-42" width="236" height="84" rx="12" /> : <circle r="62" />}
            <text textAnchor="middle">{lines(node.label).map((line, i, list) => <tspan key={i} x="0" dy={i ? 22 : list.length === 1 ? 6 : -5}>{line.length > 25 ? line.slice(0, 24) + '…' : line}</tspan>)}</text>
          </g>;
        })}
      </g>
    </svg>
    <p className="graph-caption">Connections show claims. Evidence explains them.{layout.edges.length > 10 ? ' Select a line to see its relationship.' : ''}{data && !data.coverage.complete ? ' Showing a bounded neighborhood.' : ''}</p>
  </div>;
}
