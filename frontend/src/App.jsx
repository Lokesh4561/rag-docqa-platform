import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask(e) {
    e.preventDefault();
    if (question.trim().length < 3) return;
    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>DocQA</h1>
      <p className="subtitle">Ask questions about your documents</p>

      <form onSubmit={ask} className="ask-form">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Why should ingestion pipelines be idempotent?"
          aria-label="Question"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {answer && (
        <section className="answer">
          <h2>Answer</h2>
          <p>{answer}</p>
          <h3>Sources</h3>
          <ol>
            {sources.map((s) => (
              <li key={s.n}>
                {s.title} <span className="score">(score {s.score})</span>
              </li>
            ))}
          </ol>
        </section>
      )}
    </main>
  );
}
