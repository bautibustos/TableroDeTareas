import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler, 
    Application
)
from bot_telegram.commands.register import register
from bot_telegram.commands.close_task import close_start, close_finish, close_timeout, cancel_close, EXPECTING_OBSERVATION, OBSERVATION_TIMEOUT
from bot_telegram.commands.new_task import task_start, handle_task_content, SELECTING_PRIORITY, EXPECTING_TASK, ASSIGN_TASK, cancel, handle_priority, handle_assign_selection
from bot_telegram.commands.list_task import list_task_active
from bot_telegram.commands.tkt import detail_task
from bot_telegram.commands.utils.conversation_timeout import generic_timeout_handler

async def configurar_menu(application: Application):
    comandos = [
        BotCommand("start", "Prueba de vida del bot"),
        BotCommand("registro", "Ej: /registro <nombre> - Registra tu nombre de usuario"),
        BotCommand("task", "Para registrar una nueva tarea"),
        BotCommand("cancel", "Cortar y suspender la creacion de una tarea"),
        BotCommand("list", "Lista las tareas activas"),
        BotCommand("tkt", "ej: /tkt <id_tarea> - Muestra detalles de una tarea específica"),
        BotCommand("close", "Ej: /close <id_tarea> - Cierra una tarea (solo el asignado, te pide una observación)"),
    ]
    # Registra los comandos en la API de Telegram
    await application.bot.set_my_commands(comandos)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handler global: evita que una excepción no capturada deje al usuario
    sin respuesta y sin registro más allá del log crudo de la librería."""
    logging.getLogger(__name__).error("Excepción no manejada", exc_info=context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ocurrió un error inesperado. Probá de nuevo en un momento."
            )
        except Exception:
            pass

async def run_bot(token: str):
    # Configuración de logs
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    application = ApplicationBuilder().token(token).post_init(configurar_menu).build()

    # Configuración del ConversationHandler
    # per_user=True asegura que si alguien más escribe en el grupo, no interfiera
    task_conv = ConversationHandler(
        entry_points=[CommandHandler("task", task_start)],
        states={
            EXPECTING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_priority)],
            SELECTING_PRIORITY: [CallbackQueryHandler(handle_task_content)],
            # ASSIGN_TASK ya no va acá — se maneja fuera de la conversación
            ConversationHandler.TIMEOUT: [
                CallbackQueryHandler(generic_timeout_handler),
                MessageHandler(filters.ALL, generic_timeout_handler),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=30,
        per_chat=True,
        per_user=True
    )

    close_conv = ConversationHandler(
        entry_points=[CommandHandler("close", close_start)],
        states={
            EXPECTING_OBSERVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, close_finish)],
            ConversationHandler.TIMEOUT: [
                MessageHandler(filters.ALL, close_timeout),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_close)],
        conversation_timeout=OBSERVATION_TIMEOUT,  # ver bot_telegram/commands/close_task.py
        per_chat=True,
        per_user=True
    )

    # Handlers del Bot
    application.add_handler(CommandHandler("start", ping))
    application.add_handler(CommandHandler("registro", register))
    application.add_handler(task_conv)
    application.add_handler(close_conv)
    # Handler global e independiente para los botones de asignación
    application.add_handler(CallbackQueryHandler(handle_assign_selection, pattern=r"^assign:"))
    application.add_handler(CommandHandler("list", list_task_active))
    application.add_handler(CommandHandler("tkt", detail_task))
    application.add_error_handler(error_handler)

    print("Bot de Telegram iniciado y esperando comandos...", flush=True)

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Mantener el loop asíncrono vivo
        while True:
            await asyncio.sleep(1)