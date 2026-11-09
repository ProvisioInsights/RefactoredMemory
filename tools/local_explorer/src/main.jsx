import React, { useEffect, useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const LABELS = {
  "rm:contact-point": "Contact detail",
  "rm:profile-property": "Profile statement",
  "rm:communication-record": "Mailbox observation",
  "rm:contact-record": "Contact observation",
  "rm:reported-date": "Reported date",
  "rm:relationship-date-note": "Relationship date note",
  "rm:conversation-reference": "Conversation reference",
  "rm:evidence-assessment": "Evidence assessment",
  "rm:enrichment-review": "Review item",
  "rm:review-flag": "Review item",
};
const human = (s) => LABELS[s] || s.replace(/^rm:/, "").replaceAll("-", " ");
async function api(path, query = {}) {
  const r = await fetch("/api/" + path + "?" + new URLSearchParams(query), {
    credentials: "same-origin",
  });
  const v = await r.json();
  if (!r.ok) throw new Error(v.error || "Could not read memory");
  return v;
}
function Value({ value }) {
  if (value === null || value === undefined) return <span>Unknown</span>;
  if (typeof value !== "object") return <span>{String(value)}</span>;
  return (
    <dl className="value">
      {Object.entries(value)
        .filter(
          ([k, v]) =>
            v !== null &&
            ![
              "source_ids",
              "source_identity",
              "comparison_key",
              "observed_forms",
              "source_entity_id",
              "source_family",
              "identity_basis",
              "contact_point_assertion_id",
            ].includes(k),
        )
        .map(([k, v]) => (
          <React.Fragment key={k}>
            <dt>{k.replaceAll("_", " ")}</dt>
            <dd>{typeof v === "object" ? JSON.stringify(v) : String(v)}</dd>
          </React.Fragment>
        ))}
    </dl>
  );
}
function Evidence({ evidence, onRead, onMore, onPrevious }) {
  return (
    <section>
      <h2>Evidence</h2>
      <p className="muted">{evidence?.independence}</p>
      {evidence && (
        <p className="muted">
          {evidence.document_versions} captured document versions · showing{" "}
          {evidence.offset + 1}–{evidence.offset + evidence.documents.length}
        </p>
      )}
      {evidence?.documents.length ? (
        evidence.documents.map((d) => (
          <article className="evidence-row" key={d.id}>
            <div>
              <h3>{d.title}</h3>
              <p className="muted">
                {d.namespace
                  .replace("owner-approved-", "")
                  .replaceAll("-", " ")}{" "}
                · {d.date || "Date not established"}
                {d.parts > 1 ? " · " + d.parts + " captured parts" : ""}
              </p>
              <p className="excerpt">{d.excerpt}</p>
            </div>
            <button onClick={() => onRead(d.id)}>Read source</button>
          </article>
        ))
      ) : (
        <p>
          No linked source document in this view. Legacy citations may still
          exist.
        </p>
      )}
      <div className="pagination">
        {onPrevious && evidence?.offset > 0 && (
          <button onClick={onPrevious}>Previous evidence</button>
        )}
        {onMore && evidence?.has_more && (
          <button onClick={onMore}>More evidence</button>
        )}
      </div>
    </section>
  );
}
function Timeline({ data, onSelect, onPage, onRead }) {
  return (
    <section>
      <h2>Timeline</h2>
      <p className="muted">
        {data?.meaning ||
          "Only explicit dates are shown; unknown times remain unknown."}
      </p>
      {data && (
        <div className="pagination">
          <button
            disabled={data.offset === 0}
            onClick={() => onPage(Math.max(0, data.offset - 100))}
          >
            Previous dates
          </button>
          <span>
            {data.offset + 1}–{data.offset + data.events.length} of{" "}
            {data.dated_rows} dated rows
          </span>
          <button
            disabled={!data.has_more}
            onClick={() => onPage(data.offset + 100)}
          >
            Next dates
          </button>
        </div>
      )}
      {data?.events.map((e) => (
        <article className="timeline-row" key={e.id}>
          <time>{e.date}</time>
          <div>
            {onSelect && (
              <button
                className="link-button"
                onClick={() => onSelect(e.entity_id)}
              >
                {e.label}
              </button>
            )}
            <h3>{e.title || human(e.predicate)}</h3>
            <p className="muted">
              {human(e.predicate)} ·{" "}
              {e.value.channel || e.value.property || "Source-reported date"}
            </p>
            {e.source_assertion_id && onRead && (
              <button onClick={() => onRead(e.source_assertion_id)}>
                Read source
              </button>
            )}
            <details>
              <summary>Record details</summary>
              <Value value={e.value} />
            </details>
          </div>
        </article>
      ))}
      {data && (
        <div className="pagination">
          <button
            disabled={data.offset === 0}
            onClick={() => onPage(Math.max(0, data.offset - 100))}
          >
            Previous dates
          </button>
          <span>
            {data.offset + 1}–{data.offset + data.events.length} of{" "}
            {data.dated_rows} dated rows
          </span>
          <button
            disabled={!data.has_more}
            onClick={() => onPage(data.offset + 100)}
          >
            Next dates
          </button>
        </div>
      )}
    </section>
  );
}
function SourceDialog({ source, error, onClose, onNext, onPart }) {
  const ref = useRef(null);
  useEffect(() => {
    const before = document.activeElement;
    ref.current?.querySelector("button")?.focus();
    return () => before?.focus();
  }, []);
  const trap = (e) => {
    if (e.key !== "Tab") return;
    const buttons = [...ref.current.querySelectorAll("button")].filter(
      (b) => !b.disabled,
    );
    const first = buttons[0],
      last = buttons.at(-1);
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last?.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first?.focus();
    }
  };
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <section
        ref={ref}
        onKeyDown={trap}
        className="source-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Captured source"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <h2>{source?.title || "Captured source"}</h2>
          <button onClick={onClose}>Close</button>
        </header>
        {error ? (
          <p role="alert">{error}</p>
        ) : source ? (
          <>
            <p className="muted">
              {source.family.replace("owner-approved-", "")} ·{" "}
              {source.date || "Date not established"} · part {source.part + 1}{" "}
              of {source.parts}
            </p>
            <p className="source-warning">{source.basis}</p>
            <pre>{source.text}</pre>
            <div className="pagination">
              {source.previous_part_id && (
                <button onClick={() => onPart(source.previous_part_id)}>
                  Previous part
                </button>
              )}
              {source.remaining > 0 && (
                <button onClick={onNext}>Read next excerpt</button>
              )}
              {source.next_part_id && (
                <button onClick={() => onPart(source.next_part_id)}>
                  Next part
                </button>
              )}
            </div>
          </>
        ) : (
          <p role="status">Reading captured source…</p>
        )}
      </section>
    </div>
  );
}
function Detail({ data, tab, setTab, onSelect, onRead }) {
  const [evidence, setEvidence] = useState(data.evidence);
  const [timeline, setTimeline] = useState(null);
  useEffect(() => {
    setEvidence(data.evidence);
  }, [data.entity.id]);
  useEffect(() => {
    if (tab === "Evidence")
      api("evidence", { id: data.entity.id }).then(setEvidence);
  }, [tab, data.entity.id]);
  useEffect(() => {
    setTimeline(null);
    if (tab === "Timeline")
      api("timeline", { id: data.entity.id }).then(setTimeline);
  }, [tab, data.entity.id]);
  const claims = data.assertions;
  const profile = claims.filter((a) =>
    ["rm:contact-point", "rm:profile-property"].includes(a.predicate),
  );
  const relations = claims.filter((a) => a.object);
  const assessment = claims.find(
    (a) => a.predicate === "rm:evidence-assessment",
  );
  const context = claims.filter((a) =>
    [
      "rm:prospect-record",
      "rm:conditional-interest",
      "rm:contact-classification",
      "rm:contact-record",
    ].includes(a.predicate),
  );
  return (
    <div className="detail">
      <header>
        <h2 className="identity-title">{data.entity.label}</h2>
        <p>{data.entity.type}</p>
      </header>
      <div className="tabs" role="tablist" aria-label="Identity view">
        {["Overview", "Timeline", "Evidence"].map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === "Overview" ? (
        <>
          <div className="profile-columns">
            <section>
              <h3>Source-reported profile</h3>
              {profile.length ? (
                profile.map((a) => (
                  <div className="profile-line" key={a.id}>
                    <span className="muted">
                      {a.predicate === "rm:contact-point"
                        ? a.value.kind
                        : a.value.property}
                    </span>
                    <strong>
                      {a.value.address || a.value.reported_value}
                      {a.value.country_code === "not established"
                        ? " (country code unverified)"
                        : ""}
                    </strong>
                  </div>
                ))
              ) : (
                <p className="muted">
                  No extracted contact or profile details yet.
                </p>
              )}
            </section>
            <section>
              <h3>What connects them</h3>
              {[...relations, ...data.incoming].slice(0, 18).map((a) => (
                <p className="relationship" key={a.id}>
                  <button
                    className="link-button"
                    onClick={() =>
                      onSelect(
                        a.subject === data.entity.id ? a.object : a.subject,
                      )
                    }
                  >
                    {a.subject === data.entity.id
                      ? human(a.predicate) + " · " + a.related_label
                      : a.related_label + " · " + human(a.predicate)}
                  </button>
                  <small>
                    {data.assessments[a.id]?.status ||
                      "Source reported; see supporting claim"}
                  </small>
                </p>
              ))}
              {!relations.length && !data.incoming.length && (
                <p className="muted">
                  No structured relationships in this view.
                </p>
              )}
            </section>
          </div>
          {context.length > 0 && (
            <section className="context">
              <h2>What the records say</h2>
              {context.map((a) => (
                <article key={a.id}>
                  <h3>{human(a.predicate)}</h3>
                  <Value value={a.value} />
                </article>
              ))}
            </section>
          )}
          <section className="assessment">
            <strong>Source reported. Current validity unverified.</strong>
            {assessment ? (
              <>
                <p>
                  {assessment.value.active_claims_assessed} existing structured
                  claims assessed in this review. Independent confirmation has
                  not been established.
                </p>
                <dl className="value">
                  {Object.entries(assessment.value.statuses).map(([k, v]) => (
                    <React.Fragment key={k}>
                      <dt>{k.replaceAll("-", " ")}</dt>
                      <dd>{v}</dd>
                    </React.Fragment>
                  ))}
                </dl>
              </>
            ) : (
              <p className="muted">
                Detailed assessment is being prepared. Multiple sources or
                versions alone do not establish independence.
              </p>
            )}
          </section>
          <Evidence
            evidence={tab === "Evidence" ? evidence : data.evidence}
            onRead={onRead}
            onMore={() =>
              tab === "Evidence"
                ? api("evidence", {
                    id: data.entity.id,
                    offset: String(evidence.offset + evidence.display_limit),
                  }).then(setEvidence)
                : setTab("Evidence")
            }
            onPrevious={() =>
              api("evidence", {
                id: data.entity.id,
                offset: String(
                  Math.max(0, evidence.offset - evidence.display_limit),
                ),
              }).then(setEvidence)
            }
          />
          {data.reviews.length > 0 && (
            <section>
              <h2>Review notes</h2>
              {data.reviews.map((r, i) => (
                <article key={i} className="review-row">
                  <h3>{r.reason.replaceAll("-", " ")}</h3>
                  <p>
                    {r.status}: {r.explanation}
                  </p>
                </article>
              ))}
            </section>
          )}
        </>
      ) : tab === "Timeline" ? (
        <Timeline
          onRead={onRead}
          data={timeline}
          onPage={(offset) =>
            api("timeline", { id: data.entity.id, offset }).then(setTimeline)
          }
        />
      ) : (
        <Evidence
          evidence={tab === "Evidence" ? evidence : data.evidence}
          onRead={onRead}
          onMore={() =>
            tab === "Evidence"
              ? api("evidence", {
                  id: data.entity.id,
                  offset: String(evidence.offset + evidence.display_limit),
                }).then(setEvidence)
              : setTab("Evidence")
          }
          onPrevious={() =>
            api("evidence", {
              id: data.entity.id,
              offset: String(
                Math.max(0, evidence.offset - evidence.display_limit),
              ),
            }).then(setEvidence)
          }
        />
      )}
    </div>
  );
}
function App() {
  const selectionRequest = useRef(0),
    sourceRequest = useRef(0);
  const [reviewPage, setReviewPage] = useState(null),
    [reviewOffset, setReviewOffset] = useState(0);
  const [mode, setMode] = useState("Explore"),
    [type, setType] = useState("all"),
    [query, setQuery] = useState(""),
    [result, setResult] = useState(null),
    [data, setData] = useState(null),
    [tab, setTab] = useState("Overview"),
    [error, setError] = useState(""),
    [timeline, setTimeline] = useState(null),
    [source, setSource] = useState(null),
    [sourceId, setSourceId] = useState(null),
    [sourceError, setSourceError] = useState("");
  useEffect(() => {
    let current = true;
    const t = setTimeout(
      () =>
        api("entities", {
          q: query,
          type,
          review: String(mode === "Needs review"),
        })
          .then((v) => {
            if (current) setResult(v);
          })
          .catch((e) => setError(e.message)),
      140,
    );
    return () => {
      current = false;
      clearTimeout(t);
    };
  }, [query, type, mode]);
  useEffect(() => {
    if (mode === "Needs review")
      api("review", { q: query, offset: String(reviewOffset) })
        .then(setReviewPage)
        .catch((e) => setError(e.message));
  }, [mode, query, reviewOffset]);
  useEffect(() => {
    if (mode === "Timeline")
      api("timeline", { q: query })
        .then(setTimeline)
        .catch((e) => setError(e.message));
  }, [mode, query]);
  useEffect(() => {
    const listener = (e) => {
      if (e.key === "Escape") {
        setSourceId(null);
        setSource(null);
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);
  const select = (id) => {
    const request = ++selectionRequest.current;
    setError("");
    setTab("Overview");
    setMode((m) => (m === "Timeline" ? "Explore" : m));
    api("entity", { id })
      .then((v) => {
        if (request === selectionRequest.current) setData(v);
      })
      .catch((e) => setError(e.message));
  };
  const openSource = async (id, offset = 0) => {
    const request = ++sourceRequest.current;
    setSourceId(id);
    setSource(null);
    setSourceError("");
    try {
      const value = await api("source", { id, offset });
      if (request === sourceRequest.current) setSource(value);
    } catch (e) {
      setSourceError(e.message);
    }
  };
  const navigate = (m) => {
    setMode(m);
    setType(m === "People" ? "person" : m === "Projects" ? "project" : "all");
    setQuery("");
    setReviewOffset(0);
  };
  return (
    <div className="app">
      <aside>
        <div className="brand">RefactoredMemory</div>
        <nav aria-label="Main navigation">
          {["Explore", "People", "Projects", "Timeline", "Needs review"].map(
            (m) => (
              <button
                key={m}
                aria-current={mode === m ? "page" : undefined}
                onClick={() => navigate(m)}
              >
                {m}
              </button>
            ),
          )}
        </nav>
        <p className="private-note">Private on this Mac</p>
      </aside>
      <main>
        <h1>
          {mode === "Timeline"
            ? "Your captured timeline"
            : mode === "Needs review"
              ? "What needs a closer look"
              : "Explore your memory"}
        </h1>
        <label className="search">
          <span className="sr-only">Search people, projects and topics</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search people, projects and topics"
          />
        </label>
        {mode !== "Timeline" && mode !== "Needs review" && (
          <div className="filters" aria-label="Identity type">
            {[
              ["all", "All"],
              ["person", "People"],
              ["organization", "Organizations"],
              ["project", "Projects"],
            ].map(([t, label]) => (
              <button
                aria-pressed={type === t}
                key={t}
                onClick={() => setType(t)}
              >
                {label}
              </button>
            ))}
          </div>
        )}
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {mode === "Timeline" ? (
          <Timeline
            onRead={(id) => openSource(id)}
            data={timeline}
            onSelect={select}
            onPage={(offset) =>
              api("timeline", { q: query, offset }).then(setTimeline)
            }
          />
        ) : mode === "Needs review" ? (
          <section className="review-queue">
            <h2>{reviewPage?.matched || 0} items need review</h2>
            <p className="muted">
              Ambiguous cases remain separate. This view makes no data changes.
            </p>
            {reviewPage?.items.map((r) => (
              <article className="review-row" key={r.item}>
                <h3>{r.label}</h3>
                <p>{r.reason.replaceAll("-", " ")}</p>
                <p className="muted">{r.explanation}</p>
                {r.source_readable && (
                  <button onClick={() => openSource(r.source_assertion_id)}>
                    Read source
                  </button>
                )}
                {r.entity_id && (
                  <button
                    onClick={() => {
                      navigate("Explore");
                      select(r.entity_id);
                    }}
                  >
                    Open identity
                  </button>
                )}
              </article>
            ))}
            <div className="pagination">
              <button
                disabled={reviewOffset === 0}
                onClick={() => setReviewOffset(Math.max(0, reviewOffset - 40))}
              >
                Previous
              </button>
              <span>
                Items {reviewOffset + 1}–
                {Math.min(reviewOffset + 40, reviewPage?.matched || 0)}
              </span>
              <button
                disabled={!reviewPage?.has_more}
                onClick={() => setReviewOffset(reviewOffset + 40)}
              >
                Next
              </button>
            </div>
          </section>
        ) : (
          <div className="workspace">
            <section className="identity-list" aria-label="Identity results">
              <p className="result-count">
                {result?.matched.toLocaleString() || "…"} identities
                {result?.truncated ? " · first 100" : ""}
              </p>
              {result?.entities.map((e) => (
                <button
                  className={
                    "identity-row " +
                    (data?.entity.id === e.id ? "selected" : "")
                  }
                  key={e.id}
                  onClick={() => select(e.id)}
                >
                  <span>
                    <strong>{e.label}</strong>
                    <small>{e.type}</small>
                  </span>
                  <small>{e.source_count} linked parts</small>
                </button>
              ))}
              {result?.entities.length === 0 && (
                <p>No matches. Try another name or type.</p>
              )}
            </section>
            {data ? (
              <Detail
                data={data}
                tab={tab}
                setTab={setTab}
                onSelect={select}
                onRead={openSource}
              />
            ) : (
              <div className="empty-detail">
                <h2>Follow a person, project or idea.</h2>
                <p>
                  Select a name to see their profile, relationships, dated
                  observations and captured evidence.
                </p>
                <p className="muted">
                  Search Forgence to explore the investor work, or select Needs
                  review to inspect gaps.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
      {sourceId && (
        <SourceDialog
          source={source}
          error={sourceError}
          onClose={() => {
            setSourceId(null);
            setSource(null);
          }}
          onNext={() => openSource(sourceId, source.offset + 16000)}
          onPart={(id) => openSource(id)}
        />
      )}
    </div>
  );
}
createRoot(document.getElementById("root")).render(
  <PrivateAccess>
    <App />
  </PrivateAccess>,
);

function PrivateAccess({ children }) {
  const [ready, setReady] = useState(false),
    [key, setKey] = useState(""),
    [error, setError] = useState("");
  async function unlock(value) {
    const response = await fetch("/api/session", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: value }),
    });
    if (response.ok) {
      setKey("");
      setReady(true);
    } else
      setError(
        "The private access key was not accepted. Use your Open RefactoredMemory launcher.",
      );
  }
  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const capability = params.get("access");
    if (capability) {
      history.replaceState(null, "", window.location.pathname);
      unlock(capability).catch(() =>
        setError("Could not unlock this private view."),
      );
    } else
      api("state")
        .then(() => setReady(true))
        .catch(() => {});
  }, []);
  if (ready) return children;
  return (
    <main className="unlock">
      <h1>Open your private memory</h1>
      <p>
        This view is only available on this Mac. Use the private launcher or
        enter its access key.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          unlock(key).catch(() =>
            setError("Could not unlock this private view."),
          );
        }}
      >
        <label>
          Private access key
          <input
            type="password"
            autoComplete="off"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />
        </label>
        <button type="submit">Open memory</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
