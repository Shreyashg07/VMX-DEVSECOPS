import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Plus,
  Trash2,
  GitBranch,
  Terminal,
  Layers,
  ArrowLeft,
  Save,
} from "lucide-react";

export default function PipelineNew() {
  const navigate = useNavigate();
  const API = "http://127.0.0.1:5000";
  const token = localStorage.getItem("token");

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [steps, setSteps] = useState([{ name: "Build", cmd: "" }]);
  const [loading, setLoading] = useState(false);

  /* =========================
     STEPS HANDLERS
     ========================= */
  const handleAddStep = () => {
    setSteps([...steps, { name: `Step ${steps.length + 1}`, cmd: "" }]);
  };

  const handleRemoveStep = (index) => {
    setSteps(steps.filter((_, i) => i !== index));
  };

  const handleStepChange = (index, field, value) => {
    const updated = [...steps];
    updated[index][field] = value;
    setSteps(updated);
  };

  /* =========================
     SUBMIT
     ========================= */
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) return;

    setLoading(true);
    try {
      const res = await fetch(`${API}/api/pipelines`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name,
          description,
          repo_url: repoUrl,
          branch,
          config_json: { steps },
        }),
      });

      if (!res.ok) throw new Error("Create failed");
      navigate("/pipelines");
    } catch (err) {
      alert("Failed to create pipeline");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050B18] via-[#071225] to-[#020617] text-white p-8">
      <div className="max-w-4xl mx-auto bg-[#0B1A33] border border-[#132A52] rounded-2xl shadow-xl p-8">

        {/* ================= HEADER ================= */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Create <span className="text-cyan-400">Pipeline</span>
            </h1>
            <p className="text-slate-400 mt-1">
              Define your CI/CD workflow steps
            </p>
          </div>

          <button
            onClick={() => navigate("/pipelines")}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-[#132A52] hover:bg-[#1b3a6d] rounded-lg"
          >
            <ArrowLeft size={16} />
            Back
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">

          {/* ================= BASIC INFO ================= */}
          <section>
            <SectionTitle icon={Layers} title="Pipeline Info" />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              <Input
                label="Pipeline Name"
                value={name}
                onChange={setName}
                placeholder="Build & Deploy API"
                required
              />

              <Input
                label="Branch"
                icon={GitBranch}
                value={branch}
                onChange={setBranch}
                placeholder="main"
              />
            </div>

            <div className="mt-4">
              <Textarea
                label="Description"
                value={description}
                onChange={setDescription}
                placeholder="What does this pipeline do?"
              />
            </div>

            <div className="mt-4">
              <Input
                label="Repository URL (optional)"
                value={repoUrl}
                onChange={setRepoUrl}
                placeholder="https://github.com/org/repo.git"
              />
            </div>
          </section>

          {/* ================= STEPS ================= */}
          <section>
            <SectionTitle icon={Terminal} title="Pipeline Steps" />

            <div className="space-y-4 mt-4">
              {steps.map((step, i) => (
                <div
                  key={i}
                  className="bg-[#050B18] border border-[#132A52] rounded-xl p-4"
                >
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-semibold text-sm text-cyan-400">
                      Step {i + 1}
                    </h4>

                    {steps.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveStep(i)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Step Name"
                      value={step.name}
                      onChange={(v) => handleStepChange(i, "name", v)}
                      placeholder="Build / Test / Scan"
                      required
                    />

                    <Input
                      label="Command"
                      value={step.cmd}
                      onChange={(v) => handleStepChange(i, "cmd", v)}
                      placeholder="npm install && npm test"
                      required
                    />
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={handleAddStep}
                className="flex items-center gap-2 text-sm px-3 py-2 bg-[#132A52] hover:bg-[#1b3a6d] rounded-lg"
              >
                <Plus size={16} />
                Add Step
              </button>
            </div>
          </section>

          {/* ================= ACTIONS ================= */}
          <div className="flex justify-end gap-3 pt-6 border-t border-[#132A52]">
            <button
              type="button"
              onClick={() => navigate("/pipelines")}
              className="px-4 py-2 bg-[#132A52] hover:bg-[#1b3a6d] rounded-lg"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={loading}
              className={`flex items-center gap-2 px-5 py-2 rounded-lg font-semibold ${
                loading
                  ? "bg-gray-600 cursor-not-allowed"
                  : "bg-cyan-400 text-black hover:bg-cyan-300"
              }`}
            >
              <Save size={16} />
              {loading ? "Creating…" : "Create Pipeline"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* =========================
   REUSABLE UI COMPONENTS
   ========================= */

function SectionTitle({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-2 text-lg font-semibold">
      <Icon size={18} className="text-cyan-400" />
      {title}
    </div>
  );
}

function Input({ label, value, onChange, placeholder, icon: Icon, required }) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1">{label}</label>
      <div className="relative">
        {Icon && (
          <Icon
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
          />
        )}
        <input
          required={required}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`w-full p-2 rounded-lg bg-[#050B18] border border-[#132A52] focus:ring-2 focus:ring-cyan-400 outline-none ${
            Icon ? "pl-9" : ""
          }`}
        />
      </div>
    </div>
  );
}

function Textarea({ label, value, onChange, placeholder }) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1">{label}</label>
      <textarea
        rows={3}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full p-2 rounded-lg bg-[#050B18] border border-[#132A52] focus:ring-2 focus:ring-cyan-400 outline-none"
      />
    </div>
  );
}
