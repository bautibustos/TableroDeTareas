from telegram import Update
from telegram.ext import ContextTypes
from bd.manage_bd import execute_query

import datetime


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.set_reaction(reaction="✍")
    id_telegram = update.message.from_user.id
    date_close = datetime.datetime.now()
    id_task = update.message.text.replace('/close ', '')

    try:
        query = '''
            UPDATE "TASKS" SET user_closed = %s, 
            datetime_closed = %s 
            WHERE id_task = %s  
            '''
        params = (id_telegram, date_close, id_task)
        await execute_query(query, params)
        await update.message.set_reaction(reaction="👍")
        
    except ValueError:
    # Si no es un número válido
        await update.message.reply_text('Uso correcto: `/close <id_tarea>`\nEj: `/close 42`')
    except Exception as e:
    # Cualquier otro error (ej: tarea no existe)
        await update.message.reply_text(f'Error al cerrar: {str(e)}\nLa tarea ya está cerrada o no existe')