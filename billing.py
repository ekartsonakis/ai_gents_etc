"""
Billing module - PDF bill parsing with pdfplumber.
Extracts bill details from electricity provider PDFs.
"""

import re
import pdfplumber
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


# Greek provider patterns for identification
PROVIDER_PATTERNS = {
    "ΔΕΗ": [r"ΔΕΗ", r"Δημόσια Επιχείρηση Ηλεκτρισμού", r"DEI"],
    "Protergia": [r"Protergia", r"PROTERGIA"],
    "ΕΛΙΝ": [r"ΕΛΙΝ", r"ELIN"],
    "ΗΡΕΝ": [r"ΗΡΕΝ", r"HEREN"],
    "Volton": [r"Volton", r"VOLTON"],
    "ZeniTH": [r"ZeniTH", r"ZENITH"],
    "NRG": [r"NRG", r"nrg"],
    "Elpedison": [r"Elpedison", r"ELPEDISON"],
}


def identify_provider(text: str) -> Optional[str]:
    """Identify the electricity provider from text."""
    for provider, patterns in PROVIDER_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return provider
    return None


def extract_amount(text: str) -> Optional[float]:
    """Extract the amount due from bill text."""
    # Common patterns for Greek electricity bills
    patterns = [
        # Εισπρακτέον, Πληρωτέο, Συνολο
        r"(?:Εισπρακτέον|Πληρωτέο|Συνολικό Ποσό|Συνολος)[:\s]*[\d.,]+[\s€]*(?:€)?\s*([\d.,]+)",
        # Total amount patterns
        r"(?:ΣΥΝΟΛΟ|ΣΥΝΟΛΙΚΟ|ΤΕΛΙΚΟ)[:\s]*€?\s*([\d.,]+)",
        # Amount with euro symbol
        r"(?:€|EUR|EUR[\s:])*\s*([\d]+[.,][\d]{2})",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            # Get the largest amount (usually the total)
            amounts = []
            for match in matches:
                try:
                    amount = float(match.replace(",", "."))
                    amounts.append(amount)
                except ValueError:
                    continue
            if amounts:
                return max(amounts)

    return None


def extract_due_date(text: str) -> Optional[str]:
    """Extract due date from bill text."""
    # Greek date patterns
    patterns = [
        # Λήξη προθεσμίας, Ημερομηνία λήξης
        r"(?:Λήξη|Ημερομηνία λήξης|Προθεσμία πληρωμής)[:\s]*(\d{1,2}[/.-]\d{2}[/.-]\d{2,4})",
        # Standard date formats
        r"(\d{1,2}[/.-]\d{2}[/.-]\d{2,4})",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Try to parse the date
            for match in matches:
                try:
                    # Try different formats
                    for fmt in ["%d/%m/%Y", "%d/%m/%y", "%d.%m.%Y", "%d.%m.%y"]:
                        try:
                            dt = datetime.strptime(match, fmt)
                            return dt.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except:
                    continue

    return None


def extract_supply_number(text: str) -> Optional[str]:
    """Extract supply number (Μισθωτήριο ή Λογαριασμός) from bill."""
    patterns = [
        r"(?:Μισθωτήριο|Λογαριασμός|Αριθμός Παροχής)[:\s]*([A-Z0-9]{6,})",
        r"(?:Μ/Η|Λ/Σ)[:\s]*([A-Z0-9]{6,})",
        r"(?:\b\d{9,}\b)",  # 9+ digit numbers
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_reference(text: str) -> Optional[str]:
    """Extract payment reference code."""
    patterns = [
        r"(?:Κωδικός Πληρωμής|Πληρωμή με)[:\s]*([A-Z0-9]{16,})",
        r"(?:REF|Reference)[:\s]*([A-Z0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_kwh(text: str) -> Optional[Dict[str, float]]:
    """Extract kWh consumption from bill."""
    result = {}

    # Day consumption
    day_patterns = [
        r"(?:Ημέρα|Μέρα)[:\s]*([\d.,]+)\s*kWh",
        r"([\d.,]+)\s*kWh\s*(?:Ημέρα|Μέρα)",
    ]

    for pattern in day_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result["day_kwh"] = float(match.group(1).replace(",", "."))
                break
            except ValueError:
                continue

    # Night consumption
    night_patterns = [
        r"(?:Νύχτα)[:\s]*([\d.,]+)\s*kWh",
    ]

    for pattern in night_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result["night_kwh"] = float(match.group(1).replace(",", "."))
                break
            except ValueError:
                continue

    # Total consumption
    total_patterns = [
        r"(?:Συνολική|Συνολο) Κατανάλωση[:\s]*([\d.,]+)\s*kWh",
        r"Σύνολο[:\s]*([\d.,]+)\s*kWh",
    ]

    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result["total_kwh"] = float(match.group(1).replace(",", "."))
                break
            except ValueError:
                continue

    return result if result else None


def extract_period(text: str) -> Optional[Dict[str, str]]:
    """Extract billing period."""
    patterns = [
        r"(?:Περίοδος|Χρονική Περίοδος)[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})\s*-\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return {
                "start": match.group(1),
                "end": match.group(2)
            }

    return None


def parse_bill(file_path: str) -> Dict[str, Any]:
    """
    Parse an electricity bill PDF and extract key information.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Dictionary with extracted bill details.
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    result = {
        "provider": None,
        "amount": None,
        "due_date": None,
        "supply_number": None,
        "reference": None,
        "consumption": None,
        "period": None,
        "raw_text": "",
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            # Extract text from all pages
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"

            result["raw_text"] = all_text

            # Extract each field
            result["provider"] = identify_provider(all_text)
            result["amount"] = extract_amount(all_text)
            result["due_date"] = extract_due_date(all_text)
            result["supply_number"] = extract_supply_number(all_text)
            result["reference"] = extract_reference(all_text)
            result["consumption"] = extract_kwh(all_text)
            result["period"] = extract_period(all_text)

    except Exception as e:
        result["error"] = str(e)

    return result


def validate_bill(bill: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a bill against user profile.

    Args:
        bill: Parsed bill dictionary.
        user_profile: User profile from memory.

    Returns:
        Validation result with warnings.
    """
    warnings = []
    is_valid = True

    # Check if provider matches expectation
    if user_profile.get("provider"):
        if bill.get("provider") != user_profile.get("provider"):
            warnings.append(f"Provider mismatch: expected {user_profile.get('provider')}, got {bill.get('provider')}")

    # Check if supply number matches
    if user_profile.get("supply_number"):
        if bill.get("supply_number") != user_profile.get("supply_number"):
            warnings.append(f"Supply number mismatch: expected {user_profile.get('supply_number')}, got {bill.get('supply_number')}")

    # Check if amount is reasonable (not zero or negative)
    if not bill.get("amount") or bill.get("amount") <= 0:
        warnings.append("Amount is missing or invalid")
        is_valid = False

    # Check if due date is in the future
    if bill.get("due_date"):
        try:
            due = datetime.strptime(bill.get("due_date"), "%Y-%m-%d")
            if due < datetime.now():
                warnings.append("Due date has passed")
        except ValueError:
            warnings.append("Due date format invalid")

    return {
        "is_valid": is_valid,
        "warnings": warnings,
        "bill": bill
    }


if __name__ == "__main__":
    # Test parsing
    import sys
    if len(sys.argv) > 1:
        result = parse_bill(sys.argv[1])
        print("Bill parsing result:")
        for key, value in result.items():
            if key != "raw_text":
                print(f"  {key}: {value}")
