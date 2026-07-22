import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api/client";

export default function Attendance() {
  const { sessionId }  = useParams();
  const [summary,  setSummary]  = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading,  setLoading]  = useState(true);


useEffect(() =>
  async function fetchData() {
    try {
      const [sumRes, anomRes] = await Promise.all([
        API.get(`/reports/sessions/${sessionId}/summary`),
        API.get(`/reports/sessions/${sessionId}/probe-failures`),
      ]);
      setSummary(sumRes.data);
      setAnomalies(anomRes.data.failures || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }
)


  if (loading) return <p>Loading...</p>;
  if (!summary) return <p>Session not found.</p>;

  return (
    <div>
      <h1 style={{ color: "#0f172a", marginBottom: "0.5rem" }}>
        {summary.class_name}
      </h1>
      <p style={{ color: "#64748b", marginBottom: "2rem" }}>
        Session #{sessionId} · Status:
        <strong style={{ color: summary.status === "active" ? "#16a34a" : "#64748b" }}>
          {" "}{summary.status}
        </strong>
      </p>

      {/* Stats */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
        gap: "1rem", marginBottom: "2rem"
      }}>
        {[
          { label: "Present",       value: summary.total_present,     color: "#22c55e" },
          { label: "Checked Out",   value: summary.total_checked_out, color: "#0ea5e9" },
          { label: "Probes Sent",   value: summary.total_probes,      color: "#f59e0b" },
          { label: "Probes Passed", value: summary.probes_passed,     color: "#22c55e" },
          { label: "Anomalies",     value: summary.total_anomalies,   color: "#ef4444" },
        ].map(stat => (
          <div key={stat.label} style={{
            background: "white", borderRadius: "12px", padding: "1.25rem",
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)", borderLeft: `4px solid ${stat.color}`
          }}>
            <div style={{ fontSize: "1.75rem", fontWeight: "bold", color: stat.color }}>
              {stat.value}
            </div>
            <div style={{ color: "#64748b", fontSize: "0.85rem" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Attendance Table */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "1.5rem", marginBottom: "1.5rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem" }}>Attendance Records</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f8fafc" }}>
              {["Student", "Check In", "Check Out", "Duration", "Probes", "Anomalies"].map(h => (
                <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {summary.attendance.map((r, i) => (
              <tr key={i} style={{ borderTop: "1px solid #f1f5f9" }}>
                <td style={{ padding: "0.75rem", fontWeight: "600" }}>{r.full_name}</td>
                <td style={{ padding: "0.75rem", color: "#64748b" }}>
                  {r.check_in_time ? new Date(r.check_in_time).toLocaleTimeString() : "—"}
                </td>
                <td style={{ padding: "0.75rem", color: "#64748b" }}>
                  {r.check_out_time ? new Date(r.check_out_time).toLocaleTimeString() : "—"}
                </td>
                <td style={{ padding: "0.75rem", color: "#64748b" }}>
                  {r.duration_minutes ? `${r.duration_minutes} min` : "—"}
                </td>
                <td style={{ padding: "0.75rem", color: "#64748b" }}>
                  {r.probes_passed}/{r.probes_received}
                </td>
                <td style={{ padding: "0.75rem" }}>
                  <span style={{
                    color: r.anomalies > 0 ? "#ef4444" : "#16a34a",
                    fontWeight: "bold"
                  }}>
                    {r.anomalies > 0 ? `⚠️ ${r.anomalies}` : "✅ 0"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <div style={{
          background: "white", borderRadius: "12px",
          padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
        }}>
          <h2 style={{ marginBottom: "1rem", color: "#ef4444" }}>⚠️ Probe Failures</h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#fef2f2" }}>
                {["Student", "Action", "Status", "Issued At"].map(h => (
                  <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {anomalies.map((a, i) => (
                <tr key={i} style={{ borderTop: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "0.75rem", fontWeight: "600" }}>{a.student}</td>
                  <td style={{ padding: "0.75rem", textTransform: "capitalize" }}>{a.action.replace("_", " ")}</td>
                  <td style={{ padding: "0.75rem" }}>
                    <span style={{
                      padding: "0.25rem 0.75rem", borderRadius: "999px",
                      background: "#fee2e2", color: "#dc2626",
                      fontSize: "0.8rem", fontWeight: "600"
                    }}>
                      {a.status}
                    </span>
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>
                    {new Date(a.issued_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}