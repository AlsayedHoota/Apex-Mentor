from __future__ import annotations

import csv
import io
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.config import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    settings = get_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL,
                question TEXT NOT NULL DEFAULT '',
                answer TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT 'manual',
                mastery_score REAL NOT NULL DEFAULT 0.0,
                confidence REAL NOT NULL DEFAULT 0.0,
                review_count INTEGER NOT NULL DEFAULT 0,
                last_reviewed_at TEXT,
                next_review_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL DEFAULT '',
                score REAL NOT NULL,
                confidence REAL NOT NULL DEFAULT 0.0,
                mistake_notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(concept_id) REFERENCES concepts(id)
            );
            """
        )
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def add_concept(
    title: str,
    question: str = "",
    answer: str = "",
    topic: str = "",
    notes: str = "",
    tags: str = "",
    source: str = "manual",
) -> dict[str, Any]:
    now = utc_now()
    next_review = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO concepts (
                topic, title, question, answer, notes, tags, source,
                next_review_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (topic, title, question, answer, notes, tags, source, next_review, now, now),
        )
        conn.commit()
        return get_concept(cur.lastrowid)


def get_concept(concept_id: int) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,)).fetchone()
    if row is None:
        raise KeyError(f"Concept not found: {concept_id}")
    return row_to_dict(row)


def search_concepts(query: str = "", topic: str = "", limit: int = 10) -> list[dict[str, Any]]:
    query_like = f"%{query.lower()}%"
    topic_like = f"%{topic.lower()}%"
    clauses = []
    params: list[Any] = []

    if query:
        clauses.append(
            "(lower(title) LIKE ? OR lower(question) LIKE ? OR lower(answer) LIKE ? OR lower(notes) LIKE ? OR lower(tags) LIKE ?)"
        )
        params.extend([query_like] * 5)

    if topic:
        clauses.append("lower(topic) LIKE ?")
        params.append(topic_like)

    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    sql = f"""
        SELECT * FROM concepts
        {where}
        ORDER BY mastery_score ASC, COALESCE(next_review_at, created_at) ASC
        LIMIT ?
    """
    params.append(limit)

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


def get_due_reviews(limit: int = 10) -> list[dict[str, Any]]:
    now = utc_now()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM concepts
            WHERE next_review_at IS NULL OR next_review_at <= ?
            ORDER BY mastery_score ASC, COALESCE(next_review_at, created_at) ASC
            LIMIT ?
            """,
            (now, limit),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def record_answer(
    concept_id: int,
    user_answer: str,
    score: float,
    confidence: float = 0.0,
    mistake_notes: str = "",
) -> dict[str, Any]:
    score = max(0.0, min(1.0, score))
    confidence = max(0.0, min(1.0, confidence))
    now_dt = datetime.now(timezone.utc)
    now = now_dt.isoformat()

    current = get_concept(concept_id)
    old_mastery = float(current["mastery_score"] or 0.0)
    old_confidence = float(current["confidence"] or 0.0)
    review_count = int(current["review_count"] or 0) + 1

    new_mastery = round((old_mastery * 0.7) + (score * 0.3), 4)
    new_confidence = round((old_confidence * 0.6) + (confidence * 0.4), 4)

    if score < 0.4:
        interval_days = 1
    elif score < 0.7:
        interval_days = 3
    elif score < 0.9:
        interval_days = 7
    else:
        interval_days = 14

    next_review = (now_dt + timedelta(days=interval_days)).isoformat()

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO review_events (concept_id, user_answer, score, confidence, mistake_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (concept_id, user_answer, score, confidence, mistake_notes, now),
        )
        conn.execute(
            """
            UPDATE concepts
            SET mastery_score = ?, confidence = ?, review_count = ?,
                last_reviewed_at = ?, next_review_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_mastery, new_confidence, review_count, now, next_review, now, concept_id),
        )
        conn.commit()

    return get_concept(concept_id)


def get_weak_concepts(limit: int = 10) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM concepts
            ORDER BY mastery_score ASC, confidence ASC, review_count ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row_to_dict(row) for row in rows]


def import_anki_csv(csv_bytes: bytes) -> dict[str, Any]:
    text = csv_bytes.decode("utf-8-sig")
    sample = text[:2048]
    dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)

    imported = 0
    skipped = 0
    for row in reader:
        front = (row.get("front") or row.get("Front") or row.get("question") or row.get("Question") or "").strip()
        back = (row.get("back") or row.get("Back") or row.get("answer") or row.get("Answer") or "").strip()
        tags = (row.get("tags") or row.get("Tags") or "").strip()
        deck = (row.get("deck") or row.get("Deck") or "").strip()
        title = front[:120] if front else back[:120]

        if not title and not back:
            skipped += 1
            continue

        add_concept(
            title=title or "Untitled card",
            question=front,
            answer=back,
            topic=deck,
            tags=tags,
            source="anki_csv",
        )
        imported += 1

    return {"imported": imported, "skipped": skipped}


def stats() -> dict[str, Any]:
    with connect() as conn:
        concept_count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        review_count = conn.execute("SELECT COUNT(*) FROM review_events").fetchone()[0]
        due_count = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE next_review_at IS NULL OR next_review_at <= ?",
            (utc_now(),),
        ).fetchone()[0]
    return {
        "concepts": concept_count,
        "review_events": review_count,
        "due_reviews": due_count,
    }
