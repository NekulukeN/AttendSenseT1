import { useEffect, useState } from "react";
import API from "../api/client";

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [tab,       setTab]       = useState("anomalies");

  useEffect(() => {
    async function fetchData() {
      try {
        const [anomRes, auditRes] = await Promise.all([
          API.get("/audit/anomalies"),
          API.get("/audit/logs"),
        ]);
        setAnomalies(anomRes.data || []);
        setAuditLogs(auditRes.data || []);
      } catch {
        setAnomalies([]);
        setAuditLogs([]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const tabStyle = (active) => ({
    padding: "0.6rem 1.5rem",
    borderRadius: "8px 8px 0 0",
    border: "none",
    cursor: "pointer",
    fontWeight: "600",
    background: active ? "white" : "#e2e8f0",
    color: active ? "#0f172a" : "#64748b",
    borderBottom: active ? "2px solid #0ea5e9" : "none",
  });

  return (
    <div>
      <h1 style={{ color: "#0f172a", marginBottom: "0.5rem" }}>
        Anomaly & Audit Logs
      </h1>
      <p style={{ color: "#64748b", marginBottom: "2rem" }}>
        Monitor suspicious activity and system actions.
      </p>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0" }}>
        <button style={tabStyle(tab === "anomalies")} onClick={() => setTab("anomalies")}>
          ⚠️ Anomalies ({anomalies.length})
        </button>
        <button style={tabStyle(tab === "audit")} onClick={() => setTab("audit")}>
          📋 Audit Trail ({auditLogs.length})
        </button>
      </div>

      <div style={{
        background: "white", borderRadius: "0 12px 12px 12px",
        padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        {loading ? (
          <p style={{ color: "#64748b" }}>Loading...</p>
        ) : tab === "anomalies" ? (
          <>
            <h2 style={{ marginBottom: "1rem", color: "#ef4444" }}>
              ⚠️ Flagged Anomalies
            </h2>
            {anomalies.length === 0 ? (
              <p style={{ color: "#64748b" }}>No anomalies detected. ✅</p>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#fef2f2" }}>
                    {["Student", "Session", "Reason", "Flagged At"].map(h => (
                      <th key={h} style={{
                        padding: "0.75rem", textAlign: "left", color: "#374151"
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {anomalies.map((a, i) => (
                    <tr key={i} style={{ borderTop: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "0.75rem", fontWeight: "600" }}>
                        {a.student}
                      </td>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>
                        {a.session}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        <span style={{
                          background: "#fee2e2", color: "#dc2626",
                          padding: "0.25rem 0.75rem", borderRadius: "999px",
                          fontSize: "0.8rem", fontWeight: "600"
                        }}>
                          {a.reason}
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>
                        {new Date(a.flagged_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        ) : (
          <>
            <h2 style={{ marginBottom: "1rem" }}>📋 Audit Trail</h2>
            {auditLogs.length === 0 ? (
              <p style={{ color: "#64748b" }}>No audit logs yet.</p>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#f8fafc" }}>
                    {["Actor", "Action", "Detail", "Timestamp"].map(h => (
                      <th key={h} style={{
                        padding: "0.75rem", textAlign: "left", color: "#374151"
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log, i) => (
                    <tr key={i} style={{ borderTop: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "0.75rem", fontWeight: "600" }}>
                        {log.actor}
                      </td>
                      <td style={{ padding: "0.75rem" }}>
                        <span style={{
                          background: "#dbeafe", color: "#1d4ed8",
                          padding: "0.25rem 0.75rem", borderRadius: "999px",
                          fontSize: "0.8rem", fontWeight: "600"
                        }}>
                          {log.action}
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>
                        {log.detail || "—"}
                      </td>
                      <td style={{ padding: "0.75rem", color: "#64748b" }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </div>
  );
}