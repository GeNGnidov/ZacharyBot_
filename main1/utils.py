import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s %(funcName)s %(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs.log', mode="w", encoding='utf-8'),
        logging.StreamHandler()
    ]

)

logger = logging.getLogger(__name__)

def send_error_message(message):
    from bot_main import bot, chat_admin
    bot.send_message(chat_admin, message)
def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            message = f"В результате работы функции {func.__name__} произошла ошибка: {e}"
            logger.error(f"В результате работы функции {func.__name__} произошла ошибка: {e}", exc_info=True)
            send_error_message(message)
    return wrapper