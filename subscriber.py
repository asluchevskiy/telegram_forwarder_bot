import asyncio

from loguru import logger
from telethon import TelegramClient, events

import config

logger.add(config.LOG_FILE, rotation=config.LOG_ROTATION, level=config.LOG_LEVEL)

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)


@client.on(events.NewMessage(chats=config.SOURCE_CHAT_IDS))
async def handler(event):
    try:
        bot_id = int(config.BOT_TOKEN.split(':')[0])
        await client.forward_messages(bot_id, event.message)
        logger.info(f"Forwarded from {event.chat_id}")
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
