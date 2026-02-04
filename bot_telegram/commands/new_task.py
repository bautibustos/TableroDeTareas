from telegram import Update
from telegram.ext import ContextTypes
from bd.manage_bd import execute_query
import datetime



async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.set_reaction(reaction="✍")
    mensaje = update.message.text.replace('/task ', '')
    id_telegram = update.message.from_user.id
    date_open = datetime.datetime.now()
    query = 'insert into "TASKS" (user_open, context_task, datetime_open) values (%s, %s, %s);'
    params = (id_telegram, mensaje, date_open)
    await execute_query(query, params)
    await update.message.set_reaction(reaction="👍")
    
    