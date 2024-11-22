import re
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from telethon import events
from telethon.tl.types import ChannelParticipantCreator  # Импортируем тип участника для создателя чата
import logging

# Устанавливаем логирование для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к MongoDB
def get_db():
    try:
        client = MongoClient('mongodb://localhost:27017/')  # Убедитесь, что MongoDB работает на локальном сервере
        db = client.get_database('db_bot')
        return db
    except ServerSelectionTimeoutError:
        logger.error("Ошибка подключения к MongoDB.")
        return None

# Проверка, является ли пользователь создателем чата
async def is_creator(client, chat_id, user_id):
    async for participant in client.iter_participants(chat_id):
        if participant.id == user_id and isinstance(participant.participant, ChannelParticipantCreator):
            return True
    return False

# Проверка роли пользователя в базе данных
def has_permission(user_id, db):
    users_collection = db.get_collection("users")  # Получаем или создаем коллекцию users
    user = users_collection.find_one({"user_id": user_id})
    if user:
        role_id = user.get("role_id", 4)  # Если role_id нет, то по умолчанию 4 (без прав)
        logger.info(f"Пользователь {user_id} имеет role_id {role_id}.")  # Логируем role_id
        if 0 <= role_id <= 3:  # Проверка диапазона role_id от 0 до 3
            return True
    logger.info(f"Пользователь {user_id} не найден или у него нет прав.")
    return False

# Удаление роли из базы данных
async def delete_role_command(event, role_id):
    db = get_db()
    if db is not None:
        roles_collection = db.get_collection("roles")  # Получаем или создаем коллекцию roles

        # Находим роль по ID
        existing_role = roles_collection.find_one({"role_id": role_id})
        if existing_role:
            # Удаляем роль из базы данных
            roles_collection.delete_one({"role_id": role_id})
            await event.respond(f"Роль с ID {role_id} успешно убрана из реестра.")
        else:
            await event.respond(f"Ошибка: Роль с ID {role_id} не найдена в реестре.")
    else:
        await event.respond("Ошибка подключения к базе данных.")

# Регистрация обработчика команды удаления роли
def register_get_delete_role_handler(client):
    @client.on(events.NewMessage(func=lambda e: e.is_group))  # Ограничиваем обработку только для групп
    async def handler(event):
        command_text = event.message.text.strip()

        # Проверка на команду
        if 'удалить роль' in command_text.lower():  # Проверяем, есть ли подстрока 'удалить роль'
            # Используем регулярное выражение для извлечения ID роли
            match = re.match(r'удалить роль\s+(\d{1,3})', command_text.strip())
            if match:
                role_id = int(match.group(1))

                # Проверка, что ID в допустимом диапазоне (от 0 до 255)
                if 0 <= role_id <= 255:
                    db = get_db()
                    # Логируем данные для отладки
                    logger.info(f"Пользователь {event.sender_id} выполняет команду в чате {event.chat_id}.")
                    
                    # Проверка прав доступа пользователя
                    if await is_creator(client, event.chat_id, event.sender_id):
                        logger.info(f"Пользователь {event.sender_id} является создателем чата.")
                        await delete_role_command(event, role_id)
                    elif db is not None and has_permission(event.sender_id, db):
                        logger.info(f"Пользователь {event.sender_id} имеет права на выполнение команды.")
                        await delete_role_command(event, role_id)
                    else:
                        logger.warning(f"Пользователь {event.sender_id} не имеет прав для выполнения команды.")
                        await event.respond("У вас нет прав для выполнения этой команды.")
                else:
                    await event.respond("Ошибка: ID роли должен быть в диапазоне от 0 до 255.")
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "удалить роль ID".')
