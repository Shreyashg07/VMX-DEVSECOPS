import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, User, Lock } from "lucide-react";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const API = "http://127.0.0.1:5000";

  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setErr("");

    // ✅ CLIENT VALIDATION
    if (!username.trim()) return setErr("Username is required.");
    if (!password.trim()) return setErr("Password is required.");
    if (password.length < 4)
      return setErr("Password must be at least 4 characters.");
    if (password !== confirmPassword)
      return setErr("Passwords do not match.");

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Signup failed");

      // ✅ DO NOT LOGIN HERE (JWT FLOW)
      navigate("/login");
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#061328] to-[#173255] flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-[#64ffda] rounded-xl mx-auto flex items-center justify-center shadow-[0_0_15px_rgba(100,255,218,0.3)] mb-4">
            <Shield className="w-10 h-10 text-[#061328]" />
          </div>
          <h1 className="text-4xl font-bold text-white">Create Account</h1>
          <p className="text-[#ccd6f6] mt-1">Join VigilantX today</p>
        </div>

        {/* Card */}
        <div className="bg-[#112240] p-8 rounded-xl border border-[#233554] shadow-2xl">
          <form onSubmit={submit} className="space-y-6">

            {/* Username */}
            <div>
              <label className="text-sm text-[#ccd6f6]">Username</label>
              <div className="relative mt-1">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8892b0]" />
                <input
                  type="text"
                  placeholder="Choose a username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-[#0a1929] border border-[#233554] rounded-lg text-[#ccd6f6] focus:border-[#64ffda]"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="text-sm text-[#ccd6f6]">Password</label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8892b0]" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-[#0a1929] border border-[#233554] rounded-lg text-[#ccd6f6] focus:border-[#64ffda]"
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="text-sm text-[#ccd6f6]">Confirm Password</label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8892b0]" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-[#0a1929] border border-[#233554] rounded-lg text-[#ccd6f6] focus:border-[#64ffda]"
                />
              </div>
            </div>

            {/* Error */}
            {err && (
              <div className="p-3 bg-red-900/30 border border-red-500 rounded-lg text-red-300 text-sm">
                {err}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-[#64ffda] text-[#061328] font-bold rounded-lg hover:bg-[#79ffe0] disabled:bg-gray-600"
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          <p className="text-center text-[#8892b0] mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-[#64ffda] hover:text-[#79ffe0]">
              Sign in
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
