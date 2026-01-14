# scanner/scanner/detectors/dependency_detector.py

import json
from typing import List, Dict, Any


class DependencyDetector:
    name = "dependency_detector"

    # package names shorter than this are suspicious (typosquatting)
    SHORT_NAME_THRESHOLD = 2

    # -----------------------------------------------------
    # Helper: Load JSON safely
    # -----------------------------------------------------
    def _load_json(self, filepath: str) -> dict:
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    # -----------------------------------------------------
    # NPM: package.json scanning (single file)
    # -----------------------------------------------------
    def _scan_package_json(self, filepath: str) -> List[Dict[str, Any]]:
        findings = []
        data = self._load_json(filepath)

        deps = data.get("dependencies", {}) or {}
        dev_deps = data.get("devDependencies", {}) or {}

        all_deps = {**deps, **dev_deps}

        for name, version in all_deps.items():

            # 1. short or suspicious names → typosquatting
            if len(name) <= self.SHORT_NAME_THRESHOLD or any(c in name for c in ['$', '%', '#']):
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "suspicious_package_name",
                    "type": "dependency",
                    "score": 6,
                    "description": f"Suspicious or typosquatted dependency name: {name}",
                    "meta": {"package": name, "version": version}
                })

            # 2. URL or git installs
            if isinstance(version, str) and (
                version.startswith("http://") or
                version.startswith("https://") or
                version.startswith("git+")
            ):
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "package_from_url_or_vcs",
                    "type": "dependency",
                    "score": 7,
                    "description": f"Dependency installed from URL/VCS: {name} -> {version}",
                    "meta": {"package": name, "version": version}
                })

            # 3. Loose semver range (^)
            if isinstance(version, str) and version.startswith("^"):
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "loose_semver_range",
                    "type": "dependency",
                    "score": 2,
                    "description": f"Loose version range: {name} -> {version} (use pinned versions)",
                    "meta": {"package": name, "version": version}
                })

        return findings

    # -----------------------------------------------------
    # Python: requirements.txt scanning (single file)
    # -----------------------------------------------------
    def _scan_requirements(self, filepath: str) -> List[Dict[str, Any]]:
        findings = []

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # 1. VCS or URL installs
                    if line.startswith(("http://", "https://", "git+")):
                        findings.append({
                            "detector": self.name,
                            "file": filepath,
                            "id": "vcs_or_url_requirement",
                            "type": "dependency",
                            "score": 7,
                            "description": f"Dependency installed from URL/VCS: {line}",
                            "meta": {"line": line}
                        })

                    # 2. Local path installs
                    if line.startswith(("./", "../", "/")):
                        findings.append({
                            "detector": self.name,
                            "file": filepath,
                            "id": "local_path_install",
                            "type": "dependency",
                            "score": 4,
                            "description": f"Local path dependency install: {line}",
                            "meta": {"line": line}
                        })

        except Exception:
            pass

        return findings

    # -----------------------------------------------------
    # NEW ENGINE API — detect a single file
    # -----------------------------------------------------
    def detect(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        """
        The engine passes *one file at a time* here.
        We choose which detector to run based on filename.
        """

        # scan NPM package.json
        if filepath.endswith("package.json"):
            return self._scan_package_json(filepath)

        # scan Python requirements files
        if filepath.endswith("requirements.txt") or filepath.endswith("requirements-dev.txt"):
            return self._scan_requirements(filepath)

        # not a dependency file → ignore
        return []
