# app/clean.py (FINAL, MINIMAL DEPENDENCY VERSION - Renamed for process.py compatibility)
import json, re, os
from bs4 import BeautifulSoup # Required: BeautifulSoup4
from datetime import datetime, date

BOILERPLATE_PATTERNS = [
    r"(?i)Advertisement", r"(?i)Subscribe", r"(?i)Read More", r"(?i)Most Popular",
    r"(?i)Latest Stories", r"(?i)Continue reading", r"(?i)Story continues",
    r"(?i)Click/Scan to Subscribe", r"(?i)Tags", r"(?i)©", r"(?i)Follow us",
    r"(?i)Contact Us", r"(?i)About Us", r"(?i)Related Articles", r"(?i)Sponsored"
]

# 🚨 FIX: Renaming 'extract_text' to 'extract_text_from_html' to match app/process.py import
def extract_text_from_html(html: str) -> str:
    """
    Robust heuristic article text extractor (uses BeautifulSoup only).
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # remove scripts/styles
        for t in soup(["script", "style", "noscript", "iframe", "svg"]):
            t.decompose()

        # 1) Try <article>
        article = soup.find("article")
        if article:
            text = article.get_text(" ", strip=True)
        else:
            # 2) Try common main/content ids/classes
            selectors = [
                {"id": "main"}, {"id": "content"}, {"class_": "article-body"},
                {"class_": "post-content"}, {"class_": "story-body"}, {"class_": "entry-content"}
            ]
            text = None
            for s in selectors:
                tag = soup.find(attrs=s)
                if tag:
                    text = tag.get_text(" ", strip=True)
                    break

            # 3) fallback: meta description / og:description
            if not text or len(text.split()) < 40:
                meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
                if meta and meta.get("content"):
                    text = meta.get("content").strip()

            # 4) fallback to entire page text
            if not text:
                text = soup.get_text(" ", strip=True)

        # remove boilerplate patterns
        for pat in BOILERPLATE_PATTERNS:
            text = re.sub(pat, " ", text)

        # remove "Story continues" or "End of Article..." fragments
        text = re.sub(r"(?i)story continues.*", " ", text)
        text = re.sub(r"(?i)end of article.*", " ", text)

        # collapse whitespace
        text = " ".join(text.split())

        return text

    except Exception:
        # fallback to naive get_text
        return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def guess_publish_date(html):
    """
    Simplified date guesser (avoids dateparser). This is a placeholder.
    """
    # Returns today's date if the crawler missed it.
    return date.today().isoformat()