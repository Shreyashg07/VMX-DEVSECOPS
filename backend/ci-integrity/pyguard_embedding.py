import os
import json
import pickle
import sys
import subprocess
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np
from utils.file_reader import read_file_text
from utils.similarity import cosine_sim

# --- BASE PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "embeddings", "malicious.pkl")

# backend/
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# backend/reports/
REPORT_DIR = os.path.join(BACKEND_DIR, "reports")

TRAIN_SCRIPT = os.path.join(BASE_DIR, "train_embeddings.py")

MODEL_NAME = "all-MiniLM-L6-v2"

# thresholds
THRESHOLD_LOW = 0.50
THRESHOLD_MED = 0.65
THRESHOLD_HIGH = 0.80


# =========================
# LOAD EMBEDDINGS
# =========================
def load_embeddings():
    print(f"[PyGuard] Using embeddings file: {EMBEDDINGS_FILE}")

    if not os.path.exists(EMBEDDINGS_FILE):
        print("[PyGuard] ⚠️ Embedding DB not found. Training now...")
        subprocess.run([sys.executable, TRAIN_SCRIPT], cwd=BASE_DIR, check=True)

    with open(EMBEDDINGS_FILE, "rb") as f:
        return pickle.load(f)


# =========================
# RISK CLASSIFIER
# =========================
def classify_risk(score):
    if score >= THRESHOLD_HIGH:
        return "HIGH"
    elif score >= THRESHOLD_MED:
        return "MEDIUM"
    elif score >= THRESHOLD_LOW:
        return "LOW"
    else:
        return "SAFE"


# =========================
# FILE SCAN
# =========================
def scan_file(model, text, db):
    emb = model.encode(text, convert_to_numpy=True)
    best_score = 0
    best_entry = None

    for entry in db:
        score = cosine_sim(emb, entry["embedding"])
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_score, best_entry


# =========================
# REPO SCAN
# =========================
def scan_repo(repo_path):
    print(f"[PyGuard] Loading embedding model {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    print("[PyGuard] Loading malicious embedding database...")
    db = load_embeddings()

    os.makedirs(REPORT_DIR, exist_ok=True)

    findings = []
    scanned = 0

    print(f"[PyGuard] Scanning repository: {repo_path}\n")

    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.startswith("."):
                continue

            if not f.endswith((".py", ".js", ".sh", ".yml", ".yaml",
                               ".json", ".php", ".txt", "Dockerfile")):
                continue

            file_path = os.path.join(root, f)
            scanned += 1

            text = read_file_text(file_path)
            if not text.strip():
                continue

            score, match = scan_file(model, text, db)
            if score < THRESHOLD_LOW:
                continue

            risk = classify_risk(score)
            print(f"[!] ALERT: {file_path} -> {risk} (score {score:.2f})")

            findings.append({
                "file": file_path,
                "score": float(score),
                "risk": risk,
                "category": match["category"],
                "matched_sample": match["path"],
                "malicious_snippet": match["text_snippet"][:350]
            })

    summary = {
        "timestamp": str(datetime.now()),
        "repo": repo_path,
        "files_scanned": scanned,
        "hits": len(findings),
        "risk_level": max([f["risk"] for f in findings], default="SAFE"),
        "details": findings
    }

    # JSON report
    json_out = os.path.join(REPORT_DIR, "embedding_report.json")
    with open(json_out, "w") as jf:
        json.dump(summary, jf, indent=4)

    # HTML report
    html_out = os.path.join(REPORT_DIR, "embedding_report.html")
    with open(html_out, "w", encoding="utf-8") as hf:
        hf.write(generate_html(summary))

    print("\n[PyGuard] Scan complete.")
    print(f"[PyGuard] JSON report: {json_out}")
    print(f"[PyGuard] HTML report: {html_out}")

    return summary


# =========================
# HTML REPORT (COOL UI)
# =========================
def generate_html(data):
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PyGuard Integrity Report</title>
  <style>
    body {{
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #0a192f;
      color: #ccd6f6;
      margin: 0;
      padding: 0;
    }}
    h1 {{
      text-align: center;
      color: #64ffda;
      padding: 25px 0;
    }}
    .container {{
      width: 90%;
      max-width: 1100px;
      margin: auto;
    }}
    .card {{
      background: #112240;
      border: 1px solid #233554;
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 20px;
      box-shadow: 0 0 10px rgba(100,255,218,0.08);
    }}
    .risk {{
      font-weight: bold;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .risk.HIGH {{ color: #ffa500; background: rgba(255,165,0,0.15); }}
    .risk.MEDIUM {{ color: #ffd700; background: rgba(255,255,0,0.15); }}
    .risk.LOW {{ color: #9aff9a; background: rgba(50,205,50,0.15); }}

    code {{
      display: block;
      background: #0b1b30;
      border: 1px solid #233554;
      border-radius: 8px;
      padding: 10px;
      margin-top: 10px;
      white-space: pre-wrap;
      color: #9aff9a;
      font-size: 13px;
    }}
    footer {{
      text-align: center;
      color: #8892b0;
      margin: 40px 0;
      font-size: 13px;
    }}
  </style>
</head>

<body>
<h1>🚀 PyGuard Integrity Scan Report</h1>

<div class="container">
  <div class="card">
    <p><b>Timestamp:</b> {data["timestamp"]}</p>
    <p><b>Repository:</b> {data["repo"]}</p>
    <p><b>Files Scanned:</b> {data["files_scanned"]}</p>
    <p><b>Findings:</b> {data["hits"]}</p>
    <p><b>Overall Risk:</b>
      <span class="risk {data["risk_level"]}">{data["risk_level"]}</span>
    </p>
  </div>
"""

    for f in data["details"]:
        html += f"""
  <div class="card">
    <h3>
      <span class="risk {f["risk"]}">{f["risk"]}</span>
      — {os.path.basename(f["file"])}
    </h3>
    <p><b>Category:</b> {f["category"]}</p>
    <p><b>Score:</b> {f["score"]:.2f}</p>
    <p><b>Matched Sample:</b> {f["matched_sample"]}</p>
    <p><b>File Path:</b> <small>{f["file"]}</small></p>
    <code>{f["malicious_snippet"]}</code>
  </div>
"""

    html += """
</div>

<footer>
  PyGuard AI © 2025 — CI/CD Integrity Protection
</footer>

</body>
</html>
"""
    return html


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pyguard_embedding.py <repo_path>")
        sys.exit(1)

    scan_repo(sys.argv[1])
