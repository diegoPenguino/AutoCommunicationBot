from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from app.services.llm import generate_draft
from app.services.broadcaster import broadcast_message
from app.config import settings

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if settings.admin_user_id and user_id != settings.admin_user_id:
        await update.message.reply_text("You are not authorized to use this bot.")
        return
        
    await update.message.reply_text(
        "¡Hola! Soy el bot del IOI Team Bolivia.\n"
        "Envíame un enlace y un comentario (en un solo mensaje o separados) para redactar un anuncio."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if settings.admin_user_id and user_id != settings.admin_user_id:
        return

    text = update.message.text
    
    # Store link and comment in user_data simply by taking the whole text for now.
    # A more advanced version could parse URLs.
    
    await update.message.reply_text("Generando borrador, por favor espera...")
    
    draft = await generate_draft(link=text, comment="Please base the announcement on the link provided in the message.")
    
    # Save draft to context for later broadcasting
    context.user_data['current_draft'] = draft
    
    keyboard = [
        [InlineKeyboardButton("✅ Aceptar y Enviar", callback_data="accept")],
        [InlineKeyboardButton("🔄 Regenerar", callback_data="regenerate")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"**Borrador Generado:**\n\n{draft}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if settings.admin_user_id and user_id != settings.admin_user_id:
        return
        
    action = query.data
    
    if action == "cancel":
        await query.edit_message_text(text="Acción cancelada. Envíame otro enlace cuando estés listo.")
        context.user_data.pop('current_draft', None)
        
    elif action == "regenerate":
        # In a real scenario, you'd pull the original link and comment from user_data
        await query.edit_message_text(text="Regeneración aún no implementada en este demo. Por favor envía el enlace de nuevo.")
        
    elif action == "accept":
        draft = context.user_data.get('current_draft')
        if not draft:
            await query.edit_message_text(text="Error: No se encontró el borrador.")
            return
            
        await query.edit_message_text(text="¡Borrador aceptado! Iniciando envío a Email, WhatsApp y Telegram...")
        
        # We can trigger the broadcast asynchronously
        import asyncio
        asyncio.create_task(broadcast_message(draft))
        
        await context.bot.send_message(chat_id=user_id, text="¡Envío programado en segundo plano exitosamente!")
