import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api/client";

// Fetches a probe photo as an authenticated blob and displays it.
// Plain <img src="..."> can't send the JWT header, so we fetch manually.
function ProbeImage({ probeId }) {
  const [imgUrl, setImgUrl] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let objectUrl = null;
    let cancelled = false;

    async function loadImage() {
      try {
        const res = await API.get(`/probe/image/${probeId}`, { responseType: "blob" });
        if (cancelled) return;
        objectUrl = URL.createObjectURL(res.data);
        setImgUrl(objectUrl);
      } catch {
        if (!cancelled) setFailed(true);
      }
    }
    loadImage();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [probeId]);

  if (failed) {
    return <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>No image</span>;
  }
  if (!imgUrl) {
    return <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>Loading...</span>;
  }
  return (
    <img
      src={imgUrl}
      alt="Probe capture"
      onClick={() => window.open(imgUrl, "_blank")}
      style={{
        width: "56px", height: "56px", objectFit: "cover",
        borderRadius: "6px", cursor: "pointer", border: "1px solid #e2e8f0"
      }}
    />
  );
}

function StatusPill({ passed }) {
  if (passed === null || passed === undefined) {
    return (
      <span style={{
        background: "#f1f5f9", color: "#64748b",
        padding: "0.2rem 0.6rem", borderRadius: "999px",
        fontSize: "0.75rem", fontWeight: "600"
      }}>—</span>
    );
  }
  return (
    <span style={{
      background: passed ? "#dcfce7" : "#fee2e2",
      color: passed ? "#16a34a" : "#dc2626",
      padding: "0.2rem 0.6rem", borderRadius: "999px",
      fontSize: "0.75rem", fontWeight: "600"
    }}>
      {passed ? "✅ Pass" : "❌ Fail"}
    </span>
  );
}

export default function Probes() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [probes, setProbes]       = useState([]);
  const [loading, setLoading]     = useState(true);
  const [slideInput, setSlideInput] = useState("");
  const [savingSlide, setSavingSlide] = useState(false);
  const [issuing, setIssuing]     = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);

  useEffect(() => {
    fetchAll();
    // Poll every 10s so the dashboard updates live as students respond
    const interval = setInterval(fetchProbes, 10000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function fetchAll() {
    await Promise.all([fetchProbes(), fetchSessionInfo()]);
    setLoading(false);
  }

  async function fetchProbes() {
    try {
      const res = await API.get(`/probe/results/${sessionId}`);
      setProbes(res.data || []);
    } catch {
      setProbes([]);
    }
  }

  async function fetchSessionInfo() {
    try {
      const res = await API.get("/attendance/sessions/all");
      const found = (res.data || []).find(s => String(s.id) === String(sessionId));
      setSessionInfo(found || null);
      if (found?.current_slide) setSlideInput(String(found.current_slide));
    } catch {
      setSessionInfo(null);
    }
  }

  async function saveSlide() {
    const num = parseInt(slideInput, 10);
    if (isNaN(num)) return;
    setSavingSlide(true);
    try {
      await API.patch(`/attendance/sessions/${sessionId}/slide?slide_number=${num}`);
      await fetchSessionInfo();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update slide number.");
    } finally {
      setSavingSlide(false);
    }
  }

  async function issueProbe() {
    setIssuing(true);
    try {
      await API.post(`/probe/issue-manual/${sessionId}`);
      await fetchProbes();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to issue probe.");
    } finally {
      setIssuing(false);
    }
  }

  return (
    <div>
      <button
        onClick={() => navigate("/sessions")}
        style={{
          background: "none", border: "none", color: "#0ea5e9",
          cursor: "pointer", marginBottom: "1rem", fontWeight: "600", padding: 0
        }}
      >
        ← Back to Sessions
      </button>

      <h1 style={{ color: "#0f172a", marginBottom: "0.25rem" }}>
        Probe Responses {sessionInfo ? `— ${sessionInfo.class_name}` : ""}
      </h1>
      <p style={{ color: "#64748b", marginBottom: "2rem" }}>
        Session #{sessionId} · Review captured photos and probe pass/fail results.
      </p>

      {/* Controls */}
      <div style={{
        background: "white", borderRadius: "12px", padding: "1.5rem",
        marginBottom: "1.5rem", boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        display: "flex", gap: "2rem", flexWrap: "wrap", alignItems: "flex-end"
      }}>
        <div>
          <label style={{ display: "block", fontSize: "0.85rem", color: "#64748b", marginBottom: "0.4rem" }}>
            Current Slide Number
          </label>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="number"
              value={slideInput}
              onChange={e => setSlideInput(e.target.value)}
              placeholder="e.g. 5"
              style={{
                width: "100px", padding: "0.6rem", border: "1px solid #d1d5db",
                borderRadius: "8px", fontSize: "1rem"
              }}
            />
            <button onClick={saveSlide} disabled={savingSlide} style={{
              padding: "0.6rem 1.2rem", background: "#0ea5e9", color: "white",
              border: "none", borderRadius: "8px", fontWeight: "bold", cursor: "pointer"
            }}>
              {savingSlide ? "Saving..." : "Update"}
            </button>
          </div>
        </div>

        <button onClick={issueProbe} disabled={issuing} style={{
          padding: "0.7rem 1.4rem", background: "#E65100", color: "white",
          border: "none", borderRadius: "8px", fontWeight: "bold", cursor: "pointer"
        }}>
          {issuing ? "Issuing..." : "⚠️ Issue Probe Now"}
        </button>
      </div>

      {/* Probe Results Table */}
      <div style={{
        background: "white", borderRadius: "12px", padding: "1.5rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)"
      }}>
        <h2 style={{ marginBottom: "1rem" }}>All Probe Attempts ({probes.length})</h2>

        {loading ? (
          <p style={{ color: "#64748b" }}>Loading...</p>
        ) : probes.length === 0 ? (
          <p style={{ color: "#64748b" }}>No probes issued for this session yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                {["Photo", "Student", "Action", "Camera", "Slide", "Overall", "Sent", "Responded"].map(h => (
                  <th key={h} style={{ padding: "0.75rem", textAlign: "left", color: "#374151" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {probes.map(p => (
                <tr key={p.probe_id} style={{ borderTop: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "0.75rem" }}>
                    {p.has_image ? <ProbeImage probeId={p.probe_id} /> : (
                      <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>—</span>
                    )}
                  </td>
                  <td style={{ padding: "0.75rem", fontWeight: "600" }}>{p.student}</td>
                  <td style={{ padding: "0.75rem", color: "#64748b" }}>
                    {p.action.replace("_", " ")}
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    <StatusPill passed={p.camera_passed} />
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    {p.slide_answer !== null && p.slide_answer !== undefined ? (
                      <div>
                        <StatusPill passed={p.slide_passed} />
                        <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "2px" }}>
                          answered {p.slide_answer} (expected {p.expected_slide})
                        </div>
                      </div>
                    ) : (
                      <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>—</span>
                    )}
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    <span style={{
                      padding: "0.2rem 0.6rem", borderRadius: "999px", fontSize: "0.75rem",
                      fontWeight: "600",
                      background: p.status === "passed" ? "#dcfce7" : p.status === "pending" ? "#fef9c3" : "#fee2e2",
                      color: p.status === "passed" ? "#16a34a" : p.status === "pending" ? "#a16207" : "#dc2626",
                    }}>
                      {p.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b", fontSize: "0.85rem" }}>
                    {new Date(p.sent_time).toLocaleTimeString()}
                  </td>
                  <td style={{ padding: "0.75rem", color: "#64748b", fontSize: "0.85rem" }}>
                    {p.response_time ? new Date(p.response_time).toLocaleTimeString() : "—"}
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
