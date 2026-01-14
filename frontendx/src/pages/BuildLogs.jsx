import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';

export default function BuildLogs() {
  const { id } = useParams();
  const [logs, setLogs] = useState([]);
  const socketRef = useRef(null);

  // Use backend API URL from .env or fallback to localhost
  const API = "http://127.0.0.1:5000";


  useEffect(() => {
    // Fetch initial logs from backend
    const fetchLogs = async () => {
      try {
        const res = await fetch(`${API}/api/builds/${id}/logs`);
        if (!res.ok) throw new Error('Failed to fetch logs');
        const data = await res.json();
        // Assuming backend returns { logs: [...] }
        setLogs(data.logs || []);
      } catch (err) {
        console.error('Error fetching logs:', err);
        setLogs([]);
      }
    };

    fetchLogs();

    // Connect Socket.IO for live logs
    const socket = io(API, { transports: ['websocket', 'polling'] });
    socketRef.current = socket;

    socket.on('connect', () => console.log('Socket connected:', socket.id));

    socket.on('build_log', (data) => {
      if (String(data.build_id) === String(id)) {
        setLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            text: data.text,
            step_index: data.step_index,
          },
        ]);
      }
    });

    socket.on('build_finished', (data) => {
      if (String(data.build_id) === String(id)) {
        setLogs((prev) => [
          ...prev,
          {
            timestamp: new Date().toISOString(),
            text: `BUILD FINISHED: ${data.status}`,
            step_index: null,
          },
        ]);
      }
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [id, API]);

  return (
    <div className="p-6 bg-slate-900 rounded shadow-neon-glow min-h-screen">
      <h2 className="text-2xl mb-4 text-white">Build #{id} Logs</h2>
      <div className="bg-black/60 p-4 rounded h-96 overflow-auto font-mono text-sm text-slate-200">
        {logs.length === 0 ? (
          <p className="text-gray-400">No logs yet...</p>
        ) : (
          logs.map((l, i) => (
            <div key={i} className="mb-1">
              [{new Date(l.timestamp).toLocaleTimeString()}] {l.text}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
