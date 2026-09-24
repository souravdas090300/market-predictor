"""Fetch and parse web pages, PDFs and CSVs for material."""
from __future__ import annotations

import tempfile
from io import StringIO, BytesIO

from . import config
from ..services import material


def fetch_url(url: str) -> dict:
    """Fetch a web page and extract text. Returns text or error."""
    try:
        import requests
        from bs4 import BeautifulSoup

        r = requests.get(url, timeout=config.FETCH_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Remove script and style
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        text = "\n".join(lines)[: config.FETCH_MAX_CHARS]
        return {"text": text, "title": soup.title.string if soup.title else url[:60]}
    except Exception as e:
        raise ValueError(f"Could not fetch that URL: {e}")


def extract_pdf(data: bytes) -> dict:
    """Extract text from a PDF. Returns text or error."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)[
            : config.FETCH_MAX_CHARS
        ]
        if not text.strip():
            raise ValueError("No text found in PDF")
        return {"text": text, "title": reader.metadata.title or "PDF"}
    except Exception as e:
        raise ValueError(f"Could not read that PDF: {e}")


def extract_csv(data: bytes) -> dict:
    """Parse CSV into column names and a summary. Returns text or error."""
    try:
        import csv

        text = data.decode("utf-8", errors="replace")
        reader = csv.DictReader(StringIO(text))
        rows = list(reader)
        if not rows:
            raise ValueError("CSV is empty")
        cols = reader.fieldnames or []
        # Build a summary: column names and a few rows
        summary = f"Columns: {', '.join(cols)}\n\n"
        for i, row in enumerate(rows[:20]):
            summary += " | ".join(f"{v}" for v in row.values()) + "\n"
        if len(rows) > 20:
            summary += f"\n... and {len(rows) - 20} more rows"
        return {"text": summary, "title": "CSV data"}
    except Exception as e:
        raise ValueError(f"Could not read that CSV: {e}")
