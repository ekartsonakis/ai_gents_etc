"""
Dashboard API - FastAPI backend for the web dashboard.
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from memory import (
    init_db, get_user_profile, save_user_profile, get_preferences, save_preferences,
    get_audit_log, get_consumption_history, save_consumption, log_audit
)
from providers import ProviderScraper
from browser import Browser
from calculator import calculate_monthly_cost, get_top_recommendations

app = FastAPI(title="EnerSave Greece Dashboard")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure database is initialized
init_db()


@app.get("/api/profile")
def get_profile():
    """Get user profile."""
    profile = get_user_profile()
    if not profile:
        return JSONResponse({"error": "No profile found"}, status_code=404)
    # Remove sensitive fields
    profile.pop("afm", None)
    return profile


@app.post("/api/profile")
def update_profile(data: dict):
    """Update user profile."""
    save_user_profile(data)
    log_audit("PROFILE_UPDATED", details="User profile updated via dashboard")
    return {"success": True}


@app.get("/api/preferences")
def get_user_preferences():
    """Get user preferences."""
    prefs = get_preferences()
    if not prefs:
        return {"fixed_only": False, "max_contract_months": 24, "max_exit_fee": 0}
    return prefs


@app.post("/api/preferences")
def update_preferences(data: dict):
    """Update user preferences."""
    save_preferences(data)
    log_audit("PREFERENCES_UPDATED", details="User preferences updated via dashboard")
    return {"success": True}


@app.get("/api/comparison")
def run_comparison():
    """Run provider comparison."""
    profile = get_user_profile()
    prefs = get_preferences()

    # Get consumption
    history = get_consumption_history(12)
    if history:
        avg = sum(h["total_kwh"] for h in history) / len(history)
        consumption = {
            "total": avg,
            "day": avg * 0.7,
            "night": avg * 0.3,
        }
    else:
        consumption = {"total": 300, "day": 210, "night": 90}

    # Scrape and compare
    browser = Browser(headless=True)
    browser.start()

    scraper = ProviderScraper(browser=browser)
    scraper.scrape_all_providers()
    results = scraper.compare_plans(consumption, prefs)
    top = get_top_recommendations(results, 5, prefs)

    browser.close()

    # Log comparison
    if top:
        log_audit(
            action="COMPARE",
            provider=top[0]["plan"]["provider"],
            plan_name=top[0]["plan"]["name"],
            amount=top[0]["expected_monthly_cost"],
            details=f"Comparison via dashboard - Top: €{top[0]['expected_monthly_cost']:.2f}"
        )

    return {
        "consumption": consumption,
        "top_plans": top,
        "all_plans": results[:10],
        "compared_at": datetime.now().isoformat()
    }


@app.get("/api/history")
def get_history(limit: int = 12):
    """Get consumption history."""
    return get_consumption_history(limit)


@app.post("/api/history")
def add_history(data: dict):
    """Add consumption record."""
    save_consumption(
        month=data.get("month", ""),
        year=data.get("year", 2026),
        total_kwh=data.get("total_kwh", 0),
        day_kwh=data.get("day_kwh"),
        night_kwh=data.get("night_kwh"),
        provider=data.get("provider")
    )
    return {"success": True}


@app.get("/api/audit")
def get_audit(limit: int = 50):
    """Get audit log."""
    return get_audit_log(limit)


@app.get("/api/providers")
def get_providers():
    """Get list of providers."""
    from providers import PROVIDER_URLS
    return [{"name": name, "url": url} for name, url in PROVIDER_URLS.items()]


@app.get("/")
def dashboard():
    """Serve the dashboard HTML."""
    import os
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return HTMLResponse(f.read())
    else:
        return HTMLResponse("<h1>Dashboard not found</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8040)
