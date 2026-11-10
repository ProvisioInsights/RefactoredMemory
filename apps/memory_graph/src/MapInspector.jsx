import React, { useEffect, useRef, useState } from 'react';
import { Source } from './Inspector.jsx';
import { compact, displayName, human } from './format.js';
import { pathTo, topology } from './neighborhoodModel.js';
import { relationshipLabel } from './briefModel.js';
import { qualifiersOf } from './fieldModel.js';
import { checkedInspection, contractRows, profileSections, selectedHistory, validity } from './mapInspectorModel.js';

export default function MapInspector({ selection, graph, schema, call, available, pending, onSelect, onClose, onFocus, onEdit }) {
  const [data, setData] = useState(null), [error, setError] = useState(''), [loading, setLoading] = useState(false), [retry, setRetry] = useState(0);
  const [tab, setTab] = useState('Fields'), [showEmpty, setShowEmpty] = useState(false), [history, setHistory] = useState(null), [historyError, setHistoryError] = useState('');
  const [hidden, setHidden] = useState([]);
  const [related, setRelated] = useState({});
  const close = useRef(null);
  const id = selection.id, kind = selection.kind;
  useEffect(() => { close.current?.focus({ preventScroll: true }); }, [id, kind]);
  useEffect(() => {
    let stale = false;
    setData(null); setError(''); setTab('Fields'); setShowEmpty(false); setHidden([]); setHistory(null); setHistoryError('');
    if (!available) { setLoading(false); return; }
    setLoading(true);
    call('memory_inspect', { target_id: id }).then(d => { const checked = checkedInspection(d, { id, kind }); if (!stale) setData(checked); })
      .catch(e => { if (!stale) setError(e.message); }).finally(() => { if (!stale) setLoading(false); });
    return () => { stale = true; };
  }, [id, kind, available, call, retry]);
  useEffect(() => {
    if (tab !== 'History' || !data || !available) return;
    let stale = false; setHistory(null); setHistoryError('');
    call('memory_history', { entity_id: data.entity.id, limit: 40 }).then(h => { if (!stale) setHistory(h); }).catch(e => { if (!stale) setHistoryError(e.message); });
    return () => { stale = true; };
  }, [tab, data, available, call]);
  const entities = new Map(graph.entities.map(n => [n.id, n]));
  const entity = kind === 'node' ? data?.entity || entities.get(id) : null;
  const claim = kind === 'edge' ? data?.claims.assertions[0] : null;
  const supplied = kind === 'edge' ? graph.edges.find(e => e.id === id) : null;
  const edge = claim || (!available ? supplied : null);
  const claims = data?.claims.assertions || [];
  const rows = contractRows(data, schema?.field_catalog, showEmpty);
  const missingTargets = [...new Set(claims.map(c => c.object).filter(target => target && !entities.has(target)))].sort().slice(0, 16).join('\n');
  useEffect(() => {
    let stale = false; setRelated({});
    if (!available || !missingTargets) return;
    Promise.allSettled(missingTargets.split('\n').map(async target => {
      const result = await call('memory_entity', { entity_id: target });
      if (result.entity?.id !== target) throw new Error('Connected identity did not match.');
      return [target, result.entity];
    })).then(results => { if (!stale) setRelated(Object.fromEntries(results.filter(r => r.status === 'fulfilled').map(r => r.value))); });
    return () => { stale = true; };
  }, [missingTargets, available, call]);
  const legacyLinks = claims.filter(c => c.object && data?.field_view?.unmapped_claim_ids?.includes(c.id));
  const otherClaims = claims.filter(c => !c.object && data?.field_view?.unmapped_claim_ids?.includes(c.id));
  const sections = profileSections(rows, entity, { hidden, showIdentity: showEmpty });
  const fieldOptions = profileSections(rows, entity, { showIdentity: showEmpty }).flatMap(([, fields]) => fields);
  const contextPath = kind === 'node' ? pathTo(topology(graph, 2), id) : null;
  const sourceRefs = [...new Map(claims.flatMap(c => (c.source_ids || []).map(source => [source, { source, target: c.id }]))).values()];
  const label = target => displayName(entities.get(target) || related[target] || (data?.entity.id === target ? data.entity : null));
  const recordLink = target => <button className="inspector-record-link" disabled={pending || !available && !entities.has(target)} onClick={() => onSelect(target)}>{label(target)}</button>;
  const times = edge && validity(edge), q = edge && qualifiersOf(edge);
  const title = kind === 'node' ? displayName(entity) : 'Relationship';
  const operations = selectedHistory(history, selection);
  return <aside className="map-inspector" aria-label={`${title} information`} onKeyDown={e => { if (e.key === 'Escape' && !pending) { e.stopPropagation(); onClose(); } }}>
    <header className="map-inspector-header"><div><span className="inspector-kind">{kind === 'node' ? 'Record' : 'Connection'}</span><h2>{title}</h2>{kind === 'node' && <p>{entity?.classification?.canonical_types?.join(' · ') || entity?.entity_type || 'Type not recorded'}</p>}</div><button ref={close} className="close-map-inspector" aria-label="Close information panel" disabled={pending} onClick={onClose}>×</button></header>
    <div className="tabs" role="tablist" aria-label="Selected item information">{['Fields', 'Evidence', 'History'].map(t => <button key={t} role="tab" aria-selected={tab === t} disabled={pending || !available && t !== 'Fields' || loading || !!error} onClick={() => setTab(t)}>{t}</button>)}</div>
    <div className="map-inspector-body">
      {loading && <p role="status">Loading recorded details…</p>}
      {error && <p role="alert">{error} <button disabled={pending} onClick={() => setRetry(n => n + 1)}>Retry</button></p>}
      {!available && <p className="muted">Supplied snapshot only. Fields, evidence, history and editing require a live connection.</p>}
      {tab === 'Fields' && !loading && !error && <>
        {edge && <div className="inspector-relationship"><div><small>From</small>{recordLink(edge.subject)}</div><p>{relationshipLabel(edge)}</p><div><small>To</small>{recordLink(edge.object)}</div></div>}
        {data?.entity.classification?.ambiguous && <p className="warning">Type is disputed. Competing records remain separate.</p>}
        {rows ? <>
          {kind === 'node' && <details className="inspector-field-options"><summary>Show / hide fields</summary><label className="check"><input type="checkbox" checked={showEmpty} onChange={e => setShowEmpty(e.target.checked)}/>Include empty fields</label>{fieldOptions.map(f => <label className="check" key={f.id}><input type="checkbox" disabled={f.important} checked={!hidden.includes(f.id)} onChange={e => setHidden(h => e.target.checked ? h.filter(id => id !== f.id) : [...h, f.id])}/>{f.definition.label}</label>)}<p className="muted">View only; hiding a field does not remove it. Missing required fields, uncertainty and conflicts stay visible.</p></details>}
          {kind === 'node' && sections.map(([section, fields]) => <section className="inspector-profile-section" aria-label={section} key={section}><h3>{section}</h3><dl className="inspector-fields">{fields.map(row => <div key={row.id} className={row.id === 'identity.description' ? 'inspector-background' : row.paired ? 'inspector-paired' : ''}><dt>{row.definition.label}</dt><dd>{row.values.length ? row.values.map(({ claim: c, text }, i) => <div className="inspector-field-value" key={c?.id || i}>{c?.object ? recordLink(c.object) : <span>{text}</span>}{row.values.length > 1 && <small>Multiple recorded values · review separately</small>}{c?.conflicts?.length > 0 || c?.alternatives?.length > 0 ? <small className="warning">Competing corrections</small> : null}{row.definition.required_context?.includes('investment_status') && <small>{qualifiersOf(c).investment_status ? human(qualifiersOf(c).investment_status) : 'Status not recorded'} · {qualifiersOf(c).amount == null ? 'amount unknown' : compact(qualifiersOf(c).amount)}</small>}</div>) : <span className="muted">{row.empty === 'not_recorded' ? 'Not recorded' : 'Not in this selection'}</span>}</dd></div>)}</dl></section>)}
          {kind === 'node' && legacyLinks.length > 0 && <section className="inspector-profile-section" aria-label="Other recorded connections"><h3>Other connections</h3><dl className="inspector-fields">{legacyLinks.map(c => <div key={c.id}><dt>{human(c.predicate)}</dt><dd>{recordLink(c.object)}<small className="inspector-legacy-label">Legacy relationship</small></dd></div>)}</dl></section>}
          {kind === 'node' && contextPath?.edges.length > 0 && <section className="inspector-profile-section inspector-view-context" aria-label="Context in this view"><h3>In this view</h3><div className="inspector-context-path">{contextPath.nodes.map((target, i) => <React.Fragment key={target}>{i > 0 && <span>—</span>}{recordLink(target)}</React.Fragment>)}</div>{contextPath.edges.length === 1 && <p className="muted">{relationshipLabel(graph.edges.find(e => e.id === contextPath.edges[0]))} · recorded connection</p>}</section>}
          {kind === 'node' && otherClaims.length > 0 && <details><summary>Other recorded statements ({otherClaims.length})</summary>{otherClaims.map(c => <div className="inspector-legacy" key={c.id}><strong>{human(c.predicate)}</strong><p>{c.object ? recordLink(c.object) : compact(c.excerpt ?? c.value)}</p><small>No standard field mapping</small></div>)}</details>}
          {!data.field_view.coverage.complete && <p className="muted">{kind === 'edge' ? 'This assertion only; other record fields are outside this selection.' : 'Partial selection; missing fields may exist outside this view.'}</p>}
        </> : data && <p className="warning">Standard fields are unavailable for this catalog version. Recorded relationship details remain below.</p>}
        {!available && entity && <dl className="inspector-fields"><div><dt>Name in snapshot</dt><dd>{displayName(entity)}</dd></div><div><dt>Type in snapshot</dt><dd>{entity.entity_type || 'Not supplied'}</dd></div></dl>}
        {edge && <dl className="inspector-fields inspector-validity"><div><dt>Valid from</dt><dd>{times.from}</dd></div><div><dt>Precision</dt><dd>{times.precision}</dd></div><div><dt>Valid until</dt><dd>{times.until}</dd></div>{q.investment_status && <div><dt>Investment status</dt><dd>{q.investment_status}</dd></div>}{Object.hasOwn(q, 'amount') && <div><dt>Amount</dt><dd>{q.amount === null ? 'Explicitly unknown' : compact(q.amount)}</dd></div>}</dl>}
        {claim && rows && !rows.length && <p className="muted">Legacy relationship · no standard field mapping.</p>}
        {claim && <p className="muted">{claim.review?.human_verified ? 'Owner reviewed · this revision only' : 'Recorded claim · factual validity unverified'}</p>}
        <details className="inspector-contract"><summary>Contract reference</summary><dl><dt>{kind === 'edge' ? 'Assertion ID' : 'Entity ID'}</dt><dd>{id}</dd>{edge && <><dt>Recorded predicate</dt><dd>{edge.predicate}</dd></>}{rows && <><dt>Field contract</dt><dd>{data.field_view.schema} · revision {data.field_view.revision}</dd><dt>Qualification</dt><dd>{claims.filter(c => data.field_view.claims[c.id]?.qualification === 'legacy_unqualified').length} mapped legacy, unqualified claims. A declared contract is separate from factual verification.</dd><dt>Catalog digest</dt><dd>{data.field_view.digest_sha256}</dd></>}</dl></details>
      </>}
      {tab === 'Evidence' && data && <>
        <p className="muted">{sourceRefs.length} source reference{sourceRefs.length === 1 ? '' : 's'} in this selection. References do not establish independent corroboration.</p>
        {sourceRefs.slice(0, 12).map(({ source, target }, i) => <Source key={source} id={source} target={target} call={call} auto={i < 3} disabled={pending}/>)}
        {sourceRefs.length > 12 && <p className="muted">First 12 sources shown. Open the full record to inspect more.</p>}
        <details className="inspector-attribution"><summary>Who recorded this?</summary>{claims.slice(0, 12).map(c => <article key={c.id}><strong>{human(c.predicate)}</strong><dl><dt>Authenticated contributor</dt><dd>{c.actor?.kind || 'Not recorded'} · {c.actor?.id || 'Not recorded'}</dd><dt>Application (client reported)</dt><dd>{c.provenance?.contribution?.reported?.application || 'Not recorded'}</dd><dt>Model (client reported)</dt><dd>{c.provenance?.contribution?.reported?.model || 'Not recorded'}</dd><dt>Method (client reported)</dt><dd>{c.provenance?.contribution?.reported?.method || 'Not recorded'}</dd><dt>Operation</dt><dd>{c.operation_id}</dd></dl></article>)}{claims.length > 12 && <p>First 12 claims shown.</p>}</details>
      </>}
      {tab === 'History' && data && <>
        {historyError ? <p role="alert">{historyError}</p> : !history ? <p role="status">Loading history…</p> : <><p className="muted">{kind === 'edge' ? 'This assertion and its returned predecessors.' : 'Recorded field and relationship changes.'} Recording time is separate from validity.</p>{operations.map(op => <article className="inspector-history" key={op.id}><time>{op.applied_at}</time><small>{op.actor?.kind || 'Attributed'} contributor</small>{op.actions.map(a => <p key={a.id}><strong>{human(a.kind || 'assert')}</strong> · {human(a.predicate)}{a.reason && <span> — {a.reason}</span>}</p>)}</article>)}{!operations.length && <p>No matching changes in the returned history.</p>}{!history.coverage?.complete && <p className="muted">Bounded history; earlier changes may be outside this response.</p>}</>}
      </>}
    </div>
    {available && data && <footer className="map-inspector-actions">{kind === 'node' && <button disabled={pending || id === graph.start} onClick={() => onFocus(id)}>Explore from here</button>}<button disabled={pending || !(data.permissions.correct || data.permissions.write) || !rows || kind === 'edge' && !rows.length} onClick={() => onEdit(id)}>Edit fields</button></footer>}
  </aside>;
}
