from __future__ import annotations

from fastapi import Depends, FastAPI, File, UploadFile
from pydantic import BaseModel, Field

from app.auth import require_auth
from app.config import get_settings
from app.db import (
    add_concept,
    get_due_reviews,
    get_weak_concepts,
    import_anki_csv,
    init_db,
    record_answer,
    search_concepts,
    stats,
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


class ConceptIn(BaseModel):
    title: str = Field(min_length=1)
    question: str = ""
    answer: str = ""
    topic: str = ""
    notes: str = ""
    tags: str = ""
    source: str = "manual"


class SearchIn(BaseModel):
    query: str = ""
    topic: str = ""
    limit: int = Field(default=10, ge=1, le=50)


class AnswerIn(BaseModel):
    concept_id: int
    user_answer: str = ""
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    mistake_notes: str = ""


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "ready",
        "docs": "/docs",
        "private_endpoints_require": "Authorization: Bearer <token>",
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True, "stats": stats()}


@app.post("/api/concepts", dependencies=[Depends(require_auth)])
def api_add_concept(payload: ConceptIn) -> dict:
    return add_concept(**payload.model_dump())


@app.post("/api/search", dependencies=[Depends(require_auth)])
def api_search(payload: SearchIn) -> dict:
    return {"results": search_concepts(payload.query, payload.topic, payload.limit)}


@app.get("/api/reviews/due", dependencies=[Depends(require_auth)])
def api_due_reviews(limit: int = 10) -> dict:
    return {"results": get_due_reviews(limit)}


@app.get("/api/reviews/weak", dependencies=[Depends(require_auth)])
def api_weak_concepts(limit: int = 10) -> dict:
    return {"results": get_weak_concepts(limit)}


@app.post("/api/reviews/answer", dependencies=[Depends(require_auth)])
def api_record_answer(payload: AnswerIn) -> dict:
    updated = record_answer(
        concept_id=payload.concept_id,
        user_answer=payload.user_answer,
        score=payload.score,
        confidence=payload.confidence,
        mistake_notes=payload.mistake_notes,
    )
    return {"updated_concept": updated}


@app.post("/api/import/anki-csv", dependencies=[Depends(require_auth)])
async def api_import_anki_csv(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    result = import_anki_csv(data)
    return result


@app.get("/api/mentor/review-context", dependencies=[Depends(require_auth)])
def api_review_context(topic: str = "", limit: int = 8) -> dict:
    due = get_due_reviews(limit)
    weak = get_weak_concepts(limit)
    related = search_concepts(query="", topic=topic, limit=limit) if topic else []
    return {
        "instruction": "Use this context to teach, quiz, and update the learner model. Do not simply repeat flashcards; explain concepts from different angles.",
        "topic": topic,
        "due_reviews": due,
        "weak_concepts": weak,
        "topic_related": related,
        "stats": stats(),
    }
