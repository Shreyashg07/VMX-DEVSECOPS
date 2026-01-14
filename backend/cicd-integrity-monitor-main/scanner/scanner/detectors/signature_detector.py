import hashlib
import json
import re
from typing import List, Dict, Any


class SignatureDetector:
    name = "signature_detector"

    def __init__(self, signature_path):
        try:
            with open(signature_path, "r", encoding="utf-8") as fh:
                self.signatures = json.load(fh)
        except Exception:
            self.signatures = {
                "hashes": [],
                "strings": [],
                "regex": [],
                "urls": []
            }

        # compile regex signatures
        self.regex_rules = [
            re.compile(p, re.IGNORECASE) for p in self.signatures.get("regex", [])
        ]

    # -----------------------------
    # Hash file contents
    # -----------------------------
    def _file_hash(self, filepath):
        try:
            sha = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(4096):
                    sha.update(chunk)
            return sha.hexdigest()
        except:
            return None

    # -----------------------------
    # Main detector API
    # -----------------------------
    def detect(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        findings = []

        # ----------------------------------------
        # 1. Check file hash
        # ----------------------------------------
        fh = self._file_hash(filepath)
        if fh and fh.lower() in [h.lower() for h in self.signatures.get("hashes", [])]:
            findings.append({
                "detector": self.name,
                "file": filepath,
                "id": "malicious_file_hash",
                "score": 10,
                "type": "signature",
                "description": f"File hash matches known malicious signature: {fh}"
            })

        # ----------------------------------------
        # 2. Check for suspicious strings
        # ----------------------------------------
        for sig in self.signatures.get("strings", []):
            if sig.lower() in content.lower():
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "malicious_string_match",
                    "score": 8,
                    "type": "signature",
                    "description": f"Matched signature string: {sig}"
                })

        # ----------------------------------------
        # 3. Regex signatures
        # ----------------------------------------
        for rule in self.regex_rules:
            if rule.search(content):
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "malicious_regex_match",
                    "score": 9,
                    "type": "signature",
                    "description": f"Matched signature regex: {rule.pattern}"
                })

        # ----------------------------------------
        # 4. Malicious URL scanning
        # ----------------------------------------
        for url in self.signatures.get("urls", []):
            if url.lower() in content.lower():
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "malicious_url_match",
                    "score": 8,
                    "type": "signature",
                    "description": f"Matched malicious URL: {url}"
                })

        return findings
