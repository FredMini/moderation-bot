from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
from datetime import datetime, timedelta
import re

# Функция для преобразования времени в секунды
def convert_to_seconds(duration, unit):
    if unit == 'с':  # секунды
        return duration
    elif unit == 'м':  # минуты
        return duration * 60
    elif unit == 'ч':  # часы
        return duration * 3600
    elif unit == 'д':  # дни
        return duration * 86400
    elif unit == 'н':  # недели
        return duration * 604800
    elif unit == 'мц':  # месяца (приблизительно 30 дней)
        return duration * 2592000
    elif unit == 'г':  # года (приблизительно 365 дней)
        return duration * 31536000
    else:
        raise ValueError("Неправильная единица времени")

# Функция для преобразования времени в полный формат
def format_duration(duration, unit):
    if unit == 'с':
        return f"{duration} секунд"
    elif unit == 'м':
        return f"{duration} минут"
    elif unit == 'ч':
        return f"{duration} часов"
    elif unit == 'д':
        return f"{duration} дней"
    elif unit == 'н':
        return f"{duration} недели"
    elif unit == 'мц':
        return f"{duration} месяца"
    elif unit == 'г':
        return f"{duration} года"
    else:
        raise ValueError("Неправильная единица времени")

# Функция для мута пользователя по username на определенное время
async def mute_user(client, chat_id, username, duration, unit):
    try:
        # Ищем пользователя по username
        user = await client.get_entity(username)
        user_id = user.id  # Получаем user_id

        # Получаем информацию о чате, чтобы проверить, является ли бот администратором
        chat = await client.get_entity(chat_id)

        # Проверяем, является ли бот администратором, используя фильтр ChannelParticipantsAdmins
        bot_admin = False
        async for participant in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            if participant.id == (await client.get_me()).id:
                bot_admin = True
                break

        # Если бот не администратор, не выполняем команду
        if not bot_admin:
            return "Реестру Адептус Администратум не даны соотвествующие полномочие"

        # Проверяем, является ли пользователь администратором
        async for participant in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            if user_id == participant.id:
                return f"Невозможно замутить Адептус Администратум {username}."

        # Конвертируем время в секунды
        duration_seconds = convert_to_seconds(duration, unit)
        
        # Устанавливаем дату размучивания (время окончания мута)
        until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
        mute_rights = ChatBannedRights(
            until_date=until_date,
            send_messages=True
        )

        # Применяем мут
        await client(EditBannedRequest(chat_id, user_id, mute_rights))
        return True
    except Exception as e:
        return str(e)

# Регистрация обработчика команды !мут
def register_mute_handler(client):
    @client.on(events.NewMessage(pattern=r'мут (@\w+) (\d+)([смчднмг])'))
    async def handler(event):
        if event.is_group:
            try:
                # Извлекаем @username, длительность и единицу измерения из команды
                username = event.pattern_match.group(1)  # @username
                duration = int(event.pattern_match.group(2))  # Длительность
                unit = event.pattern_match.group(3)  # Единица времени (например, 'м' для минут)

                # Преобразуем время в полный формат
                full_duration = format_duration(duration, unit)

                # Время и единица времени передаются в функцию
                success = await mute_user(client, event.chat_id, username, duration, unit)
                if success is True:
                    await event.reply(f'Адептус {username} был замучен на {full_duration}.')
                else:
                    await event.reply(f'Ошибка: {success}')
            except Exception as e:
                await event.reply(f'Ошибка при обработке команды: {str(e)}')
        else:
            await event.reply("Эту команду можно использовать только в группе.")
