from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.app.routers import health, incidents, policies
from api.app.db import init_db
from api.app.routers import stats
from api.app.routers import timeline
import os

app = FastAPI(title="CI/CD Integrity Monitor API")

# ============================================================
# 1) CORS CONFIG (Safe + Flexible)
# ============================================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],   # "*" for local dev, restrict in prod
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ============================================================
# 2) API KEY SECURITY MIDDLEWARE
# ============================================================
API_KEY = os.getenv("API_KEY", None)

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Enforces API key for write endpoints (POST/DELETE/PATCH).
    GET endpoints are public for frontend display.
    """
    write_methods = {"POST", "PUT", "PATCH", "DELETE"}

    if request.method in write_methods:
        provided_key = request.headers.get("x-api-key")

        if not API_KEY:
            # no key configured in env — allow everything for dev
            pass
        else:
            if provided_key != API_KEY:
                raise HTTPException(status_code=401, detail="Invalid or missing API key")

    response = await call_next(request)
    return response


# ============================================================
# 3) ROUTES
# ============================================================
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(policies.router)
app.include_router(stats.router, prefix="", tags=["stats"])
app.include_router(timeline.router, prefix="", tags=["timeline"])

# ============================================================
# 4) STARTUP: Initialize Database
# ============================================================
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 CI/CD Integrity Monitor backend initialized.")
