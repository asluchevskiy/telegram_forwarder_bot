import asyncio
import re
from functools import wraps
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from aiogram.exceptions import TelegramRetryAfter
from loguru import logger

import config

# Configure logging
logger.add(config.LOG_FILE, rotation=config.LOG_ROTATION, level=config.LOG_LEVEL)

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Album buffer: {media_group_id: [messages]}
album_buffer = {}


def retry_on_flood(max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except TelegramRetryAfter as e:
                    if attempt < max_retries:
                        logger.warning(f"Rate limited, waiting {e.retry_after} seconds (attempt {attempt + 1})")
                        await asyncio.sleep(e.retry_after)
                    else:
                        logger.error(f"Failed after {max_retries} retries")
                        break
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    break
        return wrapper
    return decorator


def create_media_item(msg):
    caption = msg.caption if msg.caption else None
    if msg.photo:
        return InputMediaPhoto(media=msg.photo[-1].file_id, caption=caption)
    elif msg.video:
        return InputMediaVideo(media=msg.video.file_id, caption=caption)
    elif msg.document:
        return InputMediaDocument(media=msg.document.file_id, caption=caption)
    return None


@retry_on_flood()
async def copy_album(messages, target_chat_id):
    media_group = [create_media_item(msg) for msg in messages]
    media_group = [m for m in media_group if m]
    if media_group:
        await bot.send_media_group(target_chat_id, media_group)
        logger.info(f"Album copied to {target_chat_id}")


@retry_on_flood()
async def copy_single_message(target_chat_id, chat_id, message_id):
    await bot.copy_message(target_chat_id, chat_id, message_id)
    logger.info(f"Message copied to {target_chat_id}")


async def flush_album_later(media_group_id, target_chat_id):
    await asyncio.sleep(1.0)
    if media_group_id in album_buffer:
        await copy_album(album_buffer[media_group_id], target_chat_id)
        del album_buffer[media_group_id]


@dp.message()
async def handle_message(message: types.Message):
    """
    Handle incoming messages and copy them to appropriate channels
    using Telegram's copy_message method. Only process messages from whitelisted users.
    """

    if message.from_user.id not in config.ALLOWED_USERS:
        return
    if not message.forward_from_chat:
        return

    # logger.info(f'Received message from channel = {message.forward_from_chat.id}')

    target_chat_id = config.CHAT_FORWARD_MAP.get(message.forward_from_chat.id)
    if not target_chat_id:
        return

    if message.media_group_id:
        album_buffer.setdefault(message.media_group_id, []).append(message)
        if len(album_buffer[message.media_group_id]) == 1:
            asyncio.create_task(flush_album_later(message.media_group_id, target_chat_id))
        return

    await copy_single_message(target_chat_id, message.chat.id, message.message_id)


async def main():
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
