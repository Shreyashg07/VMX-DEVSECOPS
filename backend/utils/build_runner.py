import json
import subprocess
import platform
from datetime import datetime, timezone

def run_command_and_stream(build_id, step_index, cmd, app, socketio):
    if not cmd:
        return 0

    if platform.system() == "Windows":
        cmd = f"cmd /c {cmd}"

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        print(f"[Build {build_id} | Step {step_index}] Failed to start: {e}")
        socketio.emit("activity_log", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"❌ Step {step_index + 1} failed to start: {e}"
        })
        return 1

    buffer = []
    emit_cooldown = 0

    for line in iter(proc.stdout.readline, ""):
        if not line:
            break

        text_line = line.rstrip("\n")
        print(f"[Build {build_id} | Step {step_index}]: {text_line}")

        # Add to DB periodically
        buffer.append(text_line)
        if len(buffer) >= 15:
            with app.app_context():
                from models import db, BuildLog
                for log_line in buffer:
                    db.session.add(BuildLog(build_id=build_id, step_index=step_index, text=log_line))
                db.session.commit()
            buffer.clear()

        # emit log events (for PipelineDetail + Activity)
        emit_cooldown += 1
        if emit_cooldown >= 5:
            socketio.emit("build_log", {
                "build_id": build_id,
                "step_index": step_index,
                "text": text_line,
            })
            socketio.emit("activity_log", {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": text_line,
            })
            emit_cooldown = 0

    # flush remaining logs
    if buffer:
        with app.app_context():
            from models import db, BuildLog
            for log_line in buffer:
                db.session.add(BuildLog(build_id=build_id, step_index=step_index, text=log_line))
            db.session.commit()

    proc.stdout.close()
    rc = proc.wait()
    print(f"[Build {build_id} | Step {step_index}] Return code {rc}")
    return rc


def run_build_thread(build_id, pipeline_config_json, app, socketio):
    with app.app_context():
        from models import db, Build
        build = db.session.get(Build, build_id)
        if not build:
            print(f"[Build {build_id}] Not found in DB")
            return

        build.status = "running"
        db.session.commit()

    socketio.emit("build_status_update", {"build_id": build_id, "status": "running"})
    socketio.emit("activity_log", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"🏁 Build {build_id} started."
    })

    try:
        config = json.loads(pipeline_config_json or "{}")
        steps = config.get("steps", [])
        total_steps = len(steps) or 1

        for index, step in enumerate(steps):
            cmd = step.get("cmd")
            socketio.emit("activity_log", {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"▶ Step {index + 1} running: {cmd}"
            })

            rc = run_command_and_stream(build_id, index, cmd, app, socketio)

            socketio.emit("build_progress", {
                "build_id": build_id,
                "progress": int(((index + 1) / total_steps) * 100),
            })

            if rc != 0:
                with app.app_context():
                    from models import db, Build
                    build = db.session.get(Build, build_id)
                    build.status = "failed"
                    build.finished_at = datetime.now(timezone.utc)
                    db.session.commit()

                socketio.emit("build_finished", {"build_id": build_id, "status": "failed"})
                socketio.emit("activity_log", {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": f"❌ Build {build_id} failed at step {index + 1}"
                })
                return

        with app.app_context():
            from models import db, Build
            build = db.session.get(Build, build_id)
            build.status = "success"
            build.finished_at = datetime.now(timezone.utc)
            db.session.commit()

        socketio.emit("build_finished", {"build_id": build_id, "status": "success"})
        socketio.emit("activity_log", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"✅ Build {build_id} completed successfully."
        })

    except Exception as e:
        with app.app_context():
            from models import db, Build
            build = db.session.get(Build, build_id)
            if build:
                build.status = "failed"
                build.finished_at = datetime.now(timezone.utc)
                db.session.commit()

        socketio.emit("build_finished", {"build_id": build_id, "status": "failed"})
        socketio.emit("activity_log", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"❌ Build {build_id} encountered an error: {e}"
        })
