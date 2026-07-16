"""Document conversions: DOCX -> PDF and PDF -> DOCX.

DOCX -> PDF uses Microsoft Word via docx2pdf when Word is installed,
otherwise falls back to LibreOffice in headless mode.
PDF -> DOCX uses pdf2docx and needs no external programs.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DOC_FORMATS = {"docx", "pdf"}

_LIBREOFFICE_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def _find_libreoffice() -> str | None:
    path = shutil.which("soffice")
    if path:
        return path
    for candidate in _LIBREOFFICE_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


def _word_available() -> bool:
    if sys.platform != "win32":
        return False
    import winreg

    try:
        winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Word.Application").Close()
        return True
    except OSError:
        return False


def docx_to_pdf(src: Path, dest: Path) -> Path:
    if _word_available():
        from docx2pdf import convert

        convert(str(src), str(dest))
        return dest

    soffice = _find_libreoffice()
    if soffice:
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(dest.parent), str(src)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed:\n{result.stderr.strip()}")
        produced = dest.parent / (src.stem + ".pdf")
        if produced != dest:
            produced.replace(dest)
        return dest

    raise RuntimeError(
        "DOCX -> PDF needs Microsoft Word or LibreOffice installed; neither was found."
    )


def pdf_to_docx(src: Path, dest: Path) -> Path:
    from pdf2docx import Converter

    converter = Converter(str(src))
    try:
        converter.convert(str(dest))
    finally:
        converter.close()
    return dest
