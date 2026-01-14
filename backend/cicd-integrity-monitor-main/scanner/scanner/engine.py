# scanner/scanner/engine.py

import os
import traceback

from scanner.scanner.policy import PolicyEngine
from scanner.scanner.alerts import AlertManager   # <-- ADDED

from scanner.scanner.detectors.regex_detector import RegexDetector
from scanner.scanner.detectors.ast_detector import ASTDetector
from scanner.scanner.detectors.entropy_detector import EntropyDetector
from scanner.scanner.detectors.yaml_detector import YAMLDetector
from scanner.scanner.detectors.dependency_detector import DependencyDetector
from scanner.scanner.detectors.ci_config_detector import CIConfigDetector
from scanner.scanner.detectors.signature_detector import SignatureDetector


class ScannerEngine:

    IGNORE_DIRS = {
        "rules", "policies", "scan_reports", "api",
        ".github", ".git", "__pycache__", ".vscode",
        ".idea", "docker", "venv", "env",
        "node_modules", "examples", "scanner", "reports", "anomaly"
    }

    IGNORE_FILES = {
        "scan_report.json",
        "scan_report.html",
        "README.md"
    }

    IGNORE_EXTENSIONS = {
        ".lock", ".db", ".sqlite",
        ".png", ".jpg", ".jpeg", ".gif",
        ".ico", ".svg"
    }

    def __init__(self, policy_path=None):
        self.policy = PolicyEngine(policy_path)
        cwd = os.getcwd()

        # Alert manager (Discord + Email)
        self.alerts = AlertManager({         # <-- ADDED
            "DISCORD_WEBHOOK": os.getenv("DISCORD_WEBHOOK"),
            "SMTP_HOST": os.getenv("SMTP_HOST"),
            "SMTP_PORT": os.getenv("SMTP_PORT"),
            "SMTP_USER": os.getenv("SMTP_USER"),
            "SMTP_PASS": os.getenv("SMTP_PASS"),
            "EMAIL_FROM": os.getenv("EMAIL_FROM"),
            "EMAIL_TO": os.getenv("EMAIL_TO"),
        })

        # Correct detector list (NO ML here)
        self.detectors = [
            SignatureDetector(signature_path=os.path.join(cwd, "rules", "signatures.json")),
            RegexDetector(rules_path=os.path.join(cwd, "rules", "suspicious_patterns.json")),
            ASTDetector(),
            EntropyDetector(),
            YAMLDetector(),
            DependencyDetector(),
            CIConfigDetector(),
        ]

    def _should_ignore(self, filepath):
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        return filename in self.IGNORE_FILES or ext in self.IGNORE_EXTENSIONS

    def _should_ignore_dir(self, dirpath):
        clean = dirpath.replace("\\", "/")
        return any(clean.endswith(d) or f"/{d}/" in clean for d in self.IGNORE_DIRS)

    def scan_path(self, path):
        findings = []
        abs_path = os.path.abspath(path)
        scanned_files = []

        # Walk the filesystem
        for root, dirs, files in os.walk(abs_path):

            dirs[:] = [d for d in dirs if not self._should_ignore_dir(os.path.join(root, d))]

            for file in files:
                filepath = os.path.join(root, file)

                if self._should_ignore(filepath):
                    continue

                scanned_files.append(filepath)

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    continue

                # Run traditional detectors
                for detector in self.detectors:
                    try:
                        results = detector.detect(filepath, content)
                        if results:
                            findings.extend(results)
                    except Exception as e:
                        findings.append({
                            "detector": detector.__class__.__name__,
                            "file": filepath,
                            "id": "detector_error",
                            "type": "error",
                            "score": 0,
                            "description": f"Detector crashed: {str(e)}"
                        })

        # ---------------------------
        # WHITELIST + SCORING
        # ---------------------------

        filtered = self.policy.filter_whitelisted(findings)   # <-- already built-in
        score = self.policy.score_findings(filtered)
        action = self.policy.get_action(score)

        report = {
            "meta": {"path": abs_path},
            "findings": filtered,
            "raw_findings": findings,
            "score": score,
            "action": action,
        }

        # ---------------------------
        # ALERTING (Discord + Email)
        # ---------------------------
        try:
            alert_result = self.alerts.send_alert(report)
            # Debug optional:
            # print("Alert result:", alert_result)
        except Exception as e:
            print("Alert error:", str(e))
            traceback.print_exc()

        return report
