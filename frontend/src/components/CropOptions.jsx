// Ranked crop options (Tier-0 #3): suitability, water need, risk, rough profit
// and the `because` reasoning — plus the KB citations that ground the ranking.
const RISK_COLOR = { low: "#4caf50", medium: "#e0a458", high: "#e05858" };

export default function CropOptions({ data, busy, onPick }) {
  if (!data?.options?.length) return null;
  return (
    <div className="card crops">
      <h2>Crop options</h2>
      <div className="crop-list">
        {data.options.map((o, i) => (
          <div key={o.crop} className={`crop-opt ${i === 0 ? "best" : ""}`}>
            <div className="crop-head">
              <span className="crop-rank">#{i + 1}</span>
              <span className="crop-name">{o.crop}</span>
              <span className="crop-suit">suitability {Math.round(o.suitability * 100)}%</span>
              {!o.in_season && <span className="crop-off">off-season</span>}
            </div>
            <div className="crop-meta">
              <span>💧 {o.water_need}</span>
              <span style={{ color: RISK_COLOR[o.risk] || "inherit" }}>
                ⚠ risk: {o.risk}
              </span>
              <span>📅 {o.sowing_window}</span>
              <span>
                ≈ {o.rough_profit_bdt_per_acre?.toLocaleString()} BDT/acre profit
              </span>
            </div>
            <p className="crop-because">{o.because}</p>
            {onPick && (
              <button
                className="crop-pick"
                disabled={busy}
                onClick={() => onPick(o.crop)}
              >
                {busy ? "Working…" : "Plan this crop"}
              </button>
            )}
          </div>
        ))}
      </div>
      {data.weather_note && <p className="warning">ℹ {data.weather_note}</p>}
      {data.kb_references?.length > 0 && (
        <p className="kb-refs">
          KB sources:{" "}
          {[...new Set(data.kb_references.map((r) => r.source))].join(", ")}
        </p>
      )}
      {data.note && <p className="assumptions">{data.note}</p>}
    </div>
  );
}
