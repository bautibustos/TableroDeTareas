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
from bd.manage_bd import execute_query
from bd.timezone_utils import now_ar
from psycopg.errors import ForeignKeyViolation
from .utils.conversation_timeout import generic_timeout_handler, make_default_choice_timeout


# Estados para la conversación
SELECTING_PRIORITY, EXPECTING_TASK, ASSIGN_TASK = range(3)


async def task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el comando /task, pide la tarea y pasa al estado EXPECTING_TASK."""
    await update.message.set_reaction(reaction="✍")
    context.user_data['task_owner'] = update.effective_user.id

    await update.message.reply_text(text="¿Cuál es la tarea?")

    await update.message.set_reaction(reaction="👍")
    return EXPECTING_TASK


async def handle_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != context.user_data.get('task_owner'):
        return EXPECTING_TASK

    contenido = update.message.text
    context.user_data['task_content'] = contenido

    keyboard = [
        [
            InlineKeyboardButton("Alta 🔴", callback_data="1"),
            InlineKeyboardButton("Media 🟡", callback_data="2"),
            InlineKeyboardButton("Baja 🟢", callback_data="3"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        "Selecciona la prioridad de la tarea:",
        reply_markup=reply_markup
    )
    context.user_data['choice_message_id'] = sent_message.message_id
    context.user_data['choice_chat_id'] = sent_message.chat_id

    # Definimos QUÉ hay que guardar si se cumple el timeout: prioridad Baja por defecto
    async def guardar_prioridad_baja(context):
        date_open = now_ar()
        sql_query = 'insert into "TASKS" (user_open, context_task, datetime_open, priority) values (%s, %s, %s, %s) returning id_task;'
        params = (user_id, contenido, date_open, "3")
        result = await execute_query(sql_query, params, fetch=True)
        task_id = result[0][0]  # AJUSTAR según cómo devuelva tu execute_query

        context.user_data['task_id'] = task_id
        # Como acá también hace falta pedir la asignación, seguimos la cadena:
        await assign_task(update, context)

    context.user_data['on_timeout'] = make_default_choice_timeout(
        guard_key='task_content',
        save_fn=guardar_prioridad_baja,
        texto_final="Tarea registrada con prioridad Baja."
    )

    return SELECTING_PRIORITY


async def handle_task_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_cb = update.callback_query
    await query_cb.answer()

    user_id = update.effective_user.id
    if user_id != context.user_data.get('task_owner'):
        return SELECTING_PRIORITY

    prioridad = query_cb.data
    contenido = context.user_data.get('task_content')

    date_open = now_ar()
    sql_query = 'insert into "TASKS" (user_open, context_task, datetime_open, priority) values (%s, %s, %s, %s) returning id_task;'
    params = (user_id, contenido, date_open, prioridad)
    result = await execute_query(sql_query, params, fetch=True)
    task_id = result[0][0]

    context.user_data['task_id'] = task_id

    await query_cb.edit_message_text("Tarea registrada, ahora asignala")

    await assign_task(update, context)

    # La conversación termina acá; la asignación se maneja de forma
    # independiente (handler global + job_queue), no como parte de este ConversationHandler.
    return ConversationHandler.END

async def assign_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Pide a quién asignar la tarea. Ya NO depende del ConversationHandler para
    su propio timeout: usa job_queue directamente, así funciona igual sea
    invocada desde el flujo normal o desde el timeout de prioridad.
    """
    query = '''
                SELECT id_user, name_user, id_telegram
                FROM "USERS"
            '''
    result = await execute_query(query, fetch=True)

    keyboard = []
    for user in result:
        # Prefijo "assign:" para distinguir estos botones de los de prioridad
        # cuando el handler global los reciba.
        keyboard.append(
            [InlineKeyboardButton(f"{user[1]}", callback_data=f"assign:{user[2]}")]
        )
    reply_markup = InlineKeyboardMarkup(keyboard)

    chat_id = update.effective_chat.id

    sent_message = await context.bot.send_message(
        chat_id=chat_id,
        text="¿A quién va destinada la tarea? (30s, si no elijo se autoasigna a quien la creó)",
        reply_markup=reply_markup
    )

    task_id = context.user_data.get('task_id')
    id_telegram_creador = context.user_data.get('task_owner')

    async def auto_asignar(job_context: ContextTypes.DEFAULT_TYPE):
        """Se ejecuta vía job_queue si nadie responde en 30s, sin depender
        de que la conversación siga formalmente activa."""
        query = 'UPDATE "TASKS" SET user_assigned = %s WHERE id_task = %s;'
        params = (id_telegram_creador, task_id)
        try:
            await execute_query(query, params)
        except ForeignKeyViolation:
            texto = "No se pudo autoasignar: registrate con /registro e intentá de nuevo."
        else:
            texto = "Se te autoasignó la tarea."

        try:
            await job_context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=sent_message.message_id,
                text=texto
            )
        except Exception:
            await job_context.bot.send_message(chat_id, texto)

    context.job_queue.run_once(
        auto_asignar,
        30,
        name=f"assign_timeout_{task_id}",
    )

    # Le avisamos al generic_timeout_handler que no borre user_data si venimos
    # de un timeout de prioridad encadenado.
    context.user_data['keep_alive'] = True

    return ASSIGN_TASK


async def handle_assign_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_cb = update.callback_query
    await query_cb.answer()

    user_id = update.effective_user.id
    if user_id != context.user_data.get('task_owner'):
        return

    id_telegram_asignado = query_cb.data.split(":", 1)[1]
    task_id = context.user_data.get('task_id')

    # Cancelamos el auto-asignado, ya que contestó a tiempo
    for job in context.job_queue.get_jobs_by_name(f"assign_timeout_{task_id}"):
        job.schedule_removal()

    query = 'UPDATE "TASKS" SET user_assigned = %s WHERE id_task = %s;'
    params = (id_telegram_asignado, task_id)
    try:
        await execute_query(query, params)
    except ForeignKeyViolation:
        await query_cb.edit_message_text(
            "No se pudo asignar: ese usuario ya no está registrado. Probá de nuevo con /task."
        )
    else:
        await query_cb.edit_message_text("Tarea asignada correctamente.")

    context.user_data.clear()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el flujo."""
    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.edit_message_text("Operación cancelada.")
    else:
        await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END