import { useState, useEffect } from "react";
import DashboardCard from "../components/DashboardCard";
import { Activity as ActivityIcon, Edit, Trash2, Plus, Shield } from "lucide-react";
import io from "socket.io-client";

// Connect to backend socket server
const socket = io("http://127.0.0.1:5000");
const API = "http://127.0.0.1:5000";

export default function ActivityPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // ---- Fetch existing logs from backend ----
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/activity-logs")
      .then((res) => res.json())
      .then((data) => {
        setLogs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching activity logs:", err);
        setLoading(false);
      });
  }, []);

  // ---- Listen to real-time socket updates ----
  useEffect(() => {
    socket.on("activity_log", (newLog) => {
      const action = detectAction(newLog.message);
      setLogs((prev) => [
        {
          id: Date.now(),
          created_at: newLog.timestamp,
          details: { message: newLog.message },
          action,
          resource_type: "pipeline",
          resource_id: "live",
        },
        ...prev,
      ]);
    });

    return () => socket.off("activity_log");
  }, []);

  // ---- Detect action for color/icon ----
  const detectAction = (msg) => {
    if (!msg) return "updated";
    const text = msg.toLowerCase();
    if (text.includes("error") || text.includes("fail") || text.includes("alert"))
      return "deleted";
    if (text.includes("success") || text.includes("complete") || text.includes("finished"))
      return "created";
    if (text.includes("start") || text.includes("running"))
      return "updated";
    return "updated";
  };

  const getActionIcon = (action) => {
    switch (action) {
      case "created":
        return <Plus className="w-4 h-4 text-green-400" />;
      case "updated":
        return <Edit className="w-4 h-4 text-blue-400" />;
      case "deleted":
        return <Trash2 className="w-4 h-4 text-red-400" />;
      default:
        return <ActivityIcon className="w-4 h-4 text-[#64ffda]" />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case "created":
        return "text-green-400 bg-green-900 bg-opacity-20";
      case "updated":
        return "text-blue-400 bg-blue-900 bg-opacity-20";
      case "deleted":
        return "text-red-400 bg-red-900 bg-opacity-20";
      default:
        return "text-[#64ffda] bg-cyan-900 bg-opacity-20";
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "just now";
    const date = new Date(dateString);
    const diff = Date.now() - date.getTime();

    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  // ---- UI ----
  return (
    <div className="p-6">
      {/* Page Title */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Activity Log</h1>
        <p className="text-[#8892b0]">
          View all pipeline actions and real-time events in your VigilantX account.
        </p>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="text-center text-[#8892b0] py-12 animate-pulse">
          Loading activity logs...
        </div>
      ) : logs.length === 0 ? (
        <DashboardCard title="Recent Activity">
          <div className="text-center text-[#8892b0] py-12">
            No activity yet.
            <p className="text-sm mt-1">
              Logs will appear here when pipelines start running.
            </p>
          </div>
        </DashboardCard>
      ) : (
        <DashboardCard title="Recent Activity">
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="p-4 bg-[#0a1929] rounded-lg border border-[#233554] hover:border-[#64ffda] transition-all"
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className={`p-2 rounded-lg ${getActionColor(log.action)}`}>
                    {getActionIcon(log.action)}
                  </div>

                  {/* Message */}
                  <div className="flex-1 min-w-0">
                    <p className="text-[#ccd6f6] font-semibold">
                      {log.details?.message || "No additional details"}
                    </p>
                    <p className="text-[#8892b0] text-xs mt-2">
                      {formatDate(log.created_at)}
                    </p>
                  </div>

                  {/* Shield */}
                  <Shield className="w-5 h-5 text-[#64ffda] flex-shrink-0" />
                </div>
              </div>
            ))}
          </div>
        </DashboardCard>
      )}
    </div>
  );
}
