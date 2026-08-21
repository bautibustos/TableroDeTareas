from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bd.manage_bd import execute_query

import datetime

# Estado para la conversación de cierre
EXPECTING_OBSERVATION = 0

# Tiempo de espera (en segundos) para recibir la observación antes de cerrar
# la tarea automaticamente sin ella. Modificar este valor si hace falta otro plazo.
OBSERVATION_TIMEOUT = 3 * 60  # 3 minutos


async def close_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia /close <id_tarea>: valida que exista, que no esté cerrada y que
    quien pide el cierre sea la persona asignada. Si todo ok, pide la
    observación de cierre y pasa a EXPECTING_OBSERVATION."""
    await update.message.set_reaction(reaction="✍")

    id_telegram = update.message.from_user.id
    texto = update.message.text.replace('/close', '').strip()

    try:
        id_task = int(texto)
    except ValueError:
        await update.message.reply_text('Uso correcto: `/close <id_tarea>`\nEj: `/close 42`')
        return ConversationHandler.END

    query = 'SELECT user_assigned, datetime_closed FROM "TASKS" WHERE id_task = %s;'
    result = await execute_query(query, (id_task,), fetch=True)

    if not result:
        await update.message.reply_text(f'No se encontró la tarea #{id_task}.')
        return ConversationHandler.END

    user_assigned, datetime_closed = result[0]

    if datetime_closed is not None:
        await update.message.reply_text(f'La tarea #{id_task} ya está cerrada.')
        return ConversationHandler.END

    if user_assigned != id_telegram:
        await update.message.reply_text('Solo la persona asignada a la tarea puede cerrarla.')
        return ConversationHandler.END

    context.user_data['close_task_id'] = id_task
    context.user_data['close_owner'] = id_telegram
    context.user_data['close_chat_id'] = update.effective_chat.id

    minutos = OBSERVATION_TIMEOUT // 60
    await update.message.reply_text(
        f'¿Cuál es la observación de cierre? '
        f'(tenés {minutos} minutos; si no respondés, la tarea se cierra sin observación)'
    )
    return EXPECTING_OBSERVATION


async def close_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la observación de cierre, cierra la tarea y la guarda en extra_info_1."""
    user_id = update.effective_user.id
    if user_id != context.user_data.get('close_owner'):
        return EXPECTING_OBSERVATION

    id_task = context.user_data.get('close_task_id')
    observacion = update.message.text
    date_close = datetime.datetime.now()

    query = '''
        UPDATE "TASKS" SET user_closed = %s,
        datetime_closed = %s,
        extra_info_1 = %s
        WHERE id_task = %s
        '''
    params = (user_id, date_close, observacion, id_task)
    await execute_query(query, params)

    await update.message.reply_text(f'Tarea #{id_task} cerrada con éxito.')
    await update.message.set_reaction(reaction="👍")
    context.user_data.clear()
    return ConversationHandler.END


async def close_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Se dispara si no llega una observación dentro de OBSERVATION_TIMEOUT:
    cierra la tarea igual, sin observación."""
    id_task = context.user_data.get('close_task_id')
    user_id = context.user_data.get('close_owner')
    chat_id = context.user_data.get('close_chat_id')

    if id_task is None:
        context.user_data.clear()
        return ConversationHandler.END

    date_close = datetime.datetime.now()
    query = '''
        UPDATE "TASKS" SET user_closed = %s,
        datetime_closed = %s
        WHERE id_task = %s
        '''
    params = (user_id, date_close, id_task)
    await execute_query(query, params)

    if chat_id:
        await context.bot.send_message(
            chat_id,
            f'Se venció el tiempo de espera: la tarea #{id_task} se cerró automáticamente sin observación.'
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el flujo de cierre."""
    context.user_data.clear()
    await update.message.reply_text('Cierre cancelado.')
    return ConversationHandler.END
