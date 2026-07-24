// Thin client for the AgriSense backend.
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function sendChat(sessionId, message) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) throw new Error(`chat failed: ${res.status}`);
  return res.json(); // -> ChatResponse
}

export async function getTrace(sessionId) {
  const res = await fetch(`${BASE}/api/trace/${sessionId}`);
  if (!res.ok) throw new Error(`trace failed: ${res.status}`);
  return res.json();
}

// Live trace via Server-Sent Events. Returns the EventSource so callers can close it.
export function streamTrace(sessionId, onStep) {
  const es = new EventSource(`${BASE}/api/trace/${sessionId}/stream`);
  es.onmessage = (e) => {
    try {
      onStep(JSON.parse(e.data));
    } catch {
      /* ignore keep-alives */
    }
  };
  return es;
}

export async function checkout(sessionId, subscriberId, amountBdt, items) {
  const res = await fetch(`${BASE}/api/payment/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      subscriber_id: subscriberId,
      amount_bdt: amountBdt,
      items,
    }),
  });
  if (!res.ok) throw new Error(`checkout failed: ${res.status}`);
  return res.json();
}
