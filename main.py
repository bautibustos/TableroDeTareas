import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Configuración de estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Registro de rutas de la API
app.include_router(tasks_router, prefix="/api")

# Ruta para la Pizarra Web
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})