from sqlalchemy import create_engine, Integer, String, Column, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


from utils import logger, exception_handler



engine = create_engine("sqlite:///maindb.db")

Base = declarative_base()

class TGuser(Base):
    __tablename__ = "tg_users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False)

    tguserowners = relationship("MCuser", back_populates="tguser_main")
    tagowners= relationship("Tag", back_populates="tags_main")
class Tag(Base):
    __tablename__ = "ooc_tags"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("tg_users.id"))
    tag = Column(String, nullable=False)

    tags_main= relationship("TGuser", back_populates="tagowners")

class MCuser(Base):
    __tablename__ = "minecraft_users"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey("tg_users.id"))
    nickname = Column(String, nullable=False)
    rank = Column(String, default="Гость")

    tguser_main = relationship("TGuser", back_populates="tguserowners")
    levels_main= relationship('Levels', back_populates="levelowners")
    inventories_main= relationship("Inventory", back_populates="inventoryowners")
class Levels(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("minecraft_users.id"))
    current_xp = Column(Integer, default=0)
    needed_xp = Column(Integer, default=200)
    player_lvl = Column(Integer, default=1)


    levelowners= relationship("MCuser", back_populates="levels_main")
class Inventory(Base):
    __tablename__ = "player_inventory"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("minecraft_users.id"))
    money = Column(Integer, default=0)
    backpack = Column(String, nullable=True)

    inventoryowners= relationship("MCuser", back_populates="inventories_main")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

@exception_handler
def register_user(user_tg:int, user_nickname:str, new_user_tag=None):#обработать наличие
    """Main function, registers the user

    kwargs:

    user_tg -- int, automatically while registering

    user_nickname -- string, minecraft playername, manual input by user or automatically

    new_user_tag -- string, mostly for test usage

    returns:

    finish_line -- string, message that contains details about how the registration passed

    something_wrong -- boolean, True if is"""
    something_wrong = False

    telegramm_user = session.query(TGuser).filter_by(tg_id=user_tg).first()
    if telegramm_user:
        finish_line = f"Пользователь с айди {user_tg} уже существует."
        logger.info(finish_line)

        something_wrong = True
        return finish_line, something_wrong

    new_tg_user= TGuser(tg_id=user_tg)
    session.add(new_tg_user)
    session.flush()
    logger.info(f"Пользователь {user_tg} добавлен в таблицу пользователей...")

    if new_user_tag is not None:
        new_tg_user_tag = Tag(owner=new_tg_user.id, tag=new_user_tag)
        session.add(new_tg_user_tag)
        session.flush()
        logger.info(f"Во время регистрации пользователю {user_tg} присвоен тег {new_user_tag}...")

    minecraft_user = session.query(MCuser).filter_by(nickname=user_nickname).first()
    if minecraft_user:
        finish_line = f"Игрок с ником {user_nickname} уже существует."
        logger.info(finish_line)

        something_wrong = True
        return finish_line, something_wrong

    new_minecraft_user = MCuser(tg_user_id=new_tg_user.id, nickname=user_nickname)#создаю юзера
    session.add(new_minecraft_user)
    session.flush()
    logger.info(f"Игрок {user_nickname} добавлен в таблицу игроков...")

    player_level = session.query(Levels).filter_by(player_id=new_minecraft_user.id).first()
    if player_level:
        finish_line = f"У игрока {user_nickname} по какой-то причине уже существует запись в базе уровней."
        logger.error(finish_line)

        something_wrong = True
        return finish_line, something_wrong

    new_player_level_record = Levels(player_id=new_minecraft_user.id)# добавляю его в таблицу отслеживания уровней
    session.add(new_player_level_record)
    session.flush()
    logger.info(f"Игрок {user_nickname} внесен в таблицу уровней...")

    player_inventory = session.query(Inventory).filter_by(player_id=new_minecraft_user.id).first()
    if player_inventory:
        finish_line = f"У игрока {user_nickname} по какой-то причине уже существует запись в базе инвентарей."
        logger.error(finish_line)

        something_wrong = True
        return finish_line, something_wrong

    new_player_inventory_record = Inventory(player_id=new_minecraft_user.id)#дообавляю в систему инвентаря
    session.add(new_player_inventory_record)
    session.commit()
    logger.info(f"Игроку {user_nickname} создан инвентарь...")
    finish_line = f"Регистрация игрока {user_nickname} прошла успешно!"
    logger.info(finish_line)
    return finish_line, something_wrong
@exception_handler
def add_tag(user_telegramm_id:int, new_tag:str): #готова
    """Add special tag to person using their telegramm id:

    keyword arguments:

    user_telegramm_id -- integer, gets user tg id in private chat with bot

    new_tag -- string, special tag that bot uses to greet people, which is connected with telegramm account, not minecraft username. Can be "female", "admin", etc.

    returns 2 values:

    finish_line -- string, contains details about how the function has finished

    successful -- boolean, True if tag added successfully, False if  not

    """


    user = session.query(TGuser).filter_by(tg_id=user_telegramm_id).first()
    if not user:
        finish_line = "Отсутствует пользователь с таким айди телеграмм."
        successful = False
        logger.info(f"{finish_line}\nsuccessful:{successful}\n")
        return finish_line, successful

    user_tags = [tag.tag for tag in user.tagowners]
    if new_tag in user_tags:
        finish_line = f"У пользователя {user_telegramm_id} уже есть тег {new_tag}."
        successful = False
        logger.info(f"{finish_line}\nsuccessful:{successful}\n")
        return finish_line, successful

    new_tag_for_user = Tag(owner=user.id, tag=new_tag)
    session.add(new_tag_for_user)
    session.commit()

    finish_line = f"Пользователь {user_telegramm_id} теперь носит тег {new_tag}."
    successful = True
    logger.info(f"{finish_line}\nsuccessful: {successful}\n")
    return finish_line, successful
@exception_handler
def check_if_registered(user_nickname:str):#готова
    """Check if user is registered:

    keyword arguments:

    user_nickname -- nickname of minecraft user

    returns 1 argument:

    isregistered -- boolean, True if is, False if is not"""

    if session.query(MCuser).filter_by(nickname=user_nickname).first():

        isregistered = True
        logger.info(f"Игрок {user_nickname} действительно зарегистрирован.\n"f"isregistered = {isregistered}")
        return isregistered

    logger.info(f"Не удалось найти игрока {user_nickname} среди зарегистрированных пользователей.")
    isregistered = False

    return isregistered
@exception_handler
def get_person_tag(user_nickname:str):#готова
    """ Gets personal tag.

    keyword arguments:

    user_nickname -- minecraft user nickname that bot gets from players_online()

    returns 1 argument:

    False -- if by any reason user id can not be found in database
    or
    None -- if user has no tags
    or
    tags_itered -- list. List of tags"""
    user_mc = session.query(MCuser).filter_by(nickname=user_nickname).first()
    if not user_mc:

        logger.info(f"Пользователь с ником {user_nickname} не найден.")
        return False
    user= session.query(TGuser).filter_by(id=user_mc.tg_user_id).first()
    if not user:

        logger.info(f"Пользователь с айди {user.tg_id} не найден")
        return False
    user_tags= [tag.tag for tag in user.tagowners]
    if user_tags:
        tags_list = []

        for tag_name in user_tags:
            tags_list.append(tag_name)
        tags_itered = [f"{tag}" for tag in tags_list]

        logger.info(f"Пользователь, которому принадлежит персонаж {user_nickname} носит теги:\n" + "\n".join(tags_itered))
        return tags_itered
    else:

        logger.info(f"У пользователя, которому принадлежит персонаж {user_nickname} нет тегов")
        return None

@exception_handler
def lookup_procedure(user_nickname:str):
    """Function that gets crucial info for the greeting/exiting message.

    kwargs:

    user_nickname -- string. Player minecraft username

    returns 1 value:

    list -- [username, user_rank]

    or

    dictionary -- {username:[user_rank, user_tag(s)]}"""
    user = session.query(MCuser).filter_by(nickname=user_nickname).first()
    tags = get_person_tag(user_nickname)
    rank = user.rank
    if tags:
        user_data = {user_nickname:[rank, tags]}
        return user_data
    user_data = [user_nickname, rank]
    return user_data
@exception_handler
def get_current_level(user_nickname:str):#готова
    """Gets current player level, rank, needed and current xp points.

    kwargs:

    user_nickname -- Player's minecraft username

    returns 1 value:

    False -- if player with this playername does not exist
    or
    finish_line --  string. Contains player data."""
    user = session.query(MCuser).filter_by(nickname=user_nickname).first()
    if not user:
        logger.info(f"Отсутствует игрок c именем {user_nickname}(get_current_level)")

        return False

    user_lvl = session.query(Levels).filter_by(player_id=user.id).first()

    lvl_data = {"nick":user_nickname,
                "cur_xp":user_lvl.current_xp,
                "need_xp":user_lvl.needed_xp,
                "lev":user_lvl.player_lvl}
    finish_line = (f"Текущий уровень игрока {user_nickname} - ({lvl_data["lev"]}){user.rank}\n"
               f"Текущее количество опыта - {lvl_data['cur_xp']}\n"
               f"Нужно до следующего уровня - {lvl_data['need_xp']}")
    logger.info(finish_line)
    return finish_line
@exception_handler
def add_money(user_nickname:str, value:int):#готова
    """ Adds money on minecraft player's account.

    kwargs:

    user_nickname - String. Minecraft username.

    value -- integer. Wanted amount of money.

    returns 1 value:

    False -- if player with this minecraft playername does not exist
    or
    finish_line -- string. Contains message about the amount of money added and current account state."""
    user = session.query(MCuser).filter_by(nickname=user_nickname).first()
    if not user:

        logger.info("Отсутствует игрок с таким именем (add_money)")
        return False
    user_inventory = session.query(Inventory).filter_by(player_id=user.id).first()
    user_inventory.money += value
    finish_line = (f"\nИгроку {user_nickname} начислено {value} ЗахарБаксов.\n"
                 f"Текущее число ЗахарБаксов на счету: {user_inventory.money}")
    logger.info(finish_line)
    return finish_line
@exception_handler
def change_level(user_nickname:str,xp_points:int):#готова
    """Changes Minecraft players' level. Adds, if to be particular.

    kwargs:

    user_nickname -- string. Minecraft player nickname.

    xp_points -- integer. Wanted experience points. Sets automatically.

    returns:

    False -- if by some reason the player doesn't exist

    or

    finish_line -- Contains info about success of the funiction"""
    list_of_ranks = ["Новичок", "Любитель", "Майнкрафтер","Дока рецептов", "Опытный строитель", "Олд сервера", "PVP-Мастер", "Коллега Нотча", "Друган Захара"]
    user = session.query(MCuser).filter_by(nickname=user_nickname).first()
    if not user:

        logger.info(f"Отсутствует игрок с именем {user_nickname}.")
        return False
    user_lvl = session.query(Levels).filter_by(player_id=user.id).first()
    user_lvl.current_xp += xp_points
    session.commit()
    difference = user_lvl.needed_xp - user_lvl.current_xp



    if difference <= 0 and user_lvl.player_lvl == 10: #можно потом добавить чтобы оно уравнивало уровень текущего опыта с необходимым
        finish_line = f"\nУ игрока {user_nickname} максимальный уровень!"
        logger.info(finish_line)
        return finish_line
    if difference > 0:
        pre_finish_line=f"\nИгроку {user_nickname} добавлено {xp_points} очков опыта."
        logger.info(pre_finish_line)
        return pre_finish_line
    while difference <= 0:
        user_lvl.player_lvl += 1
        user_lvl.needed_xp = round(user_lvl.needed_xp * 1.5)
        user_lvl.current_xp = abs(difference)
        session.flush()

        user.rank = list_of_ranks[user_lvl.player_lvl -2]
        session.flush()
        add_money(user_nickname, (user_lvl.player_lvl - 1) * 25 )
        difference = user_lvl.needed_xp - user_lvl.current_xp
        finish_line =(
            f"\nУровень игрока {user_nickname} повышен до {user.rank}.\n"
              f"Текущее количество очков опыта {user_lvl.current_xp}, до следующего уровня нужно {user_lvl.needed_xp}")
        logger.info(finish_line)

    return finish_line
def delete_tag(user_nickname:str, tag_to_delete:str): #сделать чтобыв выдавал список всех тегов
    user = session.query(MCuser).filter_by(nickname=user_nickname).first()

    if not user:
        logger.info("Пользователь с таким никнеймом не найден")
        return False
    session.query(Tag).filter_by(owner=user.tg_user_id, tag=tag_to_delete).delete()
    session.commit()
    return True


if __name__ == "__main__":
    delete_tag("Suka", "admin")




    #change_level("GeNGnidov", 350)
    #add_money("GeNGnidov", 2000)