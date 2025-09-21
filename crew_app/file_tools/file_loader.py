import io
from typing import Tuple
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        parts.append(txt)
    return "\n".join(parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    f = io.BytesIO(file_bytes)
    doc = Document(f)
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    return "\n".join(parts)

def detect_and_extract(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Return (ext, text). ext in {pdf, docx, txt}."""
    low = filename.lower()
    if low.endswith(".pdf"):
        return "pdf", extract_text_from_pdf(file_bytes)
    if low.endswith(".docx"):
        return "docx", extract_text_from_docx(file_bytes)
    # basic text fallback
    try:
        return "txt", file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return "bin", ""
