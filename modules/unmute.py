from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# Функция для размута пользователя
async def unmute_user(client, chat_id, username):
    try:
        # Ищем пользователя по username
        user = await client.get_entity(username)
        user_id = user.id  # Получаем user_id

        # Снимаем все ограничения с пользователя (размут)
        mute_rights = ChatBannedRights(
            until_date=None,  # Отмена временного мута
            send_messages=False  # Разрешаем отправку сообщений
        )

        # Применяем размутид
        await client(EditBannedRequest(chat_id, user_id, mute_rights))
        return True
    except Exception as e:
        return str(e)

# Регистрация обработчика команды !размут
def register_unmute_handler(client):
    @client.on(events.NewMessage(pattern=r'размут (@\w+)'))
    async def handler(event):
        if event.is_group:
            try:
                username = event.pattern_match.group(1)  # @username

                # Размучиваем пользователя
                success = await unmute_user(client, event.chat_id, username)
                if success is True:
                    await event.reply(f'Адептус {username} был размучен')
                else:
                    await event.reply(f'Ошибка: {success}')
            except Exception as e:
                await event.reply(f'Ошибка при обработке команды: {str(e)}')
        else:
            await event.reply("Эту команду можно использовать только в группе.")
