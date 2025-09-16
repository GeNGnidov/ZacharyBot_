from bot_main import register_name_mention_handler, bot, polling_start, players_online, chat_players, thread_chat_players, send_register_message
from utils import logger

if __name__ == "__main__":
    logger.info("Бот Захар стартует...")
    register_name_mention_handler(bot)

    logger.info("Помогатор бот-захар версии 2.0 на связи! Я уже работаю, так что не кипишуйте")
    bot.send_message(chat_players,
                     "Помогатор Захар на связи. Обновление 2.0:\n\n"
                     "1. Улучшена функция вызова бота по ключевому слову \"захаръ\":\n"
                     "-- Вместо bot.polling теперь работает функция bot.infinity_polling во избежание перебоев в связи с API Telebot или самим телеграмом\n"
                     "2. Добавлены уникальные реакции при входе и выходе игрока если игрок девушка, или среди игроков девушка. Список ников еще неполный.\n"
                     "3. Захар теперь пишет автоматические уведомления в специальный тред (ну, точнее, в этот). Вызвать Захара все еще можно в любом чате.", message_thread_id=thread_chat_players)

    polling_start()



    # Запускаем цикл опроса сервера
    players_online()
