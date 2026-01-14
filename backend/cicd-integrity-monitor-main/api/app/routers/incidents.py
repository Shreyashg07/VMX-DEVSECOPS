from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from api.app.schemas import IncidentCreate, IncidentOut
from api.app.db import SessionLocal
from api.app import models

router = APIRouter()


# ------------------------
# DB Session
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------
# Create Incident (CI upload)
# ------------------------
@router.post("/", response_model=IncidentOut)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):

    inc = models.Incident(
        scanned_path=payload.meta.get("path") if payload.meta else None,
        score=payload.score,
        action=payload.action,
        findings=[f.dict() if hasattr(f, "dict") else f for f in payload.findings],
        report_html=payload.report_html,
        extra_metadata=payload.meta
    )

    db.add(inc)
    db.commit()
    db.refresh(inc)

    return {
        "id": inc.id,
        "created_at": inc.created_at.isoformat(),
        "scanned_path": inc.scanned_path,
        "score": inc.score,
        "action": inc.action,
        "findings": inc.findings,
        "metadata": inc.extra_metadata,
    }


# ------------------------
# List Incidents (SORT + FILTER + PAGINATION)
# ------------------------
@router.get("/", response_model=list[IncidentOut])
def list_incidents(
    db: Session = Depends(get_db),

    # Pagination
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),

    # Filters
    search: str | None = None,
    score_min: int | None = None,
    score_max: int | None = None,

    # Sorting
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc")
):

    # allowed sortable columns
    sortable_columns = {
        "id": models.Incident.id,
        "score": models.Incident.score,
        "created_at": models.Incident.created_at,
        "action": models.Incident.action,
    }

    sort_col = sortable_columns.get(sort_by, models.Incident.created_at)
    sort_order = sort_col.asc() if sort_dir == "asc" else sort_col.desc()

    q = db.query(models.Incident)

    # Search
    if search:
        q = q.filter(models.Incident.scanned_path.ilike(f"%{search}%"))

    # Score range filtering
    if score_min is not None:
        q = q.filter(models.Incident.score >= score_min)
    if score_max is not None:
        q = q.filter(models.Incident.score <= score_max)

    # Final SQL ordering
    q = q.order_by(sort_order)

    # Pagination
    offset = (page - 1) * limit
    rows = q.offset(offset).limit(limit).all()

    # Format output
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "scanned_path": r.scanned_path,
            "score": r.score,
            "action": r.action,
            "findings": r.findings,
            "metadata": r.extra_metadata,
        })

    return out


# ------------------------
# Get Single Incident
# ------------------------
@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Incident).filter(models.Incident.id == incident_id).first()

    if not r:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "id": r.id,
        "created_at": r.created_at.isoformat(),
        "scanned_path": r.scanned_path,
        "score": r.score,
        "action": r.action,
        "findings": r.findings,
        "metadata": r.extra_metadata,
    }


# ------------------------
# HTML Report Endpoint
# ------------------------
@router.get("/report/{incident_id}", response_class=HTMLResponse)
def get_report(incident_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Incident).filter(models.Incident.id == incident_id).first()

    if not r or not r.report_html:
        raise HTTPException(status_code=404, detail="Report not found")

    return HTMLResponse(content=r.report_html, status_code=200)
