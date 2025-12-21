from typing import Optional, Union, List, Dict

from nicegui import ui
from nicegui.element import Element
from PIL import Image

from nice_droplets.components.pdf import PdfPage, PdfTextBlock
from nice_droplets.elements.pdf.pdf_page_overlay import PdfPageOverlay


class PdfPageView(Element, component='pdf_page.js'):
    """A custom NiceGUI element for displaying a PDF page with text overlay.
    
    This element displays a PDF page as an image with text blocks overlaid on top,
    allowing for text selection while maintaining the exact visual appearance of the PDF.
    """
    
    def __init__(self, 
                 page_data: PdfPage,
                 zoom: float = 1.0,
                 page_shadow: bool = True,
                 **kwargs):
        """Initialize a PdfPage element.
        
        Args:
            page_data: The PdfPage object containing the page information
            zoom: Initial zoom level
            page_shadow: Whether to show a shadow and border around the page
        """
        super().__init__(**kwargs)
        
        if page_shadow:
            self.style(
                "box-shadow: 0 4px 24px rgba(0,0,0,0.10); border: 1.5px solid #e5e7eb; border-radius: 8px; background: #fff;"
            )
        
        self.page_data = page_data
        self.overlay_component = None
        self.show_boundings = False
        self.bounding_style = '1px solid red'
        
        # Set props for the JavaScript component
        self._props['imgSrc'] = page_data.img_base64
        self._props['width'] = page_data.width
        self._props['height'] = page_data.height
        self._props['zoom'] = zoom
        
        # Create combined overlay component (text + rectangles)
        self._create_page_overlay()
    
    def _create_page_overlay(self) -> None:
        """Create the combined text and rectangle overlay component."""
        self.clear()
        with self:
            self.overlay_component = PdfPageOverlay(
                text_blocks=self.page_data.text_blocks,
                overlays=[],
                show_boundings=self.show_boundings,
                bounding_style=self.bounding_style
            )
    
    def set_zoom(self, zoom: float) -> None:
        """Set the zoom level of the PDF page.
        
        Args:
            zoom: The zoom level (1.0 = 100%)
        """
        self._props['zoom'] = zoom
        self.update()
    
    def set_boundings(self, show: bool, style: str = '1px solid red') -> None:
        """Set whether to show bounding boxes and their style.
        
        Args:
            show: Whether to show bounding boxes around text blocks
            style: CSS border style (e.g., '1px solid red', '2px dashed blue')
        """
        self.show_boundings = show
        self.bounding_style = style
        
        # Update the text overlay
        if self.overlay_component:
            self.overlay_component.set_boundings(show, style)
        else:
            # Recreate the text overlay if it doesn't exist
            self._create_page_overlay()
    
    def update_text_blocks(self, text_blocks: List[PdfTextBlock]) -> None:
        """Update the text blocks without refreshing the image.
        
        This method allows for dynamic updates to the text blocks without
        requiring a full refresh of the component, which would also reload the image.
        
        Args:
            text_blocks: The new list of text blocks to display
        """
        # Update the page_data object
        self.page_data.text_blocks = text_blocks
        
        # Update the text overlay
        if self.overlay_component:
            self.overlay_component.set_text_blocks(text_blocks)
        else:
            # Recreate the text overlay if it doesn't exist
            self._create_page_overlay()
    
    def adjust_text_scaling(self) -> None:
        """Manually trigger text scaling adjustment."""
        if self.overlay_component:
            self.overlay_component.adjust_text_and_overlay_scaling()

    def set_overlays(self, overlays: List[Dict]) -> None:
        """Set rectangle overlays in the combined overlay component."""
        if self.overlay_component:
            self.overlay_component.set_overlays(overlays)
        else:
            self._create_page_overlay()
