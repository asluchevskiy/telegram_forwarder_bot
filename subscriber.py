import asyncio
from typing import Dict, List

from loguru import logger
from telethon import TelegramClient, events
from telethon.tl.types import Message

import config

logger.add(config.LOG_FILE, rotation=config.LOG_ROTATION, level=config.LOG_LEVEL)

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)

# Буфер для альбомов: {grouped_id: [messages]}
album_buffer: Dict[int, List[Message]] = {}


async def forward_album(messages: List[Message], bot_id: int):
    """Пересылает альбом как группу сообщений"""
    try:
        await client.forward_messages(bot_id, messages)
        logger.info(f"Forwarded album ({len(messages)} messages) from {messages[0].chat_id}")
    except Exception as e:
        logger.error(f"Forward album error: {e}")


async def flush_album_later(grouped_id: int, bot_id: int):
    """Ждет 1 секунду и пересылает альбом"""
    await asyncio.sleep(1.0)
    if grouped_id in album_buffer:
        await forward_album(album_buffer[grouped_id], bot_id)
        del album_buffer[grouped_id]


@client.on(events.NewMessage(chats=config.SOURCE_CHAT_IDS))
async def handler(event):
    try:
        bot_id = int(config.BOT_TOKEN.split(':')[0])
        
        # Если сообщение - часть альбома
        if event.message.grouped_id:
            grouped_id = event.message.grouped_id
            
            # Добавляем сообщение в буфер
            if grouped_id not in album_buffer:
                album_buffer[grouped_id] = []
            album_buffer[grouped_id].append(event.message)
            
            # Если это первое сообщение альбома, запускаем таймер
            if len(album_buffer[grouped_id]) == 1:
                asyncio.create_task(flush_album_later(grouped_id, bot_id))
            
            logger.info(f"Buffered album message {len(album_buffer[grouped_id])} from {event.chat_id}")
        else:
            # Обычное сообщение - пересылаем сразу
            await client.forward_messages(bot_id, event.message)
            logger.info(f"Forwarded single message from {event.chat_id}")
            
    except Exception as e:
        logger.error(f"Forward error: {e}")


async def main():
    logger.info("Subscriber started")
    await client.start()
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Subscriber stopped")
