from telethon import TelegramClient, events
import re
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from telethon.tl.types import ChannelParticipantCreator

# Подключение к MongoDB
def get_db():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.get_database('db_bot')
        return db
    except ServerSelectionTimeoutError:
        print("Ошибка подключения к MongoDB.")
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
    if user and 0 <= user.get("role_id", 4) <= 3:  # Проверка диапазона role_id от 0 до 3
        return True
    return False

# Создание или обновление роли в базе данных
async def create_or_update_role_command(event, role_id, role_name):
    db = get_db()
    if db is not None:
        roles_collection = db.get_collection("roles")  # Получаем или создаем коллекцию roles
        existing_role = roles_collection.find_one({"role_id": role_id})
        if existing_role:
            roles_collection.update_one(
                {"role_id": role_id},
                {"$set": {"role_name": role_name}}
            )
            await event.respond(f"Роль {role_id} обновлена на {role_name} и изменения внесены в реестр.")
        else:
            new_role = {
                "role_id": role_id,
                "role_name": role_name,
                "users": []
            }
            roles_collection.insert_one(new_role)
            await event.respond(f"Роль с ID {role_id} и названием \"{role_name}\" успешно внесена в реестр.")
    else:
        await event.respond("Ошибка подключения к базе данных.")

# Регистрация обработчика команды создания роли
def register_create_role_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group))
    async def handler(event):
        command_text = event.message.text.strip()
        if 'создать роль' in command_text.lower():
            match = re.match(r'создать роль\s+(\d{1,3})\s+"([^"]+)"', command_text)
            if match:
                role_id = int(match.group(1))
                role_name = match.group(2)

                if 0 <= role_id <= 255:
                    db = get_db()
                    # Проверка прав доступа пользователя
                    if await is_creator(client, event.chat_id, event.sender_id) or (db is not None and has_permission(event.sender_id, db)):
                        await create_or_update_role_command(event, role_id, role_name)
                    else:
                        await event.respond("У вас нет прав для выполнения этой команды.")
                else:
                    await event.respond("Ошибка: ID роли должен быть в диапазоне от 0 до 255.")
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "Создать роль ID "Имя".')
