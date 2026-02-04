import os
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager


from bd.manage_bd import pool
from bot_telegram.run_bot import run_bot
from api.routes.tasks import router as tasks_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Conexión a BD
    await pool.open()
    
    # 2. Definir la tarea del bot
    token = os.getenv('TOKEN_BOT_TELEGRAM')
    # Usamos create_task para que no bloquee el inicio de la API
    bot_task = asyncio.create_task(run_bot(token))
    
    yield # Aquí la API empieza a recibir peticiones
    
    # 3. Limpieza al apagar
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    await pool.close()

app = FastAPI(lifespan=lifespan)
app.include_router(tasks_router, prefix="/api")