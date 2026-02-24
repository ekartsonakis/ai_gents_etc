"""
Calculator module - Cost calculation engine for electricity plans.
Calculates expected monthly costs based on consumption and plan details.
"""

from typing import Dict, Any, Optional
from providers import ProviderPlan


# Typical monthly consumption in Greece (kWh)
DEFAULT_CONSUMPTION = {
    "low": 150,       # Small apartment, 1-2 people
    "medium": 300,    # Medium apartment, 2-3 people
    "high": 500,      # House with appliances
    "very_high": 800, # House with heating/AC
}


def calculate_monthly_cost(plan: ProviderPlan, consumption: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate expected monthly cost for a plan.

    Args:
        plan: ProviderPlan object with pricing details.
        consumption: Dict with 'total', 'day', 'night' kWh values.

    Returns:
        Dict with cost breakdown: energy, fee, discount, total.
    """
    day_kwh = consumption.get("day", 0)
    night_kwh = consumption.get("night", 0)

    # Calculate energy cost based on meter type
    if plan.price_night and night_kwh > 0:
        # Day/Night meter
        day_cost = day_kwh * plan.price_day if plan.price_day else 0
        night_cost = night_kwh * plan.price_night
        energy_cost = day_cost + night_cost
    elif plan.price_single:
        # Single tariff meter
        total_kwh = day_kwh + night_kwh
        energy_cost = total_kwh * plan.price_single
    elif plan.price_day:
        # Default to day rate
        total_kwh = day_kwh + night_kwh
        energy_cost = total_kwh * plan.price_day
    else:
        energy_cost = 0

    # Monthly base fee
    monthly_fee = plan.monthly_fee

    # Calculate discount
    discount = 0
    if plan.discount_percent and plan.discount_conditions:
        # In a real implementation, check if user meets conditions
        # For now, assume conditions are met if specified
        discount = (energy_cost + monthly_fee) * (plan.discount_percent / 100)

    # Total cost
    total = energy_cost + monthly_fee - discount

    return {
        "energy": round(energy_cost, 2),
        "fee": round(monthly_fee, 2),
        "discount": round(discount, 2),
        "total": round(total, 2),
    }


def calculate_annual_cost(monthly_cost: float, discount_months: int = 12) -> Dict[str, float]:
    """
    Calculate annual cost including discount period.

    Args:
        monthly_cost: Monthly cost during discount period.
        discount_months: Number of months discount applies.

    Returns:
        Dict with annual breakdown.
    """
    # Assume same price after discount ends
    # This is simplified - real calculation would use post-discount prices
    annual_cost = monthly_cost * discount_months

    return {
        "annual_cost": round(annual_cost, 2),
        "discount_months": discount_months,
    }


def compare_consumption_scenarios(plan: ProviderPlan) -> Dict[str, Dict[str, float]]:
    """
    Calculate costs for different consumption levels.

    Args:
        plan: ProviderPlan to evaluate.

    Returns:
        Dict with costs for each consumption level.
    """
    results = {}

    for level, kwh in DEFAULT_CONSUMPTION.items():
        # Assume 70% day, 30% night split
        day_kwh = kwh * 0.7
        night_kwh = kwh * 0.3

        consumption = {
            "total": kwh,
            "day": day_kwh,
            "night": night_kwh,
        }

        cost = calculate_monthly_cost(plan, consumption)
        results[level] = cost

    return results


def is_discount_applicable(plan: ProviderPlan, user_conditions: Dict[str, bool]) -> bool:
    """
    Check if discount conditions are met.

    Args:
        plan: ProviderPlan with discount conditions.
        user_conditions: Dict of user meeting each condition.

    Returns:
        True if all conditions are met.
    """
    if not plan.discount_conditions:
        return False

    for condition in plan.discount_conditions:
        if not user_conditions.get(condition, False):
            return False

    return True


def calculate_savings(current_plan: ProviderPlan, new_plan: ProviderPlan,
                     consumption: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate potential savings from switching plans.

    Args:
        current_plan: Current provider plan.
        new_plan: New provider plan to compare.
        consumption: User's consumption pattern.

    Returns:
        Dict with savings breakdown.
    """
    current_cost = calculate_monthly_cost(current_plan, consumption)
    new_cost = calculate_monthly_cost(new_plan, consumption)

    monthly_savings = current_cost["total"] - new_cost["total"]
    annual_savings = monthly_savings * 12

    # Factor in exit fee if applicable
    effective_savings = annual_savings - new_plan.exit_fee

    return {
        "current_monthly": current_cost["total"],
        "new_monthly": new_cost["total"],
        "monthly_savings": round(monthly_savings, 2),
        "annual_savings": round(annual_savings, 2),
        "exit_fee": new_plan.exit_fee,
        "effective_annual_savings": round(effective_savings, 2),
        "breakeven_months": round(new_plan.exit_fee / monthly_savings, 1) if monthly_savings > 0 else None,
    }


def format_cost_comparison(results: list) -> str:
    """
    Format plan comparison results for display.

    Args:
        results: List of plan comparison dicts.

    Returns:
        Formatted string for display.
    """
    output = "\n" + "=" * 70
    output += "\nPROVIDER COMPARISON RESULTS"
    output += "\n" + "=" * 70 + "\n"

    for i, result in enumerate(results, 1):
        plan = result["plan"]
        output += f"\n{i}. {plan['provider']} - {plan['name']}\n"
        output += f"   Type: {plan['type'].capitalize()}\n"
        output += f"   Expected Monthly Cost: €{result['expected_monthly_cost']:.2f}\n"
        output += f"   Energy Cost: €{result['energy_cost']:.2f}\n"
        output += f"   Monthly Fee: €{result['monthly_fee']:.2f}\n"

        if result['discount'] > 0:
            output += f"   Discount Applied: €{result['discount']:.2f}\n"

        if plan['exit_fee'] > 0:
            output += f"   Exit Fee: €{plan['exit_fee']:.2f}\n"

        output += f"   Contract: {plan['contract_months']} months\n"

        if plan['requirements']:
            output += f"   Requirements: {', '.join(plan['requirements'])}\n"

        output += "\n" + "-" * 40 + "\n"

    return output


def get_top_recommendations(results: list, top_n: int = 3,
                            preferences: Dict[str, Any] = None) -> list:
    """
    Get top recommended plans based on criteria.

    Args:
        results: List of comparison results.
        top_n: Number of recommendations.
        preferences: User preferences.

    Returns:
        List of top N recommendations.
    """
    # Already sorted by cost, just return top N
    recommendations = results[:top_n]

    # Add risk notes
    for rec in recommendations:
        plan = rec["plan"]
        notes = []

        if plan["type"] == "variable":
            notes.append("Variable pricing - rates may change")
        if plan["exit_fee"] > 0:
            notes.append(f"Early termination fee: €{plan['exit_fee']}")
        if plan["discount_percent"] and plan["discount_duration"]:
            notes.append(f"Discount valid for {plan['discount_duration']} months only")
        if plan["contract_months"] > 0:
            notes.append(f"{plan['contract_months']}-month commitment required")

        rec["risk_notes"] = notes

    return recommendations


if __name__ == "__main__":
    # Demo usage
    from providers import ProviderScraper

    scraper = ProviderScraper()
    plans = scraper.scrape_all_providers()

    # Test consumption: 300 kWh/month, 70/30 split
    consumption = {
        "total": 300,
        "day": 210,
        "night": 90,
    }

    # Compare plans
    results = scraper.compare_plans(consumption)

    # Print comparison
    print(format_cost_comparison(results))

    # Show top 3
    print("\nTOP RECOMMENDATIONS:")
    print("-" * 40)
    top = get_top_recommendations(results, 3)
    for i, rec in enumerate(top, 1):
        print(f"\n{i}. {rec['plan']['provider']} - {rec['plan']['name']}")
        print(f"   Monthly: €{rec['expected_monthly_cost']:.2f}")
        if rec.get('risk_notes'):
            print("   Notes:")
            for note in rec['risk_notes']:
                print(f"     - {note}")

    scraper.close()
