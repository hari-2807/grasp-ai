import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def parse(url: str, timeout: int = 10) -> dict:
    """Scrape a web URL and return cleaned text with metadata."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""

    # prefer article/main body, fall back to full body
    body = soup.find("article") or soup.find("main") or soup.find("body")
    raw_text = body.get_text(separator=" ", strip=True) if body else ""

    # collapse whitespace
    cleaned = " ".join(raw_text.split())
    word_count = len(cleaned.split())

    return {
        "title": title_text,
        "text": cleaned,
        "word_count": word_count,
        "url": url,
        "source_type": "web",
    }
