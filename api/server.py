"""User Management API — SQLite-backed storage."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from api.database import get_conn, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="User Management API", version="1.0.0", lifespan=lifespan)


class UserCreate(BaseModel):
    name: str
    email: str


class StatusUpdate(BaseModel):
    status: str  # active | inactive | banned


def _row_to_dict(row) -> dict:
    return dict(row)


@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?) RETURNING *",
                (body.name, body.email),
            )
            return _row_to_dict(cur.fetchone())
        except Exception as exc:
            if "UNIQUE constraint" in str(exc):
                raise HTTPException(status_code=409, detail="Email already exists")
            raise HTTPException(status_code=500, detail=str(exc))


@app.get("/users/{user_id}")
def get_user(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _row_to_dict(row)


@app.patch("/users/{user_id}/status")
def update_status(user_id: int, body: StatusUpdate):
    allowed = {"active", "inactive", "banned"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed}")
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE users SET status = ? WHERE id = ? RETURNING *",
            (body.status, user_id),
        )
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _row_to_dict(row)


@app.get("/users")
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    users = [_row_to_dict(r) for r in rows]
    return {"users": users, "total": len(users)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
