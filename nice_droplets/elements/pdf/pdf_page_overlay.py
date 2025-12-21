from typing import List, Dict, Any, override
from nicegui.element import Element

class PdfPageOverlay(Element, component='pdf_page_overlay.js'):
    """Combined text and rectangle overlays for a PDF page."""

    def __init__(self,
                 text_blocks: List[Dict[str, Any]],
                 overlays: List[Dict[str, Any]],
                 show_boundings: bool = False,
                 bounding_style: str = '1px solid red',
                 **kwargs):
        super().__init__(**kwargs)
        self._props['textBlocks'] = text_blocks
        self._props['showBoundings'] = show_boundings
        self._props['boundingStyle'] = bounding_style
        self._props['overlays'] = overlays

    def set_text_blocks(self, text_blocks: List[Dict[str, Any]]) -> None:
        self._props['textBlocks'] = text_blocks
        self.update()

    def set_overlays(self, overlays: List[Dict[str, Any]]) -> None:
        self._props['overlays'] = overlays
        self.update()

    def set_boundings(self, show: bool, style: str = '1px solid red') -> None:
        self._props['showBoundings'] = show
        self._props['boundingStyle'] = style
        self.update()

    def adjust_text_and_overlay_scaling(self) -> None:
        self.run_method('adjustTextAndOverlayScaling')

    @override
    def update(self) -> None:
        return super().update()
