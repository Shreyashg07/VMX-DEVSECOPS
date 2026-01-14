
import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import {
  Play,
  Trash2,
  ArrowLeft,
  Activity,
  FileText,
  CheckCircle,
  XCircle,
  Loader,
} from "lucide-react";

export default function PipelineDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [pipeline, setPipeline] = useState(null);
  const [logs, setLogs] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔥 UI states
  const [runStatus, setRunStatus] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const API = "http://localhost:5000";
  const token = localStorage.getItem("token");
  const socketRef = useRef(null);

  /* ============================
     FETCH PIPELINE
     ============================ */
  const fetchPipeline = async () => {
    try {
      const res = await fetch(`${API}/api/pipelines/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setPipeline(data);
      setLogs(data.logs || []);
      setHistory(data.history || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  /* ============================
     SOCKET
     ============================ */
  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    fetchPipeline();

    const socket = io(API, {
      auth: { token },
      transports: ["websocket"],
    });

    socketRef.current = socket;

    socket.on("build_log", (line) =>
      setLogs((prev) => [...prev, line])
    );
    socket.on("build_status_update", fetchPipeline);
    socket.on("build_finished", fetchPipeline);

    return () => socket.disconnect();
    // eslint-disable-next-line
  }, [id]);

  /* ============================
     ACTIONS
     ============================ */
  const handleRun = async () => {
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

      fetchPipeline();
    } catch {
      setRunStatus({
        type: "error",
        message: "Pipeline failed to start",
      });
    }
  };

  const handleDelete = async () => {
    try {
      await fetch(`${API}/api/pipelines/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      navigate("/pipelines");
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !pipeline) {
    return (
      <div className="flex items-center justify-center min-h-screen text-slate-400">
        Loading pipeline…
      </div>
    );
  }

  /* ============================
     STAGES (SAFE PARSE)
     ============================ */
  let stages = [];
  try {
    const cfg =
      typeof pipeline.config_json === "string"
        ? JSON.parse(pipeline.config_json)
        : pipeline.config_json;
    stages = cfg?.steps || [];
  } catch {
    stages = [];
  }

  const overallStatus = pipeline.status;

  return (
    <div className="p-6 min-h-screen bg-[#050B18] text-white">
      {/* ================= HEADER ================= */}
      <div className="flex justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">{pipeline.name}</h1>
          <p className="text-slate-400">
            {pipeline.description || "No description"}
          </p>
        </div>

        {/* ACTION BUTTONS */}
        <div className="flex gap-2">
          <button
            onClick={handleRun}
            className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                       bg-green-600 hover:bg-green-500 rounded-md"
          >
            <Play size={16} />
            Run
          </button>

          <button
            onClick={() => setConfirmDelete(true)}
            className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                       bg-red-600 hover:bg-red-500 rounded-md"
          >
            <Trash2 size={16} />
            Delete
          </button>

          <button
            onClick={() => navigate("/pipelines")}
            className="h-9 px-4 flex items-center gap-2 text-sm font-medium
                       bg-slate-700 hover:bg-slate-600 rounded-md"
          >
            <ArrowLeft size={16} />
            Back
          </button>
        </div>
      </div>

      {/* ================= STATUS ================= */}
      <div className="mb-8">
        <StatusBadge status={overallStatus} />
      </div>

      {/* ================= STAGES ================= */}
      <div className="mb-12">
        <h2 className="flex items-center gap-2 mb-4">
          <Activity size={16} /> Pipeline Stages
        </h2>

        <div className="flex gap-6 overflow-x-auto">
          {stages.map((s, i) => (
            <div key={i} className="flex items-center gap-4">
              <div
                className={`w-24 h-24 flex items-center justify-center rounded-xl text-sm font-semibold
                  ${overallStatus === "running"
                    ? "bg-yellow-900/20 border border-yellow-400 text-yellow-300 animate-pulse"
                    : overallStatus === "success"
                      ? "bg-green-900/20 border border-green-400 text-green-300"
                      : overallStatus === "failed"
                        ? "bg-red-900/20 border border-red-400 text-red-300"
                        : "bg-[#0B1A33] border border-[#132A52] text-slate-400"
                  }`}
              >
                {s.name}
              </div>

              {i < stages.length - 1 && (
                <div className="w-8 h-[2px] bg-[#132A52]" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ================= LOGS ================= */}
      <div className="mb-12">
        <h2 className="flex items-center gap-2 mb-4">
          <FileText size={16} /> Build Logs
        </h2>

        <div className="bg-black border border-[#132A52] rounded p-4 max-h-96 overflow-y-auto font-mono text-sm">
          {logs.length ? logs.map((l, i) => <div key={i}>{l}</div>) : "No logs"}
        </div>
      </div>

      {/* ================= HISTORY ================= */}
      <div>
        <h2 className="flex items-center gap-2 mb-4">
          <Activity size={16} /> Build History
        </h2>

        <div className="bg-[#0B1A33] border border-[#132A52] rounded">
          <table className="w-full text-sm">
            <thead className="bg-[#050B18] text-slate-400">
              <tr>
                <th className="p-3">#</th>
                <th className="p-3">Date</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {history.length ? (
                history.map((h, i) => (
                  <tr key={i} className="border-t border-[#132A52]">
                    <td className="p-3">{i + 1}</td>
                    <td className="p-3">{h.date}</td>
                    <td className="p-3">
                      <StatusBadge status={h.status} small />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="3" className="text-center p-6 text-slate-500">
                    No history
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ================= DELETE MODAL ================= */}
      {confirmDelete && (
        <Modal
          title="Delete Pipeline?"
          message="This action cannot be undone."
          onClose={() => setConfirmDelete(false)}
          onConfirm={handleDelete}
          danger
        />
      )}

      {/* ================= RUN STATUS MODAL ================= */}
      {runStatus && (
        <Modal
          title={
            runStatus.type === "success"
              ? "Pipeline Started"
              : "Pipeline Failed"
          }
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

function StatusBadge({ status, small }) {
  const cls = small ? "text-xs px-2 py-1" : "text-sm px-3 py-1";

  if (status === "success")
    return (
      <span className={`${cls} bg-green-600/20 text-green-400 rounded`}>
        SUCCESS
      </span>
    );
  if (status === "failed")
    return (
      <span className={`${cls} bg-red-600/20 text-red-400 rounded`}>
        FAILED
      </span>
    );
  if (status === "running")
    return (
      <span
        className={`${cls} bg-yellow-600/20 text-yellow-400 rounded flex items-center gap-1`}
      >
        <Loader size={12} className="animate-spin" /> RUNNING
      </span>
    );

  return (
    <span className={`${cls} bg-slate-700 text-slate-300 rounded`}>
      IDLE
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
              className={`h-9 px-4 rounded-md ${danger
                  ? "bg-red-600 hover:bg-red-500"
                  : "bg-green-600"
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