CI/CD Pipeline Integrity & Code Injection Monitoring Tool
🚀 CI/CD Pipeline Integrity Scanner
Detect & stop malicious code injection, pipeline tampering, and supply-chain attacks in automated CI/CD builds.
🛡️ Overview

Modern supply-chain attacks target CI/CD pipelines, not just source code.
Attackers inject malicious steps, modify build scripts, hijack dependencies, or insert encoded payloads inside automated workflows.

Traditional tools like Trivy, Semgrep, Gitleaks, SonarQube do not detect CI/CD build-level attacks.

This tool solves that.

This is a lightweight CI/CD Integrity Monitoring & Malicious Code Injection Detection system that:

scans code, configs, pipelines, scripts, dependencies

detects malicious patterns, encoded payloads, RCE triggers

monitors GitHub Actions / Jenkins / GitLab pipelines

blocks malicious builds using risk scoring

sends incidents to a dashboard API

provides HTML + JSON reports

acts as a “Firewall” for CI/CD pipelines

🔥 FEATURES
✔ CI/CD Workflow Security

Scans .github/workflows/*.yml, Jenkinsfile, .gitlab-ci.yml

Detects malicious CI steps (curl | sh, downloaded scripts, inline bash)

Detects unauthorized external GitHub Actions

Detects CI tampering in PRs

✔ Code Injection Detection

Python AST detection: eval(), exec(), compile()

Suspicious subprocess usage

Inline shell execution

Obfuscated or encoded payloads

Dangerous JS patterns (new Function, eval)

✔ Supply-Chain Defense

Typosquatted dependency detection

Suspicious package names (a, x, test123)

Dependency hijack patterns

High-entropy encoded blobs

✔ Behavioral Security (Unique!)

Not just regex. It detects behavior patterns:

remote script execution

git history tampering (reset --hard)

suspicious network calls

unexpected automation changes

embedded secrets or tokens

potential backdoor code

✔ CI Build Protection

Generates risk score

Fails CI build if score > threshold

Warn / allow based on policy

Real-time blocking of malicious PR builds

✔ Dashboard API & Incident Storage

FastAPI backend

Stores incidents in SQLite

View JSON + HTML reports

Perfect for enterprise DevSecOps teams

📦 Project Structure
cicd-integrity-monitor/
│
├── scanner/                  # Main detection engine
│   ├── detectors/            # Regex, AST, YAML, entropy detectors
│   ├── policy.py             # Thresholds & scoring
│   ├── engine.py             # Combines all detectors
│   ├── cli.py                # CLI entrypoint
│   └── reporter.py           # JSON + HTML reports
│
├── api/                      # Dashboard API (FastAPI)
│   ├── app/
│   └── templates/
│
├── rules/                    # Regex signatures
├── policies/                 # Policy config
├── scripts/                  # Local scan script
├── docker/                   # Docker setup
└── .github/workflows         # GitHub Action integration

🚀 Quick Start
🔧 Local Scan (CLI)
python -m scanner.scanner.cli /path/to/project

🐳 Docker Scan (recommended)
docker build -t cicd-scan:latest -f docker/Dockerfile .
docker run --rm -v /your/code:/workspace cicd-scan:latest /workspace


Generates:

scan_report.json

scan_report.html

⚙️ GitHub Actions Integration

Add this to ANY repo (no scanner files needed):

name: CI Security Scan

on:
  push:
  pull_request:

jobs:
  scan:
    uses: yourname/cicd-integrity-monitor/.github/workflows/cicd-security-scan.yml@main


Automatically:

runs scanner

blocks malicious code

uploads HTML + JSON reports

sends incident to dashboard API

🖥️ Dashboard API

Start dashboard:

uvicorn api.app.main:app --host 0.0.0.0 --port 8000


View incidents:

http://localhost:8000/incidents


View HTML report:

http://localhost:8000/incidents/report/{id}

🔬 How It Works (Detection Pipeline)
1. File Walker

Scans repo, excluding:

scanner internal files

rules

CI files

API backend

generated reports

2. Multi-Detector Engine

Runs detectors on each file:

✔ Regex detector
✔ AST detector
✔ Entropy detector
✔ YAML CI-config detector
✔ Dependency analyzer
✔ Git history tamper detection

3. Scoring Engine

Each finding adds score:

Type	Example	Score
Critical	curl	sh
High	eval(), base64 payloads	7
Medium	suspicious token	6
Low	external GitHub action	3
4. Policy Decision
Score < 7   => Allow
Score 7–15 => Warn
Score > 15 => Fail

5. Reporter

CLI output

HTML report

JSON report

Auto-upload to dashboard API

🔍 Why This Tool Is Different (vs Trivy, Semgrep, Gitleaks)
Feature	This Scanner	Trivy	Semgrep	Gitleaks
CI/CD workflow detection	✅	❌	❌	❌
Build tampering detection	✅	❌	❌	❌
Behavior-based detection	✅	❌	⚠️ rules only	❌
Typosquat dependency detection	✅	⚠️	❌	❌
High entropy encoded payloads	✅	❌	❌	❌
Real-time CI build blocking	✅	⚠️	⚠️	❌
Dashboard with incident storage	✅	❌	❌	❌
🎓 Use Cases

Detect malicious PR modifications

Prevent supply-chain injection attacks

Secure GitHub Actions / Jenkins / GitLab pipelines

Audit automation scripts

Monitor developer environments

Protect production release workflows

🛠️ Future Enhancements

AI-powered anomaly detection

SBOM generation (CycloneDX)

Integration with Slack/Teams alerts

Support for GitLab CI, Jenkins, Azure Pipelines

Threat intel feeds for package names

Risk heatmap & dashboard charts

🙌 Contributing

Contributions are welcome!
Feel free to submit issues, PRs, and feature ideas.

📄 License

MIT License.
