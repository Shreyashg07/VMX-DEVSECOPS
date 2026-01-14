# scanner/scanner/detectors/ast_detector.py
import ast
from typing import List


class ASTDetector:
    name = "ast_detector"

    def _check_node(self, node, filepath):
        findings = []

        # Detect eval/exec/compile/subprocess usage
        if isinstance(node, ast.Call):
            try:
                func = node.func
                fname = ""

                if isinstance(func, ast.Name):
                    fname = func.id
                elif isinstance(func, ast.Attribute):
                    fname = func.attr

                if fname in ("eval", "exec", "compile"):
                    findings.append({
                        "detector": self.name,
                        "file": filepath,
                        "id": "suspicious_eval_exec",
                        "type": "ast",
                        "score": 6,
                        "description": f"Use of {fname}()"
                    })

                if fname in ("system", "popen", "Popen", "call", "check_output"):
                    findings.append({
                        "detector": self.name,
                        "file": filepath,
                        "id": "suspicious_subprocess",
                        "type": "ast",
                        "score": 6,
                        "description": f"Use of subprocess/os system call: {fname}"
                    })

            except Exception:
                pass

        # Detect suspicious imports (urllib, requests)
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name and ("urllib" in n.name or "requests" in n.name):
                    findings.append({
                        "detector": self.name,
                        "file": filepath,
                        "id": "suspicious_import",
                        "type": "ast",
                        "score": 1,
                        "description": f"Import {n.name}"
                    })

        # Detect "from os import ..." or "from sys import ..."
        if isinstance(node, ast.ImportFrom):
            mod = getattr(node, "module", "")
            if mod and ("os" in mod or "sys" in mod):
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "import_from_core",
                    "type": "ast",
                    "score": 0,
                    "description": f"Import from {mod}"
                })

        return findings

    def scan_python_file(self, filepath, content):
        findings = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                findings.extend(self._check_node(node, filepath))
        except Exception:
            # Parsing error -> skip
            pass
        return findings

    # NEW METHOD — required by updated engine
    def detect(self, filepath, content):
        if not filepath.endswith(".py"):
            return []
        return self.scan_python_file(filepath, content)

    # (Old method kept for backward compatibility)
    def scan(self, path) -> List[dict]:
        # Deprecated in new engine — engine now uses detect()
        return []
