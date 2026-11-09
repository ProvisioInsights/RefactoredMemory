import React, { useCallback, useEffect, useRef, useState } from 'react';
import { connect, displayName } from './client';
import Graph from './Graph';
import Inspector from './Inspector';
import Fields, { CreateRecord } from './Fields.jsx';
import { EDITOR_SCHEMA } from './fieldModel.js';
import Icon from './Icon';
import EditBoundary from './EditBoundary';

function InlineRecord({ id, client, call, schema, onSelect, onChanged }) {
  const [data, setData] = useState(null), [error, setError] = useState('');
  const reload = async changed => {
    try { setData(await call('memory_inspect', { target_id: id })); if (changed) onChanged(); }
    catch (e) { setError(e.message); }
  };
  useEffect(() => { let stale = false; setData(null); setError('');
    call('memory_inspect', { target_id: id }).then(r => { if (!stale) setData(r); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [id, call]);
  return <div className="inline-record">{error && <p role="alert" className="error">{error}</p>}{data ? <Fields data={data} schema={schema} call={call} available={client.available} onSaved={reload} onSelect={onSelect}/> : !error && <p role="status">Reading fields…</p>}</div>;
}

export default function App() {
  const [client, setClient] = useState(null), [graph, setGraph] = useState(null), [detail, setDetail] = useState(null);
  const [view, setView] = useState('Graph'), [query, setQuery] = useState(''), [matches, setMatches] = useState(null);
  const [selected, setSelected] = useState(null), [schema, setSchema] = useState(null), [error, setError] = useState('');
  const [key, setKey] = useState(''), [fit, setFit] = useState(0), [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(''), [inline, setInline] = useState(null), [creating, setCreating] = useState(false), [expanded, setExpanded] = useState(false);
  const [pending, setPending] = useState(false), navigationLock = useRef(false), navigationEpoch = useRef(0);
  const lock = useCallback(value => { navigationLock.current = value; setPending(value); }, []);
  const canNavigate = () => {
    if (!navigationLock.current) return true;
    setError('Finish the pending save with an identical retry or close and reload before navigating.'); return false;
  };
  const select = id => { if (canNavigate()) { navigationEpoch.current += 1; setSelected(id); setMessage(''); } };
  useEffect(() => {
    const guard = event => { if (navigationLock.current) { event.preventDefault(); event.returnValue = ''; } };
    window.addEventListener('beforeunload', guard);
    return () => window.removeEventListener('beforeunload', guard);
  }, []);
  const call = useCallback((name, args) => client.call(name, args), [client]);
  useEffect(() => {
    connect(setGraph).then(async c => {
      setClient(c);
      if (c.authenticated && c.available) {
        setSchema(await c.call('memory_schema'));
        if (c.start) { const g = await c.call('memory_graph', { start: c.start, limit: 12 }); setGraph(g); setSelected(c.start); }
      }
    }).catch(e => setError(e.message));
  }, []);
  useEffect(() => {
    if (!client?.authenticated || !client.available || !selected) return;
    let stale = false; setDetail(null);
    client.call('memory_inspect', { target_id: selected }).then(d => { if (!stale) setDetail(d); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [selected, client]);
  useEffect(() => {
    if (!client?.authenticated || !client.available || !query.trim()) { setMatches(null); return; }
    let stale = false; setMatches(null);
    const timer = setTimeout(() => client.call('memory_search_entities', { text: query, limit: 12 }).then(data => { if (!stale) setMatches(data); }).catch(e => { if (!stale) setError(e.message); }), 180);
    return () => { stale = true; clearTimeout(timer); };
  }, [query, client]);
  const open = async (id, budget = 12, full = false) => {
    if (!client?.available || !canNavigate()) return;
    const epoch = ++navigationEpoch.current;
    setBusy(true); setError(''); setMessage(''); setView('Graph'); setExpanded(full);
    try {
      const inspected = await call('memory_inspect', { target_id: id });
      const g = await call('memory_graph', { start: inspected.entity.id, depth: 1, limit: budget });
      if (epoch !== navigationEpoch.current || !canNavigate()) return;
      setGraph(g); setSelected(id); setDetail(inspected);
    } catch (e) { if (epoch === navigationEpoch.current) setError(e.message); }
    finally { if (epoch === navigationEpoch.current) setBusy(false); }
  };
  const saved = async changed => {
    const subject = detail?.entity.id;
    if (changed && subject) {
      await open(subject, 12, expanded);
      setMessage('Saved to memory. Evidence and history are retained.');
    } else if (selected) setDetail(await call('memory_inspect', { target_id: selected }));
  };
  const catalog = schema?.field_catalog;
  const editorSupported = catalog?.schema === 'refactoredmemory.fields:v1' && catalog.revision === 1 && schema?.field_editor?.schema === EDITOR_SCHEMA;
  const records = matches?.entities || (!query.trim() ? graph?.entities || [] : []);
  if (!client?.authenticated) return <main className="unlock"><h1>Open your private memory</h1><p>Your authorized connection controls which records you can read and edit.</p>{error && <p role="alert" className="error">{error}</p>}
    {client?.local && <form onSubmit={async e => { e.preventDefault(); try { await client.unlock(key); setKey(''); location.reload(); } catch (e) { setError(e.message); } }}><label>Private access key<input type="password" value={key} onChange={e => setKey(e.target.value)} autoComplete="off" required /></label><button className="primary">Open memory</button></form>}</main>;
  return <EditBoundary.Provider value={{ set: lock, active: pending }}><div className={'app-shell' + (expanded ? ' record-expanded' : '')}>
    <nav aria-label="Main navigation"><div className="brand">RefactoredMemory</div><div className="nav-items">{['Graph', 'Records'].map(name => <button key={name} aria-current={view === name ? 'page' : undefined} disabled={pending || !client.available && name !== 'Graph'} onClick={() => { setView(name); setExpanded(false); }}><Icon name={name}/>{name}</button>)}</div><p className="nav-caption">Explore what you know.<br/>Keep the evidence close.</p><div className="private"><Icon name="Lock"/>Private memory</div></nav>
    <main className={view === 'Graph' ? 'graph-main' : 'content-main'}>
      <header className="toolbar"><div className="title-row"><div><p className="eyebrow">YOUR LINKED MEMORY</p><h1>{view === 'Graph' ? 'Explore connections' : 'Explore records'}</h1></div><button className="primary" disabled={pending || !client.available || !editorSupported || !schema.permissions?.write} onClick={() => setCreating(!creating)}>New record</button></div>
        <div className="tools"><div className="search-wrap"><Icon name="Search"/><input aria-label="Find a person, project or topic" placeholder="Find a person, project or topic" value={query} disabled={pending || !client.available} maxLength={256} onChange={e => { setQuery(e.target.value); setInline(null); }} />
          {matches && view === 'Graph' && <div className="search-results" role="region" aria-label="Matching identities">{matches.entities.length ? matches.entities.map(entity => <div className="search-result" key={entity.id}><button disabled={pending} onClick={() => { if (canNavigate()) { setQuery(''); open(entity.id); } }}><strong>{displayName(entity)}</strong><small>{entity.classification?.canonical_types?.join(', ') || entity.entity_type}</small></button><button className="text-action" disabled={pending} onClick={() => { if (canNavigate()) { setView('Records'); setInline(entity.id); } }}>Edit fields</button></div>) : <p>No matching identities.</p>}</div>}</div>
          {view === 'Graph' && <><button disabled={!graph || busy || !client.available} onClick={() => { const focus = graph.entities.some(e => e.id === selected) ? selected : graph.start; open(focus, focus === graph.start ? Math.min(60, graph.coverage.limit * 2) : 12); }}><Icon name="Expand"/>Expand connections</button><button onClick={() => setFit(fit + 1)}><Icon name="Fit"/>Fit</button></>}
        </div>
        {!client.available && <p className="warning">This host can display the graph. Additional reads and changes are unavailable here.</p>}
        {client.available && !editorSupported && <p className="warning">This connection has not published the standard editor contract. Existing records remain readable.</p>}
        {error && <p role="alert" className="error">{error}</p>}{busy && <p role="status">Reading connections…</p>}{message && <p role="status">{message}</p>}
      </header>
      {creating && editorSupported && <CreateRecord catalog={catalog} call={call} onCancel={async unconfirmed => { setCreating(false); if (unconfirmed) await open(unconfirmed, 12, true); setMessage('Inspect memory history before repeating an unconfirmed creation.'); }} onSaved={async id => { setCreating(false); setQuery(''); await open(id, 12, true); setMessage('Record created. Optional fields can be added when you have evidence.'); }}/>}
      {view === 'Graph' ? <Graph data={graph} selected={selected} fitSignal={fit} onSelect={select}/>
        : <section className="record-results" aria-label="Record results"><p className="muted">{query.trim() ? `${records.length} matching identities shown${matches?.has_more ? ' · refine the search for more' : ''}` : 'Records in the selected neighborhood. Search to find other identities.'} · Names are candidates, never an automatic merge.</p>
          {records.map(entity => <article className="record-result" key={entity.id}><header><div><h2>{displayName(entity)}</h2><p className="muted">{entity.classification?.canonical_types?.join(', ') || entity.entity_type}</p></div><div className="actions"><button disabled={pending} onClick={() => open(entity.id, 12, true)}>Open record</button><button disabled={pending} onClick={() => setInline(inline === entity.id ? null : entity.id)}>{inline === entity.id ? 'Close fields' : 'Edit fields'}</button></div></header>
            {inline === entity.id && <InlineRecord id={entity.id} client={client} call={call} schema={schema} onSelect={id => open(id, 12, true)} onChanged={() => setMessage('Saved to memory. Evidence and history are retained.')}/>}</article>)}
          {!records.length && <p>{query.trim() ? 'No matching identities in this result.' : 'Search for a person, project or topic, or create a new record.'}</p>}
        </section>}
    </main>
    {view === 'Graph' && <Inspector data={detail} target={selected} graph={graph} call={call} available={client.available} onSelect={select} onSaved={saved} schema={schema} expanded={expanded} onExpand={() => { if (canNavigate()) setExpanded(!expanded); }} pending={pending} message={message} appError={error}/>}
  </div></EditBoundary.Provider>;
}
