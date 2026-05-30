"""LangChain tools wrapping the User Management API.

Real HTTP calls are made on lines 20, 38, 55, 71 respectively.
Debug output via print() is on the line immediately after each call.
"""
import json
import os

import httpx
from langchain.tools import tool

_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@tool
def create_user(name: str, email: str) -> str:
    """Create a new user. Requires name and email."""
    print(f"[TOOL] POST /users  name={name!r} email={email!r}")  # L20 debug
    try:
        r = httpx.post(f"{_BASE}/users", json={"name": name, "email": email}, timeout=5)
        data = r.json()
        print(f"[TOOL] response {r.status_code}: {data}")  # L23 debug
        if r.status_code == 201:
            return json.dumps({"success": True, "user": data})
        return json.dumps({"success": False, "error": data.get("detail", "unknown")})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def get_user(user_id: int) -> str:
    """Get user information by numeric user ID."""
    print(f"[TOOL] GET /users/{user_id}")  # L33 debug
    try:
        r = httpx.get(f"{_BASE}/users/{user_id}", timeout=5)
        data = r.json()
        print(f"[TOOL] response {r.status_code}: {data}")  # L37 debug
        if r.status_code == 200:
            return json.dumps({"success": True, "user": data})
        return json.dumps({"success": False, "error": data.get("detail", "not found")})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def update_user_status(user_id: int, status: str) -> str:
    """Update user status. Allowed values: active, inactive, banned."""
    print(f"[TOOL] PATCH /users/{user_id}/status  status={status!r}")  # L46 debug
    try:
        r = httpx.patch(f"{_BASE}/users/{user_id}/status", json={"status": status}, timeout=5)
        data = r.json()
        print(f"[TOOL] response {r.status_code}: {data}")  # L50 debug
        if r.status_code == 200:
            return json.dumps({"success": True, "user": data})
        return json.dumps({"success": False, "error": data.get("detail", "unknown")})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def list_users() -> str:
    """Return the full list of users and the total count."""
    print("[TOOL] GET /users")  # L60 debug
    try:
        r = httpx.get(f"{_BASE}/users", timeout=5)
        data = r.json()
        print(f"[TOOL] response {r.status_code}: {data}")  # L64 debug
        if r.status_code == 200:
            return json.dumps({"success": True, "data": data})
        return json.dumps({"success": False, "error": "failed to fetch users"})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})
