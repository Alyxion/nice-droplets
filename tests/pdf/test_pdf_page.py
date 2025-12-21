import pytest
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

from nicegui import ui
from nicegui.testing import Screen
from nice_droplets.elements.pdf.pdf_page_view import PdfPageView as PdfPageElement
from nice_droplets.components.pdf import PdfPage as PdfPageModel, PdfTextBlock, Pdf

# Path to the test PDF file
TEST_PDF_PATH = Path(__file__).parent / 'data' / 'test_pdf.pdf'


def extract_page_data(pdf_path, page_num) -> PdfPageModel:
    """Extract image and text blocks from a PDF page."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # Create a PdfPage data model object
    page_data = PdfPageModel(
        page_number=page_num + 1,
        width=int(page.rect.width),
        height=int(page.rect.height),
        display_width=int(page.rect.width),
        display_height=int(page.rect.height)
    )
    
    # Get page image
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    page_data.set_image(img_bytes)
    
    # Get text blocks
    text_blocks = []
    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_blocks.append(PdfTextBlock(
                        text=span["text"],
                        x=span["bbox"][0],
                        y=span["bbox"][1],
                        width=span["bbox"][2] - span["bbox"][0],
                        height=span["bbox"][3] - span["bbox"][1],
                        font_size=span["size"],
                        font_name=span["font"]
                    ))
    
    page_data.text_blocks = text_blocks
    return page_data


def test_pdf_page_creation(screen: Screen):
    """Test that PdfPage can be created with valid parameters."""
    # Create a test image
    img = Image.new('RGB', (100, 100), color='white')

    # Create a PdfPage object
    page_data = PdfPageModel(
        page_number=1,
        width=100,
        height=100,
        display_width=100,
        display_height=100,
        text_blocks=[PdfTextBlock(
            text="Test",
            x=10,
            y=10,
            width=50,
            height=20,
            font_size=12
        )]
    )
    page_data.set_image(img)
    pdf_page_ref = []

    @ui.page('/')
    def page():
        pdf_page = PdfPageElement(page_data)
        pdf_page_ref.append(pdf_page)

    screen.open('/')
    screen.wait(0.3)

    # Verify the properties
    pdf_page = pdf_page_ref[0]
    assert pdf_page._props['width'] == 100
    assert pdf_page._props['height'] == 100
    assert pdf_page.overlay_component is not None
    assert len(pdf_page.overlay_component._props['textBlocks']) == 1
    # textBlocks can be either dicts or PdfTextBlock objects
    text_block = pdf_page.overlay_component._props['textBlocks'][0]
    if isinstance(text_block, dict):
        assert text_block['text'] == "Test"
    else:
        assert text_block.text == "Test"
    assert 'imgSrc' in pdf_page._props
    assert pdf_page._props['imgSrc'].startswith('data:image/png;base64,')


def test_pdf_page_first_page_content(screen: Screen):
    """Test that the first page of the PDF contains the word 'Brass'."""
    page_data = extract_page_data(TEST_PDF_PATH, 0)

    # Check if any text block contains "Brass"
    brass_blocks = [block for block in page_data.text_blocks if "Brass" in block.text]
    assert len(brass_blocks) > 0, "First page should contain the word 'Brass'"

    # Create a PdfPage with the first page
    @ui.page('/')
    def page():
        PdfPageElement(page_data)

    # Open the page and verify it renders
    screen.open('/')
    screen.wait(0.3)

    # Check if the page contains an image
    img_element = screen.find_by_class('pdf-page-image')
    assert img_element is not None

    # Check if text blocks are rendered
    text_elements = screen.find_all_by_class('pdf-text-block')
    assert len(text_elements) > 0

    # Find the text block containing "Brass"
    brass_text = None
    for block in page_data.text_blocks:
        if "Brass" in block.text:
            brass_text = block.text
            break

    assert brass_text is not None
    # Verify the text is in the rendered page (checking DOM content)
    page_content = screen.selenium.page_source
    assert "Brass" in page_content, "The word 'Brass' should be visible on the page"


def test_pdf_page_second_page_content(screen: Screen):
    """Test that the second page of the PDF contains the word 'Certifications'."""
    page_data = extract_page_data(TEST_PDF_PATH, 1)

    # Check if any text block contains "Certifications"
    cert_blocks = [block for block in page_data.text_blocks if "Certifications" in block.text]
    assert len(cert_blocks) > 0, "Second page should contain the word 'Certifications'"

    # Create a PdfPage with the second page
    @ui.page('/')
    def page():
        PdfPageElement(page_data)

    # Open the page and verify it renders
    screen.open('/')
    screen.wait(0.3)

    # Check if the page contains an image
    img_element = screen.find_by_class('pdf-page-image')
    assert img_element is not None

    # Check if text blocks are rendered
    text_elements = screen.find_all_by_class('pdf-text-block')
    assert len(text_elements) > 0

    # Find the text block containing "Certifications"
    cert_text = None
    for block in page_data.text_blocks:
        if "Certifications" in block.text:
            cert_text = block.text
            break

    assert cert_text is not None
    # Verify the text is in the rendered page (checking DOM content)
    page_content = screen.selenium.page_source
    assert "Certifications" in page_content, "The word 'Certifications' should be visible on the page"


def test_pdf_page_zoom_functionality(screen: Screen):
    """Test that the zoom functionality of PdfPage works correctly."""
    page_data = extract_page_data(TEST_PDF_PATH, 0)
    
    @ui.page('/')
    def page():
        pdf_page = PdfPageElement(page_data)
        ui.button('Zoom In', on_click=lambda: pdf_page.set_zoom(1.5))
        ui.button('Zoom Out', on_click=lambda: pdf_page.set_zoom(0.8))
    
    # Open the page and verify it renders
    screen.open('/')
    
    # Check initial zoom
    container = screen.find_by_class('pdf-page-container')
    initial_transform = container.get_attribute('style')
    assert 'scale(1)' in initial_transform or 'scale(1.0)' in initial_transform
    
    # Test zoom in
    screen.click('Zoom In')
    screen.wait(0.3)
    container = screen.find_by_class('pdf-page-container')
    zoomed_in_transform = container.get_attribute('style')
    assert 'scale(1.5)' in zoomed_in_transform
    
    # Test zoom out
    screen.click('Zoom Out')
    screen.wait(0.3)
    container = screen.find_by_class('pdf-page-container')
    zoomed_out_transform = container.get_attribute('style')
    assert 'scale(0.8)' in zoomed_out_transform


def test_pdf_page_boundings(screen: Screen):
    """Test that the bounding boxes can be toggled and styled."""
    page_data = extract_page_data(TEST_PDF_PATH, 0)
    
    @ui.page('/')
    def page():
        pdf_page = PdfPageElement(page_data)
        ui.button('Show Boundings', on_click=lambda: pdf_page.set_boundings(True))
        ui.button('Blue Dashed', on_click=lambda: pdf_page.set_boundings(True, '2px dashed blue'))
    
    # Open the page and verify it renders
    screen.open('/')
    
    # Check initial state (boundings should be off)
    text_blocks_elements = screen.find_all_by_class('pdf-text-block')
    for element in text_blocks_elements:
        style = element.get_attribute('style')
        assert 'border: none' in style or 'border:none' in style
    
    # Toggle boundings on
    screen.click('Show Boundings')
    screen.wait(0.3)
    
    # Check boundings are on with default style (red borders)
    text_blocks_elements = screen.find_all_by_class('pdf-text-block')
    for element in text_blocks_elements:
        style = element.get_attribute('style')
        assert 'border: 1px solid red' in style or 'border:1px solid red' in style
    
    # Change to blue dashed style
    screen.click('Blue Dashed')
    screen.wait(0.3)
    
    # Check boundings style has changed
    text_blocks_elements = screen.find_all_by_class('pdf-text-block')
    for element in text_blocks_elements:
        style = element.get_attribute('style')
        assert 'border: 2px dashed blue' in style or 'border:2px dashed blue' in style


def test_pdf_document():
    """Test the Pdf class."""
    # Create a document with multiple pages
    page1 = extract_page_data(TEST_PDF_PATH, 0)
    page2 = extract_page_data(TEST_PDF_PATH, 1)

    doc = Pdf(pages=[page1, page2])

    # Test document properties
    assert len(doc.pages) == 2

    # Verify page content
    brass_blocks = [block for block in doc.pages[0].text_blocks if "Brass" in block.text]
    assert len(brass_blocks) > 0

    cert_blocks = [block for block in doc.pages[1].text_blocks if "Certifications" in block.text]
    assert len(cert_blocks) > 0
