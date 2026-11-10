import React, { useContext, useEffect, useRef, useState } from 'react';
import { compact, requestId, displayName } from './client';
import { EDITOR_SCHEMA, tagOf, qualifiersOf, fieldValue, mappedValue, fieldUpdate, fieldAction, manualSource, createArguments } from './fieldModel.js';
import EditBoundary from './EditBoundary';

function EntityPicker({ value, onChange, range, call, disabled }) {
  const [query, setQuery] = useState(''), [items, setItems] = useState([]), [selected, setSelected] = useState(''), [error, setError] = useState('');
  useEffect(() => { let stale = false;
    if (value) call('memory_entity', { entity_id: value }).then(r => { if (!stale) setSelected(displayName(r.entity)); }).catch(e => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [value, call]);
  useEffect(() => { let stale = false;
    if (!query.trim()) { setItems([]); return; }
    const timer = setTimeout(() => call('memory_search_entities', { text: query, limit: 20 }).then(r => {
      if (!stale) setItems(r.entities.filter(e => e.classification?.canonical_types?.length === 1 && range.includes(e.classification.canonical_types[0])));
    }).catch(e => { if (!stale) setError(e.message); }), 200);
    return () => { stale = true; clearTimeout(timer); };
  }, [query, call, range]);
  return <div className="entity-picker"><label>Connected record<input placeholder="Search by name" value={query} disabled={disabled} onChange={e => setQuery(e.target.value)} /></label>
    {value && <p className="muted">Selected: {selected || 'Loading record…'}</p>}
    <div className="picker-results">{items.map(item => <button type="button" key={item.id} disabled={disabled} aria-pressed={value === item.id} onClick={() => { onChange(item.id); setSelected(displayName(item)); setQuery(''); }}>{displayName(item)}<small>{item.classification.canonical_types.join(', ')}</small></button>)}</div>
    {!value && <p className="muted">Choose an existing {range.join(' or ')}. Matching names do not establish identity.</p>}
    {error && <p role="alert">{error}</p>}</div>;
}

function ValueInput({ definition, catalog, value, onChange, precision, onPrecision, call, disabled }) {
  if (definition.value_type === 'entity_reference') return <EntityPicker value={value} onChange={onChange} range={definition.range} call={call} disabled={disabled}/>;
  if (definition.value_type === 'entity_type') return <label>{definition.label}<select required value={value} disabled={disabled} onChange={e => onChange(e.target.value)}><option value="">Choose a type</option>{catalog.record_types.map(t => <option key={t}>{t}</option>)}</select></label>;
  if (definition.value_type === 'calendar_date') return <><label>Reported date precision<select required value={precision} disabled={disabled} onChange={e => onPrecision(e.target.value)}><option value="">Choose precision</option>{['year', 'month', 'day'].map(p => <option key={p}>{p}</option>)}</select></label><label>{definition.label}<input required placeholder={precision === 'year' ? 'YYYY' : precision === 'month' ? 'YYYY-MM' : 'YYYY-MM-DD'} value={value} disabled={disabled} onChange={e => onChange(e.target.value)} /></label></>;
  if (definition.value_type === 'text_list') return <label>{definition.label}<textarea required placeholder="One alias per line" value={value} disabled={disabled} onChange={e => onChange(e.target.value)} /></label>;
  const type = definition.value_type === 'email' ? 'email' : definition.value_type === 'http_url' ? 'url' : definition.value_type === 'phone_text' ? 'tel' : 'text';
  return <label>{definition.label}<input type={type} required value={value} disabled={disabled} onChange={e => onChange(e.target.value)} /></label>;
}

function Submission({ frozen, error, saving, onRetry, onCancel }) {
  return <>{error && <div role="alert" className="error"><p>{error}</p>{frozen && <p>The save is not confirmed. Retry sends the identical request. Reload and inspect history before making a different change.</p>}</div>}
    <div className="actions"><button type="button" disabled={saving} onClick={onCancel}>{frozen ? 'Close and reload' : 'Cancel'}</button><button className="primary" disabled={saving} type={frozen ? 'button' : 'submit'} onClick={frozen ? onRetry : undefined}>{saving ? 'Saving…' : frozen ? 'Retry same save' : 'Save'}</button></div></>;
}

export function CreateRecord({ catalog, call, onSaved, onCancel }) {
  const [name, setName] = useState(''), [type, setType] = useState('person'), [note, setNote] = useState('');
  const [saving, setSaving] = useState(false), [error, setError] = useState(''), [frozen, setFrozen] = useState(false);
  const request = useRef(null), id = useRef(requestId());
  const { set: lock } = useContext(EditBoundary);
  const save = async event => {
    event?.preventDefault(); setSaving(true); setError('');
    try {
      request.current ||= createArguments(catalog, { id: id.current, type, name: name.trim(), note: note.trim() });
      setFrozen(true); lock(true); await call('memory_submit', request.current); lock(false);
      await onSaved(id.current);
    } catch (e) { setError(e.message); } finally { setSaving(false); }
  };
  return <form className="record-create field-card" onSubmit={save}><h2>Create a record</h2><p className="muted">A name and type are enough. Optional contact details can be added later.</p>
    <fieldset disabled={frozen || saving}><legend>Required identity fields</legend><ValueInput definition={catalog.fields['identity.type']} catalog={catalog} value={type} onChange={setType}/><ValueInput definition={catalog.fields['identity.name']} catalog={catalog} value={name} onChange={setName}/><label>Source or basis<textarea required maxLength={8192} value={note} onChange={e => setNote(e.target.value)} placeholder="How do you know this? This statement will be retained as evidence." /></label></fieldset>
    <p className="muted">Creates a separate identity. Similar names are not merged.</p><Submission frozen={frozen} error={error} saving={saving} onRetry={save} onCancel={() => { lock(false); onCancel(frozen ? id.current : null); }}/></form>;
}

function FieldForm({ field, catalog, claim, allClaims, subject, subjectTypes, call, onSaved, onCancel, remove, ending, reclassify }) {
  const [nextField, setNextField] = useState(field);
  const chosen = reclassify ? nextField : field;
  const definition = catalog.fields[chosen], tag = tagOf(claim), raw = fieldValue(catalog.fields[field], claim);
  const [value, setValue] = useState(Array.isArray(raw) ? raw.join('\n') : raw ?? '');
  const [state, setState] = useState(tag?.state || (claim && raw == null ? '' : 'known'));
  const [start, setStart] = useState(claim?.valid_from || ''), [timePrecision, setTimePrecision] = useState(claim?.time_precision || 'unknown');
  const [end, setEnd] = useState(tag?.validity_end || (claim ? ('valid_to' in claim ? (claim.valid_to === null ? 'unknown' : 'known') : '') : 'unknown'));
  const [until, setUntil] = useState(claim?.valid_to || ''), [precision, setPrecision] = useState(claim?.value?.precision || '');
  const [note, setNote] = useState(''), [resolve, setResolve] = useState(false);
  const q = qualifiersOf(claim);
  const [status, setStatus] = useState(q.investment_status || ''), [amountState, setAmountState] = useState(q.amount === null ? 'unknown' : q.amount ? 'known' : '');
  const [amount, setAmount] = useState(q.amount?.value ?? ''), [currency, setCurrency] = useState(q.amount?.currency || '');
  const [saving, setSaving] = useState(false), [error, setError] = useState(''), [frozen, setFrozen] = useState(false);
  const request = useRef(null), id = useRef(requestId());
  const { set: lock } = useContext(EditBoundary), formNode = useRef(null), originalSubject = useRef(subject);
  useEffect(() => { formNode.current?.querySelector('select, input, textarea')?.focus(); }, []);
  const typeHeads = allClaims.filter(c => c.predicate === definition.storage.predicate).map(c => c.id);
  const save = async event => {
    event?.preventDefault(); setError(''); setSaving(true);
    try {
      if (subject !== originalSubject.current) throw new Error('The selected record changed. Reload before editing.');
      if (!request.current) {
        if (!remove && state === 'known' && definition.value_type === 'entity_reference' && !value) throw new Error('Choose a connected record.');
        const context = definition.required_context?.includes('investment_status') ? { investment_status: status,
          amount: amountState === 'unknown' ? null : { value: Number(amount), currency } } : {};
        if (!remove && definition.required_context?.includes('amount') && (!amountState || amountState === 'known' && (amount === '' || !currency))) throw new Error('Choose a sourced amount or explicitly unknown amount.');
        const update = fieldUpdate(catalog, chosen, { state, start, timePrecision, end, until, context });
        const typed = state !== 'known' ? null : definition.value_type === 'text_list' ? value.split('\n').map(s => s.trim()).filter(Boolean) : value;
        const payload = mappedValue(definition, typed, claim, precision);
        if (claim) request.current = { name: 'memory_correct', args: { target_id: claim.id,
          expected_heads: resolve ? typeHeads : [claim.id], reason: note, request_id: id.current,
          operation: ending ? 'invalidate' : remove ? 'retract' : reclassify ? 'reclassify' : 'correct', reported: { application: 'RM field editor' },
          ...(ending ? { valid_to: until } : remove ? {} : { ...payload, field_update: update }),
          ...(reclassify ? { predicate: definition.storage.predicate } : {}) } };
        else {
          const source = id.current + '-source';
          request.current = { name: 'memory_submit', args: { catalog_digest: catalog.digest_sha256,
            request_id: id.current, reported: { application: 'RM field editor' }, actions: [manualSource(source, note),
              fieldAction(catalog, field, payload, update, { id: id.current + '-field', subject, source })] } };
        }
      }
      setFrozen(true);
      lock(true);
      await call(request.current.name, request.current.args);
      lock(false);
      await onSaved();
    } catch (e) { setError(e.message); } finally { setSaving(false); }
  };
  return <form className="edit-form" ref={formNode} onSubmit={save}><h3>{ending ? 'End' : remove ? 'Withdraw' : reclassify ? 'Change' : claim ? 'Edit' : 'Add'} {definition.label.toLowerCase()}</h3>
    {ending ? <p>Record the supported end of this relationship. Its original target, meaning, evidence and history stay intact.</p> : remove ? <p>The mistaken claim will leave the current view. Its original value, evidence and history remain. This does not erase a record or mean a relationship ended.</p> : claim && !tag && <p className="warning">Legacy claim: saving explicitly qualifies this correction under the field contract. The original remains unchanged in history.</p>}
    <fieldset disabled={saving || frozen}><legend>{remove ? 'Reason for withdrawal' : 'Field details'}</legend>
      {ending && <label>Valid until<input required value={until} placeholder="Source-reported date/timestamp" onChange={e => setUntil(e.target.value)}/></label>}
      {!remove && <><label>Value state<select required value={state} onChange={e => setState(e.target.value)}><option value="">Choose a state</option>{definition.states.map(s => <option key={s} value={s}>{s === 'known' ? 'Known value' : s === 'unknown' ? 'Explicitly unknown' : 'Not applicable'}</option>)}</select></label>
        {reclassify && <label>Relationship meaning<select required value={nextField} onChange={e => setNextField(e.target.value)}>{Object.entries(catalog.fields).filter(([id, d]) => d.value_type === 'entity_reference' && subjectTypes.length === 1 && d.applies_to.includes(subjectTypes[0])).map(([id, d]) => <option key={id} value={id}>{d.label}</option>)}</select></label>}
        {state === 'known' && <ValueInput definition={definition} catalog={catalog} value={value} onChange={setValue} precision={precision} onPrecision={setPrecision} call={call} disabled={saving || frozen}/>}
        {definition.required_context?.includes('investment_status') && <><label>Source-reported investment status<select required value={status} onChange={e => setStatus(e.target.value)}><option value="">Choose a status</option>{catalog.investment_context.investment_status.map(s => <option key={s}>{s}</option>)}</select></label><label>Investment amount<select required value={amountState} onChange={e => setAmountState(e.target.value)}><option value="">Choose amount coverage</option><option value="unknown">Explicitly unknown</option><option value="known">Source-reported amount</option></select></label>{amountState === 'known' && <><label>Amount<input required type="number" min="0" step="any" value={amount} onChange={e => setAmount(e.target.value)}/></label><label>Currency<input required pattern="[A-Z]{3}" placeholder="Three-letter code from source" value={currency} onChange={e => setCurrency(e.target.value)}/></label></>}</>}
        <details className="field-time" open={Boolean(start) || Boolean(claim)}><summary>Dates and validity</summary><label>Valid from<input value={start} placeholder="Unknown, or source-reported date/timestamp" onChange={e => setStart(e.target.value)}/></label>{start && <label>Start precision<select value={timePrecision} onChange={e => setTimePrecision(e.target.value)}>{['unknown', 'day', 'approximate', 'exact'].map(p => <option key={p}>{p}</option>)}</select></label>}<label>End status<select required value={end} onChange={e => setEnd(e.target.value)}><option value="">Choose explicitly</option><option value="unknown">Unknown</option><option value="ongoing">Explicitly ongoing</option><option value="known">Known end</option></select></label>{end === 'known' && <label>Valid until<input required value={until} placeholder="Source-reported date/timestamp" onChange={e => setUntil(e.target.value)}/></label>}</details>
        {field === 'identity.type' && typeHeads.length > 1 && <label className="check"><input type="checkbox" checked={resolve} onChange={e => setResolve(e.target.checked)}/>Resolve all {typeHeads.length} displayed competing type heads to this type. Original claims remain in history.</label>}
      </>}
      <label>{claim ? 'Reason and supporting basis' : 'Source or basis'}<textarea required value={note} maxLength={8192} onChange={e => setNote(e.target.value)} /></label>
    </fieldset><p className="muted">Attributed changes retain earlier sources and history. Admission is not independent verification.</p>
    <Submission frozen={frozen} error={error} saving={saving} onRetry={save} onCancel={() => { lock(false); onCancel(); }}/></form>;
}

export default function Fields({ data, schema, call, available, onSaved, onSelect, compact: compactMode = false }) {
  const { active: pending } = useContext(EditBoundary);
  const [showEmpty, setShowEmpty] = useState(false), [form, setForm] = useState(null), [add, setAdd] = useState('');
  const [editing, setEditing] = useState(false);
  const [targets, setTargets] = useState({}), [panelError, setPanelError] = useState('');
  const catalog = schema?.field_catalog, projection = data?.field_view;
  const supported = catalog?.schema === 'refactoredmemory.fields:v1' && catalog.revision === 1 && schema?.field_editor?.schema === EDITOR_SCHEMA && projection?.digest_sha256 === catalog.digest_sha256;
  const allClaims = data?.claims.assertions || [];
  const targetIds = [...new Set(allClaims.map(c => c.object).filter(Boolean))].sort().join('\n');
  useEffect(() => { let stale = false;
    if (!available || !targetIds) { setTargets({}); return; }
    Promise.allSettled(targetIds.split('\n').map(async id => [id, displayName((await call('memory_entity', { entity_id: id })).entity)]))
      .then(results => { if (!stale) setTargets(Object.fromEntries(results.filter(r => r.status === 'fulfilled').map(r => r.value))); });
    return () => { stale = true; };
  }, [targetIds, call, available]);
  const entries = Object.entries(projection?.fields || {});
  const visible = entries.filter(([id, f]) => f.claim_ids.length || !projection.coverage.selection_only && (showEmpty || catalog?.fields[id]?.required_for_create));
  const emptyOptions = entries.filter(([id, f]) => (f.applicable || id === 'identity.type') && !catalog.fields[id]?.required_for_create);
  const canAdd = !pending && available && supported && data?.permissions.write;
  const cancel = async () => { setForm(null); try { await onSaved(false); } catch (e) { setPanelError(e.message); } };
  if (!projection || !catalog) return <p className="warning">This runtime does not publish field editing. Existing evidence and history remain readable.</p>;
  return <section className={'field-panel' + (compactMode ? ' compact-fields' : '') + (editing || form ? ' fields-editing' : '') + (data.entity.classification?.ambiguous ? ' type-ambiguous' : '')} aria-label="Standard fields">
    {panelError && <p role="alert" className="error">{panelError}</p>}
    <div className="field-panel-header"><h3>Standard fields</h3>{!projection.coverage.selection_only && <label className="check"><input type="checkbox" checked={showEmpty} onChange={e => setShowEmpty(e.target.checked)}/>Show empty optional fields</label>}</div>
    {compactMode && <button className="primary correct-details" disabled={pending || !available || !supported || !(data.permissions.correct || data.permissions.write)} onClick={() => setEditing(!editing)}>{editing ? 'Finish reviewing fields' : data.permissions.correct ? 'Correct details' : 'Add details'}</button>}
    {!supported && <p className="warning">Field editing is unavailable until this connection supports the same catalog and editor contract.</p>}
    {data.entity.classification?.ambiguous && <p className="warning">Record type is disputed. Resolve the Type field before adding type-specific values. Existing claims can still be withdrawn.</p>}
    {!projection.coverage.complete && <p className="muted">Partial selection: an undisplayed field is not proof of absence.</p>}
    {visible.map(([field, info]) => {
      const definition = catalog.fields[field];
      return <article className="field-card" data-field={field} key={field}><div className="field-card-heading"><strong>{definition.label}</strong>{definition.required_for_create && <small>Required on creation</small>}</div>
        {info.claim_ids.length ? info.claim_ids.map(id => {
          const claim = allClaims.find(c => c.id === id), mapping = projection.claims[id];
          const value = fieldValue(definition, claim), tag = tagOf(claim);
          const display = tag?.state === 'unknown' ? 'Explicitly unknown' : tag?.state === 'not_applicable' ? 'Not applicable' : definition.value_type === 'entity_reference' ? targets[claim.object] || 'Connected record · label not loaded' : mapping.editable_value_loaded ? compact(value) : claim.excerpt || 'Value not loaded';
          return <div className="field-value" key={id}>{claim.object && compactMode ? <button type="button" className="text-action connected-field-value" onClick={() => onSelect(claim.object)}>{display}</button> : <p>{display}</p>}{claim.object && !compactMode && <button type="button" className="text-action" onClick={() => onSelect(claim.object)}>Open connected record</button>}
            <p className="muted field-lineage">{mapping.qualification === 'explicit_v1' ? 'Declares field contract v1' : 'Legacy · unqualified'} · {claim.source_ids.length} source reference{claim.source_ids.length === 1 ? '' : 's'}</p>
            {claim.valid_from && <p className="muted field-validity">From {claim.valid_from} · {claim.time_precision || 'precision not recorded'}</p>}{claim.valid_to && <p className="muted field-validity">Until {claim.valid_to}</p>}{tag?.validity_end === 'ongoing' && <p className="muted field-validity">Explicitly ongoing</p>}
            {definition.required_context?.includes('investment_status') && <p className="muted">Source-reported status: {qualifiersOf(claim).investment_status || 'Not established'} · Amount: {qualifiersOf(claim).amount == null ? 'Unknown' : compact(qualifiersOf(claim).amount)}</p>}
            {claim.alternatives?.length > 0 || claim.conflicts?.length > 0 ? <p className="warning">Competing claims are retained. Inspect all alternatives before resolving.</p> : null}
            <div className="field-actions"><button type="button" disabled={pending} onClick={() => onSelect(id)}>Evidence & history</button><button type="button" disabled={pending || !available || !supported || !data.permissions.correct || !mapping.editable_value_loaded || !info.applicable && field !== 'identity.type'} onClick={() => setForm({ field, claim, remove: false })}>Edit</button><button type="button" disabled={pending || !available || !supported || !data.permissions.correct || !mapping.editable_value_loaded} onClick={() => setForm({ field, claim, remove: true })}>Withdraw</button>
              {claim.object && <><button type="button" disabled={pending || !available || !supported || !data.permissions.correct || !info.applicable} onClick={() => setForm({ field, claim, reclassify: true })}>Change relationship</button><button type="button" disabled={pending || !available || !supported || !data.permissions.correct} onClick={() => setForm({ field, claim, remove: true, ending: true })}>End relationship</button></>}
            </div>
          </div>;
        }) : <><p className="muted">{info.empty_state === 'not_recorded' ? 'Not recorded' : 'Not loaded in this selection'}</p><button type="button" disabled={!canAdd || !info.applicable && field !== 'identity.type'} onClick={() => setForm({ field })}>Add {definition.label.toLowerCase()}</button></>}
      </article>;
    })}
    {!projection.coverage.selection_only && <div className="add-field"><label>Add a field or relationship<select value={add} onChange={e => setAdd(e.target.value)}><option value="">Choose a field</option>{emptyOptions.map(([id]) => <option key={id} value={id}>{catalog.fields[id].label}</option>)}</select></label><button type="button" disabled={!canAdd || !add} onClick={() => setForm({ field: add })}>Add</button></div>}
    {form && <FieldForm key={data.entity.id + form.field + (form.claim?.id || 'new') + Boolean(form.remove) + Boolean(form.ending) + Boolean(form.reclassify)} {...form} catalog={catalog} allClaims={allClaims} subject={data.entity.id} subjectTypes={data.entity.classification.canonical_types} call={call} onSaved={async () => { setForm(null); await onSaved(true); }} onCancel={cancel}/>}
    {projection.unmapped_claim_ids.length > 0 && <details><summary>Other legacy records ({projection.unmapped_claim_ids.length})</summary><p className="muted">These claims have no unambiguous field mapping. Inspect evidence before proposing a correction.</p>{projection.unmapped_claim_ids.map(id => <button key={id} type="button" onClick={() => onSelect(id)}>{allClaims.find(c => c.id === id)?.predicate || 'Inspect record'}</button>)}</details>}
  </section>;
}
