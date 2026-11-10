import React, { useEffect, useState } from 'react';
import { compact, displayName, human } from './client';
import Fields from './Fields.jsx';
import { Source } from './Inspector.jsx';
import Graph from './Graph.jsx';
import { selectedPath } from './briefModel.js';

export function RecordView({ data, schema, call, available, pending, onSaved, onSelect, tab, setTab, claimIds = [] }) {
  const [history, setHistory] = useState(null), [error, setError] = useState('');
  useEffect(() => { setHistory(null); setError(''); }, [data?.entity.id]);
  useEffect(() => {
    if (tab !== 'History' || !available || !data) return;
    let stale = false;
    call('memory_history', { entity_id: data.entity.id, limit: 30 }).then(r => { if (!stale) setHistory(r); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [tab, data, call, available]);
  if (!data) return <p role="status">{available ? 'Reading the selected record…' : 'This host cannot read additional fields, evidence or history.'}</p>;
  const claims = data.claims.assertions.filter(c => claimIds.includes(c.id));
  return <div className="brief-record-view">
    <div className="tabs" role="tablist" aria-label="Selected record">{['Fields', 'Evidence', 'History'].map(t => <button key={t} role="tab" aria-selected={tab === t} disabled={pending} onClick={() => setTab(t)}>{t}</button>)}</div>
    {error && <p className="error" role="alert">{error}</p>}
    {tab === 'Fields' && <Fields compact data={data} schema={schema} call={call} available={available} onSaved={onSaved} onSelect={onSelect}/>}
    {tab === 'Evidence' && <div className="inline-evidence"><p className="muted">Source references support individual claims; independence is not established.</p>{claims.length ? claims.map(c => <section key={c.id}><h3>{human(c.predicate)}</h3>{c.source_ids.slice(0, 3).map((id, i) => available ? <Source key={id} id={id} target={c.id} call={call} auto={i === 0} disabled={pending}/> : <p key={id}>Source reading is unavailable in this host.</p>)}</section>) : <p>Choose a connection in the explanation pane to read its exact evidence. Full record claims remain available through Fields.</p>}</div>}
    {tab === 'History' && <div className="readable-history">{!available ? <p>History reading is unavailable in this host.</p> : !history ? <p role="status">Reading history…</p> : <><p className="muted">This peer’s recorded history; earlier evidence is retained.</p><ol>{(history.operations || []).map(op => <li key={op.id}><strong>{op.actor?.kind === 'owner' ? 'Owner contribution' : 'Attributed contribution'}</strong><p>{op.received_at || op.id}</p><span>{op.actions?.filter(a => a.type === 'assertion').map(a => human(a.predicate)).join(' · ')}</span></li>)}</ol><details><summary>Operation details and retained revisions</summary><pre>{JSON.stringify(history, null, 2)}</pre></details></>}</div>}
  </div>;
}

export function ResultGroups({ groups, selected, inlineId, onChoose, pending, detail, schema, call, available, onSaved, onSelect, tab, setTab, typeFilter }) {
  const filtered = groups.map(group => ({ ...group, items: group.items.filter(r => !typeFilter || (r.entity.classification?.canonical_types || [r.entity.entity_type]).includes(typeFilter)) })).filter(g => g.items.length);
  return <div className="brief-results">{filtered.map(group => <section className="brief-group" key={group.title}><h2>{group.title}</h2>{group.items.map(row => <article className={'brief-result' + (selected === row.entity_id ? ' selected-result' : '')} key={row.entity_id}>
    <div className="brief-result-heading"><button className="record-choice" disabled={pending} aria-expanded={inlineId === row.entity_id} onClick={() => onChoose(row, true)}><strong>{displayName(row.entity)}<small className="record-type">{row.entity.classification?.ambiguous ? 'Type disputed' : row.entity.classification?.canonical_types?.[0] || row.entity.entity_type}</small></strong><span>{row.relationship}{row.date ? ` · reported from ${row.date}` : ' · date not recorded'}</span></button>
      <div className="row-basis"><p>{row.why}</p>{row.context && <p className="muted relationship-context">{row.context}</p>}</div>
      <button className="source-count" disabled={pending || !available} onClick={() => { onChoose(row); setTab('Evidence'); }}>{row.sourceCount} source reference{row.sourceCount === 1 ? '' : 's'}</button>
      <button className="review-record" disabled={pending || !available} onClick={() => onChoose(row)}>Review</button>
    </div>
    {inlineId === row.entity_id && <RecordView data={detail?.entity.id === selected ? detail : null} schema={schema} call={call} available={available} pending={pending} onSaved={onSaved} onSelect={onSelect} tab={tab} setTab={setTab} claimIds={row.claim_ids}/>}
  </article>)}</section>)}{!filtered.length && <p className="empty-state">No connections in this selection match the filter. Search for another record or broaden the view.</p>}</div>;
}

export function Explanation({ graph, row, target, evidence, call, available, pending, onSelect, onTarget, onOpen }) {
  const path = selectedPath(graph, row);
  const chosen = evidence?.claims.assertions.find(c => c.id === target);
  if (!row) return <aside className="brief-explanation"><h2>Follow what matters.</h2><p>Select a record to see its supporting connection and evidence.</p></aside>;
  return <aside className="brief-explanation"><h2>Why {displayName(row.entity)} appears</h2>
    {path && <div className="brief-path"><Graph compact data={path} selected={target} onSelect={onSelect}/></div>}
    <section className="explanation-basis"><h3>{graph.brief ? 'Client explanation' : 'Recorded connection'}</h3><p>{row.why}</p>{graph.brief && <p className="muted">Client interpretation · not independent confirmation.</p>}
      <details className="supporting-claims"><summary>{row.supporting.length} supporting claim{row.supporting.length === 1 ? '' : 's'}</summary>{row.supporting.map(claim => <button className={'claim-choice' + (target === claim.id ? ' active-claim' : '')} key={claim.id} disabled={pending || !available} onClick={() => onTarget(claim.id)}><strong>{human(claim.predicate)}</strong><span>{claim.valid_from ? `Reported from ${claim.valid_from}` : 'Date not recorded'} · {claim.source_ids.length} source reference{claim.source_ids.length === 1 ? '' : 's'}</span>{claim.conflicts?.length > 0 && <small>Competing revisions retained</small>}</button>)}</details>
    </section>
    <section className="explanation-evidence"><h3>Evidence</h3>{!available ? <p>This host can display the selection; source reads are unavailable.</p> : !chosen ? <p role="status">Choose a connection to inspect its exact source.</p> : <><p className="muted">{chosen.review?.human_verified ? 'Owner reviewed this revision' : 'Source reported · current status unverified'}</p>{!chosen.object && <p className="statement">{compact(chosen.excerpt ?? chosen.value)}</p>}{chosen.source_ids.slice(0, 2).map(id => <Source key={chosen.id + id} id={id} target={chosen.id} call={call} auto disabled={pending}/>)}{chosen.source_ids.length > 2 && <p className="muted">Additional source references remain in the full record.</p>}</>}</section>
    <button className="open-full-record" disabled={pending || !available} onClick={onOpen}>Open full record</button>
    {graph.brief?.contribution && <footer className="brief-attribution"><p>Prepared through {graph.brief.contribution.reported?.application || 'an authenticated client'}</p><details><summary>Contribution and input details</summary><dl><dt>Authenticated connection</dt><dd>{graph.brief.contribution.connection?.id}</dd><dt>Reported model</dt><dd>{graph.brief.contribution.reported?.model || 'Not recorded'}</dd></dl><p>Reported processor metadata is client-supplied. Inputs remain pinned; this is not owner verification.</p></details></footer>}
  </aside>;
}
