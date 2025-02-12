# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY bot/requirements.txt ./bot/requirements.txt
COPY webapp/requirements.txt ./webapp/requirements.txt

# Устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r bot/requirements.txt && \
    pip install -r webapp/requirements.txt

# Копируем исходный код
COPY bot ./bot
COPY webapp ./webapp

# Указываем рабочую директорию для веб-приложения
WORKDIR /app/webapp

# Запускаем приложения
CMD python ../bot/bot.py & python app.py