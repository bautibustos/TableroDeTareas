import os
import asyncio


import bot_telegram.run_bot as run_bot
from bd.manage_bd import pool

token_bot = os.getenv('TOKEN_BOT_TELEGRAM')

async def main():
    await pool.open()
    # El bloque finally asegura que el pool se cierre al detener el proceso
    try:
        await run_bot.run_bot(token_bot)
    finally:
        await pool.close()

if __name__ == '__main__':
    asyncio.run(main())