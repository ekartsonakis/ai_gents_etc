"""
Browser module - Playwright wrapper for browser automation.
Supports real browser interaction with JavaScript enabled.
"""

from playwright.sync_api import sync_playwright, Browser as PlaywrightBrowser
from playwright.sync_api import BrowserContext, Page
from typing import Optional, Dict, Any, List
import time


class Browser:
    """Playwright browser wrapper for automation."""

    def __init__(self, headless: bool = False):
        """
        Initialize browser.

        Args:
            headless: If True, run in headless mode. Default False for user interaction.
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[PlaywrightBrowser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self):
        """Start Playwright and launch browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        return self

    def open(self, url: str, wait_until: str = "load"):
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to.
            wait_until: Wait until event ('load', 'domcontentloaded', 'networkidle').
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        self.page.goto(url, wait_until=wait_until)
        return self

    def click(self, selector: str, timeout: int = 30000):
        """
        Click an element.

        Args:
            selector: CSS or XPath selector.
            timeout: Timeout in milliseconds.
        """
        self.page.click(selector, timeout=timeout)
        return self

    def fill(self, selector: str, value: str, timeout: int = 30000):
        """
        Fill an input field.

        Args:
            selector: CSS or XPath selector.
            value: Value to fill.
            timeout: Timeout in milliseconds.
        """
        self.page.fill(selector, value, timeout=timeout)
        return self

    def type(self, selector: str, text: str, delay: int = 50):
        """
        Type text with a delay between keystrokes.

        Args:
            selector: CSS or XPath selector.
            text: Text to type.
            delay: Delay between keystrokes in ms.
        """
        self.page.type(selector, text, delay=delay)
        return self

    def select(self, selector: str, value: str):
        """
        Select an option from a dropdown.

        Args:
            selector: CSS or XPath selector.
            value: Value to select.
        """
        self.page.select_option(selector, value)
        return self

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """
        Wait for an element to appear.

        Args:
            selector: CSS or XPath selector.
            timeout: Timeout in milliseconds.
        """
        self.page.wait_for_selector(selector, timeout=timeout)
        return self

    def wait_for_load_state(self, state: str = "load"):
        """
        Wait for a specific load state.

        Args:
            state: 'load', 'domcontentloaded', or 'networkidle'.
        """
        self.page.wait_for_load_state(state)
        return self

    def screenshot(self, path: str = None, full_page: bool = False) -> Optional[bytes]:
        """
        Take a screenshot.

        Args:
            path: Path to save screenshot. If None, returns bytes.
            full_page: If True, capture full scrollable page.

        Returns:
            Screenshot bytes if path is None, else None.
        """
        return self.page.screenshot(path=path, full_page=full_page)

    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return self.page.text_content(selector)

    def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        """Get an attribute from an element."""
        return self.page.get_attribute(selector, attr)

    def evaluate(self, script: str) -> Any:
        """Execute JavaScript in the page context."""
        return self.page.evaluate(script)

    def get_html(self) -> str:
        """Get the page HTML."""
        return self.page.content()

    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.is_visible(selector)

    def is_enabled(self, selector: str) -> bool:
        """Check if an element is enabled."""
        return self.page.is_enabled(selector)

    def download_file(self, url: str, path: str):
        """Download a file from URL."""
        import urllib.request
        urllib.request.urlretrieve(url, path)

    def scroll_down(self, pixels: int = 500):
        """Scroll down the page."""
        self.page.evaluate(f"window.scrollBy(0, {pixels})")

    def scroll_up(self, pixels: int = 500):
        """Scroll up the page."""
        self.page.evaluate(f"window.scrollBy(0, -{pixels})")

    def wait(self, seconds: float):
        """Wait for specified seconds."""
        time.sleep(seconds)

    def close(self):
        """Close browser and Playwright."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions for quick operations
def quick_open(url: str, headless: bool = False) -> Browser:
    """Quickly open a URL in a new browser instance."""
    browser = Browser(headless=headless)
    browser.start()
    browser.open(url)
    return browser
