from typing import List, Optional
import typing
from nicegui.element import Element

if typing.TYPE_CHECKING:
    from nice_droplets.elements.pdf.doc_overlay_element import DocOverlayElement


class DocView(Element):
    """Base class for document viewers with overlay support."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # overlays: list of dict with keys: name, page, x, y, width, height, color
        self.overlays: List["DocOverlayElement"] = []
        # mapping page index to DocOverlay instance
        self._overlay_objs: Dict[int, object] = {}

    def set_overlays(self, overlays: List["DocOverlayElement"]) -> None:
        """Replace all overlays."""
        self.overlays = overlays
        self._apply_overlays()

    def add_overlay(self, overlay: "DocOverlayElement") -> None:
        """Add a single overlay."""
        self.overlays.append(overlay)
        self._apply_overlays()

    def add_overlays(self, overlays: List["DocOverlayElement"]) -> None:
        """Add a list of overlays."""
        self.overlays.extend(overlays)
        self._apply_overlays()

    def remove_overlays(self, page_index: Optional[int] = None, name_filter: Optional[str] = None) -> None:
        """Remove overlays by page index or name filter."""
        self.overlays = [o for o in self.overlays if not (
            (page_index is not None and o.page == page_index) or
            (name_filter is not None and name_filter in (o.name or ''))
        )]
        self._apply_overlays()

    def _apply_overlays(self) -> None:
        """Apply overlays to each page. Should be overridden by subclasses."""
        pass
