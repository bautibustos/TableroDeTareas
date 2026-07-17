from telegram import Update
from telegram.ext import ContextTypes
from bd.manage_bd import execute_query

async def detail_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #await update.message.set_reaction(reaction="📜")
    id_telegram = update.message.from_user.id

    try:
            texto = update.message.text.replace('/tkt', '')
            id = int(texto)
            if not texto:
                await update.message.reply_text(
                    "Uso incorrecto. Uso correcto:\n/tkt <id_tarea>"
                )
                return
            
            query = '''
                SELECT t.context_task, t.user_open, t.datetime_open, t.priority, u.name_user
                FROM "TASKS" t
                LEFT JOIN "USERS" u ON t.user_open = u.id_telegram
                WHERE t.id_task = %s AND t.user_closed IS NULL
            '''

            result = await execute_query(query, (id,), fetch=True)

            if not result:
                await update.message.reply_text(f"No se encontró la tarea #{id} (o ya está cerrada).")
                return

            context_task, user_open, datetime_open, priority, name_user = result[0]

            priority_dict = {1: "🔴Alta", 2: "🟡Media", 3: "🟢Baja"}

            await update.message.reply_text(
                f"Tarea #{id}\n"
                f"Prioridad: {priority_dict[priority]}\n"
                f"Descripción: {context_task}\n"
                f"Abierta por: {name_user}\n"
                f"Fecha: {datetime_open}\n"
            )

    except ValueError as e:
            await update.message.reply_text(f"Ocurrió un error al procesar el id de la tarea. {e}")
    except Exception as e:
            await update.message.reply_text(f"Ocurrió un error inesperado al buscar la tarea. {e}")