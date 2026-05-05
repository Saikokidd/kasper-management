from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот Kasper Management.\n\n"
        "Введи свой email от системы чтобы привязать аккаунт:"
    )

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    telegram_id = str(update.effective_user.id)

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await update.message.reply_text(
                "❌ Пользователь с таким email не найден.\n"
                "Проверь правильность email и попробуй снова."
            )
            return

        if user.telegram_id == telegram_id:
            await update.message.reply_text("✅ Аккаунт уже привязан!")
            return

        user.telegram_id = telegram_id
        db.commit()
        await update.message.reply_text(
            f"✅ Готово! Аккаунт {user.full_name} успешно привязан.\n"
            "Теперь ты будешь получать уведомления о задачах и собеседованиях."
        )
    finally:
        db.close()

def create_bot():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
    return app
