import { useEffect, useState } from "react";
import API from "../api/client";

function StatCard({ title, value, color, icon }) {
  return (
    <div style={{
      background: "white", borderRadius: "12px",
      padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
      borderLeft: `4px solid ${color}`
    }}>
      <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>{icon}</div>
      <div style={{ fontSize: "2rem", fontWeight: "bold", color }}>{value}</div>
      <div style={{ color: "#64748b", marginTop: "0.25rem" }}>{title}</div>
    </div>
  );
}

export default function Dashboard() {
  const [sessions,  setSessions]  = useState([]);
  const [loading,   setLoading]   = useState(true);
  const full_name = localStorage.getItem("full_name");


 useEffect(() => {
  async function fetchSessions() {
    try {
      const res = await API.get("/attendance/sessions/all");
      setSessions(res.data || []);
    } catch {
      setSessions([]);
    } finally {
      setLoading(false);
    }
  }
   fetchSessions();
  }, []);

  const active = sessions.filter(s => s.status === "active").length;
  const ended  = sessions.filter(s => s.status === "ended").length;

  return (
    <div>
      <h1 style={{ color: "#0f172a", marginBottom: "0.5rem" }}>Dashboard</h1>
      <p style={{ color: "#64748b", marginBottom: "2rem" }}>
        Welcome back, <strong>{full_name}</strong>
      </p>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "1rem", marginBottom: "2rem"
      }}>
        <StatCard title="Total Sessions"  value={sessions.length} color="#0ea5e9" icon="📅" />
        <StatCard title="Active Sessions" value={active}          color="#22c55e" icon="🟢" />
        <StatCard title="Ended Sessions"  value={ended}           color="#64748b" icon="✅" />
      </div>

      <div style={{
        background: "white", borderRadius: "12px",
        padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem", color: "#0f172a" }}>Recent Sessions</h2>
        {loading ? (
          <p style={{ color: "#64748b" }}>Loading...</p>
        ) : sessions.length === 0 ? (
          <p style={{ color: "#64748b" }}>No sessions yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                {["ID", "Class", "Status", "Start Time", "Action"].map(h => (
                  <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151", fontWeight: "600" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => (
                <tr key={s.id} style={{ borderTop: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>#{s.id}</td>
                  <td style={{ padding: "0.75rem", fontWeight: "600" }}>{s.class_name}</td>
                  <td style={{ padding: "0.75rem" }}>
                    <span style={{
                      padding: "0.25rem 0.75rem", borderRadius: "999px", fontSize: "0.8rem",
                      background: s.status === "active" ? "#dcfce7" : "#f1f5f9",
                      color: s.status === "active" ? "#16a34a" : "#64748b",
                      fontWeight: "600"
                    }}>
                      {s.status}
                    </span>
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>
                    {new Date(s.start_time).toLocaleString()}
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    <a href={`/attendance/${s.id}`} style={{ color: "#0ea5e9", textDecoration: "none", fontWeight: "600" }}>
                      View →
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}