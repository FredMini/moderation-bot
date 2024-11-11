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

# Функция для назначения роли пользователю
async def assign_role_command(event, role_id, username_original):
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
        
        # Проверяем, существует ли роль с заданным role_id
        role = roles_collection.find_one({"role_id": role_id})
        if role:
            # Добавляем user_id в новую роль
            roles_collection.update_one(
                {"role_id": role_id},
                {"$addToSet": {"users": user_id}}
            )
            await event.respond(f"Адептус @{username_original} успешно назначен на роль с ID {role_id}.")
        else:
            await event.respond(f"Роль с ID {role_id} не найдена.")
    else:
        await event.respond("Ошибка подключения к базе данных.")

# Регистрация обработчика команды присвоения роли
def register_assign_role_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group))  # Ограничиваем обработку только для групп
    async def handler(event):
        command_text = event.message.text.strip()

        # Проверка на команду
        if command_text.lower().startswith('присвоить роль'):  # Проверяем, начинается ли команда с !присвоить роль
            # Используем регулярное выражение для извлечения ID и username
            match = re.match(r'присвоить роль\s+(\d{1,3})\s+@(\w+)', command_text)
            if match:
                role_id = int(match.group(1))
                username_original = match.group(2)  # Используем оригинальный @username из команды

                # Проверка, что ID в допустимом диапазоне (от 0 до 255)
                if 0 <= role_id <= 255:
                    await assign_role_command(event, role_id, username_original)
                else:
                    await event.respond("Ошибка: ID роли должен быть в диапазоне от 0 до 255.")
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "присвоить роль ID @username".')
