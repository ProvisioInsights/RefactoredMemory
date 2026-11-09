import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { connect } from './client';
import Graph from './Graph';
import Inspector from './Inspector';
import Icon from './Icon';
import { Work, Review, Activity } from './Lists';
import './styles.css';

function App() {
  const [client, setClient] = useState(null), [graph, setGraph] = useState(null), [detail, setDetail] = useState(null);
  const [view, setView] = useState('Graph'), [query, setQuery] = useState(''), [matches, setMatches] = useState(null);
  const [selected, setSelected] = useState(null), [schema, setSchema] = useState(null), [error, setError] = useState('');
  const [key, setKey] = useState(''), [fit, setFit] = useState(0), [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
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
    let stale = false;
    client.call('memory_inspect', { target_id: selected }).then(d => { if (!stale) setDetail(d); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [selected, client]);
  useEffect(() => {
    if (!client?.authenticated || !client.available || !query.trim()) { setMatches(null); return; }
    let stale = false;
    const timer = setTimeout(() => client.call('memory_search_entities', { text: query, limit: 12 }).then(data => { if (!stale) setMatches(data); }).catch(e => { if (!stale) setError(e.message); }), 180);
    return () => { stale = true; clearTimeout(timer); };
  }, [query, client]);
  const open = async (id, budget = 12) => {
    if (!client?.available) return;
    setBusy(true); setError(''); setMessage(''); setMatches(null); setView('Graph');
    try {
      const inspected = await client.call('memory_inspect', { target_id: id });
      const g = await client.call('memory_graph', { start: inspected.entity.id, depth: 1, limit: budget });
      setGraph(g); setSelected(id); setDetail(inspected);
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const saved = async correction => {
    setMessage('Saved to memory. History is retained.');
    if (correction) await open(detail.entity.id);
    else setDetail(await client.call('memory_inspect', { target_id: selected }));
  };
  const call = (name, args) => client.call(name, args);
  if (!client?.authenticated) return <main className="unlock"><h1>Open your private memory</h1><p>This graph stays within your authorized memory connection.</p>{error && <p role="alert" className="error">{error}</p>}
    {client?.local && <form onSubmit={async e => { e.preventDefault(); try { await client.unlock(key); setKey(''); location.reload(); } catch (e) { setError(e.message); } }}><label>Private access key<input type="password" value={key} onChange={e => setKey(e.target.value)} autoComplete="off" required /></label><button className="primary">Open memory</button></form>}</main>;
  return <div className="app-shell"><nav aria-label="Main navigation"><div className="brand">RefactoredMemory</div><div className="nav-items">{['Graph', 'Review', 'Work', 'Activity'].map(name => <button key={name} aria-current={view === name ? 'page' : undefined} disabled={!client.available && name !== 'Graph'} onClick={() => setView(name)}><Icon name={name}/>{name}</button>)}</div><div className="private"><Icon name="Lock"/>Private memory</div></nav>
    <main className={view === 'Graph' ? 'graph-main' : 'content-main'}>
      {view === 'Graph' ? <>
        <header className="toolbar"><h1>Explore connections</h1><div className="tools"><div className="search-wrap"><Icon name="Search"/><input aria-label="Find a person, project or topic" placeholder="Find a person, project or topic" value={query} disabled={!client.available} onChange={e => setQuery(e.target.value)} />
          {matches && <div className="search-results" role="listbox" aria-label="Matching identities">{matches.entities.length ? matches.entities.map(entity => <button key={entity.id} onClick={() => { setQuery(''); open(entity.id); }}><strong>{entity.label}</strong><small>{entity.classification?.canonical_types?.join(', ') || entity.canonical_types?.join(', ') || entity.entity_type}</small></button>) : <p>No matching identities.</p>}</div>}</div>
          <button disabled={!graph || busy || !client.available} onClick={() => { const focus = graph.entities.some(e => e.id === selected) ? selected : graph.start; open(focus, focus === graph.start ? Math.min(60, graph.coverage.limit * 2) : 12); }}><Icon name="Expand"/>Expand</button><button onClick={() => setFit(fit + 1)}><Icon name="Fit"/>Fit</button></div>
          {!client.available && <p className="warning">This host can display the graph. Additional reads and changes are unavailable here.</p>}
          {error && <p role="alert" className="error">{error}</p>}{busy && <p role="status">Reading connections…</p>}{message && <p role="status">{message}</p>}</header>
        <Graph data={graph} selected={selected} fitSignal={fit} onSelect={id => { setSelected(id); setMessage(''); }}/>
      </> : view === 'Work' ? <Work call={call} subject={detail?.entity.id} claims={detail?.claims.assertions} canWrite={detail?.permissions.write}/>
        : view === 'Review' ? <Review call={call} onSelect={open}/> : <Activity call={call} onSelect={open}/>}
    </main>
    {view === 'Graph' && <Inspector data={detail} target={selected} graph={graph} call={call} available={client.available} onSelect={setSelected} onSaved={saved} schema={schema}/>}
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
