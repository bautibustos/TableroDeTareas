from telegram import Update
from telegram.ext import ContextTypes
from bd.manage_bd import execute_query

async def list_task_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ''' Comando para listar tareas /list '''
    #await update.message.set_reaction(reaction="")
    id_telegram = update.message.from_user.id

    try:
        #trae las tareas abiertas y la descripcion
        query = '''
            SELECT id_task, context_task FROM "TASKS" where user_closed IS NULL
            '''  
        tasks = await execute_query(query, fetch=True)
        # Función para resumir la descripción a las primeras n palabras
        def resumen(desc, n=5):
            palabras = desc.split()
            resumen = ' '.join(palabras[:n])
            if len(palabras) > n:
                resumen += '...'
            return resumen
        
        await update.message.reply_text('Tareas abiertas:\n' + '\n' + '\n'.join([f"#{task[0]} - {resumen(task[1])}" for task in tasks]))

    except ValueError:
    # Si no es un número válido
        await update.message.reply_text('Comando incorrecto. Uso correcto: `/list`')
    except Exception as e:
    # Cualquier otro error (ej: tarea no existe)
        await update.message.reply_text(f'Error al listar tareas: {str(e)}\nNo hay tareas abiertas o no existen')