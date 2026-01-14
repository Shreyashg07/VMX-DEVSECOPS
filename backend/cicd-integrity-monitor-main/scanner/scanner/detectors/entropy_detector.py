# scanner/scanner/detectors/entropy_detector.py

import math
from typing import List


def _entropy_bytes(data: bytes) -> float:
    """Calculate Shannon entropy of byte sequence."""
    if not data:
        return 0.0

    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1

    ent = 0.0
    length = len(data)

    for count in freq.values():
        p = count / length
        ent -= p * math.log2(p)

    return ent


class EntropyDetector:
    name = "entropy_detector"

    # Tuneable threshold — >= 4.5 usually indicates obfuscation or packed payloads
    THRESHOLD = 4.5

    def detect(self, filepath: str, content: str) -> List[dict]:
        """
        NEW interface supported by ScannerEngine.
        Only scans one file at a time, not the whole repo.
        """

        # Only check entropy for selected file types
        if not filepath.endswith(
            (".py", ".js", ".ts", ".sh", ".bin", ".dat", ".exe", ".dll")
        ):
            return []

        findings = []

        try:
            with open(filepath, "rb") as fh:
                data = fh.read()

            entropy = _entropy_bytes(data)

            if entropy >= self.THRESHOLD:
                findings.append({
                    "detector": self.name,
                    "file": filepath,
                    "id": "high_entropy",
                    "type": "entropy",
                    "score": 7,
                    "description": "High entropy file (possible encoded/obfuscated payload)",
                    "meta": {"entropy": entropy}
                })

        except Exception:
            # Don't break scanning if file unreadable
            return []

        return findings
