from pathlib import Path

import pytest

from fileconv.docs import _find_libreoffice, _word_available, docx_to_pdf, pdf_to_docx


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """One-page PDF generated with PyMuPDF (already installed via pdf2docx)."""
    import fitz

    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from fileconv test suite.")
    doc.save(str(path))
    doc.close()
    return path


def test_pdf_to_docx(sample_pdf: Path, tmp_path: Path):
    dest = pdf_to_docx(sample_pdf, tmp_path / "out.docx")
    assert dest.exists() and dest.stat().st_size > 0


@pytest.mark.skipif(
    not (_word_available() or _find_libreoffice()),
    reason="needs Microsoft Word or LibreOffice",
)
def test_docx_to_pdf_round_trip(sample_pdf: Path, tmp_path: Path):
    docx = pdf_to_docx(sample_pdf, tmp_path / "mid.docx")
    pdf = docx_to_pdf(docx, tmp_path / "back.pdf")
    assert pdf.exists() and pdf.stat().st_size > 0
