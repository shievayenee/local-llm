import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { sendChat } from "./lib/api";

const DEFAULT_PROMPT = "Say hi!";

function App() {
  const [messages, setMessages] = useState([
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: DEFAULT_PROMPT },
  ]);
  const [input, setInput] = useState(DEFAULT_PROMPT);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);

  const displayMessages = useMemo(
    () => messages.filter((m) => m.role !== "system"),
    [messages]
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [displayMessages.length]);

  const handleSubmit = async (evt) => {
    evt.preventDefault();
    if (!input.trim() || loading) return;

    const nextMessages = [
      ...messages,
      { role: "user", content: input.trim() },
    ];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const result = await sendChat(nextMessages);
      setMessages([...nextMessages, result.message]);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Local LLM Chat</p>
          <h1>Talk to your local model</h1>
          <p className="subtitle">
            Powered by FastAPI + Ollama. Update <code>VITE_API_BASE_URL</code>{" "}
            for remote deployments.
          </p>
        </div>
        <div className="pill">React + Vite</div>
      </header>

      <section className="chat-panel">
        <div className="chat-history" ref={scrollRef}>
          {displayMessages.map((msg, idx) => (
            <div key={idx} className={`chat-row ${msg.role}`}>
              <div className="avatar">{msg.role === "user" ? "🧑" : "🤖"}</div>
              <div className="bubble">{msg.content}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-row assistant">
              <div className="avatar">🤖</div>
              <div className="bubble bubble-muted">Thinking…</div>
            </div>
          )}
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>
        {error && <div className="error">{error}</div>}
      </section>
    </div>
  );
}

export default App;
