import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/client";

export default function Sessions() {
  const [sessions,   setSessions]   = useState([]);
  const [className,  setClassName]  = useState("");
  const [loading,    setLoading]    = useState(true);
  const [creating,   setCreating]   = useState(false);
  const navigate = useNavigate();

  useEffect(() => { fetchSessions(); }, []);

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

  async function createSession() {
    if (!className.trim()) return;
    setCreating(true);
    try {
      await API.post(`/attendance/sessions/create?class_name=${encodeURIComponent(className)}`);
      setClassName("");
      fetchSessions();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create session.");
    } finally {
      setCreating(false);
    }
  }

  async function endSession(id) {
    if (!window.confirm("End this session?")) return;
    try {
      await API.post(`/attendance/sessions/${id}/end`);
      fetchSessions();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to end session.");
    }
  }

  return (
    <div>
      <h1 style={{ color: "#0f172a", marginBottom: "2rem" }}>Sessions</h1>

      {/* Create Session */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "1.5rem", marginBottom: "1.5rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem" }}>Create New Session</h2>
        <div style={{ display: "flex", gap: "1rem" }}>
          <input
            value={className}
            onChange={e => setClassName(e.target.value)}
            placeholder="e.g. Web Technology - Group A"
            style={{
              flex: 1, padding: "0.75rem",
              border: "1px solid #d1d5db", borderRadius: "8px", fontSize: "1rem"
            }}
          />
          <button onClick={createSession} disabled={creating} style={{
            padding: "0.75rem 1.5rem", background: "#0ea5e9",
            color: "white", border: "none", borderRadius: "8px",
            fontWeight: "bold", cursor: "pointer"
          }}>
            {creating ? "Creating..." : "Create Session"}
          </button>
        </div>
      </div>

      {/* Sessions List */}
      <div style={{
        background: "white", borderRadius: "12px",
        padding: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem" }}>All Sessions</h2>
        {loading ? <p>Loading...</p> : sessions.length === 0 ? (
          <p style={{ color: "#64748b" }}>No sessions created yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                {["ID", "Class Name", "Status", "Start Time", "End Time", "Actions"].map(h => (
                  <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151" }}>{h}</th>
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
                      color: s.status === "active" ? "#16a34a" : "#64748b", fontWeight: "600"
                    }}>
                      {s.status}
                    </span>
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>
                    {new Date(s.start_time).toLocaleString()}
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>
                    {s.end_time ? new Date(s.end_time).toLocaleString() : "—"}
                  </td>
                  <td style={{ padding: "0.75rem", display: "flex", gap: "0.5rem" }}>
                    <button onClick={() => navigate(`/attendance/${s.id}`)} style={{
                        padding: "0.4rem 0.75rem", background: "#0ea5e9",
                        color: "white", border: "none", borderRadius: "6px", cursor: "pointer"
                      }}>
                        View
                    </button>
                    <button onClick={() => navigate(`/probes/${s.id}`)} style={{
                      padding: "0.4rem 0.75rem", background: "#E65100",
                      color: "white", border: "none", borderRadius: "6px", cursor: "pointer"
                    }}>
                      Probes
                      </button>
                      {s.status === "active" && (
                        <button onClick={() => endSession(s.id)} style={{
                          padding: "0.4rem 0.75rem", background: "#ef4444",
                          color: "white", border: "none", borderRadius: "6px", cursor: "pointer"
                        }}>
                          End
                      </button>
                    )}
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