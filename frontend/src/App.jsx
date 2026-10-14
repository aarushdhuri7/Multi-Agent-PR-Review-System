
import { useCallback, useEffect, useState } from "react";
import {
  ShieldCheck,
  GitPullRequest,
  History,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  FileCode2,
  ChevronDown,
  ChevronUp,
  LoaderCircle,
  Bug,
  Gauge,
  FlaskConical,
  FileText,
  ShieldAlert,
  Sparkles,
  XCircle,
} from "lucide-react";
import "./App.css";

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const AGENT_ICONS = {
  security: ShieldAlert,
  bug: Bug,
  performance: Gauge,
  testing: FlaskConical,
  documentation: FileText,
};

function getSeverity(text = "") {
  const match = text.match(
    /\b(CRITICAL|HIGH|MEDIUM|LOW|INFO|INFORMATIONAL)\b/i
  );
  return match ? match[1].toLowerCase() : "info";
}

function parseReport(report = "") {
  const sections = [];
  let currentSection = {
    title: "Review Summary",
    content: [],
    findings: [],
  };

  const lines = String(report).split(/\r?\n/);
  const sectionPattern =
    /^(SECURITY REVIEW|BUG REVIEW|PERFORMANCE REVIEW|TESTING RECOMMENDATIONS|DOCUMENTATION REVIEW|FINAL RECOMMENDATION|AGENT ERRORS|WORKFLOW LIMITATION|CRITICAL ISSUES|HIGH ISSUES|MEDIUM ISSUES|LOW ISSUES)$/i;

  const saveSection = () => {
    if (
      currentSection.title ||
      currentSection.content.length ||
      currentSection.findings.length
    ) {
      sections.push(currentSection);
    }
  };

  let currentFinding = null;
  let previousField = "";

  const saveFinding = () => {
    if (currentFinding) {
      currentSection.findings.push(currentFinding);
      currentFinding = null;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line || /^[-=]{3,}$/.test(line)) continue;
    if (/^PULL REQUEST REVIEW SUMMARY$/i.test(line)) continue;
    if (/^Results from specialist code-review agents\.$/i.test(line)) continue;

    if (sectionPattern.test(line)) {
      saveFinding();
      saveSection();

      currentSection = {
        title: line
          .toLowerCase()
          .replace(/\b\w/g, (char) => char.toUpperCase()),
        content: [],
        findings: [],
      };
      previousField = "";
      continue;
    }

    const fieldMatch = line.match(
      /^(Severity|Priority|Issue|Test|Expected Result|Recommendation):\s*(.*)$/i
    );

    if (fieldMatch) {
      const field = fieldMatch[1].toLowerCase();
      const value = fieldMatch[2].trim();

      if (field === "severity" || field === "priority" || field === "test") {
        saveFinding();
        currentFinding = {
          severity: field === "test" ? "info" : getSeverity(value),
          issue: field === "test" ? value : "",
          recommendation: "",
          expectedResult: "",
          extra: [],
        };
      }

      if (!currentFinding) {
        currentFinding = {
          severity: "info",
          issue: "",
          recommendation: "",
          expectedResult: "",
          extra: [],
        };
      }

      if (field === "issue") currentFinding.issue = value;
      else if (field === "recommendation") {
        currentFinding.recommendation = value;
      } else if (field === "expected result") {
        currentFinding.expectedResult = value;
      } else if (field === "severity" || field === "priority") {
        currentFinding.severity = getSeverity(value);
      }

      previousField = field;
      continue;
    }

    if (currentFinding) {
      if (previousField === "recommendation") {
        currentFinding.recommendation +=
          (currentFinding.recommendation ? "\n" : "") + line;
      } else if (previousField === "expected result") {
        currentFinding.expectedResult +=
          (currentFinding.expectedResult ? "\n" : "") + line;
      } else if (previousField === "issue" || previousField === "test") {
        currentFinding.issue +=
          (currentFinding.issue ? "\n" : "") + line;
      } else {
        currentFinding.extra.push(line);
      }
    } else {
      currentSection.content.push(line);
    }
  }

  saveFinding();
  saveSection();

  return sections.filter(
    (section) =>
      section.title ||
      section.content.length ||
      section.findings.length
  );
}

function SeverityBadge({ severity }) {
  const label = severity || "info";
  return (
    <span className={`severity-badge severity-${label}`}>
      <span className="severity-dot" />
      {label}
    </span>
  );
}

function FindingCard({ finding, index }) {
  const [expanded, setExpanded] = useState(false);
  const hasDetails =
    finding.extra?.length > 0 || finding.expectedResult;

  return (
    <article className="finding-card">
      <div className="finding-topline">
        <SeverityBadge severity={finding.severity} />
        <span className="finding-number">
          Finding {String(index + 1).padStart(2, "0")}
        </span>
      </div>

      <h4 className="finding-title">
        {finding.issue || "Review observation"}
      </h4>

      {finding.recommendation && (
        <div className="recommendation-block">
          <span className="recommendation-label">
            <CheckCircle2 size={15} />
            Recommended action
          </span>
          <p>{finding.recommendation}</p>
        </div>
      )}

      {hasDetails && (
        <button
          className="details-toggle"
          onClick={() => setExpanded((value) => !value)}
          type="button"
        >
          {expanded ? "Hide details" : "Show details"}
          {expanded ? (
            <ChevronUp size={15} />
          ) : (
            <ChevronDown size={15} />
          )}
        </button>
      )}

      {expanded && (
        <div className="finding-details">
          {finding.expectedResult && (
            <p>
              <strong>Expected result:</strong>{" "}
              {finding.expectedResult}
            </p>
          )}
          {finding.extra?.map((item, i) => (
            <p key={i}>{item}</p>
          ))}
        </div>
      )}
    </article>
  );
}

function ReportSection({ section }) {
  const Icon =
    Object.entries(AGENT_ICONS).find(([key]) =>
      section.title.toLowerCase().includes(key)
    )?.[1] || FileText;

  const isFinal =
    section.title.toLowerCase().includes("final recommendation");

  return (
    <section
      className={`report-section ${isFinal ? "final-section" : ""}`}
    >
      <div className="section-heading">
        <span className="section-icon">
          <Icon size={18} />
        </span>
        <h3>{section.title}</h3>
        {section.findings.length > 0 && (
          <span className="section-count">
            {section.findings.length}{" "}
            {section.findings.length === 1 ? "item" : "items"}
          </span>
        )}
      </div>

      {section.content.length > 0 && (
        <div className="section-summary">
          {section.content.map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      )}

      {section.findings.length > 0 && (
        <div className="findings-list">
          {section.findings.map((finding, index) => (
            <FindingCard
              finding={finding}
              index={index}
              key={`${section.title}-${index}`}
            />
          ))}
        </div>
      )}
    </section>
  );
}

function VerifierPanel({ result }) {
  if (!result) return null;

  const status = result.verifier_status || (
    result.review_complete ? "passed" : "issues_detected"
  );

  const warnings = result.validation_warnings || [];
  const duplicates = result.duplicate_findings || [];
  const errors = result.agent_errors || [];

  return (
    <section className="verifier-panel">
      <div className="verifier-header">
        <span className="verifier-icon">
          <ShieldCheck size={20} />
        </span>
        <div className="verifier-heading">
          <h3>Verifier Agent</h3>
          <p>Structural checks on specialist outputs</p>
        </div>
        <span className={`verifier-status status-${status}`}>
          {status.replaceAll("_", " ")}
        </span>
      </div>

      <p className="verifier-message">
        {result.verifier_message ||
          "The verifier processed the specialist-agent outputs."}
      </p>

      <div className="verifier-metrics">
        <div>
          <span>Outputs checked</span>
          <strong>{result.verifier_checks ?? "—"}</strong>
        </div>
        <div>
          <span>Errors</span>
          <strong>{errors.length}</strong>
        </div>
        <div>
          <span>Warnings</span>
          <strong>{warnings.length}</strong>
        </div>
        <div>
          <span>Possible duplicates</span>
          <strong>{duplicates.length}</strong>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="verifier-alert">
          <XCircle size={16} />
          <div>
            <strong>Agent errors</strong>
            {errors.map((error, index) => (
              <p key={index}>
                {error.agent}: {error.message}
              </p>
            ))}
          </div>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="verifier-alert warning-alert">
          <AlertTriangle size={16} />
          <div>
            <strong>Validation warnings</strong>
            {warnings.map((warning, index) => (
              <p key={index}>
                {warning.agent}: {warning.message}
              </p>
            ))}
          </div>
        </div>
      )}

      {duplicates.length > 0 && (
        <div className="verifier-alert warning-alert">
          <AlertTriangle size={16} />
          <div>
            <strong>Possible duplicate findings</strong>
            {duplicates.map((duplicate, index) => (
              <p key={index}>
                {duplicate.agents?.join(" and ")}:{" "}
                {duplicate.text}
              </p>
            ))}
          </div>
        </div>
      )}

      <p className="verifier-disclaimer">
        Verification checks output structure and consistency signals.
        It does not prove that every reported issue is genuine.
      </p>
    </section>
  );
}

function App() {
  const [code, setCode] = useState(
    "def divide(a, b):\n    return a / b\n"
  );
  const [reviewResult, setReviewResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("report");

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_URL}/reviews`);
      if (!response.ok) throw new Error("Could not load review history.");

      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("History loading failed:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const submitReview = async (event) => {
    event.preventDefault();
    if (!code.trim()) {
      setError("Paste some code before starting a review.");
      return;
    }

    setLoading(true);
    setError("");
    setReviewResult(null);
    setActiveTab("report");

    try {
      const response = await fetch(`${API_URL}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || `Review failed (${response.status}).`
        );
      }

      setReviewResult(data);
      await loadHistory();
    } catch (err) {
      setError(
        err.message ||
          "Unable to reach the backend. Check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const openHistoryItem = async (item) => {
    setError("");
    setReviewResult(null);

    try {
      const response = await fetch(`${API_URL}/reviews/${item.id}`);
      if (!response.ok) throw new Error("Could not open this saved review.");

      const data = await response.json();

      setCode(data.code || "");
      setReviewResult({
        review_id: data.id,
        final_report: data.report,
        historyOnly: true,
      });
      setActiveTab("report");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(err.message);
    }
  };

  const reportSections = reviewResult?.final_report
    ? parseReport(reviewResult.final_report)
    : [];

  const counts = reportSections.reduce(
    (acc, section) => {
      section.findings.forEach((finding) => {
        acc[finding.severity] = (acc[finding.severity] || 0) + 1;
      });
      return acc;
    },
    {}
  );

  const agentCount = reviewResult?.verified_findings
    ? Object.keys(reviewResult.verified_findings).length
    : reviewResult?.findings
      ? Object.keys(reviewResult.findings).filter(
          (key) => !reviewResult.findings[key]?.status
        ).length
      : 0;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={23} />
          </div>
          <div>
            <h1>ReviewPilot</h1>
            <p>Multi-Agent Code Intelligence</p>
          </div>
        </div>

        <div className="local-pill">
          <span className="live-dot" />
          Local AI <span className="pill-divider">·</span> Ollama
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <div className="eyebrow">
            <Sparkles size={14} />
            AI-POWERED CODE REVIEW
          </div>
          <h2>
            Ship cleaner code<span>.</span>
          </h2>
          <p>
            Independent specialist agents review your code for security,
            bugs, performance, testing, and documentation.
          </p>
        </section>

        <div className="workspace">
          <section className="panel editor-panel">
            <div className="panel-heading">
              <div className="panel-heading-icon">
                <GitPullRequest size={19} />
              </div>
              <div>
                <h3>New code review</h3>
                <p>Paste a code snippet to start a review.</p>
              </div>
            </div>

            <form onSubmit={submitReview}>
              <label className="field-label" htmlFor="source-code">
                <FileCode2 size={15} />
                Source code
              </label>

              <textarea
                id="source-code"
                className="code-editor"
                value={code}
                onChange={(event) => setCode(event.target.value)}
                placeholder="Paste your source code here..."
                spellCheck={false}
                autoCapitalize="off"
                autoCorrect="off"
              />

              <div className="editor-footer">
                <span>{code.split("\n").length} lines</span>
                <span>{code.length.toLocaleString()} characters</span>
              </div>

              <button
                className="primary-button"
                type="submit"
                disabled={loading || !code.trim()}
              >
                {loading ? (
                  <>
                    <LoaderCircle className="spin" size={19} />
                    Analyzing with five agents...
                  </>
                ) : (
                  <>
                    <ShieldCheck size={19} />
                    Analyze code
                  </>
                )}
              </button>

              {loading && (
                <div className="loading-panel">
                  <LoaderCircle className="spin" size={17} />
                  <div>
                    <strong>Review in progress</strong>
                    <p>
                      Specialist agents are analyzing your code. Local
                      model inference can take some time.
                    </p>
                  </div>
                </div>
              )}

              {error && (
                <div className="error-banner">
                  <AlertTriangle size={18} />
                  <span>{error}</span>
                </div>
              )}
            </form>
          </section>

          <aside className="panel history-panel">
            <div className="panel-heading history-heading">
              <div className="panel-heading-icon">
                <History size={19} />
              </div>
              <div className="history-title">
                <h3>Review history</h3>
                <p>Your saved reviews</p>
              </div>
              <button
                className="icon-button"
                type="button"
                title="Refresh review history"
                onClick={loadHistory}
                disabled={historyLoading}
              >
                <RefreshCw
                  size={17}
                  className={historyLoading ? "spin" : ""}
                />
              </button>
            </div>

            {historyLoading && history.length === 0 ? (
              <div className="empty-state">
                <LoaderCircle className="spin" size={22} />
                <p>Loading history...</p>
              </div>
            ) : history.length === 0 ? (
              <div className="empty-state">
                <Clock3 size={27} />
                <p>Your completed reviews will appear here.</p>
              </div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <button
                    className="history-item"
                    type="button"
                    key={item.id}
                    onClick={() => openHistoryItem(item)}
                  >
                    <span className="history-item-icon">
                      <FileCode2 size={17} />
                    </span>
                    <span className="history-item-copy">
                      <strong>Review #{item.id}</strong>
                      <small>
                        {item.created_at
                          ? new Date(item.created_at).toLocaleString()
                          : "Saved review"}
                      </small>
                    </span>
                    <ChevronDown size={16} />
                  </button>
                ))}
              </div>
            )}
          </aside>
        </div>

        {reviewResult?.final_report && (
          <section className="results-area">
            <div className="results-heading">
              <div>
                <div className="eyebrow results-eyebrow">
                  <CheckCircle2 size={14} />
                  REVIEW REPORT
                </div>
                <h2>Analysis results</h2>
                <p>
                  {reviewResult.historyOnly
                    ? `Saved review #${reviewResult.review_id}`
                    : `Review #${reviewResult.review_id ?? "completed"} · ${
                        agentCount ? `${agentCount} usable agent outputs` : "Specialist findings"
                      }`}
                </p>
              </div>
              <span className="completed-pill">
                <span className="live-dot" />
                Report ready
              </span>
            </div>

            <div className="summary-grid">
              <div className="summary-card">
                <span className="summary-icon critical-icon">
                  <ShieldAlert size={19} />
                </span>
                <span className="summary-label">Critical</span>
                <strong>{counts.critical || 0}</strong>
              </div>
              <div className="summary-card">
                <span className="summary-icon high-icon">
                  <AlertTriangle size={19} />
                </span>
                <span className="summary-label">High</span>
                <strong>{counts.high || 0}</strong>
              </div>
              <div className="summary-card">
                <span className="summary-icon medium-icon">
                  <Bug size={19} />
                </span>
                <span className="summary-label">Medium</span>
                <strong>{counts.medium || 0}</strong>
              </div>
              <div className="summary-card">
                <span className="summary-icon low-icon">
                  <CheckCircle2 size={19} />
                </span>
                <span className="summary-label">Low / Info</span>
                <strong>{(counts.low || 0) + (counts.info || 0)}</strong>
              </div>
            </div>

            <div className="results-tabs">
              <button
                type="button"
                className={activeTab === "report" ? "active" : ""}
                onClick={() => setActiveTab("report")}
              >
                <FileText size={16} />
                Final report
              </button>
              {!reviewResult.historyOnly && (
                <button
                  type="button"
                  className={activeTab === "verifier" ? "active" : ""}
                  onClick={() => setActiveTab("verifier")}
                >
                  <ShieldCheck size={16} />
                  Verifier
                  {reviewResult.agent_errors?.length > 0 && (
                    <span className="tab-alert">
                      {reviewResult.agent_errors.length}
                    </span>
                  )}
                </button>
              )}
              {!reviewResult.historyOnly && (
                <button
                  type="button"
                  className={activeTab === "raw" ? "active" : ""}
                  onClick={() => setActiveTab("raw")}
                >
                  <FileCode2 size={16} />
                  Raw report
                </button>
              )}
            </div>

            {activeTab === "report" && (
              <div className="report-container">
                {reportSections.map((section, index) => (
                  <ReportSection section={section} key={index} />
                ))}

                <div className="report-footer">
                  <ShieldCheck size={17} />
                  Generated by ReviewPilot specialist agents
                </div>
              </div>
            )}

            {activeTab === "verifier" && (
              <VerifierPanel result={reviewResult} />
            )}

            {activeTab === "raw" && (
              <pre className="raw-report">
                {reviewResult.final_report}
              </pre>
            )}
          </section>
        )}
      </main>

      <footer className="app-footer">
        <span>
          <ShieldCheck size={15} />
          ReviewPilot
        </span>
        <span>Local inference · Your code stays on your machine</span>
      </footer>
    </div>
  );
}

export default App;
