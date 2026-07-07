from urllib.parse import urlparse


YOUTUBE_HOSTS = {
    "www.youtube.com",
    "youtube.com",
    "youtu.be",
    "m.youtube.com",
    "music.youtube.com",
}


def detect(url: str) -> str:
    """Return 'youtube' or 'web' based on the URL."""
        if not url or "://" not in url:
           url = f"https://{url}"
            
    host = urlparse(url).hostname or ""
    return "youtube" if host in YOUTUBE_HOSTS else "web"
