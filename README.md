# Telegram Forwarder Bot 🤖

Бот для пересылки сообщений между Telegram каналами/чатами с поддержкой медиа-групп и фильтрацией по пользователям.

## Особенности ✨

- 📨 Автоматическая пересылка сообщений между каналами
- 🖼️ Поддержка медиа-групп (альбомы фото/видео)
- 👥 Фильтрация по разрешенным пользователям
- 🔄 Retry механизм при rate limiting
- 📝 Детальное логирование
- 🐳 Docker поддержка

## Архитектура

Проект состоит из двух процессов:

1. **Subscriber** (`subscriber.py`) - подписывается на исходные каналы через Telethon и пересылает сообщения боту
2. **Bot** (`bot.py`) - получает сообщения и пересылает их в целевые каналы через aiogram

## Быстрый старт 🚀

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd telegram_forwarder_bot
```

### 2. Настройка окружения

```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте .env файл
nano .env
```

### 3. Заполнение .env файла

```env
# Telegram API (получите на https://my.telegram.org)
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Пользователи которым разрешено использовать бота
ALLOWED_USERS=[123456789, 987654321]

# Карта пересылки: источник -> назначение
CHAT_FORWARD_MAP={"-100123456789": "-100987654321"}

# Остальные настройки (опционально)
LOG_FILE=logs/bot.log
LOG_LEVEL=INFO
```

### 4. Создание Telegram сессии

Первый раз нужно авторизоваться и создать файл сессии:

```bash
python subscriber.py
# Введите номер телефона и код подтверждения
```

### 5. Запуск через Docker

```bash
# Создание и запуск контейнеров
docker compose up -d --build

# Или используйте готовый скрипт
./start.sh
```

## Управление 🎛️

### Основные команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск с перечитыванием .env
docker compose down && docker compose up -d

# Просмотр логов
docker compose logs -f              # все логи
docker compose logs -f bot          # только бот
docker compose logs -f subscriber   # только subscriber

# Статус контейнеров
docker compose ps
```

### Применение изменений конфигурации

После изменения `.env` файла:

```bash
docker compose down && docker compose up -d
```

**Важно:** Простой `restart` не перечитывает переменные окружения!

## Конфигурация ⚙️

### Основные параметры

| Параметр | Описание | Пример |
|----------|----------|---------|
| `API_ID` | ID приложения Telegram API | `12345678` |
| `API_HASH` | Hash приложения Telegram API | `abcdef123456...` |
| `BOT_TOKEN` | Токен Telegram бота | `123456:ABC-DEF...` |
| `ALLOWED_USERS` | Разрешенные пользователи (JSON) | `[123456789, 987654321]` |
| `CHAT_FORWARD_MAP` | Карта пересылки (JSON) | `{"-100111": "-100222"}` |

### Настройки логирования

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `LOG_FILE` | Путь к файлу логов | `logs/bot.log` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `LOG_ROTATION` | Ротация логов | `5 MB` |

## Структура проекта 📁

```
telegram_forwarder_bot/
├── bot.py                 # Основной бот (aiogram)
├── subscriber.py          # Подписчик на каналы (telethon) 
├── config.py             # Конфигурация
├── requirements.txt      # Python зависимости
├── docker-compose.yml    # Docker Compose конфигурация
├── Dockerfile           # Docker образ
├── start.sh            # Скрипт запуска
├── .env               # Переменные окружения (создать из .env.example)
├── env.example        # Пример конфигурации
└── logs/             # Директория логов
```

## Troubleshooting 🔧

### Проблемы с запуском

1. **Контейнер уже существует:**
   ```bash
   docker compose down
   docker compose up -d
   ```

2. **Ошибки зависимостей:**
   ```bash
   docker compose build --no-cache
   ```

3. **Проблемы с .env файлом:**
   - Проверьте синтаксис JSON в `ALLOWED_USERS` и `CHAT_FORWARD_MAP`
   - Убедитесь что нет лишних пробелов

### Проверка логов

```bash
# Детальные логи для отладки
docker compose logs -f --tail=100

# Логи конкретного сервиса
docker compose logs -f subscriber
```

### Типичные ошибки

- **"Flood wait"** - слишком много запросов, бот автоматически ждет
- **"Chat not found"** - неверный ID канала или бот не добавлен в канал
- **"User not allowed"** - пользователь не в списке `ALLOWED_USERS`

## Лицензия 📄

MIT License - используйте свободно с указанием авторства.

## Поддержка 💡

При возникновении вопросов:

1. Проверьте логи: `docker compose logs -f`
2. Убедитесь что все переменные в `.env` заполнены корректно  
3. Проверьте, что бот добавлен в каналы как администратор
4. Создайте issue в репозитории 