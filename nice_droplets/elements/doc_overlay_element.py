from pydantic import BaseModel, Field
from typing import Optional

class DocOverlayElement(BaseModel):
    """
    Represents an overlay element which highlights a region of a document page.
    """
    page: int = Field(description="Page number (1-indexed)", ge=1)
    x: float = Field(description="Left position as percent of page width (0.0 .. 1.0)")
    y: float = Field(description="Top position as percent of page height (0.0 .. 1.0)")
    width: float = Field(description="Width as percent of page width (0.0 .. 1.0)")
    height: float = Field(description="Height as percent of page height (0.0 .. 1.0)")
    color: Optional[str] = Field('red', description="Overlay border color")
    background_color: Optional[str] = Field(None, description="Overlay background color")
    name: Optional[str] = Field(None, description="Optional overlay name")
