import { useEffect, useState } from "react";
import {
  ShieldCheck,
  GitPullRequest,
  History,
  RefreshCw,
} from "lucide-react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const [code, setCode] = useState("");
  const [review, setReview] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadHistory() {
    try {
      const response = await fetch(`${API}/reviews`);
      if (!response.ok) throw new Error("Could not load review history.");
      setHistory(await response.json());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function submitReview(event) {
    event.preventDefault();

    if (!code.trim()) {
      setError("Paste some code before starting a review.");
      return;
    }

    setLoading(true);
    setError("");
    setReview(null);

    try {
      const response = await fetch(`${API}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Review failed.");

      setReview(data);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function openReview(id) {
    setError("");

    try {
      const response = await fetch(`${API}/reviews/${id}`);
      if (!response.ok) throw new Error("Could not open saved review.");

      const data = await response.json();

      setReview({
        review_id: data.id,
        final_report: data.report,
        findings: {},
        verified_findings: {},
        review_complete: true,
        saved_code: data.code,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={23} /></div>
          <div>
            <h1>ReviewPilot</h1>
            <p>Multi-Agent Code Intelligence</p>
          </div>
        </div>
        <span className="status"><span /> Local AI · Ollama</span>
      </header>

      <section className="hero">
        <p className="eyebrow">AI-POWERED CODE REVIEW</p>
        <h2>Ship cleaner code.</h2>
        <p className="hero-copy">
          Review code with specialist AI agents for security, bugs,
          performance, testing and documentation.
        </p>
      </section>

      <div className="dashboard-grid">
        <section className="panel editor-panel">
          <div className="panel-heading">
            <div>
              <h3><GitPullRequest size={18} /> New code review</h3>
              <p>Paste a code snippet to start a review.</p>
            </div>
          </div>

          <form onSubmit={submitReview}>
            <label htmlFor="code">Source code</label>
            <textarea
              id="code"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder={"def divide(a, b):\n    return a / b"}
              spellCheck="false"
            />
            <button className="primary-button" disabled={loading}>
              {loading
                ? <><RefreshCw className="spin" size={17} /> Reviewing agents...</>
                : <><ShieldCheck size={17} /> Analyze code</>}
            </button>
            {loading && (
              <p className="helper-text">
                The local model may take a few minutes to complete all agents.
              </p>
            )}
          </form>

          {error && <div className="error-box">{error}</div>}
        </section>

        <aside className="panel history-panel">
          <div className="panel-heading">
            <div>
              <h3><History size={18} /> Review history</h3>
              <p>Your saved reviews</p>
            </div>
            <button
              className="icon-button"
              onClick={loadHistory}
              title="Refresh history"
            >
              <RefreshCw size={16} />
            </button>
          </div>

          {history.length === 0 ? (
            <p className="empty-state">
              Your completed reviews will appear here.
            </p>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <button
                  className="history-item"
                  key={item.id}
                  onClick={() => openReview(item.id)}
                >
                  <span className="history-id">Review #{item.id}</span>
                  <span className="history-date">
                    {item.created_at
                      ? new Date(item.created_at).toLocaleString()
                      : "Saved review"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </aside>
      </div>

      {review && (
        <section className="panel results-panel">
          <div className="results-heading">
            <div>
              <p className="eyebrow">REVIEW RESULTS</p>
              <h3>Review #{review.review_id}</h3>
            </div>
            <span className={`review-status ${review.review_complete === false ? "incomplete" : ""}`}>
              {review.review_complete === false ? "Partial review" : "Report available"}
            </span>
          </div>

          <h4>Final report</h4>
          <pre className="report-content">{review.final_report}</pre>

          {review.agent_errors?.length > 0 && (
            <>
              <h4>Agent errors</h4>
              {review.agent_errors.map((item, index) => (
                <p className="error-box" key={`${item.agent}-${index}`}>
                  {item.agent}: {item.message}
                </p>
              ))}
            </>
          )}

          {Object.keys(review.verified_findings || {}).length > 0 && (
            <>
              <h4>Specialist findings</h4>
              {Object.entries(review.verified_findings).map(([agent, finding]) => (
                <div className="finding-card" key={agent}>
                  <strong>{agent.replaceAll("_", " ")}</strong>
                  <pre>
                    {typeof finding === "string"
                      ? finding
                      : JSON.stringify(finding, null, 2)}
                  </pre>
                </div>
              ))}
            </>
          )}
        </section>
      )}

      <footer>ReviewPilot · Built with FastAPI, React and local Ollama</footer>
    </main>
  );
}