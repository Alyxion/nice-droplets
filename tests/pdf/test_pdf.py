import os
import pytest
from nice_droplets.components.pdf import Pdf

TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "data/test_pdf.pdf")

def test_load_all_pages_with_images():
    pdf = Pdf.from_file(pdf_path=TEST_PDF_PATH, fmt="jpg")
    assert len(pdf.pages) > 0
    for page in pdf.pages:
        assert page.img_bytes is not None
        assert isinstance(page.page_number, int)
        assert page.width > 0 and page.height > 0

def test_load_all_pages_no_images():
    pdf = Pdf.from_file(pdf_path=TEST_PDF_PATH, fmt=None)
    assert len(pdf.pages) > 0
    # Check for expected text on page 1 and 2
    expected_texts = [
        ("Materials", 0),
        ("Brass", 0),
        ("Steel", 0),
        ("Certifications", 1),
        ("Applications", 1),
    ]
    for text, page_idx in expected_texts:
        found = any(text in block.text for block in pdf.pages[page_idx].text_blocks)
        assert found, f"Expected text '{text}' not found on page {page_idx+1}"
    for page in pdf.pages:
        assert page.img_bytes is None
        assert isinstance(page.page_number, int)
        assert page.width > 0 and page.height > 0
        # Check that at least one text block has reasonable coordinates
        assert any(
            0 <= block.x < page.width and
            0 <= block.y < page.height and
            block.width > 0 and block.height > 0
            for block in page.text_blocks
        ), f"No text block with reasonable coordinates on page {page.page_number}"

def test_load_page_range():
    pdf = Pdf.from_file(pdf_path=TEST_PDF_PATH, fmt="jpg", start_page=2, end_page=3)
    # The test PDF has only 2 pages, so only page 2 should be returned
    assert len(pdf.pages) == 1
    assert pdf.pages[0].page_number == 2

def test_page_number_and_text_blocks():
    pdf = Pdf.from_file(pdf_path=TEST_PDF_PATH, fmt=None)
    for idx, page in enumerate(pdf.pages):
        assert page.page_number == idx + 1
        assert isinstance(page.text_blocks, list)
        # Check that text blocks are not empty for the first two pages
        if idx < 2:
            assert len(page.text_blocks) > 0
