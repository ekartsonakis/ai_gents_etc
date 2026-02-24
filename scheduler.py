"""
Scheduler module - APScheduler for monthly comparison jobs.
Runs provider comparison on a monthly schedule.
"""

import logging
from datetime import datetime
from typing import Optional, Callable
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global scheduler instance
scheduler: Optional[BlockingScheduler] = None


def compare_providers():
    """
    Run monthly provider comparison.
    This function is called by the scheduler.
    """
    logger.info("Starting monthly provider comparison...")

    try:
        # Import here to avoid circular imports
        from providers import ProviderScraper
        from calculator import format_cost_comparison, get_top_recommendations
        from memory import get_user_profile, get_preferences, get_average_consumption, log_audit

        # Get user data
        user_profile = get_user_profile()
        preferences = get_preferences()

        if not user_profile:
            logger.warning("No user profile found. Skipping comparison.")
            return

        # Get consumption
        consumption_data = get_average_consumption()
        if consumption_data["total"] > 0:
            consumption = {
                "total": consumption_data["total"],
                "day": consumption_data["day"],
                "night": consumption_data["night"],
            }
        else:
            # Use default if no history
            consumption = {
                "total": 300,
                "day": 210,
                "night": 90,
            }

        # Scrape providers
        scraper = ProviderScraper()
        scraper.scrape_all_providers()

        # Compare plans
        results = scraper.compare_plans(consumption, preferences)

        # Get top recommendations
        top = get_top_recommendations(results, 3, preferences)

        # Log comparison
        log_audit(
            action="COMPARE",
            provider=top[0]["plan"]["provider"] if top else None,
            plan_name=top[0]["plan"]["name"] if top else None,
            amount=top[0]["expected_monthly_cost"] if top else None,
            details=f"Top plan: €{top[0]['expected_monthly_cost']:.2f}/month" if top else "No plans found"
        )

        scraper.close()

        logger.info("Monthly comparison completed successfully")
        logger.info(f"Top recommendation: {top[0]['plan']['provider']} - {top[0]['plan']['name']}")

        return top

    except Exception as e:
        logger.error(f"Error during monthly comparison: {e}")
        log_audit(
            action="COMPARE_ERROR",
            details=str(e)
        )
        raise


def check_gmail_bills():
    """
    Check Gmail for new electricity bills.
    This function is called by the scheduler.
    """
    logger.info("Checking Gmail for electricity bills...")

    try:
        from gmail import GmailMonitor

        monitor = GmailMonitor()
        monitor.open_gmail(wait_for_login=True)

        # Search for bills
        results = monitor.search_bills()

        if results:
            logger.info(f"Found {len(results)} electricity bills")
            for result in results[:5]:
                logger.info(f"  - {result['subject']} from {result['sender']}")
        else:
            logger.info("No new electricity bills found")

        monitor.close()

    except Exception as e:
        logger.error(f"Error checking Gmail: {e}")
        raise


def start_scheduler(day: int = 1, hour: int = 9):
    """
    Start the scheduler with monthly job.

    Args:
        day: Day of month to run comparison (default: 1st)
        hour: Hour to run comparison (default: 9 AM)
    """
    global scheduler

    scheduler = BlockingScheduler()

    # Add monthly comparison job
    scheduler.add_job(
        compare_providers,
        CronTrigger(day=day, hour=hour),
        id='monthly_comparison',
        name='Monthly Provider Comparison',
        replace_existing=True
    )

    logger.info(f"Scheduler started. Next run: day {day} at {hour}:00")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()


def stop_scheduler():
    """Stop the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")


def run_now(job_func: Callable):
    """
    Run a job function immediately.

    Args:
        job_func: Function to run.
    """
    try:
        job_func()
    except Exception as e:
        logger.error(f"Error running job: {e}")
        raise


def list_jobs():
    """
    List scheduled jobs.

    Returns:
        List of scheduled job info.
    """
    if not scheduler:
        return []

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })

    return jobs


# CLI-friendly job runner
def run_monthly_job():
    """Run monthly comparison job from CLI."""
    logger.info("Running monthly provider comparison...")
    compare_providers()
    logger.info("Done!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            # Start scheduler
            day = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            hour = int(sys.argv[3]) if len(sys.argv) > 3 else 9
            start_scheduler(day, hour)
        elif sys.argv[1] == "run":
            # Run job now
            run_monthly_job()
        elif sys.argv[1] == "list":
            # List jobs
            run_now(compare_providers)  # First run to initialize
            jobs = list_jobs()
            for job in jobs:
                print(f"  {job['name']}: {job['next_run']}")
        else:
            print("Usage: python scheduler.py [start|run|list] [day] [hour]")
    else:
        # Run once for testing
        run_monthly_job()
