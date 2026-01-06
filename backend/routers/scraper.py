"""
Scraper control endpoints.
"""
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime, timedelta
from typing import Optional

from services.tender_scraper import TenderScraper

router = APIRouter()

# Global scraper instance
scraper_instance: Optional[TenderScraper] = None
scraper_status = {"running": False, "last_run": None, "error": None}


@router.post("/run")
async def run_scraper(
    background_tasks: BackgroundTasks,
    target_date: Optional[str] = None,  # Format: YYYY-MM-DD
):
    """
    Trigger the scraper manually.
    If target_date is not provided, defaults to yesterday.
    """
    global scraper_status
    
    if scraper_status["running"]:
        return {"status": "error", "message": "Scraper is already running"}
    
    if target_date:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        date_obj = (datetime.now() - timedelta(days=1)).date()
    
    scraper_status["running"] = True
    scraper_status["error"] = None
    
    background_tasks.add_task(run_scraper_task, date_obj)
    
    return {
        "status": "started",
        "target_date": str(date_obj),
        "message": "Scraper started in background",
    }


async def run_scraper_task(target_date):
    """Background task to run the scraper."""
    global scraper_status, scraper_instance
    
    try:
        scraper_instance = TenderScraper()
        await scraper_instance.run(target_date)
        scraper_status["last_run"] = datetime.now().isoformat()
    except Exception as e:
        scraper_status["error"] = str(e)
    finally:
        scraper_status["running"] = False


@router.get("/status")
async def get_scraper_status():
    """Get current scraper status."""
    return scraper_status


@router.post("/stop")
async def stop_scraper():
    """Attempt to stop the running scraper."""
    global scraper_instance, scraper_status
    
    if not scraper_status["running"]:
        return {"status": "error", "message": "Scraper is not running"}
    
    if scraper_instance:
        await scraper_instance.stop()
    
    scraper_status["running"] = False
    return {"status": "stopped"}
