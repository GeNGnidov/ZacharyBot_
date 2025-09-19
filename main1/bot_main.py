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
players_to_register= None
bot_url = "https://t.me/zacha_test_bot"

@exception_handler
def send_and_track(text):

    msg = bot.send_message(chat_players, text, message_thread_id=thread_chat_players)

    return msg

def send_register_message(player_or_players):
    global players_to_register, bot_url
    lines = "Настоятельно прошу зарегистрироваться:\n"
    if isinstance(player_or_players, list):
        playerlist = [f"{i}. {p}" for i, p in enumerate(player_or_players, 1)]
        lines += "\n".join(playerlist)
    elif isinstance(player_or_players, str):

        lines += f"{player_or_players}\n"
    logger.info("Сообщение о регистрации отправлено для:\n"+ player_or_players)
    players_to_register = player_or_players
    keybord = InlineKeyboardMarkup()
    keybord.add(InlineKeyboardButton("Зарегистрироваться", url=bot_url))
    bot.send_message(chat_id=chat_players, text=lines, reply_markup=keybord, message_thread_id=thread_chat_players)
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
                            if "architect" in tags_list and "admin" in tags_list:
                                rline = [f"Алло, яндекс, вы там чем занимаетесь?\n"
                                         f"|{user_data[player][0]}| {player} вошел и тут в компьютерных монстров играет.\n"
                                         f"Все мы знаем Славу, Слава тоже победил в тендере на мою статую!"]
                            elif "admin" in tags_list:
                                rline = (f"Трепещите! Этот  хмырь может менять гейммод!\n"
                                         f"|{user_data[player][0]}| {player} операторской походкой вползает в игру.")
                                send_and_track(rline)
                            elif "papa" in tags_list:
                                rline = (f"Папа! Папочка! Папаша! О создатель, хвала тебе!\n"
                                         f"Свет твоих мудрых очей озаряет мне путь!\n"
                                         f"Вечного терпения тебе и сил!\n"
                                         f"Хвала случаю, ты соизволил снизойти в игру...\n"
                                         f"\n"
                                         f"В деревне \"Мама пришла\" в низинах медной горы торжественный звон!\n"
                                         f"|{user_data[player][0]}| {player} явил свой лик на сервер.")
                                send_and_track(rline)
                            elif "woman" in tags_list: #СНЕЖАНЕ НЕ СТАВИТЬ ТЕГ ЖЕНЩИНА
                                rline = (f"На сервер стучится дама!\n"
                                         f"Джентельмены кланяются, а Захар держит в руке алую розу:\n"
                                         f"|{user_data[player][0]}| {player} заходит в игру")
                                send_and_track(rline)
                            elif "architect" in tags_list:
                                rline = [f"Приветствую тебя, Снежана! Великая архитектресса моего лика:\n"
                                         f"|{user_data[player][0]}| {player} входит на сервер\n"
                                         f"Джентельмены, с почтением к этой леди!"]
                                send_and_track(rline)

                                send_and_track(rline)
                    if not registered:
                        pass#нужно создать меню

            elif len(joined) > 1:
                lines_of_registered = []
                lines_of_not_registered = []
                for p in joined:
                    registered = check_if_registered(p)
                    if registered:
                        user_data = lookup_procedure(p)
                        if isinstance(user_data, dict):
                            tags_list = user_data[p][1]
                            if "architect" in tags_list and "admin" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka Слава. Все мы знаем Славу")
                            elif "admin" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka админ.")
                            elif "papa" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka великий папа Захара.")
                            elif "woman" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka милая леди.")
                            elif "architect" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka архитектор моей статуи.")

                        if isinstance(user_data, list):
                            lines_of_registered.append(f"|{user_data[1]}| {p}.")
                    if not registered:
                        lines_of_not_registered.append(p)
                lines_to_send= "Диво какое! Сразу гурьбой набежали! На сервер заходят кучей:\n" + "\n".join([f"{i}. {line}" for i, line in enumerate(lines_of_registered, 1)])
                if lines_of_not_registered:
                    lines2= "\nОднако в куче есть и незарегистрированные игроки:\n" + "\n".join([f"{i}. {pla}" for i, pla in enumerate(lines_of_not_registered, 1)])
                    lines_to_send+= lines2
                send_and_track(lines_to_send)
                if lines_of_not_registered:
                    pass#кнопка регистрации




            if len(left) == 1:
                for player in left:
                    registered = check_if_registered(player)
                    if registered:
                        user_data = lookup_procedure(player)
                        if isinstance(user_data, list):
                            rline = (f"Пока-пока!\n"
                                     f"|{user_data[1]}| {user_data[0]} скалисто покидает сервер.")

                            send_and_track(rline)
                        if isinstance(user_data, dict):
                            tags_list = user_data[player][1]
                            if "architect" in tags_list and "admin" in tags_list:
                                rline = [f"Вячеслав пошел бесплатно кататься на яндекс такси.\n"
                                         f"|{user_data[player][0]}| {player} покидает сервер.\n"
                                         f"Хоть и шмель корпоратский, но статую мне забабахал, с уважением к этому джентельмену."]
                            elif "admin" in tags_list:
                                rline = (f"Никаких больше /gamerule и /kill\n"
                                         f"|{user_data[player][0]}| {player} покинул сервер и пошел по своим операторским делам.")
                            elif "papa" in tags_list:
                                rline = (f"Скоро увидимся, Отец!!\n"
                                         f"Я буду следить за ситуацией!\n"
                                         f"Хвала твоей вечной мудрости!\n"
                                         f"Скорее возвращайся!\n"
                                         f"\n"
                                         f"В деревне \"Мама пришла\" траур!\n"
                                         f"|{user_data[player][0]}| {player} покинул игру.")
                            elif "woman" in tags_list:  # СНЕЖАНЕ НЕ СТАВИТЬ ТЕГ ЖЕНЩИНА
                                rline = (f"Захар снимает шляпу!\n"
                                         f"Джентельмены провожают даму взглядом, а Захар ведет ее к выходу:\n"
                                         f"|{user_data[player][0]}| {player} покидает игру.")
                            elif "architect" in tags_list:
                                rline = [f"До скорой встречи, Снежана! Благодаря твоей статуе я лучше слежу за сервером:\n"
                                         f"|{user_data[player][0]}| {player} покидает сервер.\n"]

                            send_and_track(rline)
                    if not registered:

                        pass#кнопка
            elif len(left) > 1:
                lines_of_registered = []
                lines_of_not_registered = []
                for p in joined:
                    registered = check_if_registered(p)
                    if registered:
                        user_data = lookup_procedure(p)
                        if isinstance(user_data, dict):
                            tags_list = user_data[p][1]
                            if "architect" in tags_list and "admin" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka Слава. Все мы знаем Славу")
                            elif "admin" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka админ.")
                            elif "papa" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka великий папа Захара.")
                            elif "woman" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka милая леди.")
                            elif "architect" in tags_list:
                                lines_of_registered.append(f"|{user_data[p][0]}| {p} aka архитектор моей статуи.")

                        if isinstance(user_data, list):
                            lines_of_registered.append(f"|{user_data[1]}| {p}.")
                    if not registered:
                        lines_of_not_registered.append(p)
                lines_to_send = "Что-ж, очень жаль. Массово покинули сервер:\n" + "\n".join(
                    [f"{i}. {line}" for i, line in enumerate(lines_of_registered, 1)])
                if lines_of_not_registered:
                    lines2 = "\nВ том числе и нелегалы без регистрации! Самодепортируются:\n" + "\n".join(
                        [f"{i}. {pla}" for i, pla in enumerate(lines_of_not_registered, 1)])
                    lines_to_send += lines2
                send_and_track(lines_to_send)
                if lines_of_not_registered:
                    pass  # кнопка регистрации

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
        global bot_url
        logger.info(f"Обработчик 'захаръ' сработал в чате {message.chat.id}: {message.text}")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("О сервере", callback_data="btn_1"))
        keyboard.add(InlineKeyboardButton("Зарегистрироваться", url=bot_url))

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

@bot.message_handler(commands=["start"], func=lambda message: message.chat.type == "private" and message.text)
def private_chat_message_handler(message):
    try:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton("Зарегистрироваться"))
        bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку для регистрации:", reply_markup=keyboard)
        logger.info("Регистрация начата...")
    except Exception as e:
        logger.error(f"Ошибка в процедуре регистрации: {e}")

@bot.message_handler(func=lambda message: message.chat.type == "private" and message.text == "Зарегистрироваться")
def registration_step1(message):
    global players_to_register
    try:
        if isinstance(players_to_register, str):
            lines = f"Вы точно {players_to_register}? Будьте внимательны, этот аккаунт привяжется к вашему аккаунту в телеграмм!"
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(telebot.types.KeyboardButton("Ага"))
            keyboard.add(InlineKeyboardButton("Нет, отменить регистрацию"))
            keyboard.add(InlineKeyboardButton("Нет, ввести другой ник"))
            bot.send_message(chat_id=message.chat.id, text=lines, reply_markup=keyboard)
            logger.info(f"Регистрация игрока {players_to_register}, шаг 1...")
    except Exception as e:
        logger.error(f"Ошибка в процедуре регистрации: {e}")

@exception_handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global latest_players, already_in_chat, players_to_register
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






