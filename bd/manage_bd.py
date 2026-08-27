import os
import asyncio
from psycopg import sql
from psycopg_pool import AsyncConnectionPool

# --- CONFIGURACIÓN DE CONEXIÓN USANDO OS.GETENV ---
CONN_INFO = (
    f"host={os.getenv('db_host')} "
    f"dbname={os.getenv('db_name')} "
    f"user={os.getenv('db_user')} "
    f"password={os.getenv('db_pass')} "
    f"port={os.getenv('db_port')}"
)

# Schema de Postgres a usar: viene de env, sin default, para forzar que cada
# entorno (dev/producción) lo elija explícitamente y no se mezclen datos de
# prueba con datos reales (ver CLAUDE.md).
DB_SCHEMA = os.getenv('db_schema')

# Creamos el pool global
pool = AsyncConnectionPool(conninfo=CONN_INFO, open=False)

async def execute_query(query, params=None, fetch=False):
    """
    Ejecuta consultas de forma asíncrona usando el pool.
    """
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql.SQL("SET search_path TO {}, public;").format(sql.Identifier(DB_SCHEMA))
            )
            await cur.execute(query, params)

            if fetch:
                return await cur.fetchall()
            return None
        
