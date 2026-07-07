import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

MIN_WORD_COUNT = 30


def _is_safe_url(url: str) -> bool:
    """Block requests to local/private/internal addresses (basic SSRF guard)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    try:
        host = parsed.hostname
        if not host:
            return False
        ip = socket.gethostbyname(host)
        return not ipaddress.ip_address(ip).is_private
    except (socket.gaierror, ValueError):
        return False


def parse(url: str, timeout: int = 10) -> dict:
    """Scrape a web URL and return cleaned text with metadata."""
    if not _is_safe_url(url):
        return {
            "title": "",
            "text": "",
            "word_count": 0,
            "url": url,
            "source_type": "web",
            "error": "This URL cannot be accessed.",
        }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {
            "title": "",
            "text": "",
            "word_count": 0,
            "url": url,
            "source_type": "web",
            "error": str(e),
        }

    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        return {
            "title": "",
            "text": "",
            "word_count": 0,
            "url": url,
            "source_type": "web",
            "error": f"Unsupported content type: {content_type}",
        }

    soup = BeautifulSoup(resp.text, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""

    body = soup.find("article") or soup.find("main") or soup.find("body")
    raw_text = body.get_text(separator=" ", strip=True) if body else ""

    cleaned = " ".join(raw_text.split())
    word_count = len(cleaned.split())

    result = {
        "title": title_text,
        "text": cleaned,
        "word_count": word_count,
        "url": url,
        "source_type": "web",
    }

    if word_count < MIN_WORD_COUNT:
        result["warning"] = "This page had very little extractable text — it may require JavaScript to load content."

    return result
