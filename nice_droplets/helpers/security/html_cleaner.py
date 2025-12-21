from bleach.sanitizer import Cleaner, ALLOWED_PROTOCOLS
from bleach.css_sanitizer import CSSSanitizer
import bleach

class HtmlCleaner:
    """Helper class to remove malicious content from HTML content."""

    _default_cleaner = None

    def __init__(self) -> None:
        # Add support for data: URIs
        ALLOWED_PROTOCOLS = list(bleach.sanitizer.ALLOWED_PROTOCOLS) + ['data', 'cid']
        # Define allowed tags
        ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
            'p', 'div', 'span', 'br', 'hr', 'style', 'meta', 'html', 'body', 'head', 'img', 'a', 'ul', 'li',
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'col', 'colgroup', 'caption', 'thead', 'tbody', 'tfoot',
            'b', 'u', 'link', 'center', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'font', 'title'
        ]
        # Define allowed attributes
        ALLOWED_ATTRIBUTES = {
            '*': ['style', 'class', 'id', 'dir'],
            'a': ['href', 'title', 'name'],
            'img': ['src', 'alt', 'title', 'style'],
        }
        # Define allowed CSS properties
        ALLOWED_STYLES = [
            'color', 'font-weight', 'font-size', 'font-family', 'text-align', 'background-color',
            'margin', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom',
            'padding', 'padding-left', 'padding-right', 'padding-top', 'padding-bottom',
            'border', 'border-color', 'border-width', 'border-style',
            'line-height', 'text-decoration', 'width', 'height', 'max-width'
        ]
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=ALLOWED_STYLES
        )
        # THIS IS THE FIX: Use Cleaner instead of bleach.clean()
        self.cleaner = Cleaner(
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            css_sanitizer=css_sanitizer,
            strip=False,
            strip_comments=True
        )

    @classmethod
    def clean_default(cls, html_content):
        return cls._default_cleaner.clean(html_content)

    def clean(self, html_content):
        return self.cleaner.clean(html_content)

    def __call__(self, html_content):
        return self.clean(html_content)    

HtmlCleaner._default_cleaner = HtmlCleaner()