# api/app/routers/policies.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json

router = APIRouter(prefix="/policies", tags=["policies"])

POLICY_FILE = os.path.join(os.getcwd(), "policies", "default_policy.json")

# Default policy structure
DEFAULT_POLICY = {
    "whitelist_files": [],
    "whitelist_rules": [],
    "whitelist_detectors": [],
    "whitelist_patterns": [],
    "whitelist_enabled": True,
}


# ---------------------------------------------------------
# Ensure policy file exists
# ---------------------------------------------------------
def load_policy():
    if not os.path.exists(POLICY_FILE):
        os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
        with open(POLICY_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_POLICY, f, indent=2)

    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        raise HTTPException(500, detail="Invalid policy JSON format")


def save_policy(data):
    try:
        with open(POLICY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to save policy: {str(e)}")


# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class PolicyUpdate(BaseModel):
    whitelist_files: list = []
    whitelist_rules: list = []
    whitelist_detectors: list = []
    whitelist_patterns: list = []
    whitelist_enabled: bool = True


class WhitelistRequest(BaseModel):
    file: str | None = None
    rule_id: str | None = None
    detector: str | None = None


# ---------------------------------------------------------
# GET POLICY (supports /policies & /policies/)
# ---------------------------------------------------------
@router.get("")
@router.get("/")
def get_policy():
    policy = load_policy()
    return policy


# ---------------------------------------------------------
# OVERWRITE POLICY
# ---------------------------------------------------------
@router.post("")
@router.post("/", summary="Replace entire policy")
def update_policy(p: PolicyUpdate):
    save_policy(p.dict())
    return {"status": "ok", "policy": p}


# ---------------------------------------------------------
# ADD WHITELIST ENTRY
# ---------------------------------------------------------
@router.post("/whitelist", summary="Add whitelist entry")
def add_whitelist(entry: WhitelistRequest):
    policy = load_policy()

    updated = False

    if entry.file:
        if entry.file not in policy["whitelist_files"]:
            policy["whitelist_files"].append(entry.file)
            updated = True

    if entry.rule_id:
        if entry.rule_id not in policy["whitelist_rules"]:
            policy["whitelist_rules"].append(entry.rule_id)
            updated = True

    if entry.detector:
        if entry.detector not in policy["whitelist_detectors"]:
            policy["whitelist_detectors"].append(entry.detector)
            updated = True

    if updated:
        save_policy(policy)
        return {"status": "ok", "policy": policy}

    return {"status": "noop", "policy": policy}
