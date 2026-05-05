import httpx
from app.config import settings

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

async def send_message(telegram_id: str, text: str):
    if not telegram_id or not settings.TELEGRAM_BOT_TOKEN:
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API}/sendMessage", json={
                "chat_id": telegram_id,
                "text": text,
                "parse_mode": "HTML"
            })
    except Exception as e:
        pass

async def notify_task_assigned(task, assignees):
    """Уведомление о новой задаче"""
    type_labels = {"daily": "на день", "weekly": "на неделю", "monthly": "на месяц"}
    due = ""
    if task.due_date:
        from datetime import timezone
        dt = task.due_date
        due = f"\n⏰ Дедлайн: {dt.strftime('%d.%m.%Y %H:%M')}"

    text = (
        f"📋 <b>Новая задача</b>\n\n"
        f"<b>{task.title}</b>\n"
        f"📅 Тип: {type_labels.get(task.type, task.type)}"
        f"{due}\n"
    )
    if task.description:
        text += f"\n{task.description}"

    for user in assignees:
        if user.telegram_id:
            await send_message(user.telegram_id, text)

async def notify_interview_reminder(interview, users):
    """Напоминание о собеседовании"""
    dt = interview.scheduled_at
    time_str = dt.strftime('%d.%m.%Y в %H:%M')

    text = (
        f"📅 <b>Напоминание о собеседовании</b>\n\n"
        f"👤 <b>{interview.full_name}</b>\n"
        f"🕐 {time_str}\n"
    )
    if interview.phone:
        text += f"📞 {interview.phone}\n"
    if interview.username:
        text += f"💬 {interview.username}\n"

    for user in users:
        if user.telegram_id:
            await send_message(user.telegram_id, text)
