import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login      from "./pages/Login";
import Dashboard  from "./pages/Dashboard";
import Sessions   from "./pages/Sessions";
import Attendance from "./pages/Attendance";
import Reports    from "./pages/Reports";
import Navbar     from "./components/Navbar";
import Anomalies from "./pages/Anomalies";
import Probes from "./pages/Probes";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <div style={{ display: "flex", minHeight: "100vh", background: "#f1f5f9" }}>
              <Navbar />
              <div style={{ flex: 1, padding: "2rem" }}>
                <Routes>
                  <Route path="/"          element={<Dashboard />} />
                  <Route path="/sessions"  element={<Sessions />} />
                  <Route path="/attendance/:sessionId" element={<Attendance />} />
                  <Route path="/reports"   element={<Reports />} />
                  <Route path="/anomalies" element={<Anomalies />} />
                  <Route path="/probes/:sessionId" element={<Probes />} />
                </Routes>
              </div>
            </div>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}