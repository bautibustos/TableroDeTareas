from telegram import Update
from telegram.ext import ContextTypes

from bd.manage_bd import execute_query

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_telegram = update.message.from_user.id
    query = 'SELECT EXISTS(SELECT 1 FROM "USERS" WHERE id_telegram = %s);'
    # execute_query debe retornar el primer valor del primer registro
    answer = await execute_query(query, (id_telegram,), fetch=True)
    if answer[0][0]:
        await update.message.reply_text('El usuario ya está registrado')
    else:
        query='INSERT INTO "USERS" (id_telegram, name_user) VALUES (%s, %s);'
        nombre = str(update.message.text).replace('/registro ', '')
        await execute_query(query, (id_telegram, nombre))
        await update.message.reply_text('Usuario registrado con exito')