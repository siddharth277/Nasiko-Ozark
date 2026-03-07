"""
PDF Utility - Extract text from PDF resumes using PyMuPDF
"""
import fitz  # PyMuPDF
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract clean text from PDF bytes."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = []
    for page in doc:
        text = page.get_text("text")
        full_text.append(text)
    doc.close()
    raw = "\n".join(full_text)
    # Clean up excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', raw)
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    return cleaned.strip()
