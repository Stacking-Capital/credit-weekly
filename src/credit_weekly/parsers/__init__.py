"""Pluggable credit report parser registry supporting PDF and extracted text."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .experian_equifax import parse_equifax_text, parse_experian_text
from .transunion import parse_transunion_text


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract text locally from a saved bureau PDF using pdftotext or pypdf.

    Never sends files over the network. Rejects empty/scanned image PDFs.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    text = ""
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            text = proc.stdout

    if not text.strip():
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(str(path))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise RuntimeError(f"Failed to extract text from PDF {path}: {exc}") from exc

    if len(text.strip()) < 40:
        raise ValueError(
            f"PDF {path.name} has no extractable text (likely scanned image or corrupted)."
        )
    return text


def detect_bureau(text: str, hint: str | None = None) -> str:
    if hint and hint.lower() in {"equifax", "experian", "transunion"}:
        return hint.lower()
    head = text[:2500].lower()
    if "transunion" in head:
        return "transunion"
    if "experian" in head:
        return "experian"
    if "equifax" in head:
        return "equifax"
    raise ValueError("Unable to detect bureau from report text; pass bureau hint explicitly.")


def parse_report_text(text: str, bureau: str | None = None) -> dict[str, Any]:
    detected = detect_bureau(text, bureau)
    if detected == "transunion":
        return parse_transunion_text(text)
    if detected == "experian":
        return parse_experian_text(text)
    if detected == "equifax":
        return parse_equifax_text(text)
    raise ValueError(f"Unsupported bureau: {detected}")


def parse_report_file(file_path: str | Path, bureau: str | None = None) -> dict[str, Any]:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(path)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
    return parse_report_text(text, bureau=bureau)
