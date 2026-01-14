# scanner/scanner/detectors/regex_detector.py

import os
import re
import json
from typing import List

class RegexDetector:
    name = "regex_detector"

    def __init__(self, rules_path="rules/suspicious_patterns.json"):
        self.rules_path = rules_path
        self.rules = self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # -----------------------------
    # NEW: detect() method (used by engine)
    # -----------------------------
    def detect(self, filepath, content):
        findings = []

        # Only scan text-like files
        if not filepath.endswith((
            ".py", ".js", ".ts", ".sh",
            ".yaml", ".yml", ".json",
            ".md", ".txt"
        )):
            return findings

        for rule in self.rules:
            pattern = rule.get("pattern")
            try:
                if re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE):
                    findings.append({
                        "detector": self.name,
                        "file": filepath,
                        "id": rule.get("id"),
                        "type": rule.get("type", "regex"),
                        "score": rule.get("score", 5),
                        "description": rule.get("description", "")
                    })
            except re.error:
                # invalid regex → skip safely
                continue

        return findings

    # -----------------------------
    # OLD scan() method is kept for compatibility (not used by engine)
    # -----------------------------
    def scan(self, path) -> List[dict]:
        findings = []
        for root, _, files in os.walk(path):
            for fname in files:
                filepath = os.path.join(root, fname)
                if filepath.endswith((
                    ".py", ".js", ".ts", ".sh",
                    ".yaml", ".yml", ".json",
                    ".md", ".txt"
                )):
                    findings.extend(self.scan_file(filepath))
        return findings

    # -----------------------------
    # OLD file scanner (still usable)
    # -----------------------------
    def scan_file(self, filepath):
        findings = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except Exception:
            return findings

        return self.detect(filepath, content)
