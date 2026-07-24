// Renders the dated season plan (Tier-0 #4). Each stage shows its date, action,
// and the `because` reasoning that grounds it.
export default function PlanView({ plan }) {
  if (!plan) return null;
  return (
    <div className="card plan">
      <h2>Season plan · {plan.crop}</h2>
      {plan.sowing_window && (
        <p className="sub">
          Sowing window: {plan.sowing_window.start} → {plan.sowing_window.end}
        </p>
      )}
      <ul className="stages">
        {plan.stages?.map((st, i) => (
          <li key={i}>
            <span className="date">{st.date}</span>
            <span className="stage">{st.stage}</span>
            <span className="action">{st.action}</span>
            {st.because && <span className="because">— {st.because}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
