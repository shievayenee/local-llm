import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { sendChat } from "./lib/api";

const parseContentParts = (text) => {
  const parts = [];
  const fence = /```([a-zA-Z0-9_-]*)?\n?([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = fence.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", content: text.slice(lastIndex, match.index) });
    }
    parts.push({
      type: "code",
      lang: match[1] || "",
      content: match[2].trim(),
    });
    lastIndex = fence.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push({ type: "text", content: text.slice(lastIndex) });
  }

  return parts.length ? parts : [{ type: "text", content: text }];
};

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
              <div className="bubble">
                {parseContentParts(msg.content).map((part, innerIdx) =>
                  part.type === "code" ? (
                    <pre className="code-block" key={`${idx}-${innerIdx}`}>
                      <code>{part.content}</code>
                    </pre>
                  ) : (
                    <p className="text-part" key={`${idx}-${innerIdx}`}>
                      {part.content}
                    </p>
                  )
                )}
              </div>
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
