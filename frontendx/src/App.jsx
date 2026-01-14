import React, { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";

import Home from "./pages/Home";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Reports from "./pages/Reports";
import Pipelines from "./pages/Pipelines";
import DashboardPipelines from "./pages/DashboardPipelines";
import ActivityPage from "./pages/Activity";
import AboutDevelopers from "./pages/AboutDevelopers";
import SettingsPage from "./pages/Settings";
import HelpPage from "./pages/Help";
import PipelineNew from "./pages/PipelineNew";
import PipelineDetail from "./pages/PipelineDetail";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";

export default function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  /* ============================
     FETCH CURRENT USER
     ============================ */
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch("http://127.0.0.1:5000/api/me", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error("Unauthorized");
        return r.json();
      })
      .then((data) => setUser(data.user))
      .catch(() => setUser(null));
  }, []);

  /* ============================
     LOGOUT
     ============================ */
  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/login");
  };

  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Home />} />
      <Route path="signup" element={<Signup />} />
      <Route path="login" element={<Login onLogin={setUser} />} />

      {/* Protected */}
      <Route element={<ProtectedRoute />}>
        <Route
          element={
            <AppLayout
              handleLogout={handleLogout}
              user={user}          // ✅ THIS FIXES EVERYTHING
            />
          }
        >
          <Route path="dashboard" element={<Dashboard user={user} />} />
          <Route path="dashboard/pipelines" element={<DashboardPipelines />} />
          <Route path="pipelines" element={<Pipelines />} />
          <Route path="pipelines/new" element={<PipelineNew />} />
          <Route path="pipelines/:id" element={<PipelineDetail />} />
          <Route path="reports" element={<Reports />} />
          <Route path="activity" element={<ActivityPage />} />
          <Route path="about" element={<AboutDevelopers />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="help" element={<HelpPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
