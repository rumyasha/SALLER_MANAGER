# Используем официальный Python 3.10 образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для psycopg2 и WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем проект в контейнер
COPY . /app/

# Экспортируем порт
EXPOSE 8000

# Команда для запуска сервера (можно поменять на gunicorn для продакшена)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
