import asyncio
import traceback
from datetime import datetime
from database import SessionLocal
from models import UserSettings
from pipeline_service import run_pipeline_analysis_sync, broadcast_event

scheduler_running = True

async def background_pipeline_scheduler(interval_seconds: int = 300):
    """
    Periodically scans active pipelines in the background every `interval_seconds` (default 5 mins)
    without blocking requests or requiring manual triggers.
    """
    global scheduler_running
    print(f"[Scheduler] Background Pipeline Monitor started (Interval: {interval_seconds}s)")

    # Initial delay so startup completes
    await asyncio.sleep(5)

    while scheduler_running:
        try:
            db = SessionLocal()
            try:
                # Find all users with auto-healing enabled
                settings_list = db.query(UserSettings).filter(UserSettings.auto_heal_enabled == True).all()
                if not settings_list:
                    # Run default user analysis if no specific settings
                    run_pipeline_analysis_sync(db, user_id=1)
                else:
                    for s in settings_list:
                        run_pipeline_analysis_sync(db, user_id=s.user_id)
            finally:
                db.close()
        except Exception as e:
            print(f"[Scheduler] Error during scheduled scan: {e}")
            traceback.print_exc()

        # Wait for next interval
        await asyncio.sleep(interval_seconds)


def stop_scheduler():
    global scheduler_running
    scheduler_running = False
