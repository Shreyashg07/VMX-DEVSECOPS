"""
Enhanced training script for PyGuard
------------------------------------
- Walks data/* or malicious_samples/* subfolders (categories)
- Computes embeddings per sample using sentence-transformers
- Saves a pickled DB at embeddings/malicious.pkl

Output structure (pickled list of dicts):
[
  {
    "category": "backdoors",
    "path": "data/backdoors/backdoor_1.py",
    "text_snippet": "<first 1200 chars>",
    "embedding": numpy.array([...], dtype=float32)
  },
  ...
]
"""

import os
import pickle
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from utils.file_reader import read_file_text
import numpy as np

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
# Prefer 'data' directory, fallback to 'malicious_samples'
if os.path.isdir("data"):
    MAL_DIR = "data"
elif os.path.isdir("malicious_samples"):
    MAL_DIR = "malicious_samples"
else:
    MAL_DIR = None

OUT_DIR = "embeddings"
OUT_FILE = os.path.join(OUT_DIR, "malicious.pkl")
MODEL_NAME = os.environ.get("PYGUARD_MODEL", "all-MiniLM-L6-v2")
MAX_SNIPPET = 1200  # chars

# ----------------------------------------------------------------------
def gather_samples_by_category(root_dir):
    samples = []
    counts = defaultdict(int)
    for category in sorted(os.listdir(root_dir)):
        cat_path = os.path.join(root_dir, category)
        if not os.path.isdir(cat_path) or category.startswith("."):
            continue
        for fname in sorted(os.listdir(cat_path)):
            if fname.startswith("."):
                continue
            fpath = os.path.join(cat_path, fname)
            text = read_file_text(fpath)
            if not text:
                continue
            samples.append({
                "category": category,
                "path": fpath,
                "text": text
            })
            counts[category] += 1
    return samples, counts

# ----------------------------------------------------------------------
def main():
    if not MAL_DIR:
        print("[train] ❌ Error: no 'data/' or 'malicious_samples/' directory found.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[train] Scanning directory: {os.path.abspath(MAL_DIR)}")
    print(f"[train] Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    samples, counts = gather_samples_by_category(MAL_DIR)
    total = len(samples)
    print(f"[train] Found total {total} samples across categories:")
    for c, n in counts.items():
        print(f"  - {c}: {n}")

    if total == 0:
        print("[train] ⚠️ No samples to embed. Exiting.")
        return

    texts = [s["text"] for s in samples]

    # Compute embeddings (batched)
    print("[train] Computing embeddings (this may take a moment)...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Build database
    db = []
    for s, emb in zip(samples, embeddings):
        db.append({
            "category": s["category"],
            "path": s["path"],
            "text_snippet": s["text"][:MAX_SNIPPET],
            "embedding": emb.astype("float32")  # smaller, portable
        })

    # Save embeddings
    with open(OUT_FILE, "wb") as f:
        pickle.dump(db, f)

    print(f"[train] ✅ Saved {len(db)} embeddings to {OUT_FILE}")

    # Write summary index
    idx_file = os.path.join(OUT_DIR, "index.txt")
    with open(idx_file, "w", encoding="utf-8") as fi:
        fi.write(f"model: {MODEL_NAME}\n")
        fi.write(f"total_samples: {len(db)}\n")
        for c, n in counts.items():
            fi.write(f"{c}: {n}\n")
    print(f"[train] 🧾 Wrote summary to {idx_file}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
