from fastapi import APIRouter, HTTPException, Depends

from api.models.schemas import (
    SummaryRequest, AnalysisRequest, QARequest, TeachingRequest,
    FlashcardsRequest, ModeResponse, FlashcardsResponse,
)
from agent.modes import summary, analysis, qa, teaching, flashcards
from api.services.session_store import get_session

router = APIRouter(prefix="/agent", tags=["agent"])


def _get_content_or_404(session_id: str) -> dict:
    content = get_session(session_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return content


@router.post("/summary", response_model=ModeResponse)
def run_summary(req: SummaryRequest, anthropic_key: str = None, gemini_key: str = None):
    content = _get_content_or_404(req.session_id)
    result = summary.run(content, anthropic_key=anthropic_key, gemini_key=gemini_key)
    return ModeResponse(**result)


@router.post("/analysis", response_model=ModeResponse)
def run_analysis(req: AnalysisRequest, anthropic_key: str = None):
    content = _get_content_or_404(req.session_id)
    result = analysis.run(content, anthropic_key=anthropic_key)
    return ModeResponse(**result)


@router.post("/qa", response_model=ModeResponse)
def run_qa(req: QARequest, anthropic_key: str = None):
    content = _get_content_or_404(req.session_id)
    history = [m.model_dump() for m in req.history]
    result = qa.run(content, req.question, history=history, anthropic_key=anthropic_key)
    return ModeResponse(**result)


@router.post("/teaching", response_model=ModeResponse)
def run_teaching(req: TeachingRequest, anthropic_key: str = None):
    content = _get_content_or_404(req.session_id)
    history = [m.model_dump() for m in req.history]
    result = teaching.run(content, req.message, history=history, anthropic_key=anthropic_key)
    return ModeResponse(**result)


@router.post("/flashcards", response_model=FlashcardsResponse)
def run_flashcards(req: FlashcardsRequest, gemini_key: str = None):
    content = _get_content_or_404(req.session_id)
    result = flashcards.run(content, gemini_key=gemini_key)
    return FlashcardsResponse(**result)
