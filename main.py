"""
Main module - CLI interface for EnerSave Greece Electricity Optimizer.
Provides user consent gates for enrollment and payment actions.
"""

import sys
import os
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import (
    init_db, get_user_profile, save_user_profile,
    get_preferences, save_preferences, get_audit_log,
    get_average_consumption, save_consumption
)
from browser import Browser
from providers import ProviderScraper
from calculator import format_cost_comparison, get_top_recommendations
from gmail import GmailMonitor
from billing import parse_bill, validate_bill


def print_header():
    """Print application header."""
    print("\n" + "=" * 60)
    print("  EnerSave Greece - Electricity Optimizer")
    print("=" * 60)


def print_menu():
    """Print main menu."""
    print("\n--- Main Menu ---")
    print("1. Compare Providers")
    print("2. Check Gmail for Bills")
    print("3. View Profile")
    print("4. View Audit Log")
    print("5. Update Preferences")
    print("6. Run Monthly Scheduler")
    print("7. Exit")


def collect_user_profile() -> Dict[str, Any]:
    """
    Collect user profile information.

    Returns:
        User profile dictionary.
    """
    print("\n--- User Profile Setup ---")
    print("(Press Enter to keep current value)\n")

    profile = {}

    current = get_user_profile()

    # Full name
    prompt = "Full Name: "
    val = input(prompt).strip()
    profile["full_name"] = val if val else (current.get("full_name") if current else "")

    # AFM (tax number)
    prompt = "AFM (Tax Number): "
    val = input(prompt).strip()
    profile["afm"] = val if val else (current.get("afm") if current else "")

    # Supply number
    prompt = "Supply Number (Μισθωτήριο): "
    val = input(prompt).strip()
    profile["supply_number"] = val if val else (current.get("supply_number") if current else "")

    # Address
    prompt = "Supply Address: "
    val = input(prompt).strip()
    profile["address"] = val if val else (current.get("address") if current else "")

    # Email
    prompt = "Email: "
    val = input(prompt).strip()
    profile["email"] = val if val else (current.get("email") if current else "")

    # Phone
    prompt = "Phone: "
    val = input(prompt).strip()
    profile["phone"] = val if val else (current.get("phone") if current else "")

    # Meter type
    default_meter = current.get("meter_type", "single") if current else "single"
    prompt = f"Meter Type (single/dual): [{default_meter}] "
    val = input(prompt).strip().lower()
    profile["meter_type"] = val if val in ["single", "dual"] else default_meter

    # Day/night split (if dual)
    if profile["meter_type"] == "dual":
        default_day = current.get("day_split", 0.7) if current else 0.7
        default_night = current.get("night_split", 0.3) if current else 0.3

        prompt = f"Day usage % (0-1): [{default_day}] "
        val = input(prompt).strip()
        try:
            profile["day_split"] = float(val) if val else default_day
        except ValueError:
            profile["day_split"] = default_day

        profile["night_split"] = 1 - profile["day_split"]

    return profile


def collect_preferences() -> Dict[str, Any]:
    """
    Collect user preferences.

    Returns:
        Preferences dictionary.
    """
    print("\n--- Preferences Setup ---")

    prefs = {}
    current = get_preferences()

    # Fixed only
    default_fixed = "Y" if (current and current.get("fixed_only")) else "N"
    prompt = f"Prefer fixed-rate plans only? (Y/N): [{default_fixed}] "
    val = input(prompt).strip().upper()
    prefs["fixed_only"] = val == "Y"

    # Max contract months
    default_months = current.get("max_contract_months", 24) if current else 24
    prompt = f"Max contract length (months): [{default_months}] "
    val = input(prompt).strip()
    try:
        prefs["max_contract_months"] = int(val) if val else default_months
    except ValueError:
        prefs["max_contract_months"] = default_months

    # Max exit fee
    default_fee = current.get("max_exit_fee", 0) if current else 0
    prompt = f"Max acceptable exit fee (EUR): [{default_fee}] "
    val = input(prompt).strip()
    try:
        prefs["max_exit_fee"] = float(val) if val else default_fee
    except ValueError:
        prefs["max_exit_fee"] = default_fee

    # E-bill only
    default_ebill = "Y" if (current and current.get("ebill_only")) else "N"
    prompt = f"Prefer e-bill/online-only? (Y/N): [{default_ebill}] "
    val = input(prompt).strip().upper()
    prefs["ebill_only"] = val == "Y"

    return prefs


def compare_providers_cli():
    """Compare providers workflow."""
    print("\n" + "=" * 60)
    print("PROVIDER COMPARISON")
    print("=" * 60)

    # Check if profile exists
    profile = get_user_profile()
    if not profile:
        print("\nNo profile found. Please set up your profile first.")
        if input("Set up profile now? (Y/N): ").strip().upper() == "Y":
            profile_data = collect_user_profile()
            save_user_profile(profile_data)
            profile = get_user_profile()
        else:
            return

    # Check for consumption data
    consumption = get_average_consumption()
    if consumption["total"] == 0:
        print("\nNo consumption history found.")
        prompt = "Enter estimated monthly kWh: "
        val = input(prompt).strip()
        try:
            total_kwh = float(val)
            day_kwh = total_kwh * (profile.get("day_split", 0.7))
            night_kwh = total_kwh * (profile.get("night_split", 0.3))
            consumption = {
                "total": total_kwh,
                "day": day_kwh,
                "night": night_kwh,
            }
        except ValueError:
            print("Invalid input. Using default 300 kWh.")
            consumption = {"total": 300, "day": 210, "night": 90}

    print(f"\nUsing consumption: {consumption['total']:.0f} kWh/month")
    print(f"  Day: {consumption['day']:.0f} kWh")
    print(f"  Night: {consumption['night']:.0f} kWh")

    # Get preferences
    preferences = get_preferences()
    if not preferences:
        preferences = {"fixed_only": False, "max_contract_months": 24, "max_exit_fee": 0}

    # Scrape and compare
    print("\nScraping provider plans...")
    scraper = ProviderScraper()
    scraper.scrape_all_providers()

    results = scraper.compare_plans(consumption, preferences)
    scraper.close()

    if not results:
        print("\nNo plans found matching your criteria.")
        return

    # Display results
    print(format_cost_comparison(results))

    # Get recommendations
    top = get_top_recommendations(results, 3, preferences)

    print("\n" + "=" * 60)
    print("TOP RECOMMENDATIONS")
    print("=" * 60)

    for i, rec in enumerate(top, 1):
        plan = rec["plan"]
        print(f"\n{i}. {plan['provider']} - {plan['name']}")
        print(f"   Monthly Cost: €{rec['expected_monthly_cost']:.2f}")

        if rec.get("risk_notes"):
            print("   Risk Notes:")
            for note in rec["risk_notes"]:
                print(f"     - {note}")

    # Ask about enrollment
    print("\n" + "-" * 60)
    choice = input("Would you like to enroll in a plan? (Enter number 1-3, or N to skip): ").strip()

    if choice.upper() == "N" or not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(top):
            selected = top[idx]
            present_enrollment_summary(selected)
    except ValueError:
        pass


def present_enrollment_summary(recommendation: Dict[str, Any]):
    """Present enrollment summary and request confirmation."""
    plan = recommendation["plan"]

    print("\n" + "=" * 60)
    print("ENROLLMENT SUMMARY")
    print("=" * 60)

    print(f"\nProvider: {plan['provider']}")
    print(f"Plan Name: {plan['name']}")
    print(f"Plan Type: {plan['type'].capitalize()}")
    print(f"Monthly Cost: €{recommendation['expected_monthly_cost']:.2f}")
    print(f"Contract Duration: {plan['contract_months']} months")
    print(f"Exit Fee: €{plan['exit_fee']}")

    if plan["discount_percent"]:
        print(f"Discount: {plan['discount_percent']}% for {plan['discount_duration']} months")

    if plan["requirements"]:
        print(f"Requirements: {', '.join(plan['requirements'])}")

    print("\n" + "-" * 60)
    print("KEY CONTRACT RISKS:")
    print("-" * 60)

    if plan["type"] == "variable":
        print("- This is a variable rate plan. Prices may change.")
    if plan["exit_fee"] > 0:
        print(f"- Early termination fee: €{plan['exit_fee']}")
    if plan["contract_months"] > 0:
        print(f"- Minimum contract term: {plan['contract_months']} months")
    if plan["discount_percent"] and plan["discount_duration"]:
        print(f"- Discount only valid for {plan['discount_duration']} months")

    print("\n" + "=" * 60)
    print("CONFIRMATION REQUIRED")
    print("=" * 60)

    confirm = input('\nType "CONFIRM ENROLL" to proceed with enrollment: ')

    if confirm == "CONFIRM ENROLL":
        print("\nEnrollment confirmed!")
        print("Navigate to the provider's website to complete enrollment.")

        from memory import log_audit
        log_audit(
            action="ENROLLMENT_REQUESTED",
            provider=plan["provider"],
            plan_name=plan["name"],
            amount=recommendation["expected_monthly_cost"],
            details="Enrollment confirmed via CLI"
        )
    else:
        print("\nEnrollment cancelled.")


def check_gmail_cli():
    """Check Gmail for bills workflow."""
    print("\n" + "=" * 60)
    print("GMAIL BILL CHECK")
    print("=" * 60)

    print("\nOpening Gmail in browser...")
    print("Please log in and complete 2FA, then press Enter.\n")

    monitor = GmailMonitor()
    monitor.open_gmail(wait_for_login=True)

    # Search for bills
    print("\nSearching for electricity bills...")
    results = monitor.search_bills()

    if not results:
        print("\nNo electricity bills found.")
        monitor.close()
        return

    print(f"\nFound {len(results)} emails:\n")

    for i, result in enumerate(results[:10], 1):
        print(f"{i}. Subject: {result['subject']}")
        print(f"   From: {result['sender']}")
        print(f"   Date: {result['date']}")
        print(f"   Provider: {result['provider']}")
        print()

    # Ask to open an email
    choice = input("Enter email number to view (or Enter to skip): ").strip()

    if choice:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                email = results[idx]
                monitor.open_email(email)

                details = monitor.get_email_details()
                print(f"\nSubject: {details.get('subject')}")
                print(f"From: {details.get('sender')}")

                bill_info = monitor.get_bill_from_email()
                if bill_info:
                    print(f"\nBill detected!")
                    print(f"Provider: {bill_info.get('provider')}")

                print("\nTake any necessary actions in the browser.")
                print("Press Enter when done:")
                input()

        except ValueError:
            pass

    monitor.close()


def view_profile_cli():
    """View user profile."""
    print("\n--- User Profile ---")

    profile = get_user_profile()

    if not profile:
        print("No profile found.")
        return

    for key, value in profile.items():
        if key not in ["id", "created_at", "updated_at"]:
            print(f"  {key}: {value}")


def view_audit_cli():
    """View audit log."""
    print("\n--- Audit Log ---")

    logs = get_audit_log(20)

    if not logs:
        print("No audit entries found.")
        return

    for log in logs:
        print(f"\n[{log['date']}] {log['action']}")
        if log.get("provider"):
            print(f"  Provider: {log['provider']}")
        if log.get("plan_name"):
            print(f"  Plan: {log['plan_name']}")
        if log.get("amount"):
            print(f"  Amount: €{log['amount']}")
        if log.get("details"):
            print(f"  Details: {log['details']}")


def update_preferences_cli():
    """Update user preferences."""
    prefs = collect_preferences()
    save_preferences(prefs)
    print("\nPreferences saved!")


def run_scheduler_cli():
    """Run monthly scheduler."""
    print("\nRunning monthly comparison...")
    from scheduler import compare_providers
    compare_providers()
    print("\nMonthly comparison completed!")


def main():
    """Main CLI entry point."""
    # Initialize database
    init_db()

    print_header()

    while True:
        print_menu()
        choice = input("\nSelect option: ").strip()

        if choice == "1":
            compare_providers_cli()
        elif choice == "2":
            check_gmail_cli()
        elif choice == "3":
            view_profile_cli()
        elif choice == "4":
            view_audit_cli()
        elif choice == "5":
            update_preferences_cli()
        elif choice == "6":
            run_scheduler_cli()
        elif choice == "7":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
