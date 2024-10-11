from celery import Celery

# Создаем экземпляр приложения Celery
app = Celery("fastapi_celery", broker="redis://localhost:6379")

# Настройки Beat (планировщика задач)
app.conf.beat_schedule = {
    "parsing_steam": {
        "task": "service.tasks.table_update",
        "schedule": 60.0,  # Запускается каждые 60 секунд
    },
}

# Дополнительные настройки (например, тайм-ауты, результаты и т.д.)
app.conf.timezone = "UTC"  # Установите временную зону, если это необходимо

# Загрузка модулей задач (при необходимости)
app.autodiscover_tasks(['tasks'])
