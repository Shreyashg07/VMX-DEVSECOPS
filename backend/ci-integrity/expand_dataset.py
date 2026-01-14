import os, re, io, sys, zipfile, requests, shutil, hashlib
from pathlib import Path
from tqdm import tqdm

# --- Repositories to download (owner/repo) ---
REPOS = [
    "swisskyrepo/PayloadsAllTheThings",
    # "carlospolop/hacktricks",  # Commented out (too large)
]

# --- Category mapping keywords (lowercase) ---
CATEGORY_KEYWORDS = {
    "backdoors": ["backdoor", "webshell", "persistence"],
    "ci_attacks": ["jenkins", "gitlab", "github-actions", "ci", "pipeline", "gitlab-ci"],
    "docker_attacks": ["docker", "container", "image", "k8s", "kubernetes"],
    "miners": ["miner", "xmrig", "crypto", "coinhive"],
    "obfuscated": ["obfuscation", "obfuscated", "encoded", "base64", "rot13"],
    "reverse_shells": ["reverse", "reverse-shell", "nc -e", "netcat", "bash -i", "socket"]
}

# --- Allowed extensions ---
ALLOWED_EXT = {".py", ".sh", ".bash", ".yml", ".yaml", ".dockerfile", ".ps1", ".txt", ".md"}

DATA_DIR = Path("data")
TEMP_DIR = Path("temp_repos_zip")
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
for c in CATEGORY_KEYWORDS:
    (DATA_DIR / c).mkdir(parents=True, exist_ok=True)

def safe_filename(name, max_len=120):
    name = re.sub(r"[<>:\"/\\|?*\x00-\x1F]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:max_len]

def classify_text(txt):
    t = txt.lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in t for k in keys):
            return cat
    return None

def fetch_zip(url, out_path, max_mb=100):
    """Download a zip with progress, abort if larger than max_mb."""
    r = requests.get(url, stream=True, timeout=(10, 30))
    total = int(r.headers.get("content-length", 0))
    if total > max_mb * 1024 * 1024:
        print(f"  ⚠️ Skipping {url} (too large: {total/1024/1024:.1f} MB)")
        return None
    bar = tqdm(total=total, unit="B", unit_scale=True, desc=f"Downloading {url}")
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    bar.close()
    return out_path

def process_repo(owner_repo):
    owner, repo = owner_repo.split("/")
    for branch in ("main", "master"):
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        print(f"🔽 {owner_repo} ({branch})")
        try:
            zip_path = TEMP_DIR / f"{repo}-{branch}.zip"
            p = fetch_zip(zip_url, zip_path)
            if not p:
                continue
            z = zipfile.ZipFile(zip_path)
            print(f"  -> Extracting {len(z.namelist())} entries...")
            for info in z.infolist():
                if info.is_dir():
                    continue
                name = info.filename.lower()
                _, ext = os.path.splitext(name)
                if ext not in ALLOWED_EXT and not name.endswith("dockerfile"):
                    continue
                raw = z.read(info.filename)
                try:
                    txt = raw.decode("utf-8", errors="ignore")
                except Exception:
                    txt = ""
                cat = classify_text(txt) or classify_text(name)
                if not cat:
                    continue
                short = safe_filename(Path(info.filename).name)
                h = hashlib.sha1(raw).hexdigest()[:10]
                dest = DATA_DIR / cat / f"{short}_{h}{Path(info.filename).suffix}"
                if not dest.exists():
                    dest.write_bytes(raw)
            print(f"  ✅ Done: {owner_repo}")
            return True
        except Exception as e:
            print(f"  ⚠️ Error {owner_repo}: {e}")
    return False

def main():
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    for r in REPOS:
        process_repo(r)
    print("✅ Dataset expansion complete! You can now run:")
    print("   python train_embeddings.py")

if __name__ == "__main__":
    main()
