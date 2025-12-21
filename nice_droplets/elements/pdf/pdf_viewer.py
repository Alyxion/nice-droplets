"""
PDF Viewer component for displaying PDF pages.
"""
import asyncio
import inspect
from typing import List, Literal, Optional, Union, Dict, Any, Callable
import threading
import queue
import time
import os
import io
from pathlib import Path

from nicegui import ui
from nicegui.element import Element
from nice_droplets.elements.doc_view import DocView
from nice_droplets.components.pdf import Pdf
from nice_droplets.elements.pdf.pdf_page_view import PdfPageView as pdf_page
from nice_droplets import dui
from nice_droplets.utils.compat import html as compat_html

class PdfViewer(DocView):
    """A component for displaying PDF pages.
    
    This component can display either a single page at a time or multiple pages
    in a row or column layout.
    """
    
    def __init__(self, 
                 pdf_path: str = None,
                 pdf_data: bytes = None,
                 document: Pdf = None,
                 single_page: bool = True,
                 layout: str = 'vertical',
                 zoom: float = 1.0,
                 dpi: int = 150,
                 fmt: str = 'jpg',
                 jpeg_quality: int = 85,
                 page_splitter_text: str = None,
                 page_shadow: bool = True,
                 **kwargs):
        """Initialize a PdfViewer element.
        
        Args:
            pdf_path: The path to the PDF file to display
            pdf_data: The PDF file data as bytes (optional)
            document: The Pdf object containing the pages to display (optional, if pdf_path or pdf_data is provided)
            single_page: Whether to display only one page at a time
            layout: Layout direction when displaying multiple pages ('horizontal' or 'vertical')
            zoom: Initial zoom level
            dpi: DPI for rendering PDF pages as images
            fmt: Image format for rendering pages ('jpg', 'png', etc.)
            jpeg_quality: JPEG compression quality (if applicable)
        """
        super().__init__(**kwargs)
        
        self.pdf_path = pdf_path
        self.pdf_data = pdf_data
        self.single_page = single_page
        self.layout = layout
        self.zoom = zoom
        self.dpi = dpi
        self.fmt = fmt
        self.jpeg_quality = jpeg_quality
        self.current_page_index = 0
        self.pdf_pages = []
        self.page_splitter_text = page_splitter_text
        self.page_shadow = page_shadow
        self.finished_loading = False
        self._on_pdfs_loaded: list[Callable] = []
        
        # Store global bounding box settings to apply to all pages
        self.show_boundings = False
        self.bounding_style = '1px solid red'
        
        # Background loading variables
        self.loading_thread = None
        self.loading_queue = queue.Queue()
        self.loaded_pages = {}
        self.stop_loading = False
        self._stop_event = threading.Event()
        
        # Create the container for the PDF pages
        self.container = ui.element('div')
        
        # If a document is provided, use it directly
        if document is not None:
            self.document = document
            with self.container:
                if single_page:
                    self._create_single_page_view()
                else:
                    self._create_multi_page_view()
            
            # Start background loading of pages
            self._start_background_loading()
        
        # Otherwise, load the document from the PDF file or bytes
        elif pdf_path is not None or pdf_data is not None:
            # Create the Pdf object and assign to UI immediately
            self.document = Pdf()

            # Prepare placeholders for all expected pages (if possible)
            import pdfplumber
            import io
            total_pages = 1
            try:
                if pdf_data is not None:
                    with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                        total_pages = len(pdf.pages)
                elif pdf_path is not None:
                    with open(pdf_path, "rb") as f:
                        with pdfplumber.open(f) as pdf:
                            total_pages = len(pdf.pages)
            except Exception:
                pass

            self.pdf_pages = []
            for i in range(total_pages):
                placeholder = ui.element('div').classes('pdf-page-placeholder flex justify-center items-center').style('width: 1240px; height: 1755px; background: #f3f4f6; border: 1.5px dashed #d1d5db; border-radius: 8px;')
                with placeholder:
                    ui.label(f'Page {i+1}').classes('text-3xl font-bold text-gray-500')
                self.pdf_pages.append(placeholder)

            def on_page_loaded(page):
                idx = page.page_number - 1
                if 0 <= idx < len(self.pdf_pages):
                    placeholder = self.pdf_pages[idx]
                    placeholder.clear()
                    with placeholder:
                        pdf_page_obj = dui.pdf_page(page, zoom=self.zoom, page_shadow=self.page_shadow)
                        if hasattr(pdf_page_obj, 'set_boundings'):
                            pdf_page_obj.set_boundings(self.show_boundings, self.bounding_style)
                        self.pdf_pages[idx] = pdf_page_obj
                        # apply overlays on loaded page
                        self._apply_overlays()

            def background_load():
                if pdf_data is not None:
                    self.document.load_from_bytes(
                        pdf_bytes=pdf_data,
                        dpi=self.dpi,
                        fmt=self.fmt,
                        jpeg_quality=self.jpeg_quality,
                        on_page_loaded=on_page_loaded,
                        stop_event=self._stop_event
                    )
                elif pdf_path is not None:
                    with open(pdf_path, "rb") as f:
                        self.document.load_from_bytes(
                            pdf_bytes=f.read(),
                            dpi=self.dpi,
                            fmt=self.fmt,
                            jpeg_quality=self.jpeg_quality,
                            on_page_loaded=on_page_loaded,
                            stop_event=self._stop_event
                        )

            self.loading_thread = threading.Thread(
                target=background_load,
                daemon=True
            )
            self.loading_thread.start()
        else:
            # No document or file path or data provided
            self.document = PDFDocument()
            with self.container:
                ui.label('No PDF document provided').classes('text-xl text-center')
        
        # Track which pages have overlays applied
        self._overlays_applied_pages = set()
        # Set up timer to check for loaded pages and overlays
        self._overlay_timer = ui.timer(0.5, self._check_loaded_pages)

    def on_pdfs_loaded(self, callback: Callable):
        self._on_pdfs_loaded.append(callback)
    
    def _update_navigation_controls(self):
        """Update the navigation controls based on the current page index."""
        if self.prev_button and self.next_button and self.page_label:
            self.prev_button._props['disable'] = self.current_page_index == 0
            self.prev_button.update()
            self.next_button._props['disable'] = self.current_page_index == len(self.document.pages) - 1
            self.next_button.update()
            self.page_label.text = f'Page {self.current_page_index + 1} of {len(self.document.pages)}'
    
    def _create_single_page_view(self):
        """Create a view that displays a single page at a time with navigation controls."""
        # Create navigation controls
        with ui.row().classes('w-full justify-center items-center gap-4 mb-2'):
            self.prev_button = ui.button('Previous', icon='arrow_back', on_click=self.previous_page)
            self.page_label = ui.label(f'Page 1 of {len(self.document.pages)}')
            self.next_button = ui.button('Next', icon='arrow_forward', on_click=self.next_page)
            
            # Update button visibility based on current page
            self._update_navigation_controls()
        
        # Create container for the current page
        style = ""
        if self.page_shadow:
            style = "box-shadow: 0 4px 24px rgba(0,0,0,0.10); border: 1.5px solid #e5e7eb; border-radius: 8px; background: #fff;"
        self.page_container = ui.element('div').classes('w-full flex justify-center').style(style)
        
        # Display the first page
        if self.document.pages:
            self._display_current_page()
    
    def _create_multi_page_view(self):
        """Create a view that displays all pages in a row or column."""
        # Create container for all pages
        if self.layout == 'horizontal':
            self.pages_container = ui.row().classes('w-full overflow-x-auto')
        else:  # vertical
            self.pages_container = ui.column().classes('w-full')
        
        # Create placeholders for all pages
        with self.pages_container:
            for i, _ in enumerate(self.document.pages):
                # Add a page splitter before each page except the first
                if i > 0 and self.page_splitter_text:
                    # Format the splitter text with page number (starting at 2)
                    splitter_text = self.page_splitter_text.format(page=i+1)
                    compat_html(
                        f'''
                        <div style="margin: 36px 0 24px 0; padding: 0; border-top: 1.5px solid #d1d5db; display: flex; align-items: center; justify-content: flex-start;">
                            <span style="
                                background: #fff;
                                color: #222;
                                font-size: 1.08em;
                                font-weight: 500;
                                padding: 0 20px;
                                margin-left: 18px;
                                margin-top: -15px;
                                letter-spacing: 0.01em;
                                border-radius: 6px;
                                box-shadow: 0 1px 4px rgba(0,0,0,0.03);
                                border: 1px solid #e5e7eb;
                                display: inline-block;
                            ">
                                {splitter_text}
                            </span>
                        </div>
                        '''
                    )
                # Create a placeholder for the page using the real dimensions if available
                width = 1240
                height = 1755
                page = self.document.pages[i]
                width = getattr(page, "width", 1240)
                height = getattr(page, "height", 1755)
                placeholder = ui.element('div').classes('pdf-page-placeholder flex justify-center items-center').style(f'width: {width}px; height: {height}px; background: #f3f4f6; border: 1.5px dashed #d1d5db; border-radius: 8px;')
                with placeholder:
                    ui.label(f'Page {i+1}').classes('text-3xl font-bold text-gray-500')
                
                # Add the placeholder to the list of pages
                self.pdf_pages.append(placeholder)
        
        # Queue the first few pages for immediate loading
        priority_pages = min(3, len(self.document.pages))
        for i in range(priority_pages):
            self._load_page_in_background(i)
    
    def _display_current_page(self):
        """Display the current page in single page mode."""
        # Clear the container
        self.page_container.clear()
        
        # Create a placeholder for the page
        with self.page_container:
            # Try to get the real page dimensions if available
            width = 1240
            height = 1755
            if self.document.pages and 0 <= self.current_page_index < len(self.document.pages):
                page = self.document.pages[self.current_page_index]
                width = getattr(page, "width", 1240)
                height = getattr(page, "height", 1755)
            placeholder = ui.element('div').classes('pdf-page-placeholder flex justify-center items-center').style(f'width: {width}px; height: {height}px; background: #f3f4f6; border: 1.5px dashed #d1d5db; border-radius: 8px;')
            with placeholder:
                ui.label(f'Page {self.current_page_index+1}').classes('text-3xl font-bold text-gray-500')
            
            # Store the placeholder
            self.pdf_pages = [placeholder]
        
        # Queue the page for loading
        self._load_page_in_background(self.current_page_index)
    
    def _load_page_in_background(self, page_index: int) -> None:
        """Queue a page for background loading.
        
        Args:
            page_index: The index of the page to load
        """
        # Check if the page index is valid
        if not (0 <= page_index < len(self.document.pages)):
            return
        
        # Get the page data
        page_data = self.document.pages[page_index]
        
        # Queue the page for loading
        self.loading_queue.put((page_index, page_data))
    
    def next_page(self):
        """Go to the next page in single page mode."""
        if not self.single_page or self.current_page_index >= len(self.document.pages) - 1:
            return
        
        self.current_page_index += 1
        self._display_current_page()
        self._update_navigation_controls()
    
    def previous_page(self):
        """Go to the previous page in single page mode."""
        if not self.single_page or self.current_page_index <= 0:
            return
        
        self.current_page_index -= 1
        self._display_current_page()
        self._update_navigation_controls()
    
    def go_to_page(self, page_index: int):
        """Go to a specific page in single page mode.
        
        Args:
            page_index: The index of the page to display (0-based)
        """
        if not self.single_page or not (0 <= page_index < len(self.document.pages)):
            return
        
        self.current_page_index = page_index
        self._display_current_page()
    
    def set_zoom(self, zoom: float):
        """Set the zoom level for all pages.
        
        Args:
            zoom: The zoom level (1.0 = 100%)
        """
        self.zoom = zoom
        
        # Update zoom for all displayed pages
        for pdf_page in self.pdf_pages:
            # Check if the page is a PdfPage instance
            if hasattr(pdf_page, 'set_zoom'):
                pdf_page.set_zoom(zoom)

    def set_overlays(self, overlays: List[Dict[str, Any]]):
        self.overlays = overlays
        self._apply_overlays(force=True)
    
    def set_boundings(self, show: bool, style: str = '1px solid red'):
        """Set whether to show bounding boxes and their style for all pages.
        
        Args:
            show: Whether to show bounding boxes around text blocks
            style: CSS border style (e.g., '1px solid red', '2px dashed blue')
        """
        # Store the settings in instance variables
        self.show_boundings = show
        self.bounding_style = style
        
        # Update bounding settings for all currently displayed pages
        for pdf_page in self.pdf_pages:
            # Check if the page is a PdfPage instance
            if hasattr(pdf_page, 'set_boundings'):
                # Recreate the text overlay with the new settings
                pdf_page.set_boundings(show, style)
        
        # also apply overlays after bounding change
        self._apply_overlays()

    def _apply_overlays(self, force: bool = False) -> None:
        """Apply overlays to each page by passing them to PdfPageView, only once per page."""
        all_applied = True
        for idx, page_elem in enumerate(self.pdf_pages):
            # Only apply overlays if not already applied for this page
            if (idx not in self._overlays_applied_pages or force) and hasattr(page_elem, 'set_overlays'):
                overlays = [
                    {k: getattr(o, k) for k in o.__fields__ if k != 'page'}
                    for o in self.overlays
                    if o.page - 1 == idx
                ]
                page_elem.set_overlays(overlays)
                self._overlays_applied_pages.add(idx)
            if idx not in self._overlays_applied_pages:
                all_applied = False
        # Stop the timer if overlays have been applied to all pages
        if all_applied and self._overlay_timer:
            self.finished_loading = True
            self._overlay_timer.cancel()
            for callback in self._on_pdfs_loaded:
                # await if coroutine
                if inspect.iscoroutinefunction(callback):
                    # call async in the background
                    ui.timer(0, callback, once=True)
                else:
                    callback()

    def _start_background_loading(self) -> None:
        """Start background loading of pages."""
        # Queue all pages for loading
        for i, page_data in enumerate(self.document.pages):
            self.loading_queue.put((i, page_data))
        
        # Start the background loading thread
        self.loading_thread = threading.Thread(
            target=self._background_loading_worker,
            daemon=True
        )
        self.loading_thread.start()
    
    def _background_loading_worker(self) -> None:
        """Worker function for background loading of pages."""
        while not self.stop_loading:
            try:
                # Get the next page to load from the queue
                # Use a timeout to allow checking the stop_loading flag
                try:
                    page_index, page_data = self.loading_queue.get(timeout=0.5)
                except queue.Empty:
                    # No more pages to load
                    continue
                
                # Skip if we're stopping
                if self.stop_loading:
                    break
                
                # Process the page data
                # This is the CPU-intensive part that we're doing in the background
                # For example, we might need to decode the image data, extract text, etc.
                # In a real implementation, this would be more complex
                
                # For now, we'll just store the processed page data
                processed_page = {
                    'index': page_index,
                    'data': page_data
                }
                
                # Store the loaded page
                self.loaded_pages[page_index] = processed_page
                
                # Mark the task as done
                self.loading_queue.task_done()
                
                # Sleep a bit to simulate CPU-intensive work
                # This is just for demonstration purposes
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error loading page: {e}")
                # Continue loading other pages even if one fails
                continue
    
    def _check_loaded_pages(self) -> None:
        """Check for loaded pages and update the UI."""
        # Check if the document has been loaded
        if hasattr(self, 'document_loaded') and self.document_loaded:  # hasattr check, can be ui.element
            if not hasattr(self, 'document_ui_updated') or not self.document_ui_updated:
                # Clear the loading placeholder
                self.container.clear()
                
                # Create the view
                with self.container:
                    if self.single_page:
                        self._create_single_page_view()
                    else:
                        self._create_multi_page_view()
                
                # Start background loading of pages
                self._start_background_loading()
                
                # Mark the UI as updated
                self.document_ui_updated = True
                
                # Return early since we just updated the UI
                return
        elif hasattr(self, 'document_loaded') and not self.document_loaded and hasattr(self, 'load_error'):
            # Document failed to load, show error
            if not hasattr(self, 'error_ui_updated') or not self.error_ui_updated:
                # Clear the loading placeholder
                self.container.clear()
                
                # Show an error message
                with self.container:
                    ui.label(f"Error loading PDF: {self.load_error}").classes('text-xl text-center text-red-500')
                
                # Mark the error UI as updated
                self.error_ui_updated = True
                
                # Return early since we just updated the UI
                return
        
        # Check for loaded pages
        # In single page mode, check if the current page is loaded
        if self.single_page:
            if self.current_page_index in self.loaded_pages:
                # Get the loaded page data
                loaded_page = self.loaded_pages[self.current_page_index]
                page_data = loaded_page['data']
                
                # Remove it from the loaded pages
                del self.loaded_pages[self.current_page_index]
                
                # Clear the container
                self.page_container.clear()
                
                # Create the actual PDF page
                with self.page_container:
                    pdf_page_obj = dui.pdf_page(page_data, zoom=self.zoom, page_shadow=self.page_shadow)
                    
                    # Apply the global bounding box settings
                    if hasattr(pdf_page_obj, 'set_boundings'):
                        pdf_page_obj.set_boundings(self.show_boundings, self.bounding_style)
                    
                    # Store the page and update self.pdf_pages to remove any lingering placeholder
                    self.pdf_pages = [pdf_page_obj]
        
        # In multi-page mode, check if any pages are loaded
        elif hasattr(self, 'pages_container'):
            # Get all loaded pages
            loaded_indices = list(self.loaded_pages.keys())
            
            # Update the UI with the loaded pages
            for index in loaded_indices:
                if index < len(self.pdf_pages):
                    pdf_page_obj = None
                    try:
                        # Get the loaded page data
                        loaded_page = self.loaded_pages[index]
                        page_data = loaded_page['data']
                        
                        # Remove it from the loaded pages
                        del self.loaded_pages[index]
                        
                        # Get the placeholder
                        placeholder = self.pdf_pages[index]
                        
                        # Clear the placeholder
                        placeholder.clear()
                        
                        # Create a new PDF page in the placeholder
                        with placeholder:
                            pdf_page_obj = dui.pdf_page(page_data, zoom=self.zoom, page_shadow=self.page_shadow)
                            
                            # Apply the global bounding box settings
                            if hasattr(pdf_page_obj, 'set_boundings'):
                                pdf_page_obj.set_boundings(self.show_boundings, self.bounding_style)
                        
                        # Store the page only if successfully created
                        if pdf_page_obj is not None:
                            self.pdf_pages[index] = pdf_page_obj
                    except Exception as e:
                        print(f"Error updating page {index}: {e}")
                        # Ensure we do not reference pdf_page_obj if not assigned
                        continue
        
        # apply overlays for newly loaded pages
        self._apply_overlays()

    
    def _load_pdf_file(self) -> None:
        """Load the PDF file in a background thread using PDFDocument's loader with cancellation support."""
        try:
            if self.pdf_path is not None:
                self.document = Pdf.from_file(
                    pdf_path=self.pdf_path,
                    dpi=self.dpi,
                    fmt=self.fmt,
                    jpeg_quality=self.jpeg_quality,
                    stop_event=self._stop_event
                )
            elif self.pdf_data is not None:
                self.document = Pdf.from_bytes(
                    pdf_bytes=self.pdf_data,
                    dpi=self.dpi,
                    fmt=self.fmt,
                    jpeg_quality=self.jpeg_quality,
                    stop_event=self._stop_event
                )
            else:
                self.document = Pdf()
            self.document_loaded = True
        except Exception as e:
            print(f"Error loading PDF file: {e}")
            self.document_loaded = False
            self.load_error = str(e)

    
    def _delete(self) -> None:        
        """Clean up resources when the element is deleted."""
        print("Cleaning up")
        # Stop the background loading thread
        self.stop_loading = True
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        
        # Wait for the thread to finish
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)
        
        # Call the parent's _delete method
        super()._delete()
