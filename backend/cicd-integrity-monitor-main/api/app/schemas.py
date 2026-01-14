from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Finding(BaseModel):
    detector: str
    file: str
    id: str
    type: str
    score: int
    description: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class IncidentCreate(BaseModel):
    meta: Optional[Dict[str, Any]] = None
    findings: List[Finding]
    score: int
    action: str
    report_html: Optional[str] = None

class IncidentOut(BaseModel):
    id: int
    created_at: str
    scanned_path: Optional[str]
    score: int
    action: str
    findings: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
