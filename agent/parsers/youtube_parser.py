from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from urllib.parse import urlparse, parse_qs


def _extract_video_id(url: str) -> str:
    """Pull the video ID out of any YouTube URL format."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
    raise ValueError(f"Cannot extract video ID from URL: {url}")


def parse(url: str) -> dict:
    """Fetch the transcript of a YouTube video and return cleaned text."""
    try:
        video_id = _extract_video_id(url)
    except ValueError as e:
        return {
            "title": "",
            "text": "",
            "word_count": 0,
            "url": url,
            "source_type": "youtube",
            "video_id": None,
            "error": str(e),
        }

    ytt_api = YouTubeTranscriptApi()

    try:
        fetched = ytt_api.fetch(video_id)
        transcript_list = fetched.to_raw_data()
    except TranscriptsDisabled:
        return _error_result(url, video_id, "Captions are disabled for this video.")
    except NoTranscriptFound:
        return _error_result(url, video_id, "No transcript is available for this video.")
    except VideoUnavailable:
        return _error_result(url, video_id, "This video is unavailable.")
    except Exception as e:
        return _error_result(url, video_id, f"Could not fetch transcript: {e}")

    raw_text = " ".join(entry["text"] for entry in transcript_list)
    cleaned = " ".join(raw_text.split())
    word_count = len(cleaned.split())

    return {
        "title": f"YouTube video ({video_id})",
        "text": cleaned,
        "word_count": word_count,
        "url": url,
        "source_type": "youtube",
        "video_id": video_id,
    }


def _error_result(url: str, video_id: str, message: str) -> dict:
    return {
        "title": f"YouTube video ({video_id})",
        "text": "",
        "word_count": 0,
        "url": url,
        "source_type": "youtube",
        "video_id": video_id,
        "error": message,
    }
