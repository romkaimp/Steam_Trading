# Используем официальный образ Python
FROM python:3.11

ENV APP_HOME /app
# Устанавливаем рабочую директорию
WORKDIR $APP_HOME

# Копируем файлы зависимостей в рабочую директорию
COPY ./requirements.txt .

# танавливаем зависимости
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Устанавливаем переменную окружения для указания имени модуля FastAPI
ENV MODULE_NAME web.web_api

# Указываем команду на запуск Uvicorn при старте контейнера
CMD ["sh", "-c", "uvicorn web.web_api:app --host 0.0.0.0 --port 8000"]