
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import json
from datetime import datetime, timezone
from typing import Optional
from collections import Counter
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

from models import db, Pipeline, Build, BuildLog, User
from utils.build_runner import run_build_thread

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
from flask_jwt_extended import verify_jwt_in_request

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import disconnect

@socketio.on("connect")
def socket_connect(auth):
    print("🔌 Socket connect attempt")

    # auth comes from client: io(url, { auth: { token: "..." } })
    token = auth.get("token") if auth else None

    if not token:
        print("❌ No token provided, disconnecting")
        disconnect()
        return

    try:
        decoded = decode_token(token)
        user_id = decoded["sub"]
        print(f"✅ Socket authenticated for user {user_id}")

    except Exception as e:
        print("❌ Invalid token:", e)
        disconnect()




def find_latest_json_report(reports_dir: str) -> Optional[str]:
    """Return path to latest .json file in reports dir."""
    if not os.path.isdir(reports_dir):
        return None
    json_files = [
        os.path.join(reports_dir, f)
        for f in os.listdir(reports_dir)
        if f.lower().endswith(".json")
    ]
    if not json_files:
        return None
    json_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return json_files[0]


def create_app():
    app = Flask(__name__, static_folder=None)
    CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True,
    )

    



    # ============================
    # DB + JWT Setup
    # ============================
    instance_dir = os.path.join(os.path.dirname(__file__), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    db_path = os.path.join(instance_dir, "pipeline.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}?check_same_thread=False"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret"

    db.init_app(app)
    JWTManager(app)
    socketio.init_app(app, cors_allowed_origins="*")
    app.socketio = socketio

    with app.app_context():
        db.create_all()
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.json

        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "User exists"}), 409
        user = User(
            username=data["username"],
            email=data.get("email"),
            password=generate_password_hash(data["password"])
    )
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created"}), 201
    @app.route("/api/me", methods=["GET"])
    @jwt_required()
    def me():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"user": None}), 404

        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        })
    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.json
        user = User.query.filter_by(username=data["username"]).first()

        if not user or not check_password_hash(user.password, data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=str(user.id))


        return jsonify({"access_token": token})

    # ============================
    # PIPELINE ROUTES
    # ============================
    @app.route("/api/pipelines", methods=["GET"])
    @jwt_required()
    def get_pipelines():
        user_id = get_jwt_identity()

        pipelines = []
        for p in Pipeline.query.filter_by(user_id=user_id).all():
            last_build = (
                Build.query.filter_by(pipeline_id=p.id)
                .order_by(Build.id.desc())
                .first()
            )

            status = "unknown"
            runtime = "N/A"

            if last_build:
                status = last_build.status or "unknown"
                if last_build.started_at:
                    try:
                        end_time = last_build.finished_at or datetime.now(timezone.utc)
                        start_time = last_build.started_at
                        if start_time.tzinfo is None:
                            start_time = start_time.replace(tzinfo=timezone.utc)
                        if end_time.tzinfo is None:
                            end_time = end_time.replace(tzinfo=timezone.utc)

                        runtime_min = int((end_time - start_time).total_seconds() / 60)
                        runtime = f"{runtime_min} min"
                    except Exception as e:
                        print(f"⚠️ Runtime calc error for {p.name}: {e}")

            pipelines.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": status,
                "runtime": runtime,
            })

        return jsonify(pipelines)

    # ✅ GET SINGLE PIPELINE DETAIL
    @app.route("/api/pipelines/<int:pipeline_id>", methods=["GET"])
    @jwt_required()
    def get_pipeline_detail(pipeline_id):
        user_id = get_jwt_identity()

        pipeline = Pipeline.query.filter_by(
            id=pipeline_id,
            user_id=user_id
        ).first_or_404()

        builds = (
            Build.query.filter_by(pipeline_id=pipeline_id)
            .order_by(Build.id.desc())
            .limit(10)
            .all()
        )

        history = []
        for b in builds:
            duration = None
            if b.started_at and b.finished_at:
                start_time = b.started_at
                end_time = b.finished_at
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)
                duration = f"{int((end_time - start_time).total_seconds() // 60)} min"

            history.append({
                "id": b.id,
                "date": b.started_at.isoformat() if b.started_at else None,
                "status": b.status,
                "duration": duration
            })

        logs = []
        if builds:
            last_build = builds[0]
            for log in BuildLog.query.filter_by(build_id=last_build.id).order_by(BuildLog.id.asc()).all():
                logs.append(log.text)

        return jsonify({
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "status": builds[0].status if builds else "idle",
            "last_run": builds[0].started_at.isoformat() if builds else None,
            "logs": logs,
            "history": history
        })

    @app.route("/api/pipelines", methods=["POST"])
    @jwt_required()
    def create_pipeline():
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        pipeline = Pipeline(
            name=data["name"],
            description=data.get("description", ""),
            config_json=json.dumps(data["config_json"]),
            user_id=user_id               # ✅ OWNER SET HERE
        )
        db.session.add(pipeline)
        db.session.commit()
        return jsonify(pipeline.to_dict()), 201
    
    @app.route("/api/pipelines/<int:pipeline_id>/run", methods=["POST"])
    @jwt_required()
    def run_pipeline(pipeline_id):
        user_id = get_jwt_identity()

        pipeline = Pipeline.query.filter_by(
            id=pipeline_id,
            user_id=user_id
        ).first_or_404()


        build = Build(
            pipeline_id=pipeline.id,
            status="queued",
            started_at=datetime.now(timezone.utc),
        )
        db.session.add(build)
        db.session.commit()

        socketio.emit("build_status_update", {
            "pipeline_id": pipeline.id,
            "build_id": build.id,
            "status": "queued"
        })

        socketio.start_background_task(
            run_build_thread,
            build.id,
            pipeline.config_json,
            app,
            socketio,
        )
        return jsonify({"build_id": build.id}), 202

    @app.route("/api/pipelines/<int:pipeline_id>", methods=["DELETE"])
    @jwt_required()
    def delete_pipeline(pipeline_id):
        user_id = get_jwt_identity()

        pipeline = Pipeline.query.filter_by(
            id=pipeline_id,
            user_id=user_id
        ).first_or_404()

        db.session.delete(pipeline)
        db.session.commit()
        return jsonify({"message": "Pipeline deleted"}), 200


    # ============================
    # BUILD ROUTES
    # ============================
    @app.route("/api/builds", methods=["GET"]) 
    @jwt_required() 
    def list_builds():
        user_id = get_jwt_identity()

        builds = (
            Build.query
            .join(Pipeline)
            .filter(Pipeline.user_id == user_id)
            .order_by(Build.started_at.desc().nullslast())
            .limit(20)
            .all()
        )

        return jsonify([b.to_dict() for b in builds])


    @app.route("/api/builds/<int:build_id>/logs", methods=["GET"])
    def get_build_logs(build_id):
        build = db.session.get(Build, build_id)
        if not build:
            return jsonify({"error": "Build not found"}), 404
        logs = (
            BuildLog.query.filter_by(build_id=build_id)
            .order_by(BuildLog.id.asc())
            .all()
        )
        return jsonify(
            [
                {
                    "step_index": l.step_index,
                    "text": l.text,
                    "timestamp": l.timestamp.isoformat() if getattr(l, "timestamp", None) else None,
                }
                for l in logs
            ]
        )

    # ============================
    # ACTIVITY LOG ROUTE
    # ============================
    @app.route("/api/activity-logs", methods=["GET"])
    def get_activity_logs():
        logs = BuildLog.query.order_by(BuildLog.id.desc()).limit(20).all()
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "created_at": log.timestamp.isoformat() if log.timestamp else None,
                "details": {"message": log.text.strip() if log.text else ""},
            })
        return jsonify(result)

    # ============================
    # DASHBOARD DATA ROUTE
    # ============================
    @app.route("/api/dashboard-data", methods=["GET"])
    @jwt_required()
    def dashboard_data():
    # 🔐 Get user from JWT
        user_id = get_jwt_identity()

    # =========================
    # PIPELINES + STATUS
    # =========================
        pipelines = []

        for p in Pipeline.query.filter_by(user_id=user_id).all():
            last_build = (
                Build.query.filter_by(pipeline_id=p.id)
                .order_by(Build.id.desc())
                .first()
            )

            status = last_build.status if last_build else "unknown"
            runtime = "N/A"

            if last_build and last_build.started_at:
                try:
                    start_time = last_build.started_at
                    now = datetime.now(timezone.utc)

                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=timezone.utc)

                    runtime_minutes = int((now - start_time).total_seconds() // 60)
                    runtime = f"{runtime_minutes} min"

                except Exception as e:
                    print(f"⚠️ Runtime calc error for pipeline {p.id}: {e}")

            pipelines.append({
                "id": p.id,
                "name": p.name,
                "status": status,
                "runtime": runtime,
            })

    # =========================
    # RECENT LOGS (LAST 5)
    # =========================
        logs = []

        for log in BuildLog.query.order_by(BuildLog.id.desc()).limit(5).all():
            logs.append({
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "text": (log.text or "").strip(),
            })

    # =========================
    # LOCAL REPORT FILE PATH
    # =========================
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        report_file = os.path.join(
            BASE_DIR,
            "reports",
            "embedding_report.json"
        )

        risk_score = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        threat_categories = Counter()

    # =========================
    # READ REPORT (LOCAL)
    # =========================
        if os.path.exists(report_file):
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                   data = json.load(f)

                if isinstance(data, dict):
                   # Merge top-level scores
                   risk_score.update(data.get("risk_score", {}))
                   threat_categories.update(data.get("threat_categories", {}))

                # Count details (if present)
                   for item in data.get("details", []):
                        sev = (item.get("risk") or item.get("severity") or "").upper()
                        if sev in risk_score:
                            risk_score[sev] += 1

                        cat = item.get("category", "unknown")
                        threat_categories[cat] += 1

            except Exception as e:
                print(f"⚠️ Error reading embedding_report.json: {e}")
        else:
            print("⚠️ embedding_report.json not found at:", report_file)

    # =========================
    # RESPONSE
    # =========================
        return jsonify({
            "pipelines": pipelines,
            "logs": logs,
            "risk_score": risk_score,
            "threat_categories": dict(threat_categories),
            "report_file": report_file  # helpful for local debugging
        })

    # ============================
    # REPORTS ROUTE (explicit fixed files)
    # ============================
    @app.route("/api/reports", methods=["GET"])
    def list_reports():
        report_files = [
            {
                "path": os.path.join(BASE_DIR, "scan_reports", "report.json"),
                "type": "Security",
                "format": "JSON",
            },
            {
                "path": os.path.join(BASE_DIR, "scan_reports", "report.html"),
                "type": "Security",
                "format": "HTML",
            },
            {
                "path": os.path.join(BASE_DIR, "reports", "embedding_report.json"),
                "type": "Security",
                "format": "JSON",
            },
            {
                "path": os.path.join(BASE_DIR, "reports", "embedding_report.html"),
                "type": "Security",
                "format": "HTML",
            },
        ]

        reports = []
        base_url = "http://127.0.0.1:5000"

        for item in report_files:
            file_path = item["path"]
            if not os.path.exists(file_path):
                continue

            created_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            filename = os.path.basename(file_path)
            dir_name = os.path.basename(os.path.dirname(file_path))

            reports.append({
                "name": filename,
                "type": item["type"],
                "format": item["format"],
                "generated_at": created_time.strftime("%d/%m/%Y %H:%M"),
                "view_url": f"{base_url}/api/reports/view/{filename}?dir={dir_name}",
                "download_url": f"{base_url}/api/reports/download/{filename}?dir={dir_name}",
            })

        reports.sort(key=lambda x: x["generated_at"], reverse=True)
        return jsonify({"reports": reports})

    @app.route("/api/reports/view/<filename>", methods=["GET"])
    def view_report(filename):
        dir_param = request.args.get("dir", "").lower()
        base_dirs = {
            "scan_reports": os.path.join(BASE_DIR, "scan_reports"),
            "reports": os.path.join(BASE_DIR, "reports"),
        }

        reports_dir = base_dirs.get(dir_param)
        if not reports_dir:
            return jsonify({"error": "Invalid directory"}), 400

        full_path = os.path.join(reports_dir, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "Report not found"}), 404

        return send_from_directory(reports_dir, filename)

    @app.route("/api/reports/download/<filename>", methods=["GET"])
    def download_report(filename):
        dir_param = request.args.get("dir", "").lower()
        base_dirs = {
            "scan_reports": os.path.join(BASE_DIR, "scan_reports"),
            "reports": os.path.join(BASE_DIR, "reports"),
        }

        reports_dir = base_dirs.get(dir_param)
        if not reports_dir:
            return jsonify({"error": "Invalid directory"}), 400

        full_path = os.path.join(reports_dir, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "Report not found"}), 404

        return send_from_directory(reports_dir, filename, as_attachment=True)

    return app


# ============================
# ENTRY POINT
# ============================
if __name__ == "__main__":
    app = create_app()

    print("🚀 Backend starting on http://127.0.0.1:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
