import React, { useEffect, useRef, useState } from 'react';
import Icon from './Icon';
import { compact, human, requestId, displayName } from './client';
import Fields from './Fields.jsx';

export function Source({ id, target, call, auto, disabled = false }) {
  const [source, setSource] = useState(null), [error, setError] = useState('');
  const [expanded, setExpanded] = useState(false);
  useEffect(() => { let stale = false; setSource(null); setExpanded(false); setError('');
    if (auto) call('memory_evidence', { target_id: target, source_id: id, chars: 900 }).then(s => { if (!stale) setSource(s); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [id, target, auto]);
  const read = async (offset = 0) => {
    try { setSource(await call('memory_evidence', { target_id: target, source_id: id, chars: 4096, offset })); setExpanded(true); } catch (e) { setError(e.message); }
  };
  return <div className="source-row">{source?.withheld ? <p className="muted">{source.reason}</p> : <>
    {source?.title && <strong>{source.title}</strong>}
    {source?.excerpt && <blockquote>{source.excerpt}</blockquote>}
    {source?.date && <span className="muted">Captured source · {source.date}</span>}
    <button disabled={disabled} onClick={() => read()}>Read source</button>{expanded && source?.has_more && <button disabled={disabled} onClick={() => read(source.next_offset)}>Next excerpt</button>}
    {expanded && source?.offset > 0 && <button disabled={disabled} onClick={() => read(Math.max(0, source.offset - 4096))}>Previous excerpt</button>}
    <details><summary>Source reference</summary><p className="muted">{id}</p><p className="muted">{source?.meaning}</p></details>
    </>}{error && <p role="alert">{error}</p>}</div>;
}
export default function Inspector({ data, target, graph, call, available, onSelect, onSaved, schema, expanded, onExpand, pending, message, appError, initialTab }) {
  const [tab, setTab] = useState('Fields'), [form, setForm] = useState(null), [text, setText] = useState('');
  const [history, setHistory] = useState(null), [error, setError] = useState(''), [saving, setSaving] = useState(false);
  const [operation, setOperation] = useState('correct'), [newPredicate, setNewPredicate] = useState(''), [newValue, setNewValue] = useState('');
  const saveRequest = useRef(null);
  useEffect(() => { setForm(null); setText(''); setError(''); setHistory(null); setTab(initialTab || (graph?.entities.some(e => e.id === target) ? 'Fields' : 'Why?')); }, [target, initialTab]);
  const claim = data?.claims.assertions.find(a => a.id === target);
  const entities = graph?.entities || [];
  const label = id => { const entity = entities.find(e => e.id === id); return entity ? displayName(entity) : id; };
  const display = claim ? `${label(claim.subject)} → ${claim.object ? label(claim.object) : human(claim.predicate)}` : displayName(data?.entity);
  const contribution = claim?.provenance?.contribution;
  const refreshHistory = async () => {
    setTab('History');
    if (!available) return;
    try { setHistory(await call('memory_history', { entity_id: data.entity.id, limit: 40 })); } catch (e) { setError(e.message); }
  };
  const showForm = mode => {
    saveRequest.current = requestId();
    setForm(mode); setText(''); setError(''); setOperation('correct'); setNewPredicate(claim?.predicate || '');
    setNewValue(claim?.object || compact(claim?.value));
  };
  const save = async event => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      if (form === 'comment') await call('memory_comment', { target_id: target, text, request_id: saveRequest.current, reported: { application: 'RM graph review' } });
      else if (form === 'review') await call('memory_review', { target_id: target, disposition: operation, note: text,
        expected_reviews: claim.review?.review_ids || [], request_id: saveRequest.current, reported: { application: 'RM graph review' } });
      else {
        const args = { target_id: target, expected_heads: [target], operation, reason: text, request_id: saveRequest.current, reported: { application: 'RM graph review' } };
        if (operation !== 'retract') {
          if (claim.object) args.object = newValue;
          else args.value = typeof claim.value === 'string' ? newValue : JSON.parse(newValue);
        }
        if (operation === 'reclassify') args.predicate = newPredicate;
        await call('memory_correct', args);
      }
      setForm(null); setText(''); await onSaved(true);
      if (form === 'comment') setTab('Notes');
    } catch (e) { setError(e.message); } finally { setSaving(false); }
  };
  if (!data) return <aside className="inspector"><h2>Follow a connection.</h2><p>Select a node or a labeled line to inspect its evidence, notes and history.</p></aside>;
  return <aside className="inspector">
    <header><button className="text-action expand-record" disabled={pending} onClick={onExpand}>{expanded ? 'Return to graph' : 'Expand record'}</button><h2>{display}</h2><p className="muted">{claim?.review?.human_verified ? 'Owner reviewed · this revision only' : 'Source reported · current status unverified'}</p>{expanded && message && <p role="status">{message}</p>}{appError && <p role="alert" className="error">{appError}</p>}</header>
    <div className="tabs" role="tablist" aria-label="Record view">{['Fields', 'Why?', 'Notes', 'History'].map(t => <button key={t} role="tab" disabled={pending} aria-selected={tab === t} onClick={() => t === 'History' ? refreshHistory() : setTab(t)}>{t}</button>)}</div>
    <div className="inspector-body">
      {error && <p role="alert" className="error">{error}</p>}
      {tab === 'Fields' && <Fields key={data.entity.id + target} data={data} schema={schema} call={call} available={available} onSaved={onSaved} onSelect={onSelect}/>}
      {tab === 'Why?' && <>
        <h3>Evidence</h3>
        {claim ? <>
          <p className="statement">{claim.object ? human(claim.predicate) + ' · ' + label(claim.object) : compact(claim.value)}</p>
          {claim.valid_from && <p className="muted">Reported start: {claim.valid_from}</p>}
          <p className="muted">{claim.source_ids.length} source reference{claim.source_ids.length === 1 ? '' : 's'} · independence not established</p>
          {claim.source_ids.map((id, i) => <Source key={id} id={id} target={target} call={call} auto={i < 3} />)}
          <div className="attribution"><p>{contribution?.reported.application ? `Suggested through ${contribution.reported.application}` : `Recorded by ${claim.actor?.kind || 'an attributed contributor'}`}</p>
            <p className="muted">{contribution?.reported.model ? `${contribution.reported.model} · model reported by client` : 'Model not recorded'}</p>
            <details><summary>Attribution details</summary><dl><dt>Authenticated connection</dt><dd>{claim.actor?.id}</dd><dt>Operation</dt><dd>{claim.operation_id}</dd><dt>Local knowledge position</dt><dd>{claim.known_position}</dd><dt>Method</dt><dd>{contribution?.reported.method || claim.provenance?.method || 'Not recorded'}</dd></dl></details></div>
          {claim.conflicts?.length > 0 && <p className="warning">Competing corrections are retained. Review all branches before resolving.</p>}
        </> : <>
          <p>Choose a statement to see exactly what supports it.</p>
          <div className="claim-list">{data.claims.assertions.filter(a => !['has-type', 'rm:canonical-type', 'rm:comment', 'rm:task-state', 'rm:review'].includes(a.predicate)).map(a => <button key={a.id} onClick={() => onSelect(a.id)}><strong>{human(a.predicate)}</strong><span>{a.object ? label(a.object) : compact(a.excerpt ?? a.value).slice(0, 160)}</span></button>)}</div>
          {!data.claims.coverage.complete && <p className="muted">This is a bounded selection. Use the memory tools to retrieve additional records.</p>}
        </>}
      </>}
      {tab === 'Notes' && <>
        <h3>Comments</h3>{data.comments.length ? data.comments.map(n => <article className="note" key={n.id}><p>{n.value.text}</p><small>{n.actor.kind} connection · revision-specific note</small></article>) : <p className="muted">No comments on this selection yet.</p>}
        <h3>Linked briefs</h3>{data.artifacts.length ? data.artifacts.map(a => <article className="note" key={a.id}><h4>{a.value.title}</h4><p className={a.freshness.state === 'stale' ? 'warning' : 'muted'}>{a.freshness.state === 'stale' ? 'Stale: an input changed or is unavailable.' : 'Pinned inputs are current; factual validity is separate.'}</p><p>{a.value.text}</p><small>Generated by a connected client · {a.value.inputs.length} pinned inputs</small></article>) : <p className="muted">Connected assistants can save source-linked summaries here.</p>}
      </>}
      {tab === 'History' && <>
        <h3>Change history</h3><p className="muted">Changes are retained. Local admission does not prove another peer has received them.</p>
        {history?.operations.map(op => <article className="note" key={op.id}><strong>{op.actor.kind} connection</strong><small>{op.applied_at} · position {op.known_position}</small>{op.actions.filter(a => a.type === 'assertion').map(a => <p key={a.id}>{a.kind || 'assert'} · {human(a.predicate)}{a.reason ? ' · ' + a.reason : ''}</p>)}</article>)}
        {history && !history.coverage.complete && <p className="muted">Earlier/broader history is available through memory_history.</p>}
      </>}
      {form && <form className="edit-form" onSubmit={save}><h3>{form === 'comment' ? 'Add a comment' : form === 'review' ? 'Review this revision' : 'Correct this claim'}</h3>
        {form === 'correct' && <>
          <label>Change<select value={operation} onChange={e => setOperation(e.target.value)}><option value="correct">Correct the value or target</option><option value="retract">Withdraw this mistaken claim</option><option value="reclassify">Change the relationship meaning</option></select></label>
          {operation === 'reclassify' && <label>Relationship<select value={newPredicate} onChange={e => setNewPredicate(e.target.value)}>{Object.keys(schema?.predicates || {}).map(p => <option key={p} value={p}>{human(p)}</option>)}</select></label>}
          {operation !== 'retract' && (claim.object ? <label>Connected entity<select value={newValue} onChange={e => setNewValue(e.target.value)}>{entities.map(n => <option key={n.id} value={n.id}>{n.label}</option>)}</select></label> : <label>Corrected value<textarea value={newValue} onChange={e => setNewValue(e.target.value)} required /></label>)}
          <p className="muted">The earlier claim and evidence stay in history. Unsupported relationship types are rejected.</p>
        </>}
        {form === 'review' && <label>Decision<select value={operation} onChange={e => setOperation(e.target.value)}><option value="confirmed">Confirm this revision</option><option value="disputed">Dispute this revision</option><option value="needs-review">Needs more review</option></select></label>}
        <label>{form === 'comment' ? 'Comment' : 'Reason'}<textarea value={text} onChange={e => setText(e.target.value)} maxLength={8192} required /></label>
        <div className="actions"><button type="button" onClick={() => setForm(null)}>Cancel</button><button className="primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button></div>
      </form>}
    </div>
    <footer className="inspector-actions"><button disabled={pending || !available || !data.permissions.write} onClick={() => showForm('comment')}><Icon name="Comment"/>Add note</button>
      {claim && data.permissions.owner_review && <button disabled={pending || !available} onClick={() => { showForm('review'); setOperation('confirmed'); }}>Owner review</button>}</footer>
  </aside>;
}
