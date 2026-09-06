import { useEffect, useMemo, useState, type CSSProperties } from "react";
import AtlasMap from "./AtlasMap";
import { hasNearbyMine, makeMineIndex, mineType, nearbyMines, type MineContextFilter } from "./mines";
import type { AtlasData, GeoCollection, Mine, MineData, Prediction, Sample, Split } from "./types";

const SCORE_LABEL: Record<Prediction, string> = { high: "Higher prospectivity", low: "Lower prospectivity" };
const REE_ORDER = ["Nd", "Pr", "Tb", "Dy", "Y"];

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
  return (
    <section className="detail-card chemistry">
      <div className="eyebrow">Assay signal</div>
      <h3>Rare-earth measurements</h3>
      <p>DL/2-treated values used in the baseline export; shown as concentration, not a claim of recoverable output.</p>
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

function MineContext({ sample, mineIndex, mineCount }: { sample: Sample; mineIndex: Map<string, Mine[]>; mineCount: number }) {
  const nearby = useMemo(() => nearbyMines(sample, mineIndex).slice(0, 3), [sample, mineIndex]);
  return (
    <section className="detail-card mine-context">
      <div className="eyebrow">MSHA mine context</div>
      <h3>Nearby named coal-mine records</h3>
      <p>Nearest MSHA coal-mine records within 25 km ({number(mineCount, 0)} records). These are reported mine locations, not mine boundaries.</p>
      {nearby.length === 0 ? <p className="mine-empty">No MSHA coal-mine record was found within 25 km.</p> : <div className="mine-list">
        {nearby.map((mine) => <article className="mine-row" key={mine.id}>
          <div className="mine-row__distance">{number(mine.distanceKm, 1)}<small>km</small></div>
          <div><h4>{mine.n ?? "Unnamed MSHA record"}</h4><p>MSHA {mine.id} · {mine.st ?? "Status not reported"} · {mineType(mine.ty)}</p>{mine.o && <p className="mine-row__operator">{mine.o}</p>}</div>
        </article>)}
      </div>}
    </section>
  );
}

function DetailPanel({ sample, meta, coalFields, mineIndex, mineCount, onClose }: { sample: Sample; meta: AtlasData["meta"]; coalFields: GeoCollection | null; mineIndex: Map<string, Mine[]>; mineCount: number; onClose: () => void }) {
  const actualTier = sample.tier ? `${sample.tier === "high" ? "Higher" : "Lower"} measured value tier` : "No measured tier";
  const role = sample.split === "test" ? "Held-out test sample" : "Training sample";
  const mapShapeNote = coalFields ? "A mapped coal-field outline is shown on the map when this coordinate falls inside one. It is field context, not a mine footprint." : "Coal-field outline unavailable.";
  return (
    <aside className="detail" aria-label={`Assessment details for ${sample.id}`}>
      <div className="detail__topline">
        <div>
          <span className="eyebrow">Selected analysis sample</span>
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
          <p>The classifier estimates whether this sample belongs to the model’s top-half REE-value target. It is not a mine viability or recovery decision.</p>
        </div>
      </section>

      <section className="detail-card evidence">
        <div className="eyebrow">ML evidence context</div>
        <div className="evidence__grid">
          <div><span>Role in model</span><strong>{role}</strong></div>
          <div><span>Observed target</span><strong>{actualTier}</strong></div>
          <div><span>Training set</span><strong>{number(meta.steps.train_rows, 0)} samples</strong></div>
          <div><span>Held-out test set</span><strong>{number(meta.steps.test_rows, 0)} samples</strong></div>
        </div>
        <p className="callout"><b>How to read this:</b> use the model-split filter to isolate training or held-out test samples; map symbols intentionally use the same styling for both. Reported test accuracy is {pct(meta.metrics.accuracy)} and ROC AUC is {meta.metrics.auc.toFixed(3)}. {meta.his_caveat}</p>
      </section>

      <ChemStrip sample={sample} />

      <MineContext sample={sample} mineIndex={mineIndex} mineCount={mineCount} />

      <section className="detail-card site-context">
        <div className="eyebrow">Location & source context</div>
        <div className="site-context__grid">
          <div><span>Coal rank</span><strong>{sample.rank ?? "Not reported"}</strong></div>
          <div><span>Bed / formation</span><strong>{sample.bed ?? "Not reported"}</strong></div>
          <div><span>Ash</span><strong>{number(sample.ash)}{sample.ash != null ? "%" : ""}</strong></div>
          <div><span>Reported thickness</span><strong>{number(sample.thick)}{sample.thick != null ? " in" : ""}</strong></div>
          <div><span>Baseline whole-coal value</span><strong>{sample.value == null ? "Not reported" : `$${number(sample.value, 2)}/t`}</strong></div>
          <div><span>Coordinates</span><strong>{sample.lat.toFixed(4)}, {sample.lon.toFixed(4)}</strong></div>
        </div>
        <p className="shape-note">{mapShapeNote}</p>
      </section>

      <section className="detail-card model-inputs">
        <div className="eyebrow">What the model was given</div>
        <p>The baseline model learns from trace-element assays, proximate and ultimate coal-quality measurements, geologic descriptors, seam thickness, and location. Individual feature weights are intentionally omitted here: they are global model behavior, not an explanation of this one sample.</p>
      </section>
    </aside>
  );
}

export default function App() {
  const [data, setData] = useState<AtlasData | null>(null);
  const [coalFields, setCoalFields] = useState<GeoCollection | null>(null);
  const [mines, setMines] = useState<Mine[]>([]);
  const [selected, setSelected] = useState<Sample | null>(null);
  const [prediction, setPrediction] = useState<"all" | Prediction>("all");
  const [split, setSplit] = useState<"all" | Split>("all");
  const [mineContext, setMineContext] = useState<MineContextFilter>("all");
  const [state, setState] = useState("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/miles_data.json").then((response) => {
        if (!response.ok) throw new Error("The baseline sample export could not be loaded.");
        return response.json() as Promise<AtlasData>;
      }),
      fetch("/coalfields2.geojson").then((response) => response.ok ? response.json() as Promise<GeoCollection> : null),
      fetch("/mines.json").then((response) => response.ok ? response.json() as Promise<MineData> : null),
    ]).then(([atlas, fields, mineData]) => {
      setData(atlas);
      setCoalFields(fields);
      setMines(mineData?.mines ?? []);
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load Atlas data."));
  }, []);

  const states = useMemo(() => Array.from(new Set(data?.samples.map((sample) => sample.state).filter((value): value is string => Boolean(value)) ?? [])).sort(), [data]);
  const samplesById = useMemo(() => new Map(data?.samples.map((sample) => [sample.id, sample]) ?? []), [data]);
  const mineIndex = useMemo(() => makeMineIndex(mines), [mines]);
  const filtered = useMemo(
    () => (data?.samples ?? []).filter((sample) =>
      (prediction === "all" || sample.pred === prediction) &&
      (split === "all" || sample.split === split) &&
      (state === "all" || sample.state === state) &&
      (mineContext === "all" || hasNearbyMine(sample, mineIndex, mineContext)),
    ),
    [data, prediction, split, state, mineContext, mineIndex],
  );

  if (error) return <main className="loading"><div><span className="eyebrow">Atlas unavailable</span><h1>Data could not load</h1><p>{error}</p></div></main>;
  if (!data) return <main className="loading"><div className="loading__mark" /><p>Loading the REE prospectivity Atlas…</p></main>;

  return (
    <main className="app-shell">
      <AtlasMap samples={filtered} allSamplesById={samplesById} coalFields={coalFields} selected={selected} onSelect={setSelected} />
      <header className="masthead panel">
        <div className="brand-mark" aria-hidden="true">A</div>
        <div>
          <div className="eyebrow">DN Mining · baseline model</div>
          <h1>REE Prospectivity Atlas</h1>
          <p>Interactive analysis samples, not mine inventory or resource estimates.</p>
        </div>
      </header>

      <section className="model-card panel" aria-label="Model summary">
        <div className="model-card__top"><span className="eyebrow">Model snapshot</span><span className="model-badge">XGBoost</span></div>
        <div className="model-card__metrics">
          <div><strong>{number(data.meta.steps.labeled_rows, 0)}</strong><span>labeled samples</span></div>
          <div><strong>{pct(data.meta.metrics.accuracy)}</strong><span>test accuracy</span></div>
          <div><strong>{data.meta.metrics.auc.toFixed(3)}</strong><span>ROC AUC</span></div>
        </div>
        <p>Training: <b>{number(data.meta.steps.train_rows, 0)}</b> · Held-out test: <b>{number(data.meta.steps.test_rows, 0)}</b>. Use the split filter to compare them.</p>
      </section>

      <section className="filters panel" aria-label="Map filters">
        <div className="filter-heading"><span className="eyebrow">Display</span><strong>{number(filtered.length, 0)} shown</strong></div>
        <div className="filter-block"><label>Predicted class</label><div className="segmented"><FilterButton label="All" value="all" current={prediction} onChange={setPrediction} /><FilterButton label="Higher" value="high" current={prediction} onChange={setPrediction} /><FilterButton label="Lower" value="low" current={prediction} onChange={setPrediction} /></div></div>
        <div className="filter-block"><label>Model split</label><div className="segmented"><FilterButton label="All" value="all" current={split} onChange={setSplit} /><FilterButton label="Training" value="train" current={split} onChange={setSplit} /><FilterButton label="Test" value="test" current={split} onChange={setSplit} /></div></div>
        <div className="filter-block"><label>Nearby MSHA mine (25 km)</label><div className="segmented"><FilterButton label="All" value="all" current={mineContext} onChange={setMineContext} /><FilterButton label="Current" value="current" current={mineContext} onChange={setMineContext} /><FilterButton label="Abandoned" value="abandoned" current={mineContext} onChange={setMineContext} /></div></div>
        <label className="select-label">State<select value={state} onChange={(event) => setState(event.target.value)}><option value="all">All states</option>{states.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      </section>

      <section className="legend panel" aria-label="Map legend">
        <div><i className="legend-dot legend-dot--high" /> Higher prospectivity</div>
        <div><i className="legend-dot legend-dot--low" /> Lower prospectivity</div>
        <div><i className="legend-dot legend-dot--site" /> Individual sites · no count clustering</div>
      </section>

      {selected && <DetailPanel sample={selected} meta={data.meta} coalFields={coalFields} mineIndex={mineIndex} mineCount={mines.length} onClose={() => setSelected(null)} />}
    </main>
  );
}
