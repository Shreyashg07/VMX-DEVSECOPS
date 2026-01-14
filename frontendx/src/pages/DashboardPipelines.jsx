import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import {
  List,
  Plus,
  Activity,
  CheckCircle,
  XCircle,
  Loader,
  RefreshCw,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  Info,
} from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const API = "http://127.0.0.1:5000";

  const token = localStorage.getItem("token");
  const socketRef = useRef(null);

  const [stats, setStats] = useState({
    pipelines: 0,
    running: 0,
    failed: 0,
    success: 0,
  });

  const [pipelines, setPipelines] = useState([]);
  const [recentBuilds, setRecentBuilds] = useState([]);
  const [loading, setLoading] = useState(true);

  /* ============================
     AUTH GUARD
     ============================ */
  useEffect(() => {
    if (!token) navigate("/login");
  }, [token, navigate]);

  /* ============================
     FETCH PIPELINES
     ============================ */
  const fetchPipelines = async () => {
    const res = await fetch(`${API}/api/pipelines`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();

    setPipelines(data);
    setStats({
      pipelines: data.length,
      running: data.filter((p) => p.status === "running").length,
      failed: data.filter((p) => p.status === "failed").length,
      success: data.filter((p) => p.status === "success").length,
    });
  };

  /* ============================
     FETCH BUILDS
     ============================ */
  const fetchBuilds = async () => {
    const res = await fetch(`${API}/api/builds`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();

    setRecentBuilds(
      data
        .sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
        .slice(0, 10)
    );
  };

  /* ============================
     SOCKET
     ============================ */
  useEffect(() => {
    if (!token) return;

    fetchPipelines();
    fetchBuilds();

    const socket = io(API, {
      auth: { token },
      transports: ["websocket"],
    });

    socketRef.current = socket;

    socket.on("build_status_update", () => {
      fetchPipelines();
      fetchBuilds();
    });

    socket.on("build_finished", () => {
      fetchPipelines();
      fetchBuilds();
    });

    setLoading(false);
    return () => socket.disconnect();
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#050B18] text-slate-400">
        Loading dashboard…
      </div>
    );
  }

  const totalBuilds = stats.running + stats.failed + stats.success;
  const successRate =
    totalBuilds > 0 ? Math.round((stats.success / totalBuilds) * 100) : 0;
  const failureRate =
    totalBuilds > 0 ? Math.round((stats.failed / totalBuilds) * 100) : 0;

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-[#050B18] via-[#071225] to-[#020617] text-white font-sans">
      {/* ================= HEADER ================= */}
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">
            CI/CD Pipeline <span className="text-cyan-400">Dashboard</span>
          </h1>
          <p className="text-slate-400 mt-1">
            Real-time pipeline health and execution overview
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => {
              fetchPipelines();
              fetchBuilds();
            }}
            className="flex items-center gap-2 px-4 py-2 bg-[#0B1A33] border border-[#132A52] rounded-lg hover:bg-[#132A52]"
          >
            <RefreshCw size={16} />
            Refresh
          </button>

          <button
            onClick={() => navigate("/pipelines/new")}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black rounded-lg hover:bg-cyan-300"
          >
            <Plus size={16} />
            New Pipeline
          </button>
        </div>
      </div>

      {/* ================= STATS ================= */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <Stat title="Total Pipelines" value={stats.pipelines} />
        <Stat title="Running" value={stats.running} icon={Loader} color="text-yellow-400" />
        <Stat title="Failed" value={stats.failed} icon={XCircle} color="text-red-400" />
        <Stat title="Success" value={stats.success} icon={CheckCircle} color="text-green-400" />
      </div>

      {/* ================= DASHBOARD INSIGHTS ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        {/* PERFORMANCE */}
        <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-cyan-400" />
            <h3 className="font-semibold">Pipeline Performance</h3>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <InlineKPI label="Executions" value={totalBuilds} />
            <InlineKPI label="Success Rate" value={`${successRate}%`} />
          </div>

          <div className="mt-6 space-y-4">
            <HealthBar label="Successful Builds" percent={successRate} />
            <HealthBar label="Failed Builds" percent={failureRate} />
          </div>
        </div>

        {/* STABILITY */}
        <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck size={16} className="text-cyan-400" />
            <h3 className="font-semibold">System Stability</h3>
          </div>

          <ul className="space-y-3 text-sm text-slate-400">
            <li>
              Healthy pipelines:{" "}
              <span className="text-white font-medium">{stats.success}</span>
            </li>
            <li>
              Active executions:{" "}
              <span className="text-white font-medium">{stats.running}</span>
            </li>
            <li>
              Failure signals:{" "}
              <span className="text-red-400 font-medium">{stats.failed}</span>
            </li>
          </ul>
        </div>

        {/* QUICK INSIGHTS */}
        <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6">
          <h3 className="font-semibold mb-4">Quick Insights</h3>

          <ul className="space-y-3 text-sm">
            {stats.failed === 0 && stats.running === 0 && (
              <Insight
                icon={CheckCircle}
                color="text-green-400"
                text="All pipelines are stable with no active issues"
              />
            )}

            {stats.failed > 0 && (
              <Insight
                icon={AlertTriangle}
                color="text-red-400"
                text={`${stats.failed} pipeline failure(s) detected — review required`}
              />
            )}

            {stats.running > 0 && (
              <Insight
                icon={Loader}
                color="text-yellow-400"
                spin
                text={`${stats.running} pipeline execution(s) currently running`}
              />
            )}

            {successRate >= 90 && stats.failed === 0 && (
              <Insight
                icon={TrendingUp}
                color="text-cyan-400"
                text="High reliability: success rate above 90%"
              />
            )}

            {pipelines.length === 0 && (
              <Insight
                icon={Info}
                color="text-slate-400"
                text="No pipelines configured — create your first pipeline"
              />
            )}
          </ul>
        </div>
      </div>

      {/* ================= MAIN CONTENT ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* PIPELINES */}
        <div className="lg:col-span-2 bg-[#0B1A33] border border-[#132A52] rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-5 flex items-center gap-2">
            <List size={16} className="text-cyan-400" />
            Pipelines
          </h2>

          {pipelines.length === 0 ? (
            <p className="text-slate-400 text-sm">No pipelines created yet</p>
          ) : (
            pipelines.map((p) => (
              <div
                key={p.id}
                onClick={() => navigate(`/pipelines/${p.id}`)}
                className="cursor-pointer mb-3 p-4 rounded-lg border border-[#132A52] bg-[#050B18] hover:bg-[#071225]"
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium">{p.name}</span>
                  <span className="text-xs uppercase text-slate-400">
                    {p.status || "idle"}
                  </span>
                </div>
                <div className="text-sm text-slate-400 mt-1">
                  {p.description || "No description provided"}
                </div>
              </div>
            ))
          )}
        </div>

        {/* ACTIVITY */}
        <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-5 flex items-center gap-2">
            <Activity size={16} className="text-cyan-400" />
            Recent Activity
          </h2>

          {recentBuilds.length === 0 ? (
            <p className="text-slate-400 text-sm">No recent activity</p>
          ) : (
            recentBuilds.map((b) => (
              <div
                key={b.id}
                className="flex items-start gap-3 mb-4 p-3 rounded-lg bg-[#050B18] border border-[#132A52]"
              >
                {b.status === "success" && (
                  <CheckCircle className="text-green-400 mt-1" size={16} />
                )}
                {b.status === "failed" && (
                  <XCircle className="text-red-400 mt-1" size={16} />
                )}
                {b.status === "running" && (
                  <Loader className="text-yellow-400 mt-1 animate-spin" size={16} />
                )}

                <div>
                  <div className="text-sm font-medium">
                    {b.pipeline_name || `Pipeline #${b.pipeline_id}`}{" "}
                    <span className="uppercase text-slate-400 ml-1">
                      {b.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    {b.started_at
                      ? new Date(b.started_at).toLocaleString()
                      : "—"}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

/* ============================
   REUSABLE COMPONENTS
   ============================ */

function Stat({ title, value, icon: Icon, color = "text-cyan-400" }) {
  return (
    <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-5">
      <div className="flex justify-between items-center text-slate-400 text-sm">
        {title}
        {Icon && <Icon size={16} />}
      </div>
      <div className={`text-3xl font-extrabold tracking-tight mt-2 ${color}`}>
        {value}
      </div>
    </div>
  );
}

function InlineKPI({ label, value }) {
  return (
    <div>
      <div className="text-xs text-slate-400 uppercase tracking-wide">
        {label}
      </div>
      <div className="text-2xl font-extrabold tracking-tight">
        {value}
      </div>
    </div>
  );
}

function HealthBar({ label, percent }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 bg-[#132A52] rounded-full overflow-hidden">
        <div
          className="h-2 bg-cyan-400"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

function Insight({ icon: Icon, text, color, spin }) {
  return (
    <li className="flex items-start gap-2">
      <Icon
        size={16}
        className={`${color} ${spin ? "animate-spin" : ""} mt-0.5`}
      />
      <span className="text-slate-300">{text}</span>
    </li>
  );
}
