import io
import os
import pytest
from nice_droplets.elements.pdf.pdf_viewer import PdfViewer
from nice_droplets.components.pdf import Pdf, PdfPage, PdfTextBlock
from nicegui import ui
from nicegui.testing import Screen


def test_pdf_viewer_with_pdf_data(screen: Screen):
    """Test PdfViewer with PDF data bytes."""
    path = os.path.dirname(__file__)
    pdf_bytes = open(path + '/data/test_pdf.pdf', 'rb').read()
    viewer_ref = []

    @ui.page('/')
    def page():
        viewer = PdfViewer(pdf_data=pdf_bytes, single_page=True)
        viewer_ref.append(viewer)

    screen.open('/')
    screen.wait(0.3)

    # Check initial state
    viewer = viewer_ref[0]
    assert viewer.pdf_data == pdf_bytes
    assert viewer.single_page is True

    # Check that the document object was created
    assert isinstance(viewer.document, Pdf)
