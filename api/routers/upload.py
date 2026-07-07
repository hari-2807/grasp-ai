import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from api.models.schemas import UploadResponse, UploadUrlRequest
from agent.router import detect
from agent.parsers import pdf_parser, image_parser, youtube_parser, web_parser, audio_parser
from api.services.session_store import save_session
from auth.usage_tracker import check_upload_allowed,record_action
from api.auth.dependencies import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"]

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
_AUDIO_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".webm"}


def _check_upload_allowed(user: dict):
    result = check_upload_allowed(user["user_id"])
    if not result["allowed"]:
        raise HTTPException(status_code=402, detail=result["reason"])
        

def _save_and_respond(content: dict, user_id: str) -> UploadResponse:
    if content.get("error"):
        return UploadResponse(
            session_id="",
            title=content.get("title", ""),
            source_type=content.get("source_type", "web"),
            word_count=0,
            error=content["error"],
        )

    session_id = str(uuid.uuid4())
    save_session(session_id, content)
    record_action(user_id, action="upload")

    return UploadResponse(
        session_id=session_id,
        title=content.get("title", ""),
        source_type=content["source_type"],
        word_count=content.get("word_count", 0),
        truncated=content.get("truncated", False),
        likely_scanned=content.get("likely_scanned"),
        warning=content.get("warning"),
    )


@router.post("/url", response_model=UploadResponse)
def upload_url(req: UploadUrlRequest, user: dict = Depends(get_current_user)):
    """Upload via URL — auto-detects YouTube vs regular web page."""
    _check_upload_allowed(user)

    source = detect(req.url)
    if source == "youtube":
        content = youtube_parser.parse(req.url)
    else:
        content = web_parser.parse(req.url)

    return _save_and_respond(content, user["user_id"])


@router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Upload a PDF, image, or audio file — routes by file extension."""
    _check_upload_allowed(user)

    filename = file.filename or "upload"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    file_bytes = await file.read()

    if ext == ".pdf":
        content = pdf_parser.parse(file_bytes, filename=filename)
    elif ext in _IMAGE_EXTENSIONS:
        content = image_parser.parse(file_bytes)
    elif ext in _AUDIO_EXTENSIONS:
        content = audio_parser.transcribe(file_bytes, filename=filename)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    return _save_and_respond(content, user["user_id"])
