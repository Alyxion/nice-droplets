"""
PDF data structures: PdfTextBlock (dataclass), PdfPage and Pdf (Pydantic models).
"""
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Union
from PIL import Image
import base64
import io
from pydantic import BaseModel, Field, root_validator

import logging
# suppress PyPDF2 and pdfminer CropBox/MediaBox warnings
logging.getLogger("PyPDF2").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)

@dataclass
class PdfTextBlock:
    """Represents a single text block in a PDF page."""
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: float
    font_name: Optional[str] = None

class PdfPage(BaseModel):
    """Represents a single page of a PDF document with image and text data."""
    page_number: int
    width: int  # rasterized image width in pixels (from DPI)
    height: int  # rasterized image height in pixels (from DPI)
    display_width: int  # display width in pixels (fixed, independent of DPI)
    display_height: int  # display height in pixels (fixed, independent of DPI)
    text_blocks: List[PdfTextBlock] = Field(default_factory=list)
    img_bytes: Optional[bytes] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def convert_text_blocks(cls, values):
        # Convert text_blocks from dicts if needed
        blocks = values.get("text_blocks", [])
        processed = []
        for block in blocks:
            if isinstance(block, dict):
                processed.append(PdfTextBlock(**block))
            else:
                processed.append(block)
        values["text_blocks"] = processed
        return values

    def set_image(self, img_data: Union[bytes, Image.Image]) -> None:
        """Set the image data for the page."""
        if isinstance(img_data, Image.Image):
            img_buffer = io.BytesIO()
            img_data.save(img_buffer, format='PNG')
            self.img_bytes = img_buffer.getvalue()
        else:
            self.img_bytes = img_data

    @property
    def img_base64(self) -> str:
        """Get the image data as a base64-encoded string."""
        if not self.img_bytes:
            return ""
        img_b64 = base64.b64encode(self.img_bytes).decode('ascii')
        return f"data:image/png;base64,{img_b64}"

    def get_text_blocks_dicts(self) -> List[Dict[str, Any]]:
        """Get the text blocks as a list of dictionaries for the frontend."""
        return [asdict(block) for block in self.text_blocks]

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class Pdf(BaseModel):
    """Represents a complete PDF document with multiple pages."""
    pages: List[PdfPage] = Field(default_factory=list)

    def load_from_bytes(
        self,
        pdf_bytes: bytes,
        dpi: int = 150,
        fmt: Optional[str] = 'jpg',
        jpeg_quality: int = 85,
        x_tolerance_ratio: Optional[float] = None,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        on_page_loaded: Optional[callable] = None,
        stop_event: Optional["threading.Event"] = None,
    ):
        """
        Loads PDF pages from bytes, adding each page to self.pages as soon as it's ready.
        For each page, plumber and convert_from_bytes are run in parallel using threads.
        Calls on_page_loaded(page) after each page is added.
        """
        import pdfplumber
        from pdf2image import convert_from_bytes
        import io
        import os

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)
            s_page = start_page if start_page is not None else 1
            if end_page is not None:
                e_page = min(end_page, total_pages) + 1
            else:
                e_page = total_pages + 1
            page_indices = list(range(s_page - 1, e_page - 1))

            for idx, page_num in enumerate(page_indices):
                if stop_event is not None and stop_event.is_set():
                    break

                plumber_page = [None]
                image = [None]
                width = [None]
                height = [None]

                def extract_text():
                    plumber_page[0] = pdf.pages[page_num]

                def extract_image():
                    if fmt is not None:
                        jpegopt = {'quality': jpeg_quality} if fmt and fmt.lower() == 'jpg' else None
                        img = convert_from_bytes(
                            pdf_bytes,
                            dpi=dpi,
                            fmt=fmt,
                            jpegopt=jpegopt,
                            first_page=page_num + 1,
                            last_page=page_num + 1,
                            thread_count=1
                        )[0]
                        image[0] = img
                        width[0], height[0] = img.size

                t1 = threading.Thread(target=extract_text)
                t2 = threading.Thread(target=extract_image)
                t1.start()
                t2.start()
                t1.join()
                t2.join()

                if plumber_page[0] is None:
                    continue

                if fmt is not None and image[0] is not None:
                    w, h = width[0], height[0]
                else:
                    w = int(plumber_page[0].width * dpi / 72.0)
                    h = int(plumber_page[0].height * dpi / 72.0)

                # Calculate display size based on PDF points, fixed screen DPI, and zoom
                screen_dpi = 96.0  # typical screen DPI
                zoom = 1.0  # can be parameterized if needed
                pdf_width_pts = plumber_page[0].width
                pdf_height_pts = plumber_page[0].height
                display_width = int(pdf_width_pts * screen_dpi / 72.0 * zoom)
                display_height = int(pdf_height_pts * screen_dpi / 72.0 * zoom)

                page_data = PdfPage(
                    page_number=page_num + 1,
                    width=w,
                    height=h,
                    display_width=display_width,
                    display_height=display_height
                )
                if fmt is not None and image[0] is not None:
                    img_buffer = io.BytesIO()
                    image[0].save(
                        img_buffer,
                        format=fmt.upper() if fmt and fmt.lower() != 'jpg' else 'JPEG',
                        quality=jpeg_quality if fmt and fmt.lower() == 'jpg' else None
                    )
                    page_data.set_image(img_buffer.getvalue())

                # Text extraction
                text_blocks = []
                if x_tolerance_ratio is None:
                    words = plumber_page[0].extract_words(
                        x_tolerance=8,
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    )
                else:
                    words = plumber_page[0].extract_words(
                        x_tolerance_ratio=x_tolerance_ratio,
                        y_tolerance=3,
                        keep_blank_chars=False,
                        use_text_flow=False
                    )

                scale_factor = dpi / 72.0
                for word in words:
                    if stop_event is not None and stop_event.is_set():
                        break
                    x0, top, x1, bottom = word['x0'], word['top'], word['x1'], word['bottom']
                    text = word['text']
                    font_size = (bottom - top) * scale_factor * 0.9
                    x0 *= scale_factor
                    top *= scale_factor
                    x1 *= scale_factor
                    bottom *= scale_factor
                    text_blocks.append(PdfTextBlock(
                        text=text,
                        x=x0,
                        y=top,
                        width=x1 - x0,
                        height=bottom - top,
                        font_size=font_size,
                        font_name="sans-serif"
                    ))
                page_data.text_blocks = text_blocks
                self.pages.append(page_data)
                if on_page_loaded:
                    on_page_loaded(page_data)

    @staticmethod
    def from_bytes(
        *,
        pdf_bytes: bytes,
        dpi: int = 150,
        fmt: Optional[str] = 'jpg',
        jpeg_quality: int = 85,
        stop_event: Optional["threading.Event"] = None,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        thread_count: Optional[int] = None
    ) -> "Pdf":
        """
        Extract PDF pages from bytes and return a Pdf object.
        If stop_event is set and stop_event.is_set() becomes True, loading will be cancelled.
        If fmt is None, no images are extracted (only text).
        start_page and end_page are 1-based and inclusive; if not set, all pages are loaded.
        thread_count sets the number of threads for convert_from_bytes (default: all CPUs).
        """
        pdf = Pdf()
        pdf.load_from_bytes(
            pdf_bytes=pdf_bytes,
            dpi=dpi,
            fmt=fmt,
            jpeg_quality=jpeg_quality,
            start_page=start_page,
            end_page=end_page,
            stop_event=stop_event
        )
        return pdf

    @staticmethod
    def from_file(
        *,
        pdf_path: str,
        dpi: int = 150,
        fmt: Optional[str] = 'jpg',
        jpeg_quality: int = 85,
        stop_event: Optional["threading.Event"] = None,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        thread_count: Optional[int] = None
    ) -> "Pdf":
        """
        Load a PDF from a file path and return a Pdf object.
        If stop_event is set and stop_event.is_set() becomes True, loading will be cancelled.
        If fmt is None, no images are extracted (only text).
        start_page and end_page are 1-based and inclusive; if not set, all pages are loaded.
        thread_count sets the number of threads for convert_from_bytes (default: all CPUs).
        """
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        return Pdf.from_bytes(
            pdf_bytes=pdf_bytes,
            dpi=dpi,
            fmt=fmt,
            jpeg_quality=jpeg_quality,
            stop_event=stop_event,
            start_page=start_page,
            end_page=end_page,
            thread_count=thread_count
        )
