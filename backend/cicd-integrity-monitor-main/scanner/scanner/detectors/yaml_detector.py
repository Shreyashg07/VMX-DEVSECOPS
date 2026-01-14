# scanner/scanner/detectors/yaml_detector.py

import re
import yaml
from typing import List, Dict, Any


class YAMLDetector:
    name = "yaml_detector"

    # Raw suspicious patterns
    SUSPICIOUS_CMD_PATTERN = re.compile(r"(curl|wget).*\|.*(sh|bash)", re.IGNORECASE)
    SECRET_PATTERN = re.compile(
        r"(PASSWORD|SECRET|TOKEN|API_KEY|ACCESS_KEY|PRIVATE_KEY)",
        re.IGNORECASE
    )

    # ---------------------------------------------------------
    # Scan YAML content (single file)
    # ---------------------------------------------------------
    def _scan_yaml_file(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        findings = []

        # =====================================================
        # 1) RAW TEXT CHECKS (Before YAML parsing)
        # =====================================================

        # Detect curl|sh patterns in CI steps
        if self.SUSPICIOUS_CMD_PATTERN.search(content):
            findings.append({
                "detector": self.name,
                "file": filepath,
                "id": "curl_pipe_sh",
                "type": "yaml",
                "score": 10,
                "description": "Found `curl | sh` pattern in YAML"
            })

        # Detect secret-like keywords
        if self.SECRET_PATTERN.search(content):
            findings.append({
                "detector": self.name,
                "file": filepath,
                "id": "possible_secret_in_yaml",
                "type": "yaml",
                "score": 5,
                "description": "Possible secret-like words in YAML"
            })

        # =====================================================
        # 2) YAML STRUCTURE CHECKS
        # =====================================================
        try:
            parsed = yaml.safe_load(content)
        except Exception:
            return findings  # YAML parse failed → skip structured checks

        if not isinstance(parsed, dict):
            return findings

        # GitHub Actions / GitLab CI patterns:
        jobs = (
            parsed.get("jobs") or      # GitHub Actions
            parsed.get("stages") or    # GitLab
            parsed.get("pipelines") or
            {}
        )

        if isinstance(jobs, dict):
            for job_name, job_def in jobs.items():
                if not isinstance(job_def, dict):
                    continue

                steps = job_def.get("steps")
                if steps and isinstance(steps, list):
                    for step in steps:
                        if not isinstance(step, dict):
                            continue

                        run = step.get("run", "")
                        if run and isinstance(run, str):
                            if self.SUSPICIOUS_CMD_PATTERN.search(run):
                                findings.append({
                                    "detector": self.name,
                                    "file": filepath,
                                    "id": "ci_step_curl_pipe_sh",
                                    "type": "yaml",
                                    "score": 10,
                                    "description": f"CI job '{job_name}' runs curl|sh",
                                })

        return findings

    # ---------------------------------------------------------
    # NEW ENGINE API — detect() = scan ONE FILE only
    # ---------------------------------------------------------
    def detect(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        # Only scan CI-related YAML files
        is_yaml = filepath.endswith((".yml", ".yaml"))
        is_ci = (
            "/.github/workflows/" in filepath.replace("\\", "/") or
            filepath.endswith(".gitlab-ci.yml") or
            filepath.lower().startswith("jenkinsfile")
        )

        if not (is_yaml or is_ci):
            return []

        return self._scan_yaml_file(filepath, content)
