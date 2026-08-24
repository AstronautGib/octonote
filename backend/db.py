"""
Minimal local storage for saved chart entries.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "data" / "voicedoc.db"
DB_PATH.parent.mkdir(exist_ok=True)


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                transcript TEXT NOT NULL,
                note_json TEXT NOT NULL
            )
            """
        )


def save_note(transcript: str, note: dict) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (transcript, note_json) VALUES (?, ?)",
            (transcript, json.dumps(note)),
        )
        return cursor.lastrowid


def list_notes() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, created_at, note_json FROM notes ORDER BY created_at DESC"
        ).fetchall()
    return [{"id": r[0], "created_at": r[1], "note": json.loads(r[2])} for r in rows]


def get_note(note_id: int) -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, created_at, transcript, note_json FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "created_at": row[1],
        "transcript": row[2],
        "note": json.loads(row[3]),
    }
