import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)
from bot_telegram.commands.register import register
from bot_telegram.commands.close_task import close
from bot_telegram.commands.new_task import task_start, handle_task_content, SELECTING_PRIORITY, EXPECTING_TASK, cancel, handle_priority

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

async def run_bot(token: str):
    # Configuración de logs
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    application = ApplicationBuilder().token(token).build()

    # Configuración del ConversationHandler
    # per_user=True asegura que si alguien más escribe en el grupo, no interfiera
    task_conv = ConversationHandler(
        entry_points=[CommandHandler("task", task_start)],
        states={
            SELECTING_PRIORITY: [
                CallbackQueryHandler(handle_priority)
            ],
            EXPECTING_TASK: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_task_content)
            ],
        },
        #  aca se puede cambiar el comando para cancelar la tarea
        fallbacks=[CommandHandler("cancel", cancel)],
        per_chat=True,
        per_user=True
    )

    # Handlers del Bot
    application.add_handler(CommandHandler("start", ping))
    application.add_handler(CommandHandler("close", close))
    application.add_handler(CommandHandler("registro", register))
    application.add_handler(task_conv)

    print("Bot de Telegram iniciado y esperando comandos...", flush=True)

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Mantener el loop asíncrono vivo
        while True:
            await asyncio.sleep(1)