# api/app/routes/stats.py
from fastapi import APIRouter, Depends
from typing import Any, Dict
import sqlite3
from datetime import datetime

router = APIRouter()


def get_db():
    """
    Simple sqlite3 connection provider. Adjust path to your DB file if different.
    """
    # use the same DB file your API uses; update path if needed
    conn = sqlite3.connect("integrity.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("/stats", response_model=Dict[str, Any])
def stats(db=Depends(get_db)):
    cur = db.cursor()

    # total incidents
    cur.execute("SELECT COUNT(*) as cnt FROM incidents")
    total = cur.fetchone()["cnt"] or 0

    # failed incidents (action == 'fail')
    cur.execute("SELECT COUNT(*) as cnt FROM incidents WHERE lower(action)='fail'")
    fail = cur.fetchone()["cnt"] or 0

    # average score
    cur.execute("SELECT AVG(score) as avg_score FROM incidents")
    r = cur.fetchone()
    avg_score = float(r["avg_score"]) if r and r["avg_score"] is not None else 0.0

    # last scan timestamp
    cur.execute("SELECT created_at FROM incidents ORDER BY created_at DESC LIMIT 1")
    r = cur.fetchone()
    last_scan = r["created_at"] if r else None

    # severity buckets (adjust thresholds to your policy)
    cur.execute("SELECT COUNT(*) as cnt FROM incidents WHERE score >= 25")
    high = cur.fetchone()["cnt"] or 0

    cur.execute("SELECT COUNT(*) as cnt FROM incidents WHERE score BETWEEN 15 AND 24")
    medium = cur.fetchone()["cnt"] or 0

    cur.execute("SELECT COUNT(*) as cnt FROM incidents WHERE score BETWEEN 1 AND 14")
    low = cur.fetchone()["cnt"] or 0

    # allow / clean
    cur.execute("SELECT COUNT(*) as cnt FROM incidents WHERE lower(action)='allow'")
    allow = cur.fetchone()["cnt"] or 0

    return {
        "total": total,
        "fail": fail,
        "allow": allow,
        "high": high,
        "medium": medium,
        "low": low,
        "avg_score": round(avg_score, 2),
        "last_scan": last_scan,
    }
