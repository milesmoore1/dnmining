import { useEffect, useMemo, useState, type CSSProperties } from "react";
import AtlasMap from "./AtlasMap";
import { hasNearbyMine, makeMineIndex, mineType, nearbyMines } from "./mines";
import type { AtlasData, Mine, MineData, MineStatus, Prediction, Sample, Split, ViewBy } from "./types";

const SCORE_LABEL: Record<Prediction, string> = { high: "Higher prospectivity", low: "Lower prospectivity" };
const REE_ORDER = ["La", "Ce", "Nd", "Pr", "Sm", "Gd", "Tb", "Dy", "Ho", "Y"];

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function number(value: number | null | undefined, digits = 1) {
  return value == null ? "—" : new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);
}

function scoreColor(prediction: Prediction) {
  return prediction === "high" ? "var(--green)" : "var(--red)";
}

function Meter({ score, prediction }: { score: number; prediction: Prediction }) {
  return (
    <div className="probability" style={{ "--score": `${score * 100}%`, "--score-color": scoreColor(prediction) } as CSSProperties}>
      <strong>{pct(score)}</strong>
      <span>P(high)</span>
      <div className="probability__scale"><i /></div>
      <small>lower <b>←</b> model class <b>→</b> higher</small>
    </div>
  );
}

function FilterButton<T extends string>({ label, value, current, onChange }: { label: string; value: T; current: T; onChange: (value: T) => void }) {
  return <button className={current === value ? "segmented__button is-active" : "segmented__button"} onClick={() => onChange(value)}>{label}</button>;
}

function ChemStrip({ sample }: { sample: Sample }) {
  const concentrations = REE_ORDER.map((element) => ({ element, value: sample.dl2[element] ?? null }));
  const max = Math.max(1, ...concentrations.map(({ value }) => value ?? 0));
  const total = concentrations.reduce((sum, { value }) => sum + (value ?? 0), 0);
  return (
    <section className="detail-card chemistry">
      <h3>Rare-earth measurements</h3>
      <div className="chemistry__total"><span>Total measured REE</span><strong>{number(total, 1)} <small>ppm</small></strong></div>
      <div className="chemistry__bars">
        {concentrations.map(({ element, value }) => (
          <div className="chemistry__row" key={element}>
            <span>{element}</span>
            <div className="chemistry__track"><i style={{ width: `${((value ?? 0) / max) * 100}%` }} /></div>
            <b>{number(value, 2)} <small>ppm</small></b>
          </div>
        ))}
      </div>
    </section>
  );
}

function MineContext({ sample, mineIndex }: { sample: Sample; mineIndex: Map<string, Mine[]> }) {
  const nearby = useMemo(() => nearbyMines(sample, mineIndex).slice(0, 3), [sample, mineIndex]);
  return (
    <section className="detail-card mine-context">
      <h3>At-site MSHA mine record</h3>
      {nearby.length === 0 ? <p className="mine-empty">No MSHA coal-mine point is within 1 km of this sample.</p> : <div className="mine-list">
        {nearby.map((mine) => <article className="mine-row" key={mine.id}>
          <div className="mine-row__distance">{number(mine.distanceKm, 1)}<small>km</small></div>
          <div><h4>{mine.n ?? "Unnamed MSHA record"}</h4><p>MSHA {mine.id} · {mine.st ?? "Status not reported"} · {mineType(mine.ty)}</p>{mine.o && <p className="mine-row__operator">{mine.o}</p>}</div>
        </article>)}
      </div>}
    </section>
  );
}

function DetailPanel({ sample, mineIndex, onClose }: { sample: Sample; mineIndex: Map<string, Mine[]>; onClose: () => void }) {
  const actualTier = sample.tier ? `${sample.tier === "high" ? "Higher" : "Lower"} measured value tier` : "No measured tier";
  const role = sample.split === "test" ? "Held-out test sample" : "Training sample";
  return (
    <aside className="detail" aria-label={`Assessment details for ${sample.id}`}>
      <div className="detail__topline">
        <div>
          <h2>{sample.id}</h2>
          <p>{[sample.county, sample.state].filter(Boolean).join(", ") || "Location unavailable"} · {sample.basin ?? "Basin not assigned"}</p>
        </div>
        <button className="icon-button" onClick={onClose} aria-label="Close sample details">×</button>
      </div>

      <section className="assessment">
        <Meter score={sample.p_high} prediction={sample.pred} />
        <div>
          <span className={`status status--${sample.pred}`}>{SCORE_LABEL[sample.pred]}</span>
          <h3>{pct(sample.p_high)} predicted probability of the higher-value class</h3>
        </div>
      </section>

      <section className="detail-card evidence">
        <h3>Model record</h3>
        <div className="evidence__grid">
          <div><span>Predicted class</span><strong>{SCORE_LABEL[sample.pred]}</strong></div>
          <div><span>Observed target</span><strong>{actualTier}</strong></div>
          <div><span>Evaluation cohort</span><strong>{role}</strong></div>
          <div><span>Whole-coal value</span><strong>{sample.value == null ? "Not reported" : `$${number(sample.value, 2)}/t`}</strong></div>
        </div>
      </section>

      <section className="detail-card site-profile">
        <h3>Sample profile</h3>
        <div className="site-context__grid">
          <div><span>Coal basin</span><strong>{sample.basin ?? "Not reported"}</strong></div>
          <div><span>Coal rank</span><strong>{sample.rank ?? "Not reported"}</strong></div>
          <div><span>Bed / formation</span><strong>{sample.bed ?? "Not reported"}</strong></div>
          <div><span>Ash content</span><strong>{sample.ash == null ? "Not reported" : `${number(sample.ash)}%`}</strong></div>
        </div>
      </section>

      <ChemStrip sample={sample} />

      <MineContext sample={sample} mineIndex={mineIndex} />
    </aside>
  );
}

export default function App() {
  const [data, setData] = useState<AtlasData | null>(null);
  const [mines, setMines] = useState<Mine[]>([]);
  const [selected, setSelected] = useState<Sample | null>(null);
  const [viewBy, setViewBy] = useState<ViewBy>("prospectivity");
  const [split, setSplit] = useState<"all" | Split>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/miles_data.json").then((response) => {
        if (!response.ok) throw new Error("The baseline sample export could not be loaded.");
        return response.json() as Promise<AtlasData>;
      }),
      fetch("/mines.json").then((response) => response.ok ? response.json() as Promise<MineData> : null),
    ]).then(([atlas, mineData]) => {
      setData(atlas);
      setMines(mineData?.mines ?? []);
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load Atlas data."));
  }, []);

  const samplesById = useMemo(() => new Map(data?.samples.map((sample) => [sample.id, sample]) ?? []), [data]);
  const mineIndex = useMemo(() => makeMineIndex(mines), [mines]);
  const mineStatusById = useMemo(() => new Map<string, MineStatus>((data?.samples ?? []).map((sample) => {
    const status: MineStatus = hasNearbyMine(sample, mineIndex, "current") ? "current" : hasNearbyMine(sample, mineIndex, "abandoned") ? "abandoned" : "none";
    return [sample.id, status];
  })), [data, mineIndex]);
  const filtered = useMemo(
    () => (data?.samples ?? []).filter((sample) =>
      (split === "all" || sample.split === split) &&
      (viewBy !== "mine" || (mineStatusById.get(sample.id) ?? "none") !== "none"),
    ),
    [data, split, viewBy, mineStatusById],
  );

  if (error) return <main className="loading"><div><span className="eyebrow">Atlas unavailable</span><h1>Data could not load</h1><p>{error}</p></div></main>;
  if (!data) return <main className="loading"><div className="loading__mark" /><p>Loading the REE prospectivity Atlas…</p></main>;

  return (
    <main className="app-shell">
      <AtlasMap samples={filtered} allSamplesById={samplesById} selected={selected} viewBy={viewBy} mineStatusById={mineStatusById} onSelect={setSelected} />
      <header className="masthead panel">
        <div>
          <h1>REE Prospectivity</h1>
        </div>
      </header>

      <section className="model-card panel" aria-label="Model summary">
        <div className="model-card__top"><span>Baseline model</span><span className="model-badge">XGBoost</span></div>
        <div className="model-card__metrics">
          <div><strong>{number(data.meta.steps.labeled_rows, 0)}</strong><span>labeled samples</span></div>
          <div><strong>{pct(data.meta.metrics.accuracy)}</strong><span>test accuracy</span></div>
          <div><strong>{data.meta.metrics.auc.toFixed(3)}</strong><span>ROC AUC</span></div>
        </div>
        <p>Training: <b>{number(data.meta.steps.train_rows, 0)}</b> · Held-out test: <b>{number(data.meta.steps.test_rows, 0)}</b></p>
      </section>

      <section className="filters panel" aria-label="Map filters">
        <div className="filter-heading"><span className="eyebrow">Map view</span><strong>{number(filtered.length, 0)} sites</strong></div>
        <div className="filter-block"><label>View by</label><div className="segmented"><FilterButton label="Prospectivity" value="prospectivity" current={viewBy} onChange={setViewBy} /><FilterButton label="Coal mines" value="mine" current={viewBy} onChange={setViewBy} /></div></div>
        <div className="filter-block"><label>Evaluation cohort</label><div className="segmented"><FilterButton label="All" value="all" current={split} onChange={setSplit} /><FilterButton label="Training" value="train" current={split} onChange={setSplit} /><FilterButton label="Test" value="test" current={split} onChange={setSplit} /></div></div>
      </section>

      <Legend viewBy={viewBy} />

      {selected && <DetailPanel sample={selected} mineIndex={mineIndex} onClose={() => setSelected(null)} />}
    </main>
  );
}

function Legend({ viewBy }: { viewBy: ViewBy }) {
  const items = viewBy === "prospectivity"
    ? [["high", "Higher prospectivity"], ["low", "Lower prospectivity"]]
    : [["mine-current", "Current coal mine at site"], ["mine-abandoned", "Abandoned coal mine at site"]];
  return <section className="legend panel" aria-label="Map legend">{items.map(([kind, label]) => <div key={kind}><i className={`legend-dot legend-dot--${kind}`} /> {label}</div>)}</section>;
}
