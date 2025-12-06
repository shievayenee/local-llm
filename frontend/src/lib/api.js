const API_BASE =
  (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "") || "";

export async function sendChat(messages, model) {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, model }),
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || `Request failed: ${res.status}`);
  }

  return res.json();
}
