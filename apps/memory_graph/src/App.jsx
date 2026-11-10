import React, { useCallback, useEffect, useRef, useState } from 'react';
import { connect, displayName } from './client';
import Graph from './Graph';
import Inspector from './Inspector';
import { CreateRecord } from './Fields.jsx';
import { EDITOR_SCHEMA } from './fieldModel.js';
import { BRIEF_SCHEMA, briefRows, validGraphSnapshot } from './briefModel.js';
import { ResultGroups, Explanation, RecordView } from './Brief.jsx';
import Icon from './Icon';
import EditBoundary from './EditBoundary';

export default function App() {
  const [client, setClient] = useState(null), [graph, setGraph] = useState(null), [context, setContext] = useState(null);
  const [selected, setSelected] = useState(null), [detail, setDetail] = useState(null), [target, setTarget] = useState(null), [evidence, setEvidence] = useState(null);
  const [schema, setSchema] = useState(null), [view, setView] = useState('Explore'), [mode, setMode] = useState('Brief');
  const [query, setQuery] = useState(''), [matches, setMatches] = useState(null), [error, setError] = useState(''), [message, setMessage] = useState('');
  const [key, setKey] = useState(''), [busy, setBusy] = useState(false), [pending, setPending] = useState(false), [expanded, setExpanded] = useState(false);
  const [tab, setTab] = useState('Fields'), [creating, setCreating] = useState(false), [filters, setFilters] = useState(false), [typeFilter, setTypeFilter] = useState('');
  const [inlineId, setInlineId] = useState(null);
  const [offers, setOffers] = useState([]), [incoming, setIncoming] = useState(false);
  const lockRef = useRef(false), epoch = useRef(0), incomingRef = useRef(null), clientRef = useRef(null), openRef = useRef(null), hasView = useRef(false);
  const lock = useCallback(value => { lockRef.current = value; setPending(value); }, []);
  const navigate = () => { if (!lockRef.current) return true; setError('Finish the pending save with an identical retry or close and reload before navigating.'); return false; };
  const call = useCallback((name, args = {}) => client.call(name, args), [client]);
  const choose = (row, toggle = false) => {
    if (!navigate()) return;
    setSelected(row.entity_id); setInlineId(toggle && inlineId === row.entity_id ? null : row.entity_id);
    setTarget(row.claim_ids[0] || null); setTab('Fields'); setError('');
  };
  const apply = useCallback(async (g, explicit = false) => {
    if (!validGraphSnapshot(g)) { setError('The supplied view is malformed. Your current view is unchanged.'); return; }
    if (lockRef.current || !clientRef.current || hasView.current && !explicit) { incomingRef.current = g; setIncoming(true); return; }
    if (clientRef.current.available) {
      const accepted = await openRef.current(g.start, { briefId: g.brief?.id || null }, clientRef.current);
      if (!accepted && lockRef.current) { incomingRef.current = g; setIncoming(true); }
      else if (accepted && incomingRef.current === g) { incomingRef.current = null; setIncoming(false); }
      return;
    }
    // A display-only host supplies a snapshot, not a current-input validation.
    if (g.brief && g.brief.freshness?.state !== 'stale') g = { ...g, brief: { ...g.brief, freshness: { state: 'unverified' } } };
    epoch.current += 1;
    hasView.current = true; setGraph(g); setExpanded(false); setView('Explore'); setMode('Brief'); setQuery(''); setTypeFilter('');
    const row = briefRows(g).flatMap(group => group.items)[0];
    setSelected(row?.entity_id || g.start); setInlineId(row?.entity_id || null); setTarget(row?.claim_ids[0] || null); setTab('Fields');
    incomingRef.current = null; setIncoming(false);
  }, []);
  const open = async (id, { briefId, full = false, budget = 12 } = {}, connection = client) => {
    if (!connection?.available || !navigate()) return;
    const request = ++epoch.current;
    setBusy(true); setError(''); setMessage('');
    try {
      const inspected = await connection.call('memory_inspect', { target_id: id });
      const available = (inspected.artifacts || []).filter(a => a.value?.view?.schema === BRIEF_SCHEMA);
      const chosen = briefId === undefined && available.length === 1 ? available[0].id : briefId;
      const g = await connection.call('memory_graph', { start: inspected.entity.id, depth: 1, limit: budget, ...(chosen ? { brief_id: chosen } : {}) });
      if (request !== epoch.current || !navigate()) return false;
      hasView.current = true; setContext(inspected); setOffers(available); setGraph(g); setView('Explore'); setExpanded(full); setTypeFilter(''); setQuery('');
      const row = briefRows(g).flatMap(group => group.items)[0];
      setSelected(full ? inspected.entity.id : row?.entity_id || inspected.entity.id);
      setInlineId(row?.entity_id || null);
      setTarget(full ? null : row?.claim_ids[0] || null); setTab('Fields');
      return true;
    } catch (e) { if (request === epoch.current) setError(e.message); }
    finally { if (request === epoch.current) setBusy(false); }
  };
  openRef.current = open;
  useEffect(() => {
    let stale = false;
    connect(apply).then(async c => {
      if (stale) return;
      clientRef.current = c;
      setClient(c);
      if (c.authenticated && c.available) {
        const discovery = await c.call('memory_schema');
        if (stale) return;
        setSchema(discovery);
        if (incomingRef.current) await apply(incomingRef.current);
        else if (c.start) await open(c.start, {}, c);
      }
      else if (incomingRef.current) await apply(incomingRef.current);
    }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [apply]);
  useEffect(() => {
    const guard = event => { if (lockRef.current) { event.preventDefault(); event.returnValue = ''; } };
    window.addEventListener('beforeunload', guard);
    return () => window.removeEventListener('beforeunload', guard);
  }, []);
  useEffect(() => {
    if (!client?.available || !graph?.start) return;
    let stale = false;
    call('memory_inspect', { target_id: graph.start }).then(data => {
      if (!stale) { setContext(data); setOffers((data.artifacts || []).filter(a => a.value?.view?.schema === BRIEF_SCHEMA)); }
    }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [graph?.start, client, call]);
  useEffect(() => {
    if (!client?.available || !selected) return;
    let stale = false; setDetail(null);
    call('memory_inspect', { target_id: selected }).then(d => { if (!stale) setDetail(d); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [selected, client, call]);
  useEffect(() => {
    if (!client?.available || !target) { setEvidence(null); return; }
    let stale = false; setEvidence(null);
    call('memory_inspect', { target_id: target }).then(d => { if (!stale) setEvidence(d); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [target, client, call]);
  useEffect(() => {
    if (!client?.available || !query.trim()) { setMatches(null); return; }
    let stale = false; setMatches(null);
    const timer = setTimeout(() => call('memory_search_entities', { text: query, limit: 12 }).then(r => { if (!stale) setMatches(r); }).catch(e => { if (!stale) setError(e.message); }), 180);
    return () => { stale = true; clearTimeout(timer); };
  }, [query, client, call]);
  const inspectTarget = async id => {
    if (!navigate() || !client.available) return;
    const request = ++epoch.current;
    try {
      const d = await call('memory_inspect', { target_id: id });
      if (request !== epoch.current || !navigate()) return;
      if (d.claims.assertions.some(c => c.id === id)) { setTarget(id); setEvidence(d); }
      else await open(d.entity.id, { full: true, briefId: null });
    } catch (e) { if (request === epoch.current) setError(e.message); }
  };
  const saved = async changed => {
    const request = ++epoch.current;
    try {
      const [d, g, freshMatches] = await Promise.all([
        call('memory_inspect', { target_id: selected }),
        graph ? call('memory_graph', { start: graph.start, depth: 1, limit: graph.coverage.limit || 12, ...(graph.brief ? { brief_id: graph.brief.id } : {}) }) : Promise.resolve(null),
        query.trim() ? call('memory_search_entities', { text: query, limit: 12 }) : Promise.resolve(null)
      ]);
      if (request !== epoch.current || lockRef.current) return;
      setDetail(d); if (g) setGraph(g); if (freshMatches) setMatches(freshMatches);
      const currentRow = briefRows(g).flatMap(group => group.items).find(item => item.entity_id === selected);
      setTarget(currentRow?.claim_ids[0] || null); setEvidence(null);
      if (g?.brief?.freshness?.state === 'stale') setMessage('Saved. This brief needs a client refresh because a supporting input changed. Earlier evidence remains in history.');
      else setMessage(changed ? 'Saved to memory. Earlier evidence and history are retained.' : 'Record refreshed. Inspect history before making a different change.');
    } catch (e) {
      if (request !== epoch.current || lockRef.current) return;
      setError(e.message);
      setMessage(changed ? 'The save was confirmed, but the view could not be refreshed. Inspect history before making another change.' : 'The view could not be refreshed. Inspect history before making another change.');
      if (graph?.brief) {
        setGraph({ ...graph, edges: [], brief: { id: graph.brief.id, freshness: { state: 'stale' } } });
        setTarget(null); setEvidence(null);
      }
    }
  };
  const groups = briefRows(graph), rows = groups.flatMap(g => g.items), row = rows.find(r => r.entity_id === selected);
  const contextEntity = graph?.entities.find(e => e.id === graph.start), contextName = displayName(contextEntity);
  const catalog = schema?.field_catalog;
  const supported = catalog?.schema === 'refactoredmemory.fields:v1' && catalog.revision === 1
    && schema?.field_editor?.schema === EDITOR_SCHEMA && Array.isArray(catalog.record_types)
    && catalog.fields?.['identity.name']?.value_type === 'text'
    && catalog.fields?.['identity.type']?.value_type === 'entity_type';
  const staleBrief = graph?.brief?.freshness.state === 'stale';
  const results = matches?.entities || (!query.trim() ? graph?.entities || [] : []);
  const types = [...new Set([...(view === 'Records' ? catalog?.record_types || [] : []), ...(view === 'Records' ? results : rows.map(r => r.entity)).flatMap(entity => entity.classification?.canonical_types?.length ? entity.classification.canonical_types : [entity.entity_type])])].filter(Boolean);
  const filteredResults = results.filter(entity => !typeFilter || (entity.classification?.canonical_types?.length ? entity.classification.canonical_types : [entity.entity_type]).includes(typeFilter));
  if (!client?.authenticated) return <main className="unlock"><h1>Open your private memory</h1><p>Your connection controls which records you can read and edit.</p>{error && <p className="error" role="alert">{error}</p>}{client?.local && <form onSubmit={async e => { e.preventDefault(); try { await client.unlock(key); setKey(''); location.reload(); } catch (e) { setError(e.message); } }}><label>Private access key<input type="password" value={key} onChange={e => setKey(e.target.value)} autoComplete="off" required/></label><button className="primary">Open memory</button></form>}</main>;
  return <EditBoundary.Provider value={{ set: lock, active: pending }}><div className="relationship-app">
    <header className="app-topbar"><div className="brand">RefactoredMemory</div><nav aria-label="Main navigation">{['Explore', 'Records'].map(name => <button key={name} aria-current={view === name ? 'page' : undefined} disabled={pending} onClick={() => { if (navigate()) { setView(name); setExpanded(false); setTypeFilter(''); setFilters(false); } }}>{name}</button>)}</nav>
      <div className="global-search search-wrap"><Icon name="Search"/><input aria-label="Find a person, project or topic" placeholder="Search memory…" value={query} disabled={pending || !client.available} maxLength={256} onChange={e => setQuery(e.target.value)}/>
        {matches && view === 'Explore' && <div className="search-results" role="region" aria-label="Matching identities">{matches.entities.map(entity => <button key={entity.id} disabled={pending} onClick={() => open(entity.id)}><strong>{displayName(entity)}</strong><small>{entity.classification?.canonical_types?.join(', ') || entity.entity_type}</small></button>)}{!matches.entities.length && <p>No matching identities.</p>}{matches.has_more && <p>Refine the name to find other matches.</p>}</div>}</div>
      <div className="private"><Icon name="Lock"/>Private memory</div>
    </header>
    <div className="app-notices">{error && <p className="error" role="alert">{error}</p>}{message && <p role="status">{message}</p>}{busy && <p role="status">Reading the selected view…</p>}{!client.available && <p className="warning">This host displays supplied records. Additional reads and changes are unavailable.</p>}{client.available && schema?.permissions && !schema.permissions.correct && <p className="access-caption">{schema.permissions.write ? 'This connection can add records and details. Correcting existing claims is unavailable.' : 'This connection is read-only. You can inspect records, sources and history.'}</p>}{incoming && <button disabled={pending} onClick={() => { if (navigate()) apply(incomingRef.current, true); }}>Open the new view supplied by your client</button>}</div>
    {expanded ? <div className="expanded-record"><Inspector data={target ? evidence : detail} target={target || selected} graph={graph} call={call} available={client.available} onSelect={inspectTarget} onSaved={saved} schema={schema} expanded onExpand={() => { if (navigate()) setExpanded(false); }} pending={pending} message={message} appError={error}/></div>
      : <div className={'brief-layout' + (view === 'Records' ? ' records-layout' : '')}>
        <main className="brief-main"><header className="brief-header"><p className="breadcrumb">{contextEntity ? contextName : 'Your memory'}<span>/</span>{view === 'Records' ? 'Records' : 'Explore connections'}{graph?.example_data && <small className="example-label">Example data</small>}</p>
          <h1>{view === 'Records' ? 'Explore records' : staleBrief ? 'This brief needs a refresh' : graph?.brief?.title || (contextEntity ? `Connections around ${contextName}` : 'Start with what matters.')}</h1>
          <p className="brief-summary">{view === 'Records' ? 'Find an identity. Inspect and correct its sourced fields.' : staleBrief ? 'A supporting input is unavailable or has changed. The earlier explanation is withheld.' : graph?.brief?.text || (contextEntity ? 'Direct recorded connections, with their evidence close at hand.' : 'Find a person, project or idea to explore its important connections.')}</p>
          {graph && view === 'Explore' && <p className="coverage-note">{!client.available ? 'Supplied snapshot · this host cannot refresh its inputs' : graph.brief ? 'Client-selected connections · current status may be unverified' : 'A bounded set of direct recorded connections'}</p>}
          <div className="brief-controls">{view === 'Explore' && <div className="view-switch" aria-label="Explore view">{['Brief', 'Connections'].map(name => <button key={name} aria-pressed={mode === name} disabled={pending} onClick={() => { if (navigate()) setMode(name); }}>{name}</button>)}</div>}
            {view === 'Explore' && offers.length > 0 && <label className="brief-picker">Prepared view<select aria-label="Prepared view" value={graph?.brief?.id || ''} disabled={pending || !client.available} onChange={e => open(graph.start, { briefId: e.target.value || null })}><option value="">Current connections</option>{offers.map(a => <option key={a.id} value={a.id}>{a.freshness.state === 'stale' ? 'Needs refresh · ' : ''}{a.value.title}</option>)}</select></label>}
            <button className="filter-toggle" aria-expanded={filters} disabled={pending} onClick={() => { if (navigate()) setFilters(!filters); }}>Filters</button>{view === 'Records' && <button className="new-record-button" disabled={pending || !client.available || !supported || !schema.permissions?.write} onClick={() => { if (navigate()) setCreating(!creating); }}>New record</button>}
          </div>
          {filters && <label className="type-filter">Record type<select value={typeFilter} disabled={pending} onChange={e => setTypeFilter(e.target.value)}><option value="">All types in this view</option>{types.map(t => <option key={t}>{t}</option>)}</select></label>}
        </header>
        {creating && supported && <CreateRecord catalog={catalog} call={call} onCancel={async id => { setCreating(false); if (id) { await open(id, { full: true, briefId: null }); setMessage('Creation is unconfirmed. Inspect matching records and history before creating another identity.'); } }} onSaved={async id => { setCreating(false); await open(id, { full: true, briefId: null }); setMessage('Record created. Optional fields can be added when supported by evidence.'); }}/>}
        {view === 'Records' ? <section className="identity-results"><p className="muted">{query.trim() ? `${filteredResults.length} matching identities shown${matches?.has_more ? ' · refine your search for more' : ''}` : 'Records in the current view. Search to find other identities.'} Names are candidates; identities remain separate.</p>{filteredResults.map(entity => <article className="identity-result" key={entity.id}><header><button disabled={pending} onClick={() => { if (navigate()) { setSelected(entity.id); setTab('Fields'); } }}><strong>{displayName(entity)}</strong><small>{entity.classification?.canonical_types?.join(', ') || entity.entity_type}</small></button><button disabled={pending || !client.available} onClick={() => open(entity.id, { full: true, briefId: null })}>Open record</button></header>{selected === entity.id && <RecordView data={detail} schema={schema} call={call} available={client.available} pending={pending} onSaved={saved} onSelect={inspectTarget} tab={tab} setTab={setTab}/>}</article>)}{!filteredResults.length && <p>No identities match this bounded selection. Change the type filter or refine your search.</p>}</section>
          : staleBrief ? <div className="stale-brief"><p>Ask your connected client to regenerate the brief from current evidence, or browse the current recorded connections.</p><button disabled={pending || !client.available} onClick={() => open(graph.start, { briefId: null })}>Browse current connections</button></div>
          : mode === 'Connections' ? <Graph data={graph} selected={target || selected} onSelect={inspectTarget}/>
          : <><ResultGroups groups={groups} selected={selected} inlineId={inlineId} onChoose={choose} pending={pending} detail={detail} schema={schema} call={call} available={client.available} onSaved={saved} onSelect={inspectTarget} tab={tab} setTab={setTab} typeFilter={typeFilter}/>{graph && !graph.brief && graph.coverage.complete === false && <button className="more-connections" disabled={pending || !client.available} onClick={() => open(graph.start, { briefId: null, budget: Math.min(60, (graph.coverage.limit || 12) * 2) })}>Read more direct connections</button>}</>}
        </main>
        {view === 'Explore' && !staleBrief && <Explanation graph={graph} row={row} target={target} evidence={evidence} call={call} available={client.available} pending={pending} onSelect={inspectTarget} onTarget={id => { if (navigate()) setTarget(id); }} onOpen={() => { if (navigate()) { setTarget(null); setExpanded(true); } }}/>}</div>}
  </div></EditBoundary.Provider>;
}
