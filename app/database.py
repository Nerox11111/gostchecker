import json
from pathlib import Path
from typing import Any

import aiosqlite

from app.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    vk_user_id INTEGER PRIMARY KEY,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    vk_user_id INTEGER,
    doc_type TEXT,
    mode TEXT,
    score_before REAL,
    score_after REAL,
    orig_path TEXT,
    fixed_path TEXT,
    issues_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS feedback_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vk_user_id INTEGER,
    filepath TEXT NOT NULL,
    predicted_type TEXT,
    corrected_type TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def upsert_user(vk_user_id: int) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(vk_user_id) VALUES (?)",
            (vk_user_id,),
        )
        await db.commit()


async def create_session(
    *,
    session_id: str,
    vk_user_id: int,
    doc_type: str,
    mode: str,
    score_before: float,
    orig_path: Path,
    issues: list[dict[str, Any]],
) -> None:
    await upsert_user(vk_user_id)
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO sessions(
                id, vk_user_id, doc_type, mode, score_before,
                orig_path, issues_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                vk_user_id,
                doc_type,
                mode,
                score_before,
                str(orig_path),
                json.dumps(issues, ensure_ascii=False),
            ),
        )
        await db.commit()


async def get_session(session_id: str, vk_user_id: int) -> dict[str, Any] | None:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE id = ? AND vk_user_id = ?",
            (session_id, vk_user_id),
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def update_fixed_session(
    *,
    session_id: str,
    vk_user_id: int,
    score_after: float,
    fixed_path: Path,
    issues: list[dict[str, Any]],
) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            UPDATE sessions
            SET score_after = ?, fixed_path = ?, issues_json = ?
            WHERE id = ? AND vk_user_id = ?
            """,
            (
                score_after,
                str(fixed_path),
                json.dumps(issues, ensure_ascii=False),
                session_id,
                vk_user_id,
            ),
        )
        await db.commit()


async def list_sessions(vk_user_id: int) -> list[dict[str, Any]]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, doc_type, mode, score_before, score_after, created_at
            FROM sessions
            WHERE vk_user_id = ?
            ORDER BY datetime(created_at) DESC
            LIMIT 50
            """,
            (vk_user_id,),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]

