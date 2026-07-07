from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SourceType(str, Enum):
    web = "web"
    youtube = "youtube"
    pdf = "pdf"
    image = "image"
    audio = "audio"


class ModeType(str, Enum):
    summary = "summary"
    analysis = "analysis"
    qa = "qa"
    teaching = "teaching"
    flashcards = "flashcards"


class Tier(str, Enum):
    free = "free"
    pro = "pro"


# --- Upload ---

class UploadUrlRequest(BaseModel):
    url: str


class UploadResponse(BaseModel):
    session_id: str
    title: str
    source_type: SourceType
    word_count: int
    truncated: bool = False
    likely_scanned: Optional[bool] = None
    warning: Optional[str] = None
    error: Optional[str] = None


# --- Mode requests ---

class SummaryRequest(BaseModel):
    session_id: str


class AnalysisRequest(BaseModel):
    session_id: str


class ChatMessage(BaseModel):
    role: str
    content: str


class QARequest(BaseModel):
    session_id: str
    question: str
    history: list[ChatMessage] = Field(default_factory=list)


class TeachingRequest(BaseModel):
    session_id: str
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class FlashcardsRequest(BaseModel):
    session_id: str


# --- Mode responses ---

class ModeResponse(BaseModel):
    output: str
    model: str
    model_id: str
    reason: Optional[str] = None
    cost_gbp: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    truncated: bool = False
    error: Optional[str] = None


class FlashCard(BaseModel):
    question: str
    answer: str


class FlashcardsResponse(BaseModel):
    cards: list[FlashCard]
    model: str
    model_id: str
    cost_gbp: float
    truncated: bool = False
    error: Optional[str] = None


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    google_sub: str


class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    tier: Tier
    created_at: datetime


# --- Usage tracking ---

class UsageEvent(BaseModel):
    user_id: str
    action: ModeType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    month_year: str


class UsageSummary(BaseModel):
    user_id: str
    month_year: str
    uploads_this_month: int
    tier: Tier
    uploads_remaining: Optional[int] = None


# --- Payments ---

class CheckoutRequest(BaseModel):
    user_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class StripeWebhookEvent(BaseModel):
    type: str
    data: dict
