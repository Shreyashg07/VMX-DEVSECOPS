# api/app/routes/timeline.py
from fastapi import APIRouter, Depends
from typing import Any, Dict, List
import sqlite3
from datetime import datetime, timedelta

router = APIRouter()


def get_db():
    # adjust DB path if your DB is elsewhere
    conn = sqlite3.connect("integrity.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@router.get("/timeline", response_model=List[Dict[str, Any]])
def timeline(days: int = 30, db=Depends(get_db)):
    """
    Returns an array of objects, one per date (last `days` days),
    each containing counts for high, medium, low incidents.
    Example:
    [
      {"date": "2025-11-01", "high": 2, "medium": 1, "low": 0},
      ...
    ]
    """
    cur = db.cursor()

    # Compute date range (inclusive)
    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)

    # SQLite: use date(created_at) if created_at is ISO string; adjust if integer ts
    sql = """
    SELECT date(created_at) as day,
           SUM(CASE WHEN score >= 25 THEN 1 ELSE 0 END) as high,
           SUM(CASE WHEN score BETWEEN 15 AND 24 THEN 1 ELSE 0 END) as medium,
           SUM(CASE WHEN score BETWEEN 1 AND 14 THEN 1 ELSE 0 END) as low
    FROM incidents
    WHERE date(created_at) BETWEEN ? AND ?
    GROUP BY day
    ORDER BY day ASC
    """

    cur.execute(sql, (start.isoformat(), end.isoformat()))
    rows = cur.fetchall()

    # Convert rows to dict and fill missing dates with zeros
    counts_by_day = {r["day"]: {"high": r["high"], "medium": r["medium"], "low": r["low"]} for r in rows}

    out = []
    d = start
    while d <= end:
        key = d.isoformat()
        entry = counts_by_day.get(key, {"high": 0, "medium": 0, "low": 0})
        out.append({"date": key, "high": int(entry["high"]), "medium": int(entry["medium"]), "low": int(entry["low"])})
        d += timedelta(days=1)

    return out
