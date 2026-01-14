import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import DashboardCard from "../components/DashboardCard";
import { AlertCircle, CheckCircle, Clock, XCircle, RefreshCcw } from "lucide-react";
const API = "http://127.0.0.1:5000";

export default function Dashboard({ user }) {
  const [pipelines, setPipelines] = useState([]);
  const [riskScore, setRiskScore] = useState({});
  const [threatCategories, setThreatCategories] = useState({});
  const [loading, setLoading] = useState(false);

  // ✅ Fetch dashboard data
  const fetchDashboardData = useCallback(() => {
    setLoading(true);

    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No JWT token found");
      setLoading(false);
      return;
    }

    axios
      .get(`${API}/api/dashboard-data`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => {
        setPipelines(res.data.pipelines || []);
        setRiskScore(res.data.risk_score || {});
        setThreatCategories(res.data.threat_categories || {});
      })
      .catch((err) => {
        console.error("Error fetching dashboard data:", err);
      })
      .finally(() => setLoading(false));
  }, []);


  // ✅ Auto-refresh every 10 seconds
  useEffect(() => {
    fetchDashboardData(); // initial fetch
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  // Chart data
  const riskChartData = Object.entries(riskScore).map(([name, value]) => ({
    name,
    value,
  }));

  const threatChartData = Object.entries(threatCategories).map(
    ([name, value]) => ({
      name: name.replaceAll("_", " ").toUpperCase(),
      value,
    })
  );

  const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e"];

  return (
    <div className="p-6 md:p-10">
      {/* Header */}
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-2">
            Welcome back, <span className="text-[#64ffda]">{user?.username}</span>
          </h1>
          <p className="text-[#8892b0] text-lg">
            Monitor key performance metrics and real-time system activity.
          </p>
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchDashboardData}
          className="flex items-center gap-2 bg-[#64ffda] text-black px-4 py-2 rounded-xl font-semibold hover:bg-[#4be6c7] transition-all"
        >
          <RefreshCcw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        <DashboardCard title="Risk Score Chart">
          {riskChartData.length > 0 ? (
            <PieChart width={350} height={250}>
              <Pie
                data={riskChartData}
                cx="50%"
                cy="50%"
                outerRadius={90}
                dataKey="value"
                label
              >
                {riskChartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          ) : (
            <p className="text-gray-400">No data yet</p>
          )}
        </DashboardCard>

        <DashboardCard title="Threat Category Breakdown">
          {threatChartData.length > 0 ? (
            <BarChart
              width={400}
              height={250}
              data={threatChartData}
              margin={{ top: 20, right: 30, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#233554" />
              <XAxis
                dataKey="name"
                tick={{ fill: "#ccd6f6", fontSize: 12 }}
                interval={0}
                angle={-15}
                textAnchor="end"
              />
              <YAxis tick={{ fill: "#ccd6f6", fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#64ffda" barSize={30} radius={[8, 8, 0, 0]} />
            </BarChart>
          ) : (
            <p className="text-gray-400">No threats found</p>
          )}
        </DashboardCard>
      </div>

      {/* Alerts */}
      <DashboardCard
        title="Recent Alerts"
        description="Latest security alerts and incidents"
      >
        <ul className="space-y-0">
          {Object.entries(riskScore).length > 0 ? (
            Object.entries(riskScore).map(([sev, count], index) => {
              const color =
                sev === "CRITICAL"
                  ? "text-red-500"
                  : sev === "HIGH"
                    ? "text-orange-500"
                    : sev === "MEDIUM"
                      ? "text-yellow-500"
                      : "text-green-500";
              const Icon =
                sev === "CRITICAL"
                  ? XCircle
                  : sev === "HIGH"
                    ? AlertCircle
                    : sev === "MEDIUM"
                      ? Clock
                      : CheckCircle;
              return (
                <li
                  key={index}
                  className="flex items-center border-b border-[#233554] py-3 last:border-b-0"
                >
                  <Icon className={`w-5 h-5 mr-3 ${color}`} />
                  <span className="text-[#ccd6f6] flex-1">
                    {sev} Severity – {count} findings
                  </span>
                </li>
              );
            })
          ) : (
            <p className="text-gray-400">No alerts available</p>
          )}
        </ul>
      </DashboardCard>

      {/* Pipelines */}
      <div className="mt-12">
        <DashboardCard
          title="Recent Pipelines"
          description="Summary of recent pipeline runs"
        >
          <ul className="space-y-0">
            {pipelines.length > 0 ? (
              pipelines.map((pipeline, index) => (
                <li
                  key={index}
                  className="flex items-center border-b border-[#233554] py-3 last:border-b-0"
                >
                  <span className="text-[#ccd6f6] flex-1">
                    {pipeline.name} – Status:{" "}
                    <span
                      className={`font-semibold ${pipeline.status === "success"
                          ? "text-green-500"
                          : pipeline.status === "failed"
                            ? "text-red-500"
                            : "text-[#64ffda]"
                        }`}
                    >
                      {pipeline.status.charAt(0).toUpperCase() +
                        pipeline.status.slice(1)}
                    </span>{" "}
                    – {pipeline.runtime}
                  </span>
                  {pipeline.status === "running" && (
                    <Clock className="w-5 h-5 text-[#64ffda] animate-pulse" />
                  )}
                </li>
              ))
            ) : (
              <p className="text-gray-400">No pipelines yet</p>
            )}
          </ul>
        </DashboardCard>
      </div>
    </div>
  );
}
