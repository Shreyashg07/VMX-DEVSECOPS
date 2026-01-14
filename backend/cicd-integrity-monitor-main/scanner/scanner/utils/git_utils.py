# scanner/scanner/utils/git_utils.py
import subprocess
import os
from typing import List, Optional, Tuple

def repo_root(path: str = ".") -> Optional[str]:
    try:
        root = subprocess.check_output(["git", "-C", path, "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL)
        return root.decode().strip()
    except Exception:
        return None

def changed_files_between_commits(base: str = "HEAD~1", head: str = "HEAD", path: str = ".") -> List[str]:
    try:
        out = subprocess.check_output(["git", "-C", path, "diff", "--name-only", base, head], stderr=subprocess.DEVNULL)
        return [p.strip() for p in out.decode().splitlines() if p.strip()]
    except Exception:
        return []

def file_diff(base: str, head: str, file_path: str, repo_path: str = ".") -> str:
    try:
        out = subprocess.check_output(["git", "-C", repo_path, "diff", f"{base}..{head}", "--", file_path], stderr=subprocess.DEVNULL)
        return out.decode(errors="ignore")
    except Exception:
        return ""

def last_commit_info(file_path: str, repo_path: str = ".") -> Tuple[str, str]:
    """
    Returns (commit_hash, author_email) for last commit that touched file_path
    """
    try:
        out = subprocess.check_output(["git", "-C", repo_path, "log", "-n", "1", "--pretty=format:%H%n%ae", "--", file_path], stderr=subprocess.DEVNULL)
        lines = out.decode().splitlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()
    except Exception:
        pass
    return ("", "")
