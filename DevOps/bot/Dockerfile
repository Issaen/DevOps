# Официальный образ Python 
FROM python:3.9-slim

# Установка рабочей директории в контейнере
WORKDIR /app

# Установка зависимостей
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта в контейнер
COPY . .

# Команда для запуска бота
CMD ["python", "bot.py"]

# Копирование файлов зависимостей
COPY requirements.txt .
