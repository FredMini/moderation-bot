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

# Создание или обновление роли в базе данных
async def create_or_update_role_command(event, role_id, role_name):
    db = get_db()
    if db is not None:
        # Проверяем, существует ли коллекция roles
        roles_collection = db.roles
        
        # Проверяем, существует ли уже роль с таким ID
        existing_role = roles_collection.find_one({"role_id": role_id})
        if existing_role:
            # Обновляем название существующей роли
            roles_collection.update_one(
                {"role_id": role_id},  # Поиск по role_id
                {"$set": {"role_name": role_name}}  # Обновление только имени роли
            )
            await event.respond(f"Роль с ID {role_id} уже существовала. Название обновлено на \"{role_name}\".")
        else:
            # Создаем новую роль
            new_role = {
                "role_id": role_id,
                "role_name": role_name,
                "users": []  # Список пользователей, которым будет назначена роль
            }
            
            # Вставляем роль в коллекцию
            roles_collection.insert_one(new_role)
            await event.respond(f"Роль с ID {role_id} и названием \"{role_name}\" успешно создана.")
    else:
        await event.respond("Ошибка подключения к базе данных.")

# Регистрация обработчика команды создания роли
def register_create_role_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group))  # Ограничиваем обработку только для групп
    async def handler(event):
        command_text = event.message.text.strip()

        # Проверка на команду
        if 'создать роль' in command_text.lower():  # Проверяем, есть ли подстрока 'создать роль'
            # Используем регулярное выражение для извлечения ID и имени роли
            match = re.match(r'создать роль\s+(\d{1,3})\s+"([^"]+)"', command_text.strip())
            if match:
                role_id = int(match.group(1))
                role_name = match.group(2)

                # Проверка, что ID в допустимом диапазоне (от 0 до 255)
                if 0 <= role_id <= 255:
                    await create_or_update_role_command(event, role_id, role_name)
                else:
                    await event.respond("Ошибка: ID роли должен быть в диапазоне от 0 до 255.")
            else:
                await event.respond('Ошибка: Неверный формат команды. Используйте "Создать роль ID "Имя".')
