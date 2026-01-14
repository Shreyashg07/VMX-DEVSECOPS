# scanner/scanner/policy.py
import json
import os
import fnmatch
import re

from typing import List, Dict, Any


class PolicyEngine:
    def __init__(self, policy_path=None):
        # default policy path
        self.policy_path = policy_path or os.path.join(
            os.getcwd(), "policies", "default_policy.json"
        )
        self.policy = self._load_policy()

    def _load_policy(self) -> Dict[str, Any]:
        try:
            with open(self.policy_path, "r", encoding="utf-8") as fh:
                p = json.load(fh)
        except Exception:
            # fallback policy
            p = {
                "whitelist_files": [],
                "whitelist_rules": [],
                "whitelist_detectors": [],
                "whitelist_patterns": [],
                "whitelist_enabled": True,
            }

        # compile regex patterns
        patterns = p.get("whitelist_patterns", [])
        p["_compiled_patterns"] = [re.compile(x) for x in patterns if x]

        return p

    def reload(self):
        self.policy = self._load_policy()

    # ------------------------------------------------------------------
    # NEW: More accurate static rule scoring (raw)
    # ------------------------------------------------------------------
    def score_findings(self, findings: List[dict]) -> int:
        total = 0
        for f in findings:
            total += int(f.get("score", 0) or 0)
        return int(total)

    # ------------------------------------------------------------------
    # NEW: Risk action thresholds
    # These now work with your weighted risk score (0–100)
    # ------------------------------------------------------------------
    def get_action(self, risk_score: float) -> str:
        if risk_score >= 60:
            return "fail"
        if risk_score >= 30:
            return "warn"
        return "allow"

    # ------------------------------------------------------------------
    # -------------------- WHITELIST SUPPORT ----------------------------
    # ------------------------------------------------------------------
    def is_file_whitelisted(self, file_path: str) -> bool:
        if not file_path:
            return False

        # filename glob patterns
        for pattern in self.policy.get("whitelist_files", []):
            try:
                if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
                    os.path.normpath(file_path), pattern
                ):
                    return True
            except Exception:
                continue

        # regex patterns
        for cre in self.policy.get("_compiled_patterns", []):
            if cre.search(file_path):
                return True

        return False

    def is_rule_whitelisted(self, rule_id: str) -> bool:
        if not rule_id:
            return False
        return rule_id in self.policy.get("whitelist_rules", [])

    def is_detector_whitelisted(self, detector_name: str) -> bool:
        if not detector_name:
            return False
        return detector_name in self.policy.get("whitelist_detectors", [])

    # ------------------------------------------------------------------
    # NEW: apply whitelist before scoring
    # ------------------------------------------------------------------
    def filter_whitelisted(self, findings: List[dict]) -> List[dict]:
        if not self.policy.get("whitelist_enabled", True):
            return findings

        output = []

        for f in findings:
            file_path = f.get("file") or f.get("filepath") or ""
            rule_id = f.get("id") or ""
            detector = f.get("detector") or ""

            # skip if whitelisted
            if self.is_detector_whitelisted(detector):
                continue
            if self.is_rule_whitelisted(rule_id):
                continue
            if self.is_file_whitelisted(file_path):
                continue

            output.append(f)

        return output
