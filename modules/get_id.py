from telethon import TelegramClient, events
import re

async def get_id_command(event, username=None):
    """
    Обработчик команды /getid.
    Извлекает user_id пользователя, упомянутого в сообщении.
    """
    client = event.client
    group_name = event.chat  # Получаем группу, где была вызвана команда

    if username:
        # Ищем пользователя по username среди участников группы
        participants = await client.get_participants(group_name)

        # Находим пользователя с заданным username
        for participant in participants:
            if participant.username and participant.username.lower() == username.lower():  # Сравниваем без учета регистра
                await event.respond(f"User ID для @{username}: {participant.id}")
                return
        
        await event.respond(f"Ошибка: не удалось найти пользователя с username @{username} в группе.")
    else:
        # Если username не указан, выводим сообщение о том, что не был указан пользователь
        await event.respond("Ошибка: укажите username в формате @username.")

# Регистрация обработчика в main.py
def register_get_id_handler(client: TelegramClient):
    @client.on(events.NewMessage(func=lambda e: e.is_group and e.text.startswith('/getid')))
    async def handler(event):
        # Извлекаем команду и аргумент (если он есть)
        command_text = event.message.text

        # Пытаемся найти упоминание @username в сообщении
        match = re.search(r'@(\w+)', command_text)  # Используем регулярное выражение для поиска @username

        if match:
            # Извлекаем username
            username = match.group(1)  # Получаем username без символа '@'
            await get_id_command(event, username)
        else:
            # Если username не найден, отправляем ошибку
            await event.respond("Ошибка: укажите username в формате @username.")
