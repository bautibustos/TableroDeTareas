import os
import asyncio
from psycopg_pool import AsyncConnectionPool

# --- CONFIGURACIÓN DE CONEXIÓN USANDO OS.GETENV ---
CONN_INFO = (
    f"host={os.getenv('db_host', 'localhost')} "
    f"dbname={os.getenv('db_name', 'postgres')} "
    f"user={os.getenv('db_user', 'postgres')} "
    f"password={os.getenv('db_pass', 'admin')} "
    f"port={os.getenv('db_port', '5432')}"
)

# Creamos el pool global
pool = AsyncConnectionPool(conninfo=CONN_INFO, open=False)

async def execute_query(query, params=None, fetch=False):
    """
    Ejecuta consultas de forma asíncrona usando el pool.
    """
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SET search_path TO batata, public;")
            await cur.execute(query, params)
            
            if fetch:
                return await cur.fetchall()
            return None