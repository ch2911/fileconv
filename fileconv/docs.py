"""Document conversions: DOCX -> PDF and PDF -> DOCX.

DOCX -> PDF tries three engines, best fidelity first:
  1. Microsoft Word (via docx2pdf), when installed
  2. LibreOffice in headless mode, when installed
  3. pandoc + typst (pure pip packages, no installed programs needed)
PDF -> DOCX uses pdf2docx and needs no external programs.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
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


def _pandoc_typst_available() -> bool:
    try:
        import pypandoc
        import typst  # noqa: F401

        pypandoc.get_pandoc_version()
        return True
    except Exception:
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

    if _pandoc_typst_available():
        return _docx_to_pdf_pandoc(src, dest)

    raise RuntimeError(
        "DOCX -> PDF needs Microsoft Word, LibreOffice, or the pandoc/typst "
        "fallback (`pip install pypandoc-binary typst`); none was found."
    )


def _docx_to_pdf_pandoc(src: Path, dest: Path) -> Path:
    """Pure-Python engine: pandoc turns the DOCX into typst markup, typst
    compiles that to PDF. Embedded images are extracted alongside."""
    import pypandoc
    import typst

    src = src.resolve()
    dest = dest.resolve()
    with tempfile.TemporaryDirectory() as tmp:
        typ_file = Path(tmp) / "document.typ"
        # Run pandoc from inside the temp dir so extracted media get relative
        # paths, which typst resolves against its root.
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            pypandoc.convert_file(
                str(src),
                "typst",
                outputfile=str(typ_file),
                extra_args=["--extract-media", "."],
            )
        finally:
            os.chdir(cwd)
        typst.compile(str(typ_file), output=str(dest), root=tmp)
    return dest


def pdf_to_docx(src: Path, dest: Path) -> Path:
    from pdf2docx import Converter

    converter = Converter(str(src))
    try:
        converter.convert(str(dest))
    finally:
        converter.close()
    return dest
