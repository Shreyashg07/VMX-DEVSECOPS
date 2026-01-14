import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Mail, Lock } from "lucide-react";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const API = "http://127.0.0.1:5000";

  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");

    if (!username.trim()) return setError("Username is required.");
    if (!password.trim()) return setError("Password is required.");

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");

      // ✅ SAVE JWT
      localStorage.setItem("token", data.access_token);

      // ✅ SET USER (minimal)
      onLogin({ username });

      navigate("/dashboard");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#061328] to-[#173255] flex items-center justify-center px-4">
      <div className="max-w-md w-full">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#64ffda] rounded-xl mb-4 shadow-[0_0_15px_rgba(100,255,218,0.3)]">
            <Shield className="w-10 h-10 text-[#061328]" />
          </div>
          <h1 className="text-4xl font-bold text-white">Welcome Back</h1>
          <p className="text-[#ccd6f6] mt-1">Sign in to VigilantX</p>
        </div>

        {/* Card */}
        <div className="bg-[#112240] p-8 rounded-xl border border-[#233554] shadow-xl">
          <form onSubmit={submit} className="space-y-6">

            {/* Username */}
            <div>
              <label className="text-sm text-[#ccd6f6]">Username</label>
              <div className="relative mt-1">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8892b0]" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-[#0a1929] border border-[#233554] rounded-lg text-[#ccd6f6] focus:border-[#64ffda] focus:ring-[#64ffda]"
                  placeholder="Enter your username"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-sm text-[#ccd6f6]">Password</label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8892b0]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-[#0a1929] border border-[#233554] rounded-lg text-[#ccd6f6] focus:border-[#64ffda] focus:ring-[#64ffda]"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="p-3 bg-red-900/30 border border-red-500 rounded-lg text-red-300 text-sm">
                {error}
              </div>
            )}

            {/* Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-[#64ffda] text-[#061328] rounded-lg font-bold text-lg hover:bg-[#79ffe0] disabled:bg-gray-600"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Redirect */}
          <p className="text-center text-[#8892b0] mt-6">
            Don't have an account?{" "}
            <Link className="text-[#64ffda] hover:text-[#79ffe0]" to="/signup">
              Create one
            </Link>
          </p>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-[#8892b0] hover:text-[#64ffda]">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
