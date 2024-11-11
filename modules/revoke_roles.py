from telethon import TelegramClient, events
import re
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Подключение к MongoDB
def get_db():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.get_database('db_bot')
        return db
    except ServerSelectionTimeoutError:
        print("Ошибка подключения к MongoDB.")
        return None

# Функция для разжалования пользователя и присвоения роли по умолчанию (ID 255)
async def revoke_role_command(event, username_original):
    db = get_db()
    if db is not None:
        roles_collection = db.roles
        
        try:
            # Получаем user_id пользователя по username
            user = await event.client.get_entity(username_original)
            user_id = user.id
        except ValueError:
            await event.respond(f"Ошибка: Адептус @{username_original} не найден.")
            return

        # Удаляем пользователя из всех других ролей
        roles_collection.update_many(
            {"users": user_id},
            {"$pull": {"users": user_id}}
        )

        # Проверяем, существует ли роль с ID 255
        role = roles_collection.find_one({"role_id": 255})
        if role is None:
            # Если роль с ID 255 не существует, создаем ее
            roles_collection.insert_one({
                "role_id": 255,
                "role_name": "Участник",
                "users": []
            })
            role = {"role_id": 255, "role_name": "Участник"}

        # Добавляем пользователя в роль 255
        roles_collection.update_one(
            {"role_id": 255},
            {"$addToSet": {"users": user_id}}
        )

        await event.respond(f"Адептус @{username_original} был разжалован, изменения внесены в реестр.")

# Регистрация обработчика для разжалования
def register_revoke_role_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group))  # Ограничиваем обработку только для групп
    async def handler(event):
        command_text = event.message.text.strip()

        # Проверка на команду
        if command_text.lower().startswith('!разжаловать'):  # Проверяем, начинается ли команда с !разжаловать
            # Используем регулярное выражение для извлечения username
            match = re.match(r'разжаловать\s+@(\w+)', command_text)
            if match:
                username_original = match.group(1)  # Используем оригинальный @username из команды
                await revoke_role_command(event, username_original)
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "разжаловать @username".')
