# modules/delete_roles.py
import re
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from telethon import events

# Подключение к MongoDB
def get_db():
    try:
        client = MongoClient('mongodb://localhost:27017/')  # Убедитесь, что MongoDB работает на локальном сервере
        db = client.get_database('db_bot')
        return db
    except ServerSelectionTimeoutError:
        return None

# Удаление роли из базы данных
async def delete_role_command(event, role_id):
    db = get_db()
    if db is not None:
        roles_collection = db.roles

        # Находим роль по ID
        existing_role = roles_collection.find_one({"role_id": role_id})
        if existing_role:
            # Удаляем роль из базы данных
            roles_collection.delete_one({"role_id": role_id})
            await event.respond(f"Роль с ID {role_id} успешно удалена.")
        else:
            await event.respond(f"Ошибка: Роль с ID {role_id} не существует.")
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
                    await delete_role_command(event, role_id)
                else:
                    await event.respond("Ошибка: ID роли должен быть в диапазоне от 0 до 255.")
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "Удалить роль ID".')
