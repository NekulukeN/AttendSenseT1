import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/client";

export default function Login() {
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await API.post("/auth/login", { email, password });
      localStorage.setItem("token",     res.data.access_token);
      localStorage.setItem("role",      res.data.role);
      localStorage.setItem("full_name", res.data.full_name);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh", display: "flex",
      alignItems: "center", justifyContent: "center",
      background: "#0f172a"
    }}>
      <div style={{
        background: "white", padding: "2.5rem",
        borderRadius: "16px", width: "100%", maxWidth: "400px",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
      }}>
        <h1 style={{ textAlign: "center", color: "#0f172a", marginBottom: "0.5rem" }}>
          👁️ AttendSense
        </h1>
        <p style={{ textAlign: "center", color: "#64748b", marginBottom: "2rem" }}>
          Admin Dashboard
        </p>

        {error && (
          <div style={{
            background: "#fee2e2", color: "#dc2626",
            padding: "0.75rem", borderRadius: "8px", marginBottom: "1rem"
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", color: "#374151" }}>
            Email
          </label>
          <input
            type="email" value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="admin@university.edu.my"
            required
            style={{
              width: "100%", padding: "0.75rem",
              border: "1px solid #d1d5db", borderRadius: "8px",
              marginBottom: "1rem", fontSize: "1rem",
              boxSizing: "border-box"
            }}
          />

          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", color: "#374151" }}>
            Password
          </label>
          <input
            type="password" value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            style={{
              width: "100%", padding: "0.75rem",
              border: "1px solid #d1d5db", borderRadius: "8px",
              marginBottom: "1.5rem", fontSize: "1rem",
              boxSizing: "border-box"
            }}
          />

          <button type="submit" disabled={loading} style={{
            width: "100%", padding: "0.85rem",
            background: loading ? "#94a3b8" : "#0ea5e9",
            color: "white", border: "none",
            borderRadius: "8px", fontSize: "1rem",
            fontWeight: "bold", cursor: loading ? "not-allowed" : "pointer"
          }}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}