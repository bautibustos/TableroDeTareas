from telegram import Update,  InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)
from bd.manage_bd import execute_query
import datetime



async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.set_reaction(reaction="✍")
    mensaje = update.message.text.replace('/task ', '')
    id_telegram = update.message.from_user.id
    
    date_open = datetime.datetime.now()
    query = 'insert into "TASKS" (user_open, context_task, datetime_open) values (%s, %s, %s);'
    params = (id_telegram, mensaje, date_open)
    #params = (user_id, contenido, date_open)
    await execute_query(query, params)
    await update.message.set_reaction(reaction="👍")
    
    
# Estados para la conversación
SELECTING_PRIORITY, EXPECTING_TASK = range(2)

async def task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el comando /task, pide la tarea y pasa al estado EXPECTING_TASK."""

    context.user_data['task_owner'] = update.effective_user.id
    
    await update.message.reply_text(
        text="¿Cuál es la tarea?",
    )
    # 1. CORREGIDO: Borrado el código muerto de los botones acá. 
    # Primero pedimos el texto y pasamos al estado EXPECTING_TASK.
    return EXPECTING_TASK

async def handle_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe el texto de la tarea, muestra los botones y pasa al estado SELECTING_PRIORITY.
    """
    user_id = update.effective_user.id
    
    if user_id != context.user_data.get('task_owner'):
        return EXPECTING_TASK

    # 2. CORREGIDO: Guardamos el texto de la tarea que acaba de escribir el usuario
    context.user_data['task_content'] = update.message.text
    
    keyboard = [
        [
            InlineKeyboardButton("Alta 🔴", callback_data="1"),
            InlineKeyboardButton("Media 🟡", callback_data="2"),
            InlineKeyboardButton("Baja 🟢", callback_data="3"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hola {update.effective_user.first_name}, selecciona la prioridad de la tarea:",
        reply_markup=reply_markup
    )
    
    # Pasamos al estado que espera el clic del botón
    return SELECTING_PRIORITY


async def handle_task_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el contenido final de la tarea."""

    query_cb = update.callback_query
    await query_cb.answer() # Obligatorio responder al callback en Telegram
    
    user_id = update.effective_user.id
    
    if user_id != context.user_data.get('task_owner'):
        return SELECTING_PRIORITY

    # 3. CORREGIDO: Capturamos la prioridad del botón y el contenido que guardamos antes
    prioridad = query_cb.data
    contenido = context.user_data.get('task_content')
    
    print(f"DEBUG: Tarea de {user_id} | Prioridad: {prioridad} | Contenido: {contenido}", flush=True)
    
    # --- PARA LOGICA DE BASE DE DATOS ---
    date_open = datetime.datetime.now()
    sql_query = 'insert into "TASKS" (user_open, context_task, datetime_open, priority) values (%s, %s, %s, %s);'
    params = (user_id, contenido, date_open, prioridad)
    await execute_query(sql_query, params)
    # -----------------------------------------------
    
    # Editamos el mensaje de los botones para confirmar
    await query_cb.edit_message_text(f"Tarea registrada")
    
    context.user_data.clear()
    return ConversationHandler.END

    current_update = update 
    user_id = current_update.effective_user.id
    
    # Validamos usuario (redundante por ConversationHandler pero seguro)
    if user_id != context.user_data.get('task_owner'):
        return EXPECTING_TASK

    contenido = current_update.message.text
    prioridad = context.user_data.get('priority')
    
    print(f"DEBUG: Tarea de {user_id} | Prioridad: {prioridad} | Contenido: {contenido}", flush=True)
    
    # --- PARA LOGICA DE BASE DE DATOS ---

    date_open = datetime.datetime.now()
    query = 'insert into "TASKS" (user_open, context_task, datetime_open, priority) values (%s, %s, %s, %s);'
    params = (user_id, contenido, date_open, prioridad)
    await execute_query(query, params)

    # -----------------------------------------------
    
    await update.message.set_reaction(reaction="👍")
    await current_update.message.reply_text("Tarea registrada.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el flujo."""
    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.edit_message_text("Operación cancelada.")
    else:
        await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END
