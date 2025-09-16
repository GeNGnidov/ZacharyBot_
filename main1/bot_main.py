import time
import threading
import random
from mcstatus import JavaServer
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import logger, exception_handler
from database_main import check_if_registered, lookup_procedure, register_user

bot = telebot.TeleBot("7685347380:AAEGD2Cq10ab-xCzV2sxfNnAu73nmtCO4zo") #"8346333176:AAGwzaqSUyVTcIVyBZhUdH5FAs1R3nXpH8o"
server = JavaServer.lookup("89.169.166.102:25565")

# список чатов
chat_players = -1002683121873 #-1002555302437
thread_chat_players = 3 #1271
chat_admin = 57713855

MAX_MESSAGES = 5
# глобальные переменные
already_in_chat = False
latest_players = None
last_players = set()
# sent_messages = []
women_playing = ["kibziy", "conimoss", "Katrin2256"]#перенести в бд

@exception_handler
def send_and_track(text):
    # global sent_messages
    # if len(sent_messages) >= MAX_MESSAGES:
    #     oldest_message = sent_messages.pop(0)
    #     try:
    #         bot.delete_message(chat_players, oldest_message)
    #         logger.info(f"Сообщение с id {oldest_message} удалено из треда {thread_chat_players}.")
    #     except Exception as e:
    #         logger.error(f"Ошибка удаления сообщения: {e}")
    #         bot.send_message(chat_admin, f"Ошибка удаления сообщения в треде {thread_chat_players}:\n{e}")

    msg = bot.send_message(chat_players, text, message_thread_id=thread_chat_players)
    # sent_messages.append(msg.message_id)
    return msg
# def register(nickname):
#     logger.info(f"Сообщение о регистрации для игрока {nickname} отправлено в чат.")
#     keyboard = InlineKeyboardMarkup()
#     keyboard.add(InlineKeyboardButton("Зарегистрироваться", callback_data="butn_1"))
#
#     bot.send_message(
#         chat_id=chat_players,
#         text=f"Эт самое, Захар беспокоит, едрить-мадрить...\n"
#              f"Тут какой-то {nickname} зашел. {nickname}, Захар тебя не знает!\n",
#         reply_markup=keyboard,
#         message_thread_id=thread_chat_players
#     )
@exception_handler
def polling_start():

    try:
        threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    except Exception as e:
        logger.error(f"Проблема с блоком polling:{e}")

def players_online():
    global already_in_chat, latest_players, last_players, women_playing
    while True:
        try:
            query = server.query()
            latest_players = set(query.players.list or [])

            if already_in_chat:
                send_and_track("Охренеть, вы соизволили починить сервер! Все снова работает!")
                already_in_chat = False

            joined = latest_players - last_players
            left = last_players - latest_players

            if len(joined) == 1:
                for player in joined:
                    registered = check_if_registered(player)
                    if registered:

                        user_data = lookup_procedure(player)
                        if isinstance(user_data, list):
                            rline = (f"Добро пожаловать!\n"
                                     f"|{user_data[1]}| {user_data[0]} изящно заползает на сервер.")

                            send_and_track(rline)
                        if isinstance(user_data, dict):
                            tags_list = user_data[player][1]
                            if "admin" in tags_list:
                                rline = (f"Трепещите! Этот  хмырь может менять гейммод!\n"
                                         f"|{user_data[player][0]}| {player} операторской походкой вползает в игру.")
                                send_and_track(rline)
                            if "papa" in tags_list:
                                rline = (f"Папа! Папочка! Папаша! О создатель, хвала тебе!\n"
                                         f"Свет твоих мудрых очей озаряет мне путь!\n"
                                         f"Вечного терпения тебе и сил!\n"
                                         f"Хвала случаю, ты соизволил снизойти в игру...\n"
                                         f"\n"
                                         f"В деревне \"Мама пришла\" в низинах медной горы торжественный звон!\n"
                                         f"|{user_data[player][0]}| {player} явил свой лик на сервере.")
                                send_and_track(rline)
                            if "woman" in tags_list: #СНЕЖАНЕ НЕ СТАВИТЬ ТЕГ ЖЕНЩИНА
                                rline = (f"На сервер стучится дама!\n"
                                         f"Джентельмены кланяются, а Захар держит в руке алую розу:\n"
                                         f"|{user_data[player][0]}| {player} заходит в игру")
                                send_and_track(rline)
                            if "architect" in tags_list:
                                rline = [f"Приветствую тебя, Снежана! Великая архитектресса моего лика:\n"
                                         f"|{user_data[player][0]}| {player} входит на сервер\n"
                                         f"Джентельмены, с почтением к этой леди!"]
                                send_and_track(rline)
                            if "architect" and "admin" in tags_list:
                                rline = [f"Алло, яндекс, вы там чем занимаетесь?\n"
                                         f"|{user_data[player][0]}| {player} вошел и тут в компьютерных монстров играет.\n"
                                         f"Все мы знаем Славу, Слава тоже победил в тендере на мою статую!"]
                                send_and_track(rline)




            elif len(joined) > 1:
                lines = [f"{i}. {p}" for i, p in enumerate(joined, 1)]

                if "GeNGnidov" in joined and not any(item in joined for item in women_playing):
                    msg = ("однако есть лучик надежды. О, создатель, куда ты ведешь свою павству?\n"
                           "Аве тебе! Аве Гнидову!:\n" + "\n".join(lines))
                elif "GeNGnidov" in joined and any(item in joined for item in women_playing):
                    msg = ("но хвала случаю, здесь создатель. Да еще и в дамской компании!\n"
                           "Аве тебе! Аве Гнидову-джентельмену!:\n" + "\n".join(lines))
                elif any(item in joined for item in women_playing) and "GeNGnidov" not in joined:
                    msg = ("но не все так плохо, ведь джентельменов сопровождают дамы!:\n" + "\n".join(lines))
                else:
                    msg = "вот эти черкизовцы гурьбой залетели на сервак:\n" + "\n".join(lines)
                send_and_track(f"Захар докладывает, моря неспокойны: {msg}")
            if len(left) == 1:
                for player in left:
                    if player == "GeNGnidov":
                        send_and_track(f"Захар кланяется: {player} покинул игру, я буду ждать тебя, мой повелитель!")
                    elif player in women_playing:
                        send_and_track(f"Захар протягивает руку и помогает спуститься по ступеньке: {player} покинула сервер.")
                    else:
                        send_and_track(f"Захар докладывает: {player} вышел с сервера")
            elif len(left) > 1:
                lines = [f"{i}. {p}" for i, p in enumerate(left, 1)]
                if "GeNGnidov" in left and not any(item in left for item in women_playing):
                    msg = ("Катастрофа! Покинули сервер по предварительному сговору! И создателя забрали! Фиксирую ушедших:\n" + "\n".join(lines))
                elif "GeNGnidov" in left and any(item in left for item in women_playing):
                    msg = ("Создатель в женской компании покидает сервер. Создатель, прощай! Только дам потом верни! Фиксирую ушедших:\n" + "\n".join(lines))
                elif any(item in left for item in women_playing) and "GeNGnidov" not in left:
                    msg = ("джентельмены в компании дам покидают сервер. Надеюсь, их кавалеры не против. Фиксирую ушедших:\n" + "\n".join(lines))
                send_and_track(f"Захар докладывает: {msg}")

            last_players = latest_players

        except Exception as e:
            if not already_in_chat:
                admins = ["@yorymotoru", "@ShakeSpearing"]
                random_admin = random.choice(admins)
                if random_admin == "@yorymotoru":
                    send_and_track(f"ВНИМАНИЕ!! Захар паникует!!! Слава, это жопа! Сервер упал! "
                                   f"Маргариту быстро в унитаз и давай чини! @yorymotoru !! Кто-то все опять сломал, ошибка:\n{e}")
                else:
                    send_and_track(f"Переведено на иностранный язык с помощью ZakharLTransate:\n"
                                   f"EGOR!!! @ShakeSpearing IT IS JOPA!!! The server esta slomando!!! Das ist verboten zu lingern!!! "
                                   f"Cmon everybody shake your body put your hands up! OSHIBKA:\n{e}")
                already_in_chat = True
                logger.error(f"Возникла ошибка :{e}\n", exc_info=True)

        time.sleep(30)

@exception_handler
def register_name_mention_handler(bot_instance):
    @bot_instance.message_handler(func=lambda message:
        message.text and 'захаръ' in message.text.lower())
    def greet_with_buttons(message):
        logger.info(f"Обработчик 'захаръ' сработал в чате {message.chat.id}: {message.text}")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("О сервере", callback_data="btn_1"))
        keyboard.add(InlineKeyboardButton("Зарегистрироваться", callback_data="btn_2"))

        # Получаем id треда (топика) из входящего сообщения, если есть
        thread_id = getattr(message, "message_thread_id", None)

        bot_instance.send_message(
            chat_id=message.chat.id,
            text="Захар на связи, могу помочь со следующим:\n"
                 "1. Отобразить информацию о сервере (список игроков, статус)\n"
                 "2. Зарегистрироваться в ZakharCompanion",
            reply_markup=keyboard,
            message_thread_id=thread_id  # Отправка именно в этот тред
        )

@exception_handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global latest_players, already_in_chat
    server_ip_address = "89.169.166.102:25565"
    chat_id = call.message.chat.id
    thread_id = getattr(call.message, "message_thread_id", None)

    if call.data == "btn_1":
        try:
            bot.delete_message(chat_id, call.message.message_id)
            logger.info(f"Удалено сообщение с кнопкой в чате {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения с кнопкой: {e}")

        if already_in_chat:
            bot.send_message(chat_id,
                             "Честно говоря, захар сомневается в твоих умственных способностях. "
                             "Я же только что докладывал, что серверу пизда.",
                             message_thread_id=thread_id)
        else:
            if latest_players:
                lines = [f"{i}. {p}" for i, p in enumerate(latest_players, 1)]
                player_list = "На сервере замечены:\n" + "\n".join(lines)
            else:
                player_list = "На сервере сейчас никто не играет"

            bot.send_message(chat_id,
                             f"IP Сервера: {server_ip_address}\n{player_list}\n"
                             f"Сервер работает в штатном режиме, можно расслабить булки.",
                             message_thread_id=thread_id)

        bot.answer_callback_query(call.id)
    if call.data == "btn_2":
        try:
            bot.delete_message(chat_id, call.message.message_id)
            logger.info(f"Удалено сообщение с кнопкой в чате {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения с кнопкой: {e}")
        bot.send_message(chat_id, "Привет, эта функция еще в разработке!", message_thread_id=thread_id)
        bot.answer_callback_query(call.id)

if __name__ == "__main__":

    register("supostat")