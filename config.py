from typing import List, Dict
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Telegram API settings
    api_id: int
    api_hash: str
    session_name: str = "anon"
    bot_session_name: str = "bot_session"
    bot_token: str

    # OpenAI settings
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    enable_translation: bool = True
    translation_prompt: str = "chatgpt prompt"

    # Logging settings
    log_file: str = "bot.log"
    log_level: str = "INFO"
    log_rotation: str = "5 MB"

    # Users and chats
    allowed_users: List[int]
   
    # Chat mapping
    chat_forward_map: Dict[int, int]
    
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False)

    @property
    def source_chat_ids(self) -> List[int]:
        return list(self.chat_forward_map.keys())


# Создаем глобальный экземпляр настроек
settings = Settings()

# Для обратной совместимости оставляем старые имена переменных
API_ID = settings.api_id
API_HASH = settings.api_hash
SESSION_NAME = settings.session_name
BOT_SESSION_NAME = settings.bot_session_name
BOT_TOKEN = settings.bot_token
OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model
ENABLE_TRANSLATION = settings.enable_translation
TRANSLATION_PROMPT = settings.translation_prompt
LOG_FILE = settings.log_file
LOG_LEVEL = settings.log_level
LOG_ROTATION = settings.log_rotation
ALLOWED_USERS = settings.allowed_users
CHAT_FORWARD_MAP = settings.chat_forward_map
SOURCE_CHAT_IDS = settings.source_chat_ids
