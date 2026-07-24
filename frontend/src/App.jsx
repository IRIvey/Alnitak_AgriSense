import { useState } from "react";
import ChatPanel from "./components/ChatPanel.jsx";
import TracePanel from "./components/TracePanel.jsx";
import PlanView from "./components/PlanView.jsx";
import FinanceTable from "./components/FinanceTable.jsx";
import { sendChat } from "./lib/api.js";

// Two-column demo layout: conversation + plan on the left, agent TRACE on the
// right. The trace panel is a scored deliverable — keep it prominent.
export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [trace, setTrace] = useState([]);
  const [plan, setPlan] = useState(null);
  const [financials, setFinancials] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSend(text) {
    setMessages((m) => [...m, { role: "user", content: text }]);
    setBusy(true);
    try {
      const res = await sendChat(sessionId, text);
      setSessionId(res.session_id);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      if (res.trace?.length) setTrace(res.trace);
      if (res.season_plan) setPlan(res.season_plan);
      if (res.financials) setFinancials(res.financials);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `⚠️ ${e.message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>🌾 AgriSense AI</h1>
        <span className="team">Team Alnitak · Bdapps Agentic AI Hackathon</span>
      </header>

      <main className="grid">
        <section className="left">
          <ChatPanel messages={messages} busy={busy} onSend={handleSend} />
          {plan && <PlanView plan={plan} />}
          {financials && <FinanceTable financials={financials} />}
        </section>

        <aside className="right">
          <TracePanel trace={trace} />
        </aside>
      </main>
    </div>
  );
}
