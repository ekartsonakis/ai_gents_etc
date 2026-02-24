"""
Gmail module - Gmail search and authentication for bill monitoring.
Uses browser automation for user-driven login and 2FA.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from browser import Browser
from billing import parse_bill


# Known Greek electricity provider email patterns
PROVIDER_EMAIL_DOMAINS = {
    "ΔΕΗ": ["dei.gr", "energia.gr"],
    "Protergia": ["protergia.gr"],
    "ΕΛΙΝ": ["elin.gr"],
    "ΗΡΕΝ": ["heren.gr"],
    "Volton": ["volton.gr"],
    "ZeniTH": ["zenith.gr"],
    "NRG": ["nrg.gr"],
    "Elpedison": ["elpedison.gr"],
}

# Email search queries for electricity bills
BILL_SEARCH_QUERIES = [
    "subject:(λογαριασμός OR λογαριασμού OR τιμολόγιο OR invoice OR bill) (ηλεκτρικού OR ηλεκτρισμού OR electricity)",
    "subject:(ΔΕΗ OR DEI OR Protergia OR ΕΛΙΝ OR ΗΡΕΝ OR Volton OR ZeniTH OR NRG)",
    "has:attachment filename:pdf",
]


class GmailMonitor:
    """Gmail monitoring for electricity bills."""

    def __init__(self, browser: Browser = None):
        """
        Initialize Gmail monitor.

        Args:
            browser: Browser instance. If None, creates a new one.
        """
        self.browser = browser
        self.own_browser = False

    def _ensure_browser(self):
        """Ensure browser is available."""
        if not self.browser:
            self.browser = Browser(headless=False)
            self.browser.start()
            self.own_browser = True

    def open_gmail(self, wait_for_login: bool = True):
        """
        Open Gmail in browser.

        Args:
            wait_for_login: If True, wait for user to complete login/2FA.
        """
        self._ensure_browser()
        self.browser.open("https://mail.google.com")

        if wait_for_login:
            print("\n=== Gmail Login Required ===")
            print("Please log in to Gmail and complete 2FA if required.")
            print("Press ENTER when you have successfully logged in.")
            input()
            print("Continuing...\n")

    def search_bills(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Search for electricity bills in Gmail.

        Args:
            query: Custom search query. If None, uses default electricity bill query.

        Returns:
            List of email results with metadata.
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Call open_gmail() first.")

        if query is None:
            # Default query for Greek electricity bills
            query = "(subject:λογαριασμός OR subject:τιμολόγιο OR subject:invoice OR subject:bill) (subject:ηλεκτρικού OR subject:ηλεκτρισμού OR subject:electricity OR from:@dei.gr OR from:@protergia.gr OR from:@volton.gr) has:attachment"

        # Fill search box
        search_box = "input[name='q']"
        self.browser.fill(search_box, query)
        self.browser.page.keyboard.press("Enter")

        # Wait for results
        self.browser.wait_for_load_state("networkidle")
        self.browser.wait(2)

        # Extract results
        results = []
        emails = self.browser.page.query_selector_all("tr.zA")

        for email in emails[:20]:  # Limit to 20 results
            try:
                subject_elem = email.query_selector("span.bold")
                sender_elem = email.query_selector("span[email]")
                date_elem = email.query_selector("td.date")

                subject = subject_elem.inner_text() if subject_elem else ""
                sender = sender_elem.get_attribute("email") if sender_elem else ""
                date = date_elem.inner_text() if date_elem else ""

                # Determine provider from sender
                provider = self._identify_provider_from_sender(sender)

                results.append({
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "provider": provider,
                    "element": email,
                })
            except Exception as e:
                continue

        return results

    def _identify_provider_from_sender(self, sender: str) -> Optional[str]:
        """Identify provider from sender email."""
        if not sender:
            return None

        sender_lower = sender.lower()
        for provider, domains in PROVIDER_EMAIL_DOMAINS.items():
            for domain in domains:
                if domain in sender_lower:
                    return provider
        return None

    def open_email(self, email_element):
        """Open an email from search results."""
        email_element.click()
        self.browser.wait_for_load_state("networkidle")
        self.browser.wait(1)

    def get_email_details(self) -> Dict[str, Any]:
        """Get details of currently open email."""
        if not self.browser:
            raise RuntimeError("No email open")

        details = {
            "subject": "",
            "sender": "",
            "date": "",
            "body": "",
            "attachments": [],
        }

        try:
            # Get subject
            subject_elem = self.browser.page.query_selector("h.hP")
            if subject_elem:
                details["subject"] = subject_elem.inner_text()

            # Get sender
            sender_elem = self.browser.page.query_selector("span[email]")
            if sender_elem:
                details["sender"] = sender_elem.get_attribute("email")

            # Get date
            date_elem = self.browser.page.query_selector("span.gq")
            if date_elem:
                details["date"] = date_elem.inner_text()

            # Get body
            body_elem = self.browser.page.query_selector("div.a3s.aiL")
            if body_elem:
                details["body"] = body_elem.inner_text()

            # Get attachments
            attachments = self.browser.page.query_selector_all("div.Kj-JD-Jt")
            for att in attachments:
                details["attachments"].append(att.inner_text())

        except Exception as e:
            details["error"] = str(e)

        return details

    def download_attachment(self, attachment_index: int = 0, save_dir: str = "downloads") -> Optional[str]:
        """
        Download an attachment from the currently open email.

        Args:
            attachment_index: Index of attachment to download (0-based).
            save_dir: Directory to save downloads.

        Returns:
            Path to downloaded file, or None if failed.
        """
        Path(save_dir).mkdir(exist_ok=True)

        try:
            # Click on attachment
            attachments = self.browser.page.query_selector_all("div.Kj-JD-Jt")
            if attachment_index >= len(attachments):
                return None

            attachments[attachment_index].click()
            self.browser.wait(2)

            # For now, we'll need to handle download differently
            # Playwright handles downloads automatically with proper setup
            return None

        except Exception as e:
            print(f"Error downloading attachment: {e}")
            return None

    def validate_sender(self, sender: str) -> Dict[str, Any]:
        """
        Validate email sender for security.

        Args:
            sender: Sender email address.

        Returns:
            Validation result with warnings.
        """
        warnings = []
        is_valid = True

        if not sender:
            warnings.append("No sender information")
            is_valid = False

        # Check if sender is from known provider domains
        sender_lower = sender.lower() if sender else ""
        known_domain = False

        for provider, domains in PROVIDER_EMAIL_DOMAINS.items():
            for domain in domains:
                if domain in sender_lower:
                    known_domain = True
                    break

        if not known_domain and sender:
            warnings.append(f"Unknown sender domain: {sender}")

        # Check for suspicious patterns
        suspicious_patterns = [
            r"@.*\.xyz",
            r"@.*\.top",
            r"@.*\.click",
            r"electricity.*@.*\.com",  # Generic suspicious
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, sender_lower):
                warnings.append(f"Suspicious sender pattern detected")
                is_valid = False

        return {
            "is_valid": is_valid,
            "warnings": warnings,
            "sender": sender,
        }

    def get_bill_from_email(self) -> Optional[Dict[str, Any]]:
        """
        Extract bill information from currently open email.

        Returns:
            Bill information or None.
        """
        details = self.get_email_details()

        # Look for PDF attachments
        if details.get("attachments"):
            for att in details["attachments"]:
                if "pdf" in att.lower():
                    return {
                        "subject": details.get("subject"),
                        "sender": details.get("sender"),
                        "date": details.get("date"),
                        "attachment_name": att,
                        "provider": self._identify_provider_from_sender(details.get("sender")),
                    }

        # Try to extract bill info from email body
        body = details.get("body", "")
        if any(keyword in body.lower() for keyword in ["λογαριασμός", "τιμολόγιο", "amount", "due"]):
            return {
                "subject": details.get("subject"),
                "sender": details.get("sender"),
                "date": details.get("date"),
                "body": body,
                "provider": self._identify_provider_from_sender(details.get("sender")),
            }

        return None

    def close(self):
        """Close browser if we own it."""
        if self.own_browser and self.browser:
            self.browser.close()


def prompt_login() -> Browser:
    """
    Prompt user to log in to Gmail.

    Returns:
        Browser instance with Gmail open.
    """
    print("\n" + "=" * 50)
    print("GMAIL LOGIN REQUIRED")
    print("=" * 50)
    print("\nYou will be redirected to Gmail.")
    print("Please log in and complete any 2FA verification.")
    print("The assistant will wait for you to confirm login.\n")

    browser = Browser(headless=False)
    browser.start()
    browser.open("https://mail.google.com")

    print("\n[Waiting for login...]")
    print("Press ENTER after you have successfully logged in: ", end="")
    input()

    print("\nLogin confirmed! Continuing...\n")
    return browser


if __name__ == "__main__":
    # Demo usage
    monitor = GmailMonitor()

    # Open Gmail and wait for login
    monitor.open_gmail()

    # Search for bills
    results = monitor.search_bills()

    print(f"Found {len(results)} emails")
    for i, result in enumerate(results[:5]):
        print(f"\n{i+1}. Subject: {result['subject']}")
        print(f"   From: {result['sender']}")
        print(f"   Provider: {result['provider']}")
        print(f"   Date: {result['date']}")

    print("\nClose browser to exit (Ctrl+C to abort)")
    try:
        input()
    except:
        pass

    monitor.close()
