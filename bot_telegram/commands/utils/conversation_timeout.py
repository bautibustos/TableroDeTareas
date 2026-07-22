from functools import partial
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def generic_timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler de timeout genérico para cualquier ConversationHandler.
    Ejecuta lo que esté guardado en context.user_data['on_timeout'], si existe.
    """
    callback = context.user_data.get('on_timeout')

    if callback is None:
        context.user_data.clear()
        return ConversationHandler.END

    try:
        await callback(update, context)
    except Exception as e:
        print(f"ERROR en timeout callback: {e}", flush=True)
    finally:
        # Si el callback dejó un flujo en marcha (ej: pasó a pedir la asignación),
        # no limpiamos user_data para no perder esos datos.
        if not context.user_data.pop('keep_alive', False):
            context.user_data.clear()

    return ConversationHandler.END


async def _finalize_message(context, chat_id, message_id, texto_final):
    """Edita el mensaje de los botones, o manda uno nuevo si falla la edición."""
    if chat_id and message_id:
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=texto_final)
            return
        except Exception:
            pass
    if chat_id:
        await context.bot.send_message(chat_id, texto_final)


async def _default_choice_action(update, context, *, guard_key, save_fn, texto_final):
    """
    Acción GENÉRICA para "si no elige nada, aplicar valor por defecto".
    No la llames directamente: se usa con functools.partial (ver make_default_choice_timeout).

    guard_key: user_data key que confirma que el flujo llegó a un punto guardable
               (ej. 'task_content'). Si no está, no hace nada.
    save_fn:   async callable(context) -> None. Hace el insert/lo que sea con el valor default.
    texto_final: texto a mostrar al usuario cuando se aplica el default.
    """
    if not context.user_data.get(guard_key):
        return

    await save_fn(context)

    chat_id = context.user_data.get('choice_chat_id')
    message_id = context.user_data.get('choice_message_id')
    await _finalize_message(context, chat_id, message_id, texto_final)


def make_default_choice_timeout(*, guard_key: str, save_fn, texto_final: str):
    """
    Factory: devuelve una función de timeout lista para asignar a
    context.user_data['on_timeout'], sin tener que escribir una nueva
    función async por cada comando.

    Uso típico dentro del handler que muestra los botones:

        context.user_data['on_timeout'] = make_default_choice_timeout(
            guard_key='task_content',
            save_fn=mi_funcion_de_guardado,
            texto_final="⏳ Se agotó el tiempo. Prioridad Baja aplicada."
        )
    """
    return partial(_default_choice_action, guard_key=guard_key, save_fn=save_fn, texto_final=texto_final)