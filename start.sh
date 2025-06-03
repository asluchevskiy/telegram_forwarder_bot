#!/bin/bash

# Скрипт для запуска Telegram Forwarder Bot в продакшн режиме

set -e

echo "🚀 Запуск Telegram Forwarder Bot..."

# Создание директории для логов
mkdir -p logs

# Запуск
docker compose up -d --build

echo "✅ Запущены 2 процесса: subscriber и bot"
echo ""
echo "📊 Логи subscriber: docker compose logs -f subscriber"
echo "📊 Логи bot: docker compose logs -f bot"
echo "📊 Все логи: docker compose logs -f"
echo ""
echo "🛑 Остановка: docker compose down" 