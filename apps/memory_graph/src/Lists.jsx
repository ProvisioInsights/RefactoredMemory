import React, { useEffect, useRef, useState } from 'react';
import { compact, human, requestId } from './client';

export function Work({ call, subject, claims, canWrite }) {
  const [data, setData] = useState(null), [error, setError] = useState(''), [creating, setCreating] = useState(false), [title, setTitle] = useState('');
  const [selected, setSelected] = useState([]), [offset, setOffset] = useState(0);
  const saveRequest = useRef(null);
  const load = () => call('memory_tasks', { limit: 30, offset }).then(setData).catch(e => setError(e.message));
  useEffect(() => { load(); }, [offset]);
  const candidates = (claims || []).filter(c => !c.predicate.startsWith('rm:task') && c.predicate !== 'rm:canonical-type').slice(0, 20);
  return <section className="list-view"><header className="list-header"><h1>Work</h1><button disabled={!canWrite || !subject} onClick={() => { saveRequest.current = requestId(); setCreating(!creating); setSelected(candidates.slice(0, 1).map(c => c.id)); }}>New work</button></header>
    <p className="muted">Connected assistants do the processing. RM keeps the evidence, progress and results.</p>
    {error && <p role="alert" className="error">{error}</p>}
    {creating && <form className="work-form" onSubmit={async e => { e.preventDefault(); setError(''); try {
      await call('memory_task', { action: 'create', subject, title, inputs: selected.map(id => ({ kind: 'assertion', id })), request_id: saveRequest.current, reported: { application: 'RM graph review' } }); setCreating(false); setTitle(''); load();
    } catch (e) { setError(e.message); } }}><h2>Create a processing task</h2><label>What should the assistant do?<input value={title} onChange={e => setTitle(e.target.value)} maxLength={256} required /></label>
      <fieldset><legend>Evidence to process</legend>{candidates.map(c => <label className="check" key={c.id}><input type="checkbox" checked={selected.includes(c.id)} onChange={e => setSelected(old => e.target.checked ? [...old, c.id] : old.filter(id => id !== c.id))}/>{human(c.predicate)} · {compact(c.value || c.object).slice(0, 95)}</label>)}{!candidates.length && <p>Select a sourced claim in the graph first.</p>}</fieldset>
      <p className="muted">An authorized client must claim this task. Creating it does not start a model or incur an API call.</p><button className="primary" disabled={!selected.length}>Create task</button></form>}
    {!data?.assertions.length && <p>No work items on this page.</p>}
    {data?.assertions.map(job => <article className="list-row" key={job.id}><div><h2>{job.value.title}</h2><p>{job.value.status} · {job.value.inputs.length} pinned inputs · {job.value.output_ids.length} output records</p>{job.conflicts.length > 0 && <p className="warning">Concurrent claims need owner resolution.</p>}<details><summary>Progress and attribution</summary><pre>{compact({ checkpoint: job.value.checkpoint, requester: job.value.requester, assigned_connection: job.value.assignee, job_id: job.subject, revision: job.id })}</pre></details></div></article>)}
    <div className="pagination"><button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 30))}>Previous</button><button disabled={!data?.coverage.has_more} onClick={() => setOffset(offset + 30)}>Next</button></div>
  </section>;
}

export function Review({ call, onSelect }) {
  const [data, setData] = useState(null), [offset, setOffset] = useState(0), [error, setError] = useState('');
  useEffect(() => { call('memory_reviews', { offset, limit: 30 }).then(setData).catch(e => setError(e.message)); }, [offset]);
  return <section className="list-view"><h1>Review</h1><p className="muted">Uncertainty stays visible. These are review records, not counts of distinct people.</p>{error && <p role="alert">{error}</p>}
    {data?.items.map(r => <article className="list-row" key={r.id}><div><h2>{r.label}</h2><p>{r.value.reason || r.value.note || human(r.predicate)}</p><details><summary>Review details</summary><pre>{compact(r.value)}</pre></details></div><button onClick={() => onSelect(r.value.target_id || r.subject)}>Inspect</button></article>)}
    {data && !data.items.length && <p>No pending records on this page.</p>}<div className="pagination"><button disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 30))}>Previous</button><button disabled={!data?.has_more} onClick={() => setOffset(data.next_offset)}>Next</button></div></section>;
}

export function Activity({ call, onSelect }) {
  const [data, setData] = useState(null), [cursor, setCursor] = useState(0), [connection, setConnection] = useState(''), [filter, setFilter] = useState(''), [error, setError] = useState('');
  useEffect(() => { call('memory_activity', { since: cursor, limit: 30, ...(filter ? { connection_id: filter } : {}) }).then(setData).catch(e => setError(e.message)); }, [cursor, filter]);
  return <section className="list-view"><h1>Activity</h1><p className="muted">Who contributed, what changed, and which processor was reported.</p>
    <form className="activity-filter" onSubmit={e => { e.preventDefault(); setCursor(0); setFilter(connection); }}><label>Connection ID<input value={connection} onChange={e => setConnection(e.target.value)} placeholder="All authorized connections" /></label><button>Filter</button></form>
    {error && <p role="alert">{error}</p>}{data?.items.map(item => <article className="list-row" key={item.operation_id + item.id}><div><h2>{human(item.predicate)}</h2><p>{item.action} · {item.connection.kind} connection · {item.outcome}</p><p className="muted">{item.reported_processor.application || 'Application not recorded'}{item.reported_processor.model ? ' · ' + item.reported_processor.model + ' (reported)' : ''}</p><details><summary>Attribution details</summary><pre>{compact(item)}</pre></details></div><button onClick={() => onSelect(item.subject)}>Inspect</button></article>)}
    {data && !data.items.length && <p>No matching contributions on this bounded page.</p>}<div className="pagination"><button disabled={!cursor} onClick={() => setCursor(0)}>First page</button><button disabled={!data?.has_more} onClick={() => setCursor(data.next_since)}>Next</button></div></section>;
}
