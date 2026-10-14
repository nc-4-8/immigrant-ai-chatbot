import { useState, useRef, useEffect } from "react";

const API_BASE = "http://localhost:8000";
const API_KEY = process.env.REACT_APP_API_KEY;
const SUGGESTIONS = [
  "How do I get a green card?",
  "How do I become a U.S. citizen?",
  "Where can I find a doctor?",
  "Where can I learn English?",
];

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState("English");
  const bottomRef = useRef(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMessage = { id: crypto.randomUUID(), role: "user", content: trimmed };
    const assistantId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantId, role: "assistant", content: "" },
    ]);
    setQuestion("");
    setLoading(true);
    setError(null);

    const currentRequestId = ++requestIdRef.current;

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ message: trimmed, language }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        if (currentRequestId !== requestIdRef.current) {
          reader.cancel();
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          if (!part.startsWith("data: ")) continue;
          const data = JSON.parse(part.slice(6));

          if (data.type === "token") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + data.content } : m
              )
            );
                    } else if (data.type === "done") {
            const sources = [
              ...new Set(
                data.documents.map((d) => d.metadata?.source).filter(Boolean)
              ),
            ];
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantId ? { ...m, sources } : m))
            );
          } else if (data.type === "error") {
            setError(data.error);
          }
        }
      }
    } catch (err) {
      if (currentRequestId !== requestIdRef.current) return;
      console.error(err);
      setError("Something went wrong getting a response. Please try again.");
    } finally {
      if (currentRequestId === requestIdRef.current) {
        setLoading(false);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(question);
  };

  return (
    <div className="chat-container">
      {messages.length === 0 && (
        <p className="greeting">Greetings Hola سَلَامٌ عَلَيْكُمْ 你好 नमस्ते</p>
      )}

      <div className="message-list">
  {messages.map((msg) => (
    <div key={msg.id} className={`message message-${msg.role}`}>
      <strong>{msg.role === "user" ? "You" : "Bot"}:</strong>{" "}
      {msg.content || (msg.role === "assistant" && loading ? "…" : "")}
      {msg.sources?.length > 0 && (
        <div className="sources">
          Sources:{" "}
          {msg.sources.map((url) => (
            <a key={url} href={url} target="_blank" rel="noreferrer">
              {url}
            </a>
          ))}
        </div>
      )}
    </div>
  ))}
  {error && <div className="message message-error">{error}</div>}
  <div ref={bottomRef} />
</div>

      {messages.length === 0 && (
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="English">English</option>
          <option value="Spanish">Español</option>
          <option value="Chinese">中文</option>
          <option value="Arabic">العربية</option>
          <option value="Hindi">हिन्दी</option>
        </select>
      )}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Sending..." : "Submit"}
        </button>
           </form>

      {messages.length === 0 && (
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} type="button" onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <p className="notice">
        This bot gives general information, not legal advice. For your own
        situation, talk to a licensed immigration attorney or an accredited
        representative.
      </p>
    </div>
  );
}

export default Chat;