from telethon import TelegramClient, events
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

# Функция для получения информации об администраторах
async def get_admins_list(event):
    db = get_db()
    if db is not None:
        roles_collection = db.roles
        
        # Составим список для вывода
        response = "Реестр Адептус Администратум:\n\n"
        
        # Проходим по ролям с ID от 0 до 8
        for role_id in range(0, 9):
            role = roles_collection.find_one({"role_id": role_id})
            if role and role.get("users"):
                role_name = role.get("role_name", "Неизвестная роль")
                response += f"ID: {role_id} {role_name}\n"
                
                # Для каждой роли добавляем список пользователей
                for user_id in role["users"]:
                    user = await event.client.get_entity(user_id)
                    username = user.username if user.username else f"@{user_id}"  # Используем @username или user_id
                    response += f"@{username}\n"
                
                # Добавим пустую строку для разделения между ролями
                response += "\n"
        
        # Отправим результат в чат
        if response == "Реестр Адептус Администратум:\n\n":
            response = "Адептус Администратум неназначены."

        await event.respond(response, parse_mode='markdown')
    else:
        await event.respond("Ошибка подключения к реестру.")

# Регистрация обработчика команды "Кто админ"
def register_admin_list_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group))  # Ограничиваем обработку только для групп
    async def handler(event):
        command_text = event.message.text.strip()

        # Проверка на команду
        if 'кто админ' in command_text.lower():  # Проверяем, есть ли подстрока 'кто админ'
            await get_admins_list(event)
