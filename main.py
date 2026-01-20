import os

import bot_telegram.run_bot as run_bot

token_bot = os.getenv('token_bot_telegram')


if __name__ == '__main__':

    run_bot.run_bot(token_bot)
