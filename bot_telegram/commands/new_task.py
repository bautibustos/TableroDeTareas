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
    """Inicia el comando /task y muestra los botones de prioridad."""
    context.user_data['task_owner'] = update.effective_user.id
    
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
    return SELECTING_PRIORITY

async def handle_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        ### Maneja la selección de la prioridad y pide el contenido.
    """
    query = update.callback_query
    await query.answer()
    
    # Validamos que el que toque el botón sea el dueño de la tarea
    if query.from_user.id != context.user_data.get('task_owner'):
        return SELECTING_PRIORITY

    # Guardamos la prioridad seleccionada
    prioridad = query.data
    context.user_data['priority'] = prioridad
    
   # prioridades_texto = {"1": "Baja", "2": "Media", "3": "Alta"}
    
    # Mensaje que solicita la tarea nueva
    await query.edit_message_text(
        text=f"¿Cual es la tarea?",
    )
    return EXPECTING_TASK

async def handle_task_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el contenido final de la tarea."""
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
