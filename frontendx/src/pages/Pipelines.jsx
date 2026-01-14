import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import {
  Plus,
  Filter,
  Loader,
  CheckCircle,
  XCircle,
  Layers,
  Play,
  Trash2,
} from "lucide-react";

export default function Pipelines() {
  const API = "http://127.0.0.1:5000";
  const navigate = useNavigate();
  const socketRef = useRef(null);
  const token = localStorage.getItem("token");

  const [pipelines, setPipelines] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  const [deleteId, setDeleteId] = useState(null);
  const [runStatus, setRunStatus] = useState(null);

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
    if (!token) return;

    try {
      const res = await fetch(`${API}/api/pipelines`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        setPipelines([]);
        return;
      }

      const data = await res.json();
      setPipelines(Array.isArray(data) ? data : []);
    } catch {
      setPipelines([]);
    } finally {
      setLoading(false);
    }
  };

  /* ============================
     SOCKET
     ============================ */
  useEffect(() => {
    if (!token) return;

    fetchPipelines();

    const socket = io(API, {
      auth: { token },
      transports: ["websocket"],
    });

    socketRef.current = socket;
    socket.on("build_status_update", fetchPipelines);
    socket.on("build_finished", fetchPipelines);

    return () => socket.disconnect();
    // eslint-disable-next-line
  }, [token]);

  /* ============================
     ACTIONS
     ============================ */
  const handleRun = async (id) => {
    try {
      const res = await fetch(`${API}/api/pipelines/${id}/run`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error();

      setRunStatus({
        type: "success",
        message: "Pipeline started successfully",
      });

      fetchPipelines();
    } catch {
      setRunStatus({
        type: "error",
        message: "Pipeline failed to start",
      });
    }
  };

  const handleDelete = async () => {
    try {
      await fetch(`${API}/api/pipelines/${deleteId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setPipelines((prev) => prev.filter((p) => p.id !== deleteId));
    } catch (e) {
      console.error("Delete failed", e);
    } finally {
      setDeleteId(null);
    }
  };

  /* ============================
     FILTERING
     ============================ */
  const safe = Array.isArray(pipelines) ? pipelines : [];
  const filtered =
    filter === "all"
      ? safe
      : safe.filter((p) => (p.status || "idle") === filter);

  const stats = {
    total: safe.length,
    running: safe.filter((p) => p.status === "running").length,
    success: safe.filter((p) => p.status === "success").length,
    failed: safe.filter((p) => p.status === "failed").length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-slate-400">
        Loading pipelines…
      </div>
    );
  }

  return (
    <div className="p-6 min-h-screen bg-[#050B18] text-white">
      {/* ================= HEADER ================= */}
      <div className="flex justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold">
            Pipelines <span className="text-cyan-400">Overview</span>
          </h1>
          <p className="text-slate-400 mt-1">
            Manage and run CI/CD pipelines
          </p>
        </div>

        <button
          onClick={() => navigate("/pipelines/new")}
          className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                     bg-cyan-400 text-black rounded-md hover:bg-cyan-300"
        >
          <Plus size={16} />
          New Pipeline
        </button>
      </div>

      {/* ================= STATS ================= */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Stat title="Total" value={stats.total} icon={Layers} color="text-cyan-400" />
        <Stat title="Running" value={stats.running} icon={Loader} color="text-yellow-400" spin />
        <Stat title="Success" value={stats.success} icon={CheckCircle} color="text-green-400" />
        <Stat title="Failed" value={stats.failed} icon={XCircle} color="text-red-400" />
      </div>

      {/* ================= FILTER ================= */}
      <div className="flex gap-3 mb-8">
        <Filter size={16} className="text-slate-400" />
        {["all", "running", "success", "failed"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1 rounded-full text-sm ${
              filter === f
                ? "bg-cyan-400 text-black"
                : "bg-[#0B1A33] text-slate-400"
            }`}
          >
            {f.toUpperCase()}
          </button>
        ))}
      </div>

      {/* ================= PIPELINES ================= */}
      {filtered.length === 0 ? (
        <div className="text-center text-slate-400 mt-24">
          No pipelines found
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filtered.map((p) => (
            <div
              key={p.id}
              className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-5"
            >
              <div className="flex justify-between mb-2">
                <h3
                  onClick={() => navigate(`/pipelines/${p.id}`)}
                  className="font-semibold text-lg cursor-pointer hover:text-cyan-400"
                >
                  {p.name}
                </h3>
                <StatusBadge status={p.status} />
              </div>

              <p className="text-sm text-slate-400 mb-4">
                {p.description || "No description"}
              </p>

              {/* ACTION BUTTONS */}
              <div className="flex justify-between pt-4 border-t border-[#132A52]">
                <button
                  onClick={() => navigate(`/pipelines/${p.id}`)}
                  className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                             bg-slate-600 hover:bg-slate-500 rounded-md"
                >
                  Details
                </button>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleRun(p.id)}
                    className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                               bg-green-600 hover:bg-green-500 rounded-md"
                  >
                    <Play size={16} />
                    Run
                  </button>

                  <button
                    onClick={() => setDeleteId(p.id)}
                    className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                               bg-red-600 hover:bg-red-500 rounded-md"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ================= DELETE MODAL ================= */}
      {deleteId && (
        <Modal
          title="Delete Pipeline?"
          message="This action cannot be undone."
          onClose={() => setDeleteId(null)}
          onConfirm={handleDelete}
          danger
        />
      )}

      {/* ================= RUN STATUS MODAL ================= */}
      {runStatus && (
        <Modal
          title={runStatus.type === "success" ? "Pipeline Started" : "Pipeline Failed"}
          message={runStatus.message}
          onClose={() => setRunStatus(null)}
        />
      )}
    </div>
  );
}

/* ============================
   SHARED COMPONENTS
   ============================ */

function Stat({ title, value, icon: Icon, color, spin }) {
  return (
    <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6 relative">
      <div className="text-sm text-slate-400">{title}</div>
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      <div className="absolute top-4 right-4 opacity-60">
        <Icon size={18} className={spin ? "animate-spin" : ""} />
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    running: "bg-yellow-500/20 text-yellow-400",
    success: "bg-green-500/20 text-green-400",
    failed: "bg-red-500/20 text-red-400",
  };

  return (
    <span className={`text-xs px-2 py-1 rounded-full ${map[status] || "bg-slate-700 text-slate-300"}`}>
      {(status || "idle").toUpperCase()}
    </span>
  );
}

function Modal({ title, message, onClose, onConfirm, danger }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-[#0B1A33] border border-[#132A52] rounded-xl p-6 w-96 text-center">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-slate-400 mb-6">{message}</p>

        <div className="flex justify-center gap-3">
          <button
            onClick={onClose}
            className="h-9 px-4 bg-slate-700 hover:bg-slate-600 rounded-md"
          >
            Close
          </button>

          {onConfirm && (
            <button
              onClick={onConfirm}
              className={`h-9 px-4 rounded-md ${
                danger ? "bg-red-600 hover:bg-red-500" : "bg-green-600"
              }`}
            >
              Confirm
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
