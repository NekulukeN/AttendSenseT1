import { useState } from "react";
import API from "../api/client";

export default function Reports() {
  const [sessionId, setSessionId] = useState("");
  const [summary,   setSummary]   = useState(null);
  const [absent,    setAbsent]    = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState("");

  async function loadReport() {
    if (!sessionId) return;
    setLoading(true);
    setError("");
    try {
      const [sumRes, absRes] = await Promise.all([
        API.get(`/reports/sessions/${sessionId}/summary`),
        API.get(`/reports/sessions/${sessionId}/absent`),
      ]);
      setSummary(sumRes.data);
      setAbsent(absRes.data);
    } catch  {
      setError("Session not found or no data available.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadCSV() {
    try {
      const res = await API.get(`/reports/sessions/${sessionId}/export-csv`, {
        responseType: "blob"
      });
      const url  = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href  = url;
      link.setAttribute("download", `attendance_session_${sessionId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      alert("Failed to download CSV.");
    }
  }

  return (
    <div>
      <h1 style={{ color: "#0f172a", marginBottom: "2rem" }}>Reports</h1>

      {/* Search */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "1.5rem", marginBottom: "1.5rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem" }}>Load Session Report</h2>
        <div style={{ display: "flex", gap: "1rem" }}>
          <input
            type="number" value={sessionId}
            onChange={e => setSessionId(e.target.value)}
            placeholder="Enter Session ID"
            style={{
              flex: 1, padding: "0.75rem",
              border: "1px solid #d1d5db", borderRadius: "8px", fontSize: "1rem"
            }}
          />
          <button onClick={loadReport} disabled={loading} style={{
            padding: "0.75rem 1.5rem", background: "#0ea5e9",
            color: "white", border: "none", borderRadius: "8px",
            fontWeight: "bold", cursor: "pointer"
          }}>
            {loading ? "Loading..." : "Load Report"}
          </button>
        </div>
        {error && <p style={{ color: "#ef4444", marginTop: "0.5rem" }}>{error}</p>}
      </div>

      {summary && (
        <>
          {/* Summary Stats */}
          <div style={{
            background: "white", borderRadius: "12px",
            padding: "1.5rem", marginBottom: "1.5rem",
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h2>{summary.class_name} — Summary</h2>
              <button onClick={downloadCSV} style={{
                padding: "0.6rem 1.2rem", background: "#22c55e",
                color: "white", border: "none", borderRadius: "8px",
                fontWeight: "bold", cursor: "pointer"
              }}>
                ⬇️ Download CSV
              </button>
            </div>

            <div style={{
              display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
              gap: "1rem"
            }}>
              {[
                { label: "Present",       value: summary.total_present,     color: "#22c55e" },
                { label: "Checked Out",   value: summary.total_checked_out, color: "#0ea5e9" },
                { label: "Probes Sent",   value: summary.total_probes,      color: "#f59e0b" },
                { label: "Passed",        value: summary.probes_passed,     color: "#22c55e" },
                { label: "Failed",        value: summary.probes_failed,     color: "#ef4444" },
                { label: "Anomalies",     value: summary.total_anomalies,   color: "#ef4444" },
              ].map(s => (
                <div key={s.label} style={{
                  background: "#f8fafc", borderRadius: "8px", padding: "1rem",
                  borderLeft: `3px solid ${s.color}`
                }}>
                  <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: s.color }}>{s.value}</div>
                  <div style={{ color: "#64748b", fontSize: "0.8rem" }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Absent Students */}
          {absent && absent.absent_students.length > 0 && (
            <div style={{
              background: "white", borderRadius: "12px",
              padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
            }}>
              <h2 style={{ marginBottom: "1rem", color: "#ef4444" }}>
                ❌ Absent Students ({absent.total_absent})
              </h2>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#fef2f2" }}>
                    {["Student ID", "Full Name", "Email"].map(h => (
                      <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {absent.absent_students.map((s, i) => (
                    <tr key={i} style={{ borderTop: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>{s.student_id || "N/A"}</td>
                      <td style={{ padding: "0.75rem", fontWeight: "600" }}>{s.full_name}</td>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>{s.email}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}