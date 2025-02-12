FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY bot/requirements.txt ./bot/requirements.txt
COPY webapp/requirements.txt ./webapp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r bot/requirements.txt && \
    pip install -r webapp/requirements.txt

# Копирование исходного кода
COPY . .

# Запуск приложений
CMD python bot/bot.py & python webapp/app.py