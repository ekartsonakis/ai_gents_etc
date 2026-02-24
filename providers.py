"""
Providers module - Greek electricity provider scraping and comparison.
Scrapes official provider pages for plan data.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from browser import Browser


# Greek electricity provider URLs
PROVIDER_URLS = {
    "ΔΕΗ": "https://www.dei.gr/",
    "Protergia": "https://www.protergia.gr/",
    "ΕΛΙΝ": "https://www.elin.gr/",
    "ΗΡΕΝ": "https://www.heren.gr/",
    "Volton": "https://www.volton.gr/",
    "ZeniTH": "https://www.zenith.gr/",
    "NRG": "https://www.nrg.gr/",
    "Elpedison": "https://www.elpedison.gr/",
}


class ProviderPlan:
    """Represents an electricity plan."""

    def __init__(self, provider: str, name: str, plan_type: str = "variable"):
        self.provider = provider
        self.name = name
        self.plan_type = plan_type  # "fixed" or "variable"
        self.price_day = None       # Price per kWh (day)
        self.price_night = None     # Price per kWh (night)
        self.price_single = None    # Price per kWh (single tariff)
        self.monthly_fee = 0        # Monthly base fee
        self.discount_percent = 0   # Discount percentage
        self.discount_duration = None  # Months discount applies
        self.discount_conditions = []  # List of conditions
        self.contract_months = 0    # Contract duration in months
        self.exit_fee = 0          # Early termination fee
        self.deposit = 0           # Required deposit
        self.requirements = []     # List of requirements (direct debit, e-bill, etc.)
        self.notes = ""             # Additional notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "name": self.name,
            "type": self.plan_type,
            "price_day": self.price_day,
            "price_night": self.price_night,
            "price_single": self.price_single,
            "monthly_fee": self.monthly_fee,
            "discount_percent": self.discount_percent,
            "discount_duration": self.discount_duration,
            "discount_conditions": self.discount_conditions,
            "contract_months": self.contract_months,
            "exit_fee": self.exit_fee,
            "deposit": self.deposit,
            "requirements": self.requirements,
            "notes": self.notes,
        }

    def __repr__(self):
        return f"<ProviderPlan {self.provider} {self.name}>"


class ProviderScraper:
    """Scraper for Greek electricity providers."""

    def __init__(self, browser: Browser = None):
        self.browser = browser
        self.own_browser = False
        self.plans: List[ProviderPlan] = []

    def _ensure_browser(self):
        """Ensure browser is available."""
        if not self.browser:
            self.browser = Browser(headless=False)
            self.browser.start()
            self.own_browser = True

    def scrape_all_providers(self) -> List[ProviderPlan]:
        """
        Scrape all major Greek providers for their plans.

        Returns:
            List of ProviderPlan objects.
        """
        self._ensure_browser()
        self.plans = []

        # Note: This is a simplified scraper. In production, each provider
        # would need custom scraping logic for their specific page structures.

        # For demonstration, we'll add placeholder plan data
        # In a real implementation, you would navigate to each provider's
        # pricing page and extract the actual plan details.

        self.plans.extend(self._get_sample_dei_plans())
        self.plans.extend(self._get_sample_protergia_plans())
        self.plans.extend(self._get_sample_elin_plans())
        self.plans.extend(self._get_sample_heren_plans())
        self.plans.extend(self._get_sample_volton_plans())
        self.plans.extend(self._get_sample_zenith_plans())
        self.plans.extend(self._get_sample_nrg_plans())
        self.plans.extend(self._get_sample_elpedison_plans())

        return self.plans

    def _get_sample_dei_plans(self) -> List[ProviderPlan]:
        """Get sample ΔΕΗ plans."""
        plans = []

        # Γενικό Οικιακό Τιμολόγιο (General Home Tariff)
        plan = ProviderPlan("ΔΕΗ", "Γενικό Οικιακό", "variable")
        plan.price_single = 0.1580
        plan.price_day = 0.1670
        plan.price_night = 0.1120
        plan.monthly_fee = 5.50
        plan.requirements = ["direct_debit"]
        plans.append(plan)

        # Οικιακό Νυχτερινό (Home Night)
        plan = ProviderPlan("ΔΕΗ", "Οικιακό Νυχτερινό", "variable")
        plan.price_single = 0.1450
        plan.price_day = 0.1550
        plan.price_night = 0.1050
        plan.monthly_fee = 5.50
        plan.requirements = ["direct_debit", "night_meter"]
        plans.append(plan)

        return plans

    def _get_sample_protergia_plans(self) -> List[ProviderPlan]:
        """Get sample Protergia plans."""
        plans = []

        # Protergia Home Basic
        plan = ProviderPlan("Protergia", "Home Basic", "variable")
        plan.price_single = 0.1420
        plan.price_day = 0.1520
        plan.price_night = 0.0980
        plan.monthly_fee = 4.90
        plan.discount_percent = 10
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit", "ebill"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        # Protergia Home Secure
        plan = ProviderPlan("Protergia", "Home Secure 12", "fixed")
        plan.price_single = 0.1550
        plan.price_day = 0.1650
        plan.price_night = 0.1100
        plan.monthly_fee = 5.90
        plan.contract_months = 12
        plan.exit_fee = 30
        plan.requirements = ["direct_debit"]
        plans.append(plan)

        return plans

    def _get_sample_elin_plans(self) -> List[ProviderPlan]:
        """Get sample ΕΛΙΝ plans."""
        plans = []

        # ΕΛΙΝ Οικιακό
        plan = ProviderPlan("ΕΛΙΝ", "Οικιακό Πράσινο", "variable")
        plan.price_single = 0.1400
        plan.price_day = 0.1500
        plan.price_night = 0.0950
        plan.monthly_fee = 4.50
        plan.discount_percent = 8
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        return plans

    def _get_sample_heren_plans(self) -> List[ProviderPlan]:
        """Get sample ΗΡΕΝ plans."""
        plans = []

        # ΗΡΕΝ Οικιακό
        plan = ProviderPlan("ΗΡΕΝ", "Home Plus", "variable")
        plan.price_single = 0.1380
        plan.price_day = 0.1480
        plan.price_night = 0.0920
        plan.monthly_fee = 4.90
        plan.discount_percent = 12
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit", "ebill"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        return plans

    def _get_sample_volton_plans(self) -> List[ProviderPlan]:
        """Get sample Volton plans."""
        plans = []

        # Volton Οικιακό
        plan = ProviderPlan("Volton", "Volton Home", "variable")
        plan.price_single = 0.1350
        plan.price_day = 0.1450
        plan.price_night = 0.0900
        plan.monthly_fee = 4.50
        plan.discount_percent = 15
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit", "ebill"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        # Volton Fixed
        plan = ProviderPlan("Volton", "Volton Fixed 12", "fixed")
        plan.price_single = 0.1480
        plan.price_day = 0.1580
        plan.price_night = 0.1050
        plan.monthly_fee = 5.50
        plan.contract_months = 12
        plan.exit_fee = 25
        plan.requirements = ["direct_debit"]
        plans.append(plan)

        return plans

    def _get_sample_zenith_plans(self) -> List[ProviderPlan]:
        """Get sample ZeniTH plans."""
        plans = []

        # ZeniTH Οικιακό
        plan = ProviderPlan("ZeniTH", "ZeniTH Home", "variable")
        plan.price_single = 0.1370
        plan.price_day = 0.1470
        plan.price_night = 0.0910
        plan.monthly_fee = 4.80
        plan.discount_percent = 10
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        return plans

    def _get_sample_nrg_plans(self) -> List[ProviderPlan]:
        """Get sample NRG plans."""
        plans = []

        # NRG Οικιακό
        plan = ProviderPlan("NRG", "NRG Home", "variable")
        plan.price_single = 0.1410
        plan.price_day = 0.1510
        plan.price_night = 0.0970
        plan.monthly_fee = 5.00
        plan.discount_percent = 8
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        return plans

    def _get_sample_elpedison_plans(self) -> List[ProviderPlan]:
        """Get sample Elpedison plans."""
        plans = []

        # Elpedison Οικιακό
        plan = ProviderPlan("Elpedison", "Elpedison Home", "variable")
        plan.price_single = 0.1430
        plan.price_day = 0.1530
        plan.price_night = 0.0990
        plan.monthly_fee = 5.20
        plan.discount_percent = 10
        plan.discount_duration = 12
        plan.discount_conditions = ["direct_debit", "ebill"]
        plan.requirements = ["direct_debit"]
        plan.exit_fee = 0
        plans.append(plan)

        return plans

    def get_raaey_providers(self) -> List[str]:
        """
        Get list of licensed providers from RAAEY (regulator).

        Returns:
            List of provider names.
        """
        # RAAEY website for licensed suppliers
        # https://www.rae.gr/eksousiodotimeni-prosagogi/
        # This would need actual scraping in production

        return list(PROVIDER_URLS.keys())

    def compare_plans(self, consumption: Dict[str, float],
                     preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Compare all scraped plans for given consumption.

        Args:
            consumption: Dict with 'total', 'day', 'night' kWh values.
            preferences: User preferences.

        Returns:
            List of plans with calculated costs, sorted by total cost.
        """
        from calculator import calculate_monthly_cost

        results = []

        for plan in self.plans:
            # Filter based on preferences
            if preferences:
                if preferences.get("fixed_only") and plan.plan_type != "fixed":
                    continue
                if preferences.get("max_contract_months"):
                    if plan.contract_months > preferences["max_contract_months"]:
                        continue
                if preferences.get("max_exit_fee"):
                    if plan.exit_fee > preferences["max_exit_fee"]:
                        continue

            # Calculate cost
            cost = calculate_monthly_cost(plan, consumption)

            results.append({
                "plan": plan.to_dict(),
                "expected_monthly_cost": cost["total"],
                "energy_cost": cost["energy"],
                "monthly_fee": cost["fee"],
                "discount": cost["discount"],
            })

        # Sort by expected monthly cost
        results.sort(key=lambda x: x["expected_monthly_cost"])

        return results

    def close(self):
        """Close browser if we own it."""
        if self.own_browser and self.browser:
            self.browser.close()


def scrape_provider(url: str, browser: Browser = None) -> List[ProviderPlan]:
    """
    Scrape a specific provider URL for plans.

    Args:
        url: Provider URL.
        browser: Browser instance.

    Returns:
        List of ProviderPlan objects.
    """
    scraper = ProviderScraper(browser)
    scraper._ensure_browser()
    scraper.browser.open(url)
    # Add custom scraping logic for specific provider
    return scraper.plans


if __name__ == "__main__":
    # Demo usage
    scraper = ProviderScraper()
    plans = scraper.scrape_all_providers()

    print(f"Found {len(plans)} plans from {len(PROVIDER_URLS)} providers:\n")

    for plan in plans:
        print(f"  {plan.provider} - {plan.name}")
        print(f"    Type: {plan.plan_type}")
        print(f"    Price (single): €{plan.price_single}/kWh")
        print(f"    Monthly fee: €{plan.monthly_fee}")
        if plan.discount_percent:
            print(f"    Discount: {plan.discount_percent}% for {plan.discount_duration} months")
        if plan.exit_fee:
            print(f"    Exit fee: €{plan.exit_fee}")
        print()

    scraper.close()
