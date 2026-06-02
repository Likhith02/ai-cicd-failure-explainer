import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, Bot, CheckCircle2, Loader2, TerminalSquare } from "lucide-react";
import "./styles.css";

const sampleLog = `Run pytest
FAILED tests/test_app.py::test_home_page
AssertionError: expected status code 200 but got 500
Error: Process completed with exit code 1.`;

function App() {
  const [logText, setLogText] = useState(sampleLog);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const canAnalyze = useMemo(() => logText.trim().length >= 20 && !isLoading, [logText, isLoading]);

  async function analyzeLog() {
    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/analyze-log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_text: logText }),
      });

      if (!response.ok) {
        throw new Error("The backend could not analyze this log.");
      }

      setResult(await response.json());
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="top-bar">
        <div>
          <p className="eyebrow">DevOps + Gen AI project</p>
          <h1>MY AI CI/CD Failure Explainer</h1>
        </div>
        <div className="status-pill">
          <CheckCircle2 size={18} />
          MVP
        </div>
      </section>

      <section className="workspace">
        <div className="panel input-panel">
          <div className="panel-title">
            <TerminalSquare size={20} />
            <h2>Build Log</h2>
          </div>
          <textarea
            value={logText}
            onChange={(event) => setLogText(event.target.value)}
            spellCheck="false"
            aria-label="CI/CD failure log"
          />
          <div className="actions">
            <button onClick={() => setLogText(sampleLog)} type="button" className="secondary-button">
              Load Sample
            </button>
            <button onClick={analyzeLog} type="button" disabled={!canAnalyze}>
              {isLoading ? <Loader2 className="spin" size={18} /> : <Bot size={18} />}
              Analyze
            </button>
          </div>
        </div>

        <div className="panel result-panel">
          <div className="panel-title">
            <Bot size={20} />
            <h2>Explanation</h2>
          </div>

          {!result && !error && (
            <div className="empty-state">
              <AlertTriangle size={28} />
              <p>Paste a failed CI/CD log and run the analysis.</p>
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          {result && (
            <div className="result-grid">
              <ResultBlock label="Summary" value={result.summary} />
              <ResultBlock label="Likely Root Cause" value={result.root_cause} />
              <ResultBlock label="Suggested Fix" value={result.suggested_fix} />
              <div className="meta-row">
                <span>Confidence: {result.confidence}</span>
                <span>Source: {result.source}</span>
              </div>
              <div className="error-lines">
                <h3>Error Lines</h3>
                {result.error_lines.length ? (
                  result.error_lines.map((line, index) => <code key={`${line}-${index}`}>{line}</code>)
                ) : (
                  <p>No exact error lines detected.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function ResultBlock({ label, value }) {
  return (
    <section className="result-block">
      <h3>{label}</h3>
      <p>{value}</p>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
