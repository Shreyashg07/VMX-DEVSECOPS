# models.py
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# =========================
# USER MODEL
# =========================
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default="dev")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pipelines = db.relationship(
        "Pipeline",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =========================
# PIPELINE MODEL
# =========================
class Pipeline(db.Model):
    __tablename__ = "pipeline"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    config_json = db.Column(db.Text, nullable=False)

    # 🔐 OWNER (CRITICAL)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    builds = db.relationship(
        "Build",
        backref="pipeline",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ✅ REQUIRED BY API
    def to_dict(self, include_stats=False):
        try:
            config = json.loads(self.config_json or "{}")
        except Exception:
            config = {}

        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "config_json": config,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_stats:
            data["stats"] = {
                "queued": Build.query.filter_by(pipeline_id=self.id, status="queued").count(),
                "running": Build.query.filter_by(pipeline_id=self.id, status="running").count(),
                "success": Build.query.filter_by(pipeline_id=self.id, status="success").count(),
                "failed": Build.query.filter_by(pipeline_id=self.id, status="failed").count(),
            }

        return data


# =========================
# BUILD MODEL
# =========================
class Build(db.Model):
    __tablename__ = "build"

    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey("pipeline.id"), nullable=False)
    status = db.Column(db.String(32), default="queued")
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    logs = db.relationship(
        "BuildLog",
        backref="build",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        duration = None
        if self.started_at and self.finished_at:
            duration = int((self.finished_at - self.started_at).total_seconds())

        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": duration,
        }


# =========================
# BUILD LOG MODEL
# =========================
class BuildLog(db.Model):
    __tablename__ = "build_log"

    id = db.Column(db.Integer, primary_key=True)
    build_id = db.Column(db.Integer, db.ForeignKey("build.id"), nullable=False)
    step_index = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.Text, nullable=False)
