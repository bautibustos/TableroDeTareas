from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import asyncio

from bot_telegram.commands import register
from bd.manage_bd import execute_query


# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hola"
    )

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text, update.message.from_user.id)
    await update.message.set_reaction(reaction="👍")



async def run_bot(token=None):
    print("iniciando bot")
    # Reemplaza 'TU_TOKEN_AQUI' por el token que te dio BotFather
    application = ApplicationBuilder().token(token).build()
    
    # Manejador para el comando /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # Manejador para el comando /task
    task_handler = CommandHandler('task', task)
    application.add_handler(task_handler)

    # manejador de registro

    register_handler = CommandHandler('registro', register)
    application.add_handler(register_handler)

    print("bot iniciado")

    await application.initialize()
    await application.updater.start_polling() # start_polling pertenece al updater
    await application.start()

        # Mantiene el bot corriendo hasta recibir señal de parada
    try:
        while True:
            await asyncio.sleep(3600) # Mantiene el loop vivo de forma eficiente
    finally:
            # Asegura el cierre ordenado si se sale del while
        await application.updater.stop()
        await application.stop()
        await application.shutdown()