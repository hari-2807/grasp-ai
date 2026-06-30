from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def _extract_video_id(url: str) -> str:
    """Pull the video ID out of any YouTube URL format."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
    raise ValueError(f"Cannot extract video ID from URL: {url}")


def parse(url: str) -> dict:
    """Fetch the transcript of a YouTube video and return cleaned text."""
    video_id = _extract_video_id(url)

    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
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
