from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import logging

from app.config import settings
from app.bot.handlers import start, handle_message, button_callback
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize PTB Application
ptb_app = Application.builder().token(settings.telegram_bot_token).build()

ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
ptb_app.add_handler(CallbackQueryHandler(button_callback))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    await init_db()
    
    # Setup webhook
    if settings.webhook_url and settings.telegram_bot_token:
        await ptb_app.bot.set_webhook(url=f"{settings.webhook_url}/webhook")
        logger.info(f"Webhook set to {settings.webhook_url}/webhook")
    
    async with ptb_app:
        await ptb_app.start()
        yield
        await ptb_app.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Route for Telegram to send updates to.
    """
    if not ptb_app.bot:
        return {"status": "error", "message": "Bot not initialized"}
        
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    
    await ptb_app.process_update(update)
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "AutoNotifications API is running."}
