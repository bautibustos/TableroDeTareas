
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hola"
    )

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text, update.message.from_user.id)
    await update.message.set_reaction(reaction="👍")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text, update.message.from_user)
    await update.message.reply_text('Usuario registrado con exito')

def run_bot(token=None):
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


    # Inicia el bot (Polling)
    application.run_polling()