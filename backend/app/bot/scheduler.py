from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.interview import Interview
from app.models.user import User
from app.bot.notifications import notify_interview_reminder
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

async def check_interview_reminders():
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        # Собеседования сегодня и завтра
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = today_start + timedelta(days=2)

        interviews = db.query(Interview).filter(
            Interview.status == 'scheduled',
            Interview.scheduled_at >= now,
            Interview.scheduled_at <= tomorrow_end
        ).all()

        if not interviews:
            return

        users = db.query(User).filter(User.telegram_id.isnot(None)).all()
        if not users:
            return

        for interview in interviews:
            diff = interview.scheduled_at - now
            hours = diff.total_seconds() / 3600

            # Напоминание за 1 день (от 23 до 25 часов)
            if 23 <= hours <= 25:
                await notify_interview_reminder(interview, users)
            # Напоминание в день собеседования (от 1 до 3 часов)
            elif 1 <= hours <= 3:
                await notify_interview_reminder(interview, users)

    except Exception as e:
        logger.error(f"Ошибка планировщика: {e}")
    finally:
        db.close()

def create_scheduler():
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(check_interview_reminders, 'cron', hour=9, minute=0)
    scheduler.add_job(check_interview_reminders, 'interval', hours=1)
    return scheduler
