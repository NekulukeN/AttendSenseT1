import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate  = useNavigate();
  const full_name = localStorage.getItem("full_name");

  function logout() {
    localStorage.clear();
    navigate("/login");
  }

  const linkStyle = {
    display: "block", padding: "0.75rem 1rem",
    color: "#cbd5e1", textDecoration: "none",
    borderRadius: "8px", marginBottom: "0.25rem",
    transition: "background 0.2s",
  };

  return (
    <div style={{
      width: "220px", background: "#0f172a",
      padding: "1.5rem 1rem", display: "flex",
      flexDirection: "column", gap: "0.5rem"
    }}>
      {/* Logo */}
      <div style={{ color: "#38bdf8", fontWeight: "bold", fontSize: "1.2rem", marginBottom: "2rem", padding: "0 1rem" }}>
        👁️ AttendSense
      </div>

      <Link to="/"          style={linkStyle}>📊 Dashboard</Link>
      <Link to="/sessions"  style={linkStyle}>📅 Sessions</Link>
      <Link to="/reports"   style={linkStyle}>📄 Reports</Link>
      <Link to="/anomalies" style={linkStyle}>⚠️ Anomalies</Link>

      {/* User + Logout */}
      <div style={{ marginTop: "auto", padding: "1rem 0", borderTop: "1px solid #1e293b" }}>
        <div style={{ color: "#94a3b8", fontSize: "0.8rem", marginBottom: "0.5rem" }}>
          Logged in as:<br />
          <strong style={{ color: "#e2e8f0" }}>{full_name}</strong>
        </div>
        <button onClick={logout} style={{
          width: "100%", padding: "0.5rem",
          background: "#ef4444", color: "white",
          border: "none", borderRadius: "8px",
          cursor: "pointer", fontWeight: "bold"
        }}>
            
          Logout
        </button>
      </div>
    </div>
  );
}