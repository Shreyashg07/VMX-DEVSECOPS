from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.types import JSON
from api.app.db import Base
import datetime

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    scanned_path = Column(String, nullable=True)

    score = Column(Integer, nullable=False)
    action = Column(String, nullable=False)

    # JSON list of findings
    findings = Column(JSON, nullable=False)

    # Full HTML report
    report_html = Column(Text, nullable=True)

    # FIX: "metadata" is RESERVED — renamed to extra_metadata
    extra_metadata = Column(JSON, nullable=True)
