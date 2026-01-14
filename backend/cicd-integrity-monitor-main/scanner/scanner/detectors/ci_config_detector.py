# scanner/scanner/detectors/ci_config_detector.py

import re
from typing import List, Dict, Any
from scanner.scanner.utils import git_utils

# suspicious patterns: curl/wget piped to shell
SUSPICIOUS_CMD_RE = re.compile(r"(curl|wget).*\|.*(sh|bash)", re.IGNORECASE)

# third-party GitHub actions (heuristic)
EXTERNAL_ACTION_RE = re.compile(
    r"uses:\s*[-\w./@]+/(?!actions/)[\w.@/-]+",
    re.IGNORECASE
)


class CIConfigDetector:
    name = "ci_config_detector"

    # ---------------------------------------------------------
    # Scan a single CI file (GitHub Actions, GitLab CI, Jenkins)
    # ---------------------------------------------------------
    def _scan_ci_file(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        findings = []

        # 1. Detect curl|wget → shell (supply chain attacks)
        if SUSPICIOUS_CMD_RE.search(content):
            findings.append({
                "detector": self.name,
                "file": filepath,
                "id": "curl_pipe_sh",
                "type": "ci",
                "score": 10,
                "description": "Found `curl | sh` or `wget | bash` in CI config"
            })

        # 2. Detect external GitHub actions
        for match in EXTERNAL_ACTION_RE.finditer(content):
            findings.append({
                "detector": self.name,
                "file": filepath,
                "id": "external_action_used",
                "type": "ci",
                "score": 3,
                "description": f"Third-party GitHub Action referenced: {match.group(0)}"
            })

        return findings

    # ---------------------------------------------------------
    # Git diff scanning (optional)
    # ---------------------------------------------------------
    def _scan_git_diff(self, repo_path: str) -> List[Dict[str, Any]]:
        findings = []

        try:
            changed = git_utils.changed_files_between_commits(
                base="HEAD~1", head="HEAD", path=repo_path
            )
        except Exception:
            return findings  # Not a git repo or no commits

        for f in changed:
            # Only CI files
            if not (f.startswith(".github/") or
                    f.endswith(("Jenkinsfile", ".gitlab-ci.yml", ".yaml", ".yml"))):
                continue

            try:
                diff = git_utils.file_diff("HEAD~1", "HEAD", f, repo_path=repo_path)
            except Exception:
                continue

            for line in diff.splitlines():
                if not line.startswith("+"):
                    continue

                # detect newly added suspicious CI steps
                if SUSPICIOUS_CMD_RE.search(line):
                    findings.append({
                        "detector": self.name,
                        "file": f,
                        "id": "new_ci_suspicious_step",
                        "type": "ci",
                        "score": 10,
                        "description": f"Suspicious new CI step added in {f}",
                        "meta": {"line": line}
                    })

                # detect newly added third-party GitHub Actions
                if EXTERNAL_ACTION_RE.search(line):
                    findings.append({
                        "detector": self.name,
                        "file": f,
                        "id": "new_external_action",
                        "type": "ci",
                        "score": 3,
                        "description": f"New external GitHub Action referenced in {f}",
                        "meta": {"line": line}
                    })

        return findings

    # ---------------------------------------------------------
    # NEW ENGINE API — detect() = scan ONE file only
    # ---------------------------------------------------------
    def detect(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        results = []

        # Only scan CI-related file types
        is_ci_file = (
            "/.github/workflows/" in filepath.replace("\\", "/") or
            filepath.lower().endswith(("jenkinsfile", ".gitlab-ci.yml", ".yml", ".yaml"))
        )

        if is_ci_file:
            results.extend(self._scan_ci_file(filepath, content))

        # Also attempt Git diff scanning (only once)
        repo_root = git_utils.repo_root(filepath)
        if repo_root:
            results.extend(self._scan_git_diff(repo_root))

        return results
