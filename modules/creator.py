# modules/creator.py
from telethon import events
from telethon.tl.types import ChannelParticipantCreator

def register_creator_handler(client):
    @client.on(events.NewMessage(pattern='/creator'))
    async def creator_handler(event):
        if event.is_group:
            chat = await event.get_chat()
            # Получаем список участников и ищем создателя
            async for participant in client.iter_participants(chat.id):
                if isinstance(participant.participant, ChannelParticipantCreator):
                    creator_id = participant.id
                    await event.reply(f"Создатель чата имеет user_id: {creator_id}")
                    return
            # Если создатель не найден
            await event.reply("Не удалось определить создателя этого чата.")
        else:
            await event.reply("Эта команда доступна только в групповом чате.")
