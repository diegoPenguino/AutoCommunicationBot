import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import httpx
import logging
from app.config import settings
from app.database import AsyncSessionLocal, MessageLog

logger = logging.getLogger(__name__)

async def broadcast_message(message: str):
    logger.info("Starting broadcast...")
    
    # Save to Database
    if AsyncSessionLocal:
        try:
            async with AsyncSessionLocal() as session:
                new_log = MessageLog(message=message)
                session.add(new_log)
                await session.commit()
                logger.info("Message saved to database.")
        except Exception as e:
            logger.error(f"Error saving message to database: {e}")
            
    await send_emails(message)
    await send_whatsapp(message)
    await send_telegram(message)
    logger.info("Broadcast complete.")

async def send_emails(message: str):
    if not settings.gmail_address or not settings.gmail_app_password:
        logger.warning("Gmail credentials not set. Skipping emails.")
        return

    try:
        df = pd.read_csv("contacts.csv")
    except Exception as e:
        logger.error(f"Could not read contacts.csv: {e}")
        return

    try:
        # We use a synchronous SMTP client here inside the async function,
        # for production with many emails it might be better to run in an executor or use aiosmtplib.
        # But this works for a small list.
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(settings.gmail_address, settings.gmail_app_password)

        for index, row in df.iterrows():
            email_address = row.get("mail_address")
            name = row.get("name", "")
            
            if pd.isna(email_address):
                continue
            
            msg = MIMEMultipart()
            msg["From"] = settings.gmail_address
            msg["To"] = email_address
            msg["Subject"] = "Anuncio Oficial - IOI Team Bolivia"
            
            personalized_message = f"Hola {name},\n\n{message}"
            msg.attach(MIMEText(personalized_message, "plain"))
            
            server.send_message(msg)
            
        server.quit()
        logger.info(f"Sent emails to {len(df)} contacts.")
    except Exception as e:
        logger.error(f"Error sending emails: {e}")

async def send_whatsapp(message: str):
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id or not settings.whatsapp_target_group_id:
        logger.warning("WhatsApp credentials not set. Skipping WhatsApp broadcast.")
        return

    url = f"https://graph.facebook.com/v17.0/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.whatsapp_target_group_id,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            logger.info("Sent message to WhatsApp group.")
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")

async def send_telegram(message: str):
    if not settings.telegram_bot_token or not settings.telegram_group_id:
        logger.warning("Telegram group credentials not set. Skipping Telegram broadcast.")
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_group_id,
        "text": message
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Sent message to Telegram group.")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
